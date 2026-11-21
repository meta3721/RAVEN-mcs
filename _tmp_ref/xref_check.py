import re
import sys
from pathlib import Path

root = Path('TO_OVERLEAF_paper_tmc_r1_clean')

def labels_and_refs(tex):
    t = Path(tex).read_text(encoding='utf-8', errors='replace')
    labs = set(re.findall(r'\\label\{([^}]+)\}', t))
    refs = set(re.findall(r'\\(?:ref|eqref|autoref|Cref|cref)\{([^}]+)\}', t))
    return labs, refs

main_tex = root / 'main.tex'
app_tex = root / 'appendix.tex'

main_labs, main_refs = labels_and_refs(main_tex)
app_labs, app_refs = labels_and_refs(app_tex)

# aux-declared labels
aux = (root / 'main.aux').read_text(encoding='utf-8', errors='replace')
aux_new = set(re.findall(r'\\newlabel\{([^}]+)\}', aux))
sup_aux = (root / 'supplemental.aux').read_text(encoding='utf-8', errors='replace')
sup_new = set(re.findall(r'\\newlabel\{([^}]+)\}', sup_aux))
sup_new_stripped = {re.sub(r'^frommain\.', '', x) for x in sup_new}

print('=== label counts ===')
print('  main.tex labels      :', len(main_labs))
print('  appendix.tex labels  :', len(app_labs))
print('  main.aux newlabels   :', len(aux_new))
print('  suppl.aux newlabels  :', len(sup_new), '(after stripping frommain.:', len(sup_new_stripped), ')')

print()
print('=== main.tex refs that no label in main.tex provides (must come from appendix via xr) ===')
need_ext_main = sorted(main_refs - main_labs)
for r in need_ext_main:
    ok = r in app_labs
    print('  %-40s %s' % (r, 'OK in appendix' if ok else '*** MISSING EVERYWHERE ***'))

print()
print('=== appendix.tex refs that no label in appendix.tex provides (must come from main via xr) ===')
need_ext_app = sorted(app_refs - app_labs)
missing_app = []
for r in need_ext_app:
    ok = r in main_labs
    if not ok:
        missing_app.append(r)
    print('  %-40s %s' % (r, 'OK in main' if ok else '*** MISSING EVERYWHERE ***'))

print()
print('=== labels present in .tex but absent from main.aux (stale aux => ?? on next compile) ===')
only_tex = sorted(main_labs - aux_new)
for r in only_tex:
    print('  ', r)
print('  count:', len(only_tex))

print()
print('=== summary ===')
print('  main->appendix unresolved :', [r for r in need_ext_main if r not in app_labs])
print('  appendix->main unresolved :', missing_app)
print('  main.tex labels not yet in main.aux :', len(only_tex))
