"""Assess reference.bib loss: what git holds, which backup is current, and what
the compiled .bbl implies the target content is."""
import re
import subprocess
from pathlib import Path

TARGET = Path('TO_OVERLEAF_paper_tmc_r1_clean/reference.bib')

print('=== git state for %s ===' % TARGET)
for cmd in (['git', 'log', '--oneline', '-3', '--', str(TARGET)],
            ['git', 'diff', '--stat', '--', str(TARGET)],
            ['git', 'status', '--short', '--', str(TARGET)]):
    r = subprocess.run(cmd, capture_output=True, text=True)
    print('  $ %s' % ' '.join(cmd))
    print('   ', (r.stdout or r.stderr).strip() or '(no output)')

head = subprocess.run(['git', 'show', 'HEAD:%s' % TARGET.as_posix()],
                      capture_output=True, text=True)
head_txt = head.stdout if head.returncode == 0 else ''
print('  HEAD version: %d bytes' % len(head_txt))


def entries(txt):
    return re.findall(r'@\w+\{([^,]+),', txt)


def info(key, txt):
    m = re.search(r'@\w+\{%s,(.*?)\n@' % re.escape(key), txt, re.S)
    return m.group(1) if m else None


cands = {
    'git HEAD': head_txt,
    '_tmp_pack/7.26-vs-current-verification/current_paper': Path('_tmp_pack/7.26-vs-current-verification/current_paper/reference.bib').read_text(encoding='utf-8', errors='replace'),
    'RAVEN_MCS_TMC_r1_overleaf/raven_mcs_tmc_r1': Path('RAVEN_MCS_TMC_r1_overleaf/raven_mcs_tmc_r1/reference.bib').read_text(encoding='utf-8', errors='replace'),
    '_paper_work': Path('_paper_work/reference.bib').read_text(encoding='utf-8', errors='replace'),
    'deliverables/.../TO_OVERLEAF_paper_tmc_r1_clean': Path('deliverables/TO_SUBMIT_TMC_PAPER_AND_PRACTICE_R1/RAVEN_MCS_TMC_PAPER_OVERLEAF_R1/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib').read_text(encoding='utf-8', errors='replace'),
}
print()
print('%-58s %7s %6s  %s' % ('candidate', 'bytes', 'keys', 'wang2023transformer venue'))
for name, txt in cands.items():
    e = entries(txt)
    seg = info('wang2023transformer', txt) or ''
    venue = 'INFOCOM' if 'INFOCOM' in seg else ('CSUR' if 'Computing Surveys' in seg or 'CSUR' in seg else '?')
    print('%-58s %7d %6d  %s' % (name, len(txt), len(e), venue))

print()
print('=== main.bbl entry count (what the compiled PDF shows) ===')
bbl = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.bbl').read_text(encoding='utf-8', errors='replace')
bkeys = re.findall(r'\\bibitem\{([^}]+)\}', bbl)
print('  %d bibitems' % len(bkeys))
print('  first:', bkeys[:3], '... last:', bkeys[-3:])

print()
print('=== does the PDF still render a full reference list? ===')
import pymupdf
d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')
t = d[d.page_count - 1].get_text() + d[d.page_count - 2].get_text()
nums = sorted({int(m) for m in re.findall(r'\[(\d{1,3})\]', t)})
print('  page count %d; highest bracketed ref seen on last two pages: %s' % (d.page_count, max(nums) if nums else 'none'))
