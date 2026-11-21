"""T6 (round v3): G-unit re-decision for the v2 and T3 registered contrasts.

dG = (d_a - d_b) / (d_unif - d*)      ratio of means; paired bootstrap resamples numerator and
denominator in the SAME draw (10 000 draws, seed 20261002).

Thresholds (PREREG S6):
  equivalence : CI(dG) fully inside [-0.10, +0.10]
  necessity   : CI(dG) fully outside that band (both signs reported explicitly)
  practical   : CI lower bound of the absolute improvement >= 0.5 pp group TV (|d_a - d_b|/2*100)

Holm families: within each (dataset, endpoint): v2's computable contrasts + T3's computable
contrasts; the pooled v2-style family is also reported for comparability.  T4/T5 are excluded.

Read-only: writes only results_w1_ladder/round_v3/.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v3"
R2 = ROOT / "results_w1_ladder/round_v2"
BOOT_N, BOOT_SEED = 10_000, 20261002
BAND, PP_MIN = 0.10, 0.5
V2_CONTRASTS = (("L6", "L5"), ("L5", "L3"), ("L3", "L2"), ("L5", "L4p"), ("L6", "L3"))
V3_CONTRASTS = (("B1:raven", "B0:raven"), ("B2:raven", "B1:raven"), ("B3:raven", "B2:raven"),
                ("B1:raven_simoracle", "B1:raven"), ("B1:raven", "B1:raven_wo_obs"),
                ("B1:raven", "B1:raven_wo_use"), ("B1:raven", "B1:raven_wo_design"),
                ("B1:raven", "B1:uniform"))
V2_UNIT_DECISIONS = {  # v2's Delta-unit column, carried over (superseded)
    ("L6", "L5"): "v2 第1行触发（±0.10 in Delta units）",
    ("L5", "L3"): "v2 第2行触发（±0.10 in Delta units）",
    ("L3", "L2"): "NA_input_unavailable",
    ("L5", "L4p"): "—",
    ("L6", "L3"): "—",
}


def holm(pvals: list) -> list:
    p = np.asarray(pvals, dtype=float)
    ok = ~np.isnan(p)
    out = np.full_like(p, np.nan)
    idx = np.where(ok)[0]
    order = idx[np.argsort(p[idx])]
    m, run = len(order), 0.0
    for rank, i in enumerate(order):
        adj = min(1.0, (m - rank) * p[i])
        run = max(run, adj)
        out[i] = run
    return out.tolist()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v3")
    args = ap.parse_args()
    lat = pd.read_csv(R2 / "LADDER_REPORT_SEEDS.csv")
    lat = lat[lat.ruler == "R_on"]
    src = pd.read_csv(OUT / "SOURCE_LADDER.csv")
    src = src[(src["split"] == "report") & (src["status"].isna() | (src["status"] == "ok"))]
    rng = np.random.default_rng(BOOT_SEED)
    rows = []
    for ds in sorted(set(lat.ds) | set(src.ds)):
        # per-seed series for v2 rungs and v3 rules, plus the reference gap
        series, gap = {}, {}
        g = lat[lat.ds == ds]
        for seed, sub in g.groupby("seed"):
            for r in ("L0", "L1", "L3", "L4", "L4p", "L5", "L6"):
                v = sub[sub.rung == r]["d_group"]
                if len(v):
                    series[("v2", r, seed)] = float(v.iloc[0])
            if len(sub):
                gap[seed] = float(sub["d_unif_group"].iloc[0] - sub["d_star_group"].iloc[0])
                series[("unif", "L0", seed)] = float(sub["d_unif_group"].iloc[0])
        s2 = src[src.ds == ds]
        for (s, r), sub in s2.groupby(["src", "rule"]):
            for seed, v in zip(sub["seed"], sub["d_group"]):
                if np.isfinite(v):
                    series[("v3", f"{r}:{s}", int(seed))] = float(v)
                if ("unif", "L0", int(seed)) not in series:
                    gg = lat[(lat.ds == ds) & (lat.seed == seed)]
                    if len(gg):
                        series[("unif", "L0", int(seed))] = float(gg["d_unif_group"].iloc[0])
                        gap[int(seed)] = float(gg["d_unif_group"].iloc[0] - gg["d_star_group"].iloc[0])
        seeds = sorted(gap)
        if len(seeds) < 3:
            continue
        for ep in ("group",):
            recs = []
            for tagv, a, b in ([("v2", *c) for c in V2_CONTRASTS] +
                               [("v3", *c) for c in V3_CONTRASTS]):
                ka = ("v2", a, None) if tagv == "v2" else ("v3", a, None)
                kb = ("v2", b, None) if tagv == "v2" else ("v3", b, None)
                if tagv == "v3":
                    kb = ("v3", b, None) if b in {f"{r}:{s}" for s, r in
                                                  [(x.split(":")[1], x.split(":")[0]) for x in []]} or ":" in b else ("v2", b, None)
                def get(key, sd):
                    if key[0] == "v2":
                        return series.get(("v2", key[1], sd))
                    return series.get(("v3", key[1], sd))
                common = [sd for sd in seeds if get(ka, sd) is not None and get(kb, sd) is not None
                          and gap.get(sd, 0) > 0]
                if len(common) < 3:
                    recs.append({"ds": ds, "endpoint": ep, "source": tagv,
                                 "contrast": f"{a} - {b}", "status": "insufficient_alignment"
                                 if tagv == "v3" else "NA_input_unavailable",
                                 "n_seeds": len(common)})
                    continue
                num = np.array([get(ka, sd) - get(kb, sd) for sd in common], dtype=float)
                den = np.array([gap[sd] for sd in common], dtype=float)
                dg = num / den
                draws = np.array([(lambda i: num[i].mean() / den[i].mean())(
                    rng.choice(len(common), len(common), replace=True)) for _ in range(BOOT_N)])
                lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
                pp = -100 * num.mean() / 2                     # improvement of `a` over `b` in pp
                pp_draws = -100 * np.array([num[i].mean() for i in
                                            [rng.choice(len(common), len(common), replace=True)
                                             for _ in range(2000)]]) / 2
                pp_lo = float(np.percentile(pp_draws, 2.5))
                try:
                    p = float(stats.wilcoxon(dg).pvalue)
                except Exception:
                    p = float("nan")
                recs.append({"ds": ds, "endpoint": ep, "source": tagv, "contrast": f"{a} - {b}",
                             "status": "ok", "n_seeds": len(common),
                             "mean_dG": float(dg.mean()) if len(common) else None,
                             "dG_ratio_of_means": float(num.mean() / den.mean()),
                             "ci_lo": lo, "ci_hi": hi, "p_wilcoxon": p,
                             "equiv_within_band": bool(lo >= -BAND and hi <= BAND),
                             "full_a_better_beyond_band": bool(hi < -BAND),
                             "full_a_worse_beyond_band": bool(lo > BAND),
                             "pp_improvement_a_over_b": float(pp), "pp_ci_lo": pp_lo,
                             "practical_pp_ge_0.5": bool(pp_lo >= PP_MIN),
                             "superseded_units": True,
                             "v2_delta_units_verdict": V2_UNIT_DECISIONS.get((a, b), "—")})
            # Holm within (ds, endpoint) over computable contrasts
            ok = [r for r in recs if r["status"] == "ok"]
            if ok:
                hs = holm([r["p_wilcoxon"] for r in ok])
                for r, h in zip(ok, hs):
                    r["p_holm_within_ds_endpoint"] = h
            pooled = [r for r in ok]
            if pooled:
                hs = holm([r["p_wilcoxon"] for r in pooled])
                for r, h in zip(pooled, hs):
                    r["p_holm_pooled_family"] = h
            rows.extend(recs)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "G_UNIT_DECISIONS.csv", index=False)
    cols = ["ds", "source", "contrast", "status", "n_seeds", "mean_dG", "ci_lo", "ci_hi",
            "equiv_within_band", "full_a_better_beyond_band", "pp_improvement_a_over_b",
            "pp_ci_lo", "practical_pp_ge_0.5", "p_holm_within_ds_endpoint"]
    print(df[[c for c in cols if c in df.columns]].round(5).to_string(index=False))


if __name__ == "__main__":
    main()
