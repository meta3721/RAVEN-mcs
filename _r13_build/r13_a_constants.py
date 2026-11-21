"""R1.3 adversarial audit - objection (a): degenerate predictor / constant baseline.

Uses the REPO'S OWN scoring path (runner._predict + runner._mu_weights_for_test +
metrics.accuracy.rmse_mu) so numbers are directly comparable with final_metrics.json.
Also computes what a constant predictor achieves on the SAME test units and SAME
target-mass weights, for both the new FedAdam arms and the frozen arms.

ASCII only. Write only under _r13_build.
"""
import sys, json, pathlib, hashlib, math
import numpy as np
import pandas as pd
import torch

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.dataset_load import load_paper_dataset
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test
from raven_mcs.metrics.accuracy import rmse_mu
from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder

OUT = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build")
ROUND = ROOT / "results_server_optimizer" / "round_v1" / "runs"
FROZEN = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
BLOCKS = ("sensorscope", "uair", "traffic")
SEEDS = (30001, 30002, 30003, 30004, 30005)
ETA_STAR = {"sensorscope": 0.01, "uair": 0.003, "traffic": 0.003}


class Shim:
    pass


def load_model(ckpt, num_spatial):
    return CommonNDMF_from_ckpt(pathlib.Path(ckpt), num_spatial)


def score(block, ds, ckpt, n_groups):
    """Exactly the driver's validation_rmse_mu path, plus the test score and a sensitivity."""
    res = {}
    m = Shim()
    m.model = load_model(ckpt, ds.num_spatial)
    for split in ("test", "validation", "train"):
        pred = _predict(m, ds, split=split)
        res[split] = pred
    tb = TargetBuilder(group_mapper=GroupMapper("target_group_main"))
    atomic = ds._atomic_df.copy()
    if n_groups == 4:
        atomic["target_group_main"] = RepeatableTimeOfDayMapper().map(atomic)
    else:
        atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
    mu_test = np.asarray([float(tb.build(atomic, split="test").group_mass.get(str(g), 0.0))
                          for g in range(n_groups)])
    mu_val = np.asarray([float(tb.build(atomic, split="validation").group_mass.get(str(g), 0.0))
                         for g in range(n_groups)])
    out = {}
    for split in ("test", "validation"):
        p = res[split]
        out["%s_mu" % split] = float(rmse_mu(p["y_pred"], p["y_true"], _mu_weights_for_test(p, mu_test)))
    p = res["validation"]
    out["validation_driver_recipe"] = float(rmse_mu(p["y_pred"], p["y_true"],
                                                    _mu_weights_for_test(p, mu_val)))
    out["val_mu_mass_sum"] = float(np.sum(mu_val))
    out["test_mu_mass_sum"] = float(np.sum(mu_test))
    out["n_val_units"] = int(len(p["y_true"]))
    out["n_test_units"] = int(len(res["test"]["y_true"]))
    return out, res


def const_stats(pred, mu):
    """Best-in-class constant predictors on the SAME units / SAME weights."""
    y, yp = pred["y_true"], pred["y_pred"]
    w = _mu_weights_for_test(pred, mu)
    out = {}
    z0 = float(np.sum(w * y))
    for name, c in (("wmean", z0), ("zero", 0.0),
                    ("unitmean", float(np.mean(y))),
                    ("median", float(np.median(y)))):
        out[name] = float(np.sqrt(np.sum(w * (c - y) ** 2)))
    out["best_const_in_sample"] = min(out["wmean"], out["zero"], out["unitmean"], out["median"])
    out["oracle_const"] = float(np.sqrt(max(0.0, np.sum(w * y ** 2) - z0 ** 2)))
    out["model_pred_mean"] = float(np.mean(yp))
    out["model_pred_sd"] = float(np.std(yp))
    out["model_pred_min"] = float(np.min(yp))
    out["model_pred_max"] = float(np.max(yp))
    out["y_mean"] = float(np.mean(y))
    out["y_sd"] = float(np.std(y))
    out["corr_pred_true"] = float(np.corrcoef(yp, y)[0, 1]) if np.std(yp) > 0 else float("nan")
    out["r2_vs_zero"] = float(1.0 - np.sum(w * (yp - y) ** 2) / np.sum(w * y ** 2))
    out["n_units"] = int(len(y))
    out["max_abs_pred"] = float(np.max(np.abs(yp)))
    return out


def main():
    report = {}
    for block in BLOCKS:
        print("=" * 70)
        print("BLOCK", block, flush=True)
        ds = load_paper_dataset(ROOT, block)
        n_groups = int(ds.num_groups)
        au = ds._atomic_df
        unit_id = au["unit_id"].astype(str)
        split_col = au["split"].astype(str)
        groups = au["target_group"].astype(str)
        # split independence
        sets = {}
        for s in ("train", "validation", "test"):
            m = split_col == s
            sets[s] = set(unit_id[m])
            print("  split=%-11s n_atomic=%5d  n_unique_units=%5d  target mean=%.5f sd=%.5f"
                  % (s, int(m.sum()), len(sets[s]), float(au.loc[m, "target_value"].mean()),
                     float(au.loc[m, "target_value"].std())), flush=True)
        print("  overlap train/val units  =", len(sets["train"] & sets["validation"]))
        print("  overlap train/test units =", len(sets["train"] & sets["test"]))
        print("  overlap val/test units   =", len(sets["validation"] & sets["test"]))
        # group support overlap
        gv = set(groups[split_col == "validation"]); gt = set(groups[split_col == "test"])
        print("  n target groups val=%d test=%d  overlap=%d" % (len(gv), len(gt), len(gv & gt)))
        # time-index overlap between val and test
        ti = au["time_index"]
        tv = set(ti[split_col == "validation"].tolist()); tt = set(ti[split_col == "test"].tolist())
        print("  time_index overlap val/test = %d of %d val / %d test"
              % (len(tv & tt), len(tv), len(tt)), flush=True)

        # target masses three ways
        atomic = au.copy()
        if n_groups == 4:
            atomic["target_group_main"] = RepeatableTimeOfDayMapper().map(atomic)
        else:
            atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
        tb = TargetBuilder(group_mapper=GroupMapper("target_group_main"))
        mu_test_pure = np.asarray([float(tb.build(atomic, split="test").group_mass.get(str(g), 0.0))
                                   for g in range(n_groups)])
        mu_val_pure = np.asarray([float(tb.build(atomic, split="validation").group_mass.get(str(g), 0.0))
                                  for g in range(n_groups)])
        mu_full = mu_test_pure
        print("  sum mu_test_pure=%.6f  |mu_test_pure - mu_val_pure|_max=%.3e"
              % (mu_test_pure.sum(), float(np.max(np.abs(mu_test_pure - mu_val_pure)))), flush=True)
        report.setdefault("splits", {})[block] = {
            "n_atomic": {s: int((split_col == s).sum()) for s in ("train", "validation", "test")},
            "overlap_units": {
                "train_val": len(sets["train"] & sets["validation"]),
                "train_test": len(sets["train"] & sets["test"]),
                "val_test": len(sets["validation"] & sets["test"]),
            },
            "group_overlap_val_test": len(gv & gt),
            "time_index_overlap_val_test": len(tv & tt),
        }

        # ---- new arms (A) + Stage C arms, all three eta levels for sensitivity ----
        for tag, arm in (("A_eta%g" % ETA_STAR[block], "fedavg_window"),
                         ("C_raven_simoracle", "raven_simoracle"),
                         ("C_raven", "raven")):
            for seed in SEEDS:
                ck = ROUND / tag / block / arm / ("seed%d" % seed) / "checkpoints" / "final.pt"
                if not ck.is_file():
                    continue
                r, preds = score(block, ds, ck, n_groups)
                fm = json.loads((ROUND / tag / block / arm / ("seed%d" % seed) /
                                 "final_metrics.json").read_text())
                stats = const_stats(preds["test"], mu_test_pure)
                stats.update(r)
                stats["final_metrics_RMSE_mu"] = fm.get("RMSE_mu")
                stats["repro_delta"] = (None if fm.get("RMSE_mu") is None
                                        else float(stats["test_mu"] - fm.get("RMSE_mu")))
                key = "%s/%s/%d" % (tag, block, seed)
                report.setdefault("new", {})[key] = stats
                print("  [A] %-14s seed%d  test=%.6f (fm %.6f)  val=%.6f  pred mean=%+.4f sd=%.4f "
                      "max|p|=%.4f  corr=%+.3f  R2zero=%+.4f  bestconst=%.6f  gain_vs_const=%.2f%%"
                      % (tag, seed, stats["test_mu"], stats["final_metrics_RMSE_mu"] or float("nan"),
                         stats["validation_driver_recipe"], stats["model_pred_mean"],
                         stats["model_pred_sd"], stats["max_abs_pred"], stats["corr_pred_true"],
                         stats["r2_vs_zero"], stats["best_const_in_sample"],
                         100.0 * (1.0 - stats["test_mu"] / stats["best_const_in_sample"])),
                      flush=True)

        # ---- frozen arms ----
        for arm in ("central_delivered", "central_all", "fedavg_window", "local_hajek",
                    "raven_simoracle"):
            for seed in SEEDS:
                ck = FROZEN / block / arm / ("seed%d" % seed) / "checkpoints" / "final.pt"
                fm = FROZEN / block / arm / ("seed%d" % seed) / "final_metrics.json"
                if not ck.is_file() or not fm.is_file():
                    continue
                r, preds = score(block, ds, ck, n_groups)
                stats = const_stats(preds["test"], mu_test_pure)
                stats.update(r)
                stats["final_metrics_RMSE_mu"] = json.loads(fm.read_text()).get("RMSE_mu")
                key = "FROZEN/%s/%s/%d" % (arm, block, seed)
                report.setdefault("frozen", {})[key] = stats
                print("  [F] %-18s seed%d  test=%.6f (fm %.6f)  pred sd=%.4f max|p|=%.4f "
                      "corr=%+.3f  bestconst=%.6f  gain_vs_const=%.2f%%"
                      % (arm, seed, stats["test_mu"], stats["final_metrics_RMSE_mu"] or float("nan"),
                         stats["model_pred_sd"], stats["max_abs_pred"], stats["corr_pred_true"],
                         stats["best_const_in_sample"],
                         100.0 * (1.0 - stats["test_mu"] / stats["best_const_in_sample"])),
                      flush=True)

    (OUT / "r13_a_constants.json").write_text(json.dumps(report, indent=1, default=str) + "\n",
                                              encoding="utf-8")
    print("WROTE r13_a_constants.json")


if __name__ == "__main__":
    main()
