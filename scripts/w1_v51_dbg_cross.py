"""Cross-check the enumeration against SLSQP on the real debt inputs."""
from __future__ import annotations

import pathlib
import sys

import numpy as np
from scipy.optimize import minimize

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51_oracle as O                                                      # noqa: E402

E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"


def slsqp(v, hi, target, x0=None):
    K = int(v.size)
    cons = [{"type": "eq", "fun": lambda x: float(np.sum(x)) - 1.0},
            {"type": "ineq", "fun": lambda x: target - float(x @ x)}]
    bnds = [(0.0, hi)] * K
    best = None
    starts = [np.full(K, 1.0 / K)]
    if x0 is not None:
        starts.append(np.asarray(x0, dtype=float))
    for s in starts:
        try:
            r = minimize(lambda x: float(((x - v) ** 2).sum()), s, method="SLSQP",
                         bounds=bnds, constraints=cons,
                         options={"maxiter": 500, "ftol": 1e-16})
        except Exception:                                        # noqa: BLE001
            continue
        if r.x is None:
            continue
        f = O.feasibility(r.x, hi, target)
        if f <= 1e-12:
            sc = float(((r.x - v) ** 2).sum())
            if best is None or sc < best[0]:
                best = (sc, r.x.copy())
    return best


def main() -> None:
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    fails = 0
    shown = 0
    for ds in W.DS:
        for seed in W.SEEDS[:4]:
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
                ref = slsqp(w, hi, tgt, x0=a)
                if f > 1e-13 or (ref is not None
                                 and float(((a - w) ** 2).sum()) > ref[0] + 1e-12):
                    fails += 1
                    if shown < 5:
                        shown += 1
                        print("MISMATCH K=%d kind=%s feas=%.3e enum_obj=%.12f ref_obj=%s"
                              % (len(w), kind, f, float(((a - w) ** 2).sum()),
                                 "n/a" if ref is None else "%.12f" % ref[0]))
                        print("   w  =", np.round(w, 6), " sum=%.6f" % w.sum())
                        print("   a  =", np.round(a, 6), " sum=%.6f" % a.sum())
                        if ref is not None:
                            print("   ref=", np.round(ref[1], 6))
                Q = np.maximum(Q + O.ETA_DEBT * (case["mu"] - case["M"][j] @ a), 0.0)
    print("mismatches:", fails)


if __name__ == "__main__":
    main()
