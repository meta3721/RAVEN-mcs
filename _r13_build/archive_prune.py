"""Verify archive redundancy by content, then emit a deletion plan (dry-run unless --apply)."""
from __future__ import annotations

import hashlib
import os
import pathlib
import sys
import time
import zipfile
from collections import defaultdict

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
APPLY = "--apply" in sys.argv

# ---------- helpers ----------
def sha_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# ---------- A: exact duplicate copies ----------
archives = []
for line in (ROOT / "_r13_build/archives.txt").read_text(encoding="utf-8").splitlines():
    if line.strip():
        s, r = line.split("\t", 1)
        archives.append((int(s), r))

groups = defaultdict(list)
for size, rel in archives:
    try:
        groups[sha_file(ROOT / rel)].append((size, rel))
    except OSError:
        pass

dup_victims = []
for d, members in groups.items():
    if len(members) < 2:
        continue
    members.sort(key=lambda m: (m[1].count(os.sep), len(m[1]), m[1]))
    for size, rel in members[1:]:
        dup_victims.append((size, rel, members[0][1]))
print(f"=== A: exact duplicate copies: {len(dup_victims)} to remove, "
      f"{sum(v[0] for v in dup_victims)/1e6:.1f} MB ===")

# ---------- B: outer zips fully contained in their sibling directory ----------
print("\n=== B: verifying outer zips against their unpacked sibling (byte level) ===")
nested_victims = []
for size, rel in sorted(archives, reverse=True):
    p = ROOT / rel
    if p.suffix.lower() != ".zip":
        continue
    sib = p.with_suffix("")
    if not sib.is_dir():
        continue
    try:
        with zipfile.ZipFile(p) as zf:
            files = [i for i in zf.infolist() if not i.is_dir()]
            if not files or len(files) > 12000:      # skip enormous listings for time
                status = f"skipped (members={len(files)})"
                print(f"  {size/1e6:>8.1f} MB  {rel}\n            {status}")
                continue
            ok = 0
            for i in files:
                # zip members are usually stored relative to the parent of the stem dir,
                # i.e. their name already includes the top folder; try both forms.
                cands = [p.parent / i.filename, sib / i.filename]
                target = next((c for c in cands if c.is_file()), None)
                if target is None or target.stat().st_size != i.file_size:
                    continue
                if sha_file(target) == hashlib.sha256(zf.read(i)).hexdigest():
                    ok += 1
            pct = 100 * ok / len(files)
    except Exception as exc:  # noqa: BLE001
        print(f"  {size/1e6:>8.1f} MB  {rel}\n            ERROR {exc}")
        continue
    verdict = "FULLY COVERED" if ok == len(files) else f"partial {ok}/{len(files)}"
    print(f"  {size/1e6:>8.1f} MB  {rel}\n            {verdict} ({pct:.0f}%)")
    if ok == len(files):
        nested_victims.append((size, rel))

# ---------- plan ----------
total = sum(v[0] for v in dup_victims) + sum(v[0] for v in nested_victims)
print(f"\n=== PLAN: {len(dup_victims)} duplicate copies + {len(nested_victims)} fully covered outer zips "
      f"= {total/1e6:.1f} MB ===")
for size, rel, keep in dup_victims:
    print(f"  DEL  {size/1e6:>8.1f} MB  {rel}\n             (identical to {keep})")
for size, rel in nested_victims:
    print(f"  DEL  {size/1e6:>8.1f} MB  {rel}\n             (every member byte-identical to "
          f"{pathlib.Path(rel).with_suffix('')}/)")

if not APPLY:
    print("\n  dry run only - pass --apply to delete")
    sys.exit(0)

print("\n=== deleting ===")
freed = 0
failed = []
for size, rel, _ in dup_victims:
    try:
        (ROOT / rel).unlink()
        freed += size
        print(f"  removed  {rel}")
    except OSError as exc:
        failed.append((rel, str(exc)))
for size, rel in nested_victims:
    try:
        (ROOT / rel).unlink()
        freed += size
        print(f"  removed  {rel}")
    except OSError as exc:
        failed.append((rel, str(exc)))
print(f"\n  freed {freed/1e6:.1f} MB; {len(failed)} failures")
for rel, err in failed:
    print(f"    FAILED {rel}: {err}")
