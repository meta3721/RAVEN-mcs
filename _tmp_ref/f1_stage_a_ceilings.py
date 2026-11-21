"""Stage A of F-1: the measured improvement ceilings on the published E3 traces.

No training, no new traces. Reads artifacts/e3_formal_runs_r1/runs/*/*/final_metrics.json
(20 paired seeds per dataset) and prints, for each endpoint and dataset, how much a change
to the aggregation method could buy.

Ceiling definitions used here:
  delivery ceiling   = RMSE_mu(Central-All)      - RMSE_mu(RAVEN)   unreachable by reweighting
  reweighting ceiling= RMSE_mu(Central-Delivered)- RMSE_mu(RAVEN)   reachable in principle
  propensity ceiling = RMSE_mu(RAVEN)            - RMSE_mu(SimOracle) exact propensity pair
  P2 ceiling         = RMSE_mu(RAVEN)            - RMSE_mu(TwoStage)  P2 + debt removed
Negative = the reference is better than RAVEN, i.e. available gain.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

RUNS = Path("artifacts/e3_formal_runs_r1/runs")
DATASETS = ["sensorscope", "uair"]
ENDPOINTS = ["RMSE_mu", "Delta_group", "Tail_RMSE", "RMSE_rho", "WorstGroupRMSE"]


def load(ds: str) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    d = RUNS / ds
    if not d.is_dir():
        return out
    for m in sorted(p.name for p in d.iterdir() if p.is_dir()):
        per: dict[str, float] = {}
        for seed in sorted((d / m).glob("seed*")):
            f = seed / "final_metrics.json"
            if f.is_file():
                per[seed.name] = json.loads(f.read_text(encoding="utf-8"))
        if per:
            out[m] = per
    return out


def paired(data: dict[str, dict[str, float]], a: str, b: str, key: str):
    if a not in data or b not in data:
        return None
    common = sorted(set(data[a]) & set(data[b]))
    pairs = [(data[a][s][key], data[b][s][key]) for s in common
             if data[a][s].get(key) is not None and data[b][s].get(key) is not None]
    if len(pairs) < 3:
        return None
    va = np.array([p[0] for p in pairs], dtype=float)
    vb = np.array([p[1] for p in pairs], dtype=float)
    d = va - vb
    base = float(vb.mean())
    return dict(n=len(d), a=float(va.mean()), b=base, diff=float(d.mean()),
                pct=100.0 * float(d.mean()) / base if base else float("nan"),
                sd=float(d.std(ddof=1)))


REFERENCES = [
    ("propensity ceiling (exact p and q)", "raven", "raven_simoracle"),
    ("P2 + debt removed (= reference beta_hat)", "raven", "twostage_hajek"),
    ("reweighting ceiling (delivered, uncorrected)", "raven", "central_delivered"),
    ("delivery ceiling (all observations)", "raven", "central_all"),
    ("uncorrected same backbone (FedAvg)", "raven", "fedavg_window"),
    ("uncorrected same backbone (Local-Hajek)", "raven", "local_hajek"),
]

for ds in DATASETS:
    data = load(ds)
    print(f"\n================ {ds} ================")
    print(f"methods present: {', '.join(sorted(data))}")
    for key in ("RMSE_mu", "Delta_group", "Tail_RMSE"):
        print(f"\n--- endpoint {key} ---")
        print(f"{'reference':<48}{'n':>3}{'RAVEN':>11}{'ref':>11}{'delta%':>9}{'paired sd':>11}")
        for label, a, b in REFERENCES:
            r = paired(data, a, b, key)
            if r is None:
                continue
            print(f"{label:<48}{r['n']:>3}{r['a']:>11.4f}{r['b']:>11.4f}"
                  f"{r['pct']:>9.3f}{r['sd']:>11.4f}")
