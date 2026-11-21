import re
import subprocess
from pathlib import Path

import pymupdf

T = Path('_tmp_pack/rootcomp')
aux = (T / 'main.aux').read_text(encoding='utf-8', errors='replace')

# harvest label -> printed number from main.aux
labels = {}
for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}', aux):
    key, num, page = m.group(1), m.group(2), m.group(3)
    labels[key] = (num, page)

print('main.aux labels harvested:', len(labels))
for k in ['tab:main_effectiveness', 'thm:agg-lcb', 'sec:theory', 'eq:Cr']:
    print('   %-26s -> %s' % (k, labels.get(k)))

# which labels does the appendix need from main?
apx = Path('TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex').read_text(encoding='utf-8')
apx_labels = set(re.findall(r'\\label\{([^}]+)\}', apx))
needed = []
for r in re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', apx):
    if r not in apx_labels and r not in needed:
        needed.append(r)
print()
print('labels the appendix needs from main:', len(needed))

# EXP 2: provide them via \providecommand (possible fallback path)
lines = ['% AUTO-GENERATED from main.aux - fallback for standalone appendix compilation']
for k in needed:
    if k in labels:
        lines.append('\\providecommand{\\r@%s}{%s}' % (k, labels[k][0]))
(T / 'frozenlabels.tex').write_text('\n'.join(lines) + '\n', encoding='utf-8')

sup = (T / 'supplemental.tex').read_text(encoding='utf-8')
patched = sup.replace('\\externaldocument{main}',
                      '\\externaldocument{main}\n\\input{frozenlabels}')
(T / 'supplemental.tex').write_text(patched, encoding='utf-8')

# rebuild WITHOUT main.aux
for p in list(T.glob('main.*')) + list(T.glob('supplemental.aux')) + list(T.glob('supplemental.out')):
    if p.suffix in ('.aux', '.out'):
        p.unlink()
r = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'supplemental.tex'],
                   cwd=T, capture_output=True, text=True, errors='replace')
warn = re.findall(r"Reference `([^']+)' on page \d+ undefined", r.stdout)
print()
print('=== EXP 2: standalone appendix + frozen \\r@ map ===')
print('  undefined-reference warnings:', len(warn))
print('  distinct:', len(set(warn)))
for u in sorted(set(warn))[:15]:
    print('     ', u)
if (T / 'supplemental.pdf').is_file():
    d = pymupdf.open(T / 'supplemental.pdf')
    t = ''.join(p.get_text() for p in d)
    print('  ?? in rendered PDF:', len(re.findall(r'\?\?', t)), ' pages:', d.page_count)
