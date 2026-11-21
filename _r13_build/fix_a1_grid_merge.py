"""Repair defect A1: the test-seal merge key omitted eta_s, copying the selected-eta test value into
all three eta rows of STAGE_A_GRID.csv."""
from __future__ import annotations

import csv
import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
DRIVER = OUT / "driver" / "s1p_driver.py"

# 1. fix the driver so it cannot recur
t = DRIVER.read_text(encoding="utf-8")
OLD = '            m = [t for t in test_rows if t["block"] == r["block"] and t["seed"] == r["seed"]]'
NEW = ('            m = [t for t in test_rows if t["block"] == r["block"] and t["seed"] == r["seed"]\n'
       '                 and t["eta_s"] == r["eta_s"]]')
assert t.count(OLD) == 1, "merge anchor"
DRIVER.write_text(t.replace(OLD, NEW), encoding="utf-8")
print("driver merge key now includes eta_s")

# 2. repair the delivered table: keep test columns only on the frozen (selected) eta row
cfg = json.loads((OUT / "S1P_FROZEN_CONFIG.json").read_text(encoding="utf-8"))
star = {b: cfg["per_block"][b].get("eta_s_star") for b in ("sensorscope", "uair", "traffic")}
p = OUT / "tables" / "STAGE_A_GRID.csv"
rows = list(csv.DictReader(p.open(encoding="utf-8")))
fields = list(rows[0].keys())
test_cols = [c for c in fields if c.startswith("test_")]
blanked = 0
for r in rows:
    if r["eta_s"] != star.get(r["block"]):
        for c in test_cols:
            if r[c] not in ("", None):
                blanked += 1
            r[c] = ""
with p.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"blanked {blanked} copied test values outside the frozen eta row")

# 3. verify against the run directories
print("\n=== verification: CSV test_RMSE_mu vs run dir final_metrics.json (selected eta only) ===")
bad = 0
for r in rows:
    if r["eta_s"] != star.get(r["block"]):
        assert r["test_RMSE_mu"] == "", "non-selected eta row still carries a test value"
        continue
    d = ROOT / r["run_dir"] / "final_metrics.json"
    if not d.is_file():
        print("  missing", d)
        bad += 1
        continue
    want = float(json.loads(d.read_text(encoding="utf-8"))["RMSE_mu"])
    got = float(r["test_RMSE_mu"])
    if abs(want - got) > 0:
        print(f"  MISMATCH {r['block']} {r['eta_s']} seed{r['seed']}: csv={got} dir={want}")
        bad += 1
print(f"  mismatches: {bad}")
kept = sum(1 for r in rows if r["test_RMSE_mu"] != "")
print(f"  rows: {len(rows)} | rows carrying a test value: {kept} (expected 15 = 3 blocks x 5 seeds)")
print("\n  selected-eta test means now:")
for b in ("sensorscope", "uair", "traffic"):
    v = [float(r["test_RMSE_mu"]) for r in rows if r["block"] == b and r["test_RMSE_mu"] != ""]
    print(f"    {b:<12} eta_s*={star[b]:<6} n={len(v)} mean={sum(v)/len(v) if v else None}")
print("\n  non-selected eta rows now show (no test column used for selection):")
for b in ("sensorscope", "uair", "traffic"):
    v = sorted({r["eta_s"] for r in rows if r["block"] == b and r["test_RMSE_mu"] == ""})
    print(f"    {b:<12} blanked eta levels: {v}")
