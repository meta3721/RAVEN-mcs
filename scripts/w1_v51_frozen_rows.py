"""Add the frozen-arm endpoint rows to A1P_IMPL.csv (needed to form every v4 contrast).

The oracle is defined for the two trained solver rules.  The three frozen arms are
*comparators* in round_v4/TRADEOFF_PAIRED.csv and their endpoints are the stored
final_metrics.json values in both the trained and the oracle comparison, so their eps_impl is
0 by construction.
"""
from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v5_1"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"

df = pd.read_csv(OUT / "A1P_IMPL.csv")
missing = [a for a in ("fedavg_window", "inst_cal", "raven")
           if not (df.arm == a).any()]
if not missing:
    print("frozen rows already present")
    raise SystemExit(0)
rows = []
for ds in ("sensorscope", "uair"):
    for seed in range(30001, 30021):
        fm = pd.read_json(E3 / ds / "raven" / f"seed{seed}" / "final_metrics.json",
                          typ="series")
        for arm in missing:
            f = pd.read_json(E3 / ds / arm / f"seed{seed}" / "final_metrics.json",
                             typ="series")
            rows.append({"ds": ds, "arm": arm, "seed": seed,
                         "alpha_linf_trained": 0.0, "eps_impl_group": 0.0,
                         "eps_impl_cs": 0.0, "alpha_linf_ref": 0.0,
                         "eps_ref_group": 0.0, "eps_ref_cs": 0.0, "first_q_div": np.nan,
                         "d_group_oracle": float(f["Delta_group"]),
                         "d_cs_oracle": float(f["Delta_c_s"]),
                         "d_group_trained": float(f["Delta_group"]),
                         "d_cs_trained": float(f["Delta_c_s"]),
                         "d_group_reference": float(f["Delta_group"]),
                         "d_cs_reference": float(f["Delta_c_s"]),
                         "err_self_group": 0.0, "err_self_cs": 0.0,
                         "b_g1_mismatch_windows": 0, "verdict": "comparator"})
pd.concat([df, pd.DataFrame(rows)], ignore_index=True).to_csv(OUT / "A1P_IMPL.csv", index=False)
print("added", len(rows), "comparator rows")
