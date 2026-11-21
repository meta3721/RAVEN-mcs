import re
import subprocess
from pathlib import Path

import pymupdf

T = Path('_tmp_pack/rootcomp')
SRC = Path('TO_OVERLEAF_paper_tmc_r1_clean')

# restore a pristine supplemental.tex and rebuild main so main.aux exists
sup0 = (SRC / 'supplemental.tex').read_text(encoding='utf-8')
(T / 'supplemental.tex').write_text(sup0, encoding='utf-8')
for p in list(T.glob('frozen*')) + list(T.glob('supplemental.aux')) + list(T.glob('supplemental.out')):
    if p.suffix in ('.tex', '.aux', '.out'):
        p.unlink()
for cmd in [['pdflatex', '-interaction=nonstopmode', 'main.tex'],
            ['bibtex', 'main'],
            ['pdflatex', '-interaction=nonstopmode', 'main.tex']]:
    subprocess.run(cmd, cwd=T, capture_output=True, text=True, errors='replace')

aux = (T / 'main.aux').read_text(encoding='utf-8', errors='replace')
entries = re.findall(r'\\newlabel\{[^}]*\}\{\{[^}]*\}\{[^}]*\}', aux)
print('newlabel entries harvested:', len(entries))

rows = []
for e in entries:
    key = re.match(r'\\newlabel\{([^}]*)\}', e).group(1)
    rows.append('  \\@ifundefined{r@%s}{%s}{}' % (key, e))

frozen = ['% AUTO-GENERATED fallback so supplemental.tex can compile standalone.',
          '% Regenerate after any main.tex change that alters numbering.',
          '\\makeatletter']
CH = 10
for i in range(0, len(rows), CH):
    frozen.append('\\@ifundefined{r@tab:main_effectiveness}{%')
    frozen.extend(rows[i:i + CH])
    frozen.append('}{}')
frozen.append('\\makeatother')
(T / 'frozenrefs.tex').write_text('\n'.join(frozen) + '\n', encoding='utf-8')
print('frozenrefs.tex written, bytes =', (T / 'frozenrefs.tex').stat().st_size)

sup = sup0.replace('\\externaldocument{main}', '\\externaldocument{main}\n\\input{frozenrefs}')
(T / 'supplemental.tex').write_text(sup, encoding='utf-8')

# now delete main.aux and compile the appendix alone
(T / 'main.aux').unlink()
for p in list(T.glob('supplemental.aux')) + list(T.glob('supplemental.out')):
    p.unlink()
r = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'supplemental.tex'],
                   cwd=T, capture_output=True, text=True, errors='replace')
warn = re.findall(r"Reference `([^']+)' on page \d+ undefined", r.stdout)
print()
print('=== EXP 3: appendix alone (no main.aux) + guarded newlabel fallback ===')
print('  undefined-reference warnings:', len(warn), ' distinct:', len(set(warn)))
for u in sorted(set(warn))[:15]:
    print('     ', u)
p = T / 'supplemental.pdf'
if p.is_file():
    d = pymupdf.open(p)
    t = ''.join(pg.get_text() for pg in d)
    print('  ?? in rendered PDF:', len(re.findall(r'\?\?', t)), ' pages:', d.page_count)
    for probe in ['Proof of Theorem', 'Proof of Proposition', 'Proof of Corollary']:
        i = t.find(probe)
        if i >= 0:
            print('  sample:', ' '.join(t[i:i + 80].split()))
