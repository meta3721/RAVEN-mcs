"""Diagnose the frozen runs' debt update rule (G5 L6 mismatch).

Compares the recorded debt trajectory with the protocol's formula
Q_{r+1} = [Q_r + eta (mu - M_r alpha_r)]_+ and with shifted/recorded variants, and
tests whether feeding the *recorded* debt into solve_p2 reproduces the recorded alpha.
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
from raven_mcs.aggregation.p2_cvxpy import solve_p2                         # noqa: E402

d, arm, seed = "sensorscope", "raven_wo_use", 30001
pi = W.pi_tar_for(d)
case = W.build_case(d, "R_on", arm, seed, pi)
n, G = case["n"], case["G"]
blocks_arm = []
off = 0
for j in range(n):
    K = len(case["clients"][j])
    blocks_arm.append(np.asarray(case["alpha_arm"][off:off + K], dtype=float))
    off += K

# recorded debt trajectory (states[j]['debt']) and the protocol's propagation
rec = [np.asarray(x, dtype=float) for x in case["debt"]]
prop, Q = [], np.zeros(G)
for j in range(n):
    Q = np.maximum(Q + float(case["eta"][j]) * (case["mu"] - case["M"][j] @ blocks_arm[j]), 0.0)
    prop.append(Q.copy())

print("recorded: L1 norm per window  first5", [round(float(np.abs(x).sum()), 6) for x in rec[:5]])
print("propagated(protocol):          first5", [round(float(np.abs(x).sum()), 6) for x in prop[:5]])
for shift in (0, 1, -1):
    pairs = [(prop[j], rec[j + shift]) for j in range(n) if 0 <= j + shift < n]
    linf = max(float(np.abs(a - b).max()) for a, b in pairs)
    print(f"  |prop[j]-rec[j{shift:+d}]|_inf = {linf:.6g}")

# ratio test: recorded increment vs residual
inc = [rec[j + 1] - rec[j] for j in range(n - 1)]
res = [case["mu"] - case["M"][j] @ blocks_arm[j] for j in range(n - 1)]
num = float(sum(float(x @ y) for x, y in zip(inc, res)))
den = float(sum(float(y @ y) for y in res))
print("best scalar c in inc ~= c*res : %.6g" % (num / den))
c = num / den
print("residual of that fit: max %.6g" % max(float(np.abs(x - c * y).max())
                                             for x, y in zip(inc, res)))
print("mean |inc| %.6g   mean |res| %.6g   mean |rec| %.6g" %
      (float(np.mean([np.abs(x).sum() for x in inc])),
       float(np.mean([np.abs(x).sum() for x in res])),
       float(np.mean([np.abs(x).sum() for x in rec]))))

# Does the recorded debt reproduce the recorded alpha?  (open-loop Q)
for label, debts in (("recorded", rec), ("protocol-prop", prop), ("zero", [np.zeros(G)] * n)):
    alphas, linf_list = [], []
    for j in range(n):
        r = solve_p2(coverage_matrix=case["M"][j], mu=case["mu"], beta_reference=case["beta"][j],
                     debt=debts[j], variance_diag=case["variance"][j],
                     staleness=case["staleness"][j],
                     lambda_group=float(case["lambdas"]["group"]),
                     lambda_beta=float(case["lambdas"]["beta"]),
                     lambda_variance=float(case["lambdas"]["variance"]),
                     lambda_staleness=float(case["lambdas"]["staleness"]),
                     alpha_max=0.5, e_min=3.0, max_server_learning_rate=1.0, tolerance=1e-6,
                     backend="CLARABEL", instant_calibration=True)
        a = np.asarray(r.alpha, dtype=float)
        alphas.append(a)
        linf_list.append(float(np.abs(a - blocks_arm[j]).max()))
    dg = W.delta_group(case["M"], alphas, case["mu"])
    fm = json.loads((W.E4 / d / arm / f"seed{seed}" / "final_metrics.json").read_text())
    print(f"debt={label:14s}: max_j |alpha-alpha_frozen|_inf = {max(linf_list):.3e}   "
          f"Delta_group={dg:.12f} frozen={float(fm['Delta_group']):.12f}")
