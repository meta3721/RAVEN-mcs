from pathlib import Path

import pandas as pd

CHECKS = [
    ('p_obs_true (E3 formal trace)', 'artifacts/e3_formal_runs_r1/eventtraces/sensorscope/seed30001/atomic_p_obs_true.parquet'),
    ('usable_events', 'RAVEN_MCS_PUBLIC_REPRO_R1/eventtraces/e3/sensorscope/seed30001/opportunity_events.parquet'),
    ('failed_attempts', 'RAVEN_MCS_PUBLIC_REPRO_R1/eventtraces/e2/30019/complete_aligned/hard/failed_attempts.parquet'),
    ('client_window_activity', 'RAVEN_MCS_PUBLIC_REPRO_R1/eventtraces/e2/30019/complete_aligned/hard/client_window_activity.parquet'),
    ('observation_events', 'RAVEN_MCS_PUBLIC_REPRO_R1/eventtraces/e2/30019/complete_aligned/hard/observation_events.parquet'),
    ('usable_events (e2)', 'RAVEN_MCS_PUBLIC_REPRO_R1/eventtraces/e2/30019/complete_aligned/hard/usable_events.parquet'),
    ('SCD_PHI', 'RAVEN_MCS_PUBLIC_REPRO_R1/tables/SCD_PHI.csv'),
]

for name, rel in CHECKS:
    p = Path(rel)
    if not p.is_file():
        print('=== %s ===  MISSING: %s' % (name, rel))
        print()
        continue
    if p.suffix == '.csv':
        df = pd.read_csv(p)
    else:
        df = pd.read_parquet(p)
    print('=== %s ===' % name)
    print('   %s' % rel)
    print('   rows=%d cols=%s' % (len(df), list(df.columns)))
    print('   head:')
    print('   ', df.head(2).to_string().replace('\n', '\n    ')[:600])
    print()
