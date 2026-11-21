"""Integration tests for E2 empirical EventTrace matrix and freeze artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from raven_mcs.e2.empirical.gates import PROFILES, SCENARIOS, VALIDATION_SEEDS
from raven_mcs.e2.empirical.sampler import generate_empirical_mother_trace
from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.schedule import build_continuous_schedule

ROOT = Path(__file__).resolve().parents[2]
DATA_OK = (ROOT / "data/processed/sensorscope/atomic_units.parquet").is_file()

REQUIRED_TRACE_FILES = (
    "manifest.json",
    "resolved_config.yaml",
    "continuous_schedule.parquet",
    "opportunity_events.parquet",
    "observation_events.parquet",
    "usable_events.parquet",
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
    "stdout.log",
    "stderr.log",
)


def test_empirical_mother_trace_smoke_no_training() -> None:
    if not DATA_OK:
        pytest.skip("sensorscope processed data missing")
    seed = 29101
    streams = build_base_random_streams(
        seed, n_windows=300, n_clients=8, max_risk_set=20,
    )
    schedule = build_continuous_schedule(
        seed, schedule_uniforms=streams["base_client_window_schedule"], root=ROOT,
    )
    result = generate_empirical_mother_trace(
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
    assert result["manifest"]["model_training"] is False
    assert result["manifest"]["arr_audit"]["empirical_from_A_O_U"] is True


def test_trace_matrix_complete_if_present() -> None:
    path = ROOT / "outputs/e2_empirical/E2_EMPIRICAL_TRACE_MATRIX_SUMMARY.json"
    if not path.is_file():
        pytest.skip("matrix not generated yet")
    matrix = json.loads(path.read_text(encoding="utf-8"))
    assert matrix["trace_count"] == 180
    assert matrix["trace_failure_count"] == 0


def test_selected_profile_and_window_frozen_if_present() -> None:
    prof = ROOT / "configs/frozen/e2_empirical/selected_strength_profile.yaml"
    win = ROOT / "configs/frozen/e2_empirical/selected_window_length.yaml"
    if not prof.is_file() or not win.is_file():
        pytest.skip("freeze artifacts not present yet")
    p = yaml.safe_load(prof.read_text(encoding="utf-8"))
    w = yaml.safe_load(win.read_text(encoding="utf-8"))
    assert p["selected_profile_id"].startswith("PROFILE-S")
    assert int(w["selected_windows"]) in (100, 200, 300)
    assert p["revalidated_on_hard_empirical"] is True


def test_profile_selection_status_if_present() -> None:
    path = ROOT / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json"
    if not path.is_file():
        pytest.skip("selection not generated yet")
    sel = json.loads(path.read_text(encoding="utf-8"))
    assert sel["status"] in {"SELECTED", "NO_VALID_EMPIRICAL_DISTRIBUTION_PROFILE", "TRACE_MATRIX_FAIL"}
    if sel["status"] == "SELECTED":
        assert sel["selected_profile_id"] in PROFILES
        assert sel.get("revalidated_on_hard_empirical") is True


def test_schedule_nonrepetition_audit_if_present() -> None:
    path = ROOT / "outputs/audits/E2_300_WINDOW_SCHEDULE_NONREPETITION_AUDIT.json"
    if not path.is_file():
        pytest.skip("schedule audit not generated yet")
    audit = json.loads(path.read_text(encoding="utf-8"))
    assert audit["status"] == "PASS"
    assert audit["schedule_uniforms_used_all"] is True
    assert audit["block_hashes_all_equal_any"] is False


def test_required_trace_files_if_present() -> None:
    base = ROOT / "outputs/e2_empirical/traces"
    if not base.is_dir():
        pytest.skip("traces not generated yet")
    matrix_path = ROOT / "outputs/e2_empirical/E2_EMPIRICAL_TRACE_MATRIX_SUMMARY.json"
    if not matrix_path.is_file():
        pytest.skip("matrix summary missing")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if int(matrix.get("trace_count") or 0) < 180:
        pytest.skip("full matrix not complete yet")
    # Evidence ZIP may ship only the selected-profile traces.
    present_profiles = sorted({p.name for p in base.glob("*/*") if p.is_dir()})
    profiles_to_check = list(PROFILES)
    if len(present_profiles) == 1:
        profiles_to_check = present_profiles
    elif len(present_profiles) < len(PROFILES):
        sel_path = ROOT / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json"
        if sel_path.is_file():
            selected = json.loads(sel_path.read_text(encoding="utf-8")).get(
                "selected_profile_id"
            )
            if selected:
                profiles_to_check = [selected]
    for seed in VALIDATION_SEEDS:
        for profile in profiles_to_check:
            for scenario in SCENARIOS:
                trace_dir = base / str(seed) / profile / scenario
                if not trace_dir.is_dir():
                    pytest.fail(f"missing trace dir {trace_dir}")
                # Compact evidence packages omit heavy mass parquet files.
                required = REQUIRED_TRACE_FILES
                if not (trace_dir / "empirical_atomic_mass_300.parquet").is_file():
                    required = [
                        f for f in REQUIRED_TRACE_FILES
                        if not f.startswith("empirical_atomic_mass_")
                        and not f.startswith("expected_atomic_mass_")
                    ]
                missing = [f for f in required if not (trace_dir / f).is_file()]
                assert not missing, f"{trace_dir}: missing {missing}"


def test_gates_json_if_present() -> None:
    path = ROOT / "outputs/gates/E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1_GATES.json"
    if not path.is_file():
        pytest.skip("gates not generated yet")
    gates = json.loads(path.read_text(encoding="utf-8"))
    assert "gates" in gates
    assert all(k.startswith("E2EE-G") for k in gates["gates"])


def test_window_stability_selection_if_present() -> None:
    path = ROOT / "outputs/e2_empirical/E2_EMPIRICAL_WINDOW_LENGTH_SELECTION.json"
    if not path.is_file():
        pytest.skip("window selection not generated yet")
    win = json.loads(path.read_text(encoding="utf-8"))
    assert win["selected_windows"] in (100, 200, 300)
    assert win.get("prior_200_not_preferred") is True
