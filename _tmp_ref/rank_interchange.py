"""Do the two risk views rank the five methods the same way on complete_aligned?
This is the decision-relevant reading of 'non-interchangeable'."""
import numpy as np
import pandas as pd
from scipy import stats

d = pd.read_csv('paper_ready_r1/01_core_data/e2/E2_RISK_NONINTERCHANGEABILITY_MASTER.csv')
d = d[d.scenario == 'complete_aligned']
g = d.groupby('method_display')[['RMSE_mu', 'RMSE_rho']].agg(['mean', 'std'])

print('%-24s %14s %14s %10s' % ('method', 'RMSE_mu', 'RMSE_rho', 'rho-mu'))
tab = {}
for m, row in g.iterrows():
    mm, ms = row[('RMSE_mu', 'mean')], row[('RMSE_mu', 'std')]
    rm, rs = row[('RMSE_rho', 'mean')], row[('RMSE_rho', 'std')]
    tab[m] = (mm, rm)
    print('%-24s %7.4f+-%.4f %7.4f+-%.4f %+10.4f' % (m, mm, ms, rm, rs, rm - mm))

order_mu = sorted(tab, key=lambda k: tab[k][0])
order_rho = sorted(tab, key=lambda k: tab[k][1])
print()
print('rank by RMSE_mu  :', ' < '.join(order_mu))
print('rank by RMSE_rho :', ' < '.join(order_rho))
print('identical ranking:', order_mu == order_rho)

r = [order_mu.index(k) for k in order_rho]
print('Spearman rank corr = %+.3f' % stats.spearmanr(range(len(r)), r).statistic)

print()
print('--- paired per-seed gap RMSE_rho - RMSE_mu ---')
for m, sub in d.groupby('method_display'):
    diff = sub['RMSE_rho'] - sub['RMSE_mu']
    pos = int((diff > 0).sum())
    print('%-24s mean=%+.4f  sd=%.4f  rho>mu in %2d/%d seeds  wilcox p=%.3g'
          % (m, diff.mean(), diff.std(ddof=1), pos, len(diff),
             stats.wilcoxon(diff).pvalue))
