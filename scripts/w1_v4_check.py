"""Part B checks and trade-off table (round v4).

B-G1: every new run's per-window active_clients equals R_on's
B-G2: uniform_window / proj_beta structural endpoints equal the A1 read-only replays
      (uniform -> Delta_unif; proj_beta -> SOURCE_LADDER src=raven rule=B1) per seed, <= 1e-9
B-G3: proj_beta_debt equals A2's read-only value at the same kappa, <= 1e-9

Outputs: TRAIN_GATES.csv, TRADEOFF.csv, TRADEOFF_PAIRED.csv, TRAIN_SUMMARY.json
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

OUT = ROOT / "results_w1_ladder/round_v4"
TRAIN = OUT / "train/v4/C0_frozen"
V2 = ROOT / "results_w1_ladder/round_v2"
V3 = ROOT / "results_w1_ladder/round_v3"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
ARMS = ("uniform_window", "proj_beta", "proj_beta_debt")
FROZEN = ("fedavg_window", "inst_cal", "raven")
BOOT_N, BOOT_SEED = 10_000, 20261002
TAIL_KEYS = ("RMSE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho", "WorstGroupRMSE")


def load(ds: str, arm: str, seed: int, base: pathlib.Path | None = None) -> dict | None:
    p = (base or TRAIN) / ds / arm / f"seed{seed}" / "final_metrics.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    fr = pd.read_csv(V2 / "FRONTIER.csv")
    fr = fr[fr.ruler == "R_on"].groupby(["ds", "seed"])[
        ["d_unif_group", "d_unif_cs", "d_star_group", "d_star_cs"]].first()
    src = pd.read_csv(V3 / "SOURCE_LADDER.csv")
    src = src[(src.src == "raven") & (src["status"].isna() | (src["status"] == "ok"))]
    b1 = src[src.rule == "B1"].set_index(["ds", "seed"])
    a2 = pd.read_csv(OUT / "DEBT_STRENGTH_V4.csv")
    a2 = a2[np.isclose(a2.kappa, 1000.0)].set_index(["ds", "seed"])
    gates, rows = [], []
    for ds in W.DS:
        for arm in ARMS:
            for seed in W.SEEDS:
                m = load(ds, arm, seed)
                if m is None:
                    gates.append({"ds": ds, "arm": arm, "seed": seed, "gate": "missing_run"})
                    continue
                wm = json.loads((TRAIN / ds / arm / f"seed{seed}" / "window_metrics.json")
                                .read_text(encoding="utf-8"))
                act = W.active_windows(wm)
                ref = W.active_windows(json.loads((E3 / ds / "raven" / f"seed{seed}" /
                                                   "window_metrics.json").read_text(encoding="utf-8")))
                ok_sets = len(act) == len(ref) and all(
                    tuple(str(c) for c in x["active_clients"]) == tuple(str(c) for c in y["active_clients"])
                    for x, y in zip(act, ref))
                g1 = bool(ok_sets and len(act) == int(m.get("S_R", len(act))))
                dg, dc = float(m["Delta_group"]), float(m["Delta_c_s"])
                exp_g = exp_c = None
                if arm == "uniform_window":
                    exp_g, exp_c = float(fr.loc[(ds, seed), "d_unif_group"]), float(fr.loc[(ds, seed), "d_unif_cs"])
                elif arm == "proj_beta":
                    exp_g, exp_c = float(b1.loc[(ds, seed), "d_group"]), float(b1.loc[(ds, seed), "d_cs"])
                elif arm == "proj_beta_debt":
                    exp_g, exp_c = float(a2.loc[(ds, seed), "d_group"]), float(a2.loc[(ds, seed), "d_cs"])
                gates.append({"ds": ds, "arm": arm, "seed": seed, "gate": "B-G1",
                              "active_clients_match": g1, "n_windows": len(act),
                              "B-G2/3_expected_group": exp_g, "B-G2/3_expected_cs": exp_c,
                              "observed_group": dg, "observed_cs": dc,
                              "err_group": None if exp_g is None else abs(dg - exp_g),
                              "err_cs": None if exp_c is None else abs(dc - exp_c),
                              "pass": bool(g1 and exp_g is not None and abs(dg - exp_g) <= 1e-9
                                           and abs(dc - exp_c) <= 1e-9)})
                rows.append({"ds": ds, "arm": arm, "seed": seed, **{k: m.get(k) for k in TAIL_KEYS},
                             "Delta_group": dg, "Delta_c_s": dc,
                             "pp_group": 100 * dg / 2, "pp_cs": 100 * dc / 2,
                             "runtime_seconds": m.get("runtime_seconds")})
        for arm in FROZEN:
            for seed in W.SEEDS:
                m = load(ds, arm, seed, base=E3)
                if m is None:
                    continue
                rows.append({"ds": ds, "arm": arm, "seed": seed, **{k: m.get(k) for k in TAIL_KEYS},
                             "Delta_group": float(m["Delta_group"]), "Delta_c_s": float(m["Delta_c_s"]),
                             "pp_group": 100 * float(m["Delta_group"]) / 2,
                             "pp_cs": 100 * float(m["Delta_c_s"]) / 2,
                             "runtime_seconds": m.get("runtime_seconds")})
    g = pd.DataFrame(gates)
    g.to_csv(OUT / "TRAIN_GATES.csv", index=False)
    tr = pd.DataFrame(rows)
    tr.to_csv(OUT / "TRADEOFF.csv", index=False)
    # paired comparisons per dataset x endpoint
    rng = np.random.default_rng(BOOT_SEED)
    pairs = (("proj_beta", "uniform_window"), ("raven", "proj_beta"),
             ("proj_beta", "fedavg_window"), ("uniform_window", "fedavg_window"),
             ("proj_beta_debt", "proj_beta"))
    out = []
    for ds in W.DS:
        for ep in TAIL_KEYS + ("Delta_group", "Delta_c_s"):
            for a, b in pairs:
                va = tr[(tr.ds == ds) & (tr.arm == a)].set_index("seed")[ep].dropna()
                vb = tr[(tr.ds == ds) & (tr.arm == b)].set_index("seed")[ep].dropna()
                j = va.index.intersection(vb.index)
                if len(j) < 5:
                    out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}",
                                "status": "missing"})
                    continue
                d = (va.loc[j] - vb.loc[j]).to_numpy(dtype=float)
                boots = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                                  for _ in range(BOOT_N)])
                try:
                    p = float(stats.wilcoxon(d).pvalue)
                except Exception:
                    p = float("nan")
                out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}", "status": "ok",
                            "n_seeds": int(len(d)), "mean_diff": float(d.mean()),
                            "ci_lo": float(np.percentile(boots, 2.5)),
                            "ci_hi": float(np.percentile(boots, 97.5)),
                            "pp_diff": float(-100 * d.mean() / 2), "p_wilcoxon": p})
    pa = pd.DataFrame(out)
    pa.to_csv(OUT / "TRADEOFF_PAIRED.csv", index=False)
    summ = {"gates_rows": int(len(g)),
            "B-G1_pass": int(g["active_clients_match"].sum()) if "active_clients_match" in g else 0,
            "B-G2_3_pass": int(g["pass"].sum()) if "pass" in g else 0,
            "B-G2_3_evaluated": int(g["pass"].notna().sum()) if "pass" in g else 0,
            "max_err_group": None if not len(g) or g["err_group"].isna().all() else float(g["err_group"].max()),
            "max_err_cs": None if not len(g) or g["err_cs"].isna().all() else float(g["err_cs"].max()),
            "arms_present": sorted(tr.arm.unique()),
            "n_runs": int(len(tr))}
    if len(tr):
        piv = tr[tr.arm.isin(list(ARMS) + list(FROZEN))].groupby(["ds", "arm"])[
            ["RMSE_mu", "Delta_group", "Delta_c_s", "runtime_seconds"]].mean().round(5)
        summ["means"] = {"|".join(str(x) for x in k): v for k, v in piv.to_dict("index").items()}
    (OUT / "TRAIN_SUMMARY.json").write_text(json.dumps(summ, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))
    if len(pa):
        print(pa[pa.status == "ok"].round(5).to_string(index=False))


if __name__ == "__main__":
    main()
