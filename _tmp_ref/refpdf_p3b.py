"""Paper 3: locate and print the dataset/experiment description."""
import re

import pymupdf

d = pymupdf.open('C:/Cursor/raven.mcs/参考文件/相关重要论文/3.pdf')
for i in range(d.page_count):
    t = d[i].get_text()
    for kw in ('U-Air', 'PM2.5', 'Dataset', 'datasets'):
        for m in re.finditer(re.escape(kw), t):
            a = max(0, m.start() - 300)
            seg = re.sub(r'\s+', ' ', t[a:m.start() + 500])
            print('[p%d | %s] ...%s...' % (i + 1, kw, seg))
            print()
            break
