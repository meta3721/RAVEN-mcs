import re
from pathlib import Path

import pymupdf

src = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
lines = src.split('\n')

# Enumerate ALL numbered display-math environments in source order.
ENV_OPEN = re.compile(r'\\begin\{(equation|align|gather|multline|flalign|eqnarray)\}')
order = []
n = 0
i = 0
while i < len(lines):
    m = ENV_OPEN.search(lines[i])
    if m:
        env = m.group(1)
        j = i
        while j < len(lines) and ('\\end{%s}' % env) not in lines[j]:
            j += 1
        block = '\n'.join(lines[i:j + 1])
        n += 1
        lab = re.search(r'\\label\{([^}]+)\}', block)
        order.append((n, i + 1, env, lab.group(1) if lab else '(unlabeled)'))
        i = j + 1
        continue
    i += 1

print('numbered display-math environments found:', len(order))
print()
for n, ln, env, lab in order[:12]:
    print('  (%2d) L%-5d %-9s %s' % (n, ln, env, lab))

print()
print('=== the labels A1 cites ===')
for n, ln, env, lab in order:
    if lab in ('eq:atomic_target', 'eq:target_compatibility'):
        print('  %s -> source-order number (%d), L%d' % (lab, n, ln))

print()
print('=== cross-check with the PDF: what is printed as (4) and (5)? ===')
d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
for pi in range(3, 5):
    t = d[pi].get_text()
    for m in re.finditer(r'\((\d{1,2})\)', t):
        if m.group(1) in ('4', '5'):
            s = max(0, m.start() - 120)
            print('   p%d  ...%s' % (pi + 1, ' '.join(t[s:m.end() + 5].split())[-150:]))
