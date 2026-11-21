"""Immutable constants for the E3 evidence-integrity closure."""

from __future__ import annotations

ROUND = "E3-FORMAL-EVIDENCE-INTEGRITY-AND-CLAIM-CLOSURE-R1"
ART_RELATIVE_PATH = "artifacts/e3_formal_evidence_integrity_and_claim_closure_r1"
PARENT_ART_RELATIVE_PATH = "artifacts/e3_formal_runs_r1"
E2_ART_RELATIVE_PATH = "artifacts/e2_traffic_formal_runs_r1"
EPS_ZERO = 1e-12
FORMAL_SEEDS = tuple(range(30001, 30021))
MAIN_BASELINES = (
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "local_hajek",
    "twostage_hajek",
)
SECONDARY_METRICS = ("Tail_RMSE_phys", "Delta_group", "Delta_c_s")
