"""W1 round v5 - A2 (R3): worst-group re-scoring from frozen checkpoints.

Read-only.  Writes only under results_w1_ladder/round_v5/.  No training, no retraining,
no edits to round_v1..v4, artifacts/, or src/.

A2-G0   : rebuild each run with build_full_runner (same factory as run_e3_real) from the
          run's config_snapshot.json + the frozen EventTrace, load checkpoints/final.pt,
          predict the test split with runner._predict, recompute RMSE_mu / Head_RMSE /
          Tail_RMSE; pass if all three are <= 1e-10 vs final_metrics.json.  Frozen arms
          additionally reproduce the stored WorstGroupRMSE of
          RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv <= 1e-10.
A2-score: WorstGroupRMSE = max_g wRMSE_g over the four UTC six-hour blocks, using the
          mu-weights (_mu_weights_for_test) and the verbatim _wrmse_block of
          scripts/run_joint_ou_cs_p2.py (the function used by
          scripts/run_nodesign_supplement.py L234-239).  Stores WG_R0..R3 and argmax_group.

Usage:
    python scripts/w1_v5_a2.py --run --datasets sensorscope --group trained
    python scripts/w1_v5_a2.py --merge
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
from raven_mcs.correction.pi_target import build_pi_target                     # noqa: E402
from raven_mcs.e3.canary.dataset_load import (                                 # noqa: E402
    load_paper_dataset,
    load_spatial_to_client,
)
from raven_mcs.e3.real_runner.runner import (                                  # noqa: E402
    _head_tail_rmse,
    _mu_weights_for_test,
    _predict,
)
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum   # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle    # noqa: E402
from raven_mcs.metrics.accuracy import rmse_mu                                 # noqa: E402
from raven_mcs.simulation.event_trace import load_event_trace                  # noqa: E402
from raven_mcs.training.window_runner import build_full_runner                  # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5"
E3 = ROOT / "artifacts/e3_formal_runs_r1"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
STORED = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv"
TRAINED_ARMS = ("uniform_window", "proj_beta", "proj_beta_debt")
FROZEN_ARMS = ("fedavg_window", "inst_cal", "raven")
SEEDS = list(range(30001, 30021))
G0_TOL = 1e-10
_DSC: dict = {}


def block_of(label: str) -> int:
    for part in str(label).split("::"):
        if part.startswith("block"):
            return int(part[5:])
    return -1


def ds_setup(ds_name: str) -> dict:
    """Dataset + frozen target bundle + sealed support, cached per dataset."""
    if ds_name in _DSC:
        return _DSC[ds_name]
    ds = load_paper_dataset(ROOT, ds_name)
    mapping = load_spatial_to_client(ROOT, ds_name)
    atomic_sealed, stratum_meta = apply_sealed_opportunity_stratum(
        ds.atomic_df, dataset=ds_name, root=ROOT)
    sealed_by_unit = {str(r.unit_id): str(r.opportunity_stratum)
                      for r in atomic_sealed.itertuples(index=False)}
    ds._atomic_df = ds._atomic_df.copy()
    ds._atomic_df["opportunity_stratum"] = [
        sealed_by_unit.get(str(uid), str(s))
        for uid, s in zip(ds._atomic_df["unit_id"].tolist(),
                          ds._atomic_df["opportunity_stratum"].tolist())
    ]
    bundle = production_target_bundle(root=ROOT, dataset_name=ds_name, dataset=ds)
    atomic_for_pi = atomic_sealed.copy()
    if "target_group_main" not in atomic_for_pi.columns:
        atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"].astype(str)
    pi_frame = build_pi_target(atomic_for_pi, mapping, split="test")
    pi_target = {(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
                 for r in pi_frame.itertuples()}
    _DSC[ds_name] = {"ds": ds, "mapping": mapping, "bundle": bundle,
                     "pi_target": pi_target, "stratum_meta": stratum_meta}
    return _DSC[ds_name]


def run_dir_of(ds_name: str, arm: str, seed: int) -> pathlib.Path:
    if arm in TRAINED_ARMS:
        return TRAIN / ds_name / arm / f"seed{seed}"
    return E3 / "runs" / ds_name / arm / f"seed{seed}"


def evaluate(ds_name: str, arm: str, seed: int) -> dict:
    t0 = time.perf_counter()
    setup = ds_setup(ds_name)
    ds, bundle = setup["ds"], setup["bundle"]
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    ht = bundle["head_tail"]
    run_dir = run_dir_of(ds_name, arm, seed)
    cfg = json.loads((run_dir / "config_snapshot.json").read_text(encoding="utf-8"))
    fm = json.loads((run_dir / "final_metrics.json").read_text(encoding="utf-8"))
    trace, _identity = load_event_trace(E3 / "eventtraces" / ds_name / f"seed{seed}"
                                        / "training_eventtrace")
    runner = build_full_runner(
        trace, ds,
        method=str(cfg["method"]),
        n_groups=int(bundle["n_groups_runtime"]),
        model_seed=int(cfg["seed"]),
        local_steps=int(cfg["local_steps"]),
        target_mu=mu,
        pi_target=setup["pi_target"],
        s_max=int(trace.metadata.s_max),
        device="cpu",
        use_coarse_time_groups=False,
        pi_opp_joint={},
    )
    ckpt = run_dir / "checkpoints" / "final.pt"
    if not ckpt.is_file():
        return {"ds": ds_name, "arm": arm, "seed": seed, "source": "frozen_record",
                "status": "no_checkpoint",
                "RMSE_mu": fm.get("RMSE_mu"), "Head_RMSE": fm.get("Head_RMSE"),
                "Tail_RMSE": fm.get("Tail_RMSE"),
                "WorstGroupRMSE": fm.get("WorstGroupRMSE"),
                "g0_pass": None, "seconds": time.perf_counter() - t0}
    payload = torch.load(ckpt, map_location="cpu")
    if isinstance(payload, dict) and "state_dict" in payload:
        payload = payload["state_dict"]
    runner.model.load_state_dict(payload)
    runner.theta = payload
    runner.model.eval()
    pred = _predict(runner, ds, split="test")
    mu_w = _mu_weights_for_test(pred, mu)
    gids = pred["groups"]
    rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w))
    head, tail = _head_tail_rmse(pred, mu_w, list(ht["head_group_ids"]),
                                 list(ht["tail_group_ids"]))
    blocks = np.asarray([block_of(g) for g in pred["group_strs"]], dtype=int)
    if int(blocks.min()) < 0:
        raise RuntimeError("unparsable target-group block label")
    wg = [float(p2._wrmse_block(pred["y_true"], pred["y_pred"], blocks == g, mu_w))
          for g in range(4)]
    arr = np.asarray(wg, dtype=float)
    worst = float(np.nanmax(arr)) if np.isfinite(arr).any() else float("nan")
    argmax = int(np.nanargmax(arr)) if np.isfinite(arr).any() else -1
    d_rmse = abs(rmse - float(fm["RMSE_mu"]))
    d_head = abs(head - float(fm["Head_RMSE"]))
    d_tail = abs(tail - float(fm["Tail_RMSE"]))
    row = {"ds": ds_name, "arm": arm, "seed": seed, "source": "checkpoint",
           "status": "ok", "n_test_units": int(len(pred["y_true"])),
           "RMSE_mu": rmse, "RMSE_mu_stored": float(fm["RMSE_mu"]), "d_rmse": d_rmse,
           "Head_RMSE": head, "Head_RMSE_stored": float(fm["Head_RMSE"]), "d_head": d_head,
           "Tail_RMSE": tail, "Tail_RMSE_stored": float(fm["Tail_RMSE"]), "d_tail": d_tail,
           "WorstGroupRMSE": worst, "argmax_group": argmax,
           "WG_R0": wg[0], "WG_R1": wg[1], "WG_R2": wg[2], "WG_R3": wg[3],
           "WG_stored": None, "d_wg_stored": None, "g0_wg_stored_pass": None,
           "g0_pass": bool(d_rmse <= G0_TOL and d_head <= G0_TOL and d_tail <= G0_TOL),
           "seconds": time.perf_counter() - t0}
    if arm in FROZEN_ARMS:
        st = stored_wg()
        key = (ds_name, arm, seed)
        if key in st:
            row["WG_stored"] = st[key]
            row["d_wg_stored"] = abs(worst - st[key])
            row["g0_wg_stored_pass"] = bool(abs(worst - st[key]) <= G0_TOL)
        else:
            row["source"] = "checkpoint"
    return row


_SWG: dict = {}


def stored_wg() -> dict:
    if not _SWG:
        d = pd.read_csv(STORED)
        for r in d.itertuples(index=False):
            _SWG[(str(r.dataset), str(r.method), int(r.seed))] = float(r.WorstGroupRMSE)
    return _SWG


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--datasets", default="sensorscope,uair")
    ap.add_argument("--group", default="trained", choices=["trained", "frozen"])
    ap.add_argument("--seeds", default="all")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.run:
        arms = TRAINED_ARMS if args.group == "trained" else FROZEN_ARMS
        seeds = SEEDS if args.seeds == "all" else [int(x) for x in args.seeds.split(",")]
        for ds_name in [d for d in args.datasets.split(",") if d]:
            rows = []
            for arm in arms:
                for seed in seeds:
                    r = evaluate(ds_name, arm, seed)
                    rows.append(r)
                    print("a2 %s %s %d rmse=%.10f d=%.2e head=%.2e tail=%.2e wg=%.6f "
                          "g0=%s sec=%.1f"
                          % (ds_name, arm, seed, r.get("RMSE_mu") or float("nan"),
                             r.get("d_rmse") or float("nan"), r.get("d_head") or float("nan"),
                             r.get("d_tail") or float("nan"),
                             r.get("WorstGroupRMSE") or float("nan"), r.get("g0_pass"),
                             r.get("seconds") or float("nan")), flush=True)
            pd.DataFrame(rows).to_csv(
                OUT / ("A2_part_%s_%s.csv" % (args.group, ds_name)), index=False)
            print("part written %s %s" % (args.group, ds_name), flush=True)
    if args.merge:
        parts = sorted(OUT.glob("A2_part_*.csv"))
        df = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
        df = df.sort_values(["ds", "arm", "seed"]).reset_index(drop=True)
        # independent checkpoint-based reference already published in-repo (read-only)
        ref = pd.read_csv(STORED)
        ref = ref[ref.dataset.isin(["sensorscope", "uair"])]
        ref = ref.rename(columns={"dataset": "ds", "method": "arm"})
        df = df.merge(ref[["ds", "arm", "seed", "RMSE_mu", "WorstGroupRMSE"]]
                      .rename(columns={"RMSE_mu": "pub_RMSE_mu",
                                       "WorstGroupRMSE": "pub_WorstGroupRMSE"}),
                      on=["ds", "arm", "seed"], how="left")
        df["d_pub_rmse"] = (df.RMSE_mu - df.pub_RMSE_mu).abs()
        df["d_pub_wg"] = (df.WorstGroupRMSE - df.pub_WorstGroupRMSE).abs()
        df["a2_status"] = np.where(df.g0_pass.astype(bool), "G0 pass",
                                   "G0 FAILED -> A2 stopped")
        df.to_csv(OUT / "WORSTGROUP_V5.csv", index=False)
        bad = df[df.g0_pass.isna() | (~df.g0_pass.astype(bool))]
        bad_wg = df[df.g0_wg_stored_pass.notna() & (~df.g0_wg_stored_pass.astype(bool))]
        fail_cells = (bad.groupby(["ds", "arm"])["seed"]
                      .apply(lambda s: sorted(int(x) for x in s)).to_dict())
        summary = {
            "round": "round_v5",
            "protocol": "A2-G0 (PROTOCOL.md A2, PREREG 2.6)",
            "n_rows": int(len(df)),
            "n_checkpoint": int((df.source == "checkpoint").sum()),
            "n_frozen_record": int((df.source == "frozen_record").sum()),
            "g0_pass_rows": int(df.g0_pass.astype(bool).sum()),
            "g0_fail_rows": int(len(bad)),
            "g0_fail_cells": {"%s|%s" % k: v for k, v in fail_cells.items()},
            "g0_fail_seeds_uair": sorted({int(s) for s in bad.seed.unique()}),
            "g0_max_d_rmse": float(df.d_rmse.max()),
            "g0_max_d_head": float(df.d_head.max()),
            "g0_max_d_tail": float(df.d_tail.max()),
            "g0_max_d_rmse_by_ds": {d: float(g.d_rmse.max()) for d, g in df.groupby("ds")},
            "g0_stored_wg_rows": int(df.g0_wg_stored_pass.notna().sum()),
            "g0_stored_wg_pass": int(df.g0_wg_stored_pass.fillna(False).astype(bool).sum()),
            "g0_stored_wg_fail": int(len(bad_wg)),
            "g0_stored_wg_max_diff": None if df.d_wg_stored.isna().all()
            else float(df.d_wg_stored.max()),
            "agreement_with_published_checkpoint_table_max_d_rmse":
                float(df.d_pub_rmse.max()),
            "agreement_with_published_checkpoint_table_max_d_wg":
                float(df.d_pub_wg.max()),
            "agreement_with_published_checkpoint_table_max_d_rmse_uair":
                float(df[df.ds == "uair"].d_pub_rmse.max()),
            "g0_pass": bool(len(bad) == 0 and len(bad_wg) == 0),
            "stop_rule": ("PROTOCOL.md A2-G0: 'One failure => stop A2 and report; do not "
                          "fall back to retraining without asking.'"),
            "consequence": ("A2 stopped before A2-score/A2-analysis: WORSTGROUP_PAIRED.csv, "
                            "WORSTGROUP_NI.csv and the WorstGroupRMSE column of "
                            "TRADEOFF_V5.csv are TBD. SensorScope passed 120/120 G0 rows; "
                            "U-Air failed 18/120 (6 arms x seeds 30007/30016/30018)."),
        }
        (OUT / "A2_G0_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str),
                                                encoding="utf-8")
        print(json.dumps(summary, indent=2, default=str))
        # ---- the U-Air failure table (report evidence)
        bad[["ds", "arm", "seed", "RMSE_mu", "RMSE_mu_stored", "d_rmse", "d_head", "d_tail",
             "pub_RMSE_mu", "pub_WorstGroupRMSE", "WorstGroupRMSE", "d_wg_stored",
             "d_pub_rmse", "d_pub_wg"]].to_csv(OUT / "A2_G0_FAILURES.csv", index=False)
        if not summary["g0_pass"]:
            ni_cols = ["ds", "arm", "comparator", "mean_rel_diff", "ub95_one_sided", "margin",
                       "verdict", "p_holm"]
            pd.DataFrame([{c: ("TBD" if c not in ("ds", "arm", "comparator") else
                               "TBD_A2_G0_STOP") for c in ni_cols}]).to_csv(
                OUT / "WORSTGROUP_NI.csv", index=False)
            pa_cols = ["ds", "endpoint", "contrast", "status", "n_seeds", "mean_diff",
                       "ci_lo", "ci_hi", "p_wilcoxon", "p_holm"]
            pd.DataFrame([{c: "TBD_A2_G0_STOP" for c in pa_cols}]).to_csv(
                OUT / "WORSTGROUP_PAIRED.csv", index=False)
            tr = pd.read_csv(ROOT / "results_w1_ladder/round_v4/TRADEOFF.csv")
            tr["WorstGroupRMSE"] = np.nan
            tr["WG_status"] = "TBD_A2_G0_STOP"
            tr.to_csv(OUT / "TRADEOFF_V5.csv", index=False)
            (OUT / "A2_STOP.json").write_text(json.dumps(
                {"stopped": True, "at": "A2-G0", "detail": summary,
                 "files_written": ["WORSTGROUP_V5.csv (G0 evidence only)",
                                   "A2_G0_SUMMARY.json", "A2_G0_FAILURES.csv",
                                   "WORSTGROUP_PAIRED.csv (TBD stub)",
                                   "WORSTGROUP_NI.csv (TBD stub)",
                                   "TRADEOFF_V5.csv (v4 columns + empty WG column, TBD)"]},
                indent=2, default=str), encoding="utf-8")
            print("A2 STOP: G0 failed; scoring/analysis files are TBD stubs.")
            return
        # ---- descriptive means per arm (no pooling across datasets)
        means = (df.groupby(["ds", "arm"])[
            ["RMSE_mu", "WorstGroupRMSE", "WG_R0", "WG_R1", "WG_R2", "WG_R3"]]
            .mean().round(6).reset_index())
        means.to_csv(OUT / "A2_MEANS.csv", index=False)
        print(means.to_string(index=False))
        # ---- paired contrasts (same list as round_v4/TRADEOFF_PAIRED.csv)
        pairs = (("proj_beta", "uniform_window"), ("raven", "proj_beta"),
                 ("proj_beta", "fedavg_window"), ("uniform_window", "fedavg_window"),
                 ("proj_beta_debt", "proj_beta"))
        rows = []
        for ds_name in sorted(df.ds.unique()):
            piv = {a: g.set_index("seed") for a, g in df[df.ds == ds_name].groupby("arm")}
            for a, b in pairs:
                if a not in piv or b not in piv:
                    rows.append({"ds": ds_name, "endpoint": "WorstGroupRMSE",
                                 "contrast": "%s - %s" % (a, b), "status": "missing"})
                    continue
                d = (piv[a]["WorstGroupRMSE"] - piv[b]["WorstGroupRMSE"]).dropna().to_numpy(float)
                from scipy import stats
                rng = np.random.default_rng(20261002)
                boot = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                                 for _ in range(10_000)])
                try:
                    p = float(stats.wilcoxon(d).pvalue)
                except Exception:                                      # noqa: BLE001
                    p = float("nan")
                rows.append({"ds": ds_name, "endpoint": "WorstGroupRMSE",
                             "contrast": "%s - %s" % (a, b), "status": "ok",
                             "n_seeds": int(len(d)), "mean_diff": float(d.mean()),
                             "rel_diff": float(d.mean() / piv[b]["WorstGroupRMSE"].mean()),
                             "ci_lo": float(np.percentile(boot, 2.5)),
                             "ci_hi": float(np.percentile(boot, 97.5)),
                             "p_wilcoxon": p,
                             "mean_wg_a": float(piv[a]["WorstGroupRMSE"].mean()),
                             "mean_wg_b": float(piv[b]["WorstGroupRMSE"].mean()),
                             "argmax_a": int(piv[a]["argmax_group"].mode().iloc[0]),
                             "argmax_b": int(piv[b]["argmax_group"].mode().iloc[0]),
                             "argmax_changed_seeds": int((piv[a]["argmax_group"]
                                                          != piv[b]["argmax_group"]).sum())})
        pa = pd.DataFrame(rows)
        ok = pa.status == "ok"
        pv = pa.loc[ok, "p_wilcoxon"].to_numpy(float)
        order = np.argsort(pv)
        holm = np.empty_like(pv)
        run = 0.0
        m = len(pv)
        for rank, idx in enumerate(order):
            val = min(1.0, (m - rank) * pv[idx])
            run = max(run, val)
            holm[idx] = run
        pa.loc[ok, "p_holm"] = holm
        pa["family"] = "one dataset x WorstGroupRMSE (5 contrasts)"
        pa.to_csv(OUT / "WORSTGROUP_PAIRED.csv", index=False)
        # ---- non-inferiority
        ni_rows = []
        for ds_name in sorted(df.ds.unique()):
            piv = {a: g.set_index("seed") for a, g in df[df.ds == ds_name].groupby("arm")}
            for arm in TRAINED_ARMS:
                for comp in ("fedavg_window", "raven"):
                    if arm not in piv or comp not in piv:
                        continue
                    rel = ((piv[arm]["WorstGroupRMSE"] - piv[comp]["WorstGroupRMSE"])
                           / piv[comp]["WorstGroupRMSE"]).dropna().to_numpy(float)
                    rng = np.random.default_rng(20261002)
                    boot = np.array([rel[rng.choice(len(rel), len(rel), replace=True)].mean()
                                     for _ in range(10_000)])
                    margin = 0.005      # delta_WG = +0.5 % of the comparator mean, relative units
                    ub = float(np.percentile(boot, 95))
                    lb = float(np.percentile(boot, 5))
                    p_raw = float(np.mean(boot >= margin))
                    if ub < margin:
                        verdict = "non-inferior"
                    elif ub > margin and lb > 0:
                        verdict = "inferior"
                    else:
                        verdict = "inconclusive"
                    ni_rows.append({"ds": ds_name, "arm": arm, "comparator": comp,
                                    "mean_rel_diff": float(rel.mean()),
                                    "lb95_one_sided": lb, "ub95_one_sided": ub,
                                    "margin": margin, "verdict": verdict,
                                    "p_raw": p_raw,
                                    "mean_wg_arm": float(piv[arm]["WorstGroupRMSE"].mean()),
                                    "mean_wg_comparator": float(piv[comp]["WorstGroupRMSE"].mean()),
                                    "n_seeds": int(len(rel))})
        ni = pd.DataFrame(ni_rows)
        for ds_name, g in ni.groupby("ds"):
            idx = g.index.to_numpy()
            pv = g["p_raw"].to_numpy(float)
            order = np.argsort(pv)
            holm = np.empty_like(pv)
            run = 0.0
            m = len(pv)
            for rank, k in enumerate(order):
                val = min(1.0, (m - rank) * pv[k])
                run = max(run, val)
                holm[k] = run
            ni.loc[idx, "p_holm"] = holm
        ni["family"] = "one dataset x NI (3 trained arms x 2 comparators)"
        ni.to_csv(OUT / "WORSTGROUP_NI.csv", index=False)
        # ---- TRADEOFF_V5: v4 columns + filled WorstGroupRMSE
        tr = pd.read_csv(ROOT / "results_w1_ladder/round_v4/TRADEOFF.csv")
        wg = df.set_index(["ds", "arm", "seed"])[["WorstGroupRMSE"]]
        tr = tr.set_index(["ds", "arm", "seed"])
        tr["WorstGroupRMSE"] = wg["WorstGroupRMSE"]
        tr["argmax_group"] = df.set_index(["ds", "arm", "seed"])["argmax_group"]
        tr["WG_source"] = df.set_index(["ds", "arm", "seed"])["source"]
        tr.reset_index().to_csv(OUT / "TRADEOFF_V5.csv", index=False)
        print(pa.to_string(index=False))
        print(ni.to_string(index=False))


if __name__ == "__main__":
    main()
