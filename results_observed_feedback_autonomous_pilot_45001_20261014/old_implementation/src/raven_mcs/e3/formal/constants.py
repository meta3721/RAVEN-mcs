"""Immutable schedule constants for E3-FORMAL-RUNS-R1."""
from __future__ import annotations

from pathlib import Path

ROUND = "E3-FORMAL-RUNS-R1"
ART_RELATIVE_PATH = "artifacts/e3_formal_runs_r1"
FORMAL_SEEDS = list(range(30001, 30021))
CANARY_SEED = 31001
SCENARIO = "complete_aligned"
DATASETS = ("sensorscope", "uair", "traffic")
ALL_METHODS = (
    "fedavg_window", "fedasync_window", "flamf_timealign_adapted", "local_hajek",
    "twostage_hajek", "inst_cal", "debt_cal", "raven", "raven_simoracle",
    "central_all", "central_delivered",
)
REUSED_TRAFFIC_METHODS = (
    "fedavg_window", "fedasync_window", "flamf_timealign_adapted", "twostage_hajek", "raven",
)
NEW_TRAFFIC_METHODS = tuple(m for m in ALL_METHODS if m not in REUSED_TRAFFIC_METHODS)
N_SENSOR_SCOPE = 220
N_UAIR = 220
N_TRAFFIC_NEW = 120
N_NEW = 560
N_REUSED = 100
N_TOTAL = 660
E2_ART_RELATIVE_PATH = "artifacts/e2_traffic_formal_runs_r1"
REUSE_MANIFEST_RELATIVE_PATH = "artifacts/e3_protocol_reuse_and_readiness_r1/E3_REUSED_E2_TRAFFIC_BLOCK_MANIFEST.json"

def art_path(root: Path) -> Path:
    return root / ART_RELATIVE_PATH
