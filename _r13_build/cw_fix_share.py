"""Patch the frozen-rung share 0.2500 -> 0.2558 in both insertion-text copies, then rewrite W4."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
for name in ("cw_one.py", "cw_apply.py"):
    p = ROOT / "_r13_build" / name
    raw = p.read_bytes()
    n = raw.count(b"$0.2500$,")
    print(f"  {name}: {n} occurrence(s) of $0.2500$,")
    if n:
        raw = raw.replace(b"$0.2500$,", b"$0.2558$,")
        p.write_bytes(raw)
    print(f"    now has $0.2558$: {raw.count(b'$0.2558$')}, stale $0.2500$: {raw.count(b'0.2500')}")
