"""Can the six E2 scenarios be tabulated from existing results?"""
from pathlib import Path

import pandas as pd

R = Path('artifacts/e2_traffic_formal_runs_r1')

for name in ('formal_results.csv', 'formal_statistics.csv',
             'formal_group_metrics.csv', 'paired_comparisons.csv',
             'formal_runtime_metrics.csv'):
    p = R / name
    if not p.is_file():
        print('%-28s MISSING' % name)
        continue
    df = pd.read_csv(p)
    print('=' * 78)
    print('%s   rows=%d  cols=%d' % (name, len(df), len(df.columns)))
    print('  columns:', list(df.columns))
    for c in ('scenario', 'method', 'seed'):
        if c in df.columns:
            vals = sorted(df[c].dropna().unique().tolist())
            print('  %-9s %d values: %s' % (c, len(vals), vals[:8]))
    print()
