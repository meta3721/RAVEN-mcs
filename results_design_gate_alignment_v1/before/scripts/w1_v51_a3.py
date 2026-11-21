"""W1 round v5.1 - A3' (R1 wording): TOST / MDE / dose-response on theta-canonical values.

Re-runs the round-v5 A3 device unchanged on TRADEOFF_V51.csv (theta-canonical) with the AM-5
labels, prints the v5 and v5.1 tables side by side, adds the secondary WorstGroupRMSE TOST
from A2', and performs the re-sourcing check on the U-Air RMSE_mu rows of
round_v4/TRADEOFF_PAIRED.csv.  The v5 decision (R1 closed) is NOT re-opened.

Usage: python scripts/w1_v51_a3.py
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v5_1"
V4 = ROOT / "results_w1_ladder/round_v4"
V5 = ROOT / "results_w1_ladder/round_v5"
BOOT_N, BOOT_SEED = 10_000, 20261002
CONTRASTS = (("proj_beta", "uniform_window"), ("proj_beta", "fedavg_window"),
             ("raven", "proj_beta"), ("proj_beta_debt", "proj_beta"))
PRIMARY = ("proj_beta", "uniform_window")
DS = ("sensorscope", "uair")


def am5(lo, hi, margin):
    if lo > -margin and hi < margin:
        if lo <= 0.0 <= hi:
            return "equivalent_zero"
        return "equivalent_cost" if lo > 0 else "equivalent_gain"
    if lo > 0:
        return "harm"
    if hi < 0:
        return "benefit"
    return "inconclusive"


def holm(p):
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * p[i])
        run = max(run, val)
        adj[i] = run
    return adj


def tost(d, comp_mean):
    rng = np.random.default_rng(BOOT_SEED)
    boot = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                     for _ in range(BOOT_N)])
    mean = float(d.mean())
    margin = 0.005 * float(comp_mean)
    lo, hi = float(np.percentile(boot, 5)), float(np.percentile(boot, 95))
    p_tost = max(float(np.mean(boot <= -margin)), float(np.mean(boot >= margin)))
    return {"mean_diff": mean, "ci90_lo": lo, "ci90_hi": hi, "margin": margin,
            "label_AM5": am5(lo, hi, margin), "p_tost": p_tost,
            "sd": float(d.std(ddof=1)), "rel_diff": mean / float(comp_mean)}


def main() -> None:
    tr51 = pd.read_csv(OUT / "TRADEOFF_V51.csv")
    tr4 = pd.read_csv(V4 / "TRADEOFF.csv")
    piv51 = {ds: {a: g.set_index("seed") for a, g in tr51[tr51.ds == ds].groupby("arm")}
             for ds in DS}
    piv4 = {ds: {a: g.set_index("seed") for a, g in tr4[tr4.ds == ds].groupby("arm")}
            for ds in DS}
    m_family = len(CONTRASTS)
    z_a = float(stats.norm.ppf(1.0 - (0.05 / m_family) / 2.0))
    z_b = float(stats.norm.ppf(0.8))
    v5 = pd.read_csv(V5 / "R1A_TOST.csv")
    rows51, dose_rows, wg_rows = [], [], []
    for ds in DS:
        fam = []
        for a, b in CONTRASTS:
            pa, pb = piv51[ds][a], piv51[ds][b]
            common = pa.index.intersection(pb.index)
            d = (pa.loc[common, "RMSE_mu"] - pb.loc[common, "RMSE_mu"]).to_numpy(float)
            comp_mean = float(pb.loc[common, "RMSE_mu"].mean())
            r = tost(d, comp_mean)
            mde = (z_a + z_b) * r["sd"] / math.sqrt(len(d))
            fam.append({"ds": ds, "contrast": "%s - %s" % (a, b),
                        **{k: v for k, v in r.items() if k != "sd"},
                        "mde_n20": mde, "mde_n20_rel_pct": 100.0 * mde / comp_mean,
                        "n_for_0.25pct": math.ceil(((z_a + z_b) * r["sd"]
                                                    / (0.0025 * comp_mean)) ** 2),
                        "n_for_0.5pct": math.ceil(((z_a + z_b) * r["sd"]
                                                   / (0.005 * comp_mean)) ** 2),
                        "sd_pair": r["sd"], "n_pairs": len(d), "comp_mean": comp_mean})
        f = pd.DataFrame(fam)
        f["p_tost_holm"] = holm(f.p_tost.to_numpy(float))
        f["family"] = "one dataset x TOST (4 contrasts)"
        rows51.append(f)
        # secondary endpoint: WorstGroupRMSE
        wg = pd.read_csv(OUT / "WORSTGROUP_V51.csv")
        wgp = {a: g.set_index("seed") for a, g in wg[wg.ds == ds].groupby("arm")}
        fam2 = []
        for a, b in CONTRASTS:
            pa, pb = wgp[a], wgp[b]
            common = pa.index.intersection(pb.index)
            d = (pa.loc[common, "WorstGroupRMSE_canonical"]
                 - pb.loc[common, "WorstGroupRMSE_canonical"]).to_numpy(float)
            cm = float(pb.loc[common, "WorstGroupRMSE_canonical"].mean())
            r = tost(d, cm)
            mde = (z_a + z_b) * r["sd"] / math.sqrt(len(d))
            fam2.append({"ds": ds, "endpoint": "WorstGroupRMSE",
                         "contrast": "%s - %s" % (a, b),
                         **{k: v for k, v in r.items() if k != "sd"},
                         "mde_n20": mde, "mde_n20_rel_pct": 100.0 * mde / cm,
                         "n_pairs": len(d), "comp_mean": cm})
        f2 = pd.DataFrame(fam2)
        f2["p_tost_holm"] = holm(f2.p_tost.to_numpy(float))
        wg_rows.append(f2)
        # dose-response
        xs, ys, clus = [], [], []
        for a, b in CONTRASTS:
            pa, pb = piv51[ds][a], piv51[ds][b]
            common = pa.index.intersection(pb.index)
            xs.append((pa.loc[common, "Delta_group"] - pb.loc[common, "Delta_group"])
                      .to_numpy(float))
            ys.append((pa.loc[common, "RMSE_mu"] - pb.loc[common, "RMSE_mu"]).to_numpy(float))
            clus.append(np.asarray(common, dtype=int))
        x = np.concatenate(xs)
        y = np.concatenate(ys)
        seed = np.concatenate(clus)
        slope = float(np.polyfit(x, y, 1)[0])
        uniq = np.unique(seed)
        rng = np.random.default_rng(BOOT_SEED)
        boots = []
        for _ in range(BOOT_N):
            pick = rng.choice(uniq, len(uniq), replace=True)
            idx = np.concatenate([np.where(seed == s)[0] for s in pick])
            boots.append(float(np.polyfit(x[idx], y[idx], 1)[0]))
        boots = np.asarray(boots)
        ci_lo, ci_hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
        max_gain = float(np.min(x))
        implied = slope * max_gain
        imp_lo, imp_hi = (float(np.percentile(boots * max_gain, 2.5)),
                          float(np.percentile(boots * max_gain, 97.5)))
        needed = -0.0025 * float(piv51[ds][PRIMARY[1]]["RMSE_mu"].mean())
        dose_rows.append({"ds": ds, "n_obs": int(len(x)), "slope": slope,
                          "ci_lo": ci_lo, "ci_hi": ci_hi,
                          "verdict": ("slope_ci_excludes_0" if (ci_lo > 0 or ci_hi < 0)
                                      else "slope_ci_includes_0"),
                          "max_dgroup_gain": max_gain,
                          "implied_rmse_change_at_max_dgroup": implied,
                          "implied_ci_lo": imp_lo, "implied_ci_hi": imp_hi,
                          "needed_0.25pct_change": needed,
                          "dose_excludes_needed_0.25pct": bool(imp_lo > needed),
                          "p_slope_boot": float(np.mean(boots <= 0.0))})
    t51 = pd.concat(rows51, ignore_index=True)
    cols = ["ds", "contrast", "mean_diff", "rel_diff", "ci90_lo", "ci90_hi", "margin",
            "label_AM5", "p_tost_holm", "mde_n20", "mde_n20_rel_pct", "n_for_0.25pct",
            "n_for_0.5pct", "sd_pair", "n_pairs", "comp_mean", "p_tost", "family"]
    t51[cols].to_csv(OUT / "A3P_TOST_V51.csv", index=False)
    pd.concat(wg_rows, ignore_index=True).to_csv(OUT / "A3P_TOST_WG.csv", index=False)
    dose = pd.DataFrame(dose_rows)
    dose.to_csv(OUT / "A3P_DOSE.csv", index=False)
    # ---- side by side (v5 preregistered vs v5.1)
    v5r = v5.rename(columns={"verdict": "verdict_v5"}).copy()
    v5r["label_AM5_v5"] = [am5(r.ci90_lo, r.ci90_hi, r.margin)
                           for r in v5r.itertuples(index=False)]
    side = v5r[["ds", "contrast", "mean_diff", "rel_diff", "ci90_lo", "ci90_hi", "margin",
                "verdict_v5", "label_AM5_v5", "p_tost_holm", "mde_n20",
                "mde_n20_rel_pct", "n_for_0.25pct", "n_for_0.5pct"]].merge(
        t51[["ds", "contrast", "mean_diff", "rel_diff", "ci90_lo", "ci90_hi", "margin",
             "label_AM5", "p_tost_holm", "mde_n20", "mde_n20_rel_pct", "n_for_0.25pct",
             "n_for_0.5pct"]].rename(columns={
                 "mean_diff": "mean_diff_v51", "rel_diff": "rel_diff_v51",
                 "ci90_lo": "ci90_lo_v51", "ci90_hi": "ci90_hi_v51",
                 "margin": "margin_v51", "p_tost_holm": "p_tost_holm_v51",
                 "mde_n20": "mde_n20_v51", "mde_n20_rel_pct": "mde_n20_rel_pct_v51",
                 "n_for_0.25pct": "n_for_0.25pct_v51",
                 "n_for_0.5pct": "n_for_0.5pct_v51"}),
        on=["ds", "contrast"], how="outer")
    side.to_csv(OUT / "A3P_SIDE_BY_SIDE.csv", index=False)
    # ---- re-sourcing check: U-Air RMSE_mu rows of round_v4/TRADEOFF_PAIRED.csv
    v4p = pd.read_csv(V4 / "TRADEOFF_PAIRED.csv")
    v4p = v4p[(v4p.ds == "uair") & (v4p.endpoint == "RMSE_mu")]
    PAIRS = (("proj_beta", "uniform_window"), ("raven", "proj_beta"),
             ("proj_beta", "fedavg_window"), ("uniform_window", "fedavg_window"),
             ("proj_beta_debt", "proj_beta"))
    resrc = []
    for a, b in PAIRS:
        pa, pb = piv51["uair"][a], piv51["uair"][b]
        common = pa.index.intersection(pb.index)
        d = (pa.loc[common, "RMSE_mu"] - pb.loc[common, "RMSE_mu"]).to_numpy(float)
        rng = np.random.default_rng(BOOT_SEED)
        boot = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                         for _ in range(BOOT_N)])
        try:
            p = float(stats.wilcoxon(d).pvalue)
        except Exception:                                        # noqa: BLE001
            p = float("nan")
        resrc.append({"ds": "uair", "endpoint": "RMSE_mu",
                      "contrast": "%s - %s" % (a, b),
                      "mean_diff_v51": float(d.mean()),
                      "ci_lo_v51": float(np.percentile(boot, 2.5)),
                      "ci_hi_v51": float(np.percentile(boot, 97.5)),
                      "p_wilcoxon_v51": p,
                      "mean_arm_v51": float(pa["RMSE_mu"].mean()),
                      "mean_comp_v51": float(pb["RMSE_mu"].mean())})
    rs = pd.DataFrame(resrc)
    fam_p = rs.p_wilcoxon_v51.to_numpy(float)
    rs["p_holm_v51"] = holm(fam_p)
    rs = rs.merge(v4p[["contrast", "mean_diff", "ci_lo", "ci_hi", "p_wilcoxon", "p_holm",
                       "n_seeds"]].rename(columns={
                           "mean_diff": "mean_diff_v4", "ci_lo": "ci_lo_v4",
                           "ci_hi": "ci_hi_v4", "p_wilcoxon": "p_wilcoxon_v4",
                           "p_holm": "p_holm_v4"}), on="contrast", how="left")

    def sig4(x):
        return None if x is None or (isinstance(x, float) and not np.isfinite(x)) \
            else float("%.4g" % x)

    rs["mean_diff_v4_4sig"] = [sig4(v) for v in rs.mean_diff_v4]
    rs["mean_diff_v51_4sig"] = [sig4(v) for v in rs.mean_diff_v51]
    rs["ci_lo_v4_4sig"] = [sig4(v) for v in rs.ci_lo_v4]
    rs["ci_lo_v51_4sig"] = [sig4(v) for v in rs.ci_lo_v51]
    rs["ci_hi_v4_4sig"] = [sig4(v) for v in rs.ci_hi_v4]
    rs["ci_hi_v51_4sig"] = [sig4(v) for v in rs.ci_hi_v51]
    rs["p_holm_v4_4sig"] = [sig4(v) for v in rs.p_holm_v4]
    rs["p_holm_v51_4sig"] = [sig4(v) for v in rs.p_holm_v51]
    for c in ("mean_diff", "ci_lo", "ci_hi", "p_holm"):
        rs["differs_4sig_" + c] = rs[c + "_v4_4sig"] != rs[c + "_v51_4sig"]
    rs.to_csv(OUT / "A3P_RESOURCE_UPAIR.csv", index=False)
    # ---- sheet values quoted in the paper (U-Air RMSE cells)
    cells = []
    for arm in ("fedavg_window", "raven", "inst_cal", "uniform_window", "proj_beta",
                "proj_beta_debt"):
        v4m = float(piv4["uair"][arm]["RMSE_mu"].mean())
        v51m = float(piv51["uair"][arm]["RMSE_mu"].mean())
        cells.append({"arm": arm, "manuscript_value_v4": round(v4m, 5),
                      "theta_canonical_value": round(v51m, 5),
                      "differs_4sig": ("%.4g" % v4m) != ("%.4g" % v51m)})
    summary = {"z_holm_adjusted": z_a, "z_power": z_b, "family_size": m_family,
               "a2p_g0_all_pass": json.loads((OUT / "A2P_SUMMARY.json")
                                             .read_text(encoding="utf-8"))["gates"]["G0_all_pass"],
               "v5_decision_not_reopened": True,
               "v5_tost_verdicts": {"%s|%s" % k: v for k, v in
                                    v5r.set_index(["ds", "contrast"]).verdict_v5.items()},
               "v51_tost_labels": {"%s|%s" % k: v for k, v in
                                   t51.set_index(["ds", "contrast"]).label_AM5.items()},
               "re_sourced_manuscript_cells": cells,
               "n_cells_differing_4sig": int(sum(1 for c in cells if c["differs_4sig"])),
               "tost_v51": t51[cols].to_dict("records"),
               "wg_tost": pd.concat(wg_rows, ignore_index=True).to_dict("records"),
               "dose_v51": dose.to_dict("records")}
    (OUT / "A3P_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str),
                                          encoding="utf-8")
    print(side.to_string(index=False))
    print(dose.to_string(index=False))
    print(rs[["contrast", "mean_diff_v4_4sig", "mean_diff_v51_4sig", "ci_lo_v4_4sig",
              "ci_lo_v51_4sig", "ci_hi_v4_4sig", "ci_hi_v51_4sig", "p_holm_v4_4sig",
              "p_holm_v51_4sig"]].to_string(index=False))
    print(pd.DataFrame(cells).to_string(index=False))


if __name__ == "__main__":
    main()
