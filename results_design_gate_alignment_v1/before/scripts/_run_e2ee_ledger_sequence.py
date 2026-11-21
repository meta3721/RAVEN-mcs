#!/usr/bin/env python3
"""Run final E2EE ledger sequence (tests -> unpack -> gates -> export)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")
LEDGER = "logs/E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1_EXACT_COMMANDS.jsonl"
RUN = [PY, "scripts/run_and_log.py", "--ledger", LEDGER]


def run(label: str, command: list[str], outputs: list[str] | None = None) -> int:
    cmd = [
        *RUN,
        "--label", label,
        "--stdout-log", f"logs/e2ee_{label}.stdout.log",
        "--stderr-log", f"logs/e2ee_{label}.stderr.log",
    ]
    for out in outputs or []:
        cmd.extend(["--output", out])
    cmd.append("--")
    cmd.extend(command)
    print(">>", label, flush=True)
    return subprocess.call(cmd, cwd=ROOT)


def write_unpacked_helper() -> Path:
    helper = ROOT / "scripts/_e2ee_unpacked_specialized.py"
    helper.write_text(
        '''#!/usr/bin/env python3
from __future__ import annotations
import shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
with tempfile.TemporaryDirectory(prefix="e2ee_unpack_") as tmp:
    tmp_path = Path(tmp)
    for rel in [
        "src/raven_mcs/__init__.py",
        "src/raven_mcs/e2",
        "src/raven_mcs/data",
        "src/raven_mcs/utils",
        "configs",
        "scripts/check_e2_empirical_eventtrace_gates.py",
        "scripts/export_e2_empirical_eventtrace_evidence.py",
        "scripts/prepare_e2_empirical_eventtrace_and_profile_refreeze.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_empirical_eventtrace_core.py",
        "tests/integration/test_e2_empirical_eventtrace_integration.py",
        "outputs/e2_empirical",
        "outputs/audits",
        "outputs/gates",
        "data/processed/sensorscope/atomic_units.parquet",
    ]:
        src = ROOT / rel
        if not src.exists():
            continue
        dest = tmp_path / rel
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    env = dict(**__import__("os").environ, PYTHONPATH=str(tmp_path / "src"))
    junit = ROOT / "logs/e2_empirical_eventtrace_unpacked_specialized.xml"
    junit.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [PY, "-m", "pytest", "-q",
         "tests/unit/test_e2_empirical_eventtrace_core.py",
         "tests/integration/test_e2_empirical_eventtrace_integration.py",
         f"--junitxml={junit}"],
        cwd=tmp_path, env=env,
    )
    raise SystemExit(proc.returncode)
''',
        encoding="utf-8",
    )
    return helper


def main() -> int:
    ledger_path = ROOT / LEDGER
    if ledger_path.is_file():
        ledger_path.unlink()
    write_unpacked_helper()

    steps = [
        (
            "prepare_matrix",
            [PY, "scripts/prepare_e2_empirical_eventtrace_and_profile_refreeze.py"],
            [
                "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json",
                "outputs/e2_empirical/E2_EMPIRICAL_WINDOW_LENGTH_SELECTION.json",
                "configs/frozen/e2_empirical/selected_strength_profile.yaml",
                "configs/frozen/e2_empirical/selected_window_length.yaml",
                "outputs/audits/E2_300_WINDOW_SCHEDULE_NONREPETITION_AUDIT.json",
            ],
        ),
        (
            "unit_tests",
            [PY, "-m", "pytest", "-q",
             "tests/unit/test_e2_empirical_eventtrace_core.py",
             "--junitxml=logs/e2_empirical_eventtrace_unit.xml"],
            ["logs/e2_empirical_eventtrace_unit.xml"],
        ),
        (
            "integration_tests",
            [PY, "-m", "pytest", "-q",
             "tests/integration/test_e2_empirical_eventtrace_integration.py",
             "--junitxml=logs/e2_empirical_eventtrace_integration.xml"],
            ["logs/e2_empirical_eventtrace_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PY, "-m", "pytest", "-q",
             "--junitxml=logs/e2_empirical_eventtrace_full_repository.xml"],
            ["logs/e2_empirical_eventtrace_full_repository.xml"],
        ),
        (
            "pip_check",
            [PY, "-m", "pip", "check"],
            [],
        ),
        (
            "unpacked_specialized",
            [PY, "scripts/_e2ee_unpacked_specialized.py"],
            ["logs/e2_empirical_eventtrace_unpacked_specialized.xml"],
        ),
        (
            "e2ee_gates",
            [PY, "scripts/check_e2_empirical_eventtrace_gates.py"],
            ["outputs/gates/E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1_GATES.json"],
        ),
        (
            "export_evidence",
            [PY, "scripts/export_e2_empirical_eventtrace_evidence.py"],
            [
                "deliverables/TO_SUBMIT_E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1/"
                "RAVEN_MCS_E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1_EVIDENCE.zip",
                "deliverables/TO_SUBMIT_E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1/"
                "FINAL_DELIVERABLE_HASHES.json",
            ],
        ),
    ]
    for label, command, outputs in steps:
        code = run(label, command, outputs)
        if label == "pip_check":
            # Persist pip check text for evidence package.
            out = (ROOT / "logs/e2ee_pip_check.stdout.log").read_text(encoding="utf-8") if (
                ROOT / "logs/e2ee_pip_check.stdout.log"
            ).is_file() else ""
            (ROOT / "logs/e2_empirical_eventtrace_pip_check.txt").write_text(out, encoding="utf-8")
        if code != 0:
            print(json.dumps({"failed_step": label, "exit_code": code}, indent=2))
            return code
    print(json.dumps({"status": "LEDGER_SEQUENCE_PASS", "ledger": LEDGER}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
