import re
from pathlib import Path

import pymupdf

JUL = '参考文件/RAVEN_MCS_2026_7_26_.pdf'
d = pymupdf.open(JUL)
pages = [p.get_text() for p in d]


def find_jul(needle, maxhits=3, ctx=0):
    """Return (page, line, snippet) for each hit in the July PDF."""
    out = []
    for i, t in enumerate(pages):
        lines = t.splitlines()
        for j, ln in enumerate(lines):
            if needle.lower() in ln.lower():
                seg = ' '.join(lines[max(0, j - ctx):j + ctx + 1])
                out.append((i + 1, j + 1, ' '.join(seg.split())[:230]))
                if len(out) >= maxhits:
                    return out
    return out


def find_cur(path, needle, maxhits=3):
    p = Path(path)
    lines = p.read_text(encoding='utf-8').split('\n')
    out = []
    for i, ln in enumerate(lines, 1):
        if needle.lower() in ln.lower():
            out.append((p.name, i, ln.strip()[:200]))
            if len(out) >= maxhits:
                break
    return out


ITEMS = [
    ('TITLE', 'Target-Risk-Calibrated'),
    ('TITLE', 'Target-Mass-Calibrated'),
    ('ACRONYM', 'Risk Alignment Via Exposure-aware'),
    ('ACRONYM', 'Reference Alignment Via Exposure-aware'),
    ('LYAPUNOV', 'Lyapunov function'),
    ('DRIFT', 'debt drift satisfies'),
    ('LAMBDA_G', 'lambda_g'),
    ('REACHABILITY', 'Approximate window reachability'),
    ('EPS_REACH', 'reach'),
    ('TR_CONV', 'Target-Risk Convergence'),
    ('GRAD_BIAS', 'Target-gradient bias'),
    ('VAR_BOUND', 'Aggregate variance bound'),
    ('COND_CENTER', 'conditional centering'),
    ('SUPPORT_COMPAT', 'support-compatible'),
    ('PCT_255', '25.5'),
    ('OVERLAP', '51.6'),
    ('TDRIVE_SPEED', 'T-Drive-Speed'),
    ('DESIGN_BRANCH', 'Design is applied'),
]

print('=' * 100)
print('JULY 26 PDF locations')
print('=' * 100)
for tag, needle in ITEMS:
    hits = find_jul(needle)
    print('\n[%s] needle=%r' % (tag, needle))
    for pg, ln, snip in hits:
        print('   p%-3d line %-4d %s' % (pg, ln, snip))
    if not hits:
        print('   (no hit)')

print()
print('=' * 100)
print('CURRENT version locations (main.tex / appendix.tex)')
print('=' * 100)
for tag, needle in ITEMS:
    hits = find_cur('TO_OVERLEAF_paper_tmc_r1_clean/main.tex', needle)
    hits2 = find_cur('TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex', needle, 2)
    print('\n[%s]' % tag)
    for h in hits + hits2:
        print('   %-14s L%-5d %s' % h)
    if not (hits or hits2):
        print('   (no hit)')
