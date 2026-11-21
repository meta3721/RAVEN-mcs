import re
from pathlib import Path

import pymupdf

d = pymupdf.open('参考文件/RAVEN_MCS_2026_7_26_.pdf')
pages = [p.get_text() for p in d]
full = '\n'.join(pages)
Path('_tmp_ref/jul26_plain.txt').write_text(full, encoding='utf-8')


def show(label, needle, ctx_before=1, ctx_after=3, limit=4):
    print('=' * 96)
    print(label, '| needle =', repr(needle))
    print('=' * 96)
    hits = 0
    for i, t in enumerate(pages):
        lines = t.splitlines()
        for j, ln in enumerate(lines):
            if needle.lower() in ln.lower():
                hits += 1
                seg = lines[max(0, j - ctx_before):j + ctx_after + 1]
                print('  --- PDF page %d, around line %d ---' % (i + 1, j + 1))
                for s in seg:
                    if s.strip():
                        print('    ', ' '.join(s.split())[:160])
                print()
                if hits >= limit:
                    return
    if not hits:
        print('  (no hit)\n')


show('A. Design 启用判据', 'Design')
show('B. 支持兼容性措辞', 'compatible')
show('C. 二阶漂移项', 'drift')
show('D. lambda_g 约束', 'dominates')
show('E. 目标风险收敛定理陈述', 'Theorem 3')
show('F. 可达性假设陈述', 'reachability')
