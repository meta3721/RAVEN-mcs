"""W1 round v5.1 - reconnaissance (read-only).

Purpose: pin down the *theta-canonical* prediction path before any v5.1 number is
computed.  Compares, for the U-Air trigger seeds, three ways of scoring the same
checkpoint:

  A. runner path   : build_full_runner (config_snapshot.json + frozen EventTrace,
                     sealed support, target bundle) -> load checkpoints/final.pt ->
                     raven_mcs.e3.real_runner.runner._predict(runner, ds, "test")
                     -> rmse_mu / _head_tail_rmse / _wrmse_block      (== w1_v5_a2.py)
  B. theta path    : load_paper_dataset + apply_sealed_opportunity_stratum ->
                     CommonNDMF.load_state_dict(theta) -> unit loop
                     -> rmse_mu / _head_tail_rmse / _wrmse_block      (== c_impact_recalc.py)
  C. plain path    : load_paper_dataset (no sealing) -> same model loop

Reference values compared against: the run's own final_metrics.json, and the frozen
public table RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv.

Writes only results_w1_ladder/round_v5_1/recon/*.json.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
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
from raven_mcs.models.common_ndmf import CommonNDMF                            # noqa: E402
from raven_mcs.models.features import extract_features                         # noqa: E402
from raven_mcs.simulation.event_trace import load_event_trace                  # noqa: E402
from raven_mcs.training.window_runner import build_full_runner                 # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5_1/recon"
E3 = ROOT / "artifacts/e3_formal_runs_r1"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
STORED = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv"
TRIGGER_SEEDS = (30007, 30016, 30018)
ARMS = ("uniform_window", "proj_beta", "proj_beta_debt",
        "fedavg_window", "inst_cal", "raven")


def block_of(label: str) -> int:
    for part in str(label).split("::"):
        if part.startswith("block"):
            return int(part[5:])
    return -1


def run_dir_of(ds: str, arm: str, seed: int) -> pathlib.Path:
    if arm in ("uniform_window", "proj_beta", "proj_beta_debt"):
        return TRAIN / ds / arm / f"seed{seed}"
    return E3 / "runs" / ds / arm / f"seed{seed}"


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
    yt, yp, gids, gstr, uids = [], [], [], [], []
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
            uids.append(u.unit_id)
    return {"y_true": np.asarray(yt, dtype=np.float64),
            "y_pred": np.asarray(yp, dtype=np.float64),
            "groups": np.asarray(gids, dtype=int), "group_strs": gstr,
            "unit_ids": uids}


def metrics(pred: dict, mu: np.ndarray, head_ids, tail_ids) -> dict:
    mu_w = _mu_weights_for_test(pred, mu)
    rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w))
    head, tail = _head_tail_rmse(pred, mu_w, list(head_ids), list(tail_ids))
    blocks = np.asarray([block_of(g) for g in pred["group_strs"]], dtype=int)
    wg = [float(p2._wrmse_block(pred["y_true"], pred["y_pred"], blocks == g, mu_w))
          for g in range(4)]
    arr = np.asarray(wg, dtype=float)
    return {"RMSE_mu": rmse, "Head_RMSE": float(head), "Tail_RMSE": float(tail),
            "WorstGroupRMSE": float(np.nanmax(arr)) if np.isfinite(arr).any() else None,
            "WG": [float(x) for x in wg],
            "n_units": int(len(pred["y_true"])),
            "n_groups_present": int(len(np.unique(pred["groups"])))}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dsname = "uair"
    ds_plain = load_paper_dataset(ROOT, dsname)
    mapping = load_spatial_to_client(ROOT, dsname)
    atomic_sealed, stratum_meta = apply_sealed_opportunity_stratum(
        ds_plain.atomic_df, dataset=dsname, root=ROOT)
    sealed_by_unit = {str(r.unit_id): str(r.opportunity_stratum)
                      for r in atomic_sealed.itertuples(index=False)}
    ds_sealed = ds_plain
    ds_sealed._atomic_df = ds_plain._atomic_df.copy()
    ds_sealed._atomic_df["opportunity_stratum"] = [
        sealed_by_unit.get(str(uid), str(s))
        for uid, s in zip(ds_sealed._atomic_df["unit_id"].tolist(),
                          ds_sealed._atomic_df["opportunity_stratum"].tolist())]
    bundle = production_target_bundle(root=ROOT, dataset_name=dsname, dataset=ds_sealed)
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    ht = bundle["head_tail"]
    atomic_for_pi = atomic_sealed.copy()
    if "target_group_main" not in atomic_for_pi.columns:
        atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"].astype(str)
    pi_frame = build_pi_target(atomic_for_pi, mapping, split="test")
    pi_target = {(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
                 for r in pi_frame.itertuples()}
    stored = {}
    import pandas as pd
    d = pd.read_csv(STORED)
    for r in d.itertuples(index=False):
        stored[(str(r.dataset), str(r.method), int(r.seed))] = {
            "RMSE_mu": float(r.RMSE_mu), "WorstGroupRMSE": float(r.WorstGroupRMSE)}
    plain_units = ds_plain.get_atomic_units(split="test")
    sealed_units = ds_sealed.get_atomic_units(split="test")
    out = {"dataset": dsname,
           "n_test_units_plain": len(plain_units),
           "n_test_units_sealed": len(sealed_units),
           "mu": [float(x) for x in mu],
           "sealed_units_differ": None, "rows": []}
    # do the two dataset copies give the same test unit set?
    idp = sorted(str(u.unit_id) for u in plain_units)
    ids = sorted(str(u.unit_id) for u in sealed_units)
    out["sealed_units_differ"] = bool(idp != ids)
    out["n_plain"], out["n_sealed"] = len(idp), len(ids)
    prefix = 0
    while prefix < min(len(idp), len(ids)) and idp[prefix] == ids[prefix]:
        prefix += 1
    out["first_unit_id_diff_index"] = None if idp == ids else prefix
    for arm in ARMS:
        for seed in TRIGGER_SEEDS:
            rd = run_dir_of(dsname, arm, seed)
            fm = json.loads((rd / "final_metrics.json").read_text(encoding="utf-8"))
            ckpt = rd / "checkpoints" / "final.pt"
            theta = load_theta(ckpt)
            row = {"arm": arm, "seed": seed}
            # ---- B: theta path on the sealed dataset
            model = CommonNDMF(num_spatial=ds_sealed.num_spatial)
            model.load_state_dict(theta)
            pred_b = predict_model(model, ds_sealed)
            row["theta_sealed"] = metrics(pred_b, mu, ht["head_group_ids"],
                                          ht["tail_group_ids"])
            # ---- C: theta path on the plain dataset
            model2 = CommonNDMF(num_spatial=ds_plain.num_spatial)
            model2.load_state_dict(theta)
            pred_c = predict_model(model2, ds_plain)
            row["theta_plain"] = metrics(pred_c, mu, ht["head_group_ids"],
                                         ht["tail_group_ids"])
            # ---- A: runner path
            cfg = json.loads((rd / "config_snapshot.json").read_text(encoding="utf-8"))
            trace, _ = load_event_trace(E3 / "eventtraces" / dsname / f"seed{seed}"
                                        / "training_eventtrace")
            runner = build_full_runner(
                trace, ds_sealed, method=str(cfg["method"]),
                n_groups=int(bundle["n_groups_runtime"]), model_seed=int(cfg["seed"]),
                local_steps=int(cfg["local_steps"]), target_mu=mu, pi_target=pi_target,
                s_max=int(trace.metadata.s_max), device="cpu", use_coarse_time_groups=False,
                pi_opp_joint={})
            runner.model.load_state_dict(theta)
            runner.theta = theta
            runner.model.eval()
            pred_a = _predict(runner, ds_sealed, split="test")
            row["runner_sealed"] = metrics(pred_a, mu, ht["head_group_ids"],
                                           ht["tail_group_ids"])
            # prediction-array agreement
            row["d_pred_theta_sealed_vs_runner"] = float(
                np.max(np.abs(pred_b["y_pred"] - pred_a["y_pred"])))
            row["d_pred_theta_plain_vs_theta_sealed"] = float(
                np.max(np.abs(pred_c["y_pred"] - pred_b["y_pred"])))
            row["units_equal_theta_sealed_vs_runner"] = bool(
                [str(x) for x in pred_b["unit_ids"]] == [str(x) for x in pred_a["unit_ids"]])
            row["final_metrics"] = {k: fm.get(k) for k in
                                    ("RMSE_mu", "Head_RMSE", "Tail_RMSE", "WorstGroupRMSE")}
            row["stored_tableII"] = stored.get((dsname, arm, seed))
            for tag in ("theta_sealed", "theta_plain", "runner_sealed"):
                for k in ("RMSE_mu", "Head_RMSE", "Tail_RMSE", "WorstGroupRMSE"):
                    v = row[tag].get(k)
                    if v is not None and fm.get(k) is not None:
                        row["d_%s_%s_vs_final_metrics" % (tag, k)] = abs(v - float(fm[k]))
                    st = row["stored_tableII"] or {}
                    if v is not None and st.get(k) is not None:
                        row["d_%s_%s_vs_tableII" % (tag, k)] = abs(v - float(st[k]))
            out["rows"].append(row)
            print("recon %-18s seed%d theta_sealed RMSE=%.10f runner RMSE=%.10f "
                  "final=%.10f tableII=%s" % (
                      arm, seed, row["theta_sealed"]["RMSE_mu"],
                      row["runner_sealed"]["RMSE_mu"], float(fm["RMSE_mu"]),
                      (stored.get((dsname, arm, seed)) or {}).get("RMSE_mu")), flush=True)
    (OUT / "RECON_TRIGGER.json").write_text(json.dumps(out, indent=2, default=str),
                                            encoding="utf-8")
    print("wrote", OUT / "RECON_TRIGGER.json")


if __name__ == "__main__":
    main()
