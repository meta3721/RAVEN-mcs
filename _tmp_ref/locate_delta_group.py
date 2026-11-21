"""Where is Delta_group defined, and where is it used?"""
import re

import pymupdf

d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')

print('=== pages mentioning the definition phrase ===')
for i in range(d.page_count):
    t = d[i].get_text()
    if 'group-level structural mismatch' in t:
        k = t.find('group-level structural mismatch')
        print('page %d:' % (i + 1))
        print(t[max(0, k - 520):k + 260])
        print()

print('=== page 11: Delta_group occurrences ===')
t = d[10].get_text()
for m in re.finditer(r'group', t):
    pass
for ln in t.split('\n'):
    if 'group' in ln.lower() or 'RMSE' in ln:
        print('   ', ln.strip()[:110])
