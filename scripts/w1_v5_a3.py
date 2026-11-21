"""W1 round v5 - A3 (R1a): equivalence / power / dose-response on the existing 20 seeds.

Read-only.  Writes only under results_w1_ladder/round_v5/.

Inputs : results_w1_ladder/round_v4/TRADEOFF.csv (RMSE_mu, Delta_group per ds/arm/seed)
         results_w1_ladder/round_v5/WORSTGROUP_V5.csv (secondary endpoint, from A2)
Outputs: R1A_TOST.csv, R1A_TOST_WG.csv (secondary), R1A_DOSE.csv, A3_SUMMARY.json

Usage: python scripts/w1_v5_a3.py
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
OUT = ROOT / "results_w1_ladder/round_v5"
V4 = ROOT / "results_w1_ladder/round_v4"
BOOT_N, BOOT_SEED = 10_000, 20261002
CONTRASTS = (("proj_beta", "uniform_window"), ("proj_beta", "fedavg_window"),
             ("raven", "proj_beta"), ("proj_beta_debt", "proj_beta"))
PRIMARY = ("proj_beta", "uniform_window")
DS = ("sensorscope", "uair")


def tost(d: np.ndarray, comp_mean: float) -> dict:
    rng = np.random.default_rng(BOOT_SEED)
    boot = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                     for _ in range(BOOT_N)])
    mean = float(d.mean())
    margin = 0.005 * float(comp_mean)
    lo, hi = float(np.percentile(boot, 5)), float(np.percentile(boot, 95))
    p_lower = float(np.mean(boot <= -margin))
    p_upper = float(np.mean(boot >= margin))
    p_tost = max(p_lower, p_upper)
    if lo > -margin and hi < margin:
        verdict = "equivalent"
    elif lo > 0:
        verdict = "harm"
    elif hi < 0:
        verdict = "benefit"
    else:
        verdict = "inconclusive"
    sd = float(d.std(ddof=1))
    return {"mean_diff": mean, "ci90_lo": lo, "ci90_hi": hi, "margin": margin,
            "verdict": verdict, "p_tost": p_tost, "sd": sd,
            "rel_diff": mean / float(comp_mean)}


def holm(p: np.ndarray) -> np.ndarray:
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * p[i])
        run = max(run, val)
        adj[i] = run
    return adj


def main() -> None:
    tr = pd.read_csv(V4 / "TRADEOFF.csv")
    a2 = json.loads((OUT / "A2_G0_SUMMARY.json").read_text(encoding="utf-8"))
    a2_ok = bool(a2.get("g0_pass"))
    piv = {ds: {a: g.set_index("seed") for a, g in tr[tr.ds == ds].groupby("arm")}
           for ds in DS}
    m_family = len(CONTRASTS)
    z_a = float(stats.norm.ppf(1.0 - (0.05 / m_family) / 2.0))
    z_b = float(stats.norm.ppf(0.8))
    rows, wg_rows, dose_rows = [], [], []
    decision_inputs = {}
    for ds in DS:
        fam = []
        for a, b in CONTRASTS:
            pa, pb = piv[ds][a], piv[ds][b]
            common = pa.index.intersection(pb.index)
            d = (pa.loc[common, "RMSE_mu"] - pb.loc[common, "RMSE_mu"]).to_numpy(float)
            comp_mean = float(pb.loc[common, "RMSE_mu"].mean())
            r = tost(d, comp_mean)
            mde = (z_a + z_b) * r["sd"] / math.sqrt(len(d))
            n025 = math.ceil(((z_a + z_b) * r["sd"] / (0.0025 * comp_mean)) ** 2)
            n050 = math.ceil(((z_a + z_b) * r["sd"] / (0.005 * comp_mean)) ** 2)
            rec = {"ds": ds, "contrast": "%s - %s" % (a, b)}
            rec.update({k: v for k, v in r.items() if k != "sd"})
            rec.update({"mde_n20": mde, "mde_n20_rel_pct": 100.0 * mde / comp_mean,
                        "n_for_0.25pct": n025, "n_for_0.5pct": n050,
                        "sd_pair": r["sd"], "n_pairs": len(d), "comp_mean": comp_mean})
            fam.append(rec)
        f = pd.DataFrame(fam)
        f["p_tost_holm"] = holm(f["p_tost"].to_numpy(float))
        f["family"] = "one dataset x TOST (4 contrasts)"
        rows.append(f)
        decision_inputs[ds] = f
        # secondary endpoint: WorstGroupRMSE with the same 0.5 % relative margin device
        # (protocol A2 stopped at A2-G0 -> not computed; see A2_G0_SUMMARY.json)
        if not a2_ok:
            wg_rows.append(pd.DataFrame([{
                "ds": ds, "endpoint": "WorstGroupRMSE", "contrast": "TBD_A2_G0_STOP",
                "status": "TBD_A2_G0_STOP", "verdict": "TBD_A2_G0_STOP",
                "mean_diff": "TBD_A2_G0_STOP", "rel_diff": "TBD_A2_G0_STOP",
                "ci90_lo": "TBD_A2_G0_STOP", "ci90_hi": "TBD_A2_G0_STOP",
                "margin": "TBD_A2_G0_STOP", "p_tost_holm": "TBD_A2_G0_STOP",
                "mde_n20": "TBD_A2_G0_STOP", "n_pairs": "TBD_A2_G0_STOP",
                "comp_mean": "TBD_A2_G0_STOP"}]))
        else:
            wg = pd.read_csv(OUT / "WORSTGROUP_V5.csv")
            wgp = {a: g.set_index("seed") for a, g in wg[wg.ds == ds].groupby("arm")}
            fam2 = []
            for a, b in CONTRASTS:
                pa, pb = wgp[a], wgp[b]
                common = pa.index.intersection(pb.index)
                d = (pa.loc[common, "WorstGroupRMSE"]
                     - pb.loc[common, "WorstGroupRMSE"]).to_numpy(float)
                comp_mean = float(pb.loc[common, "WorstGroupRMSE"].mean())
                r = tost(d, comp_mean)
                mde = (z_a + z_b) * r["sd"] / math.sqrt(len(d))
                fam2.append(dict(zip(("ds", "contrast"), (ds, "%s - %s" % (a, b))),
                                 **{k: v for k, v in r.items() if k != "sd"},
                                 mde_n20=mde, n_pairs=len(d), comp_mean=comp_mean))
            f2 = pd.DataFrame(fam2)
            f2["p_tost_holm"] = holm(f2["p_tost"].to_numpy(float))
            f2["endpoint"] = "WorstGroupRMSE"
            wg_rows.append(f2)
        # ---- dose-response: 4 contrasts x 20 seeds, pooled slope, seed-cluster bootstrap
        xs, ys, clus = [], [], []
        for a, b in CONTRASTS:
            pa, pb = piv[ds][a], piv[ds][b]
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
        implied_boot = boots * max_gain
        imp_lo, imp_hi = (float(np.percentile(implied_boot, 2.5)),
                          float(np.percentile(implied_boot, 97.5)))
        needed = -0.0025 * float(piv[ds][PRIMARY[1]].loc[:, "RMSE_mu"].mean())
        dose_rows.append({"ds": ds, "n_obs": int(len(x)),
                          "slope": slope, "ci_lo": ci_lo, "ci_hi": ci_hi,
                          "verdict": ("slope_ci_excludes_0"
                                      if (ci_lo > 0 or ci_hi < 0) else "slope_ci_includes_0"),
                          "max_dgroup_gain": max_gain,
                          "implied_rmse_change_at_max_dgroup": implied,
                          "implied_ci_lo": imp_lo, "implied_ci_hi": imp_hi,
                          "needed_0.25pct_change": needed,
                          "dose_excludes_needed_0.25pct": bool(imp_lo > needed),
                          "p_slope_boot": float(np.mean(boots <= 0.0))})
        decision_inputs[ds + "_needed"] = needed
    tost_df = pd.concat(rows, ignore_index=True)
    cols = ["ds", "contrast", "mean_diff", "rel_diff", "ci90_lo", "ci90_hi", "margin",
            "verdict", "p_tost_holm", "mde_n20", "n_for_0.25pct", "n_for_0.5pct",
            "mde_n20_rel_pct", "sd_pair", "n_pairs", "comp_mean", "p_tost", "family"]
    tost_df[cols].to_csv(OUT / "R1A_TOST.csv", index=False)
    pd.concat(wg_rows, ignore_index=True).to_csv(OUT / "R1A_TOST_WG.csv", index=False)
    dose = pd.DataFrame(dose_rows)
    dose.to_csv(OUT / "R1A_DOSE.csv", index=False)
    # ---- mechanical decision (protocol 2 A3, quoted in the report)
    ua = decision_inputs["uair"]
    ua_pu = ua[ua.contrast == "proj_beta - uniform_window"].iloc[0]
    harm_row = bool(ua_pu["verdict"] == "harm")
    all_equiv = {ds: bool((decision_inputs[ds]["verdict"] == "equivalent").all()) for ds in DS}
    dose_excl = {r["ds"]: bool(r["dose_excludes_needed_0.25pct"]) for _, r in dose.iterrows()}
    inconf = {ds: decision_inputs[ds][decision_inputs[ds]["verdict"] == "inconclusive"]
              for ds in DS}
    mde_gt = {ds: (inconf[ds]["mde_n20"] > inconf[ds]["margin"]).tolist()
              for ds in DS if len(inconf[ds])}
    prop_ok = bool(any(len(inconf[ds]) for ds in DS)
                   and any(any(v) for v in mde_gt.values()))
    if harm_row:
        decision = ("R1a HARM FINDING: U-Air proj_beta - uniform_window is 'harm'. "
                    "Reported as a harm finding; Part B is not run to overturn it.")
    elif all(all_equiv.values()):
        decision = ("R1 CLOSED AS A MEASURED NULL: every primary TOST row is 'equivalent'. "
                    "Part B is not run.")
    elif any(dose_excl.values()):
        decision = ("R1 CLOSED AS A MEASURED NULL: the dose-response CI excludes the effect "
                    "needed for a 0.25 %% RMSE_mu gain at the observed Delta_group range "
                    "(datasets: %s). Part B is not run."
                    % ",".join([d for d, v in dose_excl.items() if v]))
    elif prop_ok:
        decision = ("PART B MAY BE PROPOSED: primary rows are 'inconclusive' and MDE > delta_P "
                    "for at least one contrast (%s)." % json.dumps(mde_gt))
    else:
        decision = ("R1 CLOSED AS A MEASURED NULL (no equivalence-block, no dose-response "
                    "exclusion and no inconclusive row with MDE > delta_P). Part B is not run.")
    summary = {"z_holm_adjusted": z_a, "z_power": z_b, "family_size": m_family,
               "a2_g0_pass": a2_ok,
               "a2_status": ("secondary WorstGroupRMSE endpoint TBD: A2 stopped at A2-G0"
                             if not a2_ok else "A2 G0 passed"),
               "uair_tree_caveat": ("round_v4/TRADEOFF.csv inherits the E3 U-Air "
                                    "final_metrics.json values; at seeds 30007/30016/30018 "
                                    "those are not reproducible from the runs' own "
                                    "checkpoints (see A2_G0_FAILURES.csv)"),
               "all_equivalent": all_equiv, "dose_excludes_needed": dose_excl,
               "uair_primary_verdict": str(ua_pu["verdict"]),
               "inconclusive_mde_gt_margin": mde_gt,
               "part_b_proposable": prop_ok, "decision": decision,
               "tost": tost_df[["ds", "contrast", "verdict", "mean_diff", "rel_diff",
                                "margin", "p_tost_holm", "mde_n20", "mde_n20_rel_pct",
                                "n_for_0.25pct", "n_for_0.5pct"]].to_dict("records"),
               "dose": dose.to_dict("records")}
    (OUT / "A3_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str),
                                         encoding="utf-8")
    print(tost_df[cols].to_string(index=False))
    print(dose.to_string(index=False))
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("tost", "dose")}, indent=2, default=str))


if __name__ == "__main__":
    main()
