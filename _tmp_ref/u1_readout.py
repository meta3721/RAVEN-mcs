"""U1 readout: U-Air headroom at 20 seeds.

Applies the unchanged pre-registered GO rule (already computed by the driver), reports the realized
resolving power, compares against the published 5-seed round, verifies that the reused rows are
bit-identical to round_v1, and classifies each condition against the revision-2 escalation band.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

R1 = Path("results_h_headroom/round_v1")
U1 = Path("results_h_headroom/round_u1")
BAND = (0.0030, 0.0075)  # revision 2 ambiguous band, inclusive
METRICS = ("RMSE_mu", "Tail_RMSE", "RMSE_rho")


def mde(se: float, n: int) -> float:
    return float((stats.t.ppf(0.975, n - 1) + stats.t.ppf(0.8, n - 1)) * se)


def main() -> int:
    u1 = pd.read_csv(U1 / "tables/H_summary.csv")
    r1 = pd.read_csv(R1 / "tables/H_summary.csv")
    dec = json.loads((U1 / "U1_DECISION.json").read_text(encoding="utf-8"))

    print("=" * 104)
    print("DECISION FILE")
    print("=" * 104)
    print(json.dumps(dec, indent=2, sort_keys=True))
    print()

    u = u1[u1.dataset == "uair"].sort_values("condition").reset_index(drop=True)
    print("=" * 104)
    print("U-Air HEADROOM AT 20 SEEDS  (H_nodesign = (FedAvg - NoDesign oracle) / FedAvg)")
    print("=" * 104)
    print(f"{'condition':<18}{'n':>3}{'H [95% CI]':>26}{'sd':>8}{'MDE':>8}"
          f"{'GO needs H>':>12}{'GO':>5}{'band':>22}")
    for r in u.itertuples():
        half = r.H_nodesign_RMSE_mu_ci_hi - r.H_nodesign_RMSE_mu
        tcrit = stats.t.ppf(0.975, r.n - 1)
        se = half / tcrit
        sd = se * np.sqrt(r.n)
        need = tcrit * se
        m = mde(se, r.n)
        if r.H_nodesign_RMSE_mu > BAND[1]:
            band = "above band -> U2 useless"
        elif r.H_nodesign_RMSE_mu < BAND[0]:
            band = "below band -> conclusive"
        else:
            band = "IN BAND -> U2 applies"
        ci = f"{100*r.H_nodesign_RMSE_mu:+.2f}% [{100*r.H_nodesign_RMSE_mu_ci_lo:+.2f},{100*r.H_nodesign_RMSE_mu_ci_hi:+.2f}]"
        print(f"{r.condition:<18}{r.n:>3}{ci:>26}{100*sd:>7.2f}pp{100*m:>7.2f}pp"
              f"{100*need:>11.2f}%{str(bool(r.go)):>5}{band:>22}")

    print()
    print("=" * 104)
    print("DESIGN SUPPORT COST AT 20 SEEDS  ((design - nodesign) / nodesign, oracle arms)")
    print("=" * 104)
    print(f"{'condition':<18}{'support cost [95% CI]':>30}{'CI lower > 0':>14}")
    for r in u.itertuples():
        ci = (f"{100*r.design_support_cost_RMSE_mu:+.2f}% "
              f"[{100*r.design_support_cost_RMSE_mu_ci_lo:+.2f},{100*r.design_support_cost_RMSE_mu_ci_hi:+.2f}]")
        print(f"{r.condition:<18}{ci:>30}{str(r.design_support_cost_RMSE_mu_ci_lo > 0):>14}")

    print()
    print("=" * 104)
    print("20 SEEDS vs PUBLISHED 5 SEEDS (U-Air)")
    print("=" * 104)
    r = r1[r1.dataset == "uair"].sort_values("condition").reset_index(drop=True)
    print(f"{'condition':<18}{'H@5':>10}{'H@20':>10}{'shift':>10}"
          f"{'cost@5':>10}{'cost@20':>10}{'shift':>10}")
    for a, b in zip(r.itertuples(), u.itertuples()):
        assert a.condition == b.condition
        print(f"{a.condition:<18}{100*a.H_nodesign_RMSE_mu:>9.2f}%{100*b.H_nodesign_RMSE_mu:>9.2f}%"
              f"{100*(b.H_nodesign_RMSE_mu-a.H_nodesign_RMSE_mu):>9.2f}pp"
              f"{100*a.design_support_cost_RMSE_mu:>9.2f}%{100*b.design_support_cost_RMSE_mu:>9.2f}%"
              f"{100*(b.design_support_cost_RMSE_mu-a.design_support_cost_RMSE_mu):>9.2f}pp")

    print()
    print("=" * 104)
    print("GATES ON THE U1 TABLE")
    print("=" * 104)
    s1 = pd.read_csv(R1 / "tables/H_seed_rows.csv")
    sN = pd.read_csv(U1 / "tables/H_seed_rows.csv")
    reused = sN[sN.source == "reuse"]
    print(f"rows total={len(sN)}  reuse={len(reused)}  new={len(sN)-len(reused)}")
    m = s1.merge(reused, on=["condition", "dataset", "method", "seed"], suffixes=("_r1", "_u1"))
    same = True
    for c in METRICS:
        d = np.abs(m[f"{c}_r1"].to_numpy(float) - m[f"{c}_u1"].to_numpy(float)).max()
        same = same and d == 0.0
        print(f"  reused row |diff| {c:<12} = {d:.3e}")
    print(f"  reuse bit-identical to round_v1: {same and len(m) == len(s1)}")
    print(f"  H == H_nodesign for every U-Air cell (arm freeze): "
          f"{bool(np.allclose(u.H_RMSE_mu, u.H_nodesign_RMSE_mu, atol=0))}")
    n_bad = 0
    for f in (U1 / "runs").rglob("final_metrics.json"):
        j = json.loads(f.read_text(encoding="utf-8"))
        if not np.isfinite(float(j.get("RMSE_mu", np.nan))):
            n_bad += 1
    print(f"  non-finite RMSE_mu runs: {n_bad}")
    print(f"  SensorScope rows carried at n=5 (power note): "
          f"{sorted(set(u1[u1.dataset=='sensorscope'].n))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
