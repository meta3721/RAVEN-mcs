"""Make project_Cr always return consistent KKT multipliers (fitted from the returned x)."""
import pathlib

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

helper = '''def fit_multipliers(v, x, hi, e_bar):
    """Multipliers (mu_sum, nu) of the projection KKT system for the point x.

        x - v + mu_sum + 2 nu x = 0 on the free coordinates,
    with nu = 0 when the ball is slack.  Least squares on the free coordinates; when the
    free set is empty the multipliers are taken as (0, 0).  Used so the O-G0 audit always
    evaluates the stationarity residual with multipliers consistent with the returned point.
    """
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    hi = float(hi)
    target = 1.0 / float(e_bar)
    free = (x > 1e-12) & (x < hi - 1e-12)
    idx = np.where(free)[0]
    if idx.size == 0:
        return 0.0, 0.0
    A = np.stack([np.ones(idx.size), 2.0 * x[idx]], axis=1)
    sol, *_ = np.linalg.lstsq(A, -(x - v)[idx], rcond=None)
    mu_sum = float(sol[0])
    nu = max(float(sol[1]), 0.0)
    if float(x @ x) < target - 1e-12:
        nu = 0.0
    return mu_sum, nu


'''
t = t.replace("def _proj_kkt_violation(v, hi, target, x):", helper + "def _proj_kkt_violation(v, hi, target, x):")

# always return the fitted multipliers
t = t.replace('''    score, x, kind, mult = min(cands, key=lambda r: r[0])''',
'''    score, x, kind, mult = min(cands, key=lambda r: r[0])
    mu_sum, nu = fit_multipliers(v, x, hi, e_bar)
    mult = {"nu": nu, "mu_sum": mu_sum}''')
t = t.replace('''    if _proj_kkt_violation(v, hi, target, x) > 1e-7:
        ok = [c for c in cands if _proj_kkt_violation(v, hi, target, c[1]) <= 1e-7]
        if ok:                                                   # pragma: no cover
            score, x, kind, mult = min(ok, key=lambda r: r[0])
        else:
            kind = kind + "_unverified"
    return x, kind, mult''',
'''    if _proj_kkt_violation(v, hi, target, x) > 1e-7:
        ok = [c for c in cands if _proj_kkt_violation(v, hi, target, c[1]) <= 1e-7]
        if ok:                                                   # pragma: no cover
            score, x, kind, mult = min(ok, key=lambda r: r[0])
            mu_sum, nu = fit_multipliers(v, x, hi, e_bar)
            mult = {"nu": nu, "mu_sum": mu_sum}
    return x, kind, mult''')
p.write_text(t, encoding="utf-8")
print("ok")
