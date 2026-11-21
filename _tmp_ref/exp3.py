import re
import subprocess
from pathlib import Path

import pymupdf

T = Path('_tmp_pack/rootcomp')

# Revert the failed experiment
sup = (T / 'supplemental.tex').read_text(encoding='utf-8')
sup = sup.replace('\\externaldocument{main}\n\\input{frozenlabels}', '\\externaldocument{main}')
(T / 'supplemental.tex').write_text(sup, encoding='utf-8')
if (T / 'frozenlabels.tex').exists():
    (T / 'frozenlabels.tex').unlink()

# Build the frozen map as \newlabel commands inside a group copy
src = (T / 'main.aux').read_text(encoding='utf-8', errors='replace')
newlabels = re.findall(r'(\\newlabel\{[^}]*\}\{\{[^}]*\}\{[^}]*\}\})', src)
print('newlabel entries to freeze:', len(newlabels))

frozen = ['% AUTO-GENERATED fallback: lets supplemental.tex resolve main-paper',
          '% cross-references when compiled on its own (no main.aux present).',
          '% Regenerate by running: python tools/make_frozen_refs.py',
          '\\makeatletter',
          '\\@ifundefined{r@tab:main_effectiveness}{%',
          '  \\@for\\x:=',  # placeholder, replaced below
          ]
# Simpler: emit each \newlabel guarded by @ifundefined using \expandafter chain
body = []
for nl in newlabels:
    key = re.match(r'\\newlabel\{([^}]*)\}', nl).group(1)
    body.append('  \\@ifundefined{r@%s}{%s}{}' % (key, nl))
frozen = ['% AUTO-GENERATED fallback so supplemental.tex can compile standalone.',
          '% Regenerate after any main.tex change that alters numbering.',
          '\\makeatletter']
# emit in chunks so we stay under TeX's argument limits
CH = 12
for i in range(0, len(body), CH):
    frozen.append('\\@ifundefined{r@tab:main_effectiveness}{%')
    frozen.extend(body[i:i + CH])
    frozen.append('}{}')
frozen.append('\\makeatother')
(T / 'frozenrefs.tex').write_text('\n'.join(frozen) + '\n', encoding='utf-8')

sup = sup.replace('\\externaldocument{main}',
                  '\\externaldocument{main}\n\\input{frozenrefs}')
(T / 'supplemental.tex').write_text(sup, encoding='utf-8')

# clean and compile standalone
for p in list(T.glob('main.*')) + list(T.glob('supplemental.aux')) + list(T.glob('supplemental.out')):
    if p.suffix in ('.aux', '.out'):
        p.unlink()
r = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'supplemental.tex'],
                   cwd=T, capture_output=True, text=True, errors='replace')
warn = re.findall(r"Reference `([^']+)' on page \d+ undefined", r.stdout)
print()
print('=== EXP 3: standalone appendix + guarded \\newlabel fallback ===')
print('  undefined-reference warnings:', len(warn))
print('  distinct:', len(set(warn)))
for u in sorted(set(warn))[:12]:
    print('     ', u)
if (T / 'supplemental.pdf').is_file():
    d = pymupdf.open(T / 'supplemental.pdf')
    t = ''.join(p.get_text() for p in d)
    print('  ?? in rendered PDF:', len(re.findall(r'\?\?', t)), ' pages:', d.page_count)
    i = t.find('Proof of')
    print('  sample heading:', ' '.join(t[i:i + 90].split()) if i >= 0 else 'n/a')
