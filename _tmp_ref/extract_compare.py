import re
from pathlib import Path

import pymupdf

# ---------- July 26 PDF: locate the method section ----------
j = pymupdf.open('参考文件/RAVEN_MCS_2026_7_26_.pdf')
jt = '\n'.join(p.get_text() for p in j)
Path('_tmp_ref/jul26_full.txt').write_text(jt, encoding='utf-8')

print('=== JULY 26: section headings ===')
for m in re.finditer(r'(?m)^(I|II|III|IV|V|VI|VII|VIII)\.\s+([A-Z][A-Z \-,&/]{6,70})$', jt):
    print('  ', m.group(0).strip())
print()
print('=== JULY 26: subsection headings inside section IV (A./B./C. ...) ===')
n = 0
for m in re.finditer(r'(?m)^([A-H])\.\s+([A-Z][A-Za-z][^\n]{5,70})$', jt):
    n += 1
    print('  %s. %s' % (m.group(1), m.group(2).strip()))
    if n > 40:
        break

# ---------- current: section list ----------
cur = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
print()
print('=== CURRENT main.tex: sections / subsections ===')
for m in re.finditer(r'\\(section|subsection)\{([^}]+)\}', cur):
    print('  %-12s %s' % (m.group(1), m.group(2)))

# ---------- abstract word-level diff of headline nouns ----------
print()
print('=== JULY 26 abstract ===')
a = re.search(r'Abstract—(.*?)(?=\nIndex Terms|\nI\.\s)', jt, re.S)
if a:
    print(' '.join(a.group(1).split())[:1900])
