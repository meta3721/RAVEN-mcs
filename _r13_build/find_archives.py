"""Find every archive in the workspace, with size and location."""
from __future__ import annotations

import os
import time
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
SUFFIXES = {".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".xz", ".bz2", ".zst", ".cab", ".jar", ".whl"}
SKIP = {".git", ".venv_new", "node_modules", "__pycache__", ".dsh"}

found = []
t0 = time.time()
stack = [str(ROOT)]
while stack:
    cur = stack.pop()
    try:
        it = os.scandir(cur)
    except OSError:
        continue
    with it:
        for e in it:
            try:
                if e.is_dir(follow_symlinks=False):
                    if e.name in SKIP:
                        continue
                    stack.append(e.path)
                    continue
                st = e.stat(follow_symlinks=False)
            except OSError:
                continue
            suf = os.path.splitext(e.name)[1].lower()
            if suf in SUFFIXES or e.name.lower().endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
                found.append((st.st_size, os.path.relpath(e.path, ROOT), st.st_mtime))

found.sort(reverse=True)
total = sum(f[0] for f in found)
print(f"=== {len(found)} archives, {total/1e9:.2f} GB total ({time.time()-t0:.0f}s) ===")
print(f"  {'size':>10}  {'date':10}  path")
for size, rel, mt in found[:40]:
    print(f"  {size/1e6:>8.1f}MB  {time.strftime('%Y-%m-%d', time.localtime(mt))}  {rel}")
if len(found) > 40:
    print(f"  ... and {len(found)-40} smaller ones")

out = ROOT / "_r13_build/archives.txt"
out.write_text("\n".join(f"{s}\t{r}" for s, r, _ in found), encoding="utf-8")
print(f"\n  full list -> {out}")
by_dir: dict[str, int] = {}
for s, r, _ in found:
    by_dir[r.split(os.sep)[0]] = by_dir.get(r.split(os.sep)[0], 0) + s
print("\n  by top-level dir:")
for k, v in sorted(by_dir.items(), key=lambda kv: -kv[1])[:12]:
    print(f"    {v/1e6:>9.1f}MB  {k}")
