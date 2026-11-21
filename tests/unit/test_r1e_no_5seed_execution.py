"""R1e must not start a 5-seed campaign."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "raven_mcs" / "experiments" / "run_sag_g1_r1e.py"


def test_r1e_no_5seed_execution() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "range(30001, 30006)" not in text
    assert "SEEDS = (30001,)" in text or "SEED = 30001" in text
    verdict_path = ROOT / "outputs" / "sag_g1_r1e" / "report" / "R1E_VERDICT.json"
    if verdict_path.is_file():
        payload = json.loads(verdict_path.read_text(encoding="utf-8"))
        assert payload.get("five_seed_started") is False
