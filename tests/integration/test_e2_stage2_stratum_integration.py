"""Integration tests for E2 Stage-2 stratum matrix and freeze artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.schedule import build_continuous_schedule
from raven_mcs.e2.stage2.gates import PROFILES, SCENARIOS, VALIDATION_SEEDS
from raven_mcs.e2.stage2.sampler import generate_stage2_mother_trace

ROOT = Path(__file__).resolve().parents[2]
DATA_OK = (ROOT / "data/processed/sensorscope/atomic_units.parquet").is_file()

REQUIRED_TRACE_FILES = (
    "manifest.json",
    "resolved_config.yaml",
    "continuous_schedule.parquet",
    "opportunity_events.parquet",
    "observation_events.parquet",
    "usable_events.parquet",
    "server_window_activity.parquet",
    "hard_arrival_events.parquet",
    "empirical_atomic_mass_100.parquet",
    "empirical_atomic_mass_200.parquet",
    "empirical_atomic_mass_300.parquet",
    "expected_atomic_mass_100.parquet",
    "expected_atomic_mass_200.parquet",
    "expected_atomic_mass_300.parquet",
    "group_mass_diagnostics_100.json",
    "group_mass_diagnostics_200.json",
    "group_mass_diagnostics_300.json",
    "stratum_mass_diagnostics_100.json",
    "stratum_mass_diagnostics_200.json",
    "stratum_mass_diagnostics_300.json",
    "failed_attempt_audit.json",
    "q_feature_audit.json",
    "stdout.log",
    "stderr.log",
)

COMPACT_DIAGNOSTIC_FILES = (
    "manifest.json",
    "group_mass_diagnostics_300.json",
    "stratum_mass_diagnostics_300.json",
    "failed_attempt_audit.json",
    "q_feature_audit.json",
)


def test_stage2_mother_trace_smoke_no_training() -> None:
    if not DATA_OK:
        pytest.skip("sensorscope processed data missing")
    seed = 29101
    streams = build_base_random_streams(
        seed, n_windows=300, n_clients=8, max_risk_set=20,
    )
    schedule = build_continuous_schedule(
        seed, schedule_uniforms=streams["base_client_window_schedule"], root=ROOT,
    )
    result = generate_stage2_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
        output_dir=None,
    )
    d = result["diagnostics"][300]
    assert d["D_TV_group"] <= 0.03
    assert d["D_TV_stratum"] <= 0.05
    assert 0.18 <= d["realized_observation_rate"] <= 0.22
    assert 0.57 <= d["realized_usable_rate"] <= 0.63
    assert result["manifest"]["stage2_eligibility_rule"] == "observed_count > 0"
    assert result["manifest"]["arr_audit"]["empirical_from_A_O_U"] is True
    assert result["activity_audit"]["active_window_equals_usable_rate_identically"] is False


def test_trace_matrix_complete_if_present() -> None:
    path = ROOT / "outputs/e2_stage2_stratum/E2_TRACE_MATRIX_SUMMARY.json"
    if not path.is_file():
        pytest.skip("matrix not generated yet")
    matrix = json.loads(path.read_text(encoding="utf-8"))
    assert matrix["trace_count"] == 180
    assert matrix["trace_failure_count"] == 0


def test_all_180_manifests_present() -> None:
    base = ROOT / "outputs/e2_stage2_stratum/traces"
    if not base.is_dir():
        pytest.skip("traces not generated yet")
    matrix_path = ROOT / "outputs/e2_stage2_stratum/E2_TRACE_MATRIX_SUMMARY.json"
    if not matrix_path.is_file():
        pytest.skip("matrix summary missing")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if int(matrix.get("trace_count") or 0) < 180:
        pytest.skip("full matrix not complete yet")
    count = 0
    for seed in VALIDATION_SEEDS:
        for profile in PROFILES:
            for scenario in SCENARIOS:
                manifest = base / str(seed) / profile / scenario / "manifest.json"
                if manifest.is_file():
                    count += 1
                else:
                    pytest.fail(f"missing manifest {manifest}")
    assert count == 180


def test_all_180_compact_diagnostics_present() -> None:
    base = ROOT / "outputs/e2_stage2_stratum/traces"
    if not base.is_dir():
        pytest.skip("traces not generated yet")
    matrix_path = ROOT / "outputs/e2_stage2_stratum/E2_TRACE_MATRIX_SUMMARY.json"
    if not matrix_path.is_file():
        pytest.skip("matrix summary missing")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if int(matrix.get("trace_count") or 0) < 180:
        pytest.skip("full matrix not complete yet")
    for seed in VALIDATION_SEEDS:
        for profile in PROFILES:
            for scenario in SCENARIOS:
                trace_dir = base / str(seed) / profile / scenario
                missing = [f for f in COMPACT_DIAGNOSTIC_FILES if not (trace_dir / f).is_file()]
                assert not missing, f"{trace_dir}: missing {missing}"


def test_selected_profile_and_window_frozen_if_present() -> None:
    prof = ROOT / "configs/frozen/e2_stage2_stratum/selected_strength_profile.yaml"
    win = ROOT / "configs/frozen/e2_stage2_stratum/selected_window_length.yaml"
    if not prof.is_file() or not win.is_file():
        pytest.skip("freeze artifacts not present yet")
    p = yaml.safe_load(prof.read_text(encoding="utf-8"))
    w = yaml.safe_load(win.read_text(encoding="utf-8"))
    assert p["selected_profile_id"].startswith("PROFILE-S")
    assert int(w["selected_windows"]) in (100, 200, 300)
    assert p["revalidated_on_stage2_and_true_stratum"] is True


def test_profile_selection_status_if_present() -> None:
    path = ROOT / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json"
    if not path.is_file():
        pytest.skip("selection not generated yet")
    sel = json.loads(path.read_text(encoding="utf-8"))
    assert sel["status"] in {"SELECTED", "NO_VALID_STAGE2_STRATUM_PROFILE", "TRACE_MATRIX_FAIL"}
    if sel["status"] == "SELECTED":
        assert sel["selected_profile_id"] in PROFILES
        assert sel.get("revalidated_on_stage2_and_true_stratum") is True


def test_failed_attempt_audit_if_present() -> None:
    path = ROOT / "outputs/audits/E2_FAILED_ATTEMPT_RETENTION_AUDIT.json"
    if not path.is_file():
        pytest.skip("failed attempt audit not generated yet")
    audit = json.loads(path.read_text(encoding="utf-8"))
    assert audit["status"] == "PASS"
    assert int(audit["missing_failed_attempt_count"]) == 0
    assert int(audit["extra_failed_attempt_count"]) == 0


def test_chronology_audit_if_present() -> None:
    path = ROOT / "outputs/audits/E2_CHRONOLOGICAL_ORDER_AUDIT.json"
    if not path.is_file():
        pytest.skip("chronology audit not generated yet")
    audit = json.loads(path.read_text(encoding="utf-8"))
    assert audit["chronological_order_status"] == "PASS"


def test_true_stratum_status_if_present() -> None:
    path = ROOT / "outputs/audits/E2_TRUE_STRATUM_STATUS.json"
    if not path.is_file():
        pytest.skip("stratum status not generated yet")
    audit = json.loads(path.read_text(encoding="utf-8"))
    assert audit["status"] == "PASS"
    assert audit["role_substitution"] is False


def test_required_trace_files_if_present() -> None:
    base = ROOT / "outputs/e2_stage2_stratum/traces"
    if not base.is_dir():
        pytest.skip("traces not generated yet")
    matrix_path = ROOT / "outputs/e2_stage2_stratum/E2_TRACE_MATRIX_SUMMARY.json"
    if not matrix_path.is_file():
        pytest.skip("matrix summary missing")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if int(matrix.get("trace_count") or 0) < 180:
        pytest.skip("full matrix not complete yet")
    sel_path = ROOT / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json"
    selected = None
    if sel_path.is_file():
        selected = json.loads(sel_path.read_text(encoding="utf-8")).get(
            "selected_profile_id"
        )
    present_profiles = sorted({p.name for p in base.glob("*/*") if p.is_dir()})
    for seed in VALIDATION_SEEDS:
        for profile in present_profiles:
            for scenario in SCENARIOS:
                trace_dir = base / str(seed) / profile / scenario
                if not trace_dir.is_dir():
                    pytest.fail(f"missing trace dir {trace_dir}")
                # Evidence ZIP: all 180 compact diagnostics; full events only for selected.
                if (trace_dir / "hard_arrival_events.parquet").is_file():
                    required = [
                        f for f in REQUIRED_TRACE_FILES
                        if not f.startswith("empirical_atomic_mass_")
                        and not f.startswith("expected_atomic_mass_")
                    ]
                else:
                    required = list(COMPACT_DIAGNOSTIC_FILES)
                missing = [f for f in required if not (trace_dir / f).is_file()]
                assert not missing, f"{trace_dir}: missing {missing}"
        if selected:
            for scenario in SCENARIOS:
                sel_dir = base / str(seed) / selected / scenario
                assert (sel_dir / "hard_arrival_events.parquet").is_file()


def test_gates_json_if_present() -> None:
    path = ROOT / "outputs/gates/E2_STAGE2_ELIGIBILITY_AND_TRUE_STRATUM_REFREEZE_R1_GATES.json"
    if not path.is_file():
        pytest.skip("gates not generated yet")
    gates = json.loads(path.read_text(encoding="utf-8"))
    assert "gates" in gates
    assert all(k.startswith("E2SR-G") for k in gates["gates"])


def test_window_stability_selection_if_present() -> None:
    path = ROOT / "outputs/e2_stage2_stratum/E2_WINDOW_SELECTION.json"
    if not path.is_file():
        pytest.skip("window selection not generated yet")
    win = json.loads(path.read_text(encoding="utf-8"))
    assert win["selected_windows"] in (100, 200, 300)
    assert win.get("prior_300_not_preferred") is True
