#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
m = json.loads((ROOT / "outputs/e2_stage2_stratum/E2_TRACE_MATRIX_SUMMARY.json").read_text(encoding="utf-8"))
s = json.loads((ROOT / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json").read_text(encoding="utf-8"))
assert int(m["trace_count"]) == 180
assert int(m["trace_failure_count"]) == 0
assert s["status"] == "SELECTED"
print("ok", s["selected_profile_id"], s.get("selected_metrics"))
