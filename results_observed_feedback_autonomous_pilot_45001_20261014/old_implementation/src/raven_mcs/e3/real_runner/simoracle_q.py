"""Fixed-prestate SimOracle q via M_MC replay."""

from __future__ import annotations

from typing import Any

import numpy as np

from raven_mcs.e3.real_runner.constants import M_MC, M_MC_CHECK
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3
from raven_mcs.utils.hashing import sha256_json


def estimate_q_true_mc(
    *,
    prestate: dict[str, Any],
    m_mc: int = M_MC,
    mc_seed: int,
) -> dict[str, Any]:
    """Estimate q_true(x_pre) = (1/M_MC) sum_j U^{(j)} with prestate frozen."""
    if int(m_mc) <= 0:
        raise ValueError("m_mc must be positive")
    prestate_hash = sha256_json(prestate)
    rng_master = np.random.default_rng(int(mc_seed))
    seeds = rng_master.integers(0, 2**31 - 1, size=int(m_mc))
    us = np.zeros(int(m_mc), dtype=np.float64)
    for j, s in enumerate(seeds):
        rng = np.random.default_rng(int(s))
        out = compute_usable_r3(
            rng=rng,
            registration_time=float(prestate["registration_time"]),
            window_deadline=float(prestate["window_deadline"]),
            window_id=int(prestate["window_id"]),
            s_max=int(prestate["s_max"]),
            align_disadvantage=bool(prestate["align_disadvantage"]),
            has_observations=bool(prestate["has_observations"]),
            force_device_tier=int(prestate.get("device_tier_prior", 1)),
        )
        us[j] = float(out["U"])
    q = float(us.mean())
    se = float(np.sqrt(max(q * (1 - q), 0.0) / int(m_mc)))
    return {
        "q_true": q,
        "q_se": se,
        "M_MC": int(m_mc),
        "prestate_hash": prestate_hash,
        "mc_seed": int(mc_seed),
    }


def diagnostic_mc_check(
    *,
    prestate: dict[str, Any],
    mc_seed: int,
    m_formal: int = M_MC,
    m_check: int = M_MC_CHECK,
) -> dict[str, Any]:
    a = estimate_q_true_mc(prestate=prestate, m_mc=m_formal, mc_seed=mc_seed)
    b = estimate_q_true_mc(prestate=prestate, m_mc=m_check, mc_seed=mc_seed)
    return {
        "q_m2000": a["q_true"],
        "q_m10000": b["q_true"],
        "abs_diff": abs(a["q_true"] - b["q_true"]),
        "M_MC": m_formal,
        "M_MC_CHECK": m_check,
        "prestate_hash": a["prestate_hash"],
    }
