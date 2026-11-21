"""Extract the subsection containing the Delta_group definition for the prose check."""
from pathlib import Path

t = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
bs = chr(92)
i = t.index(bs + 'subsection{Structural Alignment Objective}')
j = t.index(bs + 'subsection{', i + 10)
Path('_tmp_ref/sec_delta_group.tex').write_text(t[i:j], encoding='utf-8')
print('extracted %d lines' % t[i:j].count(chr(10)))
