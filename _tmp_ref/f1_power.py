"""F-1 design inputs: paired-difference statistics and minimum detectable effect.

Reads artifacts/e3_formal_runs_r1/runs/{dataset}/{method}/seed*/final_metrics.json.
Read-only.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path("artifacts/e3_formal_runs_r1/runs")
DATASETS = ["sensorscope", "uair", "traffic"]
METHODS = [
    "raven", "twostage_hajek", "local_hajek", "fedavg_window",
    "fedasync_window", "flamf_timealign_adapted", "fedau_window",
    "obsuse_window", "inst_cal", "debt_cal", "raven_simoracle",
    "central_all", "central_delivered",
]

# key discovery
sample = next((ROOT / "sensorscope" / "raven").glob("seed*/final_metrics.json"))
print("sample keys:", sorted(json.loads(sample.read_text(encoding="utf-8")).keys()))


def load(dataset: str, method: str) -> dict[str, dict]:
    out = {}
    d = ROOT / dataset / method
    if not d.is_dir():
        return out
    for seed_dir in sorted(d.glob("seed*")):
        f = seed_dir / "final_metrics.json"
        if f.is_file():
            out[seed_dir.name] = json.loads(f.read_text(encoding="utf-8"))
    return out


def pick(payload: dict, *names: str):
    for n in names:
        if n in payload:
            return payload[n]
    return None


def paired(dataset: str, a: str, b: str, key: str):
    da, db = load(dataset, a), load(dataset, b)
    seeds = sorted(set(da) & set(db))
    xa, xb = [], []
    for s in seeds:
        va, vb = pick(da[s], key), pick(db[s], key)
        if va is None or vb is None:
            continue
        xa.append(float(va)); xb.append(float(vb))
    if len(xa) < 3:
        return None
    xa, xb = np.array(xa), np.array(xb)
    d = xa - xb
    n = len(d)
    sd = float(d.std(ddof=1))
    se = sd / math.sqrt(n)
    # 80% power, two-sided alpha=0.05
    mde = (1.959964 + 0.841621) * se
    return dict(n=n, mean_a=float(xa.mean()), mean_b=float(xb.mean()),
                mean_diff=float(d.mean()), sd_diff=sd, se=se, mde=mde,
                mde_pct=100.0 * mde / float(xb.mean()) if xb.mean() else float("nan"),
                diff_pct=100.0 * float(d.mean()) / float(xb.mean()) if xb.mean() else float("nan"))


for key in ("RMSE_mu", "rmse_mu", "RMSE_mu_mean"):
    print(f"\n===== key = {key} =====")
    ok = False
    for ds in DATASETS:
        for m in METHODS:
            payload = load(ds, m)
            if payload and pick(next(iter(payload.values())), key) is not None:
                ok = True
                break
        if ok:
            break
    if not ok:
        print("  key absent")
        continue
    print(f"{'dataset':<12}{'pair':<34}{'n':>3}{'base':>12}{'diff%':>9}{'sd_diff':>10}{'MDE':>10}{'MDE%':>8}")
    for ds in DATASETS:
        for b in ("twostage_hajek", "fedavg_window", "local_hajek", "raven_simoracle"):
            r = paired(ds, "raven", b, key)
            if r is None:
                continue
            print(f"{ds:<12}{'raven - ' + b:<34}{r['n']:>3}{r['mean_b']:>12.4f}"
                  f"{r['diff_pct']:>9.3f}{r['sd_diff']:>10.4f}{r['mde']:>10.4f}{r['mde_pct']:>8.3f}")
    break

print("\n===== level means and sds (RMSE_mu) =====")
for ds in DATASETS:
    for m in METHODS:
        payload = load(ds, m)
        if not payload:
            continue
        vals = [float(pick(v, "RMSE_mu", "rmse_mu")) for v in payload.values()
                if pick(v, "RMSE_mu", "rmse_mu") is not None]
        if vals:
            a = np.array(vals)
            print(f"{ds:<12}{m:<26}n={len(a):<4}mean={a.mean():.4f} sd={a.std(ddof=1):.4f}")
