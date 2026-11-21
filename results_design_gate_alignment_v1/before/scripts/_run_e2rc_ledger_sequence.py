#!/usr/bin/env python3
"""Ledger sequence for E2 traffic profile runner consistency hotfix."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_HOTFIX_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2rc_{label}.stdout.log",
        "--stderr-log", f"logs/e2rc_{label}.stderr.log",
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

    steps = [
        (
            "hotfix_generation",
            [PYTHON, "scripts/prepare_e2_traffic_profile_runner_consistency_hotfix.py"],
            ["outputs/e2_traffic_runner_consistency/E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json"],
        ),
        (
            "input_identity_verification",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_RUNNER_CONSISTENCY_INPUT_IDENTITY.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_RUNNER_CONSISTENCY_INPUT_IDENTITY.json"],
        ),
        (
            "parameter_seal",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json"],
        ),
        (
            "exact_expected_mass",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_EXACT_EXPECTED_MASS_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_EXACT_EXPECTED_MASS_AUDIT.json"],
        ),
        (
            "clip_support_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PROFILE_CLIP_AND_SUPPORT_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_PROFILE_CLIP_AND_SUPPORT_AUDIT.json"],
        ),
        (
            "old_trace_tombstone",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_OLD_TRACE_TOMBSTONE.json'))"
             "['invalid_due_to_seed_specific_intercept_recalibration'])"],
            ["outputs/audits/E2_TRAFFIC_OLD_TRACE_TOMBSTONE.json"],
        ),
        (
            "direction_certification",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'configs/frozen/e2_traffic_profiles/traffic_s1_s6_runner_consistent_direction_certificate.json'))['status'])"],
            ["configs/frozen/e2_traffic_profiles/traffic_s1_s6_runner_consistent_direction_certificate.json"],
        ),
        (
            "registry_freeze",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'configs/frozen/e2_traffic_profiles/traffic_s1_s6_profile_registry.json'))['status'])"],
            ["configs/frozen/e2_traffic_profiles/traffic_s1_s6_profile_registry.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_traffic_profile_runner_consistency_core.py",
             "--junitxml=logs/e2_traffic_profile_runner_consistency_unit.xml"],
            ["logs/e2_traffic_profile_runner_consistency_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_traffic_profile_runner_consistency_stop.py",
             "--junitxml=logs/e2_traffic_profile_runner_consistency_integration.xml"],
            ["logs/e2_traffic_profile_runner_consistency_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_traffic_profile_runner_consistency_full_repository.xml"],
            ["logs/e2_traffic_profile_runner_consistency_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-c",
             "import subprocess,sys; from pathlib import Path; "
             "r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
             "Path('logs/e2rc_pip_check.txt').write_text((r.stdout or '')+(r.stderr or ''),encoding='utf-8'); "
             "print(r.returncode); raise SystemExit(r.returncode)"],
            ["logs/e2rc_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_traffic_profile_runner_consistency_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_replay",
            [PYTHON, "scripts/check_e2_traffic_profile_runner_consistency_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_traffic_profile_runner_consistency_evidence.py"],
            [f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"],
        ),
        (
            "hash_verify",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             f"'deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json'))['status'])"],
            [f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json"],
        ),
    ]
    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if code != 0:
            print(f"FAILED {label} exit={code}", flush=True)
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
