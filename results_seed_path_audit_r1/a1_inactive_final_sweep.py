"""A1 — sweep every tree that feeds a printed cell for 'final window inactive'.

Read-only. Writes only into results_seed_path_audit_r1/.

For each (tree, dataset, arm, seed): reads window_metrics.json and records
whether the LAST window is active, the number of active windows, and whether a
final_metrics.json exists.  This yields the candidate set for A2: seeds where the
run-time metric path and a checkpoint re-evaluation can diverge.
"""
from __future__ import annotations

import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'results_seed_path_audit_r1'
TREES = {
    'e3': ROOT / 'artifacts/e3_formal_runs_r1/runs',
    'fedau': ROOT / 'artifacts/e3_fedau_window_r1/runs',
    'obsuse': ROOT / 'artifacts/e3_obsuse_window_r1/runs',
    'e4': ROOT / 'artifacts/e4_core_mechanism_ablation_r1/runs',
    'e1_repair': ROOT / 'results_active_set_repair/round_v1/repair/C0_frozen',
}
DATASETS = ('uair', 'sensorscope')
SEEDS = list(range(30001, 30021))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for tree, base in TREES.items():
        if not base.is_dir():
            continue
        for ds in DATASETS:
            ds_dir = base / ds
            if not ds_dir.is_dir():
                continue
            for arm_dir in sorted(p for p in ds_dir.iterdir() if p.is_dir()):
                for seed in SEEDS:
                    wm = arm_dir / ('seed%d' % seed) / 'window_metrics.json'
                    if not wm.is_file():
                        continue
                    wins = json.loads(wm.read_text(encoding='utf-8'))
                    if not wins:
                        continue
                    last = wins[-1]
                    rows.append({
                        'tree': tree, 'dataset': ds, 'arm': arm_dir.name, 'seed': seed,
                        'n_windows': len(wins),
                        'last_window_id': last.get('window_id'),
                        'last_active': bool(last.get('active')),
                        'last_a_r_size': last.get('a_r_size'),
                        'n_active_windows': sum(1 for w in wins if w.get('active')),
                        'has_final_metrics': (arm_dir / ('seed%d' % seed)
                                              / 'final_metrics.json').is_file(),
                    })
    path = OUT / 'A1_INACTIVE_FINAL_SWEEP.csv'
    with path.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print('rows:', len(rows), '->', path.name)
    # summary: inactive-final counts per tree/dataset
    agg = {}
    for r in rows:
        k = (r['tree'], r['dataset'])
        agg.setdefault(k, {'n': 0, 'inactive': 0, 'seeds': []})
        agg[k]['n'] += 1
        if not r['last_active']:
            agg[k]['inactive'] += 1
            agg[k]['seeds'].append((r['arm'], r['seed']))
    for k in sorted(agg):
        a = agg[k]
        print('%-12s %-12s runs=%-4d inactive-final=%-3d %s'
              % (k[0], k[1], a['n'], a['inactive'],
                 sorted({s for _, s in a['seeds']}) if a['inactive'] else ''))


if __name__ == '__main__':
    main()
