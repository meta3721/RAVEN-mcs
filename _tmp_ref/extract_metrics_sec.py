"""Extract the edited metrics subsection so the prose check can run on it alone."""
from pathlib import Path

t = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
i = t.index('Metrics and statistical policy')
marker = chr(92) + 'subsection{Risk Interchangeability'
j = t.index(marker, i)
Path('_tmp_ref/sec_metrics.tex').write_text(t[i:j], encoding='utf-8')
print('extracted %d chars, %d lines' % (j - i, t[i:j].count(chr(10))))
