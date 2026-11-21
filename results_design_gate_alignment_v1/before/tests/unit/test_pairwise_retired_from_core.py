from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_pairwise_retired_from_core() -> None:
    payload = json.loads((ROOT / "results_sag_g1/round_r1l/theory/R1L_THEORY_STACK.json").read_text(encoding="utf-8"))
    assert payload["pairwise_formal_core"] is False
    assert payload.get("formal_cov_mode") == "aggregate_stable_regime"
    stack = (ROOT / "results_sag_g1/round_r1l/theory/R1L_THEORY_STACK.md").read_text(encoding="utf-8")
    assert "retired from the formal core" in stack
    wr = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    assert 'sag_cov_mode", "aggregate_stable_regime"' in wr
