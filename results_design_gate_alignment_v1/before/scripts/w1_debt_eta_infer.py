"""Infer and verify the frozen runs' debt step size eta from the recorded trajectory.

Q_{r+1} = [Q_r + eta (mu - omega_r)]_+,  states[j]['debt'] = Q_j (pre-update).
Grid-searches eta on the recorded (alpha, M, mu) and reports the reconstruction error.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                       # noqa: E402

GRID = [0.001, 0.002, 0.005, 0.008, 0.0095, 0.0099, 0.01, 0.0101, 0.0105, 0.011, 0.02]
rows = []
for d in W.DS:
    for arm in ("raven_wo_use", "raven_wo_obs"):
        for seed in W.SEEDS[:5]:
            pi = W.pi_tar_for(d)
            case = W.build_case(d, "R_on", arm, seed, pi)
            n, G = case["n"], case["G"]
            blocks, off = [], 0
            for j in range(n):
                K = len(case["clients"][j])
                blocks.append(np.asarray(case["alpha_arm"][off:off + K], dtype=float))
                off += K
            rec = [np.asarray(x, dtype=float) for x in case["debt"]]
            best = None
            for eta in GRID:
                Q, err = np.zeros(G), 0.0
                for j in range(n):
                    err = max(err, float(np.abs(Q - rec[j]).max()))
                    Q = np.maximum(Q + eta * (case["mu"] - case["M"][j] @ blocks[j]), 0.0)
                err = max(err, float(np.abs(Q - rec[n - 1]).max()))
                if best is None or err < best[1]:
                    best = (eta, err)
            rows.append({"dataset": d, "arm": arm, "seed": seed, "eta_best": best[0],
                         "max_abs_err": best[1]})
for r in rows:
    print(f"{r['dataset']:12s} {r['arm']:15s} seed{r['seed']} eta={r['eta_best']:<7} "
          f"max|Q_prop-Q_rec|_inf={r['max_abs_err']:.3e}")
etas = {r["eta_best"] for r in rows}
errs = [r["max_abs_err"] for r in rows]
print("distinct best eta:", etas, " max error over all:", max(errs))
