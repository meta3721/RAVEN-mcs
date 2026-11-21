"""Print the rendered text of the three edited sites."""
import pymupdf

d = pymupdf.open('TO_OVERLEAF_paper_tmc_r1_clean/main.pdf')

def find(snippet, span=900):
    for i in range(d.page_count):
        t = d[i].get_text()
        k = t.find(snippet)
        if k >= 0:
            return i + 1, t[k:k + span]
    return None, None

for label, snip, span in (
        ('VII-A.1 group map', 'deployment-group mapping', 620),
        ('VII-A.3 metrics', 'Prediction is measured on the supported test', 1500),
        ('Table III header', 'WG blocks', 260),
        ('under-served symbol', 'arg max', 320),
):
    pg, txt = find(snip, span)
    print('=== %s === (page %s)' % (label, pg))
    print(txt if txt else 'NOT FOUND')
    print()
