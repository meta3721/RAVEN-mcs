"""Class-level ceiling for the aggregate weighting class C_r (criterion RMSE_mu).

Read-only. Writes only into results_ceiling_class_r1/.

Question: inside the class the paper defines (weights in C_r, selected by (P2),
scored by RMSE_mu), how much does *estimating* the selection margins cost, and
how much headroom does the class have to a member that uses the true margins?

Pair 1 (clean): same class member, same Design setting, same everything except
    the observation and usable-update margins:
        RAVEN-Design  vs  RAVEN-SimOracle        (frozen E3 tree, 20 seeds)
Pair 2 (contrast): an uncalibrated member of the same weighting class:
        TwoStage-Hajek vs RAVEN-SimOracle        (route-A rebuilt cells, 20 seeds)

Reported as paired relative differences of RMSE_mu with 95% t intervals.
No training, no solver, no modification of any existing artifact.
"""
from __future__ import annotations

import csv
import json
import pathlib

import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'results_ceiling_class_r1'
SEEDS = list(range(30001, 30021))
ARMS = ('raven', 'inst_cal', 'local_hajek', 'twostage_hajek', 'raven_simoracle')


def ci(values):
    x = np.asarray(values, dtype=float)
    half = float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))
    return {'n': int(x.size), 'mean_pct': float(100 * x.mean()),
            'ci_lo_pct': float(100 * (x.mean() - half)),
            'ci_hi_pct': float(100 * (x.mean() + half))}


def frozen_sensorscope():
    base = ROOT / 'artifacts/e3_formal_runs_r1/runs/sensorscope'
    out = {}
    for arm in ARMS:
        vals = []
        for seed in SEEDS:
            f = base / arm / ('seed%d' % seed) / 'final_metrics.json'
            vals.append(json.loads(f.read_text())['RMSE_mu'] if f.is_file() else None)
        out[arm] = vals
    return out, 'artifacts/e3_formal_runs_r1/runs/sensorscope/*/seed*/final_metrics.json'


def rebuilt_uair():
    path = ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv'
    by = {}
    for row in list(csv.reader(path.open()))[1:]:
        by.setdefault(row[0], {})[row[1]] = float(row[4])
    return by, 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv'


def compare(table, oracle='raven_simoracle', paired_by_seed=True):
    res = {}
    ref = table[oracle] if paired_by_seed else None
    for arm in ARMS:
        if arm == oracle:
            continue
        if paired_by_seed:
            pairs = [(table[arm][i], ref[i]) for i in range(len(ref))
                     if table[arm][i] is not None and ref[i] is not None]
        else:
            seeds = sorted(set(table[arm]) & set(table[oracle]))
            pairs = [(table[arm][s], table[oracle][s]) for s in seeds]
        rel = [(a - b) / b for a, b in pairs]
        res[arm] = ci(rel)
    return res


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ss, ss_src = frozen_sensorscope()
    ua, ua_src = rebuilt_uair()
    out = {
        'criterion': 'RMSE_mu (deployment-target risk), paired over 20 seeds',
        'class': 'aggregation weights in C_r selected by (P2)',
        'sign_convention': 'positive = the first arm has larger RMSE_mu, i.e. the oracle arm is better',
        'sensorscope': {'source': ss_src, 'oracle_arm': 'raven_simoracle (true p and q)',
                        'vs_oracle': compare(ss)},
        'uair_rebuilt': {'source': ua_src, 'oracle_arm': 'raven_simoracle (true p and q)',
                         'vs_oracle': compare(ua, paired_by_seed=False)},
    }
    (OUT / 'CEILING_CLASS_PAIRED.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
