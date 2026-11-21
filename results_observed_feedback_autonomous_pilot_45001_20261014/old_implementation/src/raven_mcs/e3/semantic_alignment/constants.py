"""Constants for E3 semantic alignment closure."""

from __future__ import annotations

ROUND = "E3-SEMANTIC-ALIGNMENT-AND-RUNNER-INTEGRATION-CLOSURE-R1"
FORMAL_SEEDS = list(range(30001, 30021))
CANARY_SEED = 31001
EPS_ZERO = 1e-12
M_MC = 2000
M_MC_CHECK = 10000
S_MAX = 5
WINDOW_DURATION = 1.0
GENERATOR_VERSION = "e3-complete-aligned-r2-v1"
PAIR_STATE_SCHEMA_VERSION = "E3_PAIR_STATE_SCHEMA_V2"
REGISTRY_SHA256 = "7d9b8292522b6fbcc15d83ebb065fc8a73b79787ed643aea49c48f30596acbc7"

E2_TRAFFIC_REUSED_METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
    "raven",
]

DATASETS = ("sensorscope", "uair", "traffic")
SCENARIO = "complete_aligned"
