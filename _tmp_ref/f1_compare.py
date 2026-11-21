"""F-1 comparison: plugin-p vs oracle-p, paired over seeds, plus harness reproduction check."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(".")
PUB = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
F1 = ROOT / "artifacts" / "e3_f1_score_dependent_r1" / "runs"
DATASETS = ["sensorscope", "uair"]
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


def paired(a: dict, b: dict, ep: str):
    seeds = sorted(set(a) & set(b))
    pa = [(a[s][ep], b[s][ep]) for s in seeds
          if a[s].get(ep) is not None and b[s].get(ep) is not None]
    if len(pa) < 2:
        return None
    x = np.array([p[0] for p in pa], float)
    y = np.array([p[1] for p in pa], float)
    return x, y


def main() -> int:
    print("=== harness reproduction: published raven vs F-1 raven on the copied N trace ===")
    for ds in DATASETS:
        a, b = load(PUB, ds, "raven"), load(F1, ds, "raven")
        r = paired(a, b, "RMSE_mu")
        if r is None:
            print(f"{ds}: not enough runs yet")
            continue
        x, y = r
        print(f"{ds}: n={len(x)}  published mean={x.mean():.6f}  F-1 mean={y.mean():.6f}  "
              f"max |rel diff|={100*np.max(np.abs(y-x)/x):.6f}%")

    print("\n=== E1: raven (plugin p) minus raven_oracle_p, per endpoint ===")
    print(f"{'dataset':<12}{'endpoint':<12}{'n':>3}{'plugin':>11}{'oracle':>11}"
          f"{'delta%':>9}{'sd':>9}{'MDE%':>8}{'sig':>6}")
    for ds in DATASETS:
        plugin = load(F1, ds, "raven")
        oracle = load(F1, ds, "raven_oracle_p")
        for ep in ENDPOINTS:
            r = paired(plugin, oracle, ep)
            if r is None:
                print(f"{ds:<12}{ep:<12}  no data")
                continue
            x, y = r
            d = x - y
            sd = float(d.std(ddof=1)) if len(d) > 1 else float("nan")
            mde = 2.8016 * sd / np.sqrt(len(d))
            sig = abs(float(d.mean())) / (sd / np.sqrt(len(d))) if sd > 0 else float("inf")
            print(f"{ds:<12}{ep:<12}{len(d):>3}{x.mean():>11.4f}{y.mean():>11.4f}"
                  f"{100*d.mean()/x.mean():>9.3f}{sd:>9.4f}{100*mde/x.mean():>8.3f}{sig:>6.2f}")

    print("\n=== context: joint oracle (published raven_simoracle) vs plugin raven ===")
    for ds in DATASETS:
        plugin = load(F1, ds, "raven")
        joint = load(PUB, ds, "raven_simoracle")
        for ep in ("RMSE_mu",):
            r = paired(plugin, joint, ep)
            if r is None:
                continue
            x, y = r
            d = x - y
            print(f"{ds:<12}{ep:<12}{len(d):>3}{x.mean():>11.4f}{y.mean():>11.4f}"
                  f"{100*d.mean()/x.mean():>9.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
