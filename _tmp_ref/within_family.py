import csv, pathlib, numpy as np
from scipy import stats
O = pathlib.Path("results_active_set_repair/round_v1")
cells = [r for r in csv.DictReader(open(O/"E2_UAIR_CELLS.csv", newline="", encoding="utf-8")) if r["status"]=="OK"]
def series(m, k): return {int(r["seed"]): float(r[k]) for r in cells if r["method"]==m}
TEST=set(range(30011,30021)); ALL=set(range(30001,30021))
print("=== within-Design-family: RAVEN-Design minus TwoStage-Hajek (paired relative) ===")
for k in ("RMSE_mu_std","WorstGroupRMSE_std","Delta_group","Delta_c_s"):
    a, b = series("raven",k), series("twostage_hajek",k)
    for lab, sel in (("TEST",TEST),("ALL20",ALL)):
        ks=[s for s in a if s in b and s in sel]
        rel=np.array([(a[s]-b[s])/b[s] for s in ks]); n=len(rel)
        t=stats.t.ppf(0.975,n-1); se=rel.std(ddof=1)/np.sqrt(n)
        print(f"  {k:<22} {lab:<6} n={n} rel={rel.mean()*100:+.3f}% CI=[{(rel.mean()-t*se)*100:+.3f},{(rel.mean()+t*se)*100:+.3f}] wins={int((np.array([a[s] for s in ks])<np.array([b[s] for s in ks])).sum())}/{n} p={stats.ttest_rel([a[s] for s in ks],[b[s] for s in ks]).pvalue:.3g}")
print()
print("=== cross-family for reference: RAVEN-NoDesign minus TwoStage-Hajek on WorstGroupRMSE ===")
a,b = series("raven_wo_design","WorstGroupRMSE_std"), series("twostage_hajek","WorstGroupRMSE_std")
for lab,sel in (("TEST",TEST),("ALL20",ALL)):
    ks=[s for s in a if s in b and s in sel]
    rel=np.array([(a[s]-b[s])/b[s] for s in ks])
    print(f"  {lab}: ratio-of-means {(np.mean([a[s] for s in ks])/np.mean([b[s] for s in ks])-1)*100:+.3f}%  paired {rel.mean()*100:+.3f}%")
