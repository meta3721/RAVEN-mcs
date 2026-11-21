"""Tighten \\shortstack numeric cells: remove the inter-column space before $\\pm$.

Only touches whitespace inside tabular cells. No character of any number,
symbol, or statistic is changed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

APX = Path('TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex')
MAIN = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex')

PAT = re.compile(r'\\\\\s+\$\\pm')      # '\\ $\pm'  ->  '\\$\pm'


def run(path: Path, apply: bool):
    t = path.read_text(encoding='utf-8')
    hits = PAT.findall(t)
    new = PAT.sub(r'\\\\$\\pm', t)
    print('  %-20s occurrences=%d  chars %d -> %d' % (path.name, len(hits), len(t), len(new)))
    if apply and new != t:
        path.write_text(new, encoding='utf-8')
        b = path.read_bytes()
        if b'\r\n' in b:
            path.write_bytes(b.replace(b'\r\n', b'\n'))


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    for p in (APX, MAIN):
        run(p, apply)
    print('  applied' if apply else '  (dry run)')
