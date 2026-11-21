"""Step 1f — resample the three affected figure_data files to the theta copy.

  FIG_W1_DESIGN_GATE.csv            U-Air RMSE_mu_pct (Estimated, Oracle)
  FIG_E4_E4_COMPONENT_ABLATION.csv  U-Air rows: Design/Obs/Use/Inst/Debt x
                                    {RMSE_mu, Tail_RMSE}
  FIG_E3_E3_PREDICTION_RISK.csv     U-Air rows of the nine affected E3 arms at
                                    seeds 30007/30016/30018: RMSE_mu, Tail_RMSE

Only the listed cells change; every other row and column is copied verbatim.
Originals are preserved in snapshots/2026-09-29-pre-theta-resource/.
"""
from __future__ import annotations

import csv
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FIGD = ROOT / 'TO_OVERLEAF_paper_tmc_r1_clean/figure_data'
E4 = ROOT / 'artifacts/e4_core_mechanism_ablation_r1/runs/uair'
SEEDS = list(range(30001, 30021))
TRIGGERED = (30007, 30016, 30018)
NAME2ARM = {'RAVEN-MCS': 'raven', 'RAVEN-SimOracle': 'raven_simoracle',
            'TwoStage-Hajek': 'twostage_hajek', 'Local-Hajek': 'local_hajek',
            'Inst-Cal': 'inst_cal', 'Debt-Cal': 'debt_cal',
            'FedAvg-Window': 'fedavg_window', 'FedAsync-Window': 'fedasync_window',
            'TimeAlign-Agg': 'flamf_timealign_adapted'}


def read(path):
    with path.open(newline='', encoding='utf-8') as fh:
        r = csv.DictReader(fh)
        return list(r), r.fieldnames


def write(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def num(v):
    return repr(float(v))


def direction(mean_diff):
    if mean_diff > 1e-12:
        return 'worsened'
    if mean_diff < -1e-12:
        return 'improved'
    return 'tie'


def magnitude(rel):
    a = abs(rel)
    if a < 1e-3:
        return 'quantitatively_small'
    if a < 1e-2:
        return 'small'
    return 'moderate_or_larger'


def series_from_e2(arm, col):
    out = {}
    with (ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv').open() as fh:
        for row in csv.DictReader(fh):
            if row['method'] == arm:
                out[int(row['seed'])] = float(row[col])
    return out


def tail_theta():
    """Tail_RMSE at the triggered seeds for the nine affected E3 arms."""
    out = {}
    with (HERE / 'C_IMPACT_RECALC.csv').open() as fh:
        for row in csv.DictReader(fh):
            if row['tree'] == 'e3':
                out.setdefault(row['arm'], {})[int(row['seed'])] = float(row['Tail_RMSE'])
    with (HERE / 'C7_E3_ARMS_THETA.csv').open() as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row['arm'], {})[int(row['seed'])] = float(row['Tail_RMSE'])
    return out


def main() -> None:
    changes = []

    # ---------- FIG_W1_DESIGN_GATE.csv ----------
    path = FIGD / 'FIG_W1_DESIGN_GATE.csv'
    rows, fields = read(path)
    design = np.asarray([series_from_e2('raven', 'RMSE_mu_std')[s] for s in SEEDS])
    oracle = np.asarray([series_from_e2('raven_simoracle', 'RMSE_mu_std')[s] for s in SEEDS])
    nodes = np.asarray([json.loads((E4 / 'raven_wo_design' / ('seed%d' % s) / 'final_metrics.json')
                                    .read_text())['RMSE_mu'] for s in SEEDS])
    for row in rows:
        if row['dataset'] != 'U-Air':
            continue
        full = design if row['variant'] == 'Estimated' else oracle
        new = 100.0 * float(np.mean((full - nodes) / nodes))
        changes.append(('FIG_W1_DESIGN_GATE.csv', '%s/%s' % (row['dataset'], row['variant']),
                        'RMSE_mu_pct', row['RMSE_mu_pct'], num(new)))
        row['RMSE_mu_pct'] = num(new)
    write(path, rows, fields)

    # ---------- FIG_E4_E4_COMPONENT_ABLATION.csv ----------
    path = FIGD / 'FIG_E4_E4_COMPONENT_ABLATION.csv'
    rows, fields = read(path)
    stats = {}
    with (HERE / 'C4_T4_STATS.csv').open() as fh:
        for row in csv.DictReader(fh):
            stats[(row['component'], row['metric'])] = row
    for row in rows:
        if row['dataset'] != 'U-Air' or row['metric'] not in ('RMSE_mu', 'Tail_RMSE'):
            continue
        st = stats[(row['component'], row['metric'])]
        mapped = {'relative_change_percent': st['relative_pct'],
                  'paired_mean_difference': st['mean_diff'],
                  'Holm_p': st['Holm_p'],
                  'holm_significant': st['holm_significant'],
                  'direction': direction(float(st['mean_diff'])),
                  'qualitative_magnitude': magnitude(float(st['relative_pct']) / 100.0)}
        for col, new in mapped.items():
            if col in ('relative_change_percent', 'paired_mean_difference', 'Holm_p'):
                new = num(new)
            if row[col] != new:
                changes.append(('FIG_E4_E4_COMPONENT_ABLATION.csv',
                                '%s/%s/%s' % (row['dataset'], row['component'], row['metric']),
                                col, row[col], new))
                row[col] = new
    write(path, rows, fields)

    # ---------- FIG_E3_E3_PREDICTION_RISK.csv ----------
    path = FIGD / 'FIG_E3_E3_PREDICTION_RISK.csv'
    rows, fields = read(path)
    rmse_theta = {arm: series_from_e2(arm, 'RMSE_mu_std') for arm in NAME2ARM.values()}
    tail = tail_theta()
    for row in rows:
        if row['dataset'] != 'U-Air' or row['method'] not in NAME2ARM:
            continue
        seed = int(row['seed'])
        if seed not in TRIGGERED:
            continue
        arm = NAME2ARM[row['method']]
        for col, value in (('RMSE_mu', rmse_theta[arm][seed]), ('Tail_RMSE', tail[arm][seed])):
            new = num(value)
            if row[col] != new:
                changes.append(('FIG_E3_E3_PREDICTION_RISK.csv', '%s/%s' % (row['method'], seed),
                                col, row[col], new))
                row[col] = new
    write(path, rows, fields)

    print('%d cells changed' % len(changes))
    for c in changes:
        print('%-34s %-24s %-26s %-22s -> %s' % c)


if __name__ == '__main__':
    main()
