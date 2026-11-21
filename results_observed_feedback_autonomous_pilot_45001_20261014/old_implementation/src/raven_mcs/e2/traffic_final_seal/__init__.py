"""E2-TRAFFIC-NUMERICAL-TOLERANCE-AND-FINAL-CLAIM-SEAL-R1."""
from __future__ import annotations

EPS_ZERO = 1e-12
ALPHA = 0.05
FORMAL_SEEDS = list(range(30001, 30021))
SCENARIOS = [
    "balanced",
    "opportunity_only",
    "observation_only",
    "usable_only",
    "complete_aligned",
    "complete_counteracting",
]
METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
    "raven",
]
BASELINES = [m for m in METHODS if m != "raven"]
NON_BALANCED = [s for s in SCENARIOS if s != "balanced"]
STRUCTURAL_METRICS = ["Head_RMSE", "Tail_RMSE", "Delta_group"]


def apply_eps_zero(diff, eps: float = EPS_ZERO):
    import numpy as np

    arr = np.asarray(diff, dtype=np.float64).copy()
    arr[np.abs(arr) <= eps] = 0.0
    return arr
