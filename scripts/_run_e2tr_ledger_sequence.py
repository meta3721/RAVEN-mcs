#!/usr/bin/env python3
"""Ledger sequence for E2 traffic mapping and readiness closure."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_TRAFFIC_MAPPING_AND_READINESS_CLOSURE_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2tr_{label}.stdout.log",
        "--stderr-log", f"logs/e2tr_{label}.stderr.log",
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

    prepared = (ROOT / "outputs/traffic_mapping/E2_TRAFFIC_STOP_STATUS.json").is_file()
    steps: list[tuple[str, list[str], list[str]]] = []
    if prepared:
        steps.append((
            "atomic_table_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/traffic_mapping/E2_TRAFFIC_ATOMIC_TABLE_IDENTITY.json'))['row_count'])"],
            ["outputs/traffic_mapping/E2_TRAFFIC_ATOMIC_TABLE_IDENTITY.json"],
        ))
    else:
        steps.append((
            "atomic_table_audit",
            [PYTHON, "scripts/prepare_e2_traffic_mapping_and_readiness.py"],
            [
                "outputs/traffic_mapping/E2_TRAFFIC_ATOMIC_TABLE_IDENTITY.json",
                "outputs/traffic_mapping/E2_TRAFFIC_STOP_STATUS.json",
            ],
        ))

    steps.extend((
        (
            "dense_matrix_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/traffic_mapping/E2_TRAFFIC_DENSE_MATRIX_AUDIT.json'))['status'])"],
            ["outputs/traffic_mapping/E2_TRAFFIC_DENSE_MATRIX_AUDIT.json"],
        ),
        (
            "global_window_construction",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json"],
        ),
        (
            "atomic_unique_assignment",
            [PYTHON, "-c",
             "import json; a=json.load(open('outputs/audits/E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json')); "
             "print(a['selected_atomic_count'], a['cross_window_duplicate_count'])"],
            ["configs/frozen/e2_traffic/atomic_window_assignment.parquet"],
        ),
        (
            "reference_geometry_parse",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/traffic_mapping/E2_TRAFFIC_REFERENCE_PARSE_AUDIT.json'))['status'])"],
            ["outputs/traffic_mapping/E2_TRAFFIC_REFERENCE_PARSE_AUDIT.json"],
        ),
        (
            "station_mapping",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_SPATIAL_METADATA_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_SPATIAL_METADATA_AUDIT.json"],
        ),
        (
            "target_field_selection",
            [PYTHON, "-c",
             "import json; print(json.load(open('configs/frozen/e2_traffic/target_field_identity.json'))['target_field'])"],
            ["configs/frozen/e2_traffic/target_field_identity.json"],
        ),
        (
            "theory_mapping",
            [PYTHON, "-c",
             "import json; print(json.load(open('configs/frozen/e2_traffic/traffic_theory_mapping_identity.json'))['status'])"],
            ["configs/frozen/e2_traffic/traffic_theory_mapping_identity.json"],
        ),
        (
            "two_stage_feature_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_TWO_STAGE_MAPPING_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_TWO_STAGE_MAPPING_AUDIT.json"],
        ),
        (
            "theory_compatibility_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_THEORY_COMPATIBILITY_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_THEORY_COMPATIBILITY_AUDIT.json"],
        ),
        (
            "mapping_canary_27901",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/e2_traffic_canary/E2_TRAFFIC_MAPPING_CANARY_GATE.json'))['status'])"],
            ["outputs/e2_traffic_canary/E2_TRAFFIC_MAPPING_CANARY_GATE.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_traffic_mapping_readiness_core.py",
             "--junitxml=logs/e2_traffic_mapping_readiness_unit.xml"],
            ["logs/e2_traffic_mapping_readiness_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_traffic_mapping_readiness_stop.py",
             "--junitxml=logs/e2_traffic_mapping_readiness_integration.xml"],
            ["logs/e2_traffic_mapping_readiness_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_traffic_mapping_readiness_full_repository.xml"],
            ["logs/e2_traffic_mapping_readiness_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-c",
             "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
             "open('logs/e2tr_pip_check.txt','w',encoding='utf-8').write((r.stdout or '')+(r.stderr or '')); "
             "print(r.returncode); sys.exit(r.returncode)"],
            ["logs/e2tr_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_traffic_mapping_readiness_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_evidence",
            [PYTHON, "scripts/check_e2_traffic_mapping_readiness_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_traffic_mapping_readiness_evidence.py"],
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
