"""Constants for E3 target-pair-metric final integration closure."""

from __future__ import annotations

ROUND = "E3-TARGET-PAIR-METRIC-FINAL-INTEGRATION-CLOSURE-R1"
CANARY_SEED = 31001
DEBUG_SEED = 32999  # non-paper nondegenerate correctness smoke
FORMAL_SEEDS = list(range(30001, 30021))
PAIR_SCHEMA_VERSION = "E3_PAIR_STATE_SCHEMA_V4"
METRIC_SCHEMA_VERSION = "E3_REAL_METRIC_OUTPUT_SCHEMA_V4"
REGISTRY_SHA256 = "7d9b8292522b6fbcc15d83ebb065fc8a73b79787ed643aea49c48f30596acbc7"
M_MC = 2000

E2_TRAFFIC_REUSED_METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
    "raven",
]

FROZEN_TARGET_ARTIFACTS = {
    "sensorscope": "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json",
    "uair": "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_UAIR_TARGET_SEMANTICS_R2.json",
}

# Canonical pair domain: client × spatial×time target group
PAIR_DOMAIN = "client × target_group (spatial×time)"
