"""Diagnostic: which windows really produce infeasible oracle points?"""
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
shown = 0
bad = 0
tot = 0
for ds in ("sensorscope", "uair"):
    for seed in W.SEEDS[:3]:
        case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
        act = W.active_windows(W.load_json(E3 / ds / "raven" / f"seed{seed}" /
                                           "window_metrics.json"))
        by = {int(x["window_id"]): x for x in act}
        Q = np.zeros(case["G"])
        for j in range(case["n"]):
            b = np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
            b = b / b.sum()
            w = b + O.KAPPA * (case["M"][j].T @ Q)
            hi, eb = case["a_bar"][j], case["e_bar"][j]
            tgt = 1.0 / eb
            a, kind, mult = O.project_Cr(w, hi, eb)
            f = O.feasibility(a, hi, tgt)
            tot += 1
            if f > 1e-13:
                bad += 1
                if shown < 6:
                    shown += 1
                    print("BAD K=%d hi=%.4f eb=%.4f tgt=%.6f kind=%s feas=%.3e"
                          % (len(w), hi, eb, tgt, kind, f))
                    print("   w=%s sum=%.6f" % (np.round(w, 6), w.sum()))
                    print("   a=%s sum=%.6f n2=%.6f" % (np.round(a, 8), a.sum(), float(a @ a)))
                    uni = np.full(len(w), 1.0 / len(w))
                    print("   uniform feas=%.3e" % O.feasibility(uni, hi, tgt))
            Q = np.maximum(Q + O.ETA_DEBT * (case["mu"] - case["M"][j] @ a), 0.0)
print("bad %d / %d" % (bad, tot))
