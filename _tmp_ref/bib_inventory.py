import re
from pathlib import Path

bib = Path('TO_OVERLEAF_paper_tmc_r1_clean/reference.bib').read_text(encoding='utf-8')
tex = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
apx = Path('TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex').read_text(encoding='utf-8')

# citation order as in main.bbl (the printed numbering)
bbl = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.bbl').read_text(encoding='utf-8')
order = re.findall(r'\\bibitem\{([^}]+)\}', bbl)

entries = {}
for m in re.finditer(r'@(\w+)\{([^,]+),(.*?)\n\}', bib, re.S):
    kind, key, body = m.group(1), m.group(2).strip(), m.group(3)
    fields = {}
    for f in re.finditer(r'(\w+)\s*=\s*\{(.*?)\}\s*,?\s*\n', body + '\n', re.S):
        fields[f.group(1).lower()] = ' '.join(f.group(2).split())
    fields['_type'] = kind
    entries[key] = fields

print('bib entries parsed:', len(entries))
print()
print('%-4s %-30s %-11s %s' % ('#', 'key', 'type', 'venue / year / pages'))
print('-' * 130)
for i, key in enumerate(order, 1):
    e = entries.get(key, {})
    venue = e.get('journal') or e.get('booktitle') or e.get('howpublished') or '?'
    yr = e.get('year', '?')
    extra = []
    for k in ('volume', 'number', 'pages', 'note', 'doi'):
        if e.get(k):
            extra.append('%s=%s' % (k[0].upper(), e[k]))
    print('%-4d %-30s %-11s %s' % (i, key, e.get('_type', '?'),
                                   ('%s | %s | %s' % (venue[:52], yr, ' '.join(extra)))[:150]))

print()
print('=== 2025/2026 entries (highest verification risk) ===')
for key in order:
    e = entries.get(key, {})
    if e.get('year') in ('2025', '2026'):
        venue = e.get('journal') or e.get('booktitle') or '?'
        print('  [%d] %-30s %s | %s | vol=%s no=%s pp=%s' % (
            order.index(key) + 1, key, e.get('_type'), venue, e.get('volume', '-'),
            e.get('number', '-'), e.get('pages', '-')))
        print('       title: %s' % e.get('title', '?')[:120])
