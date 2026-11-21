"""Disputed-seed forensics for the U-Air block (read-only).

Which seeds, and what is actually different about them.  Compares the frozen E3
tree against the route-A rebuilt cells for the five arms the repair did not
touch, and pulls the per-seed provenance the run directories record.
"""
from __future__ import annotations

import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNS = ROOT / 'artifacts/e3_formal_runs_r1/runs/uair'
ARMS = ('local_hajek', 'inst_cal', 'raven', 'raven_simoracle', 'twostage_hajek')
SEEDS = (30006, 30007, 30016, 30018)
TEST_WINDOW = set(range(30011, 30021))


def rebuilt_cells():
    path = ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv'
    by = {}
    for row in list(csv.reader(path.open()))[1:]:
        by.setdefault(row[0], {})[row[1]] = float(row[4])
    return by


def frozen(arm, seed):
    d = RUNS / arm / ('seed%d' % seed)
    out = {}
    fm = d / 'final_metrics.json'
    if fm.is_file():
        j = json.loads(fm.read_text())
        out['rmse_frozen'] = j.get('RMSE_mu')
        out['delta_group_frozen'] = j.get('Delta_group')
        out['mtime'] = fm.stat().st_mtime
        out['bytes'] = fm.stat().st_size
    dual = d / 'final_metrics_dual_domain.json'
    if dual.is_file():
        j = json.loads(dual.read_text())
        out['rmse_phys'] = j.get('RMSE_mu_phys')
        out['rmse_std_dual'] = j.get('RMSE_mu_std')
    man = d / 'runtime_manifest.json'
    if man.is_file():
        j = json.loads(man.read_text())
        out['trace_hash'] = (j.get('EventTrace_hash') or '')[:12]
        out['config_hash'] = (j.get('config_hash') or '')[:12]
        out['checkpoint_hash'] = (j.get('checkpoint_hash') or '')[:12]
    pol = d / 'metric_scale_policy.json'
    if pol.is_file():
        j = json.loads(pol.read_text())
        out['sigma'] = j.get('sigma')
    return out


def main():
    cells = rebuilt_cells()
    print('U-Air disputed-seed forensics (frozen E3 tree vs route-A rebuilt cells)')
    print('TEST window = seeds 30011-30020\n')
    for arm in ARMS:
        print('=== %s ===' % arm)
        print('  seed   frozen    rebuilt   rel%%      mtime                 trace_hash   cfg_hash     ckpt_hash    sigma')
        for seed in SEEDS:
            f = frozen(arm, seed)
            r = cells.get(arm, {}).get(str(seed))
            rel = (100.0 * (r - f['rmse_frozen']) / f['rmse_frozen']) if (r and f.get('rmse_frozen')) else None
            print('  %-6d %-9s %-9s %-9s %-20s %-12s %-12s %-12s %s'
                  % (seed,
                     ('%.6f' % f['rmse_frozen']) if f.get('rmse_frozen') else 'n/a',
                     ('%.6f' % r) if r else 'n/a',
                     ('%+.3f' % rel) if rel is not None else 'n/a',
                     pathlib.Path(f.get('mtime', 0)).name if False else (
                         __import__('datetime').datetime.fromtimestamp(f['mtime']).strftime('%Y-%m-%d %H:%M:%S')
                         if f.get('mtime') else 'n/a'),
                     f.get('trace_hash', 'n/a'), f.get('config_hash', 'n/a'),
                     f.get('checkpoint_hash', 'n/a'), f.get('sigma', 'n/a')))
        print()


if __name__ == '__main__':
    main()
