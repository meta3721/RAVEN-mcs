#!/usr/bin/env python3
"""Ledger sequence for E2 PROFILE-S1 final freeze."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2s1_{label}.stdout.log",
        "--stderr-log", f"logs/e2s1_{label}.stderr.log",
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
            "profile_s1_generation",
            [PYTHON, "scripts/prepare_e2_traffic_profile_s1_final_freeze.py"],
            ["outputs/e2_traffic_profile_s1/E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json"],
        ),
        (
            "input_identity_verification",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PROFILE_S1_INPUT_IDENTITY_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_PROFILE_S1_INPUT_IDENTITY_AUDIT.json"],
        ),
        (
            "profile_s2_tombstone",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PROFILE_S2_SUPPORT_TOMBSTONE.json'))['prior_strength'])"],
            ["outputs/audits/E2_TRAFFIC_PROFILE_S2_SUPPORT_TOMBSTONE.json"],
        ),
        (
            "deterministic_intercept_solve",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PROFILE_S1_PARAMETER_CONSISTENCY_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_PROFILE_S1_PARAMETER_CONSISTENCY_AUDIT.json"],
        ),
        (
            "exact_expected_mass",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PROFILE_S1_EXACT_EXPECTED_MASS_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_PROFILE_S1_EXACT_EXPECTED_MASS_AUDIT.json"],
        ),
        (
            "clip_support_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json"],
        ),
        (
            "direction_certification",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_direction_certificate.json'))['status'])"],
            ["configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_direction_certificate.json"],
        ),
        (
            "registry_freeze",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json'))['status'])"],
            ["configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_traffic_profile_s1_final_freeze_core.py",
             "--junitxml=logs/e2_traffic_profile_s1_final_freeze_unit.xml"],
            ["logs/e2_traffic_profile_s1_final_freeze_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_traffic_profile_s1_final_freeze_stop.py",
             "--junitxml=logs/e2_traffic_profile_s1_final_freeze_integration.xml"],
            ["logs/e2_traffic_profile_s1_final_freeze_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_traffic_profile_s1_final_freeze_full_repository.xml"],
            ["logs/e2_traffic_profile_s1_final_freeze_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-c",
             "import subprocess,sys; from pathlib import Path; "
             "r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
             "Path('logs/e2s1_pip_check.txt').write_text((r.stdout or '')+(r.stderr or ''),encoding='utf-8'); "
             "print(r.returncode); raise SystemExit(r.returncode)"],
            ["logs/e2s1_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_traffic_profile_s1_final_freeze_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_replay",
            [PYTHON, "scripts/check_e2_traffic_profile_s1_final_freeze_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_traffic_profile_s1_final_freeze_evidence.py"],
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
