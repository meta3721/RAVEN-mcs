"""W1 round v5 - A1 secondary, read-only: trained endpoints vs the STORED round-v3/v4
reference columns that the round-v4 gates actually used (protocol 0.1-6, PREREG 2.4).

Reference columns:
  uniform_window  <- results_w1_ladder/round_v2/FRONTIER.csv  (ruler=R_on) d_unif_group/d_unif_cs
  proj_beta       <- results_w1_ladder/round_v3/SOURCE_LADDER.csv (src=raven, rule=B1)
  proj_beta_debt  <- results_w1_ladder/round_v4/DEBT_STRENGTH_V4.csv (kappa=1000)

Writes results_w1_ladder/round_v5/A1_LEGACY_XREF.csv only.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v5"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
ARMS = ("uniform_window", "proj_beta", "proj_beta_debt")
DS = ("sensorscope", "uair")
SEEDS = list(range(30001, 30021))


def main() -> None:
    fr = pd.read_csv(ROOT / "results_w1_ladder/round_v2/FRONTIER.csv")
    fr = fr[fr.ruler == "R_on"].groupby(["ds", "seed"])[
        ["d_unif_group", "d_unif_cs"]].first()
    src = pd.read_csv(ROOT / "results_w1_ladder/round_v3/SOURCE_LADDER.csv")
    src = src[(src.src == "raven") & (src["status"].isna() | (src["status"] == "ok"))]
    b1 = src[src.rule == "B1"].set_index(["ds", "seed"])
    a2 = pd.read_csv(ROOT / "results_w1_ladder/round_v4/DEBT_STRENGTH_V4.csv")
    a2 = a2[np.isclose(a2.kappa, 1000.0)].set_index(["ds", "seed"])
    rows = []
    for ds in DS:
        for arm in ARMS:
            for seed in SEEDS:
                fm = json.loads((TRAIN / ds / arm / f"seed{seed}" /
                                 "final_metrics.json").read_text(encoding="utf-8"))
                if arm == "uniform_window":
                    ref_g, ref_c = (float(fr.loc[(ds, seed), "d_unif_group"]),
                                    float(fr.loc[(ds, seed), "d_unif_cs"]))
                    source = "round_v2/FRONTIER.csv d_unif_* (ruler R_on)"
                elif arm == "proj_beta":
                    ref_g, ref_c = (float(b1.loc[(ds, seed), "d_group"]),
                                    float(b1.loc[(ds, seed), "d_cs"]))
                    source = "round_v3/SOURCE_LADDER.csv rule=B1 src=raven"
                else:
                    ref_g, ref_c = (float(a2.loc[(ds, seed), "d_group"]),
                                    float(a2.loc[(ds, seed), "d_cs"]))
                    source = "round_v4/DEBT_STRENGTH_V4.csv kappa=1000"
                dg, dc = float(fm["Delta_group"]), float(fm["Delta_c_s"])
                rows.append({"ds": ds, "arm": arm, "seed": seed,
                             "trained_d_group": dg, "ref_d_group": ref_g,
                             "resid_d_group": abs(dg - ref_g),
                             "trained_d_cs": dc, "ref_d_cs": ref_c,
                             "resid_d_cs": abs(dc - ref_c),
                             "resid_max": max(abs(dg - ref_g), abs(dc - ref_c)),
                             "reference_source": source})
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "A1_LEGACY_XREF.csv", index=False)
    summ = (d.groupby(["ds", "arm"])[["resid_d_group", "resid_d_cs", "resid_max"]]
            .agg(["min", "max"]).round(12).reset_index())
    summ.columns = ["_".join([c for c in col if c]) for col in summ.columns]
    summ.to_csv(OUT / "A1_LEGACY_XREF_SUMMARY.csv", index=False)
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()
