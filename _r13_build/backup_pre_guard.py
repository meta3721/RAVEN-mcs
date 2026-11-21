"""Pre-change backup before any guard modification.

Copies every file a guard change would touch, writes a sha256 manifest, and records hashes of the
sealed traffic evidence (hashes only, not copies) so that later we can prove it was untouched.
Nothing is modified or deleted.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
from datetime import datetime, timezone

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
DEST = ROOT / "results_server_optimizer" / "round_v1" / "backup_pre_guard_change"
SRC_TOUCHED = [
    ROOT / "src/raven_mcs/e3/protocol_closure",
    ROOT / "src/raven_mcs/e3/real_runner/runner.py",
]
EVIDENCE_DIRS = [
    ROOT / "artifacts/e2_traffic_formal_runs_r1/runs",
    ROOT / "artifacts/e3_formal_runs_r1/runs/traffic",
    ROOT / "results_new_block_traffic/round_v1",
]


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


DEST.mkdir(parents=True, exist_ok=True)
manifest = {"created_utc": datetime.now(timezone.utc).isoformat(),
            "purpose": "backup of every file a reuse-guard change would touch, taken before the change",
            "copied_files": [], "evidence_hashes": {}}

for src in SRC_TOUCHED:
    if src.is_dir():
        files = [f for f in src.rglob("*") if f.is_file()]
    elif src.is_file():
        files = [src]
    else:
        files = []
    for f in files:
        rel = f.relative_to(ROOT)
        dst = DEST / "src" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        manifest["copied_files"].append({
            "source": str(rel).replace("\\", "/"),
            "backup": str(dst.relative_to(ROOT)).replace("\\", "/"),
            "bytes": f.stat().st_size,
            "sha256": sha256_file(f),
            "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })

# hash-only record of the sealed traffic evidence (not copied)
for d in EVIDENCE_DIRS:
    if not d.is_dir():
        continue
    entries = {}
    for f in sorted(x for x in d.rglob("*") if x.is_file()):
        entries[str(f.relative_to(ROOT)).replace("\\", "/")] = sha256_file(f)
    manifest["evidence_hashes"][str(d.relative_to(ROOT)).replace("\\", "/")] = {
        "n_files": len(entries), "sha256": entries}

(DEST / "BACKUP_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

print("backup dir:", DEST)
print("copied files:", len(manifest["copied_files"]))
for c in manifest["copied_files"]:
    print(f"   {c['bytes']:>7} B  {c['sha256'][:16]}  {c['source']}")
print()
print("evidence hashed (not copied):")
for k, v in manifest["evidence_hashes"].items():
    print(f"   {v['n_files']:>5} files  {k}")
print()
print("wrote", DEST / "BACKUP_MANIFEST.json")
