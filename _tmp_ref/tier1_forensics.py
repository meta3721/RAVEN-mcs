"""Tier 1 forensics: where exactly does the U-Air FedAvg comparison break?

1. N3: does Table III's printed 1.1882 equal the ALL20 mean, the TEST10 mean, or neither?
2. N1: which cells reproduce under the current runner and which do not (from the gate files)?
3. Which frozen cells are numerically identical to the frozen FedAvg (same filter)?
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

FROZEN = Path("artifacts/e3_formal_runs_r1/runs/uair")
AUDIT = Path("results_table2_audit")


def per_seed(method: str) -> dict[str, float]:
    out = {}
    d = FROZEN / method
    for s in sorted(d.glob("seed*")):
        f = s / "final_metrics.json"
        if f.is_file():
            out[s.name] = json.loads(f.read_text(encoding="utf-8"))["RMSE_mu"]
    return out


print("=" * 96)
print("N3 — what is Table III's printed 1.1882?")
print("=" * 96)
v = per_seed("fedavg_window")
seeds = sorted(v)
all20 = np.array([v[s] for s in seeds], float)
test10 = np.array([v[s] for s in seeds if int(s.replace("seed", "")) >= 30011], float)
first10 = np.array([v[s] for s in seeds if int(s.replace("seed", "")) <= 30010], float)
print(f"  seeds present           : {len(seeds)}")
print(f"  ALL20  mean             : {all20.mean():.6f}")
print(f"  TEST10 mean (30011-020) : {test10.mean():.6f}")
print(f"  first10 mean(30001-010) : {first10.mean():.6f}")
print(f"  Table III prints        : 1.188200")
print(f"  |printed - ALL20|       : {abs(1.1882 - all20.mean()):.6f}"
      f"   ({100*abs(1.1882-all20.mean())/all20.mean():.3f}% )")
print(f"  |printed - TEST10|      : {abs(1.1882 - test10.mean()):.6f}"
      f"   ({100*abs(1.1882-test10.mean())/test10.mean():.3f}% )")

print()
print("=" * 96)
print("N1 — which frozen U-Air cells are identical to the frozen FedAvg row?")
print("=" * 96)
fed = all20.mean()
summary = AUDIT / "uair_table2_summary_with_current_fedavg.csv"
import csv
rows = list(csv.DictReader(summary.open(encoding="utf-8")))
print(f"{'method':<26}{'RMSE_mu':>10}{'delta vs frozen FedAvg':>26}")
for r in rows:
    m = float(r["RMSE_mu_mean"])
    print(f"{r['method']:<26}{m:>10.4f}{100*(m-fed)/fed:>25.3f}%")

print()
print("=" * 96)
print("gate evidence: reproduction status per arm")
print("=" * 96)
for tag, p in (("round_v1 (seed 30001)", Path("results_h_headroom/round_v1/GATE_uair.json")),
               ("round_u1 (seed 30006)", Path("results_h_headroom/round_u1/GATE_uair.json"))):
    g = json.loads(p.read_text(encoding="utf-8"))
    print(f"  {tag}")
    for arm, d in g["arms"].items():
        print(f"    {arm:<20} frozen={d['frozen']:.6f} rerun={d['rerun']:.6f} "
              f"abs_diff={d['abs_diff']:.3e} known_nonrepro={d['known_nonrepro']}")
