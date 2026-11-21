"""Scratch v8: primal-dual interior-point solver for the C_r projection (pure numpy)."""
from __future__ import annotations

import numpy as np


def _clip(x, hi):
    return np.minimum(np.maximum(x, 0.0), hi)


def _clip_sum(v, hi):
    v = np.asarray(v, dtype=float)
    return float(np.maximum(v, 0.0).sum()) - float(np.maximum(v - hi, 0.0).sum())


def solve_tau(v, hi, tol=1e-12):
    v = np.asarray(v, dtype=float)
    if _clip_sum(v, hi) < 1.0 - tol:
        return None
    lo = float(np.min(v)) - hi
    up = float(np.max(v))
    for _ in range(200):
        mid = lo + 0.5 * (up - lo)
        if _clip_sum(v - mid, hi) > 1.0:
            lo = mid
        else:
            up = mid
        if up - lo <= 1e-17 * max(1.0, abs(up)):
            break
    tau = 0.5 * (lo + up)
    for _ in range(4):
        s = _clip_sum(v - tau, hi)
        if s == 1.0:
            break
        n_free = int(np.sum((v - tau > 0.0) & (v - tau < hi)))
        if n_free <= 0:
            break
        cand = tau + (s - 1.0) / float(n_free)
        if abs(_clip_sum(v - cand, hi) - 1.0) < abs(s - 1.0):
            tau = cand
        else:
            break
    return tau


def capped_simplex(v, hi):
    v = np.asarray(v, dtype=float)
    tau = solve_tau(v, hi)
    return None if tau is None else _clip(v - tau, hi)


def feasibility(a, hi, target):
    a = np.asarray(a, dtype=float)
    return max(abs(float(a.sum()) - 1.0), float(max(0.0, -a.min())),
               float(max(0.0, float(a.max()) - hi)),
               float(max(0.0, float(a @ a) - target)))


def _residual(v, hi, target, x, beta, m_lo, m_hi, m_ball, t):
    r1 = x - v + beta - m_lo + m_hi + 2.0 * m_ball * x
    r2 = float(x.sum()) - 1.0
    r3 = x - hi + m_hi / t
    r4 = -x + m_lo / t
    r5 = float(x @ x) - target + m_ball / t
    return float(np.max(np.abs(np.concatenate([r1, [r2], r3, r4, [r5]]))))


def project_Cr(v, a_bar, e_bar, n_stage=60):
    """Projection of v onto C_r by a primal-dual interior-point path (pure numpy)."""
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate", {"nu": 0.0, "mu_sum": None}
    z = np.ones(K)
    s2 = target * 0.8
    disc = 1.0 - s2 * K
    if disc <= 0.0:                                              # pragma: no cover
        s2 = (1.0 - 1e-3) / K
        disc = 1.0 - s2 * K
    eps = min(0.45, (1.0 - np.sqrt(max(disc, 0.0))) / max(K, 1))
    x = eps * np.ones(K) + (1.0 - K * eps) * (np.ones(K) / K)
    x = np.clip(x, 1e-9, hi - 1e-9)
    beta = 0.0
    m_lo = np.ones(K) * 1e-6
    m_hi = np.ones(K) * 1e-6
    m_ball = 1e-6
    t = 1.0
    for _ in range(n_stage):
        t = max(t * 0.5, 1e-16)
        for _ in range(80):
            r1 = x - v + beta - m_lo + m_hi + 2.0 * m_ball * x
            r2 = float(x.sum()) - 1.0
            r3 = x - hi + m_hi / t
            r4 = -x + m_lo / t
            r5 = float(x @ x) - target + m_ball / t
            # solve [ (1+2 m_ball) I   1   -I   I   2x ] [dx]   = -r
            #        [ 1^T            0    0   0    0 ] [db]
            #        [ I              0    0   I/t  0 ] [dh]
            #        [-I              0   I/t  0    0 ] [dl]
            #        [ 2x^T           0    0   0   1/t] [dm]
            d = 1.0 + 2.0 * m_ball
            # eliminate dh, dl, dm:
            #   dh = -t*r3 - t*dx
            #   dl = -t*r4 + t*dx
            #   dm = -t*r5 - 2t*(x.dx)
            # substitute into r1:
            #  (d + 2t + 2t x x^T) dx + 1*db = -r1 + t*r3 - ... => build small system in (dx, db)
            a_mat = np.eye(K) * (d + 2.0 * t) + 2.0 * t * np.outer(x, x)
            b_vec = -r1 - t * (-r3) - t * r4 * 1.0
            # careful substitution
            b_vec = -(r1) + t * r3 + t * r4
            b_vec = b_vec - 2.0 * t * x * (r5 + 0.0) * 0.0
            b_vec = -(r1) + t * r3 + t * r4
            # from r1: d dx + db - dh + dl + 2 dm x = -r1
            # dh = -t r3 - t dx ; dl = -t r4 + t dx ; dm = -t r5 - 2t (x.dx)
            # => (d + 2t + 2t x x^T) dx + db = -r1 - t r3 - t r4 - 2t r5 x
            b_vec = -r1 - t * r3 - t * r4 - 2.0 * t * r5 * x
            big = np.zeros((K + 1, K + 1))
            big[:K, :K] = a_mat
            big[:K, K] = 1.0
            big[K, :K] = 1.0
            rhs = np.concatenate([b_vec, [-r2]])
            try:
                sol = np.linalg.solve(big, rhs)
            except np.linalg.LinAlgError:
                break
            dx = sol[:K]
            db = sol[K]
            dh = -t * r3 - t * dx
            dl = -t * r4 + t * dx
            dm = -t * r5 - 2.0 * t * float(x @ dx)
            step = 1.0
            for _ in range(80):
                xn = x + step * dx
                bl = beta + step * db
                hl = m_hi + step * dh
                ll = m_lo + step * dl
                ml = m_ball + step * dm
                if (xn.min() > 0.0 and xn.max() < hi and ll.min() > 0.0
                        and hl.min() > 0.0 and ml > 0.0):
                    if _residual(v, hi, target, xn, bl, ll, hl, ml, t) < \
                       _residual(v, hi, target, x, beta, m_lo, m_hi, m_ball, t):
                        x, beta, m_lo, m_hi, m_ball = xn, bl, ll, hl, ml
                        break
                step *= 0.5
            else:
                break
        if t <= 1e-16:
            break
    x = np.clip(x, 0.0, hi)
    kind = "ball" if float(x @ x) >= target - 1e-11 else ("cap_simplex" if x.max() >= hi - 1e-11 else "interior")
    if feasibility(x, hi, target) > 1e-12:
        kind = "residual"
    tau = solve_tau(v, hi)
    return x, kind, {"nu": float(m_ball), "mu_sum": (None if tau is None else float(tau))}


if __name__ == "__main__":
    import pathlib
    import sys
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "src"))
    from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
    rng = np.random.default_rng(5)
    bad = 0
    kinds = {}
    for trial in range(300):
        K = int(rng.integers(2, 12))
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
        v = v / v.sum() * float(rng.choice([0.9, 1.0, 1.5, 4.0]))
        x, kind, mult = project_Cr(v, ab, eb)
        f = feasibility(x, ab, 1.0 / eb)
        kinds[kind] = kinds.get(kind, 0) + 1
        if f > 1e-12:
            bad += 1
    print("bad %d/300 kinds=%s" % (bad, kinds))
    worst = 0.0
    for K in range(1, 65):
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        u = np.full(K, 1.0 / K)
        x = project_Cr(u, ab, eb)[0]
        worst = max(worst, float(np.max(np.abs(x - u))))
    print("uniform worst:", worst)
