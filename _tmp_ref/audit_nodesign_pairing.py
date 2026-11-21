"""Reconcile the NoDesign supplement: summary means vs paired relative means.

Checks whether the Delta_group paired column equals (a) the ratio of summary means or
(b) the mean of per-seed ratios, for City Scanner and Pilot 2, and the same for Delta_c_s.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

T = Path("results_nodesign_supplement/round_v1/tables")

for tag, stem in (("cityscanner", "cityscanner"), ("pilot2", "pilot2")):
    seed = pd.read_csv(T / f"{stem}_seed_rows.csv")
    paired = pd.read_csv(T / f"{stem}_paired.csv")
    s = pd.read_csv(T / f"{stem}_summary.csv")
    print("=" * 70)
    print(tag, " seed_rows columns:", list(seed.columns)[:12])
    for metric in ("RMSE_mu", "Delta_group", "Delta_c_s"):
        if metric not in seed.columns:
            print(f"  {metric}: not a column")
            continue
        piv = seed.pivot_table(index="seed", columns="method", values=metric)
        if not {"raven", "raven_wo_design"} <= set(piv.columns):
            print(f"  {metric}: missing arm")
            continue
        a = piv["raven"].to_numpy(float)          # Design
        b = piv["raven_wo_design"].to_numpy(float)  # NoDesign
        per_seed = (a - b) / b
        ratio_of_means = (a.mean() - b.mean()) / b.mean()
        row = paired[(paired.primary == "raven") & (paired.comparator == "raven_wo_design")]
        csv_val = float(row[f"{metric}_rel_mean"].iloc[0]) if len(row) and f"{metric}_rel_mean" in paired.columns else float("nan")
        print(f"  {metric:<12} ratio_of_means={ratio_of_means:+.5f}  "
              f"mean_of_per_seed={per_seed.mean():+.5f}  csv={csv_val:+.5f}  "
              f"wins_design_lower={int((a < b).sum())}/{len(a)}")
