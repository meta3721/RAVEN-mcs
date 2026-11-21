"""Step 1c — W1 design-gate figure cells and the std of every replaced cell.

Two conventions are tested against the frozen figure_data/FIG_W1_DESIGN_GATE.csv
so the corrected value keeps the same definition:

  ratio_of_means    100 * (mean(abl) - mean(full)) / mean(full)
  per_seed_mean     100 * mean_i (abl_i - full_i) / full_i

Series: RAVEN-Design and RAVEN-SimOracle from the E2 theta cells, RAVEN-NoDesign
from the E4 tree (clean arm, run-time value is already theta).  Also prints the
theta mean +/- std (ddof=1) for the seven replaced table cells.
"""
from __future__ import annotations

import csv
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
E4 = ROOT / 'artifacts/e4_core_mechanism_ablation_r1/runs/uair'
SEEDS = list(range(30001, 30021))


def series(path_col, arm, key):
    out = {}
    with (ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv').open() as fh:
        for row in csv.DictReader(fh):
            if row['method'] == arm:
                out[int(row['seed'])] = float(row[key])
    return np.asarray([out[s] for s in SEEDS])


def tree_series(arm, metric):
    import json
    vals = {}
    for s in SEEDS:
        p = E4 / arm / ('seed%d' % s) / 'final_metrics.json'
        vals[s] = json.loads(p.read_text())[metric]
    return np.asarray([vals[s] for s in SEEDS])


def main() -> None:
    design = series(None, 'raven', 'RMSE_mu_std')
    oracle = series(None, 'raven_simoracle', 'RMSE_mu_std')
    nodes = tree_series('raven_wo_design', 'RMSE_mu')
    dg_design, dg_oracle = series(None, 'raven', 'Delta_group'), series(None, 'raven_simoracle', 'Delta_group')
    dg_nodes = tree_series('raven_wo_design', 'Delta_group')

    for label, full in (('Estimated', design), ('Oracle', oracle)):
        rom = 100.0 * (full.mean() - nodes.mean()) / nodes.mean()
        psm = 100.0 * float(np.mean((full - nodes) / nodes))
        print('%-10s RMSE_mu_pct  ratio-of-means=%8.4f  per-seed-mean=%8.4f' % (label, rom, psm))
    for label, full in (('Estimated', dg_design), ('Oracle', dg_oracle)):
        rom = 100.0 * (full.mean() - dg_nodes.mean()) / dg_nodes.mean()
        psm = 100.0 * float(np.mean((full - dg_nodes) / dg_nodes))
        print('%-10s Delta_group  ratio-of-means=%8.4f  per-seed-mean=%8.4f  (printed CSV: %s)'
              % (label, rom, psm, '7.49898' if label == 'Estimated' else '7.47623'))

    print('\n--- replaced cells: old +/- -> new +/- (theta, ddof=1) ---')
    for arm, col in (('raven', 'RMSE_mu_std'), ('twostage_hajek', 'RMSE_mu_std'),
                     ('inst_cal', 'RMSE_mu_std'), ('local_hajek', 'RMSE_mu_std'),
                     ('raven_simoracle', 'RMSE_mu_std')):
        a = series(None, arm, col)
        print('%-18s %+.4f +/- %.4f' % (arm, a.mean(), a.std(ddof=1)))


if __name__ == '__main__':
    main()
