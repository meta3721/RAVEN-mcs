"""Frozen E4 protocol constants."""
from pathlib import Path

ROUND = "E4-CORE-MECHANISM-ABLATION-R1"
ART_NAME = "e4_core_mechanism_ablation_r1"
SCENARIO = "complete_aligned"
DATASETS = ("sensorscope", "uair")
FORMAL_SEEDS = tuple(range(30001, 30021))
SMOKE_SEED = 32001
ABLATIONS = (
    "raven_wo_design", "raven_wo_obs", "raven_wo_use",
    "raven_wo_inst", "raven_wo_debt",
)

def art_path(root: Path) -> Path:
    return Path(root) / "artifacts" / ART_NAME
