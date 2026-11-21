import sys, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_v51_dbg_qp3 as S
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
sys.path.insert(0, "scripts")
import w1_v51_oracle as O
rng = np.random.default_rng(99)
bad = n = 0
worstobj = -1e9
for trial in range(120):
    K = int(rng.integers(2, 14))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K)); eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05,0.3,1.0,4.0]); v = v/v.sum()*float(rng.choice([1.0,1.5,3.0]))
    if v.sum() < 1.0: continue
    x, kind = S.project_Cr(v, ab, eb)
    xc, status, tier = O.cvxpy_proj(v, ab, eb, K)
    xp = O.project_back(xc, ab, eb)
    gap = float(((x-v)**2).sum()) - float(((xp-v)**2).sum())
    n += 1
    worstobj = max(worstobj, gap)
    if gap > 1e-11:
        bad += 1
        if bad < 5: print("OBJ BAD K=%d kind=%s gap=%.3e status=%s feas_cvx=%.2e" % (K, kind, gap, status, O.feasibility(xc, ab, eb)))
print("obj failures %d/%d worst gap %.3e" % (bad, n, worstobj))
