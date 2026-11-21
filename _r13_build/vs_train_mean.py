"""Do the paper's models beat the training-mean predictor?

Independently recomputes the training-mean predictor per block, verifies it against the values the
manuscript prints, then compares every arm in the frozen trees against it.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import align_mu_to_dataset, freeze_fixture_target  # noqa: E402

PRINTED = {"sensorscope": 7.647, "uair": 1.054}
TRAFFIC_PRINTED = 1.007
ARM_DIRS = {
    "sensorscope": ROOT / "artifacts/e3_formal_runs_r1/runs/sensorscope",
    "uair": ROOT / "artifacts/e3_formal_runs_r1/runs/uair",
    "traffic": ROOT / "artifacts/e3_formal_runs_r1/runs/traffic",
}


def pred_for(block: str, ck: pathlib.Path, split: str):
    ds = load_paper_dataset(ROOT, block)
    shim = type("S", (), {})()
    shim.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
    return ds, _predict(shim, ds, split=split)


print("=== 1. the training-mean predictor, recomputed and checked against the manuscript ===")
train_mean, check = {}, {}
for block in ("sensorscope", "uair", "traffic"):
    tree = ARM_DIRS[block]
    arm0 = sorted(p.name for p in tree.iterdir() if p.is_dir())[0]
    ck = tree / arm0 / "seed30001/checkpoints/final.pt"
    ds, tr = pred_for(block, ck, "train")
    _, te = pred_for(block, ck, "test")
    mu = np.asarray(align_mu_to_dataset(ds, freeze_fixture_target(ds.atomic_df, dataset=block))[0], float)
    w = np.asarray(_mu_weights_for_test(te, mu), float)
    w = w / w.sum()
    y = np.asarray(te["y_true"], float)
    c_unw = float(np.mean(np.asarray(tr["y_true"], float)))
    wtr = np.asarray(_mu_weights_for_test(tr, mu), float)
    c_wtd = float(np.sum(wtr / wtr.sum() * np.asarray(tr["y_true"], float)))
    r_unw = float(np.sqrt(np.sum(w * (y - c_unw) ** 2)))
    r_wtd = float(np.sqrt(np.sum(w * (y - c_wtd) ** 2)))
    r_oracle = float(np.sqrt(np.sum(w * (y - float(np.sum(w * y))) ** 2)))
    train_mean[block] = {"c_unweighted": c_unw, "c_train_mu_weighted": c_wtd,
                         "train_mean_predictor_rmse_mu": r_unw,
                         "train_mu_weighted_variant": r_wtd,
                         "test_fitted_constant_rmse_mu": r_oracle,
                         "test_target_mean": float(np.sum(w * y)), "n_test_units": int(len(y))}
    printed = PRINTED.get(block, TRAFFIC_PRINTED)
    print(f"  {block:<12} c_train(unweighted)={c_unw:+.4f}  train-mean predictor RMSE_mu={r_unw:.4f}"
          f"  |  printed {printed}  match={abs(r_unw - printed) < 0.002}"
          f"  |  test-fitted constant={r_oracle:.4f}")
    check[block] = {"printed": printed, "recomputed": round(r_unw, 4),
                    "match": bool(abs(r_unw - printed) < 0.002),
                    "test_fitted_recomputed": round(r_oracle, 4)}

print("\n=== 2. every arm in the frozen trees against the training-mean predictor ===")
rows = []
for block in ("sensorscope", "uair", "traffic"):
    base = train_mean[block]["train_mean_predictor_rmse_mu"]
    for d in sorted((ARM_DIRS[block]).iterdir()):
        if not d.is_dir():
            continue
        vals = []
        for s in sorted(d.glob("seed*/final_metrics.json")):
            v = json.loads(s.read_text(encoding="utf-8")).get("RMSE_mu")
            if v is not None:
                vals.append(float(v))
        if not vals:
            continue
        m = float(np.mean(vals))
        rows.append({"block": block, "arm": d.name, "n_seeds": len(vals), "mean_RMSE_mu": m,
                     "train_mean_predictor": base, "ratio": m / base,
                     "pct_vs_train_mean": 100 * (m / base - 1),
                     "beats_train_mean": m < base})
        print(f"  {block:<12} {d.name:<20} n={len(vals):>2}  mean={m:.4f}  "
              f"vs train-mean {base:.4f}  {100*(m/base-1):+6.2f} %  "
              f"{'BEATS' if m < base else 'worse'}")

print("\n=== 3. the Adam-replaced traffic arms (TE1 tree, 15 confirm seeds) ===")
te1 = ROOT / "results_traffic_e1/round_v1/runs"
base_t = TRAFFIC_PRINTED
for d in sorted(te1.iterdir()) if te1.exists() else []:
    for arm in sorted(d.glob("traffic/*")):
        vals = [json.loads(p.read_text(encoding="utf-8"))["RMSE_mu"]
                for p in sorted(arm.glob("seed*/final_metrics.json"))]
        if not vals:
            continue
        m = float(np.mean(vals))
        rows.append({"block": "traffic", "arm": f"adam:{arm.name}", "n_seeds": len(vals),
                     "mean_RMSE_mu": m, "train_mean_predictor": base_t, "ratio": m / base_t,
                     "pct_vs_train_mean": 100 * (m / base_t - 1), "beats_train_mean": m < base_t})
        print(f"  traffic      adam:{arm.name:<14} n={len(vals):>2}  mean={m:.4f}  "
              f"vs train-mean {base_t:.4f}  {100*(m/base_t-1):+6.2f} %  "
              f"{'BEATS' if m < base_t else 'worse'}")

out = {"training_mean_predictor": train_mean, "verification": check, "comparisons": rows}
(ROOT / "results_paper_ceiling/round_v1/VS_TRAIN_MEAN.json").write_text(
    json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
print("\nwrote results_paper_ceiling/round_v1/VS_TRAIN_MEAN.json")
