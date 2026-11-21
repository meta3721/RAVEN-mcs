"""One-pass workspace inventory: depth-1 and depth-2 sizes, written to CSV + a compact table."""
from __future__ import annotations

import csv
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
SKIP_NAMES = {"node_modules", ".git", "__pycache__", ".venv_new", ".venv"}

t0 = time.time()
agg: dict[str, list] = {}          # key: rel path with 1 or 2 parts
mtimes: dict[str, float] = {}
errors = 0


def add(key: str, size: int) -> None:
    v = agg.get(key)
    if v is None:
        agg[key] = [1, size]
    else:
        v[0] += 1
        v[1] += size


stack = [str(ROOT)]
while stack:
    cur = stack.pop()
    try:
        it = os.scandir(cur)
    except OSError:
        errors += 1
        continue
    with it:
        for e in it:
            try:
                if e.is_dir(follow_symlinks=False):
                    if e.name in SKIP_NAMES:
                        continue
                    stack.append(e.path)
                    continue
                st = e.stat(follow_symlinks=False)
            except OSError:
                errors += 1
                continue
            rel = os.path.relpath(e.path, ROOT)
            parts = rel.split(os.sep)
            add(parts[0], st.st_size)
            if len(parts) > 1:
                add(parts[0] + "/" + parts[1], st.st_size)
            if len(parts) == 1:
                mtimes[parts[0]] = max(mtimes.get(parts[0], 0), st.st_mtime)

top = {k: v for k, v in agg.items() if "/" not in k}
# directory mtimes come from their own listing
for name in top:
    p = ROOT / name
    try:
        mtimes[name] = p.stat().st_mtime
    except OSError:
        pass

ordered = sorted(top.items(), key=lambda kv: -kv[1][1])
print(f"=== depth-1 ({len(ordered)} entries, {time.time()-t0:.0f}s, {errors} unreadable) ===")
print(f"  {'name':<38}{'files':>8}{'size':>12}  last write")
for name, (n, b) in ordered:
    mt = time.strftime("%Y-%m-%d", time.localtime(mtimes.get(name, 0))) if mtimes.get(name) else "?"
    print(f"  {name:<38}{n:>8}{b/1e9:>10.2f}GB  {mt}")

print("\n=== depth-2 under the largest 10 entries ===")
for name, (n, b) in ordered[:10]:
    kids = sorted(((k, v) for k, v in agg.items()
                   if k.startswith(name + "/") and k.count("/") == 1),
                  key=lambda kv: -kv[1][1])
    print(f"  {name}  ({n} files, {b/1e9:.2f} GB, {len(kids)} children)")
    for k, (kn, kb) in kids[:12]:
        print(f"      {k.split('/', 1)[1]:<44}{kn:>7}{kb/1e9:>10.3f}GB")
    if len(kids) > 12:
        print(f"      ... and {len(kids)-12} more")

out = ROOT / "_r13_build/workspace_inventory.csv"
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["path", "depth", "files", "bytes", "GB"])
    for k, (n, b) in sorted(agg.items(), key=lambda kv: (-kv[1][1])):
        w.writerow([k, k.count("/") + 1, n, b, round(b / 1e9, 4)])
print(f"\n  wrote {out}  ({out.stat().st_size} B, {len(agg)} rows)")
