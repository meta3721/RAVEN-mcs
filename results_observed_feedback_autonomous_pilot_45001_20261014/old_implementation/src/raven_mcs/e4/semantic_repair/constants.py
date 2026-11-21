"""Constants for E4-ABLATION-SEMANTIC-INTEGRITY-REPAIR-R1."""
from pathlib import Path

ROUND = "E4-ABLATION-SEMANTIC-INTEGRITY-REPAIR-R1"
ART_NAME = "e4_ablation_semantic_integrity_repair_r1"
PARENT_ART = "e4_core_mechanism_ablation_r1"
E3_ART = "e3_formal_runs_r1"
SCENARIO = "complete_aligned"
DATASETS = ("sensorscope", "uair")
FORMAL_SEEDS = tuple(range(30001, 30021))
SMOKE_SEED = 32001
ABLATIONS = (
    "raven_wo_design",
    "raven_wo_obs",
    "raven_wo_use",
    "raven_wo_inst",
    "raven_wo_debt",
)
CORRECTIVE_METHOD = "raven_wo_inst"
REFERENCE_METHODS = ("raven",) + ABLATIONS
FLAGS = (
    "uses_design_ratio",
    "uses_observation_ipw",
    "uses_usable_ipw",
    "uses_instant_calibration",
    "uses_debt",
)
METHOD_DISABLED_FLAG = {
    "raven_wo_design": "uses_design_ratio",
    "raven_wo_obs": "uses_observation_ipw",
    "raven_wo_use": "uses_usable_ipw",
    "raven_wo_inst": "uses_instant_calibration",
    "raven_wo_debt": "uses_debt",
}
E3_WINDOW_RUNNER_HASH = (
    "f7bff5e30c76898f5ab3e3998021f9b09e52ccf73f135b44bc4e141d9e13c436"
)
E4_WINDOW_RUNNER_HASH_PRE = (
    "3d44cecb6fb08d843f582f41799da99c590ee2676effdd9e7ec5a8c11004144e"
)
CRITICAL_SOURCES = (
    "src/raven_mcs/aggregation/feasibility.py",
    "src/raven_mcs/aggregation/method_policy.py",
    "src/raven_mcs/aggregation/methods.py",
    "src/raven_mcs/aggregation/p2_cvxpy.py",
    "src/raven_mcs/training/window_runner.py",
    "src/raven_mcs/e3/real_runner/runner.py",
    "src/raven_mcs/e4/execute.py",
)


def art_path(root: Path) -> Path:
    return Path(root) / "artifacts" / ART_NAME


def parent_path(root: Path) -> Path:
    return Path(root) / "artifacts" / PARENT_ART


def e3_path(root: Path) -> Path:
    return Path(root) / "artifacts" / E3_ART
