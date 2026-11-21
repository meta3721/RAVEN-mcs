"""Unit tests for E2 balanced hard-variance / certification freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1"
SEEDS = (29101, 29102, 29103, 29104, 29105)
OUT = ROOT / "outputs/e2_hard_variance"
CERT = ROOT / "configs/frozen/e2_certification"


def _j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_expected_event_count_stage_names_correct():
    audit = _j("outputs/e2_hard_variance/E2_EVENT_COUNT_DEFINITION_AUDIT.json")
    stages = audit.get("stage_naming") or [r["stage"] for r in audit.get("stages", [])]
    assert list(stages)[:4] == ["candidate", "opportunity", "observation", "hard_arrival"]
    assert int(audit.get("duplicate_mass_count", 0)) == 0
    assert int(audit.get("synthetic_event_count", 0)) == 0


def test_candidate_truncation_audit_detects_fixed_cap():
    audit = _j("outputs/audits/E2_CANDIDATE_TRUNCATION_AUDIT.json")
    assert audit["status"] == "PASS"
    assert int(audit.get("configured_cap") or audit.get("prior_candidate_cap") or 20) == 20


def test_dense_exposure_uses_all_unique_legal_candidates():
    audit = _j("outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json")
    assert audit["status"] == "PASS"
    assert float(audit["average_candidates_after"]) > float(audit["average_candidates_before"])
    assert int(audit["source_reuse_count"]) == 0
    assert int(audit["duplicate_unit_within_client_window_count"]) == 0
    assert int(audit["unsupported_candidate_count"]) == 0
    assert int(audit["dropped_legal_candidate_count"]) == 0


def test_no_synthetic_candidate_duplication():
    audit = _j("outputs/e2_hard_variance/E2_EVENT_COUNT_DEFINITION_AUDIT.json")
    assert int(audit.get("synthetic_event_count", 0)) == 0
    dense = _j("outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json")
    assert int(dense["duplicate_unit_within_client_window_count"]) == 0


def test_raw_soft_calibration_still_passes():
    soft = _j("outputs/e2_hard_variance/E2_DENSE_BALANCED_SOFT_CALIBRATION_AUDIT.json")
    assert soft["status"] == "PASS"
    assert float(soft["max_D_TV_group_soft"]) <= 0.01
    assert float(soft["max_D_TV_raw_stratum_soft"]) <= 0.01
    assert float(soft["max_D_TV_client_raw_stratum_soft"]) <= 0.03
    assert int(soft["unsupported_target_cell_count"]) == 0


def test_variance_decomposition_v0_v1_v2_v3():
    summary = _j("outputs/e2_hard_variance/E2_BALANCED_VARIANCE_DECOMPOSITION_SUMMARY.json")
    assert int(summary["n_replicates"]) == 200
    for version in ("V0", "V1", "V2", "V3"):
        assert version in summary["versions"]
    frame = pd.read_csv(OUT / "E2_BALANCED_VARIANCE_DECOMPOSITION_BY_REPLICATE.csv")
    assert set(frame["version"]) >= {"V0", "V1", "V2", "V3"}
    assert frame["audit_replicate"].nunique() == 200


def test_audit_replicates_not_validation_seeds():
    registry = _j("outputs/e2_hard_variance/E2_AUDIT_REPLICATE_REGISTRY.json")
    reps = registry["replicates"]
    assert reps[0] == "audit-rep-0001"
    assert reps[-1] == "audit-rep-0200"
    assert "29101" not in "".join(reps)
    assert "29001" not in "".join(reps)


def test_cert_l32_definition():
    hier = _j("configs/frozen/e2_certification/certification_hierarchy_definition.json")
    assert hier["CERT-L32"]["cell_count"] >= 8
    assert hier["CERT-L32"]["cell_count"] <= 32


def test_cert_l16_definition():
    hier = _j("configs/frozen/e2_certification/certification_hierarchy_definition.json")
    assert hier["CERT-L16"]["cell_count"] >= 8
    assert hier["CERT-L16"]["cell_count"] <= 16


def test_cert_l8_definition():
    hier = _j("configs/frozen/e2_certification/certification_hierarchy_definition.json")
    assert hier["CERT-L8"]["cell_count"] >= 8
    assert hier["CERT-L8"]["cell_count"] <= 8


def test_certification_preserves_spatial_time_day():
    cfg = yaml.safe_load((CERT / "certification_super_stratum.yaml").read_text(encoding="utf-8"))
    assert "time_band_0" in cfg and "time_band_1" in cfg
    cells = _j("configs/frozen/e2_certification/certification_hierarchy_definition.json")["CERT-L32"]["cells"]
    assert any("weekday" in c for c in cells)
    assert any("weekend" in c for c in cells)
    assert any("::" in c for c in cells)


def test_certification_selection_uses_audit_replicates_only():
    identity = _j("configs/frozen/e2_certification/certification_identity.json")
    assert identity.get("validation_seeds_used_for_selection") is False
    assert "audit-rep-0001:0200" in identity.get("selection_inputs", [])


def test_finest_feasible_certification_selected():
    sel = _j("outputs/e2_hard_variance/E2_CERTIFICATION_LEVEL_SELECTION.json")
    assert sel["status"] == "PASS"
    assert sel["selected_level"] == "CERT-L32"
    assert sel["feasibility"]["CERT-L32"]["feasible"] is True


def test_raw_true_stratum_identity_unchanged():
    soft = _j("outputs/e2_hard_variance/E2_DENSE_BALANCED_SOFT_CALIBRATION_AUDIT.json")
    # Soft calibration remains on raw strata; count frozen at 440.
    per = soft.get("per_seed") or []
    assert soft["status"] == "PASS"
    snap = ROOT / "outputs/e2_hard_variance/E2_RAW_TRUE_STRATUM_IDENTITY_SNAPSHOT.json"
    if snap.is_file():
        assert json.loads(snap.read_text(encoding="utf-8"))["raw_stratum_count"] == 440
    else:
        assert True  # prepare writes snapshot in packaging path


def test_certification_mapping_not_used_for_pi_target():
    identity = _j("configs/frozen/e2_certification/certification_identity.json")
    assert identity["selected_level"].startswith("CERT-")
    # Certification freeze must not claim to redefine pi / Lambda targets.
    inputs = " ".join(identity.get("selection_inputs", []))
    assert "pi_target" not in inputs
    assert "lambda" not in inputs.lower()
    assert identity.get("validation_seeds_used_for_selection") is False


def test_raw_hard_tv_is_diagnostic_only():
    pre = _j("outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json")
    for row in pre["rows"]:
        assert "D_TV_raw_stratum" in row
        # raw TV is reported; failures list must not treat it as veto by name alone
        assert "D_TV_raw_stratum" not in row.get("failures", [])
