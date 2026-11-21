"""Corrected A1 repair: rebuild the test columns from the run directories for the frozen eta only."""
from __future__ import annotations

import csv
import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
cfg = json.loads((OUT / "S1P_FROZEN_CONFIG.json").read_text(encoding="utf-8"))
star_str = {b: str(cfg["per_block"][b].get("eta_s_star")) for b in ("sensorscope", "uair", "traffic")}
print("frozen eta_s_star (as string):", star_str)

p = OUT / "tables" / "STAGE_A_GRID.csv"
rows = list(csv.DictReader(p.open(encoding="utf-8")))
fields = list(rows[0].keys())
test_cols = [c for c in fields if c.startswith("test_")]

restored = blanked = 0
for r in rows:
    if str(r["eta_s"]) == star_str.get(r["block"]):
        fm = ROOT / r["run_dir"] / "final_metrics.json"
        m = json.loads(fm.read_text(encoding="utf-8"))
        r["test_RMSE_mu"] = m.get("RMSE_mu")
        r["test_Delta_group"] = m.get("Delta_group")
        r["test_Delta_c_s"] = m.get("Delta_c_S")
        r["test_Tail_RMSE"] = m.get("Tail_RMSE")
        restored += 1
    else:
        for c in test_cols:
            r[c] = ""
        blanked += 1

with p.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"rows restored from run dirs: {restored} | rows blanked: {blanked}")

# verify every restored value against its run directory, and confirm no non-selected row carries one
bad = 0
for r in rows:
    if str(r["eta_s"]) != star_str.get(r["block"]):
        if any(r[c] for c in test_cols):
            print("  LEAK non-selected row:", r["block"], r["eta_s"], r["seed"])
            bad += 1
        continue
    m = json.loads((ROOT / r["run_dir"] / "final_metrics.json").read_text(encoding="utf-8"))
    if float(r["test_RMSE_mu"]) != float(m["RMSE_mu"]):
        print("  MISMATCH", r["block"], r["eta_s"], r["seed"])
        bad += 1
print("mismatches/leaks:", bad)
for b in ("sensorscope", "uair", "traffic"):
    v = [float(r["test_RMSE_mu"]) for r in rows if r["block"] == b and r["test_RMSE_mu"] != ""]
    print(f"  {b:<12} eta_s*={star_str[b]:<6} n={len(v)} test mean={sum(v)/len(v) if v else None}")
print("\nsanity: other eta levels keep their validation-only columns:")
for b in ("sensorscope",):
    for r in rows:
        if r["block"] == b:
            print(f"  eta={r['eta_s']} seed={r['seed']} val={r['RMSE_mu_val_mu']:.6f} test='{r['test_RMSE_mu']}'")
