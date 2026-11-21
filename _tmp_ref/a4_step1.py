"""A4 reconnaissance, step 1-2: which Table II columns exist in the E3 run
metrics, and where does WorstGroupRMSE come from?"""
import json
from pathlib import Path

print('=== E3 final_metrics.json key set (sensorscope/raven/seed30001) ===')
p = Path('artifacts/e3_formal_runs_r1/runs/sensorscope/raven/seed30001/final_metrics.json')
j = json.loads(p.read_text(encoding='utf-8'))
for k in sorted(j):
    v = j[k]
    s = str(v)
    print('  %-26s %s' % (k, s[:60]))
print()
print('  WorstGroupRMSE present?', 'WorstGroupRMSE' in j)
print('  any key containing "group"?', [k for k in j if 'roup' in k])

print()
print('=== other files in that run directory ===')
for f in sorted(p.parent.iterdir()):
    print('  %-38s %d bytes' % (f.name, f.stat().st_size))
