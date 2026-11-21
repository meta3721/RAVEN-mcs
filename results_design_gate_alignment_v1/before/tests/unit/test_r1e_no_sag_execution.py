"""R1e source and verdict must not start SAG."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "raven_mcs" / "experiments" / "run_sag_g1_r1e.py"


def test_r1e_no_sag_execution() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "build_full_runner" not in text
    assert "sag_allowed" in text
    assert "False" in text
    verdict_path = ROOT / "outputs" / "sag_g1_r1e" / "report" / "R1E_VERDICT.json"
    if verdict_path.is_file():
        payload = json.loads(verdict_path.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
