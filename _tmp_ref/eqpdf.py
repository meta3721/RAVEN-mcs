import re
from pathlib import Path

import pymupdf

d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
full = ''.join(p.get_text() for p in d)
flat = ' '.join(full.split())

print('=== A1 as printed in the PDF ===')
i = flat.find('A1 (Compatible target support')
print(' ', flat[i:i + 300] if i >= 0 else '(not found)')

print()
print('=== every equation number token in the first 7 pages, in order ===')
toks = []
for pi in range(7):
    t = d[pi].get_text()
    for m in re.finditer(r'\((\d{1,2})\)', t):
        toks.append((pi + 1, int(m.group(1))))
seen = []
for p, n in toks:
    if not seen or seen[-1][1] != n or seen[-1][0] != p:
        seen.append((p, n))
print('  (page, eq#) first occurrences:')
for p, n in seen[:26]:
    print('    p%-3d (%d)' % (p, n))
