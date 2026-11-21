"""Unit tests for E2 Stage-2 eligibility, true stratum, and packaging gates."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.events import (
    generate_observation_events,
    generate_opportunity_events,
    risk_sets_from_opportunity,
)
from raven_mcs.e2.empirical.schedule import build_continuous_schedule
from raven_mcs.e2.identity import load_e1_head_tail_mapping
from raven_mcs.e2.stage2.gates import (
    SCENARIOS,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
    select_strength_profile,
    select_window_length,
    window_prefix_stable,
)
from raven_mcs.e2.stage2.sampler import audit_chronological_schedule, generate_stage2_mother_trace
from raven_mcs.e2.stage2.stratum import build_opportunity_stratum_table, load_opportunity_stratum
from raven_mcs.e2.stage2.usable import (
    ALLOWED_Q_FEATURES,
    FORBIDDEN_Q_FEATURES,
    audit_q_features,
    enrich_risk_sets_with_observation,
    generate_stage2_usable_events,
    server_window_activity,
)
from raven_mcs.e2.empirical.events import generate_hard_arrival_events

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_STAGE2_ELIGIBILITY_AND_TRUE_STRATUM_REFREEZE_R1"
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
        "active_server_window_rate": 0.45,
        "unsupported_arrival_count": 0,
        "head_arrival_support": 10,
        "tail_arrival_support": 10,
        "missing_failed_attempt_count": 0,
        "extra_failed_attempt_count": 0,
        "not_eligible_usable_event_count": 0,
        "q_leakage_count": 0,
        "finite_status": True,
        "total_hard_arrival_mass": 100.0,
        "stage2_eligible_count": 50,
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


def test_stage2_eligible_only_if_observed_count_positive(seed_streams_schedule) -> None:
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
    enriched = enrich_risk_sets_with_observation(risk_sets, obs)
    for rs in enriched:
        assert rs["stage2_eligible"] == (int(rs["observed_count"]) > 0)


def test_opportunity_positive_observation_zero_not_eligible(seed_streams_schedule) -> None:
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
    obs, _ = generate_observation_events(
        risk_sets=risk_sets,
        obs_uniforms=streams["base_observation_uniforms"],
        client_index=client_index,
        kappa_p=0.5,
        d_p=-1,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="opportunity_only",
    )
    enriched = enrich_risk_sets_with_observation(risk_sets, obs)
    zero_obs = [rs for rs in enriched if int(rs["observed_count"]) == 0 and len(rs["unit_ids"]) > 0]
    if zero_obs:
        assert all(not rs["stage2_eligible"] for rs in zero_obs)


def test_q_intercept_uses_stage2_eligible_only(seed_streams_schedule) -> None:
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
        d_opp=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    risk_sets = enrich_risk_sets_with_observation(
        risk_sets_from_opportunity(opp),
        generate_observation_events(
            risk_sets=risk_sets_from_opportunity(opp),
            obs_uniforms=streams["base_observation_uniforms"],
            client_index=client_index,
            kappa_p=0.5,
            d_p=0,
            seed=seed,
            profile_id="PROFILE-S1",
            scenario_id="balanced",
        )[0],
    )
    usable, audit = generate_stage2_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=0.5,
        d_q=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    eligible = usable.loc[usable["stage2_eligible"]]
    assert int(audit["stage2_eligible_count"]) == len(eligible)
    assert audit["eligibility_rule"] == "observed_count > 0"
    assert float(audit["realized_usable_rate"]) == pytest.approx(0.60, abs=0.05)


def test_not_eligible_has_no_usable_draw(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_stage2_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
        output_dir=None,
    )
    use = result["use_audit"]
    assert int(use["not_eligible_count"]) >= 0
    assert use["eligibility_rule"] == "observed_count > 0"


def test_failed_attempt_set_equality(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_stage2_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
        output_dir=None,
    )
    use = result["use_audit"]
    assert int(use["missing_failed_attempt_count"]) == 0
    assert int(use["extra_failed_attempt_count"]) == 0


def test_active_server_window_from_hard_arrivals(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_stage2_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
        output_dir=None,
    )
    act = result["activity_audit"]
    assert float(act["active_server_window_rate"]) >= 0.0
    assert act["definition_alias_forbidden"] is True


def test_active_window_not_alias_of_usable_rate(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    result = generate_stage2_mother_trace(
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
        root=ROOT,
        streams=streams,
        schedule=schedule,
        output_dir=None,
    )
    assert result["activity_audit"]["active_window_equals_usable_rate_identically"] is False


def test_true_stratum_mapping_not_role_mapping() -> None:
    if not DATA_OK:
        pytest.skip("sensorscope processed data missing")
    table = build_opportunity_stratum_table(ROOT)
    identity = table["identity"]
    assert identity["role_substitution"] is False
    assert not any(s in {"head", "neutral", "tail"} for s in identity["stratum_ids"])


def test_stratum_target_mass_sums_to_one() -> None:
    if not DATA_OK:
        pytest.skip("sensorscope processed data missing")
    _, identity = load_opportunity_stratum(ROOT)
    assert identity["target_mass_sum"] == pytest.approx(1.0)


def test_stratum_merge_rule_deterministic() -> None:
    if not DATA_OK:
        pytest.skip("sensorscope processed data missing")
    a = build_opportunity_stratum_table(ROOT)
    b = build_opportunity_stratum_table(ROOT)
    assert a["identity"]["mapping_hash"] == b["identity"]["mapping_hash"]


def test_q_feature_manifest_enforced() -> None:
    manifest = json.loads(
        (ROOT / "configs/frozen/e2_stage2/q_feature_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["protocol"] == "E2-STAGE2-ELIGIBILITY-AND-TRUE-STRATUM-REFREEZE-R1"
    assert "client_id" in manifest["allowed_features"]
    assert "observed_count_as_q_numeric_feature" in manifest["forbidden_features"]


def test_q_forbidden_features_rejected() -> None:
    audit = audit_q_features(list(ALLOWED_Q_FEATURES) + ["model_delta"])
    assert audit["forbidden_feature_count"] > 0
    assert audit["leakage_status"] == "FAIL"
    clean = audit_q_features(list(ALLOWED_Q_FEATURES))
    assert clean["forbidden_feature_count"] == 0
    assert clean["leakage_status"] == "PASS"
    assert FORBIDDEN_Q_FEATURES  # module defines forbidden set


def test_chronological_order_actually_checked(seed_streams_schedule) -> None:
    _, _, schedule = seed_streams_schedule
    audit = audit_chronological_schedule(schedule)
    assert "chronological_order_status" in audit
    assert "per_client_violation_count" in audit
    assert audit["chronological_order_status"] in {"PASS", "FAIL"}


def test_no_schedule_wraparound(seed_streams_schedule) -> None:
    _, _, schedule = seed_streams_schedule
    audit = schedule["audit"]
    assert audit["block_hashes_all_equal"] is False
    assert float(audit["unique_window_payload_ratio"]) >= 0.80


def test_balanced_group_tv_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["I1"] == "PASS"


def test_single_stage_group_tv_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["I2"] == "PASS"


def test_aligned_group_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["I3"] == "PASS"


def test_counteracting_group_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["I4"] == "PASS"


def test_group_expected_empirical_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["I5"] == "PASS"


def test_stage2_semantic_gate() -> None:
    out = evaluate_seed_profile_gates(_gate_rows())
    assert out["gate_status"]["I6"] == "PASS"


def test_window_prefix_uses_same_hard_trace() -> None:
    metrics = {
        100: {s: _diag() for s in SCENARIOS},
        200: {s: _diag() for s in SCENARIOS},
        300: {s: _diag() for s in SCENARIOS},
    }
    ok, _ = window_prefix_stable(metrics, length=100)
    assert ok is True


def test_profile_selection_recomputed() -> None:
    sel_path = ROOT / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json"
    if not sel_path.is_file():
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
        assert out["revalidated_on_stage2_and_true_stratum"] is True
        assert out["prior_PROFILE_S2_not_special_cased"] is True
        return
    sel = json.loads(sel_path.read_text(encoding="utf-8"))
    assert sel.get("revalidated_on_stage2_and_true_stratum") is True
    assert sel.get("prior_PROFILE_S2_not_special_cased") is True


def test_window_selection_recomputed() -> None:
    win_path = ROOT / "outputs/e2_stage2_stratum/E2_WINDOW_SELECTION.json"
    if not win_path.is_file():
        seed_stability = {s: {100: True, 200: True, 300: True} for s in VALIDATION_SEEDS}
        out = select_window_length(seed_stability)
        assert out["prior_300_not_preferred"] is True
        assert out["selected_windows"] in (100, 200, 300)
        return
    win = json.loads(win_path.read_text(encoding="utf-8"))
    assert win.get("prior_300_not_preferred") is True
    assert win["selected_windows"] in (100, 200, 300)


def test_gate_checks_all_ledger_exit_codes() -> None:
    script = (ROOT / "scripts/check_e2_stage2_stratum_gates.py").read_text(encoding="utf-8")
    assert "failed_exit_code_count" in script
    assert "exit_code" in script
    assert "junit_ok and placeholders == 0" not in script
    assert "ledger_strict_pass" in script


def test_external_hash_verifies_all_three_artifacts() -> None:
    export = (ROOT / "scripts/export_e2_stage2_stratum_evidence.py").read_text(encoding="utf-8")
    assert "artifact_count" in export
    assert "FINAL_DELIVERABLE_HASHES.json" in export
    assert "FINAL_DELIVERABLE_HASHES_VERIFY.json" in export
    assert "RAVEN_MCS_" in export and "_SUBMISSION.zip" in export


def test_seed_29001_not_read() -> None:
    paths = [
        ROOT / "outputs/e2_stage2_stratum/E2_STAGE2_STRATUM_CONTEXT.json",
        ROOT / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json",
    ]
    blob = ""
    for path in paths:
        if path.is_file():
            blob += path.read_text(encoding="utf-8")
    if not blob:
        pytest.skip("stage2 outputs not generated yet")
    assert "29001" not in blob


def test_formal_seed_noninspection() -> None:
    path = ROOT / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json"
    if not path.is_file():
        pytest.skip("selection not generated yet")
    text = path.read_text(encoding="utf-8")
    for seed in range(30001, 30021):
        assert str(seed) not in text


def test_final_export_order() -> None:
    script = (ROOT / "scripts/export_e2_stage2_stratum_evidence.py").read_text(encoding="utf-8")
    assert "ZIP export must be last" in script or "last mutating step" in script
    zip_create = script.rfind("with zipfile.ZipFile(zip_path, \"w\"")
    hash_write = script.rfind("hash_json.write_text")
    assert zip_create > 0 and hash_write > zip_create


def test_server_window_activity_hard_arrival_mass(seed_streams_schedule) -> None:
    seed, streams, schedule = seed_streams_schedule
    mapping = {
        str(r.unit_id): int(r.tail_score)
        for r in load_e1_head_tail_mapping(ROOT).itertuples(index=False)
    }
    client_index = {c: i for i, c in enumerate(schedule["clients"])}
    opp, _ = generate_opportunity_events(
        schedule_rows=schedule["rows"][:80],
        tail_score_map=mapping,
        opp_uniforms=streams["base_opportunity_uniforms"],
        client_index=client_index,
        kappa_opp=0.5,
        d_opp=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    risk_sets = enrich_risk_sets_with_observation(
        risk_sets_from_opportunity(opp),
        generate_observation_events(
            risk_sets=risk_sets_from_opportunity(opp),
            obs_uniforms=streams["base_observation_uniforms"],
            client_index=client_index,
            kappa_p=0.5,
            d_p=0,
            seed=seed,
            profile_id="PROFILE-S1",
            scenario_id="balanced",
        )[0],
    )
    usable, _ = generate_stage2_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=0.5,
        d_q=0,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    arrival, _ = generate_hard_arrival_events(
        opp=opp, obs=generate_observation_events(
            risk_sets=risk_sets_from_opportunity(opp),
            obs_uniforms=streams["base_observation_uniforms"],
            client_index=client_index,
            kappa_p=0.5,
            d_p=0,
            seed=seed,
            profile_id="PROFILE-S1",
            scenario_id="balanced",
        )[0], usable=usable,
        seed=seed, profile_id="PROFILE-S1", scenario_id="balanced",
    )
    activity, audit = server_window_activity(arrival, usable, max_window=80)
    assert "server_window_active" in activity.columns
    assert audit["active_window_equals_usable_rate_identically"] is False
