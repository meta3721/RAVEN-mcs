import sys, math, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import importlib, w1_v51_dbg_as4 as S
importlib.reload(S)
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
rng = np.random.default_rng(2026)
fails = 0
for trial in range(200):
    K = int(rng.integers(2, 14))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K)); eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0]); v = v / v.sum() * float(rng.choice([1.0,1.5,3.0]))
    a, act = S.project_Cr(v, ab, eb)
    if a is None:
        fails += 1
        if fails == 1:
            print("FAIL trial=%d K=%d ab=%.4f eb=%.4f target=%.6f" % (trial,K,ab,eb,1.0/eb))
            print("  v=", v)
            x0 = S.capped_simplex(v, ab)
            print("  x0=", x0, "n2=", float(x0@x0))
            order = np.argsort(-v, kind="stable")
            for kc in (0,1):
                cap = order[:kc]; rest = order[kc:]; bb = 1.0-kc*ab
                for nz in range(0, K-kc+1):
                    nf = K-kc-nz
                    if nf < 1: continue
                    f = rest[:nf]; z = rest[nf:]
                    disc = bb*bb + 4.0*nf*((1.0/eb) - kc*ab*ab)
                    print("   kc=%d nz=%d nf=%d disc=%.6e" % (kc,nz,nf,disc))
                    if disc < 0: continue
                    root = math.sqrt(disc)
                    for lam in ((-bb+root)/(2*nf), (-bb-root)/(2*nf)):
                        if lam < -1e-12: continue
                        tau = (1.0-lam*float(v[f].sum()))/nf
                        x = np.empty(K); x[f]=tau+lam*v[f]; x[cap]=ab; x[z]=0.0
                        print("      lam=%.8f tau=%.8f sum=%.12f n2=%.12f x=%s" % (lam, tau, x.sum(), float(x@x), np.round(x,8)))
print("fails:", fails)
