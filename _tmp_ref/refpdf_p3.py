"""Paper 3 (TMC 2026 federated data completion in sparse MCS): dataset section."""
import re

import pymupdf

d = pymupdf.open('C:/Cursor/raven.mcs/参考文件/相关重要论文/3.pdf')
for i in (11, 12, 13):
    t = d[i - 1].get_text()
    print('=' * 78)
    print('PAGE %d' % i)
    print('=' * 78)
    print(t[:4200])
    print()
