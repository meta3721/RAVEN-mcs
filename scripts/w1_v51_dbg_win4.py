import sys, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_replay as W, w1_v51_oracle as O
from scipy.optimize import minimize
pi = {d: W.pi_tar_for(d) for d in W.DS}
ri = O.run_inputs("sensorscope", "proj_beta", 30001, pi["sensorscope"])
case = ri["case"]
a_tr = O.trained_alpha(case, ri["act"], "proj_beta")
a_or, diag = O.oracle_proj_beta(ri["betas"], case)
off = 0
for j in range(case["n"]):
    K = len(case["clients"][j])
    d = float(np.max(np.abs(a_tr[off:off+K] - a_or[off:off+K])))
    if d > 0.1:
        ab = case["a_bar"][j]; eb = case["e_bar"][j]; tgt = 1.0/eb
        b = np.asarray(ri["betas"][j], dtype=float); b = b/b.sum()
        xT = a_tr[off:off+K]; xO = a_or[off:off+K]
        cons = [{"type":"eq","fun":lambda x: float(np.sum(x))-1.0},
                {"type":"ineq","fun":lambda x: tgt - float(x@x)}]
        tot = 0.0
        for i in range(K):
            for lo in (0.0, ab):
                pass
        # distance of each to the feasible set: min over C_r of ||x - p||
        def dist(p):
            r = minimize(lambda x: float(((x-p)**2).sum()), np.full(K,1.0/K), method="SLSQP",
                         bounds=[(0.0,ab)]*K, constraints=cons, options={"maxiter":800,"ftol":1e-18})
            return float(np.sqrt(max(0.0, ((r.x-p)**2).sum()))), r.x
        dT, pT = dist(xT); dO, pO = dist(xO)
        print("win=%d K=%d kind=%s ab=%.3f tgt=%.4f" % (j, K, diag[j]["active"], ab, tgt))
        print("  trained=%s  dist_to_Cr=%.3e" % (np.round(xT,8), dT))
        print("  oracle =%s  dist_to_Cr=%.3e" % (np.round(xO,8), dO))
        print("  beta/  =%s" % np.round(b,8))
        print("  obj(trained)=%.10f obj(oracle)=%.10f obj(proj_of_trained)=%.10f" % (
            float(((xT-b)**2).sum()), float(((xO-b)**2).sum()), float(((pT-b)**2).sum())))
        break
    off += K
