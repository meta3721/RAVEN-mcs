"""Extract the experimental-setup / dataset statements from refs 2 and 3."""
import re
import sys

import pymupdf

KEYS = ['dataset', 'data set', 'Data Set', 'Dataset', 'MNIST', 'CIFAR', 'FEMNIST',
        'Shakespeare', 'Sent140', 'StackOverflow', 'synthetic', 'U-Air', 'SensorScope',
        'taxi', 'Beijing', 'Shanghai', 'temperature', 'humidity', 'PM2.5',
        'training data', 'train', 'matrix factorization', 'samples', 'users']

for f in ('2.pdf', '3.pdf'):
    p = 'C:/Cursor/raven.mcs/参考文件/相关重要论文/' + f
    d = pymupdf.open(p)
    print('=' * 80)
    print('FILE %s : %d pages' % (f, d.page_count))
    print('=' * 80)
    for i in range(d.page_count):
        t = d[i].get_text()
        hits = [k for k in KEYS if k in t]
        if len(hits) >= 2:
            print('  page %2d  hits=%s' % (i + 1, ','.join(sorted(set(hits))[:8])))
    print()
    sys.stdout.flush()
