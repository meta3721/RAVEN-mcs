"""Are ALL E3 arms degenerate on SensorScope/U-Air, or only the RAVEN-MCS family?

Scores every arm present in the frozen E3 tree, seed 30001, through the repository's own prediction
path, against the best constant predictor under the same mu weights.
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
TREE = ROOT / "artifacts/e3_formal_runs_r1/runs"


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
    arm_dirs = sorted(p for p in (TREE / block).iterdir() if p.is_dir()) if (TREE / block).is_dir() else []
    print(f"\n=== {block}: test target mean={np.sum(mu*np.array([0.0])):.4f} ===")
    rows = {}
    # reference quantities from one representative prediction
    first = True
    for ad in arm_dirs:
        ck = ad / "seed30001/checkpoints/final.pt"
        if not ck.is_file():
            continue
        shim = _Shim()
        shim.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
        pred = _predict(shim, ds, split="test")
        yp = np.asarray(pred["y_pred"], dtype=np.float64)
        yt = np.asarray(pred["y_true"], dtype=np.float64)
        w = _mu_weights_for_test(pred, mu)
        if len(w) == 0:
            continue
        w = np.asarray(w, dtype=np.float64)
        w = w / w.sum()
        ybar = float(np.sum(w * yt))
        r_const = float(np.sqrt(np.sum(w * (yt - ybar) ** 2)))
        r_zero = float(np.sqrt(np.sum(w * yt**2)))
        r_model = rmse_mu(yp, yt, w)
        sd_pred = float(np.sqrt(np.sum(w * (yp - float(np.sum(w * yp))) ** 2)))
        yc, pc = yt - ybar, yp - float(np.sum(w * yp))
        den = float(np.sqrt(np.sum(w * pc**2) * np.sum(w * yc**2)))
        corr = float(np.sum(w * pc * yc) / den) if den > 0 else float("nan")
        if first:
            print(f"    reference: ybar={ybar:8.4f}  sd_y={r_const:7.4f}  zero={r_zero:7.4f}")
            first = False
        rows[ad.name] = dict(RMSE_mu=r_model, ybar=ybar, sd_y=r_const, zero=r_zero, sd_pred=sd_pred,
                             corr=corr, vs_const_pct=100 * (r_model / r_const - 1))
        print(f"    {ad.name:<26} RMSE_mu={r_model:8.4f}  sd_pred={sd_pred:7.4f}  corr={corr:+.3f}  "
              f"vs best-const {100*(r_model/r_const-1):+8.1f}%")
    if rows:
        n_beat = sum(1 for v in rows.values() if v["vs_const_pct"] < 0)
        print(f"    -> arms scored: {len(rows)}; arms better than the best constant: {n_beat}")
    out[block] = rows

p = ROOT / "results_server_optimizer/round_v1/ALL_ARMS_VS_CONSTANT.json"
p.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
print("\nwrote", p)
