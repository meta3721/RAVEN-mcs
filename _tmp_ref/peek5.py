import re
from pathlib import Path

import pymupdf

D = Path('参考文件/相关重要论文')
for f in sorted(D.glob('*.pdf')):
    d = pymupdf.open(f)
    t = d[0].get_text()
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    print('=' * 78)
    print('FILE:', f.name, '| pages =', d.page_count, '| chars =', len(''.join(p.get_text() for p in d)))
    print('  first lines:')
    for l in lines[:14]:
        print('   ', l[:110])
    print()
