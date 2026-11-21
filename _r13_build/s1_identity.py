"""S1 identity closure: (1) is the figure CSV mirror or theta? (2) what is fedavg_window_current?

Read-only over existing CSVs and small JSONs. No inference, no re-scoring.
"""
from __future__ import annotations

import csv
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
FIG = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv"
C7 = ROOT / "results_seed_path_audit_r1/C7_E3_ARMS_THETA.csv"
IMP = ROOT / "results_seed_path_audit_r1/C_IMPACT_RECALC.csv"
AFFECTED = ["30007", "30016", "30018"]

fig = list(csv.DictReader(FIG.open(encoding="utf-8")))
c7 = {r["arm"]: {s: float(v) for s, v in zip(("30007", "30016", "30018"),
                                             (r["RMSE_mu"],))} for r in []}
c7 = {}
for r in csv.DictReader(C7.open(encoding="utf-8")):
    c7.setdefault(r["arm"], {})[r["seed"]] = float(r["RMSE_mu"])

print("=== Q1: the figure CSV's U-Air RMSE at the three affected seeds vs the theta values ===")
NAME = {"FedAvg-Window": "fedavg_window", "FedAsync-Window": "fedasync_window",
        "TimeAlign-Agg": "flamf_timealign_adapted", "Debt-Cal": "debt_cal",
        "Local-Hajek": "local_hajek"}
for fig_name, arm in NAME.items():
    rows = [r for r in fig if r["dataset"] == "U-Air" and r["method"] == fig_name]
    d = {r["seed"]: float(r["RMSE_mu"]) for r in rows}
    mean_fig = sum(d.values()) / len(d)
    if arm in c7:
        theta = c7[arm]
        new = dict(d)
        new.update(theta)
        mean_theta = sum(new.values()) / len(new)
        print(f"  {fig_name:<16} fig mean={mean_fig:.6f}")
        for s in AFFECTED:
            print(f"      seed {s}: figure {d.get(s, float('nan')):.6f}   theta {theta[s]:.6f}"
                  f"   delta {d.get(s, 0) - theta[s]:+.6f}")
        print(f"      -> mean after substituting theta = {mean_theta:.6f}")
    else:
        print(f"  {fig_name:<16} fig mean={mean_fig:.6f}  (no theta record in C7)")

print("\n=== Q2: what is fedavg_window_current? search for its provenance ===")
needle = "fedavg_window_current"
hits = []
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in {".json", ".csv", ".md", ".py", ".txt"}:
        continue
    s = str(p)
    if "\\runs\\" in s or "node_modules" in s or "\\.git" in s or "\\_r13_build\\" in s:
        continue
    try:
        if p.stat().st_size > 3_000_000:
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        continue
    if needle in t:
        hits.append((p.relative_to(ROOT).as_posix(), t.count(needle)))
print(f"  files mentioning it: {len(hits)}")
for rel, n in sorted(hits)[:14]:
    print(f"    {n:>3}x  {rel}")

print("\n=== the frozen tree's own fedavg/local_hajek per-seed RMSE (mirror) ===")
tree = ROOT / "artifacts/e3_formal_runs_r1/runs/uair"
import json
for arm in ("fedavg_window", "local_hajek"):
    vals = {}
    for s in AFFECTED:
        p = tree / arm / f"seed{s}" / "final_metrics.json"
        if p.is_file():
            vals[s] = json.loads(p.read_text(encoding="utf-8"))["RMSE_mu"]
    print(f"  {arm:<14} {vals}")
