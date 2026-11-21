import re
from pathlib import Path

jul = Path('_tmp_ref/jul26_full.txt').read_text(encoding='utf-8')
cur = Path('TO_OVERLEAF_paper_tmc_r1_clean/main.tex').read_text(encoding='utf-8')
apx = Path('TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex').read_text(encoding='utf-8')
curall = cur + '\n' + apx

PROBES = [
    # structural / theoretical machinery
    ('Lyapunov', 'Lyapunov drift analysis'),
    ('Approximate window reachability', 'window reachability assumption'),
    ('epsilon_reach', 'reachability slack'),
    ('Target-Risk Convergence', 'target-risk convergence theorem'),
    ('Per-Window Target-Gradient Bias', 'per-window gradient bias'),
    ('Local Update Decomposition', 'local update decomposition'),
    ('Aggregate Update Variance', 'aggregate variance bound'),
    ('conditional centering', 'conditional centering argument'),
    ('corrected client', 'corrected client-record composition'),
    ('pair-distribution', 'pair-distribution error'),
    # selection / gating
    ('support-compatible', 'support-compatibility language'),
    ('25.5', 'the 25.5% figure'),
    ('51.6', 'A_r overlap figure'),
    ('design ratio', 'design-ratio estimation'),
    ('oracle design', 'oracle design condition'),
    # risk semantics
    ('Target-Risk', 'target-RISK framing'),
    ('Target-Mass', 'target-MASS framing'),
    # registration / U layer
    ('registration', 'attempt registration'),
    ('P2 information boundary', 'P2 info boundary'),
    # datasets
    ('T-Drive-Speed', 'T-Drive-Speed'),
    ('SensorScope', 'SensorScope'),
    ('reachability audit', 'reachability audit'),
    ('Compared Methods', 'compared methods section'),
    # evaluation
    ('Holm', 'Holm correction'),
    ('Wilcoxon', 'Wilcoxon'),
    ('pre-registered', 'pre-registration'),
    ('non-inferior', 'non-inferiority rule'),
    ('Cliff', 'effect size'),
    ('bootstrap', 'bootstrap CI'),
]

print('%-34s %-10s %-10s' % ('probe', 'JUL26', 'CURRENT'))
print('-' * 60)
for probe, label in PROBES:
    a = jul.lower().count(probe.lower())
    b = curall.lower().count(probe.lower())
    flag = ''
    if a and not b:
        flag = '  <-- present in JUL26, ABSENT now'
    elif b and not a:
        flag = '  <-- NEW in current'
    print('%-34s %-10d %-10d%s' % (label, a, b, flag))
