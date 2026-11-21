import re
from pathlib import Path

src = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')

# Walk the file counting numbered equation-likes, and record which label gets which number.
count = 0
rows = []
lines = src.split('\n')
i = 0
while i < len(lines):
    line = lines[i]
    for m in re.finditer(r'\\begin\{(equation|align|align\*|equation\*|gather)\}', line):
        env = m.group(1)
        # find the environment end
        j = i
        while j < len(lines) and ('\\end{%s}' % env) not in lines[j]:
            j += 1
        block = '\n'.join(lines[i:j + 1])
        lab = re.search(r'\\label\{([^}]+)\}', block)
        if not env.endswith('*'):
            count += 1
            rows.append((count, lab.group(1) if lab else '(no label)', i + 1))
    i += 1

print('total numbered equation environments in main.tex:', count)
print()
print('=== equations 1..8 and the labels that A1 references ===')
for n, lab, ln in rows[:10]:
    mark = '   <-- referenced by A1' if lab in ('eq:atomic_target', 'eq:target_compatibility') else ''
    print('  (%d)  L%-5d  %s%s' % (n, ln, lab, mark))

print()
print('=== locate the two labels ===')
for n, lab, ln in rows:
    if lab in ('eq:atomic_target', 'eq:target_compatibility'):
        print('  %s is equation (%d), defined at main.tex L%d' % (lab, n, ln))
