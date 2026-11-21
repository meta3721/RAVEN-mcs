#!/usr/bin/env python3
"""Ledger sequence for E2 traffic public-target and q-feature seal."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
PACKAGE = "E2_TRAFFIC_PUBLIC_TARGET_AND_Q_FEATURE_SEAL_R1"
LEDGER = f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def run(label: str, command: list[str], outputs: list[str]) -> int:
    wrapped = [
        PYTHON, "scripts/run_and_log.py", "--ledger", LEDGER, "--label", label,
        "--stdout-log", f"logs/e2pt_{label}.stdout.log",
        "--stderr-log", f"logs/e2pt_{label}.stderr.log",
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

    prepared = (
        ROOT / "outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json"
    ).is_file()
    steps: list[tuple[str, list[str], list[str]]] = []
    if prepared:
        steps.append((
            "public_target_generation",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'configs/frozen/e2_traffic_public_target/atomic_public_target_identity.json'))['atomic_unit_count'])"],
            ["configs/frozen/e2_traffic_public_target/atomic_public_target_identity.json"],
        ))
    else:
        steps.append((
            "public_target_generation",
            [PYTHON, "scripts/prepare_e2_traffic_public_target_and_qseal.py"],
            [
                "configs/frozen/e2_traffic_public_target/atomic_public_target_identity.json",
                "outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json",
            ],
        ))

    steps.extend((
        (
            "group_mass_generation",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_GROUP_TARGET_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_GROUP_TARGET_AUDIT.json"],
        ),
        (
            "label_free_region_generation",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json"],
        ),
        (
            "stratum_mapping",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'configs/frozen/e2_traffic_public_target/public_target_identity.json'))['stratum_count'])"],
            ["configs/frozen/e2_traffic_public_target/opportunity_stratum_target.parquet"],
        ),
        (
            "lambda_pi_target_generation",
            [PYTHON, "-c",
             "import json; a=json.load(open('configs/frozen/e2_traffic_public_target/public_target_identity.json')); "
             "print(a['Lambda_sum'], a['pi_sum'])"],
            ["configs/frozen/e2_traffic_public_target/client_stratum_target.parquet"],
        ),
        (
            "q_feature_sealing",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_Q_FEATURE_AUDIT.json'))['status'])"],
            ["configs/frozen/e2_traffic_public_target/q_feature_manifest.json"],
        ),
        (
            "leakage_scan",
            [PYTHON, "-c",
             "import json; print(json.load(open('outputs/audits/E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json"],
        ),
        (
            "theory_compatibility_audit",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.json'))['status'])"],
            ["outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.json"],
        ),
        (
            "mapping_canary_27901",
            [PYTHON, "-c",
             "import json; print(json.load(open("
             "'outputs/e2_traffic_public_target_canary/E2_TRAFFIC_PUBLIC_TARGET_CANARY_GATE.json'))['status'])"],
            ["outputs/e2_traffic_public_target_canary/E2_TRAFFIC_PUBLIC_TARGET_CANARY_GATE.json"],
        ),
        (
            "unit_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/unit/test_e2_traffic_public_target_qseal_core.py",
             "--junitxml=logs/e2_traffic_public_target_qseal_unit.xml"],
            ["logs/e2_traffic_public_target_qseal_unit.xml"],
        ),
        (
            "integration_tests",
            [PYTHON, "-m", "pytest", "-q",
             "tests/integration/test_e2_traffic_public_target_qseal_stop.py",
             "--junitxml=logs/e2_traffic_public_target_qseal_integration.xml"],
            ["logs/e2_traffic_public_target_qseal_integration.xml"],
        ),
        (
            "full_repository_tests",
            [PYTHON, "-m", "pytest", "-q",
             "--junitxml=logs/e2_traffic_public_target_qseal_full_repository.xml"],
            ["logs/e2_traffic_public_target_qseal_full_repository.xml"],
        ),
        (
            "pip_check",
            [PYTHON, "-c",
             "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); "
             "open('logs/e2pt_pip_check.txt','w',encoding='utf-8').write((r.stdout or '')+(r.stderr or '')); "
             "print(r.returncode); sys.exit(r.returncode)"],
            ["logs/e2pt_pip_check.txt"],
        ),
        (
            "gates",
            [PYTHON, "scripts/check_e2_traffic_public_target_qseal_gates.py"],
            [f"outputs/gates/{PACKAGE}_GATES.json"],
        ),
        (
            "compact_evidence",
            [PYTHON, "scripts/check_e2_traffic_public_target_qseal_compact_evidence.py"],
            [f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"],
        ),
        (
            "export",
            [PYTHON, "scripts/export_e2_traffic_public_target_qseal_evidence.py"],
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
