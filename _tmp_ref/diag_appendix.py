import re
from collections import Counter
from pathlib import Path

R = Path('TO_OVERLEAF_paper_tmc_r1_clean')
main = (R / 'main.tex').read_text(encoding='utf-8')
apx = (R / 'appendix.tex').read_text(encoding='utf-8')
sup = (R / 'supplemental.tex').read_text(encoding='utf-8')

ml = set(re.findall(r'\\label\{([^}]+)\}', main))
al = set(re.findall(r'\\label\{([^}]+)\}', apx))


def refs(t):
    return re.findall(r'\\(?:ref|eqref|autoref|Cref|cref)\{([^}]+)\}', t)


ext = [x for x in refs(apx) if x not in al]
print('=== appendix references NOT defined inside appendix (need main.aux) ===')
c = Counter(ext)
print('  total occurrences:', len(ext), ' distinct:', len(c))
for k, v in c.most_common():
    where = 'IN MAIN' if k in ml else '*** MISSING EVERYWHERE ***'
    print('   %3dx  %-38s %s' % (v, k, where))

print()
print('=== the reverse direction (main references appendix labels) ===')
ext2 = [x for x in refs(main) if x not in ml]
print('  total occurrences:', len(ext2), ' distinct:', len(set(ext2)))
if ext2:
    for k, v in Counter(ext2).most_common():
        print('   %3dx  %s' % (v, k))
else:
    print('   (none - main is self-contained, as intended after the one-way conversion)')

print()
print('=== supplemental.tex: does it import main.aux? ===')
for ln, line in enumerate(sup.split('\n'), 1):
    if 'xr' in line or 'externaldocument' in line or 'setcounter' in line:
        print('   L%-4d %s' % (ln, line.strip()))

print()
print('=== strings that a reviewer might read as "proof by theory" ===')
for pat in ['by theory', 'by the theory', 'Proof by', 'proof of the theory',
            'See the proof', 'see the proof', 'Proof.', 'Proof of']:
    a = apx.count(pat)
    b = main.count(pat)
    if a or b:
        print('   %-22r appendix=%d  main=%d' % (pat, a, b))
