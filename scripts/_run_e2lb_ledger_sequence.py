#!/usr/bin/env python3
"""Run the non-training E2LB packaging ledger sequence."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_LEGAL_HORIZON_AND_BALANCED_OPPORTUNITY_CALIBRATION_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2lb_{label}.stdout.log",
        "--stderr-log", f"logs/e2lb_{label}.stderr.log",
    ]
    for output in outputs:
        wrapped.extend(("--output", output))
    wrapped.extend(("--", *command))
    print(f">> {label}", flush=True)
    return subprocess.call(wrapped, cwd=ROOT)


def main() -> int:
    if not Path(PYTHON).is_file():
        raise SystemExit(f"missing required interpreter: {PYTHON}")
    ledger = ROOT / LEDGER
    if ledger.is_file():
        ledger.unlink()
    prepared = (
        ROOT / "outputs/e2_balanced_calibration/E2_STOP_STATUS.json"
    ).is_file() and (
        ROOT / "outputs/e2_balanced_calibration/E2_BALANCED_PRE_GATE_SUMMARY.json"
    ).is_file()
    steps = []
    if not prepared:
        steps.append((
            "prepare", [PYTHON, "scripts/prepare_e2_legal_horizon_and_balanced_calibration.py"],
            ["outputs/e2_balanced_calibration/E2_STOP_STATUS.json"],
        ))
    else:
        print(">> prepare skipped: existing E2LB stop artifacts", flush=True)
    steps.extend((
        (
            "tests", [PYTHON, "-m", "pytest", "-q", "tests/test_e2_legal_horizon_balanced_calibration.py",
                      "--junitxml=logs/e2_legal_horizon_balanced_calibration.xml"],
            ["logs/e2_legal_horizon_balanced_calibration.xml"],
        ),
        (
            "gates", [PYTHON, "scripts/check_e2_legal_horizon_balanced_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_evidence", [PYTHON, "scripts/check_e2_legal_horizon_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export", [PYTHON, "scripts/export_e2_legal_horizon_balanced_evidence.py"],
            [
                f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
            ],
        ),
    ))
    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if code:
            print(json.dumps({"status": "FAIL", "failed_step": label, "exit_code": code}, indent=2))
            return code
    print(json.dumps({"status": "PASS", "prepare": "SKIPPED" if prepared else "RUN", "ledger": LEDGER}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
