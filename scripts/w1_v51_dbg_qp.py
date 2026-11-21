"""Scratch v3: exact equality-constrained active-set QP solver for C_r, pure numpy."""
from __future__ import annotations

import numpy as np

REG = 1e-12
MAX_ACTIVE = 6


def _feas(x, hi, target):
    return max(abs(float(x.sum()) - 1.0), float(max(0.0, -x.min())),
               float(max(0.0, float(x.max()) - hi)),
               float(max(0.0, float(x @ x) - target)))


def solve_equalities(v, hi, target, active):
    """Exact minimiser of ||x - v||^2 s.t. sum x = 1, x_i = 0 (i in zero),
    x_i = hi (i in cap), sum_{i in ball_set} x_i^2 = target."""
    K = int(v.size)
    zero, cap, ball = active
    nf = K - len(zero) - len(cap)
    if nf < 1:
        return None
    free = np.array([i for i in range(K) if i not in zero and i not in cap], dtype=int)
    a = np.zeros((nf + 1 + len(ball), nf + 1 + len(ball)))
    a[:nf, :nf] = np.eye(nf) * (1.0 + REG)
    a[:nf, nf] = 1.0
    a[nf, :nf] = 1.0
    if len(ball):
        a[:nf, nf + 1:] = 2.0 * v[free].reshape(-1, 1)
    for j, i in enumerate(ball):
        a[nf + 1 + j, :nf] = 2.0 * v[i]
    if len(ball):
        a[nf + 1:, nf + 1:] = np.eye(len(ball)) * REG
    rhs = np.concatenate([v[free], [1.0 - len(cap) * hi],
                          [target - len(cap) * hi * hi]])
    try:
        sol = np.linalg.solve(a, rhs)
    except np.linalg.LinAlgError:
        return None
    x = np.empty(K)
    x[free] = sol[:nf]
    x[zero] = 0.0
    x[cap] = hi
    return x


def project_Cr(v, a_bar, e_bar, max_active=MAX_ACTIVE):
    """Exact Euclidean projection of v onto C_r (pure numpy, equality-constrained active set)."""
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate"
    # ---- constraints in the form  a . x  {=,>=} b
    rows = [np.ones(K), -np.ones(K)]
    rhs = [1.0, -1.0]
    eq = [True, True]
    for i in range(K):                       # x_i <= hi
        r = np.zeros(K); r[i] = 1.0
        rows.append(r); rhs.append(hi); eq.append(False)
    for i in range(K):                       # -x_i <= 0
        r = np.zeros(K); r[i] = -1.0
        rows.append(r); rhs.append(0.0); eq.append(False)
    A = np.asarray(rows)
    b = np.asarray(rhs, dtype=float)
    eq = np.asarray(eq, dtype=bool)
    if float(v @ v) <= target:
        x = v.copy()
    elif np.max(np.abs(np.ones(K) - v)) < 1e-16:
        x = np.ones(K) / K
    else:
        x = np.ones(K) / K                   # strictly feasible start (uniform is in C_r)
    for _ in range(400):
        grad = x - v
        w = A @ x - b
        act = [i for i in range(len(b)) if eq[i] or w[i] > -1e-12]
        ball_active = False
        if float(x @ x) > target - 1e-13:
            ball_active = True
            act = act + [len(b)]
        if ball_active and len(act) > max_active:
            act = act[:max_active]
        if not act:
            break
        Aa = np.vstack([A[act], 2.0 * x.reshape(1, -1)]) if ball_active else A[act]
        if len(act) == 1 and not ball_active:
            Aa = A[act]
        lam = np.linalg.lstsq(Aa.T, -grad, rcond=None)[0]
        if not len(lam) or np.max(np.abs(Aa.T @ lam + grad)) > 1e-10:
            return None
        if np.all(lam >= -1e-12):
            break
        if ball_active and lam[-1] < -1e-12:
            # ball constraint is not needed: re-solve without it
            Aa = A[act[:-1]]
            lam = np.linalg.lstsq(Aa.T, -grad, rcond=None)[0]
            if len(act) - 1 == 0:
                break
            if np.all(lam >= -1e-12):
                break
        neg = [j for j in range(len(lam)) if lam[j] < -1e-12]
        j = neg[int(np.argmin([lam[j] for j in neg]))]
        p = np.linalg.lstsq(Aa.T, np.zeros(Aa.shape[0]), rcond=None)[0]
        p = -np.linalg.lstsq(Aa.T, -grad, rcond=None)[0]
        # direction: solve Aa . p = 0 with Aa p = 0 and reduce the objective
        p = _null_direction(Aa, grad)
        if p is None:
            break
        alpha = np.inf
        Ad = A @ p
        for i in range(len(b)):
            if eq[i] or Ad[i] <= 1e-14:
                continue
            t = (b[i] - (A @ x)[i]) / Ad[i]
            if t > 1e-14:
                alpha = min(alpha, t)
        nb = 2.0 * float(x @ p)
        if nb > 1e-14:
            alpha = min(alpha, (target - float(x @ x)) / nb)
        if not np.isfinite(alpha):
            break
        x = x + alpha * p
    if _feas(x, hi, target) > 1e-9:
        return None
    return x, "active_set"


def _null_direction(Aa, grad):
    """p = -H^{-1}(grad + Aa^T lam) restricted to Aa p = 0, H = I."""
    m, n = Aa.shape
    if m == 0:
        return -grad
    # reduced space: p = N z with N an orthonormal basis of null(Aa)
    u, s, vt = np.linalg.svd(Aa)
    rank = int(np.sum(s > 1e-12 * max(s[0], 1.0)))
    N = vt[rank:].T
    if N.shape[1] == 0:
        return None
    g = N.T @ grad
    z = np.linalg.lstsq(N.T @ N * (1.0 + 1e-12), -g, rcond=None)[0]
    return N @ z


if __name__ == "__main__":
    import math
    import pathlib
    import sys
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "scripts"))
    from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
    from w1_v51_oracle import capped_simplex, solve_tau, _clip_sum

    def proj_ref(v, hi, target):
        x0 = capped_simplex(v, hi)
        if x0 is None:
            return np.ones(int(v.size)) / int(v.size)
        if float(x0 @ x0) <= target:
            return x0
        return None

    rng = np.random.default_rng(2026)
    bad = none = 0
    n = 0
    for trial in range(500):
        K = int(rng.integers(2, 16))
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
        v = v / v.sum() * float(rng.choice([0.8, 1.0, 1.5, 3.0]))
        out = project_Cr(v, ab, eb)
        n += 1
        if out is None:
            none += 1
            continue
        x, act = out
        f = _feas(x, ab, 1.0 / eb)
        if f > 1e-9:
            bad += 1
            if bad < 4:
                print("BAD K=%d feas=%.2e act=%s" % (K, f, act))
    print("bad %d, none %d, of %d" % (bad, none, n))
    worst = 0.0
    for K in range(1, 65):
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        u = np.full(K, 1.0 / K)
        out = project_Cr(u, ab, eb)
        a = out[0]
        worst = max(worst, float(np.max(np.abs(a - u))))
    print("uniform control worst diff:", worst)
