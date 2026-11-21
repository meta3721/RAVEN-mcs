from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_optional_drift_omitted() -> None:
    text = (ROOT / "results_sag_g1/round_r1l/theory/R1L_OPTIONAL_DRIFT_EXTENSION_OMITTED.md").read_text(encoding="utf-8")
    assert "omitted" in text.lower()
    payload = json.loads((ROOT / "results_sag_g1/round_r1l/theory/R1L_THEORY_STACK.json").read_text(encoding="utf-8"))
    assert payload["optional_bounded_drift_extension"] is False
