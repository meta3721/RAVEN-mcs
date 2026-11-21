"""Constants for E3 real-runner pair/oracle correctness closure."""

from __future__ import annotations

ROUND = "E3-REAL-RUNNER-PAIR-ORACLE-CORRECTNESS-CLOSURE-R1"
FORMAL_SEEDS = list(range(30001, 30021))
CANARY_SEED = 31001
DEBUG_SEED = 31999  # non-paper correctness smoke only
EPS_ZERO = 1e-12
M_MC = 2000
M_MC_CHECK = 10000
S_MAX = 5
WINDOW_DURATION = 1.0
PAIR_SCHEMA_VERSION = "E3_PAIR_STATE_SCHEMA_V3"
GENERATOR_VERSION = "e3-complete-aligned-r3-v1"
REGISTRY_SHA256 = "7d9b8292522b6fbcc15d83ebb065fc8a73b79787ed643aea49c48f30596acbc7"

E2_TRAFFIC_REUSED_METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
    "raven",
]

FEDERATED_METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "local_hajek",
    "twostage_hajek",
    "inst_cal",
    "debt_cal",
    "raven",
    "raven_simoracle",
]

CENTRAL_METHODS = ["central_all", "central_delivered"]
