import json
from pathlib import Path

import pandas as pd

KEYS = ['q_min', 'p_min', 'a_max', 'd_max', 'lambda_beta', 'alpha_max',
        'min_effective_clients', 'E_min', 'e_min', 'a_bar', 'alpha_bar']

print('=== E3 formal run configs: look for the A5 design values ===')
base = Path('artifacts/e3_formal_runs_r1')
cfg_hits = 0
for p in list(base.rglob('*.json')) + list(base.rglob('*.yaml')) + list(base.rglob('*.yml'))[:400]:
    try:
        txt = p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        continue
    found = {}
    for k in KEYS:
        if '"%s"' % k in txt or ('%s:' % k) in txt:
            found[k] = True
    if found:
        cfg_hits += 1
        if cfg_hits <= 8:
            print('  %s  -> %s' % (p.relative_to(base), sorted(found)))
print('  files mentioning A5-ish config keys:', cfg_hits)

print()
print('=== direct search for the values in any config under the repo ===')
import re
pats = {
    'q_min': re.compile(r'q_min[\"\']?\s*[:=]\s*([0-9.eE+-]+)'),
    'p_min': re.compile(r'(?<![a-z_])p_min[\"\']?\s*[:=]\s*([0-9.eE+-]+)'),
    'a_max': re.compile(r'a_max[\"\']?\s*[:=]\s*([0-9.eE+-]+)'),
    'd_max': re.compile(r'd_max[\"\']?\s*[:=]\s*([0-9.eE+-]+)'),
}
from collections import Counter
vals = {k: Counter() for k in pats}
n = 0
for p in Path('.').rglob('*'):
    if not p.is_file() or p.suffix.lower() not in ('.json', '.yaml', '.yml', '.py', '.csv'):
        continue
    s = str(p)
    if any(x in s for x in ('.venv', 'node_modules', '.git', '\\Lib\\')):
        continue
    try:
        txt = p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        continue
    for k, rx in pats.items():
        for m in rx.findall(txt):
            vals[k][m] += 1
    n += 1
print('  files scanned:', n)
for k in pats:
    print('  %-6s most common values: %s' % (k, vals[k].most_common(6)))
