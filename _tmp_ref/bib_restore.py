"""Restore reference.bib from the only backup whose key set matches the compiled
main.bbl (54 entries, incl. the INFOCOM correction). Aborts if it does not match."""
import re
import shutil
import sys
from pathlib import Path

DST = Path('TO_OVERLEAF_paper_tmc_r1_clean/reference.bib')
SRC = Path('_tmp_pack/7.26-vs-current-verification/current_paper/reference.bib')

bbl = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.bbl').read_text(encoding='utf-8', errors='replace')
bbl_keys = re.findall(r'\\bibitem\{([^}]+)\}', bbl)

src_txt = SRC.read_text(encoding='utf-8')
src_keys = re.findall(r'@\w+\{([^,]+),', src_txt)

print('main.bbl keys : %d' % len(bbl_keys))
print('candidate keys: %d' % len(src_keys))
missing = [k for k in bbl_keys if k not in set(src_keys)]
extra = [k for k in src_keys if k not in set(bbl_keys)]
print('missing from candidate: %s' % (missing or 'none'))
print('extra in candidate    : %s' % (extra or 'none'))

seg = re.search(r'@\w+\{wang2023transformer,(.*?)\n@', src_txt, re.S)
venue_ok = bool(seg and 'INFOCOM' in seg.group(1))
print('wang2023transformer -> INFOCOM: %s' % venue_ok)

if missing or extra or not venue_ok:
    sys.exit('ABORT: candidate is not an exact match for the compiled bibliography.')

print()
print('destination before: %d bytes' % DST.stat().st_size)
shutil.copyfile(SRC, DST)
print('destination after : %d bytes' % DST.stat().st_size)
print('RESTORED from %s' % SRC)
