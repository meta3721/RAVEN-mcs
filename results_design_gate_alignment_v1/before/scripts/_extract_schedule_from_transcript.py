#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

p = Path(
    r"C:\Users\szr\.cursor\projects\d-Cursor-raven-mcs\agent-transcripts"
    r"\6d24fcc5-d896-4d48-968b-739474490c73\6d24fcc5-d896-4d48-968b-739474490c73.jsonl"
)
out_dir = Path("outputs/_tmp_schedule_extract")
out_dir.mkdir(parents=True, exist_ok=True)

n = 0
for i, line in enumerate(p.open(encoding="utf-8"), 1):
    if "schedule.py" not in line or "Write" not in line:
        continue
    try:
        obj = json.loads(line)
    except Exception:
        continue
    for c in obj.get("message", {}).get("content", []):
        if c.get("type") != "tool_use" or c.get("name") != "Write":
            continue
        inp = c.get("input", {})
        path = str(inp.get("path", ""))
        contents = inp.get("contents")
        if "schedule.py" not in path or not contents:
            continue
        n += 1
        has_role = any(
            k in contents
            for k in ("head_tail", "role_map", "head_heavy", "by_role", "quotas")
        )
        cand = "?"
        for tok in contents.splitlines():
            if tok.startswith("CANDIDATE_SIZE"):
                cand = tok.strip()
                break
        dest = out_dir / f"schedule_L{i}_{n}.py"
        dest.write_text(contents, encoding="utf-8")
        print(f"saved {dest.name} line={i} roleish={has_role} {cand} bytes={len(contents)}")

print("total", n)
