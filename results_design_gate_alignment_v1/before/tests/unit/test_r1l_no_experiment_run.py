from pathlib import Path
import ast
import json
ROOT = Path(__file__).resolve().parents[2]

def test_r1l_no_experiment_run() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1l.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
    assert "raven_mcs.experiments.sag_runtime" not in imported
    assert "sklearn" not in imported
    assert "sklearn.linear_model" not in imported
    verdict = json.loads((ROOT / "results_sag_g1/round_r1l/summary/R1L_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict.get("experiment_run") is False
    assert verdict.get("predictor_tuned") is False
    assert verdict.get("calibration_tuned") is False
