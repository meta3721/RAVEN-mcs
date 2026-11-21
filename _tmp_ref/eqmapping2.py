import re
from pathlib import Path

import pymupdf

src = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
lines = src.split('\n')

n = 0
rows = []
i = 0
while i < len(lines):
    line = lines[i]
    m = re.search(r'\\begin\{(equation|align|gather|multline|flalign|eqnarray)\}', line)
    if not m:
        i += 1
        continue
    env = m.group(1)
    j = i
    while j < len(lines) and ('\\end{%s}' % env) not in lines[j]:
        j += 1
    block = lines[i:j + 1]
    if env == 'equation':
        n += 1
        lab = re.search(r'\\label\{([^}]+)\}', '\n'.join(block))
        rows.append((n, i + 1, lab.group(1) if lab else '(unlabeled)'))
    else:
        # one number per row; a row is broken by \\ or \nonumber suppressing it
        pending_label = None
        for k, bl in enumerate(block):
            lab = re.search(r'\\label\{([^}]+)\}', bl)
            if lab:
                pending_label = lab.group(1)
            has_break = ('\\\\' in bl) or (k == len(block) - 1)
            suppressed = '\\nonumber' in bl or '\\notag' in bl
            if has_break:
                if not suppressed:
                    n += 1
                    rows.append((n, i + k + 1, pending_label or '(unlabeled)'))
                pending_label = None
    i = j + 1

print('numbered equations (row-aware):', n)
print()
for num, ln, lab in rows[:14]:
    star = ''
    if lab in ('eq:atomic_target', 'eq:target_compatibility'):
        star = '   <-- cited by A1'
    print('  (%2d)  L%-5d %s%s' % (num, ln, lab, star))
print()
print('=== confirm against the PDF ===')
d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
t4 = d[3].get_text()
for probe in ['atomic deploy', 'Compatibility requires']:
    i2 = t4.find(probe)
    if i2 >= 0:
        seg = ' '.join(t4[i2:i2 + 220].split())
        m = re.search(r'\((\d+)\)', seg)
        print('  %-22s -> printed number %s' % (probe, m.group(1) if m else '?'))
