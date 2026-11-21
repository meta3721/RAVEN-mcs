import re
import shutil
import subprocess
from pathlib import Path

import pymupdf

SRC = Path('TO_OVERLEAF_paper_tmc_r1_clean')
T = Path('_tmp_pack/rootcomp')
if T.exists():
    shutil.rmtree(T)
T.mkdir(parents=True)
for f in ['main.tex', 'appendix.tex', 'supplemental.tex', 'reference.bib', 'main.bbl']:
    shutil.copy2(SRC / f, T / f)
shutil.copytree(SRC / 'figures', T / 'figures')

# --- Case A: supplemental compiled WITHOUT main.aux (what the user is seeing) ---
for p in T.glob('main.*'):
    if p.suffix in ('.aux', '.log', '.pdf', '.out'):
        p.unlink()
r = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'supplemental.tex'],
                   cwd=T, capture_output=True, text=True, errors='replace')
warn = re.findall(r"Reference `([^']+)' on page \d+ undefined", r.stdout)
print('=== CASE A: supplemental alone, no main.aux ===')
print('  undefined-reference warnings:', len(warn))
uniq = sorted(set(warn))
print('  distinct labels unresolved :', len(uniq))
for u in uniq[:12]:
    print('     ', u)
if (T / 'supplemental.pdf').is_file():
    d = pymupdf.open(T / 'supplemental.pdf')
    txt = ''.join(p.get_text() for p in d)
    print('  ?? in rendered PDF:', len(re.findall(r'\?\?', txt)))
    print('  pages:', d.page_count)

# --- Case B: compile main first, then supplemental (the fix) ---
print()
print('=== CASE B: main first (2 passes + bibtex), then supplemental (2 passes) ===')
for cmd in [['pdflatex', '-interaction=nonstopmode', 'main.tex'],
            ['bibtex', 'main'],
            ['pdflatex', '-interaction=nonstopmode', 'main.tex'],
            ['pdflatex', '-interaction=nonstopmode', 'main.tex'],
            ['pdflatex', '-interaction=nonstopmode', 'supplemental.tex'],
            ['pdflatex', '-interaction=nonstopmode', 'supplemental.tex']]:
    r = subprocess.run(cmd, cwd=T, capture_output=True, text=True, errors='replace')
warn2 = re.findall(r"Reference `([^']+)' on page \d+ undefined", r.stdout)
print('  undefined-reference warnings on last pass:', len(warn2))
for name in ['main', 'supplemental']:
    f = T / (name + '.pdf')
    if f.is_file():
        d = pymupdf.open(f)
        t = ''.join(p.get_text() for p in d)
        print('  %-13s pages=%-3d  ?? = %d' % (name, d.page_count, len(re.findall(r'\?\?', t))))

# --- which headings were garbled in case A ---
print()
print('=== headings in the appendix that use cross-document refs ===')
app = (SRC / 'appendix.tex').read_text(encoding='utf-8')
for ln, line in enumerate(app.split('\n'), 1):
    if re.search(r'\\(sub)?section\{[^}]*\\ref', line) or re.search(r'caption\{[^}]*\\ref', line):
        print('  appendix.tex L%-5d %s' % (ln, line.strip()[:120]))
