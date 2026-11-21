"""Proof tests: atomic p_obs and joint pi_opp consumption."""

from __future__ import annotations

from typing import Any

import numpy as np

from raven_mcs.correction.hajek import raw_weights
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
from raven_mcs.e3.target_pair.errors import AtomicPobsError, PiOppScaleError


def atomic_pobs_oracle_weights(
    *,
    p1: float,
    p2: float,
    zeta: float = 1.0,
    a_max: float = 20.0,
    p_min: float = 0.05,
) -> dict[str, Any]:
    """Oracle first-stage raw weights for two units with distinct p_obs_true."""
    if not (0 < p1 <= 1 and 0 < p2 <= 1):
        raise AtomicPobsError("ATOMIC_POBS_ERROR: illegal p_obs")
    if abs(p1 - p2) < 1e-15:
        raise AtomicPobsError("ATOMIC_POBS_ERROR: p1 and p2 must differ for this test")
    p_hat = np.array([p1, p2], dtype=np.float64)
    z = np.array([zeta, zeta], dtype=np.float64)
    a = raw_weights(z, p_hat, a_max=a_max, p_min=p_min)
    # Analytical: a_i = min(a_max, zeta / max(p_i, p_min))
    hand = np.array(
        [min(a_max, zeta / max(p1, p_min)), min(a_max, zeta / max(p2, p_min))],
        dtype=np.float64,
    )
    err = float(np.max(np.abs(a - hand)))
    return {
        "p1": p1,
        "p2": p2,
        "resulting_weights": a.tolist(),
        "expected_analytical_weights": hand.tolist(),
        "error": err,
        "weights_differ": abs(a[0] - a[1]) > 1e-12,
        "status": "PASS" if err <= 1e-12 and abs(a[0] - a[1]) > 1e-12 else "FAIL",
    }


def joint_piopp_production_test() -> dict[str, Any]:
    clients = ["c0", "c1"]
    strata = {
        "c0": ["c0::block0::weekday", "c0::block2::weekday"],
        "c1": ["c1::block0::weekday", "c1::block2::weekday"],
    }
    pi_opp = build_joint_pi_opp(clients, strata)
    # Simple joint pi_tar on same keys
    keys = sorted(pi_opp.keys())
    pi_tar = {k: 1.0 / len(keys) for k in keys}
    s_opp = float(sum(pi_opp.values()))
    s_tar = float(sum(pi_tar.values()))
    if abs(s_opp - 1.0) > 1e-12:
        raise PiOppScaleError(f"PIOPP_SCALE_ERROR: sum pi_opp={s_opp}")
    if abs(s_tar - 1.0) > 1e-12:
        raise PiOppScaleError(f"PIOPP_SCALE_ERROR: sum pi_tar={s_tar}")
    ratios = {
        f"{k[0]}|{k[1]}": float(pi_tar[k] / max(pi_opp[k], 1e-12)) for k in keys
    }
    # Conditional-only check: per-client renormalized opp would differ from joint
    cond = {}
    for c in clients:
        sub = {k: v for k, v in pi_opp.items() if k[0] == c}
        z = sum(sub.values())
        for k, v in sub.items():
            cond[k] = v / z
    uses_joint = all(abs(pi_opp[k] - cond[k]) > 1e-12 for k in keys)
    return {
        "sum_pi_opp_joint": s_opp,
        "sum_pi_tar": s_tar,
        "design_ratio": "pi_tar / pi_opp_joint",
        "ratios": ratios,
        "uses_joint_not_conditional_only": uses_joint,
        "status": "PASS" if uses_joint and abs(s_opp - 1.0) <= 1e-12 else "FAIL",
    }
