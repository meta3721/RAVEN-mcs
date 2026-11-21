"""Install the final project_Cr (enumeration + golden-section fallback) into w1_v51_oracle.py."""
import pathlib

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

new_body = '''def _norm2_capped(v, hi, lam):
    x = _clip(v / (1.0 + 2.0 * lam), hi)
    return float(x @ x), x


def _ball_step(v, hi, mu):
    """x(mu) = P_capSimplex(v / (1 + 2 mu)): the candidate family with an active ball."""
    w = v / (1.0 + 2.0 * mu)
    tau = solve_tau(w, hi)
    if tau is None:                                              # pragma: no cover
        return np.full(int(v.size), 1.0 / int(v.size)), None
    return _clip(w - tau, hi), tau


def _golden_mu(v, hi, target, x0):
    """Minimise ||x(mu) - v||^2 over mu >= 0 by golden-section search.

    Globally convergent on [0, MU_MAX] because the map is continuous; used only as the
    fallback when the active-set enumeration finds no feasible candidate.  Since
    x(mu) = P_capSimplex(v/(1+2mu)) and P_capSimplex is non-expansive,
    ||x(mu) - v|| >= ||v|| - ||x(mu)|| >= ||v|| - 1, so MU_MAX = (||v|| - 1)/2 is a valid
    upper end (x(MU_MAX) collapses towards the uniform point).
    """
    def f(mu):
        x, _tau = _ball_step(v, hi, mu)
        return float(((x - v) ** 2).sum()), x

    lo, up = 0.0, max(0.5 * (float(np.linalg.norm(v)) - 1.0), 1e-6)
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = up - gr * (up - lo), lo + gr * (up - lo)
    fc, fd = f(c), f(d)
    for _ in range(400):
        if fc[0] < fd[0]:
            up, d, fd = d, c, fc
            c = up - gr * (up - lo)
            fc = f(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + gr * (up - lo)
            fd = f(d)
        if up - lo <= 1e-16 * max(1.0, up):
            break
    best = min([f(lo), f(up), f(0.5 * (lo + up)), fc, fd], key=lambda r: r[0])
    score, x = best
    if feasibility(x, hi, target) <= 1e-9 and score <= float(((x0 - v) ** 2).sum()) + 1e-9:
        return x, "ball_mu"
    return None, "none"


def project_Cr(v, a_bar, e_bar, max_kc=4):
    """Projection of v onto C_r (pure numpy; no CVXPY).

    Primary: three-level active-set enumeration.  The solution has the form
    x = tau' + lam' v with each coordinate at 0, at the cap a_bar, or free (stationarity plus
    complementary slackness); for each partition the two constraints give a quadratic in lam'
    whose roots are both tried.  Candidates must reproduce the partition, satisfy the sum and
    the cap, and respect the norm bound.

    Fallback: golden-section minimisation of ||x(mu) - v||^2 over the family
    x(mu) = P_capSimplex(v / (1 + 2 mu)), which is the correct family whenever the ball
    constraint is the only additional active one; it is non-expansive and globally convergent.

    Returns (alpha, kind, multipliers).
    """
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate", {"nu": 0.0, "mu_sum": None}
    x0 = _capped_simplex(v, hi)
    if x0 is None:
        # sum_i clip(v_i, 0, hi) < 1: the point must lie on the ball; use the fallback family
        xg, kind = _golden_mu(v, hi, target, np.full(K, 1.0 / K))
        if xg is not None:
            return xg, kind, {"nu": 0.0, "mu_sum": None}
        return np.full(K, 1.0 / K), "degenerate_infeasible", {"nu": 0.0, "mu_sum": None}
    if float(x0 @ x0) <= target:
        return x0, "cap_simplex", {"nu": 0.0, "mu_sum": solve_tau(v, hi) or 0.0}
    order = np.argsort(-v, kind="stable")
    best = None
    best_mult = {"nu": 0.0, "mu_sum": None}
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
                if feasibility(x, hi, target) > 1e-10:
                    continue
                score = float(((x - v) ** 2).sum())
                if best is None or score < best[0]:
                    best = (score, x)
                    best_mult = {"nu": float(lp), "mu_sum": float(tp)}
    xg, kind_g = _golden_mu(v, hi, target, x0)
    cands = []
    if best is not None:
        cands.append((best[0], best[1], "ball", best_mult))
    if xg is not None:
        cands.append((float(((xg - v) ** 2).sum()), xg, kind_g,
                      {"nu": 0.0, "mu_sum": None}))
    if not cands:                                                # pragma: no cover
        return x0, "fallback", {"nu": 0.0, "mu_sum": None}
    score, x, kind, mult = min(cands, key=lambda r: r[0])
    return x, kind, mult
'''

start = t.index("def _norm2_capped(v, hi, lam):")
end = t.index("def feasibility(a, a_bar, e_bar):")
t = t[:start] + new_body + "\n\n" + t[end:]
p.write_text(t, encoding="utf-8")
print("installed")
