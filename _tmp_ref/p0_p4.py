"""P0: complete P4 (Hajek denominator) and probe P6 (shared active set)."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path('artifacts/e3_formal_runs_r1/eventtraces')
DESIGN = dict(q_min=0.05, p_min=0.05, d_max=10.0)

print('=== P6 probe: what does p2_invocation_states.json contain? ===')
cands = list(Path('.').rglob('p2_invocation_states.json'))
print('  files found:', len(cands))
if cands:
    p = cands[0]
    print('  sample:', p)
    j = json.loads(p.read_text(encoding='utf-8', errors='replace'))
    if isinstance(j, dict):
        print('  top-level keys:', list(j.keys())[:15])
        for k in list(j.keys())[:4]:
            v = j[k]
            print('    %-24s %s' % (k, (str(v)[:90])))
    elif isinstance(j, list):
        print('  list len =', len(j), ' first item keys:', list(j[0].keys())[:15] if j else None)

print()
print('=== P4: recompute the local corrected mass m and Hajek denominator ===')
print('    A5 needs min_k 1^T b > 0, with b = m * d, d = min(d_max, 1/max(q_hat, q_min))')
print('    (q_hat is not in the trace; using q_true as the reference value)')
print()

for ds in ['sensorscope', 'uair']:
    rows = []
    for s in ['seed30%03d' % i for i in (1, 5, 10, 15, 20)]:
        f = ROOT / ds / s / 'training_eventtrace' / 'events.parquet'
        if not f.is_file():
            continue
        df = pd.read_parquet(f)
        for _, r in df.iterrows():
            try:
                j = json.loads(r['opportunity_features']) if isinstance(r['opportunity_features'], str) else {}
            except Exception:
                j = {}
            obs = r['observed_unit_ids']
            n_obs = len(json.loads(obs)) if isinstance(obs, str) else 0
            p = j.get('p_obs_true')
            q = j.get('q_use_true')
            if p is None or q is None:
                continue
            # corrected mass using the *true* ratios and the implemented floors
            a = n_obs / max(p, DESIGN['p_min'])
            m = a
            d = min(DESIGN['d_max'], 1.0 / max(q, DESIGN['q_min']))
            rows.append(dict(seed=s, n_obs=n_obs, p=p, q=q,
                             a=a, m=m, d=d, b=m * d,
                             floor_active=(q < DESIGN['q_min'])))
    t = pd.DataFrame(rows)
    print('=== %s ===' % ds.upper())
    print('  client-windows with O=1 (i.e. m>0): %d' % int((t['m'] > 0).sum()))
    print('  m > 0 fraction: %.1f%%   (client-windows with m==0 are dropped from A_r)' % (
        100 * (t['m'] > 0).mean()))
    pos = t[t['m'] > 0]
    if len(pos):
        print('  min b among m>0        : %.6g' % pos['b'].min())
        print('  => B_min (empirical)   > 0 : %s' % (pos['b'].min() > 0))
        print('  floor q_min active on  : %d / %d observed client-windows (%.1f%%)' % (
            int(pos['floor_active'].sum()), len(pos), 100 * pos['floor_active'].mean()))
        print('  1/q_min = %.1f  vs d_max = %.1f  -> ceiling binds on %d rows' % (
            1 / DESIGN['q_min'], DESIGN['d_max'], int((pos['q'] < 1 / DESIGN['d_max']).sum())))
    print()
