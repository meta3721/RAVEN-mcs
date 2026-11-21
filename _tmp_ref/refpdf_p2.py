"""Print the experimental-setup sections of refs 2 and 3."""
import sys

import pymupdf

def dump(f, pages, budget=3800):
    p = 'C:/Cursor/raven.mcs/参考文件/相关重要论文/' + f
    d = pymupdf.open(p)
    print('#' * 80)
    print('# %s pages %s' % (f, pages))
    print('#' * 80)
    for i in pages:
        t = d[i - 1].get_text()
        print('----- page %d -----' % i)
        print(t[:budget])
        print()
        sys.stdout.flush()

dump('2.pdf', [7, 8])
