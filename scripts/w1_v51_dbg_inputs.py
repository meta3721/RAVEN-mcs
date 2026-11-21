"""Diagnostic: what do the projection inputs look like, and where does the oracle fail?"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51_oracle as O                                                      # noqa: E402

E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
pi = {d: W.pi_tar_for(d) for d in W.DS}
for ds in W.DS:
    sums = []
    ks = []
    for seed in W.SEEDS:
        case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
        act = W.active_windows(W.load_json(E3 / ds / "raven" / f"seed{seed}" /
                                           "window_metrics.json"))
        by = {int(x["window_id"]): x for x in act}
        for j in range(case["n"]):
            b = np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
            sums.append(float(b.sum()))
            ks.append(len(case["clients"][j]))
    sums = np.asarray(sums)
    ks = np.asarray(ks)
    print("%-12s n=%d  sum(beta) min=%.6f max=%.6f mean=%.6f  n(sum<1)=%d  K range=%d..%d"
          % (ds, len(sums), sums.min(), sums.max(), sums.mean(),
             int((sums < 1.0).sum()), ks.min(), ks.max()))
    # where does project_Cr get called with sum<1 and what kind comes out
    kinds = {}
    bad = 0
    for seed in W.SEEDS[:6]:
        case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
        act = W.active_windows(W.load_json(E3 / ds / "raven" / f"seed{seed}" /
                                           "window_metrics.json"))
        by = {int(x["window_id"]): x for x in act}
        Q = np.zeros(case["G"])
        for j in range(case["n"]):
            b = np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
            b = b / b.sum()
            w = b + O.KAPPA * (case["M"][j].T @ Q)
            a, kind, mult = O.project_Cr(w, case["a_bar"][j], case["e_bar"][j])
            f = O.feasibility(a, case["a_bar"][j], case["e_bar"][j])
            kinds[kind] = kinds.get(kind, 0) + 1
            if f > 1e-13:
                bad += 1
            Q = np.maximum(Q + O.ETA_DEBT * (case["mu"] - case["M"][j] @ a), 0.0)
    print("   debt-loop kinds=%s  infeasible=%d" % (kinds, bad))
