import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "src/raven_mcs/experiments/run_sag_g1_r1m.py"
EVAL = ROOT / "src/raven_mcs/sag/r1m_eval.py"


def test_r1m_verdict_not_hardcoded() -> None:
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    assigned = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "verdict" and isinstance(node.value, ast.Constant):
                    assigned.append(node.value.value)
    assert not assigned
    eval_src = EVAL.read_text(encoding="utf-8")
    assert "def overall_verdict(" in eval_src
    runner = RUNNER.read_text(encoding="utf-8")
    assert "overall_verdict(" in runner
    assert 'executive_verdict": verdict' in runner or '"executive_verdict": verdict' in runner
