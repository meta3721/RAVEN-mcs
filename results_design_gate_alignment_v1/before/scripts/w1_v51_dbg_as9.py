import sys, math, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_v51_dbg_as8 as S
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
rng = np.random.default_rng(2026)
shown = 0
for trial in range(600):
    K = int(rng.integers(2, 16))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K)); eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05,0.3,1.0,4.0]); v = v/v.sum()*float(rng.choice([0.8,1.0,1.5,3.0]))
    a, act = S.project_Cr(v, ab, eb)
    if act != "fallback": continue
    shown += 1
    if shown > 2: break
    target = 1.0/eb
    print("trial=%d K=%d ab=%.4f eb=%.4f target=%.6f sum(v)=%.6f" % (trial,K,ab,eb,target,v.sum()))
    print("  v=", np.round(v,6))
    x0 = S.capped_simplex(v, ab); print("  x0=", np.round(x0,6), "n2=%.6f" % float(x0@x0))
    cands = S._candidates(v, ab, target)
    print("  ncand=%d" % len(cands))
    for x in cands[:8]:
        print("    x=%s feas=%.2e" % (np.round(x,6), S._feas(x, ab, target)))
    xd = S._dykstra(v, ab, target)
    print("  dykstra:", None if xd is None else (np.round(xd,6), S._feas(xd, ab, target)))
