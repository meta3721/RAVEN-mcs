"""Prove which archives are redundant: exact-duplicate hashes, and archives fully mirrored by loose files."""
from __future__ import annotations

import hashlib
import os
import pathlib
import time
import zipfile
from collections import defaultdict

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
LIST = ROOT / "_r13_build/archives.txt"

archives = []
for line in LIST.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    size, rel = line.split("\t", 1)
    archives.append((int(size), rel))

t0 = time.time()
print(f"=== hashing {len(archives)} archives ({sum(a[0] for a in archives)/1e9:.2f} GB) ===")
digests = {}
for size, rel in archives:
    p = ROOT / rel
    h = hashlib.sha256()
    try:
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        digests[rel] = (h.hexdigest(), size)
    except OSError as exc:
        print(f"  unreadable: {rel} ({exc})")
print(f"  done in {time.time()-t0:.0f}s")

groups = defaultdict(list)
for rel, (d, s) in digests.items():
    groups[d].append((rel, s))

print("\n=== exact duplicate groups (same sha256) ===")
dup_waste = 0
dup_groups = 0
for d, members in sorted(groups.items(), key=lambda kv: -kv[1][0][1]):
    if len(members) < 2:
        continue
    dup_groups += 1
    members.sort(key=lambda m: (len(m[0]), m[0]))
    keep = members[0]
    waste = sum(m[1] for m in members[1:])
    dup_waste += waste
    print(f"\n  {members[0][1]/1e6:.1f} MB x {len(members)} copies   (冗余 {waste/1e6:.1f} MB)")
    for rel, s in members:
        mark = "KEEP" if rel == keep[0] else "dup "
        print(f"    [{mark}] {rel}")
print(f"\n  duplicate groups: {dup_groups}, recoverable: {dup_waste/1e6:.1f} MB")

print("\n=== archives that unpack to a directory already on disk (self-nesting) ===")
for size, rel in archives:
    p = ROOT / rel
    if p.suffix.lower() != ".zip":
        continue
    stem = p.stem
    sib = p.with_suffix("")
    if not sib.is_dir():
        continue
    try:
        with zipfile.ZipFile(p) as zf:
            members = [(i.filename, i.file_size, i.is_dir()) for i in zf.infolist()]
    except Exception as exc:  # noqa: BLE001
        print(f"  cannot read {rel}: {exc}")
        continue
    files = [(n, s) for n, s, isd in members if not isd]
    if not files:
        continue
    loose = {}
    for dp, _, fns in os.walk(sib):
        for fn in fns:
            fp = pathlib.Path(dp) / fn
            try:
                loose[str(fp.relative_to(p.parent)).replace("\\", "/")] = fp.stat().st_size
            except OSError:
                pass
    hit = 0
    for name, msize in files:
        key = f"{stem}/{name}"
        if loose.get(key) == msize or loose.get(name) == msize:
            hit += 1
    pct = 100 * hit / len(files)
    print(f"  {size/1e6:>8.1f} MB  {rel}")
    print(f"            members={len(files)}  matched loose (name+size)={hit} ({pct:.0f}%)  "
          f"dir exists=yes")
