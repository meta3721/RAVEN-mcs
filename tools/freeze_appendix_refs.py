"""Make appendix.tex self-contained: replace every cross-document \\ref/\\eqref
with the literal number taken from main.aux, so the supplement compiles alone.

Usage:
    python tools/freeze_appendix_refs.py --check    # report what would change
    python tools/freeze_appendix_refs.py --apply    # write appendix.tex
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] if (Path(__file__).resolve().parent.name == 'tools') else Path('.')
MAIN = ROOT / 'TO_OVERLEAF_paper_tmc_r1_clean' / 'main.tex'
APX = ROOT / 'TO_OVERLEAF_paper_tmc_r1_clean' / 'appendix.tex'
AUX = ROOT / 'TO_OVERLEAF_paper_tmc_r1_clean' / 'main.aux'

REF_RE = re.compile(r'\\(ref|eqref)\{([^}]+)\}')

# \newlabel{key}{{<number>}{<page>}{<title>}{<anchor>}{}} where <number> may
# itself contain braces, e.g. {\mbox  {III-D}} for subsections.
NEWLABEL_RE = re.compile(r'\\newlabel\{([^}]+)\}\{\{((?:[^{}]|\{[^{}]*\})*)\}\{')


def load_aux(path: Path) -> dict[str, str]:
    if not path.is_file():
        sys.exit('ERROR: %s not found. Compile main.tex first (pdflatex main.tex).' % path)
    txt = path.read_text(encoding='utf-8', errors='replace')
    out = {}
    for m in NEWLABEL_RE.finditer(txt):
        out[m.group(1)] = ' '.join(m.group(2).split())
    return out


def convert(apx_text: str, main_labels: set[str], numbers: dict[str, str]):
    apx_labels = set(re.findall(r'\\label\{([^}]+)\}', apx_text))
    changes, missing, kept = [], [], []

    def sub(m):
        kind, key = m.group(1), m.group(2)
        if key in apx_labels:            # internal to the appendix: keep dynamic
            kept.append(key)
            return m.group(0)
        if key not in main_labels:
            missing.append(key)
            return m.group(0)
        num = numbers.get(key)
        if num is None:
            missing.append(key)
            return m.group(0)
        literal = '(%s)' % num if kind == 'eqref' else num
        changes.append((kind, key, num))
        return literal

    new = REF_RE.sub(sub, apx_text)
    return new, changes, missing, kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    if not (args.check or args.apply):
        ap.error('pass --check or --apply')

    numbers = load_aux(AUX)
    main_text = MAIN.read_text(encoding='utf-8')
    apx_text = APX.read_text(encoding='utf-8')
    main_labels = set(re.findall(r'\\label\{([^}]+)\}', main_text))

    new, changes, missing, kept = convert(apx_text, main_labels, numbers)

    print('main.aux labels            :', len(numbers))
    print('appendix cross-refs frozen :', len(changes))
    print('appendix-internal refs kept:', len(kept))
    print('unresolvable refs          :', len(missing))
    if missing:
        for k in sorted(set(missing)):
            print('   !! %s' % k)
    print()
    print('sample conversions:')
    seen = set()
    for kind, key, num in changes:
        if key in seen:
            continue
        seen.add(key)
        print('   %-10s %-34s -> %s' % ('\\' + kind, key, num))
        if len(seen) >= 12:
            break

    if args.apply:
        APX.write_text(new, encoding='utf-8')
        print()
        print('WROTE', APX)
        # normalise to LF to respect the repo policy
        b = APX.read_bytes()
        if b'\r\n' in b:
            APX.write_bytes(b.replace(b'\r\n', b'\n'))
            print('normalised line endings to LF')


if __name__ == '__main__':
    main()
