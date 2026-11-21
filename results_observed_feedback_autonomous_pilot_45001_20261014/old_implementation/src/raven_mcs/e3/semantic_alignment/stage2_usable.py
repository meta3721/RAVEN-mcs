"""Stage-2 usable indicator with arrival-deadline semantics."""

from __future__ import annotations

from typing import Any

import numpy as np

from raven_mcs.e3.semantic_alignment.constants import S_MAX, WINDOW_DURATION


def compute_usable_indicator(
    *,
    rng: np.random.Generator,
    registration_time: float,
    window_deadline: float,
    window_id: int,
    s_max: int = S_MAX,
    align_disadvantage: bool = False,
    has_observations: bool = True,
) -> dict[str, Any]:
    """U = 1{compute & network & T_arr < T_{r+1} & tau <= s_max} (strict deadline).

    Complete-aligned disadvantage lowers compute/network success rates for Tail strata.
    """
    # Device tiers
    tier = int(rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2]))
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
    deadline_pass = bool(t_arr < float(window_deadline))  # strict < T_{r+1}

    downloaded = int(window_id)
    if rng.random() < 0.15:
        downloaded = max(0, window_id - int(rng.integers(1, s_max + 1)))
    tau = int(window_id - downloaded)
    staleness_pass = bool(tau <= int(s_max))

    # True q (fixed-prestate controlled): product of success probs × on-time prior × staleness prior
    q_use_true = float(
        np.clip(p_cs * p_ns * 0.85 * (0.9 if align_disadvantage else 1.0), 0.05, 0.95)
    )

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
        "q_use_true": q_use_true,
        "device_profile": f"tier-{tier}",
        "network_profile": f"net-tier-{tier}",
        "deadline_rule": "strict_less_than_next_window",
    }


def usable_semantics_spec() -> dict[str, Any]:
    return {
        "formula": "T_arr = T_reg + T_cmp + T_net; U = 1{cs & ns & T_arr < T_{r+1} & tau <= S_max}",
        "deadline_rule": "strict_less_than_next_window",
        "s_max": S_MAX,
        "window_duration": WINDOW_DURATION,
        "not_sufficient_alone": [
            "compute_success",
            "network_success",
            "Bernoulli(p_use)",
            "tau <= s_max",
        ],
        "requires_arrival_deadline_test": True,
    }
