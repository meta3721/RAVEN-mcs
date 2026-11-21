from pathlib import Path
import ast
import json

ROOT = Path(__file__).resolve().parents[2]


def test_no_new_experiment_run() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1l_v11.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert "raven_mcs.experiments.sag_runtime" not in imported
    verdict = json.loads(
        (ROOT / "results_sag_g1/round_r1l_v11/summary/R1L_V11_VERDICT.json").read_text(encoding="utf-8")
    )
    assert verdict.get("experiment_run") is False
    assert verdict.get("predictor_tuned") is False

    v12_src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1l_v12.py").read_text(encoding="utf-8")
    tree12 = ast.parse(v12_src)
    imported12 = set()
    for node in ast.walk(tree12):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported12.add(node.module)
    assert "raven_mcs.experiments.sag_runtime" not in imported12
    v12 = json.loads(
        (ROOT / "results_sag_g1/round_r1l_v12/summary/R1L_V12_VERDICT.json").read_text(encoding="utf-8")
    )
    assert v12.get("experiment_run") is False
    assert v12.get("predictor_tuned") is False

    v13_src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1l_v13.py").read_text(encoding="utf-8")
    tree13 = ast.parse(v13_src)
    imported13 = set()
    for node in ast.walk(tree13):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported13.add(node.module)
    assert "raven_mcs.experiments.sag_runtime" not in imported13
    v13 = json.loads(
        (ROOT / "results_sag_g1/round_r1l_v13/summary/R1L_V13_VERDICT.json").read_text(encoding="utf-8")
    )
    assert v13.get("experiment_run") is False
    assert v13.get("predictor_tuned") is False


def test_no_r1m_started() -> None:
    assert not (ROOT / "results_sag_g1/round_r1m").exists()
    verdict = json.loads(
        (ROOT / "results_sag_g1/round_r1l_v11/summary/R1L_V11_VERDICT.json").read_text(encoding="utf-8")
    )
    assert verdict.get("r1m_started") is False
    v12 = json.loads(
        (ROOT / "results_sag_g1/round_r1l_v12/summary/R1L_V12_VERDICT.json").read_text(encoding="utf-8")
    )
    assert v12.get("r1m_started") is False
    v13 = json.loads(
        (ROOT / "results_sag_g1/round_r1l_v13/summary/R1L_V13_VERDICT.json").read_text(encoding="utf-8")
    )
    assert v13.get("r1m_started") is False
