"""P0 deeper: are the q^true = 0 cases structurally unusable, and what is B_min?"""
import json
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path('artifacts/e3_formal_runs_r1/eventtraces')
DESIGN = dict(q_min=0.05, d_max=10.0)
Q_REQ = 1.0 / DESIGN['d_max']


def load(ds, seeds):
    out = []
    for s in seeds:
        f = ROOT / ds / s / 'training_eventtrace' / 'events.parquet'
        if not f.is_file():
            continue
        df = pd.read_parquet(f)
        for _, r in df.iterrows():
            try:
                j = json.loads(r['opportunity_features']) if isinstance(r['opportunity_features'], str) \
                    else dict(r['opportunity_features'])
            except Exception:
                j = {}
            out.append(dict(
                seed=s, window=r['window_id'], client=r['client_id'],
                O=bool(r['O']) if not isinstance(r['O'], str) else len(json.loads(r['O'])) > 0,
                U=bool(r['U']) if not isinstance(r['U'], str) else r['U'],
                q_true=j.get('q_use_true'), p_true=j.get('p_obs_true'),
                pi_opp=j.get('pi_opp_true'), oracle_q=r.get('oracle_q'),
                oracle_p=r.get('oracle_p'),
                n_risk=len(json.loads(r['risk_set_unit_ids'])) if isinstance(r['risk_set_unit_ids'], str) else None,
                n_obs=len(json.loads(r['observed_unit_ids'])) if isinstance(r['observed_unit_ids'], str) else None,
            ))
    return pd.DataFrame(out)


for ds in ['sensorscope', 'uair']:
    t = load(ds, ['seed30%03d' % i for i in (1, 5, 10, 15, 20)])
    print('=== %s (5 seeds) ===' % ds.upper())
    print('  client-windows: %d' % len(t))

    zero = t[t['q_true'] == 0]
    pos = t[t['q_true'] > 0]
    print('  q_true == 0 : %d (%.1f%%)' % (len(zero), 100 * len(zero) / len(t)))
    print('  q_true  > 0 : %d (%.1f%%)' % (len(pos), 100 * len(pos) / len(t)))
    if len(pos):
        print('  among q_true>0: min=%.6g  p01=%.6g  p05=%.6g  median=%.6g' % (
            pos['q_true'].min(), pos['q_true'].quantile(0.01),
            pos['q_true'].quantile(0.05), pos['q_true'].median()))

    print()
    print('  --- do the q_true==0 rows actually ever deliver a usable update? ---')
    if len(zero):
        print('    observed (O=1) among q_true==0 : %d / %d' % (int(zero['O'].sum()), len(zero)))
        print('    usable  (U=True) among q_true==0: %d / %d' % (
            int(zero['U'].astype(str).str.lower().isin(['true', '1']).sum()), len(zero)))
    print('  --- among q_true>0 ---')
    if len(pos):
        print('    observed : %d / %d' % (int(pos['O'].sum()), len(pos)))
        print('    usable   : %d / %d' % (
            int(pos['U'].astype(str).str.lower().isin(['true', '1']).sum()), len(pos)))

    print()
    print('  --- design floor vs reality ---')
    print('    rows with 0 < q_true < q_min(0.05) : %d' % int(((pos['q_true'] > 0) & (pos['q_true'] < 0.05)).sum()))
    print('    rows with 0.05 <= q_true < 1/d_max(0.10) : %d' % int(((pos['q_true'] >= 0.05) & (pos['q_true'] < Q_REQ)).sum()))
    print('    => floor q_min=0.05 would be ACTIVE on %d of %d positive-q client-windows (%.1f%%)' % (
        int((pos['q_true'] < 0.05).sum()), len(pos),
        100 * (pos['q_true'] < 0.05).mean() if len(pos) else 0))

    print()
    print('  --- oracle_q (the simulator-side q used by SimOracle) ---')
    oq = pd.to_numeric(t['oracle_q'], errors='coerce').dropna()
    if len(oq):
        print('    n=%d  min=%.6g  p05=%.6g  median=%.6g  max=%.6g  zeros=%d' % (
            len(oq), oq.min(), oq.quantile(0.05), oq.median(), oq.max(), int((oq == 0).sum())))
    print()
