"""P0: A5 sub-condition audit on the frozen E3 formal traces (no retraining)."""
import json
import statistics as st
from pathlib import Path

import pandas as pd

ROOT = Path('artifacts/e3_formal_runs_r1/eventtraces')
DATASETS = ['sensorscope', 'uair']
SEEDS = ['seed30%03d' % i for i in range(1, 21)]

DESIGN = dict(p_min=0.05, q_min=0.05, a_max=20.0, d_max=10.0)
Q_REQ = 1.0 / DESIGN['d_max']          # A5's implied floor on min q^true


def harvest(ds):
    rows = []
    for s in SEEDS:
        f = ROOT / ds / s / 'training_eventtrace' / 'events.parquet'
        if not f.is_file():
            continue
        df = pd.read_parquet(f, columns=['window_id', 'client_id', 'opportunity_features',
                                         'oracle_p', 'oracle_q', 'O', 'U'])
        for of, op, oq in zip(df['opportunity_features'], df['oracle_p'], df['oracle_q']):
            try:
                j = json.loads(of) if isinstance(of, str) else dict(of)
            except Exception:
                continue
            rows.append(dict(
                seed=s,
                pi_opp_true=j.get('pi_opp_true'),
                p_obs_true=j.get('p_obs_true'),
                q_use_true=j.get('q_use_true'),
                q_mc_se=j.get('q_mc_se'),
                oracle_p=op, oracle_q=oq,
            ))
    return pd.DataFrame(rows)


def fmt(x):
    return 'n/a' if x is None or (isinstance(x, float) and x != x) else '%.6g' % x


summary = {}
for ds in DATASETS:
    t = harvest(ds)
    if t.empty:
        print('=== %s : no data ===' % ds)
        continue
    opp = t['pi_opp_true'].dropna()
    pob = t['p_obs_true'].dropna()
    qus = t['q_use_true'].dropna()
    summary[ds] = t
    print('=== %s ===' % ds.upper())
    print('  client-window records: %d   (seeds %d)' % (len(t), t['seed'].nunique()))
    print()
    print('  %-14s %10s %10s %10s %10s' % ('quantity', 'min', 'p05', 'median', 'max'))
    for name, col in [('pi_opp_true', opp), ('p_obs_true', pob), ('q_use_true', qus)]:
        if len(col) == 0:
            print('  %-14s %10s' % (name, 'ABSENT'))
            continue
        print('  %-14s %10s %10s %10s %10s' % (
            name, fmt(col.min()), fmt(col.quantile(0.05)),
            fmt(col.median()), fmt(col.max())))
    print()
    # A5 sub-conditions
    print('  --- A5 sub-condition readings ---')
    print('  P1 min pi_opp   = %s   (need > 0)' % fmt(opp.min() if len(opp) else None))
    print('  P2 min p_obs    = %s   (need >= p_min = %.2f)' % (
        fmt(pob.min() if len(pob) else None), DESIGN['p_min']))
    print('  P3 min q_use    = %s   (need >= 1/d_max = %.2f)' % (
        fmt(qus.min() if len(qus) else None), Q_REQ))
    if len(qus):
        print('     q_use < 0.10 count : %d / %d  (%.2f%%)' % (
            int((qus < Q_REQ).sum()), len(qus), 100.0 * (qus < Q_REQ).mean()))
        print('     q_use < q_min(0.05) : %d' % int((qus < DESIGN['q_min']).sum()))
    if len(pob):
        print('     p_obs < p_min(0.05) : %d' % int((pob < DESIGN['p_min']).sum()))
    print()

print('=== cross-dataset verdict inputs (a_max = 20) ===')
print('  A5 also needs 1/p_min^true <= a_max  =>  min p^true >= %.2f' % (1.0 / DESIGN['a_max']))
print('  A5 also needs 1/q_min^true <= d_max  =>  min q^true >= %.2f' % Q_REQ)

# save the harvested table for later steps
out = Path('_tmp_ref/a5_p0_harvest.csv')
pd.concat([v.assign(dataset=k) for k, v in summary.items()]).to_csv(out, index=False)
print()
print('harvested table written to', out)
