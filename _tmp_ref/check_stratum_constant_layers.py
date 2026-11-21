"""Check the statistical difficulty of the constructed O/U layers in the E3 aligned arm.

Read-only audit over artifacts/a5_a6_audit/audit_records.csv (28 800 client-window events,
SensorScope + U-Air). Supports record entries L6 and L7 of
ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md.

Findings:
  * p_obs_true takes exactly two values (0.1925, 0.35) and none between -> every risk set is
    block-pure, so p_obs is constant within every risk set and every opportunity stratum.
  * q_use_true is a per-(client, window) quantity: at most one value per client inside a window.
"""
from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

P = Path("artifacts/a5_a6_audit/audit_records.csv")
rows = list(csv.DictReader(P.open(encoding="utf-8")))
print("file:", P)
print("n_rows:", len(rows))
print("columns:", list(rows[0].keys()))

# --- L6: the observation propensity -----------------------------------------
pb = sorted({r["p_obs_true"] for r in rows}, key=float)
print("\n[L6] distinct p_obs_true:", pb)
print("[L6] any value strictly between the extremes?",
      any(float(pb[0]) < float(v) < float(pb[-1]) for v in pb))
for ds in sorted({r["dataset"] for r in rows}):
    sub = [r for r in rows if r["dataset"] == ds]
    print(f"[L6]   {ds}: n={len(sub)} distinct p_obs_true="
          f"{sorted({r['p_obs_true'] for r in sub}, key=float)}")

# --- L7: the usable-update propensity ---------------------------------------
qv = sorted({r["q_use_true"] for r in rows}, key=float)
print("\n[L7] distinct q_use_true overall:", len(qv), "min:", qv[0], "max:", qv[-1])
per_win = defaultdict(set)
per_cw = defaultdict(set)
for r in rows:
    g = (r["dataset"], r["seed"], r["window"])
    per_win[g].add(r["q_use_true"])
    per_cw[g + (r["client"],)].add(r["q_use_true"])
hist = defaultdict(int)
for v in per_win.values():
    hist[len(v)] += 1
print("[L7] distinct q per (dataset, seed, window):", dict(sorted(hist.items())))
print("[L7] groups with >1 distinct q inside one client-window:",
      sum(1 for v in per_cw.values() if len(v) > 1), "of", len(per_cw))
sizes = defaultdict(int)
for r in rows:
    sizes[(r["dataset"], r["seed"], r["window"], r["client"])] += 1
print("[L7] rows per client-window: min/median/max =",
      min(sizes.values()), statistics.median(sizes.values()), max(sizes.values()))
print("[L7] clients per (dataset, seed, window):",
      len({r["client"] for r in rows}))
