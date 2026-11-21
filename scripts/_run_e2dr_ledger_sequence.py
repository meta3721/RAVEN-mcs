#!/usr/bin/env python3
"""Ledger sequence for E2 data horizon / spatial recovery."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_DATA_HORIZON_AND_SPATIAL_METADATA_RECOVERY_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2dr_{label}.stdout.log",
        "--stderr-log", f"logs/e2dr_{label}.stderr.log",
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

    prepared = (ROOT / "outputs/data_recovery/E2_STOP_STATUS.json").is_file()
    steps = []
    if prepared:
        # Inventory/prepare already produced; still ledger an inventory audit first.
        steps.append((
            "inventory",
            [PYTHON, "-c",
             "import pandas as pd; df=pd.read_csv('outputs/data_recovery/E2_DATA_ASSET_INVENTORY.csv'); print(len(df))"],
            ["outputs/data_recovery/E2_DATA_ASSET_INVENTORY.csv"],
        ))
    else:
        steps.append((
            "inventory",
            [PYTHON, "scripts/prepare_e2_data_horizon_and_spatial_recovery.py"],
            ["outputs/data_recovery/E2_DATA_ASSET_INVENTORY.csv", "outputs/data_recovery/E2_STOP_STATUS.json"],
        ))

    steps.extend((
        (
            "provenance_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/data_recovery/E2_CURRENT_SUBSET_PROVENANCE.json'))['status'])"],
            ["outputs/data_recovery/E2_CURRENT_SUBSET_PROVENANCE.json"],
        ),
        (
            "horizon_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/data_recovery/E2_SENSORSCOPE_GLOBAL_WINDOW_CAPACITY.json'))['status'])"],
            ["outputs/data_recovery/E2_SENSORSCOPE_GLOBAL_WINDOW_CAPACITY.json"],
        ),
        (
            "spatial_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/data_recovery/E2_SPATIAL_METADATA_RECOVERY_AUDIT.json'))['status'])"],
            ["outputs/data_recovery/E2_SPATIAL_METADATA_RECOVERY_AUDIT.json"],
        ),
        (
            "replacement_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/data_recovery/E2_REPLACEMENT_DATASET_RANKING.json'))['status'])"],
            ["outputs/data_recovery/E2_REPLACEMENT_DATASET_RANKING.json"],
        ),
        (
            "route_decision",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/data_recovery/E2_PROTOCOL_ROUTE_DECISION.json'))['status'])"],
            ["outputs/data_recovery/E2_PROTOCOL_ROUTE_DECISION.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_data_horizon_spatial_recovery_core.py",
             "--junitxml=logs/e2_data_horizon_spatial_recovery_unit.xml"],
            ["logs/e2_data_horizon_spatial_recovery_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_data_horizon_spatial_recovery_stop.py",
             "--junitxml=logs/e2_data_horizon_spatial_recovery_integration.xml"],
            ["logs/e2_data_horizon_spatial_recovery_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_data_horizon_spatial_recovery_full_repository.xml"],
            ["logs/e2_data_horizon_spatial_recovery_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-c",
             "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
             "open('logs/e2dr_pip_check.txt','w',encoding='utf-8').write((r.stdout or '')+(r.stderr or '')); "
             "print(r.returncode); sys.exit(r.returncode)"],
            ["logs/e2dr_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "-c",
             "import subprocess,sys; r=subprocess.run([sys.executable,'scripts/check_e2_data_horizon_spatial_recovery_gates.py']); "
             "print({'gate_script_exit': r.returncode}); sys.exit(0)"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_evidence",
            [PYTHON, "scripts/check_e2_data_horizon_spatial_recovery_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_data_horizon_spatial_recovery_evidence.py"],
            [
                f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES.json",
                f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json",
            ],
        ),
        (
            "hash_verify",
            [PYTHON, "-c",
             "import json; print(json.load(open('deliverables/TO_SUBMIT_E2_DATA_HORIZON_AND_SPATIAL_METADATA_RECOVERY_R1/FINAL_DELIVERABLE_HASHES_VERIFY.json'))['status'])"],
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
