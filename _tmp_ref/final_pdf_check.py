import pymupdf
for f in ('main', 'supplemental'):
    d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/%s.pdf' % f)
    n = sum(d[i].get_text().count('??') for i in range(d.page_count))
    print('%-14s pages=%d  unresolved "??"=%d' % (f, d.page_count, n))
