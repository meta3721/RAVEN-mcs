"""Context dump around dataset mentions."""
import re

import pymupdf

def ctx(f, pages, pattern, width=420):
    p = 'C:/Cursor/raven.mcs/参考文件/相关重要论文/' + f
    d = pymupdf.open(p)
    for i in pages:
        t = d[i - 1].get_text()
        for m in re.finditer(pattern, t):
            a = max(0, m.start() - width // 2)
            seg = t[a:m.start() + width].replace('\n', ' ')
            seg = re.sub(r'\s+', ' ', seg)
            print('[p%d] ...%s...' % (i, seg))
            print()

print('########## 2.pdf : dataset identification ##########')
ctx('2.pdf', [8, 9], r'CIFAR|datasets? (?:used|are|is)|we (?:use|consider|adopt)|generated? (?:data|synthetic)', 400)
print('########## 2.pdf : appendix dataset section ##########')
ctx('2.pdf', [30, 31], r'dataset|CIFAR|synthetic', 400)
