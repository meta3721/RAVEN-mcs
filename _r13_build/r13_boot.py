"""R1.3 adversarial audit - is the reported traffic bootstrap CI a property of the data
or an artifact of percentile-bootstrapping 5 numbers with one outlier?

Compares, on the SAME H_by_seed vectors:
  - the driver's percentile bootstrap (10,000, rng 20261007, numpy default_rng)
  - the exact Student-t 95% interval on the paired mean
  - a jackknife / leave-one-out interval
  - the exact sign test on the 4 non-outlier seeds
ASCII only.
"""
import json, math, pathlib
import numpy as np
from scipy import stats

H = json.loads(pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1"
                            r"\S1P_STAGE_C_H.json").read_text())["H"]


def boot_ci(hs, seed=20261007, draws=10000):
    rng = np.random.default_rng(seed)
    b = np.asarray([np.mean(rng.choice(hs, size=len(hs), replace=True)) for _ in range(draws)])
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


for b, rec in H.items():
    hs = np.asarray(rec["H_by_seed"], dtype=float)
    n = len(hs)
    mean = float(hs.mean())
    sd = float(hs.std(ddof=1))
    se = sd / math.sqrt(n)
    lo, hi = boot_ci(hs)
    tcrit = float(stats.t.ppf(0.975, n - 1))
    print("### %s   H=%s" % (b, np.round(hs, 6).tolist()))
    print("    mean=%.6f sd=%.6f se=%.6f" % (mean, sd, se))
    print("    driver percentile bootstrap 95%%: [%.6f, %.6f]" % (lo, hi))
    print("    exact Student-t 95%% on the mean: [%.6f, %.6f]  (tcrit=%.4f)"
          % (mean - tcrit * se, mean + tcrit * se, tcrit))
    # jackknife
    jm = np.asarray([np.delete(hs, i).mean() for i in range(n)])
    jse = math.sqrt((n - 1.0) / n * float(((jm - jm.mean()) ** 2).sum()))
    print("    jackknife mean=%.6f se=%.6f  t-approx 95%%: [%.6f, %.6f]"
          % (jm.mean(), jse, jm.mean() - tcrit * jse, jm.mean() + tcrit * jse))
    print("    Tukey outlier check: q1=%.6f q3=%.6f iqr=%.6f  fence_lo=%.6f  values below fence: %s"
          % (np.percentile(hs, 25), np.percentile(hs, 75),
             np.percentile(hs, 75) - np.percentile(hs, 25),
             np.percentile(hs, 25) - 1.5 * (np.percentile(hs, 75) - np.percentile(hs, 25)),
             [float(x) for x in hs if x < np.percentile(hs, 25) - 1.5 * (np.percentile(hs, 75) - np.percentile(hs, 25))]))
    # exact sign test: how many seeds have H > 1% ?
    for thr in (0.0, 0.01):
        k = int((hs > thr).sum())
        p = float(sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)
        print("    exact one-sided sign test  H > %.2f : k=%d/%d  p=%.4f" % (thr, k, n, p))
    # what the driver's GO-H rule would say under the exact t interval
    print("    driver rule check: mean>=1%%=%s ; exact-t LCB>0.5%%=%s"
          % (mean >= 0.01, (mean - tcrit * se) > 0.005))
    print()
