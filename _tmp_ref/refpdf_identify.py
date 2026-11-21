"""Identify papers 2 and 3 and locate their training-data statements."""
import sys

import pymupdf

for f in ('2.pdf', '3.pdf'):
    p = 'C:/Cursor/raven.mcs/参考文件/相关重要论文/' + f
    d = pymupdf.open(p)
    print('=' * 78)
    print('%s : %d pages' % (f, d.page_count))
    print('=' * 78)
    t = d[0].get_text()
    print(t[:1500])
    print()
    sys.stdout.flush()
