#!/usr/bin/env python3
"""S1/S2/F driver for the NSW-Traffic new-block round.

Instruction: raven-mcs-new-block-traffic-execution-prompt.md
  sha256 25f580aa4e2824daa931addab39eadee67319a24fc89c11ce7f2cf9aa552bb36

Stages
  s1     learnability ladder (N3): fedavg_window, local_steps in {2,5,10,20},
         seeds 30001-30003, 12 runs.  Selects L*.          -> S1_LADDER.csv, S1_VERDICT.json
  s2     headroom (N4) and decision screen: fedavg_window, raven_simoracle,
         central_delivered, seeds 30001-30005 at L*, 15 runs. -> S2_CELLS.csv, S2_VERDICT.json
  f      confirmation, seeds 30006-30020 at L*, 8 arms, 120 runs. -> F_*.{csv,json}

S1/S2 require the authorization phrase "授权交通筛查"; F additionally requires GO from S2 and
"授权交通确认".  This module performs no run on its own.
No src/, manuscript, artifacts/ or other results_* writes.  No EventTrace is created.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "results_new_block_traffic" / "round_v1"
RUNS = OUT / "runs"
E3_TRACES = ROOT / "artifacts/e3_formal_runs_r1/eventtraces/traffic"
E2_TRACES = ROOT / "artifacts/e2_traffic_formal_runs_r1/eventtraces"
E3_RUNS = ROOT / "artifacts/e3_formal_runs_r1/runs/traffic"

SCREEN_SEEDS = [30001, 30002, 30003, 30004, 30005]
S1_SEEDS = [30001, 30002, 30003]
CONFIRM_SEEDS = list(range(30006, 30021))
LADDER = [2, 5, 10, 20]
H_MEAN_BAR = 0.010          # GO-H: mean H >= 1.0 %
H_LCB_BAR = 0.005           # GO-H: one-sided 95 % lower bound > 0.5 %
MDE_RATIO_BAR = 0.5         # GO-H: MDE80 < 0.5 * mean H
F1_LOWER_OPEN = 0.005       # F-H1: two-sided lower bound > 0.5 %
TAU_QUANTILE = 0.90
BASE_RATE_BAND = (0.05, 0.30)
RECALL_BAND = (0.02, 0.98)
INSTRUCTION_SHA = "25f580aa4e2824daa931addab39eadee67319a24fc89c11ce7f2cf9aa552bb36"


def dump_json(obj, p: pathlib.Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def chosen_family() -> str:
    return json.loads((OUT / "S0_VERDICT.json").read_text(encoding="utf-8"))["chosen_family"]


def trace_dir(family: str, seed: int) -> pathlib.Path:
    if family == "e3_complete_aligned":
        return E3_TRACES / ("seed%d" % seed) / "training_eventtrace"
    return E2_TRACES / ("%d" % seed) / family / "training_eventtrace"


def run_arm(arm: str, seed: int, local_steps: int, tag: str, family: str) -> pathlib.Path:
    out = RUNS / tag / arm / ("ls%d" % local_steps) / ("seed%d" % seed)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.real_runner.runner import run_e3_real

    run_e3_real(
        root=ROOT,
        run_dir=out,
        dataset=load_paper_dataset(ROOT, "traffic"),
        method=arm,
        seed=int(seed),
        eventtrace_dir=trace_dir(family, seed),
        spatial_to_client=load_spatial_to_client(ROOT, "traffic"),
        dataset_name="traffic",
        local_steps=int(local_steps),
    )
    return out


def read_run(d: pathlib.Path) -> dict:
    fm = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
    wm_path = d / "window_metrics.json"
    wm = json.loads(wm_path.read_text(encoding="utf-8")) if wm_path.is_file() else None
    return {"final_metrics": fm, "window_metrics": wm,
            "runtime_seconds": float(fm.get("runtime_seconds") or float("nan"))}


# ------------------------------------------------------------------ S1: the ladder
SEALED_LOCAL_STEPS = 2   # the sealed E2 traffic grid (amendment A1)


def rung_runs(local_steps: int, seed: int, family: str) -> tuple[float, float, str]:
    """One ladder rung: `(RMSE_mu, runtime_seconds, source)`.

    Level 2 is the sealed E2 `complete_aligned` grid and must not be retrained (amendment
    A1), so it is **read** from `artifacts/e2_traffic_formal_runs_r1`.  Other levels train
    fresh through `run_e3_real`.
    """
    if local_steps == SEALED_LOCAL_STEPS:
        e2 = (ROOT / "artifacts/e2_traffic_formal_runs_r1/runs" / ("%d" % seed)
              / "complete_aligned" / "fedavg_window")
        if not (e2 / "final_metrics.json").is_file():
            raise SystemExit("INCOMPLETE: sealed E2 rung missing at %s" % e2)
        fm = json.loads((e2 / "final_metrics.json").read_text(encoding="utf-8"))
        return float(fm["RMSE_mu"]), float(fm.get("runtime_seconds") or float("nan")), \
            str(e2.relative_to(ROOT)).replace("\\", "/")
    d = run_arm("fedavg_window", seed, local_steps, "s1", family)
    r = read_run(d)
    return (float(r["final_metrics"]["RMSE_mu"]), r["runtime_seconds"],
            str(d.relative_to(ROOT)).replace("\\", "/"))


def stage_s1() -> None:
    family = chosen_family()
    # c: mean RMSE_mu of central_delivered on the chosen family and the S1 seeds
    if family == "e3_complete_aligned":
        c_vals = [read_run(E3_RUNS / "central_delivered" / ("seed%d" % s))["final_metrics"]["RMSE_mu"]
                  for s in S1_SEEDS]
        c_source = "frozen artifacts/e3_formal_runs_r1/runs/traffic/central_delivered"
    else:
        c_vals = []
        for s in S1_SEEDS:
            d = run_arm("central_delivered", s, 2, "s1_central", family)
            c_vals.append(read_run(d)["final_metrics"]["RMSE_mu"])
        c_source = "fresh runs (chosen family is not the e3 family)"
    c = float(np.mean(c_vals))
    rows = []
    rung_sources = {}
    for ls in LADDER:
        rmses, rts = [], []
        for s in S1_SEEDS:
            v, rt, src = rung_runs(ls, s, family)
            rmses.append(v)
            rts.append(rt)
            rung_sources["%d/%d" % (ls, s)] = src
            print("  S1 local_steps=%-3d seed%d RMSE_mu=%.6f  runtime=%.1f s  src=%s"
                  % (ls, s, v, rt, "sealed-e2" if ls == SEALED_LOCAL_STEPS else "fresh"),
                  flush=True)
        rows.append({"local_steps": ls, "n": len(rmses), "mean_RMSE_mu": float(np.mean(rmses)),
                     "min_RMSE_mu": min(rmses), "max_RMSE_mu": max(rmses),
                     "mean_runtime_seconds": float(np.nanmean(rts)),
                     "ratio_to_c": float(np.mean(rmses) / c),
                     "local_steps_source": ("sealed_e2_complete_aligned_read_only"
                                            if ls == SEALED_LOCAL_STEPS else "fresh_run_e3_real")})
    with (OUT / "S1_LADDER.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) + ["threshold_1p01_c"])
        wr.writeheader()
        for r in rows:
            wr.writerow({**r, "threshold_1p01_c": 1.01 * c})
    qualifying = [r for r in rows if r["mean_RMSE_mu"] <= 1.01 * c]
    verdict = {"created_utc": now(), "instruction_sha256": INSTRUCTION_SHA, "family": family,
               "central_delivered_mean": c, "central_source": c_source,
               "threshold_1p01_c": 1.01 * c, "ladder": rows,
               "rung_sources": rung_sources,
               "amendment_A1": {
                   "reused_rung_local_steps": SEALED_LOCAL_STEPS,
                   "reused_from": "artifacts/e2_traffic_formal_runs_r1 (E2 runner, read-only)",
                   "disclosure": "level 2 is inherited, not retrained, so that rung is not "
                                 "numerically interchangeable with the fresh rungs"},
               "first_run_wall_seconds": next((r["mean_runtime_seconds"] for r in rows
                                               if r["local_steps"] != SEALED_LOCAL_STEPS), None)}
    if qualifying:
        L = min(qualifying, key=lambda r: r["local_steps"])
        verdict.update({"go": True, "L_star": L["local_steps"], "L_star_reason": "<=1.01c"})
    else:
        best = min(rows, key=lambda r: r["mean_RMSE_mu"])
        base = next(r for r in rows if r["local_steps"] == 2)
        if best["mean_RMSE_mu"] <= 0.99 * base["mean_RMSE_mu"]:
            verdict.update({"go": True, "L_star": best["local_steps"],
                            "L_star_reason": "best_not_within_1pct"})
        else:
            verdict.update({"go": False, "failed": "N3",
                            "reason": "no level within 1.01c and best is not 1 % below level 2"})
    dump_json(verdict, OUT / "S1_VERDICT.json")
    print("S1 verdict:", json.dumps({k: verdict[k] for k in verdict
                                     if k in ("go", "L_star", "L_star_reason", "failed")}))
    if not verdict["go"]:
        raise SystemExit("STOP: S1 NO-GO (N3)")


# ------------------------------------------------------- S2: headroom and decision
def traffic_ctx() -> dict:
    """Everything shared by the S2/F scoring path."""
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset
    from raven_mcs.e3.target_pair.target_wiring import production_target_bundle

    ds = load_paper_dataset(ROOT, "traffic")
    atomic = ds.atomic_df
    bundle = production_target_bundle(root=ROOT, dataset_name="traffic", dataset=ds)
    mu = np.asarray(bundle["mu"], float)
    gids = [str(g) for g in bundle["group_id_by_index"]]
    gidx = {g: i for i, g in enumerate(gids)}
    group_of = dict(zip(atomic["unit_id"].astype(str), atomic["target_group"].astype(str)))
    split_of = dict(zip(atomic["unit_id"].astype(str), atomic["split"].astype(str)))
    n_test_by_group = np.zeros(len(gids))
    for uid, g in group_of.items():
        if split_of.get(uid) == "test":
            n_test_by_group[gidx[g]] += 1.0
    train_vals = atomic.loc[atomic["split"].astype(str) == "train",
                            "target_value"].to_numpy(float)
    valid_vals = atomic.loc[atomic["split"].astype(str) == "validation",
                            "target_value"].to_numpy(float)
    return {"ds": ds, "mu": mu, "gids": gids, "n_test_by_group": n_test_by_group,
            "group_of": group_of,
            "tau": float(np.quantile(train_vals, TAU_QUANTILE)),
            "tau_validation_sensitivity": (float(np.quantile(valid_vals, TAU_QUANTILE))
                                           if valid_vals.size else None),
            "n_train_values": int(train_vals.size),
            "train_value_min": float(train_vals.min()), "train_value_max": float(train_vals.max())}


def score_checkpoint(ctx: dict, arm: str, seed: int, run_dir: pathlib.Path) -> dict:
    """The round's scoring rule: mu-weighted RMSE_mu and mu-weighted exceedance F1.

    `tau` is the 0.90 quantile of the **training**-split target values (§4); a unit is an
    exceedance iff `y > tau` and an alert iff `yhat > tau`.  `F1_mu` weights every test unit
    by `mu` of its group divided by that group's test count, exactly as the endpoint's own
    weights do, so the weighted mass sums to 1.
    """
    import torch
    from raven_mcs.e3.real_runner.runner import _predict
    from raven_mcs.models.common_ndmf import deterministic_common_ndmf

    ds, mu = ctx["ds"], ctx["mu"]
    ck = torch.load(run_dir / "checkpoints/final.pt", map_location="cpu", weights_only=False)
    state = ck["state_dict"] if isinstance(ck, dict) and "state_dict" in ck else ck
    model = deterministic_common_ndmf(ds.num_spatial, seed=seed)
    model.load_state_dict(state)
    model.eval()

    class _H:
        pass

    h = _H()
    h.model = model
    pred = _predict(h, ds, split="test")
    yt, yp, grp = pred["y_true"], pred["y_pred"], pred["groups"]
    w = np.array([mu[int(g)] / max(ctx["n_test_by_group"][int(g)], 1.0) for g in grp], float)
    w_sum_raw = float(w.sum())
    w = w / w_sum_raw
    rmse = float(np.sqrt(np.sum(w * (yt - yp) ** 2)))
    tau = ctx["tau"]
    alert, exc = yp > tau, yt > tau
    tp = float(np.sum(w * (alert & exc)))
    fp = float(np.sum(w * (alert & ~exc)))
    fn = float(np.sum(w * (~alert & exc)))
    tn = float(np.sum(w * (~alert & ~exc)))
    f1 = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) > 0 else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else float("nan")
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else float("nan")
    return {"arm": arm, "seed": seed, "RMSE_mu": rmse, "F1_mu": f1,
            "recall_mu": recall, "precision_mu": precision,
            "base_rate_mu": float(np.sum(w * exc)), "alert_rate_mu": float(np.sum(w * alert)),
            "tp_mu": tp, "fp_mu": fp, "fn_mu": fn, "tn_mu": tn,
            "n_alert": int(alert.sum()), "n_exceed": int(exc.sum()), "n_test": int(len(yt)),
            "tau": tau, "weight_sum_raw": w_sum_raw,
            "weight_sum_normalized": float(w.sum()),
            "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/")}


def stage_s2() -> None:
    family = chosen_family()
    v1 = json.loads((OUT / "S1_VERDICT.json").read_text(encoding="utf-8"))
    if not v1.get("go"):
        raise SystemExit("STOP: S1 verdict is not GO")
    L = int(v1["L_star"])
    ctx = traffic_ctx()

    def score(arm: str, seed: int, tag: str):
        d = RUNS / tag / arm / ("ls%d" % L) / ("seed%d" % seed)
        if not (d / "final_metrics.json").is_file():
            d = run_arm(arm, seed, L, tag, family)
        r = read_run(d)
        out = score_checkpoint(ctx, arm, seed, d)
        out["local_steps"] = L
        out["stored_RMSE_mu"] = float(r["final_metrics"]["RMSE_mu"])
        out["rel_diff_vs_stored"] = (abs(out["RMSE_mu"] - out["stored_RMSE_mu"])
                                     / abs(out["stored_RMSE_mu"]))
        out["runtime_seconds"] = r["runtime_seconds"]
        return out

    cells = []
    for arm in ("fedavg_window", "raven_simoracle", "central_delivered"):
        for s in SCREEN_SEEDS:
            cells.append(score(arm, s, "s2"))
            print("  S2 %-18s seed%d done" % (arm, s), flush=True)
    df = pd.DataFrame(cells)
    df.to_csv(OUT / "S2_CELLS.csv", index=False)

    fed = df[df.arm == "fedavg_window"].set_index("seed")["RMSE_mu"]
    orc = df[df.arm == "raven_simoracle"].set_index("seed")["RMSE_mu"]
    H = ((fed - orc) / fed).to_numpy(float)
    n = len(H)
    mean_h = float(H.mean())
    lcb = float(mean_h - stats.t.ppf(0.95, n - 1) * H.std(ddof=1) / np.sqrt(n))
    sd = float(H.std(ddof=1))
    mde80 = float((stats.t.ppf(0.975, 14) + stats.t.ppf(0.80, 14)) * sd / np.sqrt(15))
    go_h = bool(mean_h >= H_MEAN_BAR and lcb > H_LCB_BAR and mde80 < MDE_RATIO_BAR * mean_h)

    base = float(df[df.arm == "fedavg_window"]["base_rate_mu"].mean())
    rec_f = df[df.arm == "fedavg_window"]["recall_mu"].to_numpy(float)
    rec_o = df[df.arm == "raven_simoracle"]["recall_mu"].to_numpy(float)
    in_band = bool(BASE_RATE_BAND[0] <= base <= BASE_RATE_BAND[1])
    rec_ok = bool(np.all((rec_f > RECALL_BAND[0]) & (rec_f < RECALL_BAND[1]))
                  and np.all((rec_o > RECALL_BAND[0]) & (rec_o < RECALL_BAND[1])))
    f1_f = df[df.arm == "fedavg_window"].set_index("seed")["F1_mu"]
    f1_o = df[df.arm == "raven_simoracle"].set_index("seed")["F1_mu"]
    f1_dir = float((f1_o - f1_f).mean())
    go_d = bool(in_band and rec_ok and f1_dir > 0)

    failed = [k for k, v in (("H", mean_h >= H_MEAN_BAR), ("power", mde80 < MDE_RATIO_BAR * mean_h),
                             ("lcb", lcb > H_LCB_BAR), ("base_rate", in_band),
                             ("recall", rec_ok), ("F1_direction", f1_dir > 0)) if not v]
    per_run = float(df["runtime_seconds"].mean())
    verdict = {"created_utc": now(), "instruction_sha256": INSTRUCTION_SHA,
               "family": family, "L_star": L, "tau": tau,
               "H": {"mean": mean_h, "lcb_95": lcb, "sd": sd, "n": n,
                     "mde80_confirm": mde80, "go_h": go_h},
               "D": {"base_rate_mu": base, "in_band": in_band,
                     "recall_fedavg": rec_f.tolist(), "recall_simoracle": rec_o.tolist(),
                     "recall_ok": rec_ok, "mean_delta_F1": f1_dir, "go_d": go_d},
               "go": bool(go_h and go_d), "failed": failed,
               "wall_time": {"s2_mean_run_seconds": per_run,
                             "projected_F_hours_120_runs": 120 * per_run / 3600.0,
                             "fits_24h": (120 * per_run / 3600.0) < 24.0},
               "design_gate": {"rho_zero": True,
                               "note": "chosen family has phi_train_unit = 0, so Design is "
                                       "on and no raven_simoracle_nodesign arm is used"}}
    dump_json(verdict, OUT / "S2_VERDICT.json")
    print("S2 verdict: go=%s failed=%s  mean H=%.4f lcb=%.4f MDE=%.4f  base=%.4f  dF1=%+.4f"
          % (verdict["go"], failed, mean_h, lcb, mde80, base, f1_dir))
    print("  projected F: %.2f h (fits 24 h: %s)"
          % (verdict["wall_time"]["projected_F_hours_120_runs"], verdict["wall_time"]["fits_24h"]))
    if not verdict["go"]:
        raise SystemExit("STOP: S2 NO-GO")


# ------------------------------------------------------------------ F: confirmation
F_ARMS = ["fedavg_window", "raven", "local_hajek", "debt_cal", "inst_cal",
          "twostage_hajek", "raven_simoracle", "central_delivered"]
F_PRIMARY = "raven"
F_COMPARATOR = "fedavg_window"


def holm(pvals: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, monotone in the input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvals[i])
        running = max(running, val)
        adj[i] = running
    return adj


def stage_f() -> None:
    import torch  # noqa: F401  (kept for symmetry with the other stages)

    v2 = json.loads((OUT / "S2_VERDICT.json").read_text(encoding="utf-8"))
    if not v2.get("go"):
        raise SystemExit("STOP: S2 verdict is not GO; F is not licensed")
    L = int(v2["L_star"])
    family = chosen_family()
    ctx = traffic_ctx()

    cells = []
    for arm in F_ARMS:
        for seed in CONFIRM_SEEDS:
            d = RUNS / "f" / arm / ("ls%d" % L) / ("seed%d" % seed)
            if not (d / "final_metrics.json").is_file():
                d = run_arm(arm, seed, L, "f", family)
            r = read_run(d)
            out = score_checkpoint(ctx, arm, seed, d)
            out.update({"local_steps": L, "stored_RMSE_mu": float(r["final_metrics"]["RMSE_mu"]),
                        "runtime_seconds": r["runtime_seconds"]})
            cells.append(out)
            print("  F %-18s seed%d RMSE_mu=%.6f  F1_mu=%.4f  alert=%.4f"
                  % (arm, seed, out["RMSE_mu"], out["F1_mu"], out["alert_rate_mu"]), flush=True)
    df = pd.DataFrame(cells)
    df.to_csv(OUT / "F_CELLS.csv", index=False)

    piv_r = df.pivot(index="seed", columns="arm", values="RMSE_mu")
    piv_f = df.pivot(index="seed", columns="arm", values="F1_mu")
    n = len(piv_r)

    # F-H1: paired relative gain of raven over fedavg_window on RMSE_mu
    g = ((piv_r[F_COMPARATOR] - piv_r[F_PRIMARY]) / piv_r[F_COMPARATOR]).to_numpy(float)
    g_mean = float(g.mean())
    half = float(stats.t.ppf(0.975, n - 1) * g.std(ddof=1) / np.sqrt(n))
    g_lo, g_hi = g_mean - half, g_mean + half
    lab_h1 = "open" if g_lo > F1_LOWER_OPEN else ("harm" if g_hi < 0 else "null")

    # F-H2: paired delta F1
    d1 = (piv_f[F_PRIMARY] - piv_f[F_COMPARATOR]).to_numpy(float)
    d1_mean = float(d1.mean())
    half1 = float(stats.t.ppf(0.975, n - 1) * d1.std(ddof=1) / np.sqrt(n))
    d1_lo, d1_hi = d1_mean - half1, d1_mean + half1
    base = float(df[df.arm == F_PRIMARY]["base_rate_mu"].mean())
    rec = df[df.arm.isin([F_PRIMARY, F_COMPARATOR])]["recall_mu"].to_numpy(float)
    base_ok = bool(BASE_RATE_BAND[0] <= base <= BASE_RATE_BAND[1])
    rec_ok = bool(np.all((rec > RECALL_BAND[0]) & (rec < RECALL_BAND[1])))
    if not (base_ok and rec_ok):
        lab_h2 = "saturated"
    else:
        lab_h2 = "open" if d1_lo > 0 else ("harm" if d1_hi < 0 else "null")

    # Holm over the two co-primary tests
    def t_pvalue(x: np.ndarray) -> float:
        return float(2 * (1 - stats.t.cdf(abs(x.mean()) / (x.std(ddof=1) / np.sqrt(len(x)))),
                          len(x) - 1))
    p_h1, p_h2 = t_pvalue(g), t_pvalue(d1)
    adj = holm([p_h1, p_h2])
    both_open_holm = bool(lab_h1 == "open" and lab_h2 == "open"
                          and adj[0] < 0.05 and adj[1] < 0.05)

    # descriptive
    h_mean = float(v2["H"]["mean"])
    secondary = {}
    for arm in F_ARMS:
        if arm in (F_PRIMARY, F_COMPARATOR):
            continue
        gg = ((piv_r[arm] - piv_r[F_PRIMARY]) / piv_r[arm]).to_numpy(float)
        secondary[arm] = {"mean_gain_of_raven_over_arm": float(gg.mean()),
                          "ci_lo": float(gg.mean() - stats.t.ppf(0.975, n - 1)
                                         * gg.std(ddof=1) / np.sqrt(n)),
                          "ci_hi": float(gg.mean() + stats.t.ppf(0.975, n - 1)
                                         * gg.std(ddof=1) / np.sqrt(n))}
    summary = {"created_utc": now(), "instruction_sha256": INSTRUCTION_SHA,
               "family": family, "L_star": L, "n_confirm_seeds": n, "arms": F_ARMS,
               "tau": ctx["tau"],
               "F_H1_prediction": {"comparator": F_COMPARATOR, "arm": F_PRIMARY,
                                   "mean_g": g_mean, "ci_lo": g_lo, "ci_hi": g_hi,
                                   "label": lab_h1, "margin": F1_LOWER_OPEN},
               "F_H2_decision": {"mean_delta_F1": d1_mean, "ci_lo": d1_lo, "ci_hi": d1_hi,
                                 "label": lab_h2, "base_rate_mu": base, "base_ok": base_ok,
                                 "recall_ok": rec_ok,
                                 "recall_values": rec.tolist()},
               "holm": {"p_F_H1": p_h1, "p_F_H2": p_h2,
                        "p_adj_F_H1": adj[0], "p_adj_F_H2": adj[1],
                        "both_open_after_holm": both_open_holm},
               "oracle_headroom_recovered_g_over_H": (g_mean / h_mean) if h_mean else None,
               "secondary": secondary,
               "wall_time": {"mean_run_seconds": float(df["runtime_seconds"].mean()),
                             "n_runs": len(cells)}}
    dump_json(summary, OUT / "F_SUMMARY.json")
    dump_json({"created_utc": now(), "F_H1": lab_h1, "F_H2": lab_h2,
               "both_open_after_holm": both_open_holm,
               "e1_repair_claim_licensed": both_open_holm,
               "licensing_rule": "§5: the E1 repair claim needs both F-H1 and F-H2 open after Holm"},
              OUT / "F_DECISION.json")
    print("F: F-H1 %s (g=%+.4f [%+.4f, %+.4f])  F-H2 %s (dF1=%+.4f [%+.4f, %+.4f])"
          % (lab_h1, g_mean, g_lo, g_hi, lab_h2, d1_mean, d1_lo, d1_hi))
    print("   Holm adjusted p: F-H1 %.4g  F-H2 %.4g  -> E1 repair licensed: %s"
          % (adj[0], adj[1], both_open_holm))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["s1", "s2", "f"])
    args = ap.parse_args()
    if args.stage == "s1":
        stage_s1()
    elif args.stage == "s2":
        stage_s2()
    else:
        stage_f()


if __name__ == "__main__":
    main()
