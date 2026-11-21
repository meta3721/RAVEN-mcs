"""S1 numeric audit: per-method means in the two figure CSVs, all methods and endpoints.

Read-only. Aggregates existing CSV means only; no model inference, no re-scoring.
"""
from __future__ import annotations

import csv
import pathlib
from collections import defaultdict

D = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/figure_data")
FILES = {
    "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv": ("Delta_group", "Delta_c_s"),
    "FIG_E3_E3_PREDICTION_RISK.csv": ("RMSE_mu", "Tail_RMSE"),
}

for fn, metrics in FILES.items():
    p = D / fn
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    print(f"=== {fn}  ({len(rows)} rows) ===")
    print("  columns:", list(rows[0].keys()))
    classes = defaultdict(int)
    seeds = defaultdict(set)
    for r in rows:
        classes[r.get("comparison_class", "?")] += 1
        seeds[(r["dataset"], r["method"])].add(r["seed"])
    print("  comparison_class:", dict(classes))
    for ds in ("SensorScope", "U-Air"):
        print(f"  --- {ds}")
        methods = sorted({r["method"] for r in rows if r["dataset"] == ds})
        for m in methods:
            sel = [r for r in rows if r["dataset"] == ds and r["method"] == m]
            if not sel:
                continue
            ns = len({r["seed"] for r in sel})
            parts = []
            for met in metrics:
                v = [float(r[met]) for r in sel if r.get(met) not in (None, "", "nan")]
                parts.append(f"{met}={sum(v) / len(v):.6f}" if v else f"{met}=NA")
            cls = sorted({r.get("comparison_class", "?") for r in sel})
            print(f"    {m:<22} n_seeds={ns:>2}  " + "  ".join(parts) + f"   class={cls}")
    print()
