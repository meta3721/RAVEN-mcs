import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path('.')
patterns = [
    'window_metrics', 'method_diagnostics', 'propensity_diagnostics',
    'opportunity_ema_diagnostics', 'solver_diagnostics', 'metrics_window',
    'p2_invocation_states', 'ledger', 'final_metrics',
]
print('=== hunting for per-window logs that could verify A5 ===')
found = {}
for pat in patterns:
    hits = []
    for p in ROOT.rglob(pat + '*'):
        if any(s in str(p) for s in ('.venv', 'node_modules', '.git')):
            continue
        hits.append(p)
    if hits:
        found[pat] = hits
        print('  %-28s %d file(s)  e.g. %s' % (pat, len(hits), hits[0]))

print()
print('=== does any of them carry p/q/phi/clip diagnostics? ===')
KEYS = ['p_hat', 'q_hat', 'zeta', 'clip', 'clip_rate', 'pi_min', 'p_min', 'q_min',
        'ess', 'n_eff', 'alpha_max']
for pat, hits in found.items():
    for h in hits[:2]:
        try:
            if h.suffix == '.parquet':
                df = pd.read_parquet(h)
                cols = list(df.columns)
            elif h.suffix == '.json':
                j = json.loads(h.read_text(encoding='utf-8', errors='replace'))
                cols = list(j.keys()) if isinstance(j, dict) else ['(list)']
            elif h.suffix == '.jsonl':
                line = h.read_text(encoding='utf-8', errors='replace').splitlines()[0]
                cols = list(json.loads(line).keys())
            else:
                continue
        except Exception as e:
            print('  %-58s read-error %s' % (h.name, type(e).__name__))
            continue
        hit = [k for k in cols if any(t in k.lower() for t in KEYS)]
        if hit:
            print('  %-58s %s' % (str(h)[:58], hit[:10]))
