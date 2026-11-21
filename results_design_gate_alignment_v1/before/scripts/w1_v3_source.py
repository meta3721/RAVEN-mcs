"""T3 (round v3): reference source + projection ladder (core), plus its internal checks.

Rules on R_on for each beta source `src`:
  B0(src): alpha = beta_src                      (not projected; outside_Cr_l1 recorded)
  B1(src): alpha = Proj_{C_r}(beta_src)          (Euclidean projection)
  B2(src): v2's L3: argmin ½||M a - mu||² + ½*1*||a - beta_src||²
  B3(src): solve_p2(debt=0, frozen lambda, beta = beta_src, V from the raven_wo_use trajectory)

Internal checks (stop T3-T6 on failure):
  1. B2(raven) == v2 L3 (report rows, eps=1.0)   <= 1e-9
  2. B3(raven) == v2 L5 (report rows, lambda_g=1.0) <= 1e-7
  3. continuity: L3(eps in {10,100,1000}) -> B1(raven)

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
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                       # noqa: E402
import w1_ladder as L                                                       # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v3"
R2 = ROOT / "results_w1_ladder/round_v2"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
SRC = {
    "raven": E3,
    "raven_simoracle": E3,
    "raven_wo_obs": E4,
    "raven_wo_use": E4,
    "raven_wo_design": E4,
    "uniform": None,
    "count": None,
}
RULES = ("B0", "B1", "B2", "B3")
CONTRASTS = (("B1:raven", "B0:raven"), ("B2:raven", "B1:raven"), ("B3:raven", "B2:raven"),
             ("B1:raven", "B1:raven_wo_design"), ("B1:raven", "B1:raven_wo_obs"),
             ("B1:raven", "B1:raven_wo_use"), ("B1:raven_simoracle", "B1:raven"),
             ("B1:raven", "B1:uniform"))
EPS_CONT = (10.0, 100.0, 1000.0)
BOOT_N, BOOT_SEED = 10_000, 20261002
MIN_SEEDS = 8


def beta_seq(case: dict, src: str, arm_act: dict | None, pi: dict) -> np.ndarray | None:
    """Concatenated beta source aligned window-by-window with the R_on case."""
    if src == "uniform":
        return np.concatenate([np.full(len(c), 1.0 / len(c)) for c in case["clients"]])
    if src == "count":
        out = []
        for j in range(case["n"]):
            u = np.asarray(case["units"][j], dtype=float)
            out.append(u / max(u.sum(), 1.0))
        return np.concatenate(out)
    out = []
    for j in range(case["n"]):
        x = arm_act.get(int(case["wids"][j]))
        if x is None:
            return None
        b = np.asarray(x["beta_hat"], dtype=float)
        if len(b) != len(case["clients"][j]):
            return None
        out.append(b)
    return np.concatenate(out)


def try_solve(fn, *a, **kw):
    """Run a solve, returning (value, None) or (None, 'solver_fail:...')."""
    try:
        return fn(*a, **kw), None
    except Exception as exc:  # noqa: BLE001
        return None, f"solver_fail:{type(exc).__name__}:{str(exc)[:60]}"


def outside_cr(case: dict, alphas: np.ndarray) -> float:
    tot, off = 0.0, 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        a = np.asarray(alphas[off:off + K], dtype=float)
        off += K
        tot += (float(np.maximum(a - case["a_bar"][j], 0.0).sum()) + abs(float(a.sum()) - 1.0)
                + max(0.0, float(a @ a) - 1.0 / case["e_bar"][j]))
    return tot


def arm_beta_map(ds: str, base: pathlib.Path, arm: str, seed: int):
    p = base / ds / arm / f"seed{seed}"
    if not (p / "window_metrics.json").is_file():
        return None
    act = W.active_windows(json.loads((p / "window_metrics.json").read_text(encoding="utf-8")))
    return {int(x["window_id"]): x for x in act}


def align_frac(case: dict, act: dict) -> float:
    ok = 0
    for j in range(case["n"]):
        x = act.get(int(case["wids"][j]))
        if x is not None and tuple(str(c) for c in x["active_clients"]) == tuple(case["clients"][j]):
            ok += 1
    return ok / max(case["n"], 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v3")
    args = ap.parse_args()
    global OUT
    OUT = ROOT / "results_w1_ladder" / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    star = pd.read_csv(R2 / "FRONTIER.csv")
    star = star[star.ruler == "R_on"].groupby(["ds", "seed"])[
        ["d_unif_group", "d_star_group", "d_unif_cs", "d_star_cs"]].first().reset_index()
    stage = pd.read_csv(R2 / "LADDER.csv")
    stage = stage[(stage["split"] == "report") & (stage["ruler"] == "R_on")]
    v2_l3 = stage[stage.rung == "L3"].set_index(["ds", "seed"])["d_group"]
    v2_l3cs = stage[stage.rung == "L3"].set_index(["ds", "seed"])["d_cs"]
    v2_l5 = stage[stage.rung == "L5"].set_index(["ds", "seed"])["d_group"]
    v2_l5cs = stage[stage.rung == "L5"].set_index(["ds", "seed"])["d_cs"]

    rows, checks, cont = [], [], []
    for ds in W.DS:
        aligned_seeds = {s: 0 for s in SRC}
        for seed in W.SEEDS:
            case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
            if case is None:
                continue
            st = star[(star.ds == ds) & (star.seed == seed)]
            du = float(st["d_unif_group"].iloc[0]) if len(st) else np.nan
            dstar = float(st["d_star_group"].iloc[0]) if len(st) else np.nan
            du_cs = float(st["d_unif_cs"].iloc[0]) if len(st) else np.nan
            dstar_cs = float(st["d_star_cs"].iloc[0]) if len(st) else np.nan
            base_beta = [np.asarray(b, dtype=float) for b in case["beta"]]
            for src, base in SRC.items():
                act = arm_beta_map(ds, base, src, seed) if base is not None else None
                frac = 1.0 if base is None else (0.0 if act is None else align_frac(case, act))
                bs = beta_seq(case, src, act, pi[ds])
                if bs is None or frac < 1.0 - 1e-12:
                    checks.append({"ds": ds, "src": src, "seed": seed, "rule": "all",
                                   "aligned_frac": frac,
                                   "status": "ruler_misaligned" if base is not None else "ok"})
                    continue
                aligned_seeds[src] += 1
                blocks, off = [], 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    blocks.append(bs[off:off + K])
                    off += K
                case["beta"] = blocks
                for rule in RULES:
                    split = "report" if seed in W.REPORT else "tune"
                    status = "ok"
                    if rule == "B0":
                        a = bs.copy()
                    elif rule == "B1":
                        a, status = try_solve(L.project_seq, case, bs)
                    elif rule == "B2":
                        a, status = try_solve(L.alpha_match, case, eps=1.0)
                    else:
                        res, status = try_solve(L.alpha_p2_seq, case, 1.0, debt_source="zero")
                        a = None if res is None else res[0]
                    if a is None:
                        rows.append({"ds": ds, "src": src, "rule": rule, "seed": seed,
                                     "split": split, "d_group": np.nan, "d_cs": np.nan,
                                     "tv_group_pp": np.nan, "tv_cs_pp": np.nan,
                                     "G_group": np.nan, "G_cs": np.nan, "outside_Cr_l1": np.nan,
                                     "aligned_frac": frac, "status": status or "solver_fail"})
                        continue
                    status = status or "ok"
                    dg, dcs = L.endpoints(case, a)
                    rows.append({"ds": ds, "src": src, "rule": rule, "seed": seed, "split": split,
                                 "d_group": dg, "d_cs": dcs,
                                 "tv_group_pp": 100 * dg / 2, "tv_cs_pp": None if dcs is None else 100 * dcs / 2,
                                 "G_group": (None if not np.isfinite(du) or du - dstar <= 0
                                             else (du - dg) / (du - dstar)),
                                 "G_cs": (None if dcs is None or not np.isfinite(du_cs) or du_cs - dstar_cs <= 0
                                          else (du_cs - dcs) / (du_cs - dstar_cs)),
                                 "outside_Cr_l1": outside_cr(case, a), "aligned_frac": frac,
                                 "status": status or "ok"})
                    key = (ds, seed)
                    if rule == "B2" and src == "raven" and key in v2_l3.index:
                        checks.append({"ds": ds, "src": src, "seed": seed, "rule": "B2_vs_v2L3",
                                       "aligned_frac": frac,
                                       "err": abs(dg - float(v2_l3.loc[key])),
                                       "err_cs": None if dcs is None else abs(dcs - float(v2_l3cs.loc[key]))})
                    if rule == "B3" and src == "raven" and key in v2_l5.index:
                        checks.append({"ds": ds, "src": src, "seed": seed, "rule": "B3_vs_v2L5",
                                       "aligned_frac": frac,
                                       "err": abs(dg - float(v2_l5.loc[key])),
                                       "err_cs": None if dcs is None else abs(dcs - float(v2_l5cs.loc[key]))})
                if src == "raven" and seed in W.SEEDS[:4]:          # continuity on a few seeds
                    for eps in EPS_CONT:
                        a, st_c = try_solve(L.alpha_match, case, eps=eps)
                        if a is None:
                            cont.append({"ds": ds, "seed": seed, "eps": eps, "d_group": np.nan,
                                         "status": st_c})
                            continue
                        dg, _ = L.endpoints(case, a)
                        cont.append({"ds": ds, "seed": seed, "eps": eps, "d_group": dg,
                                     "status": "ok"})
        for src in SRC:
            if aligned_seeds[src] < MIN_SEEDS:
                checks.append({"ds": ds, "src": src, "seed": None, "rule": "all",
                               "aligned_frac": aligned_seeds[src] / len(W.SEEDS),
                               "status": "insufficient_alignment"})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "SOURCE_LADDER.csv", index=False)
    ck = pd.DataFrame(checks)
    ck.to_csv(OUT / "SOURCE_LADDER_CHECKS.csv", index=False)

    # registered contrasts on report seeds (paired, per endpoint)
    rng = np.random.default_rng(BOOT_SEED)
    out = []
    rep = df[df["split"] == "report"]
    for ds in W.DS:
        piv = {(s, r): g.set_index("seed") for (s, r), g in rep[rep.ds == ds].groupby(["src", "rule"])}
        for ep, col in (("group", "d_group"), ("cs", "d_cs")):
            for a, b in CONTRASTS:
                sa, ra = a.split(":")
                sb, rb = b.split(":")
                if (sa, ra) not in piv or (sb, rb) not in piv:
                    out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}",
                                "status": "insufficient_alignment"})
                    continue
                va, vb = piv[(sa, ra)][col], piv[(sb, rb)][col]
                j = va.index.intersection(vb.index)
                if len(j) < MIN_SEEDS:
                    out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}",
                                "status": "insufficient_alignment", "n_seeds": int(len(j))})
                    continue
                d = (va.loc[j] - vb.loc[j]).dropna()
                arr = d.to_numpy(dtype=float)
                boots = np.array([arr[rng.choice(len(arr), len(arr), replace=True)].mean()
                                  for _ in range(BOOT_N)])
                try:
                    p = float(stats.wilcoxon(arr).pvalue)
                except Exception:
                    p = float("nan")
                out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}", "status": "ok",
                            "n_seeds": int(len(arr)), "mean_diff": float(arr.mean()),
                            "ci_lo": float(np.percentile(boots, 2.5)),
                            "ci_hi": float(np.percentile(boots, 97.5)), "p_wilcoxon": p,
                            "pp": float(100 * arr.mean() / 2)})
    pd.DataFrame(out).to_csv(OUT / "SOURCE_LADDER_CONTRASTS.csv", index=False)
    if cont:
        pd.DataFrame(cont).to_csv(OUT / "SOURCE_LADDER_CONTINUITY.csv", index=False)
    errB2 = ck[ck["rule"] == "B2_vs_v2L3"]["err"] if "rule" in ck.columns else pd.Series(dtype=float)
    errB3 = ck[ck["rule"] == "B3_vs_v2L5"]["err"] if "rule" in ck.columns else pd.Series(dtype=float)
    summ = {
        "rows": int(len(df)),
        "aligned_seeds_per_src": {f"{d}|{s}": int(df[(df.ds == d) & (df.src == s)]["seed"].nunique())
                                  for d in W.DS for s in SRC},
        "check_max_err_B2_vs_v2L3": None if not len(errB2) else float(errB2.max()),
        "check_max_err_B3_vs_v2L5": None if not len(errB3) else float(errB3.max()),
        "check_pass": bool(len(errB2) and errB2.max() <= 1e-9 and len(errB3) and errB3.max() <= 1e-7),
        "insufficient_alignment": (ck[ck["status"] == "insufficient_alignment"][["ds", "src"]]
                                   .to_dict("records") if "status" in ck.columns else []),
    }
    (OUT / "SOURCE_LADDER.json").write_text(json.dumps(summ, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))
    c = pd.read_csv(OUT / "SOURCE_LADDER_CONTRASTS.csv")
    print(c[c.status == "ok"][["ds", "endpoint", "contrast", "n_seeds", "mean_diff", "ci_lo",
                              "ci_hi", "pp"]].round(6).to_string(index=False))


if __name__ == "__main__":
    main()
