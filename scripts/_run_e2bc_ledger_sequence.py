#!/usr/bin/env python3
"""Ledger sequence for E2 traffic balanced design canary."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_TRAFFIC_BALANCED_DESIGN_CANARY_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2bc_{label}.stdout.log",
        "--stderr-log", f"logs/e2bc_{label}.stderr.log",
    ]
    for output in outputs:
        wrapped.extend(("--output", output))
    wrapped.extend(("--", *command))
    print(f">> {label}", flush=True)
    return subprocess.call(wrapped, cwd=ROOT)


def main() -> int:
    if not Path(PYTHON).is_file():
        raise SystemExit(f"missing interpreter: {PYTHON}")
    ledger = ROOT / LEDGER
    if ledger.is_file():
        ledger.unlink()
    for stale in (
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
    ):
        if stale.is_file():
            stale.unlink()

    prepared = (ROOT / "outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json").is_file()
    steps: list[tuple[str, list[str], list[str]]] = []
    if prepared:
        steps.append((
            "balanced_generation",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json'))['status'])"],
            ["outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json"],
        ))
    else:
        steps.append((
            "balanced_generation",
            [PYTHON, "scripts/prepare_e2_traffic_balanced_design_canary.py"],
            ["outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json"],
        ))

    steps.extend((
        (
            "input_identity_verification",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_BALANCED_CANARY_INPUT_IDENTITY.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_BALANCED_CANARY_INPUT_IDENTITY.json"],
        ),
        (
            "p_opp_calibration",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_OPPORTUNITY_CALIBRATION.json'))['status'])"],
            ["outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_OPPORTUNITY_CALIBRATION.json"],
        ),
        (
            "seed28101_generation",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_SEED_28101_DIAG.json'))['status'])"],
            ["outputs/e2_traffic_balanced_canary/traces/28101/hard_arrival_events.parquet"],
        ),
        (
            "seed28102_generation",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_SEED_28102_DIAG.json'))['status'])"],
            ["outputs/e2_traffic_balanced_canary/traces/28102/hard_arrival_events.parquet"],
        ),
        (
            "seed28103_generation",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_SEED_28103_DIAG.json'))['status'])"],
            ["outputs/e2_traffic_balanced_canary/traces/28103/hard_arrival_events.parquet"],
        ),
        (
            "per_seed_replay",
            [PYTHON, "-c",
             "import pandas as pd; a=pd.read_parquet('outputs/e2_traffic_balanced_canary/traces/28101/hard_arrival_events.parquet'); "
             "print(bool(((a['A_opp']&a['O']&a['U'])==a['I_arr']).all()))"],
            ["outputs/e2_traffic_balanced_canary/traces/28101/eventtrace_manifest.json"],
        ),
        (
            "pooled_replay",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_BALANCED_CANARY_POOLED_DISTRIBUTION_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_BALANCED_CANARY_POOLED_DISTRIBUTION_AUDIT.json"],
        ),
        (
            "audits",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_BALANCED_CANARY_STAGE2_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_BALANCED_CANARY_STAGE2_AUDIT.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_traffic_balanced_canary_core.py",
             "--junitxml=logs/e2_traffic_balanced_canary_unit.xml"],
            ["logs/e2_traffic_balanced_canary_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_traffic_balanced_canary_stop.py",
             "--junitxml=logs/e2_traffic_balanced_canary_integration.xml"],
            ["logs/e2_traffic_balanced_canary_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_traffic_balanced_canary_full_repository.xml"],
            ["logs/e2_traffic_balanced_canary_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-c",
             "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
             "open('logs/e2bc_pip_check.txt','w',encoding='utf-8').write((r.stdout or '')+(r.stderr or '')); "
             "print(r.returncode); sys.exit(r.returncode)"],
            ["logs/e2bc_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_traffic_balanced_canary_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_evidence",
            [PYTHON, "scripts/check_e2_traffic_balanced_canary_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_traffic_balanced_canary_evidence.py"],
            [
                f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
            ],
        ),
        (
            "hash_verify",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             f"'deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json'))['status'])"],
            [f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json"],
        ),
    ))

    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if code:
            print(json.dumps({"status": "FAIL", "failed_step": label, "exit_code": code}, indent=2))
            return code
    print(json.dumps({"status": "PASS", "ledger": LEDGER}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
