"""E2-TRAFFIC-OFFLINE-METRIC-RECONSTRUCTION-AND-CLAIM-CORRECTION-R1."""
from __future__ import annotations

ROUND = "E2-TRAFFIC-OFFLINE-METRIC-RECONSTRUCTION-AND-CLAIM-CORRECTION-R1"
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
STRUCTURAL_METRICS = ["Head_RMSE", "Tail_RMSE", "Delta_group", "Delta_pair"]
HEAD_GROUPS = ("block0", "block1")
TAIL_GROUPS = ("block2", "block3")
ALPHA = 0.05
EXPECTED_RUNS = 600
