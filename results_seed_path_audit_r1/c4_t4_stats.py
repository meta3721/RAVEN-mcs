"""Step 1b — corrected Table IV statistics (per-seed paired, Holm within family).

Rebuilds the five U-Air component-removal rows at the theta copy:

  full      RAVEN-MCS            (E3 tree, RMSE from E2 theta cells)
  Design    raven_wo_design      (clean arm: run-time value already theta)
  Obs/Use   raven_wo_{obs,use}   (E4 tree + theta override at 30007/30016/30018)
  Inst      gen-2 w/o-Inst       (corrective reruns + theta override)
  Debt      raven_wo_debt        (E4 tree + theta override)

Family = (dataset, metric) across the five components, matching e4_stats.py.
Writes C4_T4_STATS.csv.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

import numpy as np
from scipy.stats import wilcoxon

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SEEDS = list(range(30001, 30021))
TRIGGERED = (30007, 30016, 30018)
E3 = ROOT / 'artifacts/e3_formal_runs_r1/runs/uair'
E4 = ROOT / 'artifacts/e4_core_mechanism_ablation_r1/runs/uair'
GEN2 = (ROOT / 'artifacts/e4_wo_inst_reference_penalty_final_correction_r1'
        '/final_corrective_runs/uair/raven_wo_inst')


def frozen(base, arm):
    out = {}
    for s in SEEDS:
        p = base / arm / ('seed%d' % s) / 'final_metrics.json'
        if p.is_file():
            j = json.loads(p.read_text())
            for k, v in j.items():
                if isinstance(v, (int, float)):
                    out.setdefault(k, {})[s] = float(v)
    return out


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        val = (m - rank) * pvals[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj


def main() -> None:
    e2 = {}
    for row in csv.DictReader((ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv').open()):
        rec = {}
        for key, col in (('RMSE_mu', 'RMSE_mu_std'), ('Delta_group', 'Delta_group'), ('Delta_c_s', 'Delta_c_s')):
            raw = (row.get(col) or '').strip()
            if raw:
                rec[key] = float(raw)
        e2.setdefault(row['method'], {})[int(row['seed'])] = rec
    ovr: dict[str, dict[int, dict[str, float]]] = {}
    for row in csv.DictReader((HERE / 'C_IMPACT_RECALC.csv').open()):
        ovr.setdefault(row['arm'], {})[int(row['seed'])] = {
            'RMSE_mu': float(row['RMSE_mu']), 'Tail_RMSE': float(row['Tail_RMSE'])}

    def series(base, arm, metric, use_override=True, use_e2=True):
        vals = dict(frozen(base, arm).get(metric, {}))
        if use_override and arm in ovr and metric in ('RMSE_mu', 'Tail_RMSE'):
            for s in TRIGGERED:
                if s in vals:
                    vals[s] = ovr[arm][s][metric]
        if use_e2 and arm in e2 and metric in ('RMSE_mu', 'Delta_group', 'Delta_c_s'):
            for s in SEEDS:
                if s in e2[arm]:
                    vals[s] = e2[arm][s][metric]
        return np.asarray([vals.get(s, np.nan) for s in SEEDS], dtype=float)

    gen2_theta = {int(k): v for k, v in json.loads(
        (HERE / 'C3_CELL_DIFF.json').read_text())['gen2_theta_triggered'].items()}

    def gen2_series(metric):
        vals = dict(frozen(GEN2.parent, 'raven_wo_inst').get(metric, {}))
        for s in TRIGGERED:
            if s in vals and metric in gen2_theta[s]:
                vals[s] = gen2_theta[s][metric]
        return np.asarray([vals.get(s, np.nan) for s in SEEDS], dtype=float)

    comps = {
        'Design': lambda m: series(E4, 'raven_wo_design', m),
        'Obs': lambda m: series(E4, 'raven_wo_obs', m),
        'Use': lambda m: series(E4, 'raven_wo_use', m),
        'Inst': lambda m: gen2_series(m),
        'Debt': lambda m: series(E4, 'raven_wo_debt', m),
    }
    metrics = ('Delta_group', 'Delta_c_s', 'RMSE_mu', 'Tail_RMSE')
    rows = []
    for metric in metrics:
        full = series(E3, 'raven', metric)
        pvals, pending = [], []
        for comp, fn in comps.items():
            abl = fn(metric)
            d = abl - full
            rel = 100.0 * (np.nanmean(abl) - np.nanmean(full)) / np.nanmean(full)
            stat, p = wilcoxon(d)
            pending.append({'component': comp, 'relative_pct': rel, 'mean_diff': float(np.nanmean(d)),
                            'raw_p': float(p), 'stat': float(stat),
                            'full_mean': float(np.nanmean(full)), 'abl_mean': float(np.nanmean(abl)),
                            'wins': int(np.sum(d > 0)), 'losses': int(np.sum(d < 0))})
            pvals.append(p)
        adj = holm(np.asarray(pvals))
        for rec, a in zip(pending, adj):
            rec['Holm_p'] = float(a)
            rec['holm_significant'] = bool(a < 0.05)
            rec['metric'] = metric
            rows.append(rec)

    printed = {('Design', 'Delta_group'): -6.943368495586542, ('Design', 'Delta_c_s'): 4.9898350597219965,
               ('Design', 'RMSE_mu'): -6.553093815666225, ('Design', 'Tail_RMSE'): -6.875242584162889,
               ('Obs', 'Delta_group'): 0.1230828111266689, ('Obs', 'Delta_c_s'): 0.0219984512770321,
               ('Obs', 'RMSE_mu'): -0.0097196306106393, ('Obs', 'Tail_RMSE'): -0.0102288937108689,
               ('Use', 'Delta_group'): 0.0137939238456002, ('Use', 'Delta_c_s'): -0.0135605115759798,
               ('Use', 'RMSE_mu'): 0.023973670577847, ('Use', 'Tail_RMSE'): 0.0252184289979606,
               ('Inst', 'Delta_group'): -0.0894468167512562, ('Inst', 'Delta_c_s'): -0.1428586189549358,
               ('Inst', 'RMSE_mu'): 0.1306837550913353, ('Inst', 'Tail_RMSE'): 0.1363753990751629,
               ('Debt', 'Delta_group'): 0.0043063951349345, ('Debt', 'Delta_c_s'): 0.0023896482868883,
               ('Debt', 'RMSE_mu'): 0.0007291917853553, ('Debt', 'Tail_RMSE'): 0.000775232954355}
    for r in rows:
        r['printed_old'] = printed.get((r['component'], r['metric']))

    with (HERE / 'C4_T4_STATS.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print('%-10s %-14s %12s %12s %8s %10s %5s %6s' %
          ('component', 'metric', 'printed_old', 'corrected', 'changes', 'Holm_p', 'sig', 'wins'))
    for r in rows:
        old = r['printed_old']
        chg = '' if old is None else ('YES' if round(old, 3) != round(r['relative_pct'], 3) else 'no')
        print('%-10s %-14s %12.6f %12.6f %8s %10.6f %5s %6d' %
              (r['component'], r['metric'], old if old is not None else float('nan'),
               r['relative_pct'], chg, r['Holm_p'], r['holm_significant'], r['wins']))


if __name__ == '__main__':
    main()
