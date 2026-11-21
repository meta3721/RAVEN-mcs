import sys, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_v51_oracle as O
for K in range(1, 8):
    from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
    ab = float(alpha_bar(alpha_max=0.5, n_active=K)); eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = np.linspace(0.1, 1.0, K)
    a, kind, mult = O.project_Cr(v, ab, eb)
    print("K=%d ab=%.3f eb=%.3f tgt=%.4f kind=%-22s feas=%.2e" % (K, ab, eb, 1.0/eb, kind, O.feasibility(a, ab, 1.0/eb)))
