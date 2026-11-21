"""Quick development check of the v5.1a oracle: patterns hit, KKT residuals, speed.

Writes nothing.  Run:  python scripts/w1_v51a_probe.py [n_runs] [ds]
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51a_oracle as O                                                     # noqa: E402

TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
TOL = {"primal": 1e-13, "stationarity": 1e-12, "cs": 1e-12}


def main() -> None:
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    dss = [sys.argv[2]] if len(sys.argv) > 2 else ["sensorscope", "uair"]
    pi = {d: W.pi_tar_for(d) for d in dss}
    kinds: dict = {}
    worst = {"primal": 0.0, "stationarity": 0.0, "cs": 0.0}
    where = {}
    t0 = time.perf_counter()
    n_win = 0
    for ds in dss:
        for arm in ("proj_beta", "proj_beta_debt"):
            for seed in range(30001, 30001 + n_runs):
                case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
                if case is None:
                    continue
                wm = W.load_json(TRAIN / ds / arm / ("seed%d" % seed) / "window_metrics.json")
                by = {int(w["window_id"]): w for w in W.active_windows(wm)}
                betas = [np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
                         for j in range(case["n"])]
                if arm == "proj_beta":
                    a_or, diag = O.oracle_proj_beta(betas, case)
                    qs = [None] * case["n"]
                else:
                    a_or, qs, diag = O.oracle_debt_seq(case, betas)
                off = 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    a = a_or[off:off + K]
                    off += K
                    n_win += 1
                    d = diag[j]
                    if arm == "proj_beta":
                        res = O.audit_projection(a, d["v"], case["a_bar"][j], case["e_bar"][j],
                                                 d["mult"])
                    else:
                        res = O.audit_debt(a, case["M"][j], qs[j], d["beta"],
                                           case["a_bar"][j], case["e_bar"][j], d["mult"])
                    kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
                    for k in worst:
                        if res[k] > worst[k]:
                            worst[k] = res[k]
                            where[k] = (ds, arm, seed, j, K, d["kind"])
    dt = time.perf_counter() - t0
    print("windows %d in %.1fs (%.0f us/window)" % (n_win, dt, 1e6 * dt / max(1, n_win)))
    print("kinds", kinds)
    for k in ("primal", "stationarity", "cs"):
        print("%-13s max=%.3e tol=%.0e pass=%s where=%s"
              % (k, worst[k], TOL[k], worst[k] <= TOL[k], where.get(k)))


if __name__ == "__main__":
    main()
