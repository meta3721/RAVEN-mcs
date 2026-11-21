"""R1f runner must not repair predictor."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src/raven_mcs/experiments/run_sag_g1_r1f.py"


def test_no_predictor_repair() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "predictor_repair_executed" in text
    assert "TOD_CONDITIONED" not in text
    import json

    freeze = ROOT / "results_sag_g1/round_r1f/audit/R1F_FREEZE_AUDIT.json"
    if freeze.is_file():
        payload = json.loads(freeze.read_text(encoding="utf-8"))
        assert payload.get("predictor_repair_executed") is False
    r1g = ROOT / "results_sag_g1/round_r1g/summary/R1G_VERDICT.json"
    r1h = ROOT / "results_sag_g1/round_r1h/summary/R1H_VERDICT.json"
    if r1g.is_file():
        payload = json.loads(r1g.read_text(encoding="utf-8"))
        assert payload.get("predictor_repair_executed") is False
    if r1h.is_file():
        payload = json.loads(r1h.read_text(encoding="utf-8"))
        assert payload.get("predictor_repair_executed") is False
    r1i = ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json"
    if r1i.is_file():
        payload = json.loads(r1i.read_text(encoding="utf-8"))
        assert payload.get("predictor_repair_executed") is False
