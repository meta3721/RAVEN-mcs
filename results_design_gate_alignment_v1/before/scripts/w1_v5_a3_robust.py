"""W1 round v5 - A3 robustness (EXPLORATORY, not preregistered, not part of the decision).

A2-G0 showed that the E3 U-Air final_metrics.json at seeds 30007/30016/30018 is not
reproducible from the same runs' checkpoints (see A2_G0_FAILURES.csv).  round_v4/TRADEOFF.csv
- the preregistered A3 input - inherits those stored values.  This script repeats the A3
TOST / MDE / dose-response on U-Air with RMSE_mu replaced by the checkpoint-based
recomputation from WORSTGROUP_V5.csv, and reports the comparison only.  It writes
A3_ROBUSTNESS_Uair.csv and prints the side-by-side.  The preregistered R1A_* files and the
A3 decision are untouched.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import w1_v5_a3 as A3                                                        # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5"
V4 = ROOT / "results_w1_ladder/round_v4"


def run(endpoint_by_arm: dict, label: str) -> pd.DataFrame:
    rows = []
    for a, b in A3.CONTRASTS:
        pa, pb = endpoint_by_arm[a], endpoint_by_arm[b]
        common = pa.index.intersection(pb.index)
        d = (pa.loc[common] - pb.loc[common]).to_numpy(float)
        comp = float(pb.loc[common].mean())
        r = A3.tost(d, comp)
        r.update({"variant": label, "contrast": "%s - %s" % (a, b),
                  "mean_diff": r["mean_diff"], "comp_mean": comp,
                  "mde_n20": (A3.__dict__ and 0) or None})
        rows.append(r)
    return pd.DataFrame(rows)


def main() -> None:
    tr = pd.read_csv(V4 / "TRADEOFF.csv")
    wg = pd.read_csv(OUT / "WORSTGROUP_V5.csv")
    ds = "uair"
    stored = {a: g.set_index("seed")["RMSE_mu"] for a, g in tr[tr.ds == ds].groupby("arm")}
    ckpt = {a: g.set_index("seed")["RMSE_mu"] for a, g in wg[wg.ds == ds].groupby("arm")}
    rows = []
    for label, src in (("stored_round_v4", stored), ("checkpoint_recomputed", ckpt)):
        f = run(src, label)
        m_family = len(A3.CONTRASTS)
        from scipy import stats
        import math
        z_a = float(stats.norm.ppf(1.0 - (0.05 / m_family) / 2.0))
        z_b = float(stats.norm.ppf(0.8))
        for _, r in f.iterrows():
            pa, pb = src[r.contrast.split(" - ")[0]], src[r.contrast.split(" - ")[1]]
            common = pa.index.intersection(pb.index)
            d = (pa.loc[common] - pb.loc[common]).to_numpy(float)
            sd = float(d.std(ddof=1))
            rows.append({**r.to_dict(), "sd_pair": sd,
                         "mde_n20": (z_a + z_b) * sd / math.sqrt(len(d)),
                         "n_for_0.25pct": math.ceil(((z_a + z_b) * sd
                                                     / (0.0025 * r["comp_mean"])) ** 2),
                         "n_for_0.5pct": math.ceil(((z_a + z_b) * sd
                                                    / (0.005 * r["comp_mean"])) ** 2)})
    out = pd.DataFrame(rows)[["variant", "contrast", "mean_diff", "rel_diff", "ci90_lo",
                              "ci90_hi", "margin", "verdict", "sd_pair", "mde_n20",
                              "n_for_0.25pct", "n_for_0.5pct", "comp_mean"]]
    out.to_csv(OUT / "A3_ROBUSTNESS_Uair.csv", index=False)
    # dose-response under the substituted endpoint
    dose = []
    for label, src in (("stored_round_v4", stored), ("checkpoint_recomputed", ckpt)):
        xs, ys = [], []
        for a, b in A3.CONTRASTS:
            pa, pb = src[a], src[b]
            common = pa.index.intersection(pb.index)
            dg = (tr[(tr.ds == ds) & (tr.arm == a)].set_index("seed")["Delta_group"]
                  - tr[(tr.ds == ds) & (tr.arm == b)].set_index("seed")["Delta_group"])
            xs.append(dg.loc[common].to_numpy(float))
            ys.append((pa.loc[common] - pb.loc[common]).to_numpy(float))
        x, y = np.concatenate(xs), np.concatenate(ys)
        slope = float(np.polyfit(x, y, 1)[0])
        dose.append({"variant": label, "slope": slope,
                     "implied_at_max_gain": slope * float(np.min(x)),
                     "max_dgroup_gain": float(np.min(x))})
    d = pd.DataFrame(dose)
    d.to_csv(OUT / "A3_ROBUSTNESS_Uair_DOSE.csv", index=False)
    print(out.to_string(index=False))
    print(d.to_string(index=False))
    (OUT / "A3_ROBUSTNESS_Uair.json").write_text(json.dumps(
        {"note": ("exploratory only; the preregistered R1A_TOST.csv / R1A_DOSE.csv and the "
                  "A3 decision are unchanged"),
         "tost": out.to_dict("records"), "dose": d.to_dict("records")},
        indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
