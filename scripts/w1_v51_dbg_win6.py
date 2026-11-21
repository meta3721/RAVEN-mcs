import sys, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_replay as W, w1_v51_oracle as O
pi = {d: W.pi_tar_for(d) for d in W.DS}
ri = O.run_inputs("sensorscope", "proj_beta", 30001, pi["sensorscope"])
case = ri["case"]
off = 0
for j in range(case["n"]):
    K = len(case["clients"][j])
    if j in (4, 42, 85):
        ab = case["a_bar"][j]; eb = case["e_bar"][j]; tgt = 1.0/eb
        b = np.asarray(ri["betas"][j], dtype=float); b = b/b.sum()
        x0 = O._capped_simplex(b, ab)
        uni = np.full(K, 1.0/K)
        a, kind, mult = O.project_Cr(b, ab, eb)
        print("win=%d K=%d ab=%.3f tgt=%.6f" % (j, K, ab, tgt))
        print("  beta/ =%s" % np.round(b, 8))
        print("  x0    =%s n2=%.10f feas=%.2e obj=%.10f" % (np.round(x0,8), float(x0@x0), O.feasibility(x0,ab,tgt), float(((x0-b)**2).sum())))
        print("  uni   feas=%.2e obj=%.10f" % (O.feasibility(uni,ab,tgt), float(((uni-b)**2).sum())))
        print("  proj  =%s kind=%s obj=%.10f" % (np.round(a,8), kind, float(((a-b)**2).sum())))
        print("  n2(proj)=%.12f  target=%.12f" % (float(a@a), tgt))
    off += K
