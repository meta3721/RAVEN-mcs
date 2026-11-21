from pathlib import Path

import pandas as pd

f = Path('artifacts/e3_formal_runs_r1/eventtraces/sensorscope/seed30001/training_eventtrace/events.parquet')
df = pd.read_parquet(f)
print('=== training_eventtrace/events.parquet ===')
print('  rows =', len(df))
print('  cols =', list(df.columns))
print()
print(df.head(3).to_string()[:1200])
print()
# look for true-probability style columns
cands = [c for c in df.columns if any(t in c.lower() for t in
         ('p_obs', 'q_use', 'q_true', 'true', 'pi_opp', 'zeta', 'prob', 'usable', 'observed'))]
print('candidate true/selection columns:', cands)
print()
for c in cands[:8]:
    try:
        print('  %-28s dtype=%-10s min=%.6g max=%.6g' % (
            c, str(df[c].dtype), df[c].min(), df[c].max()))
    except Exception:
        print('  %-28s (non-numeric)' % c)
