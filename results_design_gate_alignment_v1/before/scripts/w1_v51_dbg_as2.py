import sys, math, numpy as np
sys.path.insert(0, "scripts")
import w1_v51_oracle as O
v = np.array([0.44721023, 0.32726116, 0.22552860]); hi, target = 0.5, 1.0/3.0
K = int(v.size); order = np.argsort(-v, kind="stable"); best = None
print("early?", K == 1, hi*K <= 1.0+1e-15, target >= float(K))
for kc in (0,1):
    cap_idx = order[:kc]; rest = order[kc:]
    for nz in range(0, K-kc+1):
        nf = K-kc-nz
        if nf < 1: continue
        free_idx = rest[:nf]; zero_idx = rest[nf:]
        mf = float(v[free_idx].mean()); rhs = target - kc*hi*hi
        if rhs <= 0: continue
        disc = rhs/float(nf) - (1.0-kc*hi)**2/float(nf*nf)
        if disc < -1e-18: continue
        root = math.sqrt(max(0.0, disc))
        for sgn in (1.0,-1.0):
            lam_p = sgn*root - (1.0-kc*hi)/float(nf)
            if lam_p < -1e-12: continue
            tau_p = mf - (1.0-kc*hi)*(1.0+2.0*lam_p)/float(nf)
            x = np.empty(K); x[free_idx] = tau_p + lam_p*v[free_idx]; x[cap_idx] = hi; x[zero_idx] = 0.0
            c1 = bool(zero_idx.size and float(np.max(v[zero_idx])) > tau_p + 1e-12)
            c2 = bool(cap_idx.size and float(np.min(v[cap_idx])) < tau_p + 2.0*lam_p*hi - 1e-12)
            c3 = bool(free_idx.size and (np.any(x[free_idx] < -1e-12) or np.any(x[free_idx] > hi+1e-12)))
            c4 = abs(float(x.sum())-1.0) > 1e-14
            c5 = float(x@x) > target + 1e-12
            print("kc=%d nz=%d sgn=%+.0f lam=%.3g tau=%.6g fails: z=%s cap=%s free=%s sum=%s n2=%s x=%s" %
                  (kc, nz, sgn, lam_p, tau_p, c1, c2, c3, c4, c5, np.round(x,8)))
            if not (c1 or c2 or c3 or c4 or c5):
                score = float(((x-v)**2).sum())
                if best is None or score < best[0]: best = (score, x, tau_p)
print("best:", None if best is None else (best[0], np.round(best[1],8), best[2]))
