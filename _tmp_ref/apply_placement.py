"""Move the A5/A6 support-hypothesis audit next to the coverage-stress audit.

That placement is the most coherent of the clean options: it puts the two audit
sections of the supplement adjacent to each other instead of splitting the
theory-diagnostic pair, and it avoids the one-line column overfull that every
earlier placement induces.
"""
from pathlib import Path

APX = Path('TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex')
SEC = r'\section{Support-Hypothesis Audit for A5 and A6}'
END = r'\section{P2 Feasibility Diagnostics}'
ANCHOR = r'\section{Coverage-Stress Audit of the Candidate Gate}'

text = APX.read_text(encoding='utf-8')
start = text.index(SEC)
end = text.index(END)
block = text[start:end]
rest = text[:start] + text[end:]

if ANCHOR not in rest:
    raise SystemExit('anchor not found: %s' % ANCHOR)
i = rest.index(ANCHOR)
new = rest[:i] + block + rest[i:]

# collapse the blank lines left behind by the removal
new = new.replace('\n\n\n\n', '\n\n\n')
APX.write_text(new, encoding='utf-8')

b = APX.read_bytes()
if b'\r\n' in b:
    APX.write_bytes(b.replace(b'\r\n', b'\n'))
    print('normalised line endings to LF')

order = [l for l in new.split('\n') if l.startswith(r'\section{')]
print('new section order:')
for n, l in enumerate(order, 1):
    print('  %2d  %s' % (n, l))
