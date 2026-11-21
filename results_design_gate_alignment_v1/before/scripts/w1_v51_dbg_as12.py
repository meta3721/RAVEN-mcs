"""Scratch v7: damped-Newton KKT solver for the C_r projection (pure numpy)."""
from __future__ import annotations

import numpy as np

REG = 1e-14


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


def kkt_residual(a, v, hi, beta, capm, mu):
    """Stationarity residual max_i |a_i - v_i + beta - cap_i + 2 mu a_i| (all coordinates)."""
    return float(np.max(np.abs(a - v + beta - capm + 2.0 * mu * a)))


def project_Cr(v, a_bar, e_bar, iters=120):
    """Projection of v onto C_r by damped Newton on the KKT system (pure numpy)."""
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate", {"nu": 0.0, "mu_sum": None}
    x = np.full(K, 1.0 / K)
    cap = np.zeros(K, dtype=bool)
    zero = np.zeros(K, dtype=bool)
    beta, mu = 0.0, 0.0
    capm = np.zeros(K)
    for _ in range(iters):
        free = ~(cap | zero)
        idx = np.where(free)[0]
        ci = np.where(cap)[0]
        nf, nc = idx.size, ci.size
        if nf == 0:
            break
        xf = x[idx]
        vf = v[idx]
        # ---- linearised KKT system in (dx_f, dbeta, dcap, dmu)
        m = nf + 1 + nc + 1
        A = np.zeros((m, m))
        rhs = np.zeros(m)
        A[:nf, :nf] = np.eye(nf) * (1.0 + 2.0 * mu) + REG * np.eye(nf)
        A[:nf, nf] = 1.0
        for t, i in enumerate(ci):
            A[:nf, nf + 1 + t] = -1.0
        A[:nf, nf + 1 + nc] = 2.0 * xf
        res = xf - vf + beta - capm[ci] + 2.0 * mu * xf
        rhs[:nf] = -res
        A[nf, :nf] = 1.0
        rhs[nf] = -(float(xf.sum()) + nc * hi - 1.0)
        for t, i in enumerate(ci):
            A[nf + 1 + t, nf + 1 + t] = 1.0
            rhs[nf + 1 + t] = -(x[i] - hi)
        if mu > 1e-14 or float(xf @ xf) > target:
            A[nf + 1 + nc, :nf] = 2.0 * xf
            rhs[nf + 1 + nc] = -(float(xf @ xf) + nc * hi * hi - target)
        else:
            A[nf + 1 + nc, nf + 1 + nc] = 1.0
            rhs[nf + 1 + nc] = -mu
        try:
            sol = np.linalg.solve(A, rhs)
        except np.linalg.LinAlgError:
            break
        dx = sol[:nf]
        dbeta = sol[nf]
        dcap = sol[nf + 1:nf + 1 + nc]
        dmu = sol[-1]
        # ---- damped step keeping x feasible-ish
        t = 1.0
        for _ in range(60):
            xf_new = xf + t * dx
            cand = np.clip(xf_new, 0.0, hi)
            if float(cand.sum()) + nc * hi >= 1.0 - 1e-12 or True:
                xf_try = cand
                break
            t *= 0.5
        else:                                                    # pragma: no cover
            xf_try = np.clip(xf, 0.0, hi)
        x = x.copy()
        x[idx] = xf_try
        x[ci] = hi
        beta = beta + t * dbeta
        mu = max(0.0, mu + t * dmu)
        capm = capm.copy()
        capm[ci] = np.maximum(capm[ci] + t * dcap, 0.0)
        # ---- active-set update
        newcap = (x >= hi - 1e-15)
        newzero = (x <= 1e-15)
        newcap = newcap & ~newzero
        mult_ok = ~(newcap & (capm <= 1e-15))
        if np.array_equal(newcap, cap) and np.array_equal(newzero, zero):
            if feasibility(x, hi, target) <= 1e-13 and kkt_residual(x, v, hi, beta, capm, mu) <= 1e-11:
                break
        cap, zero = newcap, newzero
    if feasibility(x, hi, target) > 1e-12:
        kind = "residual"
    elif float(x @ x) >= target - 1e-12 and mu > 0.0:
        kind = "ball"
    elif cap.any():
        kind = "cap_simplex"
    else:
        kind = "interior"
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
    kinds = {}
    for trial in range(500):
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
            if bad < 4:
                print("BAD K=%d kind=%s feas=%.3e" % (K, kind, f))
    print("bad %d/500 kinds=%s" % (bad, kinds))
    worst = 0.0
    for K in range(1, 65):
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        u = np.full(K, 1.0 / K)
        x = project_Cr(u, ab, eb)[0]
        worst = max(worst, float(np.max(np.abs(x - u))))
    print("uniform worst:", worst)
