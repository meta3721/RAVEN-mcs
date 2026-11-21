"""Confirm each P0 edit in the rendered PDF (hyphenation-tolerant)."""
import re

import pymupdf

d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
pages = [d[i].get_text() for i in range(d.page_count)]
flat = [re.sub(r'-\n', '', re.sub(r'\s+', ' ', p)) for p in pages]

probes = {
    'abstract': 'protocol-constructed Complete-aligned selection',
    'protocol subsection': 'These layers are not measured in every block',
    'construction parameters': 'equal client mass and a factor',
    'O construction': 'Bernoulli at rate 0.35',
    'U construction': 'device-tier compute and network',
    'scoping sentence': 'conditional on it',
    'table caption': 'whose O and U layers are protocol-constructed',
    'limitation': 'protocol-constructed except Pilot 2 measured O',
}
for name, probe in probes.items():
    hit = next(((i + 1, flat[i]) for i in range(len(flat)) if probe in flat[i]), None)
    if hit:
        i, txt = hit
        k = txt.find(probe)
        print('[OK  ] p%-3d %-24s ...%s...' % (i, name, txt[max(0, k - 70):k + len(probe) + 90]))
    else:
        print('[MISS] %-24s (probe: %r)' % (name, probe))
