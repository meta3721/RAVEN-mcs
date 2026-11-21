"""A2 — two metric paths on the same checkpoints, incl. the E1 tree's own arms.

Path 1 (run time):  RMSE_mu stored in the run's final_metrics.json (2026-08-11 for
                    the E3 tree, 2026-09-27 for the E1 repair tree).
Path 2 (re-eval):   RMSE_mu recomputed here from checkpoints/final.pt, using the
                    published definition (main.tex:1600-1609): one model, all
                    supported test units, weights mu^eval_{h(i)} / n_{h(i)}.

The decisive cell: the E1 repair tree also contains `raven` and `twostage_hajek`
runs at the three inactive-final seeds.  If re-evaluating THEIR checkpoints
returns their own run-time value, the current code's two paths agree there and
the E3 discrepancy is a property of the old revision's stored checkpoint.

Read-only; writes only into results_seed_path_audit_r1/.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

import numpy as np
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset     # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle  # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF                 # noqa: E402
from raven_mcs.models.features import extract_features              # noqa: E402

OUT = ROOT / 'results_seed_path_audit_r1'
E3 = ROOT / 'artifacts/e3_formal_runs_r1/runs/uair'
E1 = ROOT / 'results_active_set_repair/round_v1/repair/C0_frozen/uair'
SEEDS = [30006, 30007, 30016, 30018]


def load_state(path):
    obj = torch.load(path, map_location='cpu', weights_only=False)
    if isinstance(obj, dict) and 'state_dict' in obj and isinstance(obj['state_dict'], dict):
        obj = obj['state_dict']
    return obj


def predict(model, dataset, split='test'):
    units = dataset.get_atomic_units(split=split)
    inv = {i: g for g, i in dataset._target_group_str_to_int.items()}
    spatial_to_idx = {str(s): int(i) for s, i in dataset._spatial_to_idx.items()}
    total_slots = int(dataset.atomic_df['time_index'].max()) + 1
    y_true, y_pred, gids = [], [], []
    model.eval()
    with torch.no_grad():
        for u in units:
            sp, hr, wd, tr = extract_features([u.spatial_id], [float(u.absolute_time)],
                                              [int(u.time_index)], spatial_to_idx, total_slots)
            p = model(sp, hr, wd, tr).cpu().numpy().reshape(-1)
            y_pred.append(float(p[0]))
            y_true.append(float(u.target_value))
            gids.append(int(u.target_group))
    return np.asarray(y_true), np.asarray(y_pred), np.asarray(gids)


def rmse_mu_published(y_true, y_pred, gids, mu, inv=None):
    """Published definition: sum_i (mu_g / n_g) (y-yhat)^2, then sqrt.

    ``gids`` are the dataset's integer group codes, which is also the encoding
    ``mu`` is aligned to (``align_mu_to_dataset`` -> ``group_str_to_int``).
    """
    counts = {}
    for g in gids.tolist():
        counts[int(g)] = counts.get(int(g), 0) + 1
    w = np.asarray([mu[int(g)] / counts[int(g)] for g in gids.tolist()], dtype=np.float64)
    return float(np.sqrt(np.sum(w * (y_true - y_pred) ** 2))), float(w.sum())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ds = load_paper_dataset(ROOT, 'uair')
    bundle = production_target_bundle(root=ROOT, dataset_name='uair', dataset=ds)
    mu = np.asarray(bundle['mu'], dtype=np.float64)
    inv = {i: g for g, i in ds._target_group_str_to_int.items()}

    e2 = {}
    for row in list(csv.reader((ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv').open()))[1:]:
        e2.setdefault(row[0], {})[row[1]] = float(row[4])

    rows = []
    targets = ([('e3', E3, a) for a in ('raven', 'twostage_hajek', 'local_hajek')]
               + [('e1', E1, a) for a in ('raven', 'twostage_hajek')])
    for tree, base, arm in targets:
        for seed in SEEDS:
            run = base / arm / ('seed%d' % seed)
            ck = run / 'checkpoints' / 'final.pt'
            if not ck.is_file():
                continue
            rt = json.loads((run / 'final_metrics.json').read_text())['RMSE_mu']
            wins = json.loads((run / 'window_metrics.json').read_text())
            model = CommonNDMF(num_spatial=ds.num_spatial)
            model.load_state_dict(load_state(ck))
            yt, yp, gids = predict(model, ds)
            re_eval, wsum = rmse_mu_published(yt, yp, gids, mu, inv)
            rows.append({
                'tree': tree, 'arm': arm, 'seed': seed,
                'last_window_active': bool(wins[-1].get('active')),
                'runtime_rmse': rt, 'reeval_rmse': re_eval,
                'rel_pct': 100.0 * (re_eval - rt) / rt,
                'e2_cell': e2.get(arm, {}).get(str(seed)),
                'weight_sum': wsum, 'n_test_units': int(len(yt)),
            })
    path = OUT / 'A2_PATH_COMPARISON.csv'
    with path.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print('%-4s %-16s %-6s %-9s %-12s %-12s %-10s %-12s' %
          ('tree', 'arm', 'seed', 'lastAct', 'runtime', 'reeval', 'rel%', 'e2_cell'))
    for r in rows:
        print('%-4s %-16s %-6d %-9s %-12.6f %-12.6f %+-10.4f %-12s'
              % (r['tree'], r['arm'], r['seed'], r['last_window_active'],
                 r['runtime_rmse'], r['reeval_rmse'], r['rel_pct'],
                 ('%.6f' % r['e2_cell']) if r['e2_cell'] else 'n/a'))
    print('\nweight_sum (must be 1):', sorted({round(r['weight_sum'], 12) for r in rows}))
    print('test units:', sorted({r['n_test_units'] for r in rows}))


if __name__ == '__main__':
    main()
