import sys, numpy as np
sys.path.insert(0, "scripts")
import w1_v51_oracle as O
v = np.array([0.44721023, 0.32726116, 0.22552860])
hi, target = 0.5, 1.0/3.0
print("proj_ball_simplex:", O._project_ball_simplex(v, hi, target))
print("project_Cr      :", O.project_Cr(v, hi, 3.0))
# manual
import math
order = np.argsort(-v)
K = 3
for kc in (0,1):
    cap = order[:kc]; rest = order[kc:]
    for nz in range(0, K-kc+1):
        nf = K-kc-nz
        if nf < 1: continue
        f = rest[:nf]; z = rest[nf:]
        mf = float(v[f].mean()); rhs = target - kc*hi*hi
        if rhs <= 0: continue
        disc = rhs/nf - (1-kc*hi)**2/nf**2
        print("  kc=%d nz=%d nf=%d mf=%.8f rhs=%.8f disc=%.3e" % (kc, nz, nf, mf, rhs, disc))
        if disc < -1e-18: continue
        root = math.sqrt(max(0.0, disc))
        for sgn in (1.0,-1.0):
            lam_p = sgn*root - (1-kc*hi)/nf
            if lam_p < -1e-12: continue
            tau_p = mf - (1-kc*hi)*(1+2*lam_p)/nf
            x = np.empty(K); x[f] = tau_p + lam_p*v[f]; x[cap] = hi; x[z] = 0.0
            print("     sgn=%+g lam=%.6g tau=%.6g x=%s sum=%.10f n2=%.10f" %
                  (sgn, lam_p, tau_p, np.round(x,8), x.sum(), float(x@x)))
