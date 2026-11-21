"""Reliable check of the regenerated bibliography (no shell escaping issues)."""
import re
from pathlib import Path

import pymupdf

bbl_path = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.bbl')
raw = bbl_path.read_bytes()
txt = raw.decode('utf-8', errors='replace')
print('main.bbl: %d bytes, mtime-ish len stable' % len(raw))
print('  literal "bibitem" occurrences: %d' % txt.count('bibitem'))
keys = re.findall(r'\\bibitem\{([^}]+)\}', txt)
print('  regex bibitem keys: %d' % len(keys))
if keys:
    print('   first:', keys[:3])
    print('   last :', keys[-3:])
else:
    i = txt.find('thebibliography')
    print('   context:', repr(txt[i:i + 300]))

ref = Path('TO_OVERLEAF_paper_tmc_r1_clean/reference.bib')
rtxt = ref.read_text(encoding='utf-8')
print('reference.bib: %d bytes, %d entries' % (len(rtxt.encode()), len(re.findall(r'@\w+\{', rtxt))))

log = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.log').read_text(encoding='utf-8', errors='replace')
print('main.log: undefined-citation lines =', len(re.findall(r'Citation .* undefined', log)),
      '| undefined-reference lines =', len(re.findall(r'Reference .* undefined', log)))

d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
last = d[d.page_count - 1].get_text()
print('last page ref numbers:', sorted({int(m) for m in re.findall(r'\[(\d{1,3})\]', last)})[-5:])
