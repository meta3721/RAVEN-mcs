"""Record the exemption-recording nuance precisely, and verify the counts."""
from __future__ import annotations

import json
import pathlib

R = pathlib.Path(r"C:\Cursor\raven.mcs\results_traffic_e1\round_v1")
runs = R / "runs"
fed = sorted((runs / "C1_fedavg/traffic/fedavg_window").glob("seed*"))
sim = sorted((runs / "C1_simoracle/traffic/raven_simoracle").glob("seed*"))
fed_ex = [d.name for d in fed if (d / "REUSE_GUARD_EXEMPTION.json").is_file()]
sim_ex = [d.name for d in sim if (d / "REUSE_GUARD_EXEMPTION.json").is_file()]
one = json.loads((sim[0] / "REUSE_GUARD_EXEMPTION.json").read_text(encoding="utf-8")) if sim_ex else {}
print(f"fedavg runs {len(fed)}, exemption file in {len(fed_ex)}")
print(f"simoracle runs {len(sim)}, exemption file in {len(sim_ex)}")
print("sample record run field:", json.dumps(one.get("run")))
meta = json.loads((sim[0] / "SERVER_OPT_META.json").read_text(encoding="utf-8"))
print("simoracle SERVER_OPT_META.reuse_guard_exemption =", meta.get("reuse_guard_exemption"))

p = R / "TE1_REPORT.md"
t = p.read_text(encoding="utf-8")
assert "## Addendum" in t and "7. **The exemption record" not in t
t += f"""
7. **The exemption record is written per traffic run, not per refused arm.** The driver passes
   `allow_reused_traffic_rerun` for every `traffic` cell and therefore stamps
   `REUSE_GUARD_EXEMPTION.json` (and `reuse_guard_exemption: true` in `SERVER_OPT_META.json`) on
   {len(fed_ex)}/{len(fed)} `fedavg_window` confirm runs **and** on {len(sim_ex)}/{len(sim)} `raven_simoracle`
   confirm runs. Only the `fedavg_window` arm is on the sealed list `E2_TRAFFIC_REUSED_METHODS`
   (`fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `twostage_hajek`, `raven`); the
   `raven_simoracle` arm is not, so the guard would have scheduled it with no opt-in at all. The record
   is faithful to what the caller passed, but it does not by itself imply that the guard refused a cell.
"""
p.write_text(t, encoding="utf-8")
print("\nrecorded; report now", len(t.splitlines()), "lines,", len(t.encode()), "B")
