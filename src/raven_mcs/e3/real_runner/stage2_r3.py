"""Stage-2 usable with realizable staleness > S_max."""

from __future__ import annotations

from typing import Any

import numpy as np

from raven_mcs.e3.real_runner.constants import S_MAX, WINDOW_DURATION


def sample_tau(rng: np.random.Generator, window_id: int, s_max: int) -> tuple[int, int]:
    """Frozen staleness distribution with support including ages > S_max.

    P(age > S_max) ≈ 0.20 under this controlled design (not performance-tuned).
    """
    # Mixture: 80% uniform {0..s_max}, 20% uniform {s_max+1 .. s_max+3}
    if rng.random() < 0.20:
        tau = int(rng.integers(s_max + 1, s_max + 4))
    else:
        tau = int(rng.integers(0, s_max + 1))
    downloaded = max(0, int(window_id) - int(tau))
    tau = int(window_id) - downloaded
    return downloaded, tau


def compute_usable_r3(
    *,
    rng: np.random.Generator,
    registration_time: float,
    window_deadline: float,
    window_id: int,
    s_max: int = S_MAX,
    align_disadvantage: bool = False,
    has_observations: bool = True,
    force_device_tier: int | None = None,
) -> dict[str, Any]:
    tier = int(force_device_tier) if force_device_tier is not None else int(rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2]))
    p_cs = {0: 0.70, 1: 0.90, 2: 0.98}[tier]
    p_ns = {0: 0.80, 1: 0.95, 2: 0.99}[tier]
    mean_cmp = {0: 0.80, 1: 0.50, 2: 0.20}[tier]
    if align_disadvantage:
        p_cs *= 0.75
        p_ns *= 0.80
        mean_cmp *= 1.25

    compute_success = bool(rng.random() < p_cs) and has_observations
    t_cmp = float(rng.lognormal(np.log(max(mean_cmp, 1e-3)), 0.3)) if compute_success else 0.0
    network_success = bool(compute_success and (rng.random() < p_ns))
    t_net = float(rng.lognormal(np.log(0.3), 0.2)) if network_success else 0.0
    t_reg = float(registration_time)
    t_arr = t_reg + t_cmp + t_net
    deadline_pass = bool(t_arr < float(window_deadline))
    downloaded, tau = sample_tau(rng, window_id, s_max)
    staleness_pass = bool(tau <= int(s_max))
    u = bool(compute_success and network_success and deadline_pass and staleness_pass and has_observations)
    return {
        "T_reg": t_reg,
        "T_cmp": t_cmp,
        "T_net": t_net,
        "T_arr": t_arr,
        "window_deadline": float(window_deadline),
        "deadline_pass": deadline_pass,
        "staleness_pass": staleness_pass,
        "compute_success": compute_success,
        "network_success": network_success,
        "downloaded_version": downloaded,
        "tau": tau,
        "U": int(u),
        "device_tier": tier,
        "device_profile": f"tier-{tier}",
        "network_profile": f"net-tier-{tier}",
        "deadline_rule": "strict_less_than_next_window",
        "window_duration": WINDOW_DURATION,
    }
