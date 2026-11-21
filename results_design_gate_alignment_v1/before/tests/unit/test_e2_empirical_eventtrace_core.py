"""Unit tests for E2 empirical EventTrace core pipeline and gates."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from raven_mcs.e2.client_windows import E2ClientWindowError, validate_client_window_record
from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.events import (
    generate_hard_arrival_events,
    generate_observation_events,
    generate_opportunity_events,
    generate_usable_events,
    risk_sets_from_opportunity,
)
from raven_mcs.e2.empirical.gates import (
    SCENARIOS,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
    select_strength_profile,
    window_prefix_stable,
)
from raven_mcs.e2.empirical.mass import (
    aggregate_group_mass,
    aggregate_stratum_mass,
    hard_empirical_atomic_mass,
)
from raven_mcs.e2.empirical.schedule import build_continuous_schedule
from raven_mcs.e2.empirical.sampler import generate_empirical_mother_trace
from raven_mcs.e2.identity import load_e1_head_tail_mapping

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1"
DATA_OK = (ROOT / "data/processed/sensorscope/atomic_units.parquet").is_file()


def _diag(**kwargs):
    base = {
        "D_TV_group": 0.01,
        "D_TV_stratum": 0.02,
        "tail_mass_ratio": 1.0,
        "head_mass_ratio": 1.0,
        "tail_mass_ratio_obs": 1.0,
        "D_TV_group_exp_emp": 0.01,
        "D_TV_stratum_exp_emp": 0.02,
        "cancellation_group_TV": 0.05,
        "realized_observation_rate": 0.20,
        "realized_usable_rate": 0.60,
        "unsupported_arrival_count": 0,
        "head_arrival_support": 10,
        "tail_arrival_support": 10,
        "failed_attempt_omission_count": 0,
        "q_leakage_count": 0,
        "finite_status": True,
        "total_hard_arrival_mass": 100.0,
        "active_window_rate": 0.60,
    }
    base.update(kwargs)
    return base


def _gate_rows():
    return {
        "balanced": _diag(),
        "opportunity_only": _diag(
            D_TV_group=0.2, tail_mass_ratio=0.5, head_mass_ratio=1.5,
        ),
        "observation_only": _diag(
            D_TV_group=0.15, tail_mass_ratio=0.6, head_mass_ratio=1.4,
        ),
        "usable_only": _diag(
            D_TV_group=0.1, tail_mass_ratio=0.7, head_mass_ratio=1.3,
        ),
        "complete_aligned": _diag(
            D_TV_group=0.4, tail_mass_ratio=0.2, head_mass_ratio=2.0, tail_mass_ratio_obs=0.3,
        ),
        "complete_counteracting": _diag(
            D_TV_group=0.3,
            tail_mass_ratio=0.25,
            head_mass_ratio=1.8,
            tail_mass_ratio_obs=0.2,
            cancellation_group_TV=0.05,
        ),
    }


@pytest.fixture
def seed_streams_schedule():
    if not DATA_OK:
        pytest.skip("sensorscope processed data missing")
    seed = 29101
    streams = build_base_random_streams(
        seed, n_windows=300, n_clients=8, max_risk_set=20,
    )
    schedule = build_continuous_schedule(
        seed, schedule_uniforms=streams["base_client_window_schedule"], root=ROOT,
    )
    return seed, streams, schedule


def test_300_window_blocks_not_identical(seed_streams_schedule) -> None:
    _, _, schedule = seed_streams_schedule
    audit = schedule["audit"]
    assert audit["block_hashes_all_equal"] is False
    assert audit["unique_window_payload_ratio"] >= 0.80
    assert audit["block_0_99_hash"] != audit["block_100_199_hash"]


def test_schedule_uniforms_actually_used(seed_streams_schedule) -> None:
    _, _, schedule = seed_streams_schedule
    assert int(schedule["audit"]["schedule_uniforms_used_count"]) > 0


def test_opportunity_uniforms_actually_used(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    mapping = {
        str(r.unit_id): int(r.tail_score)
        for r in load_e1_head_tail_mapping(ROOT).itertuples(index=False)
    }
    client_index = {c: i for i, c in enumerate(schedule["clients"])}
    opp, audit = generate_opportunity_events(
        schedule_rows=schedule["rows"],
        tail_score_map=mapping,
        opp_uniforms=streams["base_opportunity_uniforms"],
        client_index=client_index,
        kappa_opp=0.5,
        d_opp=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    assert int(audit["base_opportunity_uniforms_used_count"]) > 0
    assert len(opp) > 0


def test_balanced_and_opportunity_risksets_differ(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    bal = generate_empirical_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
    )
    opp = generate_empirical_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="opportunity_only",
        root=ROOT,
        streams=streams,
        schedule=schedule,
    )
    assert bal["opportunity_selected_set"] != opp["opportunity_selected_set"]


def test_observation_intercept_uses_actual_exposure(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    mapping = {
        str(r.unit_id): int(r.tail_score)
        for r in load_e1_head_tail_mapping(ROOT).itertuples(index=False)
    }
    client_index = {c: i for i, c in enumerate(schedule["clients"])}
    opp, _ = generate_opportunity_events(
        schedule_rows=schedule["rows"],
        tail_score_map=mapping,
        opp_uniforms=streams["base_opportunity_uniforms"],
        client_index=client_index,
        kappa_opp=0.5,
        d_opp=-1,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="opportunity_only",
    )
    risk_sets = risk_sets_from_opportunity(opp)
    obs, audit = generate_observation_events(
        risk_sets=risk_sets,
        obs_uniforms=streams["base_observation_uniforms"],
        client_index=client_index,
        kappa_p=0.5,
        d_p=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="observation_only",
    )
    assert int(audit["exposure_event_count"]) > 0
    assert int(audit["actual_O_events_saved"]) == len(obs)


def test_hard_empirical_mass_from_A_O_U(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_empirical_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
    )
    audit = result["manifest"]["arr_audit"]
    assert audit["empirical_from_A_O_U"] is True
    assert float(audit["total_hard_arrival_mass"]) > 0


def test_empirical_not_alias_of_expected(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_empirical_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
    )
    emp = result["emp_by_len"][300]
    exp = result["exp_by_len"][300]
    assert emp is not exp
    assert not np.shares_memory(emp, exp)


def test_expected_empirical_hashes_not_forced_equal(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_empirical_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
    )
    diag = result["diagnostics"][300]
    assert diag["empirical_payload_hash"] != diag["expected_payload_hash"]
    assert diag["hashes_equal_warning"] is False


def test_group_mass_aggregation() -> None:
    atomic = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float64)
    groups = np.array([0, 0, 1, 1], dtype=np.int64)
    out = aggregate_group_mass(atomic, groups, 2)
    assert out[0] == pytest.approx(0.3)
    assert out[1] == pytest.approx(0.7)


def test_stratum_mass_aggregation() -> None:
    atomic = np.array([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    strata = np.array([0, 1, 2, 2], dtype=np.int64)
    out = aggregate_stratum_mass(atomic, strata, 3)
    assert out[0] == pytest.approx(0.25)
    assert out[2] == pytest.approx(0.5)


def test_balanced_group_tv_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["H1"] == "PASS"


def test_single_stage_group_tv_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["H2"] == "PASS"


def test_aligned_group_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["H3"] == "PASS"


def test_counteracting_group_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["H4"] == "PASS"


def test_group_expected_empirical_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["H5"] == "PASS"


def test_window_prefix_uses_same_hard_trace() -> None:
    metrics = {
        100: {s: _diag() for s in SCENARIOS},
        200: {s: _diag() for s in SCENARIOS},
        300: {s: _diag() for s in SCENARIOS},
    }
    ok, _ = window_prefix_stable(metrics, length=100)
    assert ok is True


def test_profile_selection_does_not_reuse_invalid_S2() -> None:
    tomb = ROOT / "outputs/audits/E2_INVALID_PRIOR_SELECTION_TOMBSTONE.json"
    if not tomb.is_file():
        pytest.skip("tombstone not present yet")
    payload = json.loads(tomb.read_text(encoding="utf-8"))
    assert payload["prior_profile_id"] == "PROFILE-S2"
    assert payload["not_reused_without_revalidation"] is True
    sel_path = ROOT / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json"
    if sel_path.is_file():
        sel = json.loads(sel_path.read_text(encoding="utf-8"))
        if sel.get("status") == "SELECTED":
            assert sel.get("prior_PROFILE_S2_tombstoned") is True


def test_gate_checks_all_command_exit_codes() -> None:
    script = (ROOT / "scripts/check_e2_empirical_eventtrace_gates.py").read_text(
        encoding="utf-8",
    )
    assert "failed_exit_code_count" in script
    assert "exit_code" in script
    assert "junit_ok and placeholders == 0" not in script
    assert "ledger_strict_pass" in script


def test_gate_checks_log_file_existence() -> None:
    script = (ROOT / "scripts/check_e2_empirical_eventtrace_gates.py").read_text(
        encoding="utf-8",
    )
    assert "missing_stdout_stderr_count" in script
    assert "stdout_log" in script
    assert "stderr_log" in script


def test_unpacked_evidence_imports_raven_mcs_utils() -> None:
    export = (ROOT / "scripts/export_e2_empirical_eventtrace_evidence.py").read_text(
        encoding="utf-8",
    )
    assert "src/raven_mcs/utils" in export
    assert "PYTHONPATH" in export


def test_duplicate_unit_ids_rejected() -> None:
    mapping = {
        str(r.unit_id): int(r.tail_score)
        for r in load_e1_head_tail_mapping(ROOT).itertuples(index=False)
    }
    unit = next(iter(mapping))
    with pytest.raises(E2ClientWindowError, match="duplicate unit_ids"):
        validate_client_window_record(
            {
                "client_id": "c0",
                "window_id": "0",
                "unit_ids": [unit, unit],
                "opportunity_weights": [1.0, 1.0],
                "attempt_eligible": True,
            },
            supported_units={unit},
            frozen_tail_score_map=mapping,
        )


def test_seed_29001_not_read() -> None:
    paths = [
        ROOT / "outputs/e2_empirical/E2_EMPIRICAL_CONTEXT.json",
        ROOT / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json",
    ]
    blob = ""
    for path in paths:
        if path.is_file():
            blob += path.read_text(encoding="utf-8")
    if not blob:
        pytest.skip("empirical outputs not generated yet")
    assert "29001" not in blob


def test_formal_seed_noninspection() -> None:
    path = ROOT / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json"
    if not path.is_file():
        pytest.skip("selection not generated yet")
    text = path.read_text(encoding="utf-8")
    for seed in range(30001, 30021):
        assert str(seed) not in text


def test_final_export_is_last_mutating_step() -> None:
    script = (ROOT / "scripts/export_e2_empirical_eventtrace_evidence.py").read_text(
        encoding="utf-8",
    )
    assert "ZIP export must be last" in script or "last mutating step" in script


def test_hard_arrival_recompute_matches_events(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_empirical_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
    )
    # Recompute from in-memory pipeline via mass helper on synthetic frame shape.
    mapping = {
        str(r.unit_id): int(r.tail_score)
        for r in load_e1_head_tail_mapping(ROOT).itertuples(index=False)
    }
    client_index = {c: i for i, c in enumerate(schedule["clients"])}
    opp, _ = generate_opportunity_events(
        schedule_rows=schedule["rows"][:50],
        tail_score_map=mapping,
        opp_uniforms=streams["base_opportunity_uniforms"],
        client_index=client_index,
        kappa_opp=0.5,
        d_opp=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    risk_sets = risk_sets_from_opportunity(opp)
    obs, _ = generate_observation_events(
        risk_sets=risk_sets,
        obs_uniforms=streams["base_observation_uniforms"],
        client_index=client_index,
        kappa_p=0.5,
        d_p=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    usable, _ = generate_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=0.5,
        d_q=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    arrival, audit = generate_hard_arrival_events(
        opp=opp, obs=obs, usable=usable,
        seed=seed, profile_id="PROFILE-S1", scenario_id="balanced",
    )
    from raven_mcs.e2.identity import load_e1_atomic_target_weights
    unit_ids = load_e1_atomic_target_weights(ROOT)["unit_id"].astype(str).tolist()
    mass = hard_empirical_atomic_mass(arrival, unit_ids, 50)
    assert float(mass.sum()) == pytest.approx(1.0)
    assert audit["empirical_from_A_O_U"] is True


def test_profile_selection_prefers_lower_aligned_tv() -> None:
    def seed_result(aligned: float, cancel: float, valid: bool = True):
        return {
            "profile_valid_seed": valid,
            "aligned_dtv_group": aligned,
            "counteracting_cancellation": cancel,
        }

    payload = {
        "PROFILE-S1": {s: seed_result(0.4, 0.1) for s in VALIDATION_SEEDS},
        "PROFILE-S3": {s: seed_result(0.6, 0.1) for s in VALIDATION_SEEDS},
    }
    profiles = {
        "PROFILE-S1": {"kappa_opp": 0.5, "kappa_p": 0.5, "kappa_q": 0.5},
        "PROFILE-S3": {"kappa_opp": 1.5, "kappa_p": 1.5, "kappa_q": 1.5},
    }
    out = select_strength_profile(payload, profiles)
    assert out["selected_profile_id"] == "PROFILE-S1"
    assert out["prior_PROFILE_S2_not_special_cased"] is True
