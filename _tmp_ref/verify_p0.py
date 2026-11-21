"""Extract the edited protocol subsubsection for the prose check, and print the
rendered text of the four P0 edit sites."""
import re
from pathlib import Path

import pymupdf

bs = chr(92)
t = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
i = t.index(bs + 'subsubsection{Selection protocol and compared methods}')
j = t.index(bs + 'subsection{', i + 10)
Path('_tmp_ref/sec_protocol.tex').write_text(t[i:j], encoding='utf-8')
print('extracted protocol subsection: %d lines' % t[i:j].count(chr(10)))

d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
for label, snip, span in (
        ('abstract clause', 'protocol-constructed Complete-aligned', 300),
        ('protocol subsection', 'These layers are not measured in every block', 1700),
        ('main table caption', 'protocol-constructed', 240),
        ('limitation', 'protocol-constructed except', 220),
):
    hit = None
    for k in range(d.page_count):
        txt = d[k].get_text()
        pos = txt.find(snip)
        if pos >= 0:
            hit = (k + 1, txt[max(0, pos - 160):pos + span])
            break
    print()
    print('=== %s (page %s) ===' % (label, hit[0] if hit else 'NOT FOUND'))
    print(re.sub(r'\s+', ' ', hit[1]) if hit else 'not found')
