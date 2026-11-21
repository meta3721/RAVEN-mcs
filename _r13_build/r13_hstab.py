import json, pathlib, numpy as np, math
from scipy import stats
H=json.loads(pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\S1P_STAGE_C_H.json").read_text())["H"]
for b,rec in H.items():
    hs=np.array(rec["H_by_seed"]); n=len(hs)
    print("### %s  H=%s"%(b,np.round(hs,6).tolist()))
    print("   mean=%.6f median=%.6f  n_pos=%d/%d"%(hs.mean(),np.median(hs),int((hs>0).sum()),n))
    for i in range(n):
        lo=np.delete(hs,i)
        print("   drop seed%d -> mean=%.6f  (delta=%+.6f)"%(rec["paired_seeds"][i],lo.mean(),lo.mean()-hs.mean()))
    # bootstrap on 4 seeds (drop the worst)
    lo4=np.delete(hs,int(np.argmin(hs)))
    rng=np.random.default_rng(20261007)
    boot=np.array([np.mean(rng.choice(lo4,size=len(lo4),replace=True)) for _ in range(10000)])
    l,h=np.percentile(boot,[2.5,97.5])
    sd=float(np.std(lo4,ddof=1))
    mde=(stats.t.ppf(0.975,3)+stats.t.ppf(0.80,3))*sd/math.sqrt(4)
    print("   excluding worst seed: mean=%.6f CI=[%.6f,%.6f] sd=%.6f MDE80=%.6f"%(lo4.mean(),l,h,sd,mde))
