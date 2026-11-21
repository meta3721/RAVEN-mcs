#!/usr/bin/env python3
"""Ledger sequence for E2 Traffic S1-S6 profile freeze."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2pf_{label}.stdout.log",
        "--stderr-log", f"logs/e2pf_{label}.stderr.log",
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

    steps: list[tuple[str, list[str], list[str]]] = [
        (
            "profile_generation",
            [PYTHON, "scripts/prepare_e2_traffic_s1_s6_profile_freeze.py"],
            ["outputs/e2_traffic_profiles/E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json"],
        ),
        (
            "input_identity_verification",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_S1_S6_INPUT_IDENTITY_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_S1_S6_INPUT_IDENTITY_AUDIT.json"],
        ),
        (
            "q_runtime_seal",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_Q_RUNTIME_INTERFACE_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_Q_RUNTIME_INTERFACE_AUDIT.json"],
        ),
        (
            "expected_mass_check",
            [PYTHON, "-c",
             "from pathlib import Path; p=Path('outputs/e2_traffic_profiles/scenarios/balanced/"
             "expected_arrival_mass.parquet'); print(p.is_file(), p.stat().st_size)"],
            ["outputs/e2_traffic_profiles/scenarios/balanced/expected_arrival_mass.parquet"],
        ),
        (
            "direction_certification",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'configs/frozen/e2_traffic_profiles/traffic_s1_s6_direction_certificate.json'))['status'])"],
            ["configs/frozen/e2_traffic_profiles/traffic_s1_s6_direction_certificate.json"],
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
             "tests/unit/test_e2_traffic_s1_s6_profile_freeze_core.py",
             "--junitxml=logs/e2_traffic_s1_s6_profile_freeze_unit.xml"],
            ["logs/e2_traffic_s1_s6_profile_freeze_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_traffic_s1_s6_profile_freeze_stop.py",
             "--junitxml=logs/e2_traffic_s1_s6_profile_freeze_integration.xml"],
            ["logs/e2_traffic_s1_s6_profile_freeze_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_traffic_s1_s6_profile_freeze_full_repository.xml"],
            ["logs/e2_traffic_s1_s6_profile_freeze_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-m", "pip", "check"],
            ["logs/e2pf_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_traffic_s1_s6_profile_freeze_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_replay",
            [PYTHON, "scripts/check_e2_traffic_s1_s6_profile_freeze_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_traffic_s1_s6_profile_freeze_evidence.py"],
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

    # Capture pip_check stdout into file via wrapper that writes output
    # Replace pip_check step with a small python that runs pip check and writes file
    for i, (label, cmd, outs) in enumerate(steps):
        if label == "pip_check":
            steps[i] = (
                "pip_check",
                [PYTHON, "-c",
                 "import subprocess,sys; from pathlib import Path; "
                 "r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
                 "Path('logs/e2pf_pip_check.txt').write_text((r.stdout or '')+(r.stderr or ''),encoding='utf-8'); "
                 "print(r.returncode); raise SystemExit(r.returncode)"],
                ["logs/e2pf_pip_check.txt"],
            )

    rc = 0
    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if code != 0:
            rc = code
            print(f"FAILED {label} exit={code}", flush=True)
            break
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
