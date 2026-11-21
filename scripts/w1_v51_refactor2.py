"""One-off: make project_Cr return the KKT multipliers and thread them into O-G0."""
import pathlib

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

pairs = [
    # ---- project_Cr: return multipliers
    ('def project_Cr(v, a_bar, e_bar, max_kc=4):',
     'def project_Cr(v, a_bar, e_bar, max_kc=4):'),
    ('    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):\n'
     '        return np.full(K, 1.0 / K), "degenerate"\n'
     '    x0 = _capped_simplex(v, hi)\n'
     '    if x0 is None:\n'
     '        return np.full(K, 1.0 / K), "degenerate_infeasible"\n'
     '    if float(x0 @ x0) <= target:\n'
     '        return x0, "cap_simplex"',
     '    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):\n'
     '        return np.full(K, 1.0 / K), "degenerate", {"nu": 0.0, "mu_sum": None}\n'
     '    x0 = _capped_simplex(v, hi)\n'
     '    if x0 is None:\n'
     '        return np.full(K, 1.0 / K), "degenerate_infeasible", {"nu": 0.0, "mu_sum": None}\n'
     '    if float(x0 @ x0) <= target:\n'
     '        return x0, "cap_simplex", {"nu": 0.0, "mu_sum": solve_tau(v, hi) or 0.0}'),
    ('    order = np.argsort(-v, kind="stable")\n    best = None\n',
     '    order = np.argsort(-v, kind="stable")\n    best = None\n    best_mult = {"nu": 0.0, "mu_sum": None}\n'),
    ('                score = float(((x - v) ** 2).sum())\n'
     '                if best is None or score < best[0]:\n'
     '                    best = (score, x)',
     '                score = float(((x - v) ** 2).sum())\n'
     '                if best is None or score < best[0]:\n'
     '                    best = (score, x)\n'
     '                    best_mult = {"nu": float(lp), "mu_sum": float(tp)}'),
    ('    if best is not None and feasibility(best[1], hi, target) <= 1e-10:\n'
     '        return best[1], "ball"',
     '    if best is not None and feasibility(best[1], hi, target) <= 1e-10:\n'
     '        return best[1], "ball", best_mult'),
    ('        if up > 1e12:                                            # pragma: no cover\n'
     '            return (best[1] if best is not None else x0), "fallback_bound"',
     '        if up > 1e12:                                            # pragma: no cover\n'
     '            return ((best[1] if best is not None else x0), "fallback_bound",\n'
     '                    best_mult)'),
    ('    cand = _ball_step(v, hi, up)\n'
     '    if feasibility(cand, hi, target) <= 1e-11:\n'
     '        return cand, "ball_mu"\n'
     '    return (best[1] if best is not None else x0), "fallback"',
     '    cand = _ball_step(v, hi, up)\n'
     '    if feasibility(cand, hi, target) <= 1e-11:\n'
     '        tau_c = solve_tau(v / (1.0 + 2.0 * up), hi)\n'
     '        return cand, "ball_mu", {"nu": float(up),\n'
     '                                 "mu_sum": (None if tau_c is None\n'
     '                                            else float(tau_c) / (1.0 + 2.0 * up))}\n'
     '    return ((best[1] if best is not None else x0), "fallback", best_mult)'),
    # ---- callers
    ('        a, act = project_Cr(b, case["a_bar"][j], case["e_bar"][j])',
     '        a, act, _mult = project_Cr(b, case["a_bar"][j], case["e_bar"][j])'),
    ('        a, act = project_Cr(w, case["a_bar"][j], case["e_bar"][j])',
     '        a, act, _mult = project_Cr(w, case["a_bar"][j], case["e_bar"][j])'),
    ('        got, act = project_Cr(u, ab, eb)', '        got, act, _mult = project_Cr(u, ab, eb)'),
    ('            a_or, act_or = project_Cr(b, ab, eb)',
     '            a_or, act_or, mult_or = project_Cr(b, ab, eb)'),
    ('            a_or, act_or = project_Cr(b + KAPPA * (case["M"][j].T @ Q), ab, eb)',
     '            a_or, act_or, mult_or = project_Cr(b + KAPPA * (case["M"][j].T @ Q), ab, eb)'),
    ('                         "kkt_cs": res["cs"], "kind_oracle": act_or,',
     '                         "kkt_cs": res["cs"], "kind_oracle": act_or,\n'
     '                         "nu_oracle": mult_or["nu"],\n'
     '                         "nu_fit": res["nu"], "mu_sum_oracle": mult_or["mu_sum"],\n'
     '                         "fit_stationarity": res["fit_stationarity"],'),
    ('    return project_Cr(np.asarray(x, dtype=float), a_bar, e_bar)[0]',
     '    return project_Cr(np.asarray(x, dtype=float), a_bar, e_bar)[0]'),
]
for old, new in pairs:
    if old not in t:
        raise SystemExit("MISSING:\n" + old)
    t = t.replace(old, new)

# probe residuals now take the oracle multipliers
t = t.replace(
    '            res = kkt_residuals(a_or, a_or - b, ab, eb)',
    '            res = kkt_residuals(a_or, a_or - b, ab, eb, nu=mult_or["nu"],\n'
    '                                mu_sum=mult_or["mu_sum"])')
t = t.replace(
    '            res = kkt_residuals(a_or, -(case["M"][j].T @ Q) + (a_or - b) / KAPPA, ab, eb)',
    '            res = kkt_residuals(a_or, -(case["M"][j].T @ Q) + (a_or - b) / KAPPA, ab, eb,\n'
    '                                nu=mult_or["nu"], mu_sum=mult_or["mu_sum"])')
# full-run O-G0 audit: per-window oracle multipliers
t = t.replace(
    '                    if arm == "proj_beta":\n'
    '                        res = audit_projection(a, b, case["a_bar"][j], case["e_bar"][j])\n'
    '                        wmax["kind"] = diag[j]["active"]\n'
    '                    else:\n'
    '                        res = audit_debt(a, case["M"][j], qs_or[j], b,\n'
    '                                         case["a_bar"][j], case["e_bar"][j])\n'
    '                        wmax["kind"] = diag[j]["active"]\n',
    '                    if arm == "proj_beta":\n'
    '                        res = audit_projection(a, b, case["a_bar"][j], case["e_bar"][j],\n'
    '                                               diag[j]["nu"], diag[j]["mu_sum"])\n'
    '                        wmax["kind"] = diag[j]["active"]\n'
    '                    else:\n'
    '                        res = audit_debt(a, case["M"][j], qs_or[j], b,\n'
    '                                         case["a_bar"][j], case["e_bar"][j],\n'
    '                                         diag[j]["nu"], diag[j]["mu_sum"])\n'
    '                        wmax["kind"] = diag[j]["active"]\n')
# oracle_proj_beta / oracle_debt_seq must store the multipliers
t = t.replace('        a, act, _mult = project_Cr(b, case["a_bar"][j], case["e_bar"][j])\n'
              '        alphas.append(a)\n        diag.append({"active": act})',
              '        a, act, mult = project_Cr(b, case["a_bar"][j], case["e_bar"][j])\n'
              '        alphas.append(a)\n        diag.append({"active": act, **mult})')
t = t.replace('        a, act, _mult = project_Cr(w, case["a_bar"][j], case["e_bar"][j])\n'
              '        qs.append(Q.copy())\n        alphas.append(a)\n'
              '        diag.append({"active": act})',
              '        a, act, mult = project_Cr(w, case["a_bar"][j], case["e_bar"][j])\n'
              '        qs.append(Q.copy())\n        alphas.append(a)\n'
              '        diag.append({"active": act, **mult})')
# audit helpers accept multipliers
t = t.replace('def audit_projection(a, v, a_bar, e_bar):\n'
              '    """KKT audit of the projection sub-problem min ||x - v||^2 / 2 on C_r."""\n'
              '    return kkt_residuals(a, np.asarray(a, dtype=float) - np.asarray(v, dtype=float),\n'
              '                         a_bar, e_bar)',
              'def audit_projection(a, v, a_bar, e_bar, nu=0.0, mu_sum=None):\n'
              '    """KKT audit of the projection sub-problem min ||x - v||^2 / 2 on C_r."""\n'
              '    return kkt_residuals(a, np.asarray(a, dtype=float) - np.asarray(v, dtype=float),\n'
              '                         a_bar, e_bar, nu=nu, mu_sum=mu_sum)')
t = t.replace('def audit_debt(a, M, Q, beta, a_bar, e_bar, kappa=KAPPA):',
              'def audit_debt(a, M, Q, beta, a_bar, e_bar, nu=0.0, mu_sum=None, kappa=KAPPA):')
t = t.replace('    grad = -(np.asarray(M, dtype=float).T @ np.asarray(Q, dtype=float)) \\\n'
              '        + (np.asarray(a, dtype=float) - np.asarray(beta, dtype=float)) / float(kappa)\n'
              '    return kkt_residuals(a, grad, a_bar, e_bar)',
              '    grad = -(np.asarray(M, dtype=float).T @ np.asarray(Q, dtype=float)) \\\n'
              '        + (np.asarray(a, dtype=float) - np.asarray(beta, dtype=float)) / float(kappa)\n'
              '    return kkt_residuals(a, grad, a_bar, e_bar, nu=nu, mu_sum=mu_sum)')
p.write_text(t, encoding="utf-8")
print("ok")
