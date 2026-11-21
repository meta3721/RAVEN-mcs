"""Is D_aligned = Delta_mu - Delta_rho informative beyond Delta_rho itself?"""
import numpy as np
import pandas as pd

d = pd.read_csv('artifacts/e2_traffic_formal_results_analysis_r1/COMPLETE_ALIGNED_DOD.csv')
mu = pd.to_numeric(d['Delta_mu_aligned'], errors='coerce')
rho = pd.to_numeric(d['Delta_rho_aligned'], errors='coerce')
D = pd.to_numeric(d['D_aligned'], errors='coerce')

print('n =', len(d), ' methods:', sorted(d.method.unique()))
print()
print('%-22s %10s %10s %10s %10s' % ('quantity', 'mean', 'sd', 'min', 'max'))
for nm, v in (('Delta_mu', mu), ('Delta_rho', rho), ('D_aligned', D)):
    print('%-22s %10.5f %10.5f %10.5f %10.5f' % (nm, v.mean(), v.std(ddof=1), v.min(), v.max()))
print()
print('scale ratio  sd(Delta_rho)/sd(Delta_mu) = %.1f' % (rho.std() / mu.std()))
print('mean ratio   |mean rho|/|mean mu|        = %.1f' % (abs(rho.mean()) / abs(mu.mean())))
print()
print('sign(D) == -sign(Delta_rho): %d / %d  (%.1f%%)'
      % (int((np.sign(D) == -np.sign(rho)).sum()), len(D),
         100 * (np.sign(D) == -np.sign(rho)).mean()))
print('corr(D, Delta_rho) = %+.4f   corr(D, Delta_mu) = %+.4f'
      % (np.corrcoef(D, rho)[0, 1], np.corrcoef(D, mu)[0, 1]))
print()
print('sd(D)/sd(Delta_rho) = %.3f  -> D is essentially a rescaled Delta_rho'
      % (D.std() / rho.std()))
print()
print('--- per method: is mean Delta_mu distinguishable from 0? ---')
from scipy import stats
print('%-22s %12s %10s %10s %12s' % ('method', 'mean Dmu', 'sd Dmu', 'Wilcox p', 'mean D'))
for m, g in d.groupby('method'):
    a = pd.to_numeric(g['Delta_mu_aligned'], errors='coerce').to_numpy()
    dd = pd.to_numeric(g['D_aligned'], errors='coerce').to_numpy()
    try:
        p = stats.wilcoxon(a).pvalue
    except Exception:
        p = float('nan')
    print('%-22s %12.6f %10.6f %10.3g %12.5f' % (m, a.mean(), a.std(ddof=1), p, dd.mean()))
