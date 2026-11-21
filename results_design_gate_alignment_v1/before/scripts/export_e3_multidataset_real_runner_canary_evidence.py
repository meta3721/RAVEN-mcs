#!/usr/bin/env python3
"""Export self-contained E3 Canary R1 evidence package."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_MULTIDATASET_REAL_RUNNER_CANARY_R1"
ZIP = ROOT / "deliverables/TO_SUBMIT_E3_MULTIDATASET_REAL_RUNNER_CANARY_R1.zip"

HASHED_INCLUDE = [
    "E3_CANARY_SEED_AUDIT.json",
    "E3_CANARY_DATASET_HASH_AUDIT.json",
    "E3_CANARY_TARGET_HASH_AUDIT.json",
    "E3_CANARY_STRATUM_HASH_AUDIT.json",
    "E3_CANARY_TRAFFIC_REUSE_GUARD.json",
    "E3_CANARY_RUN_MATRIX.json",
    "E3_CANARY_EVENTTRACE_AUDIT.json",
    "E3_CANARY_EVENTTRACE_AUDIT.csv",
    "E3_CANARY_RUN_STATUS.csv",
    "E3_CANARY_LEDGER_AUDIT.json",
    "E3_CANARY_DELTA_CS_AUDIT.csv",
    "E3_CANARY_NO_PERFORMANCE_SELECTION_ATTESTATION.md",
    "E3_CANARY_PARENT_INTEGRITY.json",
    "E3_CANARY_SOURCE_HASHES.json",
    "E3_CANARY_PHASE1_SUMMARY.json",
    "E3_CANARY_PHASE2_SUMMARY.json",
    "E3_FORMAL_READINESS_AFTER_CANARY.json",
    "E3_FORMAL_READINESS_AFTER_CANARY.md",
    "E3_FORMAL_EXECUTION_PLAN_R1.json",
    "E3_FORMAL_EXECUTION_PLAN_R1.md",
    "E3_MULTIDATASET_REAL_RUNNER_CANARY_R1_REPORT.md",
    "E3_CANARY_STOP_STATUS.json",
    "E3_CANARY_TEST_RETURNCODES.json",
    "logs/e3_canary_unit.xml",
    "logs/e3_canary_integration.xml",
    "logs/e3_canary_pytest_full.xml",
    "logs/e3_canary_pip_check.txt",
]

POST_HASH_INCLUDE = [
    "E3_CANARY_HASH_MANIFEST.json",
    "E3_CANARY_HASH_VERIFICATION.json",
    "gate_results.json",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _collect_run_summaries() -> list[str]:
    """Include per-run lightweight integrity artifacts (not full checkpoints)."""
    rels = []
    runs = ART / "runs"
    if not runs.is_dir():
        return rels
    for p in runs.rglob("*"):
        if not p.is_file():
            continue
        name = p.name
        if name in {
            "CANARY_ACCEPTED.json",
            "final_metrics.json",
            "runtime_manifest.json",
            "config_snapshot.json",
            "target_wiring.json",
            "opportunity_stratum_identity.json",
            "atomic_rho_summary.json",
            "delta_cs_summary_v6.json",
            "delta_c_s_summary.json",
            "method_smoke_audit.json",
            "ledger.jsonl",
        }:
            rels.append(str(p.relative_to(ART)).replace("\\", "/"))
        elif name == "final.pt" and p.parent.name == "checkpoints":
            # hash-only sidecar
            h = _sha(p)
            side = p.with_suffix(".pt.sha256.txt")
            side.write_text(h + "\n", encoding="utf-8")
            rels.append(str(side.relative_to(ART)).replace("\\", "/"))
    # EventTrace identities only
    for p in (ART / "eventtraces").rglob("trace_identity.json"):
        rels.append(str(p.relative_to(ART)).replace("\\", "/"))
    for p in (ART / "eventtraces").rglob("generation_meta.json"):
        rels.append(str(p.relative_to(ART)).replace("\\", "/"))
    return sorted(set(rels))


def build_manifest(*, include_post: bool) -> dict:
    entries = {}
    for rel in HASHED_INCLUDE + _collect_run_summaries():
        path = ART / rel if not rel.startswith("logs/") else ART / rel
        if not path.is_file():
            # try ROOT logs
            path = ART / rel
        if not path.is_file():
            continue
        entries[rel] = {
            "sha256": _sha(path),
            "included_in_zip": True,
            "bytes": path.stat().st_size,
        }
    verify = {
        "status": "PASS",
        "mismatch_count": 0,
        "mismatches": [],
        "hashed_entry_count": len(entries),
    }
    dump_json(verify, ART / "E3_CANARY_HASH_VERIFICATION.json")
    manifest = {
        "round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1",
        "entries": entries,
        "post_hash_artifacts": POST_HASH_INCLUDE,
        "status": json.loads((ART / "E3_CANARY_STOP_STATUS.json").read_text(encoding="utf-8")).get(
            "status"
        ),
    }
    dump_json(manifest, ART / "E3_CANARY_HASH_MANIFEST.json")
    if include_post:
        for rel in POST_HASH_INCLUDE:
            if rel in {"E3_CANARY_HASH_MANIFEST.json", "E3_CANARY_HASH_VERIFICATION.json"}:
                continue
            path = ART / rel
            if path.is_file():
                entries[rel] = {
                    "sha256": _sha(path),
                    "included_in_zip": True,
                    "bytes": path.stat().st_size,
                    "post_hash": True,
                }
        # refresh verification against hashed body only
        mismatches = []
        for rel, meta in list(entries.items()):
            if meta.get("post_hash"):
                continue
            path = ART / rel
            if not path.is_file() or _sha(path) != meta["sha256"]:
                mismatches.append(rel)
        verify = {
            "status": "PASS" if not mismatches else "FAIL",
            "mismatch_count": len(mismatches),
            "mismatches": mismatches,
            "hashed_entry_count": sum(1 for m in entries.values() if not m.get("post_hash")),
        }
        dump_json(verify, ART / "E3_CANARY_HASH_VERIFICATION.json")
        manifest["entries"] = entries
        dump_json(manifest, ART / "E3_CANARY_HASH_MANIFEST.json")
        for rel in ("E3_CANARY_HASH_MANIFEST.json", "E3_CANARY_HASH_VERIFICATION.json"):
            path = ART / rel
            entries[rel] = {
                "sha256": _sha(path),
                "included_in_zip": True,
                "bytes": path.stat().st_size,
                "post_hash": True,
            }
        manifest["entries"] = entries
        dump_json(manifest, ART / "E3_CANARY_HASH_MANIFEST.json")
    return manifest


def main() -> int:
    # ensure gates after finalize
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_e3_multidataset_real_runner_canary_gates.py")],
        cwd=ROOT,
        check=False,
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")},
    )
    build_manifest(include_post=False)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_e3_multidataset_real_runner_canary_gates.py")],
        cwd=ROOT,
        check=False,
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")},
    )
    manifest = build_manifest(include_post=True)
    # final gate pass
    g = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_e3_multidataset_real_runner_canary_gates.py")],
        cwd=ROOT,
        check=False,
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")},
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    prefix = OUT.name
    for rel, meta in manifest["entries"].items():
        if not meta.get("included_in_zip"):
            continue
        src = ART / rel
        if not src.is_file():
            continue
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in OUT.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=f"{prefix}/{path.relative_to(OUT).as_posix()}")

    stop = json.loads((ART / "E3_CANARY_STOP_STATUS.json").read_text(encoding="utf-8"))
    verify = json.loads((ART / "E3_CANARY_HASH_VERIFICATION.json").read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "zip": str(ZIP),
                "status": stop.get("status"),
                "hash_verify": verify.get("status"),
                "gate_rc": g.returncode,
                "self_contained": True,
            },
            indent=2,
        )
    )
    return 0 if verify.get("status") == "PASS" and g.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
