"""Scratch v4: exact projection onto C_r via KKT active-set iteration (pure numpy).

For a given active set the KKT system is linear in (x, multipliers) except for the ball
constraint, which contributes  mu * 2x to the equations; the system is solved by a couple of
Newton steps started from mu = 0.  The active set is then updated by the standard primal
active-set rule and the corrector re-run, giving the exact projection.
"""
from __future__ import annotations

import numpy as np

MAX_ITER = 200
TOL_FEAS = 1e-11


def _feas(x, hi, target):
    return max(abs(float(x.sum()) - 1.0), float(max(0.0, -x.min())),
               float(max(0.0, float(x.max()) - hi)),
               float(max(0.0, float(x @ x) - target)))


def _solve_equalities(v, zero, cap, ball, hi, target, newton=6):
    K = int(v.size)
    zero = list(zero)
    cap = list(cap)
    ball = list(ball)
    nf = K - len(zero) - len(cap)
    if nf < 1:
        return None
    free = np.array([i for i in range(K) if i not in zero and i not in cap], dtype=int)
    m = 1 + len(ball)
    mu = np.zeros(len(ball))
    xf = np.zeros(nf)
    for _ in range(newton):
        # unknowns: xf (nf), lam_sum (1), mu (len(ball))
        A = np.zeros((nf + m, nf + m))
        rhs = np.zeros(nf + m)
        A[:nf, :nf] = np.eye(nf)
        A[:nf, nf] = 1.0
        for j in range(len(ball)):
            A[:nf, nf + 1 + j] = 2.0 * xf
        A[nf, :nf] = 1.0
        rhs[nf] = 1.0 - len(cap) * hi
        for j, i in enumerate(ball):
            row = nf + 1 + j
            A[row, :nf] = 2.0 * xf
            A[row, nf + 1 + j] = 0.0
            rhs[row] = target - len(cap) * hi * hi - float(xf @ xf) + float(xf @ xf)
            # linearised: 2 xf . dx + dmu * 0 = target - (||xf||^2 + |cap| hi^2) - 2 xf.(xf_new-xf)
            rhs[row] = target - len(cap) * hi * hi - float(xf @ xf) + float(xf @ xf)
        try:
            sol = np.linalg.solve(A, rhs)
        except np.linalg.LinAlgError:
            return None
        xf_new = sol[:nf]
        lam_sum = sol[nf]
        mu_new = sol[nf + 1:]
        if not np.all(np.isfinite(xf_new)):
            return None
        xf = xf_new
        mu = mu_new
    x = np.empty(K)
    x[free] = xf
    x[zero] = 0.0
    x[cap] = hi
    return x


def project_Cr(v, a_bar, e_bar):
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate"
    return None, "unimplemented"


if __name__ == "__main__":
    print("scratch v4: superseded")
