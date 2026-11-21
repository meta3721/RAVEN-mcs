"""A1 (round v4): re-evaluate hyperparameter-free rules on all 20 seeds.

Sources (all read-only):
  * round_v3/SOURCE_LADDER.csv  -> T3 rules B0-B3 for every src (20 seeds, split column)
  * round_v2/LADDER.csv         -> v2 L5/L6 on report seeds (cross-check)
  * freshly recomputed L5/L6 on the TUNE seeds (frozen lambda, beta-hat = raven_wo_use reference,
    debt = recorded Q) -- E7 label
  * frozen arms raven / inst_cal / fedavg_window -> their own final_metrics (20 seeds)
  * round_v2/FRONTIER.csv       -> Delta_unif / Delta* per (ds, seed)

Outputs: FULL_SEED_LADDER.csv, FULL_SEED_DECISIONS.csv.
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                       # noqa: E402
import w1_ladder as L                                                       # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v4"
V3 = ROOT / "results_w1_ladder/round_v3"
V2 = ROOT / "results_w1_ladder/round_v2"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
FROZEN = {"raven": E3, "inst_cal": E3, "fedavg_window": E3}
CONTRASTS = (("B1:raven", "B0:raven"), ("B1:raven", "B1:uniform"), ("B2:raven", "B1:raven"),
             ("B3:raven", "B2:raven"), ("B1:raven", "B1:raven_wo_design"),
             ("B1:raven", "B1:raven_wo_obs"), ("B1:raven", "B1:raven_wo_use"),
             ("L6", "L5"))
BLOCKS = {"all20": W.SEEDS, "tune": W.TUNE, "report": W.REPORT}
BOOT_N, BOOT_SEED = 10_000, 20261002
BAND, PP_MIN = 0.10, 0.5


def boot_ci(arr: np.ndarray, rng) -> tuple:
    if len(arr) < 2:
        return (float("nan"), float("nan"))
    draws = np.array([arr[rng.choice(len(arr), len(arr), replace=True)].mean()
                      for _ in range(BOOT_N)])
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(BOOT_SEED)
    # ---- assemble per-seed series ------------------------------------------------
    series: dict = {}          # (ds, tag, seed) -> (d_group, d_cs)
    src = pd.read_csv(V3 / "SOURCE_LADDER.csv")
    src = src[src["status"].isna() | (src["status"] == "ok")]
    for r in src.itertuples():
        series[(r.ds, f"{r.rule}:{r.src}", int(r.seed))] = (float(r.d_group), float(r.d_cs))
    v2 = pd.read_csv(V2 / "LADDER.csv")
    v2 = v2[v2["split"] == "report"]
    for r in v2[v2.rung.isin(["L5", "L6"])].itertuples():
        series.setdefault((r.ds, r.rung, int(r.seed)), (float(r.d_group), float(r.d_cs)))
    frozen = {}
    for arm, base in FROZEN.items():
        for ds in W.DS:
            for seed in W.SEEDS:
                p = base / ds / arm / f"seed{seed}" / "final_metrics.json"
                if p.is_file():
                    m = json.loads(p.read_text(encoding="utf-8"))
                    series[(ds, f"frozen:{arm}", seed)] = (float(m["Delta_group"]),
                                                           float(m["Delta_c_s"]))
    # L5 / L6 on the tuning seeds (recompute; debt = recorded Q, frozen lambda)
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    replay_check = []
    for ds in W.DS:
        for seed in W.TUNE:
            case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
            if case is None:
                continue
            for rung, dsrc in (("L5", "zero"), ("L6", "recorded")):
                a, _, _ = L.alpha_p2_seq(case, 1.0, debt_source=dsrc)
                dg, dcs = L.endpoints(case, a)
                series[(ds, rung, seed)] = (dg, dcs)
            # stop-rule check: report-half L5 must equal v2's value (<=1e-9)
            for rung, dsrc in (("L5", "zero"), ("L6", "recorded")):
                key = (ds, rung, W.REPORT[0])
    for ds in W.DS:
        case = W.build_case(ds, "R_on", "raven_wo_use", W.REPORT[0], pi[ds])
        for rung, dsrc in (("L5", "zero"), ("L6", "recorded")):
            a, _, _ = L.alpha_p2_seq(case, 1.0, debt_source=dsrc)
            dg, dcs = L.endpoints(case, a)
            ref = series.get((ds, rung, W.REPORT[0]))
            if ref is not None:
                replay_check.append({"ds": ds, "rung": rung, "seed": W.REPORT[0],
                                     "err_group": abs(dg - ref[0]), "err_cs": abs(dcs - ref[1])})
    rc = pd.DataFrame(replay_check)
    # ---- reference gap per seed -------------------------------------------------
    fr = pd.read_csv(V2 / "FRONTIER.csv")
    fr = fr[fr.ruler == "R_on"].groupby(["ds", "seed"])[
        ["d_unif_group", "d_star_group", "d_unif_cs", "d_star_cs"]].first()

    # ---- level table ------------------------------------------------------------
    rows = []
    for (ds, tag), _ in sorted({(k[0], k[1]): 1 for k in series}.items()):
        for block, seeds in BLOCKS.items():
            vals = [series[(ds, tag, s)] for s in seeds if (ds, tag, s) in series]
            if len(vals) < 3:
                continue
            g = np.array([v[0] for v in vals])
            c = np.array([v[1] for v in vals])
            gu = np.array([fr.loc[(ds, s), "d_unif_group"] for s in seeds
                           if (ds, tag, s) in series])
            rows.append({"ds": ds, "rule": tag, "block": block, "n_seeds": len(vals),
                         "d_group": float(g.mean()), "d_cs": float(c.mean()),
                         "pp_group": float(100 * g.mean() / 2),
                         "pp_cs": float(100 * c.mean() / 2),
                         "ci_group": boot_ci(g, rng), "ci_cs": boot_ci(c, rng),
                         "paired_diff_vs_uniform_group": float((g - gu).mean()),
                         "paired_diff_vs_uniform_ci": boot_ci(g - gu, rng)})
    pd.DataFrame(rows).to_csv(OUT / "FULL_SEED_LADDER.csv", index=False)

    # ---- decisions (20 seeds primary; halves for stability) ---------------------
    dec = []
    for ds in W.DS:
        for a, b in CONTRASTS:
            rec = {"ds": ds, "contrast": f"{a} - {b}"}
            half = {}
            for block, seeds in BLOCKS.items():
                pr = [(series[(ds, a, s)][0] - series[(ds, b, s)][0],
                       series[(ds, a, s)][1] - series[(ds, b, s)][1],
                       fr.loc[(ds, s), "d_unif_group"] - fr.loc[(ds, s), "d_star_group"])
                      for s in seeds
                      if (ds, a, s) in series and (ds, b, s) in series]
                if len(pr) < 3:
                    continue
                num_g = np.array([x[0] for x in pr])
                num_c = np.array([x[1] for x in pr])
                den = np.array([x[2] for x in pr])
                ppg = -100 * num_g / 2
                lo_g, hi_g = boot_ci(ppg, rng)
                lo_c, hi_c = boot_ci(-100 * num_c / 2, rng)
                idx = np.arange(len(pr))
                dg_draws = np.array([(lambda i: num_g[i].mean() / den[i].mean())(
                    rng.choice(idx, len(idx), replace=True)) for _ in range(BOOT_N)])
                g_lo, g_hi = float(np.percentile(dg_draws, 2.5)), float(np.percentile(dg_draws, 97.5))
                try:
                    p = float(stats.wilcoxon(num_g).pvalue)
                except Exception:
                    p = float("nan")
                half[block] = {"n": len(pr), "pp_group": float(ppg.mean()), "pp_group_ci": (lo_g, hi_g),
                               "pp_cs": float((-100 * num_c / 2).mean()), "pp_cs_ci": (lo_c, hi_c),
                               "dG": float(num_g.mean() / den.mean()), "dG_ci": (g_lo, g_hi),
                               "p_wilcoxon": p,
                               "equiv": bool(g_lo >= -BAND and g_hi <= BAND),
                               "a_better_beyond_band": bool(g_hi < -BAND),
                               "practical": bool(lo_g >= PP_MIN)}
            if not half:
                continue
            primary = half.get("all20", {})
            t, r_ = half.get("tune"), half.get("report")
            unstable = False
            if t and r_:
                if np.sign(t["pp_group"]) != np.sign(r_["pp_group"]):
                    unstable = True
                cross_t = t["pp_group_ci"][0] <= 0 <= t["pp_group_ci"][1]
                cross_r = r_["pp_group_ci"][0] <= 0 <= r_["pp_group_ci"][1]
                if cross_t != cross_r:
                    unstable = True
            rec.update({"n_all20": primary.get("n"), "pp_all20": primary.get("pp_group"),
                        "pp_all20_ci": primary.get("pp_group_ci"),
                        "dG_all20": primary.get("dG"), "dG_all20_ci": primary.get("dG_ci"),
                        "p_wilcoxon_all20": primary.get("p_wilcoxon"),
                        "equiv_all20": primary.get("equiv"),
                        "a_better_beyond_band_all20": primary.get("a_better_beyond_band"),
                        "practical_pp_ge_0.5_all20": primary.get("practical"),
                        "pp_tune": None if not t else t["pp_group"],
                        "pp_report": None if not r_ else r_["pp_group"],
                        "G_tune": None if not t else t["dG"],
                        "G_report": None if not r_ else r_["dG"],
                        "split_unstable": bool(unstable)})
            dec.append(rec)
    dd = pd.DataFrame(dec)
    dd.to_csv(OUT / "FULL_SEED_DECISIONS.csv", index=False)
    summ = {"replay_check": replay_check,
            "replay_max_err": float(rc[["err_group", "err_cs"]].max().max()) if len(rc) else None,
            "replay_pass": bool(len(rc) and rc[["err_group", "err_cs"]].max().max() <= 1e-9),
            "split_unstable_rows": dd[dd.split_unstable]["contrast"].tolist() if len(dd) else [],
            "n_level_rows": len(rows), "n_decision_rows": len(dd)}
    (OUT / "FULL_SEED_SUMMARY.json").write_text(json.dumps(summ, indent=2, default=str),
                                                encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))
    cols = ["ds", "contrast", "n_all20", "pp_all20", "pp_all20_ci", "dG_all20", "dG_all20_ci",
            "equiv_all20", "a_better_beyond_band_all20", "practical_pp_ge_0.5_all20",
            "pp_tune", "pp_report", "G_tune", "G_report", "split_unstable"]
    print(dd[cols].round(5).to_string(index=False))


if __name__ == "__main__":
    main()
