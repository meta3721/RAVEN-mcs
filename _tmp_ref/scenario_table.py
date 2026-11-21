"""Can the six risk-semantic scenarios be tabulated from existing results?

Also computes the generalised difference-of-differences
    D(S) = Delta_mu(S) - Delta_rho(S),   Delta(S) = metric(S) - metric(balanced)
paired by seed, for every scenario S, which is the paper's D_aligned generalised
to the whole scenario family.
"""
import numpy as np
import pandas as pd

R = 'artifacts/e2_traffic_formal_runs_r1/'
res = pd.read_csv(R + 'formal_results.csv')
grp = pd.read_csv(R + 'formal_group_metrics.csv')
sta = pd.read_csv(R + 'formal_statistics.csv')

SCEN = ['balanced', 'opportunity_only', 'observation_only', 'usable_only',
        'complete_aligned', 'complete_counteracting']
METHODS = sorted(res['method'].unique())

print('=== completeness ===')
print('rows=%d  cells(scenario x method x seed)=%d  expected=%d'
      % (len(res), res.groupby(['scenario', 'method', 'seed']).ngroups,
         6 * 5 * 20))
print('status:', res['status'].value_counts().to_dict())
print('duplicate (scenario,method,seed):',
      int(res.duplicated(['scenario', 'method', 'seed']).sum()))
print()

print('=== per-scenario, per-method means (RMSE_mu / RMSE_rho / Gap_mis) ===')
piv_mu = res.pivot_table(index=['method', 'seed'], columns='scenario', values='RMSE_mu')
piv_rho = res.pivot_table(index=['method', 'seed'], columns='scenario', values='RMSE_rho')
piv_gap = res.pivot_table(index=['method', 'seed'], columns='scenario', values='Gap_mis')

print('%-26s %-24s %10s %10s %10s' % ('scenario', 'method', 'RMSE_mu', 'RMSE_rho', 'Gap'))
for s in SCEN:
    for m in METHODS:
        sub = res[(res.scenario == s) & (res.method == m)]
        print('%-26s %-24s %10.4f %10.4f %10.4f'
              % (s, m, sub.RMSE_mu.mean(), sub.RMSE_rho.mean(), sub.Gap_mis.mean()))
    print()

print('=== generalised D(S) = Delta_mu(S) - Delta_rho(S), paired by seed ===')
print('%-26s %12s %12s %12s' % ('scenario', 'mean D', 'sd D', 'neg seeds/100'))
for s in SCEN:
    if s == 'balanced':
        continue
    dmu, drho, dd = [], [], []
    for m in METHODS:
        a = piv_mu.loc[m, s].to_numpy() - piv_mu.loc[m, 'balanced'].to_numpy()
        b = piv_rho.loc[m, s].to_numpy() - piv_rho.loc[m, 'balanced'].to_numpy()
        dmu.append(a); drho.append(b); dd.append(a - b)
    dmu = np.concatenate(dmu); drho = np.concatenate(drho); dd = np.concatenate(dd)
    print('%-26s %12.5f %12.5f %12d'
          % (s, dd.mean(), dd.std(ddof=1), int((dd < 0).sum())))
print()
print('(paper reports D_aligned = -0.02115 over 5 methods x 20 seeds = 100 values)')
print()

print('=== WorstGroupRMSE per scenario (max over the four groups) ===')
w = grp.groupby(['scenario', 'method', 'seed'])['RMSE'].max().reset_index()
for s in SCEN:
    v = w[w.scenario == s]['RMSE']
    print('%-26s mean=%.4f  sd=%.4f' % (s, v.mean(), v.std(ddof=1)))
print()

print('=== what formal_statistics.csv already aggregates ===')
print('metrics:', sorted(sta['metric'].unique()))
print('cells:', sta.groupby(['scenario', 'method']).ngroups, '(= 6 x 5)')
