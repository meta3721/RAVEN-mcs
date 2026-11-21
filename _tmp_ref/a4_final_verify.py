"""A4 final verification: is the RMSE_mu weight actually uniform, and does the
four-block identity reproduce the published values?

Uses G2's own build_pack so the check is on the same object Table II used.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path('.').resolve()
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'post_review' / 'G2_external_baselines'))

from run_g2 import build_pack  # noqa: E402

# published Table II RMSE_mu (20-seed mean) and the supplement's four block scores
PUB = {
    'sensorscope': {'rmse_mu': 7.9389,
                    'blocks': [7.4912, 7.5873, 8.6716, 8.2084],  # FedAvg-Window
                    'method': 'FedAvg-Window'},
    'uair': {'rmse_mu': 1.1882,
             'blocks': [1.1751, 1.1922, 1.2596, 1.1521],
             'method': 'FedAvg-Window'},
}

for ds in ('sensorscope', 'uair'):
    print('=== %s ===' % ds.upper())
    pack = build_pack(ds)
    w = np.asarray(pack['mu_w'], dtype=np.float64)
    n = len(w)
    print('  n_test = %d' % n)
    print('  w: min=%.12g  max=%.12g  mean=%.12g' % (w.min(), w.max(), w.mean()))
    print('  w is uniform to 1e-12? %s   (spread = %.3g)'
          % (bool(w.max() - w.min() < 1e-12), w.max() - w.min()))
    print('  => weight per unit is 1/N: %s' % (abs(w.mean() - 1.0 / n) < 1e-12))
    bc = pack['block_counts']
    print('  four-block test counts: %s  (total %d)' % (bc, sum(bc.values())))
    bl = PUB[ds]['blocks']
    pred = float(np.sqrt(sum((bc[g] / n) * bl[g] ** 2 for g in range(4))))
    print('  published RMSE_mu            = %.4f' % PUB[ds]['rmse_mu'])
    print('  sqrt(sum_g (n_g/N) RMSE_g^2) = %.4f   (delta %+.4f)'
          % (pred, pred - PUB[ds]['rmse_mu']))
    flat = float(np.sqrt(sum(0.25 * x ** 2 for x in bl)))
    print('  uniform-1/4 weighting would give %.4f  -> published is %s'
          % (flat, 'below' if PUB[ds]['rmse_mu'] < flat else 'above'))
    print()
