import re
from pathlib import Path

main = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8').split('\n')
apx = Path('TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex').read_text(encoding='utf-8').split('\n')

CLAIMS = [
    ('main.tex', 55, r'\\title\{RAVEN-MCS: Target-Mass-Calibrated'),
    ('main.tex', 148, r'Reference Alignment Via Exposure-aware'),
    ('main.tex', 618, r'Reference Alignment Via Exposure-aware'),
    ('main.tex', 924, r'\\frac\{\\lambda_g\}\{2\}'),
    ('main.tex', 1086, r'\\lambda_g,\\lambda_v,\\lambda_s'),
    ('main.tex', 1149, r'Normalized target reconstruction'),
    ('main.tex', 1198, r'Unique solution of the calibration program'),
    ('main.tex', 1230, r'Practical plug-in perturbation'),
    ('main.tex', 1470, r'support-compatible'),
    ('main.tex', 1850, r'25\.5\\%'),
    ('main.tex', 1853, r'51\.6\\%'),
    ('main.tex', 1926, r'25\.5\\%'),
    ('appendix.tex', 2161, r'25\.5\\%'),
    ('appendix.tex', 2174, r'25\.5\\%'),
]

print('=== verify line-number claims (README) ===')
ok = 0
bad = []
for fname, ln, pat in CLAIMS:
    src = main if fname == 'main.tex' else apx
    if ln - 1 < len(src):
        line = src[ln - 1]
        hit = re.search(pat, line) is not None
        # also allow +-3 lines
        near = any(re.search(pat, src[k]) for k in range(max(0, ln - 4), min(len(src), ln + 3)))
        status = 'EXACT' if hit else ('NEAR' if near else 'MISS')
        if status == 'EXACT':
            ok += 1
        else:
            bad.append((fname, ln, status, line.strip()[:90]))
        print('  %-13s L%-5d %-6s %s' % (fname, ln, status, line.strip()[:80]))
    else:
        bad.append((fname, ln, 'OUT_OF_RANGE', ''))
        print('  %-13s L%-5d OUT_OF_RANGE' % (fname, ln))

print()
print('  exact hits: %d / %d' % (ok, len(CLAIMS)))
if bad:
    print('  needs fixing:')
    for b in bad:
        print('   ', b)

# also resolve any NEAR/MISS by searching
print()
print('=== auto-locate correct lines for the misses ===')
for fname, ln, pat in CLAIMS:
    src = main if fname == 'main.tex' else apx
    hits = [i + 1 for i, l in enumerate(src) if re.search(pat, l)]
    if hits and ln not in hits:
        print('  %-13s claimed L%-5d -> actual %s' % (fname, ln, hits[:5]))
