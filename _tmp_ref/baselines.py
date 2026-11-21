import re
from pathlib import Path

root = Path('TO_OVERLEAF_paper_tmc_r1_clean')
tex = (root / 'main.tex').read_text(encoding='utf-8')
apx = (root / 'appendix.tex').read_text(encoding='utf-8')
bib = (root / 'reference.bib').read_text(encoding='utf-8')

entries = {}
for m in re.finditer(r'@(\w+)\{([^,]+),(.*?)\n\}', bib, re.S):
    kind, key, body = m.group(1), m.group(2).strip(), m.group(3)
    f = {}
    for g in re.finditer(r'(\w+)\s*=\s*\{(.*?)\}\s*,?\s*\n', body + '\n', re.S):
        f[g.group(1).lower()] = ' '.join(g.group(2).split())
    f['_type'] = kind
    entries[key] = f

# 1) baseline names used in the paper
print('=== baseline / comparator method names appearing in main.tex ===')
names = ['FedAvg-Window', 'FedAsync-Window', 'TimeAlign-Agg', 'Local-H\\\'ajek',
         'TwoStage-H\\\'ajek', 'FedAU-Window', 'ObsUse-Window',
         'Central-All', 'Central-Delivered', 'RAVEN-SimOracle', 'Inst-Cal', 'Debt-Cal']
for n in names:
    c = len(re.findall(re.escape(n.replace('\\', '')), tex))
    print('  %-24s occurrences in main.tex: %d' % (n.replace('\\', ''), c))

# 2) the key that each baseline cites, from the baseline-description block
print()
print('=== citations attached to each comparator description ===')
for pat, label in [
    (r'FedAvg-Window~\\cite\{([^}]+)\}', 'FedAvg-Window'),
    (r'FedAsync-Window~\\cite\{([^}]+)\}', 'FedAsync-Window'),
    (r'Local-H\\\'ajek \(within-client[^)]*\\cite\{([^}]+)\}', 'Local-Hajek'),
    (r'FedAU-Window adapts participation debiasing\s*\n?\\cite\{([^}]+)\}', 'FedAU-Window'),
    (r'in the spirit of\n?\\cite\{([^}]+)\}', 'TimeAlign-Agg'),
    (r'One admissible implementation', '(impl)'),
]:
    hits = re.findall(pat, tex)
    if hits:
        print('  %-18s -> %s' % (label, sorted(set(hits))))

# 3) full bib entries for the comparator keys
print()
print('=== full bibliography entries for comparator works ===')
keys = ['mcmahan2017communication', 'xie2019asynchronous', 'wang2026federated',
        'horvitz1952generalization', 'hajek1971comment', 'wang2024lightweight']
for k in keys:
    e = entries.get(k)
    if not e:
        print('  %s : NOT IN BIB' % k)
        continue
    print('  --- %s (%s) ---' % (k, e.get('_type')))
    for f in ('title', 'author', 'journal', 'booktitle', 'volume', 'number', 'pages', 'year', 'publisher', 'doi', 'note', 'url', 'eprint'):
        if e.get(f):
            print('      %-10s %s' % (f + ':', e[f]))
