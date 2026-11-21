"""Validate the diagnostic record's markdown structure."""
import re
from pathlib import Path

p = Path('ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md')
text = p.read_text(encoding='utf-8')
lines = text.split('\n')

tables, cur, fence = [], [], False
for ln in lines:
    if ln.strip().startswith('```'):
        fence = not fence
        continue
    if fence:
        continue
    if ln.strip().startswith('|'):
        cur.append(ln)
    elif cur:
        tables.append(cur)
        cur = []
if cur:
    tables.append(cur)

def cells(row):
    """Split a markdown table row on unescaped pipes (\\| stays in-cell)."""
    body = row.strip()
    if body.startswith('|'):
        body = body[1:]
    if body.endswith('|') and not body.endswith('\\|'):
        body = body[:-1]
    return re.split(r'(?<!\\)\|', body)


bad = 0
for n, tb in enumerate(tables, 1):
    widths = {len(cells(r)) for r in tb}
    seps = [r for r in tb if re.fullmatch(r'\|[\s:|-]+\|', r.strip())]
    if len(widths) != 1 or len(seps) != 1:
        bad += 1
        print('TABLE %d widths=%s seps=%d | %s' % (n, sorted(widths), len(seps), tb[0][:90]))
print('tables=%d malformed=%d' % (len(tables), bad))

for tok in ('TBD', 'TODO', '[fill]', 'FIXME'):
    if tok in text:
        print('PLACEHOLDER FOUND:', tok)
print('placeholders: none' if not any(t in text for t in ('TBD', 'TODO', '[fill]', 'FIXME')) else '')

heads = [l for l in lines if l.startswith('#')]
print('headings=%d' % len(heads))
print('lines=%d bytes=%d' % (len(lines), len(text.encode())))
