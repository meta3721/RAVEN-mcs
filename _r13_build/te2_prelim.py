"""Preliminary TE2 contrast from the cells already on disk (test RMSE_mu is written per run)."""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np
from scipy.stats import t as tdist

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"
RUNS = OUT / "runs"
ARMS = ["local_hajek", "inst_cal", "debt_cal", "raven_simoracle"]
CONTROL = "local_hajek"
SEEDS = list(range(30001, 30021))

data = {}
for a in ARMS:
    vals = {}
    for s in SEEDS:
        p = RUNS / f"K5_{a}/traffic/{a}/seed{s}/final_metrics.json"
        if p.is_file():
            vals[s] = json.loads(p.read_text(encoding="utf-8"))["RMSE_mu"]
    data[a] = vals
    print(f"  {a:<17} done={len(vals):>2}/20  mean={np.mean(list(vals.values())) if vals else float('nan'):.6f}")

ctrl = data[CONTROL]
print(f"\n  control cells available: {len(ctrl)}")
bar = 0.02 * float(np.mean(list(ctrl.values())))
print(f"  2 % of the control's concentrated error = {bar:.6f}\n")
print(f"  {'contrast':<34}{'n':>3}{'mean D':>14}{'sd D':>12}{'MDE80':>12}{'95% CI':>26}{'sep':>6}")
for a in ARMS:
    if a == CONTROL:
        continue
    seeds = sorted(set(ctrl) & set(data[a]))
    if len(seeds) < 3:
        print(f"  control - {a:<24} only {len(seeds)} pairs")
        continue
    D = np.asarray([ctrl[s] - data[a][s] for s in seeds])
    n = len(D)
    sd = float(D.std(ddof=1))
    mde = (float(tdist.ppf(0.975, n - 1)) + float(tdist.ppf(0.80, n - 1))) * sd / math.sqrt(n)
    rng = np.random.default_rng(20261007)
    boot = np.asarray([float(np.mean(rng.choice(D, size=n, replace=True))) for _ in range(10000)])
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    sep = (lo > 0) and (abs(float(D.mean())) > mde) and (abs(float(D.mean())) >= bar)
    print(f"  control - {a:<24}{n:>3}{D.mean():>+14.6f}{sd:>12.6f}{mde:>12.6f}"
          f"{f'[{lo:+.5f}, {hi:+.5f}]':>26}{str(sep):>6}")
