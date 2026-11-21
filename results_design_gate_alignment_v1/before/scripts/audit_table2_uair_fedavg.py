#!/usr/bin/env python3
"""Audit the U-Air FedAvg-Window cell of Table II.

The frozen U-Air FedAvg-Window runs (artifacts/e3_formal_runs_r1, 2026-08-11)
drop clients whose (client, stratum) has pi_tar = 0, like the Design-on methods;
FedAU-Window, ObsUse-Window and RAVEN-NoDesign on the same block keep them.
This re-runs FedAvg-Window on the 20 formal seeds with the current runner, which
keeps every delivered client, recomputes WorstGroupRMSE exactly as the Table II
per-seed file does, and compares against the frozen per-seed rows.
Writes results_table2_audit/ only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h_headroom as h  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import _mu_weights_for_test, _predict_model  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle  # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

OUT = ROOT / "results_table2_audit"
PER_SEED = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1" / "tables" / "TABLE_II_WORSTGROUP_PER_SEED.csv"
SEEDS = list(range(30001, 30021))
TEST_SEEDS = list(range(30011, 30021))
TOL = 1e-6


def block_rmse(ckpt: Path, ds, mu: np.ndarray) -> dict[str, float]:
    model = CommonNDMF(num_spatial=ds.num_spatial)
    model.load_state_dict(torch.load(ckpt, map_location="cpu"))
    model.eval()
    pred = _predict_model(model, ds)
    w = _mu_weights_for_test(pred, mu)
    blocks = np.asarray([h._block_of(g) for g in pred["group_strs"]])
    err2 = (pred["y_true"] - pred["y_pred"]) ** 2
    out = {"RMSE_mu": float(np.sqrt(np.sum(w * err2)))}
    for b in range(4):
        m = blocks == b
        wb = w[m] / w[m].sum()
        out[f"RMSE_block{b}"] = float(np.sqrt(np.sum(wb * err2[m])))
    out["WorstGroupRMSE"] = max(out[f"RMSE_block{b}"] for b in range(4))
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ds = load_paper_dataset(ROOT, "uair")
    mu = np.asarray(production_target_bundle(root=ROOT, dataset_name="uair", dataset=ds)["mu"], dtype=np.float64)
    frozen = pd.read_csv(PER_SEED)
    frozen = frozen[frozen["dataset"] == "uair"]

    ref = block_rmse(h.FROZEN_E3 / "runs" / "uair" / "fedavg_window" / "seed30001" / "checkpoints" / "final.pt", ds, mu)
    ref_row = frozen[(frozen["method"] == "fedavg_window") & (frozen["seed"] == 30001)].iloc[0]
    check = {k: (ref[k], float(ref_row[k])) for k in ("RMSE_mu", "WorstGroupRMSE")}
    if any(abs(a - b) > TOL for a, b in check.values()):
        raise SystemExit(f"WorstGroup recomputation does not match the Table II per-seed file: {check}")

    rows = []
    for seed in SEEDS:
        run = h.run_arm("C0_frozen", "uair", "fedavg_window", seed, tag="table2_audit")
        ck = h.OUT / "table2_audit" / "C0_frozen" / "uair" / "fedavg_window" / f"seed{seed}" / "checkpoints" / "final.pt"
        met = block_rmse(ck, ds, mu)
        if abs(met["RMSE_mu"] - float(run["RMSE_mu"])) > TOL:
            raise RuntimeError(f"seed{seed}: recomputed RMSE_mu != runner RMSE_mu")
        rows.append({"method": "fedavg_window_current", "seed": seed, **met})
        print(f"seed{seed} RMSE_mu={met['RMSE_mu']:.6f} WG={met['WorstGroupRMSE']:.6f}", flush=True)
    cur = pd.DataFrame(rows)
    cur.to_csv(OUT / "uair_fedavg_current_per_seed.csv", index=False)

    table = frozen[["method", "seed", "RMSE_mu", "WorstGroupRMSE"]].copy()
    table = pd.concat([table, cur[["method", "seed", "RMSE_mu", "WorstGroupRMSE"]]], ignore_index=True)
    summary = table.groupby("method")[["RMSE_mu", "WorstGroupRMSE"]].agg(["mean", "std"]).round(4)
    summary.columns = [f"{a}_{b}" for a, b in summary.columns]
    summary.reset_index().to_csv(OUT / "uair_table2_summary_with_current_fedavg.csv", index=False)

    piv = {m: g.set_index("seed") for m, g in table.groupby("method")}
    paired = []
    for primary in [m for m in piv if m.startswith("raven")] + ["fedau_window", "obsuse_window"]:
        for comp in ("fedavg_window", "fedavg_window_current"):
            for label, seeds in (("TEST", TEST_SEEDS), ("ALL20", SEEDS)):
                rec = {"primary": primary, "comparator": comp, "slice": label}
                for metric in ("RMSE_mu", "WorstGroupRMSE"):
                    a = piv[primary].loc[seeds, metric].to_numpy(float)
                    b = piv[comp].loc[seeds, metric].to_numpy(float)
                    rel = (a - b) / b
                    rec[f"{metric}_rel_mean"] = float(rel.mean())
                    rec[f"{metric}_wins"] = int((a < b).sum())
                paired.append(rec)
    pd.DataFrame(paired).to_csv(OUT / "uair_paired_vs_fedavg.csv", index=False)
    dump_json({"worstgroup_recompute_check": check, "n_seeds": len(SEEDS),
               "frozen_methods": sorted(frozen["method"].unique().tolist())}, OUT / "AUDIT_META.json")
    print(summary.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
