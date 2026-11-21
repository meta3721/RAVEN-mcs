"""E3-PROTOCOL-REUSE-AND-READINESS-R1 (no training)."""
from __future__ import annotations

ROUND = "E3-PROTOCOL-REUSE-AND-READINESS-R1"
E2_FORMAL_SEEDS = list(range(30001, 30021))
E3_FORMAL_SEEDS = list(range(30001, 30021))  # reuse labels where identity permits
CANARY_SEED = 31001  # outside E1/E2 formal ranges
E2_TRAFFIC_METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
    "raven",
]
EPS_ZERO = 1e-12
REGISTRY_SHA256 = "7d9b8292522b6fbcc15d83ebb065fc8a73b79787ed643aea49c48f30596acbc7"
