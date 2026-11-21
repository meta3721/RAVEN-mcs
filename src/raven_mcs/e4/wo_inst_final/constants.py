"""Constants for E4-WO-INST-REFERENCE-PENALTY-FINAL-CORRECTION-R1."""
from pathlib import Path

ROUND = "E4-WO-INST-REFERENCE-PENALTY-FINAL-CORRECTION-R1"
ART_NAME = "e4_wo_inst_reference_penalty_final_correction_r1"
PARENT_ART = "e4_ablation_semantic_integrity_repair_r1"
E4_ORIGINAL_ART = "e4_core_mechanism_ablation_r1"
E3_ART = "e3_formal_runs_r1"
SCENARIO = "complete_aligned"
DATASETS = ("sensorscope", "uair")
FORMAL_SEEDS = tuple(range(30001, 30021))
SMOKE_SEED = 32001
CORRECTIVE_METHOD = "raven_wo_inst"
ABLATIONS = (
    "raven_wo_design",
    "raven_wo_obs",
    "raven_wo_use",
    "raven_wo_inst",
    "raven_wo_debt",
)
REFERENCE_METHODS = ("raven",) + ABLATIONS
E3_METHODS_HASH = "0729a2d8435f6a81dec1b9724b9d01809d76c435e34a23ea704945baf6cf615d"
E3_WINDOW_RUNNER_HASH = (
    "f7bff5e30c76898f5ab3e3998021f9b09e52ccf73f135b44bc4e141d9e13c436"
)
EXPECTED_E3_LAMBDA_BETA = 1.0
GEN1_LAMBDA_BETA = 1e-8
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


def e4_original_path(root: Path) -> Path:
    return Path(root) / "artifacts" / E4_ORIGINAL_ART


def e3_path(root: Path) -> Path:
    return Path(root) / "artifacts" / E3_ART
