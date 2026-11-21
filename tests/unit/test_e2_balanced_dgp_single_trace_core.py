"""Unit tests for E2 balanced DGP / single-trace certification repair."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1"
OUT = ROOT / "outputs/e2_balanced_dgp"
SEEDS = (29101, 29102, 29103, 29104, 29105)
BOUNDED_SRC = ROOT / "src/raven_mcs/e2/balanced_dgp/bounded_schedule.py"


def _j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_candidate_timestamp_within_window_bounds():
    audit = _j("outputs/audits/E2_BOUNDED_CANDIDATE_WINDOW_AUDIT.json")
    assert audit["status"] == "PASS"
    assert int(audit["future_candidate_count"]) == 0
    assert int(audit["pre_window_candidate_count"]) == 0


def test_no_future_suffix_candidate_pool():
    audit = _j("outputs/audits/E2_BOUNDED_CANDIDATE_WINDOW_AUDIT.json")
    assert audit.get("uses_pool_iloc_start_to_end") is False
    text = BOUNDED_SRC.read_text(encoding="utf-8")
    assert "iloc[start:n]" not in text
    assert "pool.iloc[start:" not in text


def test_no_pool_slice_start_to_end():
    text = BOUNDED_SRC.read_text(encoding="utf-8")
    assert "pool.iloc[start:n]" not in text
    assert "iloc[start:n]" not in text
    # Construction must mark windows as non-suffix.
    assert "uses_future_suffix" in text


def test_event_mass_not_calibration_weight():
    mass = _j("outputs/audits/E2_EVENT_MASS_SEMANTICS_AUDIT.json")
    assert mass["status"] == "PASS"
    assert mass["event_mass_depends_on_calibration"] is False
    assert float(mass["event_mass_value"]) == 1.0


def test_calibration_changes_p_opp():
    soft = _j("outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json")
    assert soft["calibration_target"] == "p_opp"
    assert soft["event_mass_unchanged"] is True
    assert float(soft["p_opp_std"]) > 0.0


def test_balanced_p_opp_not_constant_when_targets_differ():
    soft = _j("outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json")
    assert soft["status"] == "PASS"
    assert float(soft["p_opp_min"]) < float(soft["p_opp_max"])


def test_probability_bounds_respected():
    soft = _j("outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json")
    assert float(soft["p_opp_min"]) >= 0.05 - 1e-12
    assert float(soft["p_opp_max"]) <= 0.95 + 1e-12


def test_real_spatial_identity_source():
    spatial = _j("outputs/audits/E2_REAL_SPATIAL_IDENTITY_AUDIT.json")
    assert spatial["status"] == "PASS"
    assert int(spatial["synthetic_coordinate_usage_count"]) == 0
    assert "e1" in str(spatial["coordinate_source"]).lower() or "sensor" in str(spatial["coordinate_source"]).lower()


def test_synthetic_station_rank_coordinates_rejected():
    spatial = _j("outputs/audits/E2_REAL_SPATIAL_IDENTITY_AUDIT.json")
    src = str(spatial.get("coordinate_source", "")).lower()
    assert "lex" not in src
    assert "suffix" not in src
    assert "rank" not in src


def test_single_arm_audit_replicates():
    summary = _j("outputs/e2_balanced_dgp/E2_SINGLE_ARM_VARIANCE_SUMMARY.json")
    assert int(summary["n_replicates"]) == 200
    assert summary["antithetic_used"] is False
    frame = pd.read_csv(OUT / "E2_SINGLE_ARM_VARIANCE_BY_REPLICATE.csv")
    assert frame["audit_replicate"].nunique() == 200
    assert set(frame["version"]) >= {"V0", "V1", "V2", "V3"}


def test_antithetic_excluded_from_selection():
    sel = _j("outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json")
    assert sel.get("antithetic_used_for_selection") is False
    anti = _j("outputs/e2_balanced_dgp/E2_ANTITHETIC_SENSITIVITY_SUMMARY.json")
    assert anti.get("excluded_from_selection") is True
    assert anti.get("diagnostic_only") is True


def test_zero_arrival_rate_computed_from_events():
    summary = _j("outputs/e2_balanced_dgp/E2_SINGLE_ARM_VARIANCE_SUMMARY.json")
    v3 = summary["versions"]["V3"]
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        key = f"zero_arrival_rate_{level}"
        assert key in v3
        # Mean must be a computed float field (not a hardcoded sentinel missing from CSV).
        assert "mean" in v3[key]


def test_certification_gate_not_hardcoded_l32():
    gate_src = (ROOT / "scripts/check_e2_balanced_dgp_single_trace_gates.py").read_text(encoding="utf-8")
    assert 'selected_level") == "CERT-L32"' not in gate_src
    assert "selected == finest" in gate_src or "finest_feasible" in gate_src


def test_finest_feasible_certification_selected():
    sel = _j("outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json")
    feas = sel["feasibility"]
    finest = None
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        if feas[level]["feasible"]:
            finest = level
            break
    if finest is None:
        assert sel["status"] == "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE"
        assert sel.get("selected_level") in (None, "None")
    else:
        assert sel["status"] == "PASS"
        assert sel["selected_level"] == finest


def test_ledger_starts_with_prepare_generation():
    ledger = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        pytest.skip("ledger not written yet")
    first = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    assert first.get("label") in {"prepare", "prepare_generation", "bounded_prepare"}
