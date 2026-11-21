"""One-off refactor of scripts/w1_v51_oracle.py after the projection rewrite (throwaway)."""
import pathlib

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

start = t.index("def _project_ball_simplex(v, hi, target):")
end = t.index("def _ball_step(v, hi, mu):")
t = t[:start] + t[end:]

first = t.index("def feasibility(a, a_bar, e_bar):")
second = t.index("def feasibility(a, a_bar, e_bar):", first + 10)
end2 = t.index("def project_back(", second)
t = t[:second] + t[end2:]

pairs = (
    ('a, lam, act = project_Cr(b, case["a_bar"][j], case["e_bar"][j])',
     'a, act = project_Cr(b, case["a_bar"][j], case["e_bar"][j])'),
    ('a, lam, act = project_Cr(w, case["a_bar"][j], case["e_bar"][j])',
     'a, act = project_Cr(w, case["a_bar"][j], case["e_bar"][j])'),
    ('got, lam, act = project_Cr(u, ab, eb)', 'got, act = project_Cr(u, ab, eb)'),
    ('a_or, lam, _ = project_Cr(b, ab, eb)', 'a_or, act_or = project_Cr(b, ab, eb)'),
    ('a_or, lam, _ = project_Cr(b + KAPPA * (case["M"][j].T @ Q), ab, eb)',
     'a_or, act_or = project_Cr(b + KAPPA * (case["M"][j].T @ Q), ab, eb)'),
    ('"lam_oracle": lam,', '"kind_oracle": act_or,'),
    ('wmax["lam_max"] = max(wmax["lam_max"], float(diag[j]["lam"]))',
     'wmax["kind"] = diag[j]["active"]'),
    ('wmax = {"primal": 0.0, "stationarity": 0.0, "cs": 0.0, "lam_max": 0.0}',
     'wmax = {"primal": 0.0, "stationarity": 0.0, "cs": 0.0, "kind": ""}'),
    ('"max_cs": wmax["cs"], "lam_max": wmax["lam_max"],', '"max_cs": wmax["cs"],'),
    ('diag.append({"lam": lam, "active": act})', 'diag.append({"active": act})'),
)
for old, new in pairs:
    if old not in t:
        raise SystemExit("MISSING: " + old)
    t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("refactor ok")
