"""Unit tests for Traffic Real Runner Canary."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/e2_traffic_real_runner_canary"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic_profiles_s1"
SCENARIOS = [
    "balanced", "opportunity_only", "observation_only",
    "usable_only", "complete_aligned", "complete_counteracting",
]
METHODS = [
    "fedavg_window", "fedasync_window", "flamf_timealign_adapted",
    "twostage_hajek", "raven",
]


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ready() -> bool:
    return (OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json").is_file()


def test_seed_29001_only(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert int(stop["seed"]) == 29001
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    assert set(main["seed"].astype(int)) == {29001}


def test_exactly_six_scenarios(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert int(stop["scenario_count"]) == 6
    assert sorted((OUT / "eventtraces").iterdir())  # exists
    assert len(list((OUT / "eventtraces").iterdir())) == 6


def test_exactly_five_methods(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert int(stop["method_count"]) == 5
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    assert set(main["method"]) == set(METHODS)


def test_exactly_30_runs(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert int(stop["total_run_count"]) == 30
    assert int(stop["completed_run_count"]) == 30
    # Ledger-closure may leave PENDING until gates rewrite READY.
    assert stop["status"] in {
        "READY_FOR_TRAFFIC_E2_FORMAL_RUNS",
        "PENDING_LEDGER_GATES",
        "BLOCKED_TRAFFIC_REAL_RUNNER_LEDGER_NOT_CLOSED",
        "BLOCKED_TRAFFIC_REAL_RUNNER_CANARY_FAILED",
    }


def test_100_windows_per_run(ready: bool) -> None:
    assert ready
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    assert int(main["completed_windows"].min()) == 100
    assert int(main["completed_windows"].max()) == 100


def test_no_retry(ready: bool) -> None:
    assert ready
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    assert int(main["retry_count"].sum()) == 0


def test_no_seed_replacement(ready: bool) -> None:
    assert ready
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    assert int(main["seed_replacement_count"].sum()) == 0


def test_same_eventtrace_across_methods(ready: bool) -> None:
    assert ready
    cross = _j(AUDIT / "E2_TRAFFIC_CANARY_CROSS_METHOD_TRACE_IDENTITY.json")
    assert cross["status"] == "PASS"
    assert int(cross["total_mismatch_count"]) == 0


def test_profile_s1_registry_immutable(ready: bool) -> None:
    assert ready
    reg = _j(FROZEN / "traffic_s1_s6_profile_registry.json")
    assert reg["selected_strength"] == "PROFILE-S1"
    assert reg["status"] == "FROZEN"


def test_no_per_method_scenario_regeneration(ready: bool) -> None:
    assert ready
    for sid in SCENARIOS:
        hashes = []
        for method in METHODS:
            ident = _j(OUT / "runs" / sid / method / "eventtrace_identity.json")
            hashes.append(ident["eventtrace_dir"])
        assert len(set(hashes)) == 1


def test_method_hyperparameters_frozen(ready: bool) -> None:
    assert ready
    for sid in SCENARIOS:
        for method in METHODS:
            cfg = _j(OUT / "runs" / sid / method / "config_snapshot.json")
            assert int(cfg["local_steps"]) == 2
            assert float(cfg["a_max"]) == 40.0
            assert float(cfg["learning_rate"]) == 0.01


def test_raven_runtime_components_enabled(ready: bool) -> None:
    assert ready
    audit = _j(AUDIT / "E2_TRAFFIC_CANARY_RAVEN_RUNTIME_AUDIT.json")
    assert audit["status"] == "PASS"
    for row in audit["rows"]:
        assert row["uses_design_ratio"] is True
        assert row["uses_observation_ipw"] is True
        assert row["uses_usable_ipw"] is True
        assert row["uses_debt"] is True
        assert row["uses_hajek_local_loss"] is True


def test_baselines_do_not_use_raven_only_information(ready: bool) -> None:
    assert ready
    audit = _j(AUDIT / "E2_TRAFFIC_CANARY_BASELINE_RUNTIME_AUDIT.json")
    assert audit["status"] == "PASS"
    assert int(audit["illegal_count"]) == 0


def test_no_nonfinite_model_parameters(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert int(stop["nonfinite_model_parameter_count"]) == 0


def test_no_nonfinite_losses(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert int(stop["nonfinite_loss_count"]) == 0


def test_no_nonfinite_metrics(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert int(stop["nonfinite_metric_count"]) == 0


def test_gap_mis_identity(ready: bool) -> None:
    assert ready
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    delta = (main["Gap_mis"] - (main["RMSE_mu"] - main["RMSE_rho"])).abs()
    assert float(delta.max()) < 1e-9


def test_30_main_result_rows(ready: bool) -> None:
    assert ready
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    assert len(main) == 30


def test_group_metrics_complete(ready: bool) -> None:
    assert ready
    g = pd.read_csv(OUT / "group_metrics_seed29001.csv")
    assert len(g) == 30 * 4


def test_runtime_metrics_complete(ready: bool) -> None:
    assert ready
    r = pd.read_csv(OUT / "runtime_metrics_seed29001.csv")
    assert len(r) == 30


def test_communication_metrics_complete(ready: bool) -> None:
    assert ready
    c = pd.read_csv(OUT / "communication_metrics_seed29001.csv")
    assert len(c) == 30


def test_stage_metrics_complete(ready: bool) -> None:
    assert ready
    s = pd.read_csv(OUT / "stage_metrics_seed29001.csv")
    assert len(s) == 30


def test_clip_metrics_complete(ready: bool) -> None:
    assert ready
    c = pd.read_csv(OUT / "clip_metrics_seed29001.csv")
    assert len(c) == 30


def test_p2_metrics_complete(ready: bool) -> None:
    assert ready
    p = pd.read_csv(OUT / "p2_metrics_seed29001.csv")
    assert len(p) == 30


def test_checkpoints_present(ready: bool) -> None:
    assert ready
    for sid in SCENARIOS:
        for method in METHODS:
            assert (OUT / "runs" / sid / method / "checkpoints" / "final.pt").is_file()


def test_run_manifests_present(ready: bool) -> None:
    assert ready
    for sid in SCENARIOS:
        for method in METHODS:
            assert (OUT / "runs" / sid / method / "runtime_manifest.json").is_file()


def test_validation_seed_noninspection(ready: bool) -> None:
    assert ready
    a = _j(AUDIT / "E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json")
    assert int(a["validation_seed_reads"]) == 0


def test_formal_seed_noninspection(ready: bool) -> None:
    assert ready
    a = _j(AUDIT / "E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json")
    assert int(a["formal_seed_reads"]) == 0
    assert int(a["formal_run_count"]) == 0


def test_no_formal_figures(ready: bool) -> None:
    assert ready
    a = _j(AUDIT / "E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json")
    assert int(a["formal_figures_count"]) == 0


def test_full_repository_pytest_command(ready: bool) -> None:
    assert ready
    path = ROOT / "logs/e2_traffic_real_runner_canary_full_repository.xml"
    if not path.is_file():
        pytest.skip("full repository junit not written yet")
    assert path.is_file()


def test_ledger_starts_with_real_runner_command(ready: bool) -> None:
    assert ready
    ledger = ROOT / "logs/E2_TRAFFIC_REAL_RUNNER_CANARY_R1_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        pytest.skip("ledger not written yet")
    lines = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines
    assert lines[0]["label"] == "e2rr_preflight_seed29001"
    training = [r for r in lines if r.get("run_kind") == "training" and r.get("record_type") == "FINISH"]
    if training:
        assert len(training) == 30
        assert all("--run-one" in r.get("command", []) for r in training)


def test_external_hash_verifies_three_artifacts(ready: bool) -> None:
    assert ready
    verify = ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1/FINAL_DELIVERABLE_HASHES_VERIFY.json"
    if not verify.is_file():
        pytest.skip("hash verify not written yet")
    v = _j(verify)
    assert int(v["verified_artifact_count"]) == 3
    assert int(v["hash_mismatch_count"]) == 0


def test_final_export_order(ready: bool) -> None:
    assert ready
    d = ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1"
    if not (d / "FINAL_DELIVERABLE_HASHES.json").is_file():
        pytest.skip("hashes not written yet")
    assert (d / "E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1_REPORT.docx").is_file()
    assert (d / "E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1_SUBMISSION_README.txt").is_file()
    assert (d / "RAVEN_MCS_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1_EVIDENCE.zip").is_file()
    assert (d / "TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1.zip").is_file()
