"""W1 round v5.1 - A2' (R3): theta-canonical worst-group scores with the AM-3 three-part G0.

Read-only.  Writes only under results_w1_ladder/round_v5_1/.

Canonical score = theta re-score for EVERY row:
  * theta re-score: load checkpoints/final.pt into a fresh CommonNDMF and predict the test
    split directly (the c_impact_recalc.py path).  Verified in scripts/w1_v51_recon.py to be
    bit-identical to the build_full_runner + runner._predict path used by w1_v5_a2.py
    (max |Delta y_pred| = 0.0 on all 18 trigger rows), so this is the same observable, scored
    from the saved theta.
  * non-trigger rows: it equals final_metrics.json (G0-a, AM-3).
  * trigger rows: {uair} x {30007, 30016, 30018} x all 6 arms (AM-3, fixed in advance).

Gates: G0-a <= 1e-12 endpoint equality on non-trigger rows (222 expected);
       G0-b trigger confirmation + Table II per seed within 1e-8 relative;
       G0-c frozen stored WorstGroupRMSE within 1e-8 relative (AM-4).

Usage: python scripts/w1_v51_a2.py [--rescore]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_joint_ou_cs_p2 as p2                                                # noqa: E402
import w1_v4_train                                                             # noqa: E402,F401
from raven_mcs.e3.canary.dataset_load import load_paper_dataset                # noqa: E402
from raven_mcs.e3.real_runner.runner import (                                  # noqa: E402
    _head_tail_rmse,
    _mu_weights_for_test,
)
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle    # noqa: E402
from raven_mcs.metrics.accuracy import rmse_mu                                 # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF                            # noqa: E402
from raven_mcs.models.features import extract_features                         # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5_1"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
STORED = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv"
TRAINED_ARMS = ("uniform_window", "proj_beta", "proj_beta_debt")
FROZEN_ARMS = ("fedavg_window", "inst_cal", "raven")
ARMS = TRAINED_ARMS + FROZEN_ARMS
SEEDS = list(range(30001, 30021))
TRIGGER_DS = "uair"
TRIGGER_SEEDS = (30007, 30016, 30018)
G0A_TOL = 1e-12
G0BC_TOL_REL = 1e-8
BOOT_N, BOOT_SEED = 10_000, 20261002
CONTRASTS = (("proj_beta", "uniform_window"), ("raven", "proj_beta"),
             ("proj_beta", "fedavg_window"), ("uniform_window", "fedavg_window"),
             ("proj_beta_debt", "proj_beta"))
DELTA_WG = 0.005
_DSC: dict = {}


def block_of(label: str) -> int:
    for part in str(label).split("::"):
        if part.startswith("block"):
            return int(part[5:])
    return -1


def ds_setup(name: str) -> dict:
    if name in _DSC:
        return _DSC[name]
    ds = load_paper_dataset(ROOT, name)
    bundle = production_target_bundle(root=ROOT, dataset_name=name, dataset=ds)
    _DSC[name] = {"ds": ds, "bundle": bundle}
    return _DSC[name]


def run_dir_of(ds: str, arm: str, seed: int) -> pathlib.Path:
    if arm in TRAINED_ARMS:
        return TRAIN / ds / arm / f"seed{seed}"
    return E3 / ds / arm / f"seed{seed}"


def load_theta(p: pathlib.Path) -> dict:
    obj = torch.load(p, map_location="cpu", weights_only=False)
    if isinstance(obj, dict) and "state_dict" in obj:
        obj = obj["state_dict"]
    return obj


def predict_model(model, dataset, split: str = "test") -> dict:
    units = dataset.get_atomic_units(split=split)
    inv = {i: g for g, i in dataset._target_group_str_to_int.items()}
    spatial_to_idx = {str(s): int(i) for s, i in dataset._spatial_to_idx.items()}
    total_slots = int(dataset.atomic_df["time_index"].max()) + 1
    yt, yp, gids, gstr = [], [], [], []
    model.eval()
    with torch.no_grad():
        for u in units:
            sp, hr, wd, tr = extract_features(
                [u.spatial_id], [float(u.absolute_time)], [int(u.time_index)],
                spatial_to_idx, total_slots)
            q = model(sp, hr, wd, tr).cpu().numpy().reshape(-1)
            yp.append(float(q[0]))
            yt.append(float(u.target_value))
            gids.append(int(u.target_group))
            gstr.append(inv.get(int(u.target_group), str(u.target_group)))
    return {"y_true": np.asarray(yt, dtype=np.float64),
            "y_pred": np.asarray(yp, dtype=np.float64),
            "groups": np.asarray(gids, dtype=int), "group_strs": gstr}


def score(pred: dict, mu: np.ndarray, head_ids, tail_ids) -> dict:
    mu_w = _mu_weights_for_test(pred, mu)
    rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w))
    head, tail = _head_tail_rmse(pred, mu_w, list(head_ids), list(tail_ids))
    blocks = np.asarray([block_of(g) for g in pred["group_strs"]], dtype=int)
    wg = [float(p2._wrmse_block(pred["y_true"], pred["y_pred"], blocks == g, mu_w))
          for g in range(4)]
    arr = np.asarray(wg, dtype=float)
    worst = float(np.nanmax(arr)) if np.isfinite(arr).any() else None
    argmax = int(np.nanargmax(arr)) if np.isfinite(arr).any() else -1
    return {"RMSE_mu": rmse, "Head_RMSE": float(head), "Tail_RMSE": float(tail),
            "WorstGroupRMSE": worst, "argmax_group": argmax,
            "WG_R0": wg[0], "WG_R1": wg[1], "WG_R2": wg[2], "WG_R3": wg[3]}


def stored_table() -> dict:
    d = pd.read_csv(STORED)
    out = {}
    for r in d.itertuples(index=False):
        out[(str(r.dataset), str(r.method), int(r.seed))] = {
            "RMSE_mu": float(r.RMSE_mu), "WorstGroupRMSE": float(r.WorstGroupRMSE)}
    return out


def trigger_of(ds: str, arm: str, seed: int) -> dict:
    """Read the run's own window_metrics.json and check the AM-3 trigger condition."""
    rd = run_dir_of(ds, arm, seed)
    wm = json.loads((rd / "window_metrics.json").read_text(encoding="utf-8"))
    last = wm[-1]
    active = bool(last.get("active"))
    alpha = list(last.get("alpha") or [])
    return {"trigger": (not active) or (len(alpha) == 0),
            "last_window_id": int(last.get("window_id", -1)),
            "last_active": active, "last_alpha_len": len(alpha),
            "last_a_r_size": int(last.get("a_r_size", -1)), "n_windows": len(wm)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rescore", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cache = OUT / "A2P_RESCORE.csv"
    if args.rescore or not cache.is_file():
        rows = []
        for ds in ("sensorscope", "uair"):
            setup = ds_setup(ds)
            ds_obj, bundle = setup["ds"], setup["bundle"]
            mu = np.asarray(bundle["mu"], dtype=np.float64)
            ht = bundle["head_tail"]
            for arm in ARMS:
                for seed in SEEDS:
                    rd = run_dir_of(ds, arm, seed)
                    fm = json.loads((rd / "final_metrics.json").read_text(encoding="utf-8"))
                    tg = trigger_of(ds, arm, seed)
                    theta = load_theta(rd / "checkpoints" / "final.pt")
                    model = CommonNDMF(num_spatial=ds_obj.num_spatial)
                    model.load_state_dict(theta)
                    pred = predict_model(model, ds_obj)
                    s = score(pred, mu, ht["head_group_ids"], ht["tail_group_ids"])
                    rows.append({"ds": ds, "arm": arm, "seed": seed, **s, **tg,
                                 "fm_RMSE_mu": float(fm["RMSE_mu"]),
                                 "fm_Head_RMSE": float(fm["Head_RMSE"]),
                                 "fm_Tail_RMSE": float(fm["Tail_RMSE"]),
                                 "d_rmse": abs(s["RMSE_mu"] - float(fm["RMSE_mu"])),
                                 "d_head": abs(s["Head_RMSE"] - float(fm["Head_RMSE"])),
                                 "d_tail": abs(s["Tail_RMSE"] - float(fm["Tail_RMSE"]))})
                    print("a2p %-6s %-16s %d trig=%s rmse=%.10f d=%.2e"
                          % (ds, arm, seed, tg["trigger"], s["RMSE_mu"],
                             abs(s["RMSE_mu"] - float(fm["RMSE_mu"]))), flush=True)
        pd.DataFrame(rows).to_csv(cache, index=False)
    df = pd.read_csv(cache)
    st = stored_table()
    df["tableII_RMSE_mu"] = [st.get((r.ds, r.arm, int(r.seed)), {}).get("RMSE_mu")
                             for r in df.itertuples(index=False)]
    df["tableII_WG"] = [st.get((r.ds, r.arm, int(r.seed)), {}).get("WorstGroupRMSE")
                        for r in df.itertuples(index=False)]
    df["rel_d_tableII_mu"] = ((df.RMSE_mu - df.tableII_RMSE_mu).abs() / df.tableII_RMSE_mu)
    df["rel_d_tableII_wg"] = ((df.WorstGroupRMSE - df.tableII_WG).abs() / df.tableII_WG)
    # ---------------- AM-3 G0 classification -------------------------------------------
    df["in_trigger_set"] = ((df.ds == TRIGGER_DS) & (df.seed.isin(TRIGGER_SEEDS)))
    df["source"] = np.where(df.in_trigger_set, "theta_trigger", "final_metrics")
    nontrig = df[~df.in_trigger_set]
    g0a_bad = nontrig[(nontrig.d_rmse > G0A_TOL) | (nontrig.d_head > G0A_TOL)
                      | (nontrig.d_tail > G0A_TOL)]
    unlisted = df[(df.trigger) & (~df.in_trigger_set)]
    listed_no_trigger = df[(df.in_trigger_set) & (~df.trigger)]
    trig = df[df.in_trigger_set]
    g0b_rows = []
    for r in trig.itertuples(index=False):
        rel_mu = (None if pd.isna(r.tableII_RMSE_mu)
                  else abs(r.RMSE_mu - r.tableII_RMSE_mu) / r.tableII_RMSE_mu)
        rel_wg = (None if pd.isna(r.tableII_WG)
                  else abs(r.WorstGroupRMSE - r.tableII_WG) / r.tableII_WG)
        g0b_rows.append({"ds": r.ds, "arm": r.arm, "seed": int(r.seed),
                         "trigger_confirmed": bool(r.trigger),
                         "last_active": bool(r.last_active),
                         "last_alpha_len": int(r.last_alpha_len),
                         "rel_d_tableII_RMSE_mu": rel_mu, "rel_d_tableII_WG": rel_wg,
                         "pass": bool(r.trigger and (rel_mu is None or rel_mu <= G0BC_TOL_REL))})
    g0b = pd.DataFrame(g0b_rows)
    froz = df[df.arm.isin(["fedavg_window", "raven"]) & df.tableII_WG.notna()]
    g0c = {"n_rows": int(len(froz)),
           "observed_max_rel": (None if not len(froz) else float(froz.rel_d_tableII_wg.max())),
           "tolerance_rel": G0BC_TOL_REL,
           "pass": bool(len(froz) and float(froz.rel_d_tableII_wg.max()) <= G0BC_TOL_REL)}
    gates = {
        "AM3_G0a": {"nontrigger_rows": int(len(nontrig)),
                    "expected": 222,
                    "pass_rows": int(len(nontrig) - len(g0a_bad)),
                    "observed_max_d_rmse": float(nontrig.d_rmse.max()),
                    "observed_max_d_head": float(nontrig.d_head.max()),
                    "observed_max_d_tail": float(nontrig.d_tail.max()),
                    "tolerance": G0A_TOL, "pass": bool(len(g0a_bad) == 0)},
        "AM3_G0b": {"n_rows": int(len(g0b)), "pass_rows": int(g0b["pass"].sum()),
                    "unlisted_trigger_rows": int(len(unlisted)),
                    "listed_without_trigger": int(len(listed_no_trigger)),
                    "observed_max_rel_tableII": (None if not len(g0b) else
                                                 float(g0b.rel_d_tableII_RMSE_mu.max())),
                    "tolerance_rel": G0BC_TOL_REL,
                    "pass": bool(len(g0b) == 18 and g0b["pass"].all()
                                 and len(unlisted) == 0 and len(listed_no_trigger) == 0)},
        "AM3_G0c": g0c,
        "trigger_mechanism_confirmed": bool(
            len(listed_no_trigger) == 0 and len(unlisted) == 0 and g0b.trigger_confirmed.all()),
    }
    gates["G0_all_pass"] = bool(gates["AM3_G0a"]["pass"] and gates["AM3_G0b"]["pass"]
                                and gates["AM3_G0c"]["pass"])
    # ---------------- canonical scores -------------------------------------------------
    canon = df.copy()
    canon["WorstGroupRMSE_canonical"] = canon.WorstGroupRMSE
    canon["RMSE_mu_canonical"] = canon.RMSE_mu
    (OUT / "WORSTGROUP_V51.csv").write_text("", encoding="utf-8")
    canon.to_csv(OUT / "WORSTGROUP_V51.csv", index=False)
    g0b.to_csv(OUT / "A2P_G0B_TRIGGER.csv", index=False)
    nontrig.to_csv(OUT / "A2P_G0A_NONTRIGGER.csv", index=False)
    g0a_bad.to_csv(OUT / "A2P_G0A_FAILURES.csv", index=False)

    # ---------------- analysis (v5 A2 unchanged) ---------------------------------------
    piv = {ds: {a: g.set_index("seed") for a, g in canon[canon.ds == ds].groupby("arm")}
           for ds in ("sensorscope", "uair")}
    rows = []
    for ds in ("sensorscope", "uair"):
        for a, b in CONTRASTS:
            pa, pb = piv[ds][a], piv[ds][b]
            common = pa.index.intersection(pb.index)
            d = (pa.loc[common, "WorstGroupRMSE_canonical"]
                 - pb.loc[common, "WorstGroupRMSE_canonical"]).to_numpy(float)
            from scipy import stats
            rng = np.random.default_rng(BOOT_SEED)
            boot = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                             for _ in range(BOOT_N)])
            try:
                p = float(stats.wilcoxon(d).pvalue)
            except Exception:                                    # noqa: BLE001
                p = float("nan")
            rows.append({"ds": ds, "endpoint": "WorstGroupRMSE",
                         "contrast": "%s - %s" % (a, b), "status": "ok", "n_seeds": len(d),
                         "mean_diff": float(d.mean()),
                         "rel_diff": float(d.mean() / pb["WorstGroupRMSE_canonical"].mean()),
                         "ci_lo": float(np.percentile(boot, 2.5)),
                         "ci_hi": float(np.percentile(boot, 97.5)),
                         "p_wilcoxon": p,
                         "mean_wg_a": float(pa["WorstGroupRMSE_canonical"].mean()),
                         "mean_wg_b": float(pb["WorstGroupRMSE_canonical"].mean()),
                         "argmax_a": int(pa["argmax_group"].mode().iloc[0]),
                         "argmax_b": int(pb["argmax_group"].mode().iloc[0]),
                         "argmax_changed_seeds": int((pa["argmax_group"]
                                                      != pb["argmax_group"]).sum())})
    pa_df = pd.DataFrame(rows)
    pv = pa_df.p_wilcoxon.to_numpy(float)
    order = np.argsort(pv)
    holm = np.empty_like(pv)
    run = 0.0
    m = len(pv)
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * pv[idx])
        run = max(run, val)
        holm[idx] = run
    pa_df["p_holm"] = holm
    pa_df["family"] = "one dataset x WorstGroupRMSE (5 contrasts)"
    pa_df.to_csv(OUT / "WORSTGROUP_PAIRED.csv", index=False)

    # ---------------- non-inferiority (AM-5 labels) ------------------------------------
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

    ni_rows = []
    for ds in ("sensorscope", "uair"):
        for arm in TRAINED_ARMS:
            for comp in ("fedavg_window", "raven"):
                pa, pb = piv[ds][arm], piv[ds][comp]
                rel = ((pa["WorstGroupRMSE_canonical"] - pb["WorstGroupRMSE_canonical"])
                       / pb["WorstGroupRMSE_canonical"]).dropna().to_numpy(float)
                rng = np.random.default_rng(BOOT_SEED)
                boot = np.array([rel[rng.choice(len(rel), len(rel), replace=True)].mean()
                                 for _ in range(BOOT_N)])
                lo, hi = float(np.percentile(boot, 5)), float(np.percentile(boot, 95))
                p_raw = float(np.mean(boot >= DELTA_WG))
                ni_rows.append({"ds": ds, "arm": arm, "comparator": comp,
                                "mean_rel_diff": float(rel.mean()),
                                "ci90_lo": lo, "ci90_hi": hi, "margin": DELTA_WG,
                                "label_AM5": am5(lo, hi, DELTA_WG), "p_raw": p_raw,
                                "mean_wg_arm": float(pa["WorstGroupRMSE_canonical"].mean()),
                                "mean_wg_comparator": float(pb["WorstGroupRMSE_canonical"].mean()),
                                "n_seeds": int(len(rel))})
    ni = pd.DataFrame(ni_rows)
    for ds, g in ni.groupby("ds"):
        idx = g.index.to_numpy()
        pvv = g["p_raw"].to_numpy(float)
        order = np.argsort(pvv)
        adj = np.empty_like(pvv)
        run = 0.0
        mm = len(pvv)
        for rank, k in enumerate(order):
            val = min(1.0, (mm - rank) * pvv[k])
            run = max(run, val)
            adj[k] = run
        ni.loc[idx, "p_holm"] = adj
    ni["family"] = "one dataset x NI (3 trained arms x 2 comparators)"
    ni.to_csv(OUT / "WORSTGROUP_NI.csv", index=False)

    # ---------------- TRADEOFF_V51 ------------------------------------------------------
    tr = pd.read_csv(ROOT / "results_w1_ladder/round_v4/TRADEOFF.csv")
    key = ["ds", "arm", "seed"]
    mp = canon.set_index(key)
    tr = tr.set_index(key)
    for col in ("RMSE_mu", "Head_RMSE", "Tail_RMSE"):
        tr[col] = mp[col]
    tr["WorstGroupRMSE"] = mp["WorstGroupRMSE_canonical"]
    tr["argmax_group"] = mp["argmax_group"]
    tr["source"] = mp["source"]
    tr["Delta_group"] = mp["Delta_group"] if "Delta_group" in mp else tr["Delta_group"]
    tr.reset_index().to_csv(OUT / "TRADEOFF_V51.csv", index=False)

    means = (canon.groupby(["ds", "arm"])[["RMSE_mu_canonical", "WorstGroupRMSE_canonical",
                                           "WG_R0", "WG_R1", "WG_R2", "WG_R3"]]
             .mean().round(8).reset_index())
    summary = {"gates": gates,
               "argmax_group_all_R2": bool((canon.argmax_group == 2).all()),
               "argmax_group_counts": {int(k): int(v) for k, v
                                       in canon.argmax_group.value_counts().items()},
               "means": means.to_dict("records"),
               "paired": pa_df.to_dict("records"), "ni": ni.to_dict("records")}
    (OUT / "A2P_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str),
                                          encoding="utf-8")
    print(json.dumps(gates, indent=2, default=str))
    print(means.to_string(index=False))
    print(ni.to_string(index=False))


if __name__ == "__main__":
    main()
