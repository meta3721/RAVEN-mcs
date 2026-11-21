"""Independent verification of the decisive adversarial finding: do the E3 arms actually learn?

For each block, score a frozen arm, the FedAdam arm at eta_s*, and central_delivered through the
repository's own prediction path, and compare against (a) the best constant predictor under the same
mu weights, (b) the zero predictor.  Rerun-free: read-only.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402
from raven_mcs.metrics.accuracy import rmse_mu  # noqa: E402

N_GROUPS = {"sensorscope": 220, "uair": 144, "traffic": 172}
STAR = {"sensorscope": "0.01", "uair": "0.003", "traffic": "0.003"}


def test_mu(dataset, n_groups: int) -> np.ndarray:
    atomic = dataset.atomic_df.copy()
    if n_groups == 4:
        atomic["target_group_main"] = RepeatableTimeOfDayMapper().map(atomic)
    else:
        atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
    tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split="test")
    return np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(n_groups)], dtype=np.float64)


class _Shim:
    pass


out = {}
for block in ("sensorscope", "uair", "traffic"):
    ds = load_paper_dataset(ROOT, block)
    mu = test_mu(ds, N_GROUPS[block])
    arms = {
        "frozen_fedavg_window": ROOT / f"artifacts/e3_formal_runs_r1/runs/{block}/fedavg_window/seed30001/checkpoints/final.pt",
        "fedadam_fedavg_window": ROOT / f"results_server_optimizer/round_v1/runs/A_eta{STAR[block]}/{block}/fedavg_window/seed30001/checkpoints/final.pt",
        "central_delivered": ROOT / f"artifacts/e3_formal_runs_r1/runs/{block}/central_delivered/seed30001/checkpoints/final.pt",
    }
    print(f"\n=== {block} (n_groups={N_GROUPS[block]}, test mu mass sum={mu.sum():.6f}) ===")
    rows = {}
    for name, ck in arms.items():
        if not ck.is_file():
            print(f"  {name:<24} <checkpoint absent>")
            continue
        shim = _Shim()
        shim.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
        pred = _predict(shim, ds, split="test")
        yp = np.asarray(pred["y_pred"], dtype=np.float64)
        yt = np.asarray(pred["y_true"], dtype=np.float64)
        w = _mu_weights_for_test(pred, mu)
        if len(w) == 0:
            print(f"  {name:<24} <no aligned weights>")
            continue
        w = np.asarray(w, dtype=np.float64)
        w = w / w.sum()
        r_model = rmse_mu(yp, yt, w)
        ybar = float(np.sum(w * yt))
        r_const = float(np.sqrt(np.sum(w * (yt - ybar) ** 2)))
        r_zero = float(np.sqrt(np.sum(w * yt**2)))
        sd_pred = float(np.sqrt(np.sum(w * (yp - float(np.sum(w * yp))) ** 2)))
        yc = yt - ybar
        pc = yp - float(np.sum(w * yp))
        cov = float(np.sum(w * pc * yc))
        den = float(np.sqrt(np.sum(w * pc**2) * np.sum(w * yc**2)))
        corr = cov / den if den > 0 else float("nan")
        r2 = 1.0 - (r_model**2) / (r_const**2) if r_const > 0 else float("nan")
        stored = None
        fm = ck.parent.parent / "final_metrics.json"
        if fm.is_file():
            stored = json.loads(fm.read_text(encoding="utf-8")).get("RMSE_mu")
        rows[name] = dict(RMSE_mu=r_model, stored=stored, ybar=ybar, sd_y=r_const, zero=r_zero,
                          sd_pred=sd_pred, corr=corr, r2_vs_const=r2,
                          vs_const_pct=100 * (r_model / r_const - 1) if r_const > 0 else None)
        print(f"  {name:<24} RMSE_mu={r_model:9.4f} stored={stored}  "
              f"| ybar={ybar:8.4f} sd_y={r_const:7.4f} zero={r_zero:7.4f}  "
              f"| sd_pred={sd_pred:7.4f} corr={corr:+.3f}  "
              f"| vs best-const {100*(r_model/r_const-1):+8.1f}%")
    out[block] = rows

p = ROOT / "results_server_optimizer/round_v1/DO_THE_ARMS_LEARN.json"
p.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
print("\nwrote", p)
