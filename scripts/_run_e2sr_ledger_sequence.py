#!/usr/bin/env python3
"""Final E2SR ledger: verify → tests → unpack → gates → export."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")
LEDGER = "logs/E2_STAGE2_ELIGIBILITY_AND_TRUE_STRATUM_REFREEZE_R1_EXACT_COMMANDS.jsonl"
PKG = "E2_STAGE2_ELIGIBILITY_AND_TRUE_STRATUM_REFREEZE_R1"


def run(label: str, command: list[str], outputs: list[str] | None = None) -> int:
    cmd = [
        PY, "scripts/run_and_log.py",
        "--ledger", LEDGER,
        "--label", label,
        "--stdout-log", f"logs/e2sr_{label}.stdout.log",
        "--stderr-log", f"logs/e2sr_{label}.stderr.log",
    ]
    for out in outputs or []:
        cmd.extend(["--output", out])
    cmd.append("--")
    cmd.extend(command)
    print(">>", label, flush=True)
    return subprocess.call(cmd, cwd=ROOT)


def main() -> int:
    ledger = ROOT / LEDGER
    if ledger.is_file():
        ledger.unlink()
    steps = [
        (
            "verify_prepare",
            [PY, "scripts/_verify_e2sr_prepare.py"],
            ["outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json"],
        ),
        (
            "unit_tests",
            [PY, "-m", "pytest", "-q",
             "tests/unit/test_e2_stage2_stratum_core.py",
             "--junitxml=logs/e2_stage2_stratum_unit.xml"],
            ["logs/e2_stage2_stratum_unit.xml"],
        ),
        (
            "integration_tests",
            [PY, "-m", "pytest", "-q",
             "tests/integration/test_e2_stage2_stratum_integration.py",
             "--junitxml=logs/e2_stage2_stratum_integration.xml"],
            ["logs/e2_stage2_stratum_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PY, "-m", "pytest", "-q",
             "--junitxml=logs/e2_stage2_stratum_full_repository.xml"],
            ["logs/e2_stage2_stratum_full_repository.xml"],
        ),
        ("pip_check", [PY, "-m", "pip", "check"], []),
        (
            "unpacked_specialized",
            [PY, "scripts/_e2sr_unpacked_specialized.py"],
            ["logs/e2_stage2_stratum_unpacked_specialized.xml"],
        ),
        (
            "e2sr_gates",
            [PY, "scripts/check_e2_stage2_stratum_gates.py"],
            [f"outputs/gates/{PKG}_GATES.json"],
        ),
        (
            "export_evidence",
            [PY, "scripts/export_e2_stage2_stratum_evidence.py"],
            [
                f"deliverables/TO_SUBMIT_{PKG}/RAVEN_MCS_{PKG}_EVIDENCE.zip",
                f"deliverables/TO_SUBMIT_{PKG}/FINAL_DELIVERABLE_HASHES.json",
            ],
        ),
    ]
    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if label == "pip_check":
            src = ROOT / "logs/e2sr_pip_check.stdout.log"
            if src.is_file():
                (ROOT / "logs/e2_stage2_stratum_pip_check.txt").write_text(
                    src.read_text(encoding="utf-8"), encoding="utf-8",
                )
        if code != 0:
            print(json.dumps({"failed_step": label, "exit_code": code}, indent=2))
            return code
    print(json.dumps({"status": "LEDGER_SEQUENCE_PASS"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
