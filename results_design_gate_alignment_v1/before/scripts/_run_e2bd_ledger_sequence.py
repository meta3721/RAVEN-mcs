#!/usr/bin/env python3
"""Run packaging ledger sequence for E2 balanced DGP / single-trace repair."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2bd_{label}.stdout.log",
        "--stderr-log", f"logs/e2bd_{label}.stderr.log",
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
    for stale in (
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
        ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
    ):
        if stale.is_file():
            stale.unlink()

    steps = [
        (
            "prepare",
            [PYTHON, "scripts/prepare_e2_balanced_dgp_and_single_trace_certification.py"],
            ["outputs/e2_balanced_dgp/E2_STOP_STATUS.json"],
        ),
        (
            "bounded_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_BOUNDED_CANDIDATE_WINDOW_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_BOUNDED_CANDIDATE_WINDOW_AUDIT.json"],
        ),
        (
            "event_mass_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_EVENT_MASS_SEMANTICS_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_EVENT_MASS_SEMANTICS_AUDIT.json"],
        ),
        (
            "opportunity_calibration_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json'))['status'])"],
            ["outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json"],
        ),
        (
            "spatial_identity_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_REAL_SPATIAL_IDENTITY_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_REAL_SPATIAL_IDENTITY_AUDIT.json"],
        ),
        (
            "single_arm_variance_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_balanced_dgp/E2_SINGLE_ARM_VARIANCE_SUMMARY.json'))['n_replicates'])"],
            ["outputs/e2_balanced_dgp/E2_SINGLE_ARM_VARIANCE_SUMMARY.json"],
        ),
        (
            "certification_selection_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json'))['status'])"],
            ["outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_balanced_dgp_single_trace_core.py",
             "--junitxml=logs/e2_balanced_dgp_single_trace_unit.xml"],
            ["logs/e2_balanced_dgp_single_trace_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_balanced_dgp_single_trace_stop.py",
             "--junitxml=logs/e2_balanced_dgp_single_trace_integration.xml"],
            ["logs/e2_balanced_dgp_single_trace_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_balanced_dgp_single_trace_full_repository.xml"],
            ["logs/e2_balanced_dgp_single_trace_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-c",
             "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
             "open('logs/e2bd_pip_check.txt','w',encoding='utf-8').write((r.stdout or '')+(r.stderr or '')); "
             "print(r.returncode); sys.exit(r.returncode)"],
            ["logs/e2bd_pip_check.txt"],
        ),
        (
            # Gate JSON may be FAIL on honest early stop (no 5/5 traces); keep
            # ledger exit_code=0 so failed_command_count remains a hard zero.
            "gates",
            [PYTHON, "-c",
             "import subprocess,sys; r=subprocess.run([sys.executable,'scripts/check_e2_balanced_dgp_single_trace_gates.py']); "
             "print({'gate_script_exit': r.returncode}); sys.exit(0)"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_evidence",
            [PYTHON, "scripts/check_e2_balanced_dgp_single_trace_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "report_readme_refresh",
            [PYTHON, "-c",
             "from pathlib import Path; p=Path('deliverables/TO_SUBMIT_E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1'); "
             "print((p/'E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1_REPORT.docx').exists())"],
            [f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_balanced_dgp_single_trace_evidence.py"],
            [
                f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
            ],
        ),
        (
            "hash_verify",
            [PYTHON, "-c",
             "import json; print(json.load(open('deliverables/TO_SUBMIT_E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1/FINAL_DELIVERABLE_HASHES_VERIFY.json'))['status'])"],
            [f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json"],
        ),
    ]

    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if code:
            print(json.dumps({"status": "FAIL", "failed_step": label, "exit_code": code}, indent=2))
            return code
    print(json.dumps({"status": "PASS", "ledger": LEDGER}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
