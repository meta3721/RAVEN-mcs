"""Validate the review report: heading order, table column consistency, placeholders."""
import re
import sys
from pathlib import Path

p = Path('ccfa-review-reports/raven-mcs-tmc-review.md')
text = p.read_text(encoding='utf-8')
lines = text.split('\n')

required = [
    '## 1. Report Metadata',
    '## 2. Desk Rejection Assessment',
    '## 3. Paper Summary And Contribution Map',
    '## 4. Search And Related-Work Basis',
    '## 5. Expected Review Outcome',
    '## 6. Strengths And Weaknesses',
    '## 7. Potentially Missing Related Work',
    '## 8. Claim-Evidence Audit',
    '## 9. Experiment / Benchmark / Reproducibility Audit',
    '## 10. Multi-Reviewer Panel',
    '## 11. Concerns Table',
    '## 12. AC / Meta-Review',
    '## 13. Quantitative Scores',
    '## 14. Questions For Authors',
    '## 15. Score Revision Criteria',
    '## 16. Action Plan And CCFA Handoffs',
]
pos, ok = -1, True
for h in required:
    i = text.find(h)
    if i < 0 or i < pos:
        print('MISSING/OUT-OF-ORDER:', h)
        ok = False
    else:
        pos = i
print('section order:', 'OK' if ok else 'FAIL')

# markdown table consistency (skip fenced code blocks)
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

bad = 0
for n, t in enumerate(tables, 1):
    widths = {len(r.strip().strip('|').split('|')) for r in t}
    seps = [r for r in t if re.fullmatch(r'\|[\s:|-]+\|', r.strip())]
    if len(widths) != 1 or len(seps) != 1:
        print('TABLE %d: widths=%s separators=%d' % (n, sorted(widths), len(seps)))
        print('   header:', t[0][:110])
        bad += 1
print('markdown tables:', len(tables), '| malformed:', bad)

# placeholders
for tok in ('TBD', 'TODO', '[fill]', 'XXX', 'FIXME'):
    if tok in text:
        print('PLACEHOLDER FOUND:', tok)
print('placeholders: none' if not any(t in text for t in ('TBD', 'TODO', '[fill]', 'XXX', 'FIXME')) else '')

print('lines: %d, bytes: %d' % (len(lines), len(text.encode())))
