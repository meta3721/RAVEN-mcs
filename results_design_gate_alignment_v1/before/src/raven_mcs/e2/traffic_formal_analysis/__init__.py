"""E2-TRAFFIC-FORMAL-RESULTS-AUDIT-AND-PAPER-ANALYSIS-R1 (no training)."""
from __future__ import annotations

FORMAL_SEEDS = list(range(30001, 30021))
SCENARIOS = [
    "balanced",
    "opportunity_only",
    "observation_only",
    "usable_only",
    "complete_aligned",
    "complete_counteracting",
]
SCENARIO_LABELS = {
    "balanced": "S1",
    "opportunity_only": "S2",
    "observation_only": "S3",
    "usable_only": "S4",
    "complete_aligned": "S5",
    "complete_counteracting": "S6",
}
METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
    "raven",
]
BASELINES = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
]
PRIMARY_METRICS = ["RMSE_mu", "RMSE_rho", "Gap_mis"]
# Smaller-is-better for error metrics. Gap_mis is signed; orientation documented in semantic audit.
METRIC_SMALLER_BETTER = {
    "RMSE_mu": True,
    "RMSE_rho": True,
    "Gap_mis": False,  # signed; not a pure "smaller better" misalignment magnitude
}
NON_BALANCED = [s for s in SCENARIOS if s != "balanced"]
EXPECTED_RUNS = 600
PRE_RUN_COMMIT = "e56687813f2bcb919a9208391f68a4db3488602e"
LATER_RUNTIME_COMMIT = "b01db69e8554a33446c438c060ac464dcfadac24"
ALPHA = 0.05
