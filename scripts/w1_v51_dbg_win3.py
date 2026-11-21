import sys, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_replay as W, w1_v51_oracle as O
from scipy.optimize import minimize
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
pi = {d: W.pi_tar_for(d) for d in W.DS}
ri = O.run_inputs("sensorscope", "proj_beta", 30001, pi["sensorscope"])
case = ri["case"]
a_tr = O.trained_alpha(case, ri["act"], "proj_beta")
a_or, diag = O.oracle_proj_beta(ri["betas"], case)
off = 0
for j in range(case["n"]):
    K = len(case["clients"][j])
    d = float(np.max(np.abs(a_tr[off:off+K] - a_or[off:off+K])))
    if d > 1e-6:
        ab = case["a_bar"][j]; eb = case["e_bar"][j]; tgt = 1.0/eb
        b = np.asarray(ri["betas"][j], dtype=float); b = b/b.sum()
        print("win=%d K=%d kind=%s d=%.6f ab=%.3f eb=%.3f" % (j, K, diag[j]["active"], d, ab, eb))
        print("  trained=%s" % np.round(a_tr[off:off+K], 8))
        print("  oracle =%s" % np.round(a_or[off:off+K], 8))
        print("  beta/  =%s" % np.round(b, 8))
        cons = [{"type":"eq","fun":lambda x: float(np.sum(x))-1.0},
                {"type":"ineq","fun":lambda x: tgt - float(x@x)}]
        best=None
        for s in (np.full(K,1.0/K), np.clip(b,0,ab), a_tr[off:off+K], a_or[off:off+K]):
            r = minimize(lambda x: float(((x-b)**2).sum()), s, method="SLSQP",
                         bounds=[(0.0,ab)]*K, constraints=cons, options={"maxiter":800,"ftol":1e-18})
            f = O.feasibility(r.x, ab, tgt)
            if f <= 1e-12:
                o = float(((r.x-b)**2).sum())
                if best is None or o < best[0]: best=(o, r.x.copy())
        print("  SLSQP  =%s obj=%.10f" % (np.round(best[1],8), best[0]))
        print("  obj trained=%.10f oracle=%.10f" % (float(((a_tr[off:off+K]-b)**2).sum()), float(((a_or[off:off+K]-b)**2).sum())))
        break
    off += K
