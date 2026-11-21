"""R1.3 adversarial audit - objection (b): is validation selection sound?

V1  per (block, eta, seed): validation RMSE_mu (driver recipe) vs test RMSE_mu
    (read from each cell's own sealed final_metrics.json).
V2  does the driver's target-mass recipe change the validation number or the
    eta selection?  Recipe A = driver (masses from validation rows only).
    Recipe B = masses from the WHOLE atomic frame (all splits pooled).
V3  rank agreement val vs test at the level of eta, per seed.
ASCII only.
"""
import json, math, pathlib, sys
import numpy as np
import pandas as pd
import torch

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test
from raven_mcs.metrics.accuracy import rmse_mu
from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder

OUT = ROOT / "results_server_optimizer/round_v1"
RUNS = OUT / "runs"
BUILD = ROOT / "_r13_build"
SEEDS = [30001, 30002, 30003, 30004, 30005]
BLOCKS = ("sensorscope", "uair", "traffic")
ETAS = (0.001, 0.003, 0.01)


class Shim:
    pass


def main():
    res = {}
    for b in BLOCKS:
        ds = load_paper_dataset(ROOT, b)
        ng = int(ds.num_groups)
        au = ds._atomic_df.copy()
        if ng == 4:
            au["target_group_main"] = RepeatableTimeOfDayMapper().map(au)
        else:
            au["target_group_main"] = pd.Categorical(au["target_group"]).codes
        tb = TargetBuilder(group_mapper=GroupMapper("target_group_main"))
        # Recipe A: whole frame, filtered inside by split (this is what the driver does)
        mua = np.asarray([float(tb.build(au, split="validation").group_mass.get(str(g), 0.0))
                          for g in range(ng)])
        # Recipe B: masses from the WHOLE frame (no split filter) -> pools val+test+train
        aun = au.copy()
        aun["split"] = "pooled"
        mub = np.asarray([float(tb.build(aun, split="pooled").group_mass.get(str(g), 0.0))
                          for g in range(ng)])
        # Recipe C: masses from the test rows only
        muc = np.asarray([float(tb.build(au, split="test").group_mass.get(str(g), 0.0))
                          for g in range(ng)])
        print("### block %s  max|A-B|=%.3e  max|A-C|=%.3e  max|B-C|=%.3e"
              % (b, np.abs(mua - mub).max(), np.abs(mua - muc).max(), np.abs(mub - muc).max()))
        for eta in ETAS:
            for s in SEEDS:
                d = RUNS / ("A_eta%g" % eta) / b / "fedavg_window" / ("seed%d" % s)
                ck = d / "checkpoints/final.pt"
                if not ck.is_file():
                    continue
                m = Shim()
                m.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
                pv = _predict(m, ds, split="validation")
                fm = json.loads((d / "final_metrics.json").read_text())
                va = float(rmse_mu(pv["y_pred"], pv["y_true"], _mu_weights_for_test(pv, mua)))
                vb = float(rmse_mu(pv["y_pred"], pv["y_true"], _mu_weights_for_test(pv, mub)))
                res[(b, eta, s)] = (va, vb, float(fm["RMSE_mu"]))
        print("  eta      valA(mean)  valB(mean)  test(mean)   argmin valA  argmin valB  argmin test")
        rowsa, rowsb, rowst = [], [], []
        for eta in ETAS:
            k = [(b, eta, s) for s in SEEDS if (b, eta, s) in res]
            if not k:
                continue
            va = np.mean([res[x][0] for x in k]); vb = np.mean([res[x][1] for x in k])
            vt = np.mean([res[x][2] for x in k])
            rowsa.append((va, eta)); rowsb.append((vb, eta)); rowst.append((vt, eta))
            print("  %-8g %-11.6f %-11.6f %-11.6f" % (eta, va, vb, vt))
        if rowsa:
            print("  -> selected by valA=%.3g   by valB=%.3g   by test=%.3g"
                  % (min(rowsa)[1], min(rowsb)[1], min(rowst)[1]))
        # per-seed rank agreement between validation and test over eta levels
        agree = 0; tot = 0
        for s in SEEDS:
            ks = [(b, e, s) for e in ETAS if (b, e, s) in res]
            if len(ks) < 3:
                continue
            bv = min(ks, key=lambda x: res[x][0])
            bt = min(ks, key=lambda x: res[x][2])
            tot += 1
            agree += int(bv[1] == bt[1])
        print("  per-seed argmin agreement (valA vs test) = %d/%d" % (agree, tot))
        # correlation of val and test across all (eta, seed) cells
        allk = [k for k in res if k[0] == b]
        if len(allk) >= 3:
            x = np.array([res[k][0] for k in allk]); y = np.array([res[k][2] for k in allk])
            print("  corr(valA, test) over %d cells = %+.4f" % (len(allk), float(np.corrcoef(x, y)[0, 1])))
    (BUILD / "r13_b_selection.json").write_text(
        json.dumps({"cells": {"%s|%s|%d" % k: v for k, v in res.items()}}, indent=1) + "\n", encoding="utf-8")
    print("WROTE r13_b_selection.json")


if __name__ == "__main__":
    main()
