"""Final oracle tightening: verify the selected candidate is the projection (KKT), and make
the candidate set include the ball-boundary parametrisation of the input direction."""
import pathlib

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

helper = '''def _proj_kkt_violation(v, hi, target, x):
    """Necessary-condition residual for x being the projection of v onto C_r.

    For a projection the KKT system  x - v + beta - cap + 2 mu x = 0  with mu >= 0, cap >= 0,
    0 <= x <= hi must hold.  The multipliers are fitted on the free coordinates; the residual
    is the max violation including the bound/ball complementarity terms.  Returns inf when the
    point is infeasible.
    """
    x = np.asarray(x, dtype=float)
    if feasibility(x, hi, target) > 1e-9:
        return float("inf")
    at_hi = x >= hi - 1e-12
    at_lo = x <= 1e-12
    free = ~(at_hi | at_lo)
    idx = np.where(free)[0]
    if idx.size >= 2:
        A = np.stack([np.ones(idx.size), 2.0 * x[idx]], axis=1)
        sol, *_ = np.linalg.lstsq(A, -(x - v)[idx], rcond=None)
        beta, mu = float(sol[0]), float(sol[1])
    elif idx.size == 1:
        i = int(idx[0])
        if abs(2.0 * x[i]) > 1e-12:
            mu = 0.0
            beta = float(v[i] - x[i])
        else:                                                    # pragma: no cover
            mu, beta = 0.0, float(v[i] - x[i])
    else:
        beta, mu = 0.0, 0.0
    mu = max(mu, 0.0)
    if float(x @ x) < target - 1e-12:
        mu = 0.0
    cap = np.where(at_hi, np.maximum(x - v + beta + 2.0 * mu * x, 0.0), 0.0)
    lo = np.where(at_lo & ~at_hi, np.maximum(-(x - v + beta + 2.0 * mu * x), 0.0), 0.0)
    stat = float(np.max(np.abs(x - v + beta + 2.0 * mu * x - cap + lo)))
    return max(stat, abs(mu * (float(x @ x) - target)))


'''
t = t.replace("def project_Cr(v, a_bar, e_bar, max_kc=4):", helper + "def project_Cr(v, a_bar, e_bar, max_kc=4):")
t = t.replace('''    score, x, kind, mult = min(cands, key=lambda r: r[0])
    return x, kind, mult''',
'''    score, x, kind, mult = min(cands, key=lambda r: r[0])
    # verify the winner against the projection KKT conditions; if it fails, prefer any
    # candidate that passes and is no further from v
    if _proj_kkt_violation(v, hi, target, x) > 1e-7:
        ok = [c for c in cands if _proj_kkt_violation(v, hi, target, c[1]) <= 1e-7]
        if ok:                                                   # pragma: no cover
            score, x, kind, mult = min(ok, key=lambda r: r[0])
        else:
            kind = kind + "_unverified"
    return x, kind, mult''')
# also add the direction-scaled ball point as an SLSQP start
t = t.replace('''    cs = _capped_simplex(v, hi)
    if cs is not None:
        starts.append(cs)''',
'''    cs = _capped_simplex(v, hi)
    if cs is not None:
        starts.append(cs)
    nv = float(np.linalg.norm(v))
    if nv > 0:                                                   # ball-boundary point along v
        p = v * (math.sqrt(target) / nv)
        p = np.clip(p, 0.0, hi)
        if p.sum() > 0:
            starts.append(p / p.sum())''')
p.write_text(t, encoding="utf-8")
print("ok")
