"""One-factor-at-a-time ceiling map: how much can each RAVEN module be worth?

Compares full RAVEN (artifacts/e3_formal_runs_r1/runs) against the E4 one-factor
ablations (artifacts/e4_core_mechanism_ablation_r1/runs), paired on the 20 formal seeds.

Sign convention: delta = ablation - full RAVEN, in percent of full RAVEN.
  delta < 0  -> removing the module IMPROVES the endpoint: that much is free headroom.
  delta > 0  -> removing the module hurts: the module is worth that much.
Read-only.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

FULL = Path("artifacts/e3_formal_runs_r1/runs")
ABL = Path("artifacts/e4_core_mechanism_ablation_r1/runs")
DATASETS = ["sensorscope", "uair"]
MODULES = ["raven_wo_design", "raven_wo_obs", "raven_wo_use", "raven_wo_inst", "raven_wo_debt"]
ENDPOINTS = ["RMSE_mu", "Delta_group", "Tail_RMSE"]


def load(base: Path, ds: str, method: str) -> dict[str, dict]:
    out = {}
    d = base / ds / method
    if not d.is_dir():
        return out
    for seed in sorted(d.glob("seed*")):
        f = seed / "final_metrics.json"
        if f.is_file():
            out[seed.name] = json.loads(f.read_text(encoding="utf-8"))
    return out


for ds in DATASETS:
    full = load(FULL, ds, "raven")
    if not full:
        print(f"--- {ds}: no full RAVEN runs ---")
        continue
    print(f"\n==================== {ds} ====================")
    header = f"{'endpoint':<12}{'module removed':<18}{'n':>3}{'full':>10}{'ablated':>10}{'delta%':>9}{'paired sd':>11}{'sig':>6}"
    print(header)
    for ep in ENDPOINTS:
        for m in MODULES + ["raven_simoracle"]:
            src = FULL if m == "raven_simoracle" else ABL
            other = load(src, ds, m)
            if not other:
                continue
            pairs = [(full[s][ep], other[s][ep]) for s in sorted(set(full) & set(other))
                     if full[s].get(ep) is not None and other[s].get(ep) is not None]
            if len(pairs) < 3:
                continue
            a = np.array([p[0] for p in pairs], float)
            b = np.array([p[1] for p in pairs], float)
            d = b - a
            sd = float(d.std(ddof=1))
            pct = 100.0 * float(d.mean()) / float(a.mean())
            sig = abs(float(d.mean())) / (sd / np.sqrt(len(d))) if sd > 0 else float("inf")
            label = m.replace("raven_wo_", "remove ") if m.startswith("raven_wo_") else "oracle p+q"
            print(f"{ep:<12}{label:<18}{len(d):>3}{a.mean():>10.4f}{b.mean():>10.4f}"
                  f"{pct:>9.3f}{sd:>11.4f}{sig:>6.1f}")
        print()
