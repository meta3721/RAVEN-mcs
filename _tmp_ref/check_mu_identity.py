"""Test the identity RMSE_mu^2 = sum_g mu_g * RMSE_g^2 using the paper's own
published numbers, and solve for the implied target masses mu.

Source: main.tex Table tab:main_effectiveness (RMSE_mu) and appendix.tex
Table tab:app_block_rmse (RMSE_g, g = 0..3 UTC blocks).
"""
import numpy as np

SS = {
    'FedAvg-Window':   (7.9389, [7.4912, 7.5873, 8.6716, 8.2084]),
    'TwoStage-Hajek':  (7.9309, [7.4831, 7.5795, 8.6633, 8.2004]),
    'FedAU-Window':    (7.9364, [7.4887, 7.5848, 8.6691, 8.2059]),
    'ObsUse-Window':   (7.9293, [7.4815, 7.5780, 8.6618, 8.1988]),
    'RAVEN-Design':    (7.9380, [7.4903, 7.5864, 8.6707, 8.2075]),
}
UA = {
    'FedAvg-Window':      (1.1882, [1.1751, 1.1922, 1.2596, 1.1521]),
    'TwoStage-Hajek':     (1.2160, [1.2009, 1.2194, 1.2907, 1.1800]),
    'FedAU-Window':       (1.1128, [1.1023, 1.1153, 1.1701, 1.0729]),
    'ObsUse-Window':      (1.1120, [1.1016, 1.1145, 1.1692, 1.0721]),
    'RAVEN-Design(forced)': (1.1911, [1.1779, 1.1953, 1.2630, 1.1552]),
    'RAVEN-NoDesign':     (1.1131, [1.1025, 1.1155, 1.1703, 1.0732]),
}

for name, tab in (('SensorScope', SS), ('U-Air', UA)):
    A = np.array([b for _, b in tab.values()], dtype=float) ** 2
    y = np.array([m for m, _ in tab.values()], dtype=float) ** 2
    print('=== %s ===  methods=%d' % (name, len(y)))
    print('  uniform mu guess (1/4 each): RMSE_mu implied = %s'
          % np.round(np.sqrt(A.mean(axis=1)), 4))
    print('  published RMSE_mu          = %s' % np.round(np.sqrt(y), 4))
    # constrained least squares: mu >= 0, sum mu = 1
    from scipy.optimize import nnls
    M = np.vstack([A, 1e3 * np.ones((1, 4))])
    r = np.concatenate([y, [1e3]])
    mu, res = nnls(M, r)
    pred = np.sqrt(A @ mu)
    print('  solved mu                  = %s   (sum %.6f)' % (np.round(mu, 4), mu.sum()))
    print('  RMSE_mu from solved mu     = %s' % np.round(pred, 4))
    print('  max abs residual           = %.5f' % np.max(np.abs(pred - np.sqrt(y))))
    print()
