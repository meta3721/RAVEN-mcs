import sys, math, numpy as np
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import w1_v51_oracle as O
v = np.array([0.33655152, 0.50672467, 0.08248492, 0.07423889])
hi, target, K = 0.5, 1.0/3.0, 4
order = np.argsort(-v, kind="stable")
print("order", order, "v", v)
for kc in range(0, 3):
    cap = order[:kc]; rest = order[kc:]; cc = kc*hi
    for nz in range(0, K-kc):
        nf = K-kc-nz
        if nf < 1: continue
        f = rest[:nf]; z = rest[nf:]
        sf = float(v[f].sum()); qf = float((v[f]**2).sum())
        aa = 1.0 + qf/nf - (sf/nf)**2
        bb = 2.0*(cc-1.0)/nf
        cq = (kc*hi*hi - target)/nf
        disc = bb*bb - 4*aa*cq
        print("kc=%d nz=%d nf=%d f=%s disc=%.6e" % (kc,nz,nf,f,disc))
        if disc < 0: continue
        r = math.sqrt(disc)
        for lp in ((-bb+r)/(2*aa), (-bb-r)/(2*aa)):
            tp = (1.0-cc-lp*sf)/nf
            x = np.empty(K); x[f]=tp+lp*v[f]; x[cap]=hi; x[z]=0.0
            print("   lp=%.8f tp=%.8f x=%s feas=%.2e obj=%.10f" % (lp,tp,np.round(x,8), O.feasibility(x,hi,target), float(((x-v)**2).sum())))
print("trained= [0.31867819 0.45370971 0.11707764 0.11053445] obj=%.10f feas=%.2e" % (
    float(((np.array([0.31867819,0.45370971,0.11707764,0.11053445])-v)**2).sum()),
    O.feasibility(np.array([0.31867819,0.45370971,0.11707764,0.11053445]), hi, target)))
print("oracle:", O.project_Cr(v, hi, 3.0)[1], np.round(O.project_Cr(v, hi, 3.0)[0],8))
