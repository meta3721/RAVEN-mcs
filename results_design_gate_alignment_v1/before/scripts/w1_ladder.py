"""W1 necessity ladder — Phase 4 driver (read-only replay).

Protocol: raven-mcs-w1-ladder-frontier-execution-prompt.md (attachment, sha256 a26c6388…), Phase 4.
Preregistration: results_w1_ladder/round_v2/PREREG.md (sha256 48fc1f3f…).

Rungs (all on one ruler, same active set, same mu, same beta_hat_r):
  L0 Uniform        alpha = 1/K                                       (exact)
  L1 Count          alpha ∝ raw_counts, projected onto C_r            (input reconstructed)
  L2 Target reweight  needs payload.total_masses -> input_unavailable (see report)
  L3 Target match   argmin_{C_r} ½||M a - mu||² + ½ eps ||a - beta||² (exact)
  L4 Match+variance L3 + ½ lam_v aᵀV a                                (open_loop_V)
  L5 Full P2 (debt=0), lambda_g grid                                  (exact)
  L6 Full P2 (debt=Q_r), Q propagated by the rung's own alpha         (exact)
  L4' Sequential debt matching: P2 with lam_beta=1e-8, lam_v=lam_s=0  (exact)

Writes only inside results_w1_ladder/round_v2/.  No training, no src/ edits.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import cvxpy as cp
import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                                   # noqa: E402
from raven_mcs.aggregation.p2_cvxpy import solve_p2                                     # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v2"
PRIMARY_RULER = "R_on"
# R_on ruler source: the debt-bearing Design-on arm.  G1 (round_v2) verified that
# M and w_atomic are identical across the state-bearing Design-on arms, so this is the
# same ruler; unlike raven_wo_debt it carries a non-zero recorded debt trajectory, which
# L6/L4' need as an open-loop input (see G5 / the debt-rule diagnostics).
RULERS = (("R_on", "raven_wo_use"),)
EPS_GRID = (1e-8, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1.0)
LAMV_GRID = (0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
LAMG_GRID = (1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 13.0)
G5_ALPHA_TOL, G5_ENDPOINT_TOL = 1e-6, 1e-7
BOOT_N, BOOT_SEED = 10_000, 20261002
TAU_NEAR, TAU_EQ, TAU_NEC = 0.80, 0.10, 0.10
ALPHA_MAX, E_MIN, MAX_SLR, P2_TOL = 0.5, 3.0, 1.0, 1e-6
GRID_RUNGS = {"L3": EPS_GRID, "L4": LAMV_GRID, "L5": LAMG_GRID, "L6": LAMG_GRID, "L4p": LAMG_GRID}
SIMPLE_RUNGS = ("L0", "L1", "L3", "L4", "L4p")
CONTRASTS = (("L6", "L5"), ("L5", "L3"), ("L3", "L2"), ("L5", "L4p"), ("L6", "BEST_SIMPLE"))

_cases: dict = {}
_qp: dict = {}


def load_case(d: str, ruler: str, src: str, seed: int, pi: dict):
    key = (d, ruler, seed)
    if key not in _cases:
        _cases[key] = W.build_case(d, ruler, src, seed, pi)
    return _cases[key]


def project_seq(case: dict, v: np.ndarray) -> np.ndarray:
    """Euclidean projection of each window block onto C_r."""
    out, off = [], 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        key = ("proj", K)
        if key not in _qp:
            par = cp.Parameter(K)
            ab = cp.Parameter(nonneg=True)
            eb = cp.Parameter(nonneg=True)
            a = cp.Variable(K)
            pr = cp.Problem(cp.Minimize(cp.sum_squares(a - par)),
                            [cp.sum(a) == 1.0, a >= 0.0, a <= ab,
                             cp.sum_squares(a) <= 1.0 / eb])
            _qp[key] = (par, ab, eb, a, pr)
        par, ab, eb, a, pr = _qp[key]
        par.value = np.asarray(v[off:off + K], dtype=float)
        ab.value = float(case["a_bar"][j])
        eb.value = float(case["e_bar"][j])
        pr.solve(solver=cp.CLARABEL, verbose=False)
        out.append(np.asarray(a.value, dtype=float).clip(0.0, None))
        off += K
    return np.concatenate(out)


def alpha_uniform(case: dict) -> np.ndarray:
    return np.concatenate([np.full(len(c), 1.0 / len(c)) for c in case["clients"]])


def alpha_count(case: dict) -> np.ndarray:
    """L1: alpha ∝ raw_counts, projected onto C_r.

    raw_counts is not persisted by the frozen runs (built in-memory at
    window_runner.py:1063); reconstructed as the number of atomic-unit rows the client
    holds in that window's c-s state.  Every (window, client) block has uniform
    w_atomic = 1/units and sums to exactly 1 (verified), so units = 1/w_atomic.
    """
    v, off = [], 0
    for j in range(case["n"]):
        u = np.asarray(case["units"][j], dtype=float)
        v.append(u / max(u.sum(), 1.0))
        off += len(u)
    return project_seq(case, np.concatenate(v))


def alpha_match(case: dict, eps: float, lam_v: float = 0.0) -> np.ndarray:
    """L3/L4: per-window QP with parameters (M, beta, V)."""
    out, off = [], 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        key = ("match", case["G"], K)
        if key not in _qp:
            Mp = cp.Parameter((case["G"], K))
            bp = cp.Parameter(K)
            Vp = cp.Parameter(K, nonneg=True)
            ep = cp.Parameter(nonneg=True)
            lv = cp.Parameter(nonneg=True)
            ab = cp.Parameter(nonneg=True)
            eb = cp.Parameter(nonneg=True)
            a = cp.Variable(K)
            obj = (0.5 * cp.sum_squares(Mp @ a - case["mu"])
                   + 0.5 * ep * cp.sum_squares(a - bp)
                   + 0.5 * lv * cp.sum(cp.multiply(Vp, cp.square(a))))
            pr = cp.Problem(cp.Minimize(obj),
                            [cp.sum(a) == 1.0, a >= 0.0, a <= ab,
                             cp.sum_squares(a) <= 1.0 / eb])
            _qp[key] = (Mp, bp, Vp, ep, lv, ab, eb, a, pr)
        Mp, bp, Vp, ep, lv, ab, eb, a, pr = _qp[key]
        Mp.value = case["M"][j]
        bp.value = case["beta"][j]
        Vp.value = np.maximum(case["variance"][j], 0.0)
        ep.value = float(eps)
        lv.value = float(lam_v)
        ab.value = float(case["a_bar"][j])
        eb.value = float(case["e_bar"][j])
        pr.solve(solver=cp.CLARABEL, verbose=False)
        out.append(np.asarray(a.value, dtype=float).clip(0.0, None))
        off += K
    return np.concatenate(out)


def alpha_p2_seq(case: dict, lam_g: float, *, lam_beta: float | None = None,
                 lam_v: float | None = None, lam_s: float | None = None,
                 debt_source: str = "zero"):
    """L5/L6/L4': per-window solve_p2.

    debt_source="zero"     -> debt = 0                          (L5)
    debt_source="recorded" -> debt = the run's recorded Q_r     (L6, L4'; open_loop_Q)

    The protocol's Q_{r+1}=[Q_r+eta(mu-M_r alpha_r)]_+ propagation is *not* used: G5 and
    scripts/w1_debt_rule_diag.py show no constant eta reproduces the recorded trajectory
    (best-fit eta 0.002-0.011, residual 3.9e-3), while the recorded Q reproduces alpha to 2e-10.
    """
    lams = case["lambdas"]
    lb = float(lams["beta"] if lam_beta is None else lam_beta)
    lv = float(lams["variance"] if lam_v is None else lam_v)
    ls = float(lams["staleness"] if lam_s is None else lam_s)
    alphas, times, warns = [], [], 0
    G = case["G"]
    for j in range(case["n"]):
        debt = np.asarray(case["debt"][j], dtype=float) if debt_source == "recorded" else np.zeros(G)
        res = solve_p2(
            coverage_matrix=case["M"][j], mu=case["mu"], beta_reference=case["beta"][j],
            debt=debt, variance_diag=case["variance"][j], staleness=case["staleness"][j],
            lambda_group=float(lam_g), lambda_beta=lb, lambda_variance=lv,
            lambda_staleness=ls, alpha_max=ALPHA_MAX, e_min=E_MIN,
            max_server_learning_rate=MAX_SLR, tolerance=P2_TOL, backend="CLARABEL",
            instant_calibration=True)
        a = np.asarray(res.alpha, dtype=float)
        alphas.append(a)
        times.append(float(res.solve_time_s))
        if res.fallback_used or res.feasibility_repair_used or res.status != "optimal":
            warns += 1
    return np.concatenate(alphas), times, warns


def endpoints(case: dict, alphas: np.ndarray) -> tuple:
    mats = case["M"]
    blocks, off = [], 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        blocks.append(np.asarray(alphas[off:off + K], dtype=float))
        off += K
    dg = W.delta_group(mats, blocks, case["mu"])
    amap = {case["wids"][j]: {c: float(blocks[j][i])
                              for i, c in enumerate(case["clients"][j])}
            for j in range(case["n"])}
    dcs = W.delta_cs(case["pair_state"], amap, case["n"], case["pi_tar"])
    return float(dg), (None if dcs is None else float(dcs))


def split_blocks(case: dict, alphas: np.ndarray) -> list:
    blocks, off = [], 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        blocks.append(np.asarray(alphas[off:off + K], dtype=float))
        off += K
    return blocks


def g5_checks(pi: dict, datasets=W.DS) -> pd.DataFrame:
    """G5: replay with frozen lambda and each rung's own inputs.

    L5 anchor: debt = 0, states of the debt-free full-P2 arm raven_wo_debt (== inst_cal policy).
    L6 anchor: debt = the arm's recorded Q_r (open_loop_Q), states of the debt-bearing arms.
    """
    rows = []
    for d in datasets:
        for arm, mode, src in (("raven_wo_debt", "L5_zerodebt", "zero"),
                               ("raven_wo_use", "L6_openloopQ", "recorded"),
                               ("raven_wo_obs", "L6_openloopQ", "recorded")):
            for seed in W.SEEDS:
                case = W.build_case(d, "R_on", arm, seed, pi[d])
                if case is None:
                    continue
                lam_g = float(case["lambdas"]["group"])
                a_seq, _, _ = alpha_p2_seq(case, lam_g, debt_source=src)
                linf = float(np.max(np.abs(a_seq - case["alpha_arm"])))
                dg_replay = W.delta_group(case["M"], split_blocks(case, a_seq), case["mu"])
                dg_frozen = float(json.loads((W.E4 / d / arm / f"seed{seed}" /
                                              "final_metrics.json").read_text())["Delta_group"])
                rows.append({"dataset": d, "arm": arm, "mode": mode, "seed": seed,
                             "lambda_group": lam_g, "alpha_linf": linf,
                             "debt_max_l1": float(np.max([np.abs(x).sum() for x in case["debt"]])),
                             "endpoint_absdiff": abs(dg_replay - dg_frozen),
                             "pass": bool(linf <= G5_ALPHA_TOL and
                                          abs(dg_replay - dg_frozen) <= G5_ENDPOINT_TOL)})
    return pd.DataFrame(rows)


def run_ladder(pi: dict, datasets=W.DS) -> tuple:
    rows, sel_rows = [], []
    for d in datasets:
        for ruler, src in RULERS:
            # ---------- tuning ----------
            scores: dict = {}
            for seed in W.TUNE:
                case = load_case(d, ruler, src, seed, pi[d])
                if case is None:
                    continue
                for rung, a in (("L0", alpha_uniform(case)), ("L1", alpha_count(case))):
                    g, c = endpoints(case, a)
                    scores.setdefault((rung, "none"), []).append((g, c))
                eps_star = None
                for rung, grid in GRID_RUNGS.items():
                    for cfg in grid:
                        if rung == "L3":
                            a, warns = alpha_match(case, eps=cfg), 0
                        elif rung == "L4":
                            a, warns = alpha_match(case, eps=eps_star if eps_star else EPS_GRID[0],
                                                   lam_v=cfg), 0
                        elif rung == "L5":
                            a, _, warns = alpha_p2_seq(case, cfg, debt_source="zero")
                        elif rung == "L6":
                            a, _, warns = alpha_p2_seq(case, cfg, debt_source="recorded")
                        else:  # L4p
                            a, _, warns = alpha_p2_seq(case, cfg, lam_beta=1e-8,
                                                          lam_v=0.0, lam_s=0.0, debt_source="recorded")
                        g, c = endpoints(case, a)
                        scores.setdefault((rung, cfg), []).append((g, c))
                    if rung == "L3":  # freeze L3's eps for L4
                        eps_star = min(((cfg, float(np.mean([g for g, _ in scores[(rung, cfg)]])))
                                        for cfg in grid), key=lambda kv: kv[1])[0]
            for (rung, cfg), vals in scores.items():
                arr = np.asarray(vals, dtype=float)
                sel_rows.append({"ds": d, "ruler": ruler, "rung": rung, "config": str(cfg),
                                 "split": "tune", "mean_d_group": float(arr[:, 0].mean()),
                                 "mean_d_cs": float(arr[:, 1].mean()),
                                 "mean_sum": float(arr.sum(axis=1).mean()), "n": len(vals)})
            chosen, chosen_sum = {}, {}
            for rung in GRID_RUNGS:
                cands = {cfg: float(np.mean([g for g, _ in scores[(rung, cfg)]]))
                         for cfg in GRID_RUNGS[rung]}
                chosen[rung] = min(cands.items(), key=lambda kv: kv[1])[0]
                cands2 = {cfg: float(np.mean([g + c for g, c in scores[(rung, cfg)]]))
                          for cfg in GRID_RUNGS[rung]}
                chosen_sum[rung] = min(cands2.items(), key=lambda kv: kv[1])[0]
            for rung in ("L0", "L1"):
                sel_rows.append({"ds": d, "ruler": ruler, "rung": rung, "config": "none",
                                 "split": "tune", "mean_d_group": float(np.mean([g for g, _ in
                                                                                 scores[(rung, "none")]])),
                                 "mean_d_cs": float(np.mean([c for _, c in scores[(rung, "none")]])),
                                 "mean_sum": float(np.mean([g + c for g, c in scores[(rung, "none")]])),
                                 "n": len(scores[(rung, "none")])})
            # record the configurations actually carried to the report split (no leakage)
            for rung, cfg in list(chosen.items()) + [("L0", "none"), ("L1", "none")]:
                vals = scores[(rung, "none" if cfg == "none" else cfg)]
                sel_rows.append({"ds": d, "ruler": ruler, "rung": rung, "config": str(cfg),
                                 "split": "chosen", "mean_d_group": float(np.mean([g for g, _ in vals])),
                                 "mean_d_cs": float(np.mean([c for _, c in vals])),
                                 "mean_sum": float(np.mean([g + c for g, c in vals])),
                                 "n": len(vals)})
            # ---------- report ----------
            for seed in W.REPORT:
                case = load_case(d, ruler, src, seed, pi[d])
                if case is None:
                    continue
                for rung in ("L0", "L1"):
                    a = alpha_uniform(case) if rung == "L0" else alpha_count(case)
                    g, c = endpoints(case, a)
                    rows.append(_row(d, ruler, rung, "none", "report", seed, g, c, [], 0, "exact"))
                rows.append(_row(d, ruler, "L2", "rho_min_grid", "report", seed, np.nan, np.nan,
                                 [], 0, "input_unavailable"))
                for rung, cfg in chosen.items():
                    ts = []
                    if rung == "L3":
                        a, warns, ex = alpha_match(case, eps=cfg), 0, "exact"
                    elif rung == "L4":
                        a, warns, ex = alpha_match(case, eps=float(eps_star), lam_v=cfg), 0, "open_loop_V"
                    elif rung == "L5":
                        a, ts, warns = alpha_p2_seq(case, cfg, debt_source="zero")
                        ex = "exact"
                    elif rung == "L6":
                        a, ts, warns = alpha_p2_seq(case, cfg, debt_source="recorded")
                        ex = "exact"
                    else:
                        a, ts, warns = alpha_p2_seq(case, cfg, lam_beta=1e-8, lam_v=0.0,
                                                       lam_s=0.0, debt_source="recorded")
                        ex = "exact"
                    g, c = endpoints(case, a)
                    rows.append(_row(d, ruler, rung, str(cfg), "report", seed, g, c, ts, warns, ex))
                # second, parallel selection rule: minimise mean(d_group + d_cs) on tune seeds
                for rung, cfg in chosen_sum.items():
                    if cfg == chosen[rung]:
                        continue
                    ts = []
                    if rung == "L3":
                        a, warns, ex = alpha_match(case, eps=cfg), 0, "exact"
                    elif rung == "L4":
                        a, warns, ex = alpha_match(case, eps=float(eps_star), lam_v=cfg), 0, "open_loop_V"
                    elif rung == "L5":
                        a, ts, warns = alpha_p2_seq(case, cfg, debt_source="zero")
                        ex = "exact"
                    elif rung == "L6":
                        a, ts, warns = alpha_p2_seq(case, cfg, debt_source="recorded")
                        ex = "exact"
                    else:
                        a, ts, warns = alpha_p2_seq(case, cfg, lam_beta=1e-8, lam_v=0.0,
                                                       lam_s=0.0, debt_source="recorded")
                        ex = "exact"
                    g, c = endpoints(case, a)
                    rows.append(_row(d, ruler, rung, f"{cfg}", "report_sum", seed, g, c, ts,
                                     warns, ex))
    return pd.DataFrame(rows), pd.DataFrame(sel_rows)


def _row(d, ruler, rung, cfg, split, seed, g, c, times, warns, exactness) -> dict:
    return {"ds": d, "ruler": ruler, "rung": rung, "config": cfg, "split": split, "seed": seed,
            "d_group": g, "d_cs": c,
            "solve_ms_median": float(np.median(times) * 1e3) if times else None,
            "solve_ms_p95": float(np.percentile(times, 95) * 1e3) if times else None,
            "warnings": int(warns), "exactness": exactness}


def paired_stats(ladder: pd.DataFrame) -> pd.DataFrame:
    fr = pd.read_csv(OUT / "FRONTIER.csv")
    star = fr.groupby(["ds", "ruler", "seed"])[["d_star_group", "d_star_cs", "d_unif_group",
                                                "d_unif_cs"]].first().reset_index()
    lat = ladder[ladder["split"] == "report"].merge(star, on=["ds", "ruler", "seed"], how="left")
    for F, starc, unifc in (("group", "d_star_group", "d_unif_group"),
                            ("cs", "d_star_cs", "d_unif_cs")):
        dcol = "d_" + F
        lat[f"G_{F}"] = np.where(lat[unifc] - lat[starc] > 0,
                                 (lat[unifc] - lat[dcol]) / (lat[unifc] - lat[starc]), np.nan)
    out = []
    rng = np.random.default_rng(BOOT_SEED)
    for (d, ruler), g in lat.groupby(["ds", "ruler"]):
        piv = {rung: g[g["rung"] == rung].set_index("seed") for rung in
               ("L0", "L1", "L3", "L4", "L5", "L6", "L4p")}
        for F in ("group", "cs"):
            dcol, gcol = "d_" + F, "G_" + F
            series = {r: p[dcol] for r, p in piv.items() if len(p)}
            # strongest simple rung: chosen on the tuning split only (no report-seed leakage)
            sel = pd.read_csv(OUT / "LADDER_SELECTION.csv")
            sub = sel[(sel.ds == d) & (sel.ruler == ruler) & (sel.split == "chosen")]
            means = dict(zip(sub["rung"], sub["mean_d_group"]))
            simple_present = [r for r in SIMPLE_RUNGS if r in series and r in means]
            best_simple = (min(simple_present, key=lambda r: float(means[r]))
                           if simple_present else "L0")
            for (a, b) in CONTRASTS:
                bb = best_simple if b == "BEST_SIMPLE" else b
                if a not in series or bb not in series:
                    out.append({"ds": d, "ruler": ruler, "endpoint": F, "contrast": f"{a}-{b}",
                                "n_pairs": 0, "status": "NA_input_unavailable"
                                if bb == "L2" else "NA_rung_missing"})
                    continue
                diff = (series[a] - series[bb]).dropna()
                if len(diff) < 3:
                    out.append({"ds": d, "ruler": ruler, "endpoint": F, "contrast": f"{a}-{b}",
                                "n_pairs": int(len(diff)), "status": "NA_too_few_pairs"})
                    continue
                arr = diff.to_numpy(dtype=float)
                boot = np.array([rng.choice(arr, size=len(arr), replace=True).mean()
                                 for _ in range(BOOT_N)])
                lo, hi = np.percentile(boot, [2.5, 97.5])
                try:
                    p = float(stats.wilcoxon(arr).pvalue)
                except Exception:
                    p = float("nan")
                gdiff = None
                if gcol in piv[a].columns and gcol in piv[bb].columns:
                    gdiff = float((piv[a][gcol] - piv[bb][gcol]).dropna().mean())
                out.append({"ds": d, "ruler": ruler, "endpoint": F, "contrast": f"{a}-{bb}",
                            "n_pairs": int(len(arr)), "mean_diff": float(arr.mean()),
                            "ci_lo": float(lo), "ci_hi": float(hi),
                            "p_wilcoxon": p, "mean_G_diff": gdiff, "status": "ok"})
    df = pd.DataFrame(out)
    # Holm over the registered family (2 ds x 2 endpoints x 5 contrasts = 20; 4 are NA)
    ok = df["status"] == "ok"
    pv = df.loc[ok, "p_wilcoxon"].to_numpy(dtype=float)
    order = np.argsort(pv)
    holm = np.empty_like(pv)
    m = len(pv)
    running = 0.0
    for rank, idx in enumerate(order):
        adj = min(1.0, (m - rank) * pv[idx])
        running = max(running, adj)
        holm[idx] = running
    df.loc[ok, "p_holm"] = holm
    df["family_registered_size"] = 20
    df["family_computed_size"] = m
    return df, lat


def decisions(paired: pd.DataFrame) -> pd.DataFrame:
    """Apply the prereg decision table literally (both unit readings are reported)."""
    rows = []
    for (d, ep), g in paired[paired.ruler == PRIMARY_RULER].groupby(["ds", "endpoint"]):
        def get(name):
            s = g[g["contrast"] == name]
            return None if not len(s) or s.iloc[0]["status"] != "ok" else s.iloc[0]
        r65, r53, r32, r54p = get("L6-L5"), get("L5-L3"), get("L3-L2"), get("L5-L4p")
        verdict = "结果不足以区分"
        if r65 is not None and abs(r65["mean_diff"]) <= TAU_EQ and r65["ci_lo"] >= -TAU_EQ and r65["ci_hi"] <= TAU_EQ:
            verdict = "debt 对结构端点无独立贡献（区间落在 ±τ_eq 内）；debt 只保留为可审计记账"
        elif r53 is not None and abs(r53["mean_diff"]) <= TAU_EQ and r53["ci_lo"] >= -TAU_EQ and r53["ci_hi"] <= TAU_EQ:
            verdict = "结构收益来自“在 C_r 内做目标匹配”；P2 的其余项不是必要的"
        rows.append({"ds": d, "endpoint": ep, "ruler": PRIMARY_RULER, "verdict": verdict,
                     "L6-L5": None if r65 is None else round(r65["mean_diff"], 5),
                     "L6-L5_ci": None if r65 is None else [round(r65["ci_lo"], 5), round(r65["ci_hi"], 5)],
                     "L5-L3": None if r53 is None else round(r53["mean_diff"], 5),
                     "L5-L3_ci": None if r53 is None else [round(r53["ci_lo"], 5), round(r53["ci_hi"], 5)],
                     "L3-L2": "NA_input_unavailable",
                     "L5-L4p": None if r54p is None else round(r54p["mean_diff"], 5)})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="ladder", choices=["ladder", "stats", "both"])
    ap.add_argument("--round", default="round_v2")
    ap.add_argument("--datasets", default="sensorscope,uair")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    global OUT
    OUT = ROOT / "results_w1_ladder" / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    dss = tuple(x for x in args.datasets.split(",") if x)
    sfx = f"_part_{args.tag}" if args.tag else ""
    pi = {d: W.pi_tar_for(d) for d in dss}

    if args.phase in ("ladder", "both"):
        g5 = g5_checks(pi, dss)
        g5.to_csv(OUT / f"G5_REPLAY_CHECK{sfx}.csv", index=False)
        print("G5 rows", len(g5), "pass", int(g5["pass"].sum()),
              "max alpha_linf", float(g5["alpha_linf"].max()),
              "max endpoint diff", float(g5["endpoint_absdiff"].max()))
        ladder, sel = run_ladder(pi, dss)
        ladder.to_csv(OUT / f"LADDER{sfx}.csv", index=False)
        sel.to_csv(OUT / f"LADDER_SELECTION{sfx}.csv", index=False)
        print("ladder rows", len(ladder), "selection rows", len(sel))

    if args.phase in ("stats", "both"):
        parts = sorted(OUT.glob("LADDER_part_*.csv"))
        selparts = sorted(OUT.glob("LADDER_SELECTION_part_*.csv"))
        if len(parts) > 1:
            ladder = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
            sel = pd.concat([pd.read_csv(p) for p in selparts], ignore_index=True)
            ladder.to_csv(OUT / "LADDER.csv", index=False)
            sel.to_csv(OUT / "LADDER_SELECTION.csv", index=False)
        elif len(parts) == 1:
            pd.read_csv(parts[0]).to_csv(OUT / "LADDER.csv", index=False)
            pd.read_csv(selparts[0]).to_csv(OUT / "LADDER_SELECTION.csv", index=False)
        elif (OUT / "LADDER.csv").is_file():
            ladder = pd.read_csv(OUT / "LADDER.csv")
        else:
            raise SystemExit("no ladder parts found")
        ladder = pd.read_csv(OUT / "LADDER.csv")
        g5s = sorted(OUT.glob("G5_REPLAY_CHECK_part_*.csv"))
        if g5s:
            g5 = pd.concat([pd.read_csv(p) for p in g5s], ignore_index=True)
            g5 = g5.drop_duplicates(subset=["dataset", "arm", "mode", "seed"])
            g5.to_csv(OUT / "G5_REPLAY_CHECK.csv", index=False)
            print("G5 merged rows", len(g5), "pass", int(g5["pass"].sum()),
                  "max alpha_linf", float(g5["alpha_linf"].max()))
        paired, lat = paired_stats(ladder)
        paired.to_csv(OUT / "LADDER_PAIRED.csv", index=False)
        dec = decisions(paired)
        dec.to_csv(OUT / "LADDER_DECISIONS.csv", index=False)
        lat.to_csv(OUT / "LADDER_REPORT_SEEDS.csv", index=False)
        print("paired rows", len(paired))
        print(paired.to_string())
        print(dec.to_string())


if __name__ == "__main__":
    main()
