"""R1f must not start SAG."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_sag_started() -> None:
    verdict = ROOT / "results_sag_g1/round_r1f/summary/R1F_VERDICT.json"
    payload = json.loads(verdict.read_text(encoding="utf-8"))
    assert payload.get("sag_started") is False
    r1g = ROOT / "results_sag_g1/round_r1g/summary/R1G_VERDICT.json"
    if r1g.is_file():
        payload = json.loads(r1g.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1h = ROOT / "results_sag_g1/round_r1h/summary/R1H_VERDICT.json"
    if r1h.is_file():
        payload = json.loads(r1h.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1i = ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json"
    if r1i.is_file():
        payload = json.loads(r1i.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1j = ROOT / "results_sag_g1/round_r1j/summary/R1J_VERDICT.json"
    if r1j.is_file():
        payload = json.loads(r1j.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1k = ROOT / "results_sag_g1/round_r1k/summary/R1K_VERDICT.json"
    if r1k.is_file():
        payload = json.loads(r1k.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1l = ROOT / "results_sag_g1/round_r1l/summary/R1L_VERDICT.json"
    if r1l.is_file():
        payload = json.loads(r1l.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1lv11 = ROOT / "results_sag_g1/round_r1l_v11/summary/R1L_V11_VERDICT.json"
    if r1lv11.is_file():
        payload = json.loads(r1lv11.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1lv12 = ROOT / "results_sag_g1/round_r1l_v12/summary/R1L_V12_VERDICT.json"
    if r1lv12.is_file():
        payload = json.loads(r1lv12.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1lv13 = ROOT / "results_sag_g1/round_r1l_v13/summary/R1L_V13_VERDICT.json"
    if r1lv13.is_file():
        payload = json.loads(r1lv13.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
    r1m = ROOT / "results_sag_g1/round_r1m/summary/R1M_VERDICT.json"
    if r1m.is_file():
        payload = json.loads(r1m.read_text(encoding="utf-8"))
        assert payload.get("sag_started") is False
