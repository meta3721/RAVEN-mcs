"""Scratch v6: primal active-set Newton solver for the C_r projection (pure numpy)."""
from __future__ import annotations

import numpy as np

TOL = 1e-14
ITERS = 100


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


def project_Cr(v, a_bar, e_bar):
    """Exact Euclidean projection of v onto C_r, by primal active-set Newton (pure numpy).

    KKT:   x_i - v_i + beta - cap_i + 2 mu x_i = 0   (i free)
           sum x = 1,  0 <= x <= a_bar,  ||x||^2 <= target.
    The linearised system for (x_F, beta, cap, mu) is solved in closed form (block
    elimination); mu >= 0 is imposed analytically from the ball equation
        mu = (x_F . (v_F - beta) - x_F . cap) / (2 ||x_F||^2).
    Returns (x, kind, multipliers).
    """
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate", {"nu": 0.0, "mu_sum": None}
    x = np.full(K, 1.0 / K)
    cap = np.zeros(K, dtype=bool)
    zero = np.zeros(K, dtype=bool)
    mu = 0.0
    kind = "active_set"
    for _ in range(ITERS):
        free = ~(cap | zero)
        idx = np.where(free)[0]
        nf = idx.size
        if nf == 0:
            break
        xf = x[idx]
        vf = v[idx]
        ci = np.where(cap)[0]
        nc = ci.size
        cvec = 2.0 * xf
        q = float(xf @ vf) - float(xf @ xf) - (hi * float(xf[ci].sum()) if nc else 0.0)
        s_f = float(xf.sum())
        q_f = float((xf ** 2).sum())
        q_c = float((xf[ci] ** 2).sum()) if nc else 0.0
        r_a = 1.0 - nc * hi - s_f
        r_b = target - nc * hi * hi - q_c - q_f
        aa = float(cvec @ cvec)
        if aa < 1e-15:
            break
        beta = (2.0 * q + r_b) / (2.0 * s_f)
        mu_new = (float(cvec @ vf) - beta * s_f - 2.0 * q_c) / (2.0 * aa)
        cap_new = vf - beta + 2.0 * mu_new * xf
        xf_new = vf - beta + 2.0 * mu_new * xf - cap_new
        x_new = x.copy()
        x_new[idx] = xf_new
        x_new[ci] = hi
        # ---- active-set update
        mu_new = max(mu_new, 0.0)
        changed = False
        for i in idx:
            if x_new[i] <= 0.0 and not zero[i]:
                zero[i] = True
                changed = True
        for i in range(K):
            if not cap[i] and not zero[i] and x_new[i] > hi:
                cap[i] = True
                changed = True
        for i in ci:
            if cap_new[list(ci).index(i)] < 0.0:
                cap[i] = False
                changed = True
        for i in range(K):
            if zero[i] and False:
                pass
        x = np.clip(x_new, 0.0, hi)
        x = x / x.sum() * 1.0
        mu = mu_new
        if not changed:
            if feasibility(x, hi, target) <= 1e-13:
                break
            # nudge: rebind the active set from the current point
            cap = x >= hi - 1e-15
            zero = x <= 1e-15
    if feasibility(x, hi, target) > 1e-12:
        kind = "residual"
    tau = solve_tau(v, hi)
    return x, kind, {"nu": float(mu), "mu_sum": (None if tau is None else float(tau))}


if __name__ == "__main__":
    import pathlib
    import sys
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "src"))
    from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
    rng = np.random.default_rng(5)
    bad = 0
    for trial in range(400):
        K = int(rng.integers(2, 12))
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
        v = v / v.sum() * float(rng.choice([0.9, 1.0, 1.5, 4.0]))
        x, kind, mult = project_Cr(v, ab, eb)
        f = feasibility(x, ab, 1.0 / eb)
        if f > 1e-12:
            bad += 1
            if bad < 4:
                print("BAD K=%d kind=%s feas=%.3e" % (K, kind, f))
    print("bad %d/400" % bad)
    worst = 0.0
    for K in range(1, 65):
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        u = np.full(K, 1.0 / K)
        x = project_Cr(u, ab, eb)[0]
        worst = max(worst, float(np.max(np.abs(x - u))))
    print("uniform worst:", worst)
