"""Locate the artifact family that carries the paper's U-Air table row as a set."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
UA = ["1.1119", "1.2202", "1.1954", "1.1128", "1.1131"]
SS = ["7.9389", "7.9309", "7.9364", "7.9293", "7.9380"]

hits = {"uair": [], "sensorscope": []}
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in {".json", ".csv", ".md", ".txt"}:
        continue
    s = str(p)
    if "\\runs\\" in s or "node_modules" in s or "\\.git" in s or "\\_r13_build\\" in s:
        continue
    try:
        if p.stat().st_size > 8_000_000:
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        continue
    for name, vals in (("uair", UA), ("sensorscope", SS)):
        n = sum(1 for v in vals if v in t)
        if n >= 3:
            hits[name].append((n, p.relative_to(ROOT).as_posix()))

for name in ("uair", "sensorscope"):
    print(f"=== files carrying >=3 of the paper's {name} table values ===")
    for n, rel in sorted(hits[name], reverse=True)[:8]:
        print(f"  {n}/{len(UA if name == 'uair' else SS)}  {rel}")
    if not hits[name]:
        print("  none")
    print()
