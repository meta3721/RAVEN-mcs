import json
from pathlib import Path
import numpy as np
R = Path("artifacts/e3_formal_runs_r1/runs")
for ds in ("sensorscope","uair"):
    a, b = {}, {}
    for seed in sorted((R/ds/"raven").glob("seed*")):
        a[seed.name] = json.loads((seed/"final_metrics.json").read_text())["RMSE_mu"]
    for seed in sorted((R/ds/"raven_simoracle").glob("seed*")):
        b[seed.name] = json.loads((seed/"final_metrics.json").read_text())["RMSE_mu"]
    seeds = sorted(set(a)&set(b))
    ra = np.array([a[s] for s in seeds]); rb = np.array([b[s] for s in seeds])
    d = ra - rb
    print(f"{ds}: n={len(seeds)}")
    print(f"   raven       mean = {ra.mean():.6f}")
    print(f"   simoracle   mean = {rb.mean():.6f}")
    print(f"   abs diff        = {d.mean():+.6f}")
    print(f"   rel vs simoracle= {100*d.mean()/rb.mean():+.4f} %")
    print(f"   rel vs raven    = {100*d.mean()/ra.mean():+.4f} %")
    print(f"   sd of diff      = {d.std(ddof=1):.6f}  ({100*d.std(ddof=1)/rb.mean():.4f} % of simoracle mean)")
