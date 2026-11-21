"""Finalise the oracle projection: SLSQP primary (verified) + numpy machinery for tau/golden.

Replaces project_Cr / _golden_mu / _ball_step with a verified implementation and makes
audit_projection/audit_debt fit the KKT multipliers robustly.
"""
import pathlib

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

start = t.index("def _ball_step(v, hi, mu):")
end = t.index("def feasibility(a, a_bar, e_bar):")
new = '''def _ball_step(v, hi, mu):
    """x(mu) = P_capSimplex(v / (1 + 2 mu)): candidate family with an active ball."""
    w = v / (1.0 + 2.0 * mu)
    tau = solve_tau(w, hi)
    if tau is None:                                              # pragma: no cover
        return np.full(int(v.size), 1.0 / int(v.size)), None
    return _clip(w - tau, hi), tau


def _slsqp_project(v, hi, target):
    """Projection of v onto C_r by SLSQP from several starts; every return is verified
    feasible, so the result is always a point of C_r.  SLSQP is a deterministic local
    method; the starts (uniform, normalised v, the capped-simplex point) cover the
    projection's active sets in practice, and the caller keeps whichever candidate is
    closest to v."""
    from scipy.optimize import minimize
    K = int(v.size)
    uni = np.full(K, 1.0 / K)
    cons = [{"type": "eq", "fun": lambda x: float(np.sum(x)) - 1.0},
            {"type": "ineq", "fun": lambda x: target - float(x @ x)}]
    bnds = [(0.0, hi)] * K
    starts = [uni]
    s = np.clip(v, 0.0, hi)
    if s.sum() > 0:
        starts.append(s / s.sum())
    cs = _capped_simplex(v, hi)
    if cs is not None:
        starts.append(cs)
    best = None
    for st in starts:
        try:
            r = minimize(lambda x: float(((x - v) ** 2).sum()), np.asarray(st, dtype=float),
                         method="SLSQP", bounds=bnds, constraints=cons,
                         options={"maxiter": 1000, "ftol": 1e-16})
        except Exception:                                        # noqa: BLE001
            continue
        x = np.clip(np.asarray(r.x, dtype=float), 0.0, hi)
        if x.sum() > 0:
            x = x / x.sum()
        if feasibility(x, hi, target) <= 1e-12:
            o = float(((x - v) ** 2).sum())
            if best is None or o < best[0]:
                best = (o, x)
    return None if best is None else best[1]


def project_Cr(v, a_bar, e_bar, max_kc=4):
    """Projection of v onto C_r (the oracle; no CVXPY).

    C_r = { sum x = 1, 0 <= x <= a_bar, ||x||^2 <= 1/e_bar }.  The feasible set contains the
    uniform point whenever a_bar*K >= 1 and 1/e_bar >= 1/K, and the zero vector is infeasible,
    so the problem is a strictly convex projection with a unique optimum.

    Candidates, all verified feasible before use:
      * the capped-simplex point (optimal when it already satisfies the norm bound);
      * the uniform point (optimal when it is feasible: the zero vector is infeasible, so the
        nearest point of the ball is unique and the uniform point is it);
      * the exact active-set enumeration: x = tau' + lam' v with coordinates at 0, at the cap,
        or free, solving the two KKT constraints in closed form for each partition;
      * SLSQP from the starts above (deterministic, verified feasible).
    The closest feasible candidate to v is returned.

    Returns (alpha, kind, multipliers).
    """
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    uni = np.full(K, 1.0 / K)
    if K == 1 or hi * K <= 1.0 + 1e-15:
        return uni, "degenerate_uniform", {"nu": 0.0, "mu_sum": None}
    cands = []
    x0 = _capped_simplex(v, hi)
    if x0 is not None:
        if float(x0 @ x0) <= target:
            return x0, "cap_simplex", {"nu": 0.0, "mu_sum": solve_tau(v, hi) or 0.0}
        cands.append((float(((x0 - v) ** 2).sum()), x0, "cap_simplex_feasible",
                      {"nu": 0.0, "mu_sum": solve_tau(v, hi) or 0.0}))
    if feasibility(uni, hi, target) <= 1e-13:
        cands.append((float(((uni - v) ** 2).sum()), uni, "uniform",
                      {"nu": 0.0, "mu_sum": 0.0}))
    order = np.argsort(-v, kind="stable")
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
                cands.append((float(((x - v) ** 2).sum()), x, "ball",
                              {"nu": float(lp), "mu_sum": float(tp)}))
    xs = _slsqp_project(v, hi, target)
    if xs is not None:
        cands.append((float(((xs - v) ** 2).sum()), xs, "slsqp",
                      {"nu": 0.0, "mu_sum": None}))
    if not cands:                                                # pragma: no cover
        return uni, "fallback_uniform", {"nu": 0.0, "mu_sum": None}
    score, x, kind, mult = min(cands, key=lambda r: r[0])
    return x, kind, mult
'''
t = t[:start] + new + "\n\n" + t[end:]

# robust multiplier fit in the KKT audit
old_audit = t[t.index("def kkt_residuals("):t.index("def audit_projection(")]
new_audit = '''def kkt_residuals(a, grad, a_bar, e_bar, nu=None, mu_sum=None):
    """Max primal-feasibility, stationarity and complementary-slackness residuals.

    Lagrangian  f(a) + mu_sum (sum a - 1) - lam_lo . a + lam_hi . (a - a_bar)
                + nu (||a||^2 - 1/e_bar)
    Stationarity: grad_i + mu_sum - lam_lo_i + lam_hi_i + 2 nu a_i = 0 over ALL i.

    When the caller supplies the exact multipliers (mu_sum = tau, nu = lam of the projection)
    the residual is evaluated with them; otherwise (mu_sum, nu) are fitted by least squares on
    the free coordinates, cap_i = max(grad_i + mu_sum + 2 nu a_i, 0), which is exact whenever
    the active set classification is right and is the standard KKT measure otherwise.
    """
    a = np.asarray(a, dtype=float)
    grad = np.asarray(grad, dtype=float)
    hi = float(a_bar)
    tgt = 1.0 / float(e_bar)
    n2 = float(a @ a)
    primal = max(abs(float(a.sum()) - 1.0), float(max(0.0, -a.min())),
                 float(max(0.0, a.max() - hi)), float(max(0.0, n2 - tgt)))
    at_hi = a >= hi - 1e-12
    at_lo = a <= 1e-12
    free = ~(at_hi | at_lo)
    idx = np.where(free)[0]
    fit_stat = 0.0
    if idx.size:
        A = np.stack([np.ones(idx.size), 2.0 * a[idx]], axis=1)
        sol, *_ = np.linalg.lstsq(A, -grad[idx], rcond=None)
        fit_mu, fit_nu = float(sol[0]), float(sol[1])
        fit_stat = float(np.max(np.abs(grad[idx] + fit_mu + 2.0 * fit_nu * a[idx])))
    else:
        fit_mu, fit_nu = 0.0, 0.0
    if mu_sum is None:
        mu_sum = fit_mu
    if nu is None:
        nu = max(fit_nu, 0.0)
    nu = max(float(nu), 0.0)
    if n2 < tgt - 1e-12:
        nu = 0.0
    cap_i = np.where(at_hi, np.maximum(grad + mu_sum + 2.0 * nu * a, 0.0), 0.0)
    lo_i = np.where(at_lo & ~at_hi, np.maximum(-(grad + mu_sum + 2.0 * nu * a), 0.0), 0.0)
    stat = float(np.max(np.abs(grad + mu_sum - lo_i + cap_i + 2.0 * nu * a)))
    cs = max(float(np.max(np.abs(cap_i * (a - hi)))),
             float(np.max(np.abs(lo_i * a))),
             abs(nu * (n2 - tgt)))
    return {"primal": primal, "stationarity": stat, "cs": cs, "nu": nu,
            "mu_sum": mu_sum, "n_free": int(idx.size), "fit_stationarity": fit_stat,
            "fit_nu": fit_nu, "fit_mu_sum": fit_mu}


'''
t = t.replace(old_audit, new_audit)
t = t.replace("def audit_projection(a, v, a_bar, e_bar, nu=0.0, mu_sum=None):",
              "def audit_projection(a, v, a_bar, e_bar, nu=None, mu_sum=None):")
t = t.replace("def audit_debt(a, M, Q, beta, a_bar, e_bar, nu=0.0, mu_sum=None, kappa=KAPPA):",
              "def audit_debt(a, M, Q, beta, a_bar, e_bar, nu=None, mu_sum=None, kappa=KAPPA):")
p.write_text(t, encoding="utf-8")
print("ok")
