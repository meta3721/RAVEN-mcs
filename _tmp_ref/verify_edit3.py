import re
from pathlib import Path

import pymupdf

d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
t = ''.join(p.get_text() for p in d)
norm = re.sub(r'-\s*\n\s*', '-', t)
flat = ' '.join(norm.split())

print('=== edit 1: the design-ratio reduction sentence (was "used by the main protocol") ===')
i = flat.find('Under within-stratum exchangeability')
print(' ', flat[i:i + 150] if i >= 0 else '(not found)')

print()
print('=== edit 2: the new sentence in the experiment setup ===')
j = flat.find('The main blocks assume within-stratum exchangeability')
print(' ', flat[max(0, j - 230):j + 210] if j >= 0 else '(not found)')

print()
print('=== term cleanup ===')
print('  "main protocol" occurrences in PDF:', flat.count('main protocol'))

print()
print('=== document health ===')
print('  pages = %d   ?? = %d   E-codes = %d' % (
    d.page_count, len(re.findall(r'\?\?', t)), len(re.findall(r'\bE[1-9]\b', t))))
