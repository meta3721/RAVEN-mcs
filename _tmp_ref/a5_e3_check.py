import re
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path('.')
files = [p for p in ROOT.rglob('metrics_window.parquet')
         if not any(s in str(p) for s in ('.venv', 'node_modules', '.git'))]
print('metrics_window.parquet total:', len(files))

# group by top-level area and dataset/round hints
groups = Counter()
for p in files:
    parts = p.parts
    key = '/'.join(parts[:3]) if len(parts) >= 3 else str(p)
    groups[key] += 1
print()
print('=== by location (top 12) ===')
for k, v in groups.most_common(12):
    print('  %-58s %d' % (k[:58], v))

# does E3 show up?
e3 = [p for p in files if 'e3' in str(p).lower()]
print()
print('E3-related metrics_window files:', len(e3))
for p in e3[:6]:
    print('   ', p)

# inspect one E3 file if available, else the biggest group's file
cand = e3[0] if e3 else files[0]
print()
print('=== columns of a sample file ===')
print('   ', cand)
df = pd.read_parquet(cand)
cols = list(df.columns)
want = [c for c in cols if any(t in c.lower() for t in
        ('p_hat', 'q_hat', 'zeta', 'clip', 'ess', 'n_eff', 'alpha'))]
print('   rows=%d  A5-relevant cols=%s' % (len(df), want))
print('   all cols:', cols[:22])
