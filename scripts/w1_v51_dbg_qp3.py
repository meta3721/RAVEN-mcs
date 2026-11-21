"""Scratch v5: exact projection onto C_r by enumerating the 3-level active set over ALL roots
of the 2x2 KKT system  x = tau' + lam' v  (no range guess on lam')."""
from __future__ import annotations

import math

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
        mid = 0.5 * (lo + up)
        if _clip_sum(v - mid, hi) > 1.0:
            lo = mid
        else:
            up = mid
        if up - lo <= 1e-17 * max(1.0, abs(up)):
            break
    return 0.5 * (lo + up)


def capped_simplex(v, hi):
    v = np.asarray(v, dtype=float)
    tau = solve_tau(v, hi)
    return None if tau is None else _clip(v - tau, hi)


def _feas(x, hi, target):
    return max(abs(float(x.sum()) - 1.0), float(max(0.0, -x.min())),
               float(max(0.0, float(x.max()) - hi)),
               float(max(0.0, float(x @ x) - target)))


def project_Cr(v, a_bar, e_bar, max_kc=4):
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate"
    x0 = capped_simplex(v, hi)
    if x0 is None:
        return np.full(K, 1.0 / K), "degenerate_infeasible"
    if float(x0 @ x0) <= target:
        return x0, "cap_simplex"
    order = np.argsort(-v, kind="stable")
    best = None
    for kc in range(0, min(max_kc, K - 1) + 1):
        cap_idx = order[:kc]
        rest = order[kc:]
        cc = kc * hi
        for nz in range(0, K - kc):
            nf = K - kc - nz
            free_idx = rest[:nf]
            zero_idx = rest[nf:]
            sf = float(v[free_idx].sum())
            qf = float((v[free_idx] ** 2).sum())
            aa = 1.0 + qf / nf - (sf / nf) ** 2
            bb = 2.0 * (cc - 1.0) / nf
            cq = (kc * hi * hi - target) / nf
            if abs(aa) < 1e-14:
                roots = [-cq / bb] if abs(bb) > 1e-14 else []
            else:
                disc = bb * bb - 4.0 * aa * cq
                if disc < -1e-14 * max(1.0, abs(bb * bb)):
                    continue
                root = math.sqrt(max(0.0, disc))
                roots = [(-bb + root) / (2.0 * aa), (-bb - root) / (2.0 * aa)]
            for lp in roots:
                tp = (1.0 - cc - lp * sf) / nf
                x = np.empty(K)
                x[free_idx] = tp + lp * v[free_idx]
                x[cap_idx] = hi
                x[zero_idx] = 0.0
                if zero_idx.size and float(np.max(v[zero_idx])) > tp + 1e-12:
                    continue
                if cap_idx.size and float(np.min(v[cap_idx])) < tp + 2.0 * lp * hi - 1e-12:
                    continue
                if np.any(x[free_idx] < -1e-12) or np.any(x[free_idx] > hi + 1e-12):
                    continue
                score = float(((x - v) ** 2).sum())
                if best is None or score < best[0]:
                    best = (score, x)
    if best is not None and _feas(best[1], hi, target) <= 1e-10:
        return best[1], "ball"
    # rigorous fallback: bisect the largest mu such that the solution stays feasible
    #   x(mu) = P_capSimplex(v / (1 + 2 mu));  x(0) has norm > target, x -> 0
    lo, up = 0.0, 1.0
    for _ in range(200):
        n2 = float(_ball_step(v, hi, up) @ _ball_step(v, hi, up))
        if n2 <= target:
            break
        up *= 2.0
        if up > 1e12:
            return (best[1] if best is not None else x0), "fallback_bound"
    for _ in range(300):
        mid = 0.5 * (lo + up)
        cand = _ball_step(v, hi, mid)
        if float(cand @ cand) > target:
            lo = mid
        else:
            up = mid
        if up - lo <= 1e-17 * max(1.0, abs(up)):
            break
    cand = _ball_step(v, hi, up)
    if _feas(cand, hi, target) <= 1e-11:
        return cand, "ball_mu"
    return (best[1] if best is not None else x0), "fallback"


def _ball_step(v, hi, mu):
    w = v / (1.0 + 2.0 * mu)
    tau = solve_tau(w, hi)
    if tau is None:
        return np.full(int(v.size), 1.0 / int(v.size))
    return _clip(w - tau, hi)


if __name__ == "__main__":
    import pathlib
    import sys
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "src"))
    from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
    rng = np.random.default_rng(2026)
    bad = none = 0
    kinds = {}
    for trial in range(800):
        K = int(rng.integers(2, 16))
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
        v = v / v.sum() * float(rng.choice([0.8, 1.0, 1.5, 3.0]))
        if v.sum() < 1.0:
            continue
        out = project_Cr(v, ab, eb)
        kinds[out[1]] = kinds.get(out[1], 0) + 1
        f = _feas(out[0], ab, 1.0 / eb)
        if f > 1e-11:
            bad += 1
            if bad < 5:
                print("BAD K=%d kind=%s feas=%.3e" % (K, out[1], f))
    print("bad %d  kinds=%s" % (bad, kinds))
    worst = 0.0
    for K in range(1, 65):
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        u = np.full(K, 1.0 / K)
        a = project_Cr(u, ab, eb)[0]
        worst = max(worst, float(np.max(np.abs(a - u))))
    print("uniform control worst diff:", worst)
