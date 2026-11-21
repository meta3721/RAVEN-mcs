"""Diagnostic: trained alpha vs oracle alpha, window by window."""
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
for ds in ("sensorscope",):
    for arm in ("proj_beta", "proj_beta_debt"):
        for seed in (30001,):
            ri = O.run_inputs(ds, arm, seed, pi[ds])
            case = ri["case"]
            a_tr = O.trained_alpha(case, ri["act"], arm)
            if arm == "proj_beta":
                a_or, diag = O.oracle_proj_beta(ri["betas"], case)
            else:
                a_or, qs, diag = O.oracle_debt_seq(case, ri["betas"])
            print("== %s %s seed%d" % (ds, arm, seed))
            off = 0
            worst = []
            for j in range(case["n"]):
                K = len(case["clients"][j])
                d = float(np.max(np.abs(a_tr[off:off + K] - a_or[off:off + K])))
                worst.append((d, j, K, diag[j]["active"]))
                if d > 1e-9 and len([x for x in worst if x[0] > 1e-9]) <= 3:
                    w = np.asarray(ri["betas"][j], dtype=float)
                    w = w / w.sum()
                    print("  win=%d K=%d kind=%s d=%.6f" % (j, K, diag[j]["active"], d))
                    print("    trained=%s" % np.round(a_tr[off:off + K], 8))
                    print("    oracle =%s" % np.round(a_or[off:off + K], 8))
                    print("    beta/  =%s sum=%.6f" % (np.round(w, 8), w.sum()))
                    print("    a_bar=%.4f e_bar=%.4f" % (case["a_bar"][j], case["e_bar"][j]))
                off += K
            worst.sort(reverse=True)
            print("  n_windows=%d  worst=%s" % (case["n"], worst[:3]))
            print("  max diff = %.6f" % worst[0][0])
