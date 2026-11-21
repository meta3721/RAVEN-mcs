"""Markdown table hygiene check for the diagnostic record.

A raw '|' inside a table cell splits the row in GFM.  For every contiguous block
of table rows, report lines whose unescaped pipe count differs from the block's
first line, and list every occurrence of an unescaped '|' that is not a cell
separator (heuristic: a pipe with no space on at least one side, inside a code
span, or adjacent to a word character on both sides).
"""
from __future__ import annotations

import pathlib
import re
import sys

PATH = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                    'ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md')


def unescaped_count(line: str) -> int:
    return len(re.findall(r'(?<!\\)\|', line))


def main() -> None:
    lines = PATH.read_text(encoding='utf-8').split('\n')
    bad = []
    block = []
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith('|'):
            block.append((i, line))
            continue
        if block:
            check(block, bad)
            block = []
    if block:
        check(block, bad)
    print('table rows with a pipe-count mismatch: %d' % len(bad))
    for i, line, n, ref in bad:
        print('  line %d: %d unescaped pipes (block reference %d)\n    %s' % (i, n, ref, line[:160]))
    suspicious = [(i, line) for i, line in enumerate(lines, 1)
                  if line.lstrip().startswith('|')
                  and re.search(r'(?<!\\)\|(?=[^\s|])', line.replace('\\|', ''))]
    print('rows containing a pipe glued to a word character: %d' % len(suspicious))
    for i, line in suspicious[:20]:
        print('  line %d: %s' % (i, line[:160]))


def check(block, bad):
    ref = None
    for _, line in block[:2]:
        if re.match(r'^\|[\s:|-]+\|\s*$', line):
            ref = unescaped_count(line)
    if ref is None:
        ref = unescaped_count(block[0][1])
    for i, line in block:
        n = unescaped_count(line)
        if n != ref:
            bad.append((i, line, n, ref))


if __name__ == '__main__':
    main()
