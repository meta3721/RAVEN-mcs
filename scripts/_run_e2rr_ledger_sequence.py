#!/usr/bin/env python3
"""Ledger sequence for E2 Traffic Real Runner Ledger Closure."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_TRAFFIC_REAL_RUNNER_CANARY_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
SCENARIOS = [
    "balanced", "opportunity_only", "observation_only",
    "usable_only", "complete_aligned", "complete_counteracting",
]
METHODS = [
    "fedavg_window", "fedasync_window", "flamf_timealign_adapted",
    "twostage_hajek", "raven",
]
FROZEN_INPUTS = [
    "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json",
    "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_runner_identity.json",
    "src/raven_mcs/aggregation/method_policy.py",
]


def run(
    label: str,
    command: list[str],
    *,
    outputs: list[str] | None = None,
    inputs: list[str] | None = None,
    seed: int | None = None,
    scenario: str | None = None,
    method: str | None = None,
    profile_id: str | None = None,
    run_kind: str | None = None,
    expected_windows: int | None = None,
) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py",
        "--ledger", LEDGER,
        "--label", label,
        "--stdout-log", f"logs/e2rr_{label}.stdout.log",
        "--stderr-log", f"logs/e2rr_{label}.stderr.log",
    ]
    if run_kind:
        wrapped.extend(("--run-kind", run_kind))
    if seed is not None:
        wrapped.extend(("--seed", str(seed)))
    if scenario is not None:
        wrapped.extend(("--scenario", scenario))
    if method is not None:
        wrapped.extend(("--method", method))
    if profile_id is not None:
        wrapped.extend(("--profile-id", profile_id))
    if expected_windows is not None:
        wrapped.extend(("--expected-windows", str(expected_windows)))
    for path in inputs or []:
        wrapped.extend(("--input", path))
    for path in outputs or []:
        wrapped.extend(("--output", path))
    wrapped.extend(("--", *command))
    print(f">> {label}", flush=True)
    return subprocess.call(wrapped, cwd=ROOT)


def clean_regenerable() -> None:
    canary = ROOT / "outputs/e2_traffic_real_runner_canary"
    for rel in ("eventtraces", "runs"):
        path = canary / rel
        if path.exists():
            shutil.rmtree(path)
    if canary.is_dir():
        for path in canary.glob("*.csv"):
            path.unlink()
        for path in canary.glob("*.parquet"):
            path.unlink()
        for path in canary.glob("*.json"):
            path.unlink()
    for path in [
        ROOT / "outputs/audits/E2_TRAFFIC_REAL_RUNNER_CANARY_INPUT_IDENTITY.json",
        ROOT / "outputs/audits/E2_TRAFFIC_CANARY_CROSS_METHOD_TRACE_IDENTITY.json",
        ROOT / "outputs/audits/E2_TRAFFIC_CANARY_RAVEN_RUNTIME_AUDIT.json",
        ROOT / "outputs/audits/E2_TRAFFIC_CANARY_BASELINE_RUNTIME_AUDIT.json",
        ROOT / "outputs/audits/E2_TRAFFIC_CANARY_METRIC_CONSISTENCY_AUDIT.json",
        ROOT / "outputs/audits/E2_TRAFFIC_CANARY_NUMERICAL_STABILITY_AUDIT.json",
        ROOT / "outputs/audits/E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json",
        ROOT / f"outputs/gates/{PACKAGE}_GATES.json",
        ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        ROOT / "logs/e2_traffic_real_runner_canary_unit.xml",
        ROOT / "logs/e2_traffic_real_runner_canary_integration.xml",
        ROOT / "logs/e2_traffic_real_runner_canary_full_repository.xml",
        ROOT / "logs/e2rr_pip_check.txt",
    ]:
        if path.is_file():
            path.unlink()
    for path in (ROOT / "logs").glob("e2rr_*.stdout.log"):
        path.unlink()
    for path in (ROOT / "logs").glob("e2rr_*.stderr.log"):
        path.unlink()
    deliv = ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1"
    if deliv.exists():
        shutil.rmtree(deliv)
    # Keep archived canary deliverables; only clear active canary deliverable hashes if present.
    old = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
    if old.exists():
        # Do not delete archived copy; active canary package may be regenerated later.
        pass


def main() -> int:
    if not Path(PYTHON).is_file():
        raise SystemExit(f"missing interpreter: {PYTHON}")

    ledger = ROOT / LEDGER
    if ledger.is_file():
        ledger.unlink()

    print("Cleaning regenerable canary outputs...", flush=True)
    clean_regenerable()
    # Confirm no leftover manifests
    leftover = list((ROOT / "outputs/e2_traffic_real_runner_canary/runs").glob("*/**/runtime_manifest.json")) if (
        ROOT / "outputs/e2_traffic_real_runner_canary/runs"
    ).exists() else []
    if leftover:
        raise SystemExit(f"clean failed; leftover manifests: {len(leftover)}")

    code = run(
        "e2rr_preflight_seed29001",
        [PYTHON, "scripts/prepare_e2_traffic_real_runner_canary.py", "--preflight"],
        outputs=["outputs/audits/E2_TRAFFIC_REAL_RUNNER_CANARY_INPUT_IDENTITY.json"],
        inputs=list(FROZEN_INPUTS),
        seed=29001,
        profile_id="PROFILE-S1",
        run_kind="preflight",
    )
    if code != 0:
        return code

    et_outputs = [
        f"outputs/e2_traffic_real_runner_canary/eventtraces/{sid}/training_eventtrace/trace_identity.json"
        for sid in SCENARIOS
    ] + ["outputs/audits/E2_TRAFFIC_CANARY_CROSS_METHOD_TRACE_IDENTITY.json"]
    code = run(
        "e2rr_generate_six_eventtraces_seed29001",
        [PYTHON, "scripts/prepare_e2_traffic_real_runner_canary.py", "--generate-eventtraces"],
        outputs=et_outputs,
        inputs=list(FROZEN_INPUTS),
        seed=29001,
        profile_id="PROFILE-S1",
        run_kind="eventtrace_generation",
    )
    if code != 0:
        return code

    for scenario in SCENARIOS:
        for method in METHODS:
            label = f"e2rr_train_seed29001__{scenario}__{method}"
            run_dir = f"outputs/e2_traffic_real_runner_canary/runs/{scenario}/{method}"
            inputs = list(FROZEN_INPUTS) + [
                f"outputs/e2_traffic_real_runner_canary/eventtraces/{scenario}/training_eventtrace/trace_identity.json",
                f"outputs/e2_traffic_real_runner_canary/eventtraces/{scenario}/training_eventtrace/events.parquet",
            ]
            outputs = [
                f"{run_dir}/runtime_manifest.json",
                f"{run_dir}/config_snapshot.json",
                f"{run_dir}/window_metrics.parquet",
                f"{run_dir}/runner_diagnostics.parquet",
                f"{run_dir}/checkpoints/final.pt",
            ]
            code = run(
                label,
                [
                    PYTHON, "scripts/prepare_e2_traffic_real_runner_canary.py",
                    "--run-one", "--scenario", scenario, "--method", method,
                ],
                outputs=outputs,
                inputs=inputs,
                seed=29001,
                scenario=scenario,
                method=method,
                profile_id="PROFILE-S1",
                run_kind="training",
                expected_windows=100,
            )
            if code != 0:
                print(f"TRAINING_FAILED {scenario} {method} exit={code}", flush=True)
                return code

    code = run(
        "e2rr_finalize_existing_seed29001",
        [PYTHON, "scripts/prepare_e2_traffic_real_runner_canary.py", "--finalize-existing"],
        outputs=[
            "outputs/e2_traffic_real_runner_canary/canary_summary_seed29001.json",
            "outputs/e2_traffic_real_runner_canary/main_results_seed29001.csv",
            "outputs/e2_traffic_real_runner_canary/E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json",
        ],
        inputs=list(FROZEN_INPUTS),
        seed=29001,
        profile_id="PROFILE-S1",
        run_kind="finalization",
    )
    if code != 0:
        return code

    steps = [
        (
            "ledger_unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_traffic_real_runner_ledger_g9.py",
             "--junitxml=logs/e2_traffic_real_runner_ledger_g9_unit.xml"],
            ["logs/e2_traffic_real_runner_ledger_g9_unit.xml"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_traffic_real_runner_canary_core.py",
             "--junitxml=logs/e2_traffic_real_runner_canary_unit.xml"],
            ["logs/e2_traffic_real_runner_canary_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_traffic_real_runner_canary_stop.py",
             "--junitxml=logs/e2_traffic_real_runner_canary_integration.xml"],
            ["logs/e2_traffic_real_runner_canary_integration.xml"],
        ),
        (
            "full_repository_pytest",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_traffic_real_runner_canary_full_repository.xml"],
            ["logs/e2_traffic_real_runner_canary_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-m", "pip", "check"],
            [],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_traffic_real_runner_canary_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_replay",
            [PYTHON, "scripts/check_e2_traffic_real_runner_canary_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "ledger_closure_export",
            [PYTHON, "scripts/export_e2_traffic_real_runner_ledger_closure_evidence.py"],
            [
                "deliverables/TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1/"
                "TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1.zip",
                "deliverables/TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1/"
                "FINAL_DELIVERABLE_HASHES_VERIFY.json",
            ],
        ),
    ]
    for label, command, outputs in steps:
        if label == "pip_check":
            code = run(label, command, outputs=[], run_kind="pip_check")
            (ROOT / "logs/e2rr_pip_check.txt").write_text("pip check completed\n", encoding="utf-8")
            if code != 0:
                return code
            continue
        code = run(label, command, outputs=outputs, run_kind=label)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
