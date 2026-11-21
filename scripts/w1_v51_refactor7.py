"""Fix the O-G0 audit to use the projection's own multipliers and tighten the feasibility filter."""
import pathlib

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

# 1) O-G0 audit: use the multipliers returned by project_Cr (diag entries carry nu/mu_sum)
old = t[t.index("                for j in range(case[\"n\"]):\n                    K = len(case[\"clients\"][j])\n                    a = a_or[off:off + K]"):
        t.index("                    off += K\n                g0_rows.append(")]
new = '''                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    a = a_or[off:off + K]
                    b = np.asarray(betas[j], dtype=float)
                    b = b / b.sum()
                    d_j = diag[j]
                    if arm == "proj_beta":
                        res = audit_projection(a, b, case["a_bar"][j], case["e_bar"][j],
                                               d_j.get("nu"), d_j.get("mu_sum"))
                        wmax["kind"] = d_j["active"]
                    else:
                        res = audit_debt(a, case["M"][j], qs_or[j], b,
                                         case["a_bar"][j], case["e_bar"][j],
                                         d_j.get("nu"), d_j.get("mu_sum"))
                        wmax["kind"] = d_j["active"]
                    for k in ("primal", "stationarity", "cs"):
                        wmax[k] = max(wmax[k], float(res[k]))
'''
t = t.replace(old, new)

# 2) tighter feasibility filter inside project_Cr
t = t.replace("cands = [c for c in cands if feasibility(c[1], hi, e_bar) <= 1e-9]",
              "cands = [c for c in cands if feasibility(c[1], hi, e_bar) <= 1e-12]")
# 3) polish the SLSQP candidate onto the constraints (renormalise + rescale to the ball)
t = t.replace('''    xs = _slsqp_project(v, hi, target)
    if xs is not None:
        cands.append((float(((xs - v) ** 2).sum()), xs, "slsqp",
                      {"nu": 0.0, "mu_sum": None}))''',
'''    xs = _slsqp_project(v, hi, target)
    if xs is not None:
        nrm = float(np.linalg.norm(xs))
        if nrm > 0 and float(xs @ xs) > target:
            xs = xs * (math.sqrt(target) / nrm)
        if abs(float(xs.sum()) - 1.0) > 0:
            xs = xs / xs.sum()
        xs = _clip(xs, hi)
        if abs(float(xs.sum()) - 1.0) > 1e-15:
            xs = xs / xs.sum()
        cands.append((float(((xs - v) ** 2).sum()), xs, "slsqp",
                      {"nu": 0.0, "mu_sum": None}))''')
p.write_text(t, encoding="utf-8")
print("ok")
