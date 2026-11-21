"""Unit tests for paper-data clean-and-package invariants."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper_ready_r1"


@pytest.mark.skipif(not PAPER.exists(), reason="paper_ready_r1 not built yet")
def test_e4_core_has_240_cells() -> None:
    path = PAPER / "01_core_data" / "e4" / "E4_FINAL_VALID_EVIDENCE_240.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 240


@pytest.mark.skipif(not PAPER.exists(), reason="paper_ready_r1 not built yet")
def test_e4_wo_inst_gen2_only_in_core() -> None:
    path = PAPER / "01_core_data" / "e4" / "E4_FINAL_VALID_EVIDENCE_240.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    wo = [r for r in rows if r.get("method_raw") == "raven_wo_inst"]
    assert len(wo) == 40
    assert all(str(r.get("generation")) == "2" for r in wo)


@pytest.mark.skipif(not PAPER.exists(), reason="paper_ready_r1 not built yet")
def test_traffic_not_in_main_e3_table() -> None:
    path = PAPER / "06_table_sources" / "TABLE_E3_MAIN_EFFECTIVENESS.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert all("Traffic" not in r.get("dataset", "") for r in rows)


@pytest.mark.skipif(not PAPER.exists(), reason="paper_ready_r1 not built yet")
def test_e2_counts() -> None:
    runs = PAPER / "01_core_data" / "e2" / "E2_FINAL_VALID_RUNS_600.csv"
    et = PAPER / "05_provenance" / "E2_EVENTTRACE_INDEX_120.csv"
    with runs.open(encoding="utf-8", newline="") as f:
        assert len(list(csv.DictReader(f))) == 600
    with et.open(encoding="utf-8", newline="") as f:
        assert len(list(csv.DictReader(f))) == 120


@pytest.mark.skipif(not PAPER.exists(), reason="paper_ready_r1 not built yet")
def test_zip_manifests_match() -> None:
    import json

    for name in ("CORE_ZIP_VERIFICATION.json", "FULL_EVIDENCE_ZIP_VERIFICATION.json"):
        payload = json.loads((PAPER / "09_archive_manifest" / name).read_text(encoding="utf-8"))
        assert payload.get("pass") is True
        assert payload.get("missing") == []
        assert payload.get("mismatch") == []
