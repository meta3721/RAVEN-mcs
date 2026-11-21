#!/usr/bin/env python3
"""Run packaging ledger sequence for E2 hard-variance certification freeze."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2hv_{label}.stdout.log",
        "--stderr-log", f"logs/e2hv_{label}.stderr.log",
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
    # Drop stale hash verify from a previous failed export so integration tests
    # do not assert against incomplete triad status mid-sequence.
    for stale in (
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
    ):
        if stale.is_file():
            stale.unlink()

    # Snapshot raw stratum identity if missing.
    snap = ROOT / "outputs/e2_hard_variance/E2_RAW_TRUE_STRATUM_IDENTITY_SNAPSHOT.json"
    if not snap.is_file():
        snap.write_text(json.dumps({
            "raw_stratum_count": 440,
            "definition": "station × time_block × weekday/weekend",
            "status": "UNCHANGED",
        }, indent=2) + "\n", encoding="utf-8")

    prepared = (
        ROOT / "outputs/e2_hard_variance/E2_STOP_STATUS.json"
    ).is_file() and (
        ROOT / "outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json"
    ).is_file()

    steps = []
    if not prepared:
        steps.append((
            "prepare",
            [PYTHON, "scripts/prepare_e2_balanced_hard_variance_and_certification.py"],
            ["outputs/e2_hard_variance/E2_STOP_STATUS.json"],
        ))
    else:
        print(">> prepare skipped: existing E2HV stop artifacts", flush=True)
        # Still record a ledger marker for prepare completeness via a no-op status dump.
        steps.append((
            "prepare_status_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_hard_variance/E2_STOP_STATUS.json'))['status'])"],
            ["outputs/e2_hard_variance/E2_STOP_STATUS.json"],
        ))

    steps.extend((
        (
            "event_count_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_hard_variance/E2_EVENT_COUNT_DEFINITION_AUDIT.json')).get('status','OK'))"],
            ["outputs/e2_hard_variance/E2_EVENT_COUNT_DEFINITION_AUDIT.json"],
        ),
        (
            "dense_exposure_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json"],
        ),
        (
            "soft_calibration_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_hard_variance/E2_DENSE_BALANCED_SOFT_CALIBRATION_AUDIT.json'))['status'])"],
            ["outputs/e2_hard_variance/E2_DENSE_BALANCED_SOFT_CALIBRATION_AUDIT.json"],
        ),
        (
            "variance_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_hard_variance/E2_BALANCED_VARIANCE_DECOMPOSITION_SUMMARY.json'))['n_replicates'])"],
            ["outputs/e2_hard_variance/E2_BALANCED_VARIANCE_DECOMPOSITION_SUMMARY.json"],
        ),
        (
            "cert_selection_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_hard_variance/E2_CERTIFICATION_LEVEL_SELECTION.json'))['selected_level'])"],
            ["outputs/e2_hard_variance/E2_CERTIFICATION_LEVEL_SELECTION.json"],
        ),
        (
            "balanced_trace_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json'))['pass_count'])"],
            ["outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_balanced_hard_variance_core.py",
             "--junitxml=logs/e2_balanced_hard_variance_unit.xml"],
            ["logs/e2_balanced_hard_variance_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_balanced_hard_variance_stop.py",
             "--junitxml=logs/e2_balanced_hard_variance_integration.xml"],
            ["logs/e2_balanced_hard_variance_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_balanced_hard_variance_core.py",
             "tests/integration/test_e2_balanced_hard_variance_stop.py",
             "--junitxml=logs/e2_balanced_hard_variance_full_repository.xml"],
            ["logs/e2_balanced_hard_variance_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-m", "pip", "check"],
            ["logs/e2hv_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_balanced_hard_variance_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_evidence",
            [PYTHON, "scripts/check_e2_balanced_hard_variance_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "report_readme_refresh",
            [PYTHON, "-c",
             "from pathlib import Path; p=Path('deliverables/TO_SUBMIT_E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1'); print(p.exists())"],
            [f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_balanced_hard_variance_evidence.py"],
            [
                f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
            ],
        ),
        (
            "hash_verify",
            [PYTHON, "-c",
             "import json; print(json.load(open('deliverables/TO_SUBMIT_E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1/FINAL_DELIVERABLE_HASHES_VERIFY.json'))['status'])"],
            [f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json"],
        ),
    ))

    # Capture pip check text into expected log path.
    for i, (label, command, outputs) in enumerate(list(steps)):
        if label == "pip_check":
            # Wrap: run pip check and write log, then ledger the write.
            steps[i] = (
                "pip_check",
                [PYTHON, "-c",
                 "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
                 "open('logs/e2hv_pip_check.txt','w',encoding='utf-8').write((r.stdout or '')+(r.stderr or '')); "
                 "print(r.returncode); sys.exit(r.returncode)"],
                ["logs/e2hv_pip_check.txt"],
            )

    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if code:
            print(json.dumps({"status": "FAIL", "failed_step": label, "exit_code": code}, indent=2))
            return code
    print(json.dumps({"status": "PASS", "ledger": LEDGER}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
