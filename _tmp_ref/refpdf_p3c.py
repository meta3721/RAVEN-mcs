"""Find paper 3's Table II content and the matching bib entry."""
import re
from pathlib import Path

import pymupdf

print('=== 3.pdf page 12 full text tail ===')
d = pymupdf.open('C:/Cursor/raven.mcs/参考文件/相关重要论文/3.pdf')
t = d[11].get_text()
print(t[-2600:])
print()
print('=== search all pages for the table rows ===')
for i in range(d.page_count):
    tt = d[i].get_text()
    if 'STATISTICS OF THREE' in tt or ('Num' in tt and 'Sparsity' in tt) or 'Sparsity' in tt:
        print('page %d has a stats-ish table' % (i + 1))
        for m in re.finditer(r'Sparsity|Num(?:ber)? of|Temporal|Resolution', tt):
            a = max(0, m.start() - 90)
            print('   ', re.sub(r'\s+', ' ', tt[a:m.start() + 260]))
            break

print()
print('=== reference.bib: 2026 federated/completion entries ===')
bib = Path('TO_OVERLEAF_paper_tmc_r1_clean/reference.bib').read_text(encoding='utf-8')
for blk in re.split(r'\n@', bib):
    if re.search(r'2026', blk) and re.search(r'federated|completion|crowdsens|Mobile Computing', blk, re.I):
        print('@' + blk.strip()[:520])
        print('-' * 60)
