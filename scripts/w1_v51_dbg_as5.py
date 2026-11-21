import sys, math, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_v51_dbg_as4 as S
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
rng = np.random.default_rng(2026)
for trial in range(200):
    K = int(rng.integers(2, 14))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K)); eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0]); v = v / v.sum() * float(rng.choice([1.0,1.5,3.0]))
    a, act = S.project_Cr(v, ab, eb)
    if a is None:
        print("FAIL trial=%d K=%d ab=%.4f eb=%.4f target=%.6f" % (trial,K,ab,eb,1.0/eb))
        print("  v=", v, " x0=", S.capped_simplex(v, ab), " n2=", float(S.capped_simplex(v,ab)@S.capped_simplex(v,ab)))
        order = np.argsort(-v, kind="stable"); best=None
        for kc in (0,1):
            cap = order[:kc]; rest = order[kc:]; rhs = 1.0/eb - kc*ab*ab
            if rhs <= 0: continue
            for nz in range(0, K-kc+1):
                nf = K-kc-nz
                if nf < 1: continue
                f = rest[:nf]; z = rest[nf:]
                mf = float(v[f].sum())/nf; aa = (1.0-kc*ab)/nf
                disc = rhs/nf - aa*aa
                root = math.sqrt(max(0.0,disc))
                for lam in (aa+root, aa-root):
                    if lam < -1e-12: continue
                    tau = mf - (1.0-kc*ab)*(1.0+2.0*lam)/nf
                    x = np.empty(K); x[f] = tau + lam*v[f]; x[cap]=ab; x[z]=0.0
                    c1 = z.size and float(np.max(v[z])) > tau+1e-12
                    c2 = cap.size and float(np.min(v[cap])) < tau+2.0*lam*ab-1e-12
                    c3 = bool(np.any(x[f] < -1e-12) or np.any(x[f] > ab+1e-12))
                    c4 = abs(float(x.sum())-1.0) > 1e-13
                    c5 = float(x@x) > 1.0/eb + 1e-10
                    print("   kc=%d nz=%d nf=%d disc=%.3e lam=%.6g tau=%.6g fails z=%s cap=%s free=%s sum=%.2e n2=%.6f/%s" %
                          (kc,nz,nf,disc,lam,tau,bool(c1),bool(c2),c3,float(x.sum())-1.0,float(x@x),bool(c5)))
        break
