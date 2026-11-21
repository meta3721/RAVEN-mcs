import math, numpy as np
v = np.array([0.544024, 0.535509, 0.420467]); hi=0.5; target=1.0/3.0; K=3
order = np.argsort(-v, kind="stable")
print("order", order, "v", v)
for kc in range(0, K):
    cap = order[:kc]; rest = order[kc:]
    for nz in range(0, K-kc):
        nf = K-kc-nz
        if nf < 1: continue
        f = rest[:nf]; z = rest[nf:]
        sf = float(v[f].sum()); qf = float((v[f]**2).sum())
        b = 2.0*(hi*kc - 1.0)/nf
        c = (kc*hi*hi - target)/nf
        aa = 1.0 + qf/nf - (sf/nf)**2
        disc = b*b - 4*aa*c
        print("kc=%d nz=%d nf=%d f=%s z=%s  a=%.6f b=%.6f c=%.6f disc=%.6e" % (kc,nz,nf,f,z,aa,b,c,disc))
        if disc < 0: continue
        r = math.sqrt(disc)
        for lp in ((-b+r)/(2*aa), (-b-r)/(2*aa)):
            if lp < -1e-12: continue
            tp = (1.0 - kc*hi - lp*sf)/nf
            x = np.empty(K); x[f] = tp + lp*v[f]; x[cap] = hi; x[z] = 0.0
            print("     lp=%.8f tp=%.8f sum=%.12f n2=%.12f x=%s  ztest=%s captest=%s" % (
                lp, tp, x.sum(), float(x@x), np.round(x,8),
                bool(z.size and float(np.max(v[z])) > tp+1e-12),
                bool(cap.size and float(np.min(v[cap])) < tp+2*lp*hi-1e-12)))
