"""Audit the 85 untracked entries under src/: expansion, sizes, and mtime clustering.

Read-only. Output: _r13_build/SRC_UNTRACKED_AUDIT.json
"""
from __future__ import annotations

import json
import pathlib
import subprocess
from collections import Counter, defaultdict

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True).stdout


porcelain = [ln for ln in git("status", "--porcelain", "--", "src").splitlines() if ln.startswith("??")]
entries = [ln[3:].strip() for ln in porcelain]

tracked = [ln for ln in git("ls-files", "src").splitlines() if ln.strip()]
head = git("rev-parse", "HEAD").strip()
head_date = git("log", "-1", "--format=%ci").strip()

per_entry = []
by_date = Counter()
by_month = Counter()
total_files = 0
total_bytes = 0
all_files = []

for rel in entries:
    p = ROOT / rel
    if p.is_dir():
        files = [f for f in p.rglob("*") if f.is_file()]
    elif p.is_file():
        files = [p]
    else:
        files = []
    size = sum(f.stat().st_size for f in files)
    mts = [f.stat().st_mtime for f in files] or [p.stat().st_mtime if p.exists() else 0]
    lo, hi = (min(mts), max(mts)) if mts else (0, 0)
    import datetime as _dt
    f = lambda t: _dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S") if t else None
    per_entry.append({"path": rel, "is_dir": p.is_dir(), "n_files": len(files),
                      "bytes": size, "first_mtime": f(lo), "last_mtime": f(hi)})
    total_files += len(files)
    total_bytes += size
    for fl in files:
        d = _dt.datetime.fromtimestamp(fl.stat().st_mtime)
        by_date[d.strftime("%Y-%m-%d")] += 1
        by_month[d.strftime("%Y-%m")] += 1
        all_files.append((fl.stat().st_mtime, str(fl.relative_to(ROOT)).replace("\\", "/")))

out = {
    "purpose": "audit of the untracked entries under src/ (why they are untracked)",
    "head_commit": head,
    "head_commit_date": head_date,
    "tracked_files_under_src": len(tracked),
    "untracked_entries_under_src": len(entries),
    "untracked_files_total": total_files,
    "untracked_bytes_total": total_bytes,
    "ignored_by_gitignore": False,
    "gitignore_evidence": "git check-ignore -v returns nothing for reuse_guard.py, real_runner/runner.py "
                          "or protocol_closure/__init__.py; .gitignore has no src/e3/protocol match; "
                          "core.excludesfile is unset",
    "files_by_month": dict(sorted(by_month.items())),
    "files_by_date": dict(sorted(by_date.items())),
    "per_entry": sorted(per_entry, key=lambda e: -e["n_files"]),
    "oldest_untracked_file": None,
    "newest_untracked_file": None,
}
if all_files:
    all_files.sort()
    out["oldest_untracked_file"] = {"mtime": all_files[0][1], "path": all_files[0][1], "ts": all_files[0][0]}
    out["oldest_untracked_file"] = {"path": all_files[0][1]}
    import datetime as _dt
    out["oldest_untracked_file"]["mtime"] = _dt.datetime.fromtimestamp(all_files[0][0]).isoformat()
    out["newest_untracked_file"] = {
        "path": all_files[-1][1],
        "mtime": _dt.datetime.fromtimestamp(all_files[-1][0]).isoformat(),
    }

p = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\SRC_UNTRACKED_AUDIT.json")
p.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

print("HEAD", head, head_date)
print("tracked under src:", len(tracked), "| untracked entries:", len(entries),
      "| untracked files:", total_files, f"({total_bytes/1e6:.1f} MB)")
print("files by month:", dict(sorted(by_month.items())))
print("files by date:")
for d, n in sorted(by_date.items()):
    print(f"   {d}  {n}")
print("top 12 entries by file count:")
for e in out["per_entry"][:12]:
    print(f"   {e['n_files']:>5} files {e['bytes']/1e6:>7.2f} MB  {e['first_mtime']} .. {e['last_mtime']}  {e['path']}")
print("wrote", p)
