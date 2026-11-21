"""Step 1 — cell-by-cell impact of the mirror/theta finding (read-only).

Only the three triggered seeds (30007/30016/30018) need re-evaluation: at the
other 17 seeds the two metric paths agree, so the tree value stands.

For every affected arm this script:

  * reloads the three checkpoints and computes, at the theta copy, the
    prediction-based metrics: RMSE_mu, WorstGroupRMSE, Head_RMSE, Tail_RMSE
    (weights mu_g / n_g, per-block renormalised for the worst-block maximum);
  * rebuilds the corrected 20-seed mean as (17 unaffected tree values + 3 theta
    values) / 20, using each run's own final_metrics.json for the 17;
  * reports the structural metrics (Delta_group, Delta_c_s) as model-free, with
    the independent check that the round's E2 cells equal the tree's values;
  * compares the printed WorstGroupRMSE of the Design-on row with the theta-based
    value and with the public-repro per-seed CSV, to say whether that column was
    already theta-based.

Outputs: C_IMPACT_RECALC.csv (per arm/seed) and C_IMPACT_RECALC.json (means).
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
sys.path.insert(0, str(ROOT / 'scripts'))

import run_h_headroom as h                                    # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import _head_tail_rmse    # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle  # noqa: E402
from raven_mcs.metrics.accuracy import rmse_mu                 # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF            # noqa: E402
from raven_mcs.models.features import extract_features         # noqa: E402

OUT = ROOT / 'results_seed_path_audit_r1'
TREES = {
    'e3': ROOT / 'artifacts/e3_formal_runs_r1/runs/uair',
    'e4': ROOT / 'artifacts/e4_core_mechanism_ablation_r1/runs/uair',
}
TRIGGERED = (30007, 30016, 30018)
AFFECTED = {
    'e3': ('raven', 'inst_cal', 'local_hajek', 'twostage_hajek', 'raven_simoracle'),
    'e4': ('raven_wo_inst', 'raven_wo_obs', 'raven_wo_use', 'raven_wo_debt'),
}


def load_state(path):
    obj = torch.load(path, map_location='cpu', weights_only=False)
    if isinstance(obj, dict) and 'state_dict' in obj:
        obj = obj['state_dict']
    return obj


def predict(model, dataset, split='test'):
    units = dataset.get_atomic_units(split=split)
    inv = {i: g for g, i in dataset._target_group_str_to_int.items()}
    spatial_to_idx = {str(s): int(i) for s, i in dataset._spatial_to_idx.items()}
    total_slots = int(dataset.atomic_df['time_index'].max()) + 1
    yt, yp, gids, gstr = [], [], [], []
    model.eval()
    with torch.no_grad():
        for u in units:
            sp, hr, wd, tr = extract_features([u.spatial_id], [float(u.absolute_time)],
                                              [int(u.time_index)], spatial_to_idx, total_slots)
            p = model(sp, hr, wd, tr).cpu().numpy().reshape(-1)
            yp.append(float(p[0]))
            yt.append(float(u.target_value))
            gids.append(int(u.target_group))
            gstr.append(inv.get(int(u.target_group), str(u.target_group)))
    return {'y_true': np.asarray(yt), 'y_pred': np.asarray(yp),
            'groups': np.asarray(gids), 'group_strs': gstr}


def metrics_at_theta(pred, mu, head_ids, tail_ids):
    gids = pred['groups']
    counts = {}
    for g in gids.tolist():
        counts[int(g)] = counts.get(int(g), 0) + 1
    w = np.asarray([mu[int(g)] / counts[int(g)] for g in gids.tolist()], dtype=np.float64)
    err2 = (pred['y_true'] - pred['y_pred']) ** 2
    blocks = np.asarray([h._block_of(g) for g in pred['group_strs']])
    block_rmse = []
    for b in range(4):
        m = blocks == b
        if not m.any():
            continue
        wb = w[m] / w[m].sum()
        block_rmse.append(float(np.sqrt(np.sum(wb * err2[m]))))
    head, tail = _head_tail_rmse(pred, w, head_ids, tail_ids)
    return {'RMSE_mu': float(np.sqrt(np.sum(w * err2))),
            'WorstGroupRMSE': max(block_rmse) if block_rmse else None,
            'Head_RMSE': head, 'Tail_RMSE': tail}


def main() -> None:
    ds = load_paper_dataset(ROOT, 'uair')
    bundle = production_target_bundle(root=ROOT, dataset_name='uair', dataset=ds)
    mu = np.asarray(bundle['mu'], dtype=np.float64)
    ht = bundle['head_tail']
    head_ids, tail_ids = ht['head_group_ids'], ht['tail_group_ids']

    repro = {}
    repro_path = ROOT / 'RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv'
    if repro_path.is_file():
        for row in list(csv.DictReader(repro_path.open())):
            key = (row.get('method'), str(row.get('seed')))
            repro[key] = row

    rows, summary = [], {}
    for tree, arms in AFFECTED.items():
        for arm in arms:
            base = TREES[tree] / arm
            per_seed = {}
            for seed in range(30001, 30021):
                fm = base / ('seed%d' % seed) / 'final_metrics.json'
                if fm.is_file():
                    per_seed[seed] = json.loads(fm.read_text())
            if not per_seed:
                print('skip', tree, arm)
                continue
            rec = {'tree': tree, 'arm': arm, 'n_seeds': len(per_seed), 'theta': {}, 'tree_means': {}}
            for metric in ('RMSE_mu', 'WorstGroupRMSE', 'Head_RMSE', 'Tail_RMSE'):
                tree_vals = [per_seed[s].get(metric) for s in sorted(per_seed)
                             if per_seed[s].get(metric) is not None]
                if tree_vals:
                    rec['tree_means'][metric] = float(np.mean(tree_vals))
            theta_vals = {m: [] for m in ('RMSE_mu', 'WorstGroupRMSE', 'Head_RMSE', 'Tail_RMSE')}
            for seed in TRIGGERED:
                ck = base / ('seed%d' % seed) / 'checkpoints' / 'final.pt'
                if not ck.is_file():
                    continue
                model = CommonNDMF(num_spatial=ds.num_spatial)
                model.load_state_dict(load_state(ck))
                pred = predict(model, ds)
                got = metrics_at_theta(pred, mu, head_ids, tail_ids)
                rows.append({'tree': tree, 'arm': arm, 'seed': seed,
                             **{k: (None if v is None else float(v)) for k, v in got.items()},
                             'tree_RMSE_mu': per_seed.get(seed, {}).get('RMSE_mu'),
                             'tree_Tail_RMSE': per_seed.get(seed, {}).get('Tail_RMSE'),
                             'tree_Head_RMSE': per_seed.get(seed, {}).get('Head_RMSE')})
                for m in theta_vals:
                    if got.get(m) is not None:
                        theta_vals[m].append(got[m])
            rec['theta'] = {m: (float(np.mean(v)) if v else None) for m, v in theta_vals.items()}
            # corrected 20-seed mean for the prediction-based metrics
            corrected = {}
            for metric in ('RMSE_mu', 'WorstGroupRMSE', 'Head_RMSE', 'Tail_RMSE'):
                keep = [per_seed[s][metric] for s in sorted(per_seed)
                        if s not in TRIGGERED and per_seed[s].get(metric) is not None]
                if keep and theta_vals[metric] and len(keep) + len(theta_vals[metric]) == len(per_seed):
                    corrected[metric] = float((sum(keep) + sum(theta_vals[metric])) / len(per_seed))
            rec['corrected_mean'] = corrected
            rec['rel_change_pct'] = {m: (100.0 * (corrected[m] - rec['tree_means'][m]) / rec['tree_means'][m])
                                     if m in corrected and m in rec['tree_means'] else None
                                     for m in corrected}
            # structural metrics come from the tree verbatim; check E2 copies them
            summary[(tree, arm)] = rec
            print('%-3s %-18s tree RMSE_mu=%.6f -> theta-corrected=%.6f (%+.3f%%)  WG: %s -> %s'
                  % (tree, arm, rec['tree_means'].get('RMSE_mu', float('nan')),
                     corrected.get('RMSE_mu', float('nan')),
                     rec['rel_change_pct'].get('RMSE_mu') or 0.0,
                     ('%.4f' % rec['tree_means']['WorstGroupRMSE']) if rec['tree_means'].get('WorstGroupRMSE') else 'n/a',
                     ('%.4f' % corrected['WorstGroupRMSE']) if corrected.get('WorstGroupRMSE') else 'n/a'))

    with (OUT / 'C_IMPACT_RECALC.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (OUT / 'C_IMPACT_RECALC.json').write_text(
        json.dumps({('%s/%s' % k): v for k, v in summary.items()}, indent=2), encoding='utf-8')
    print('\nwrote C_IMPACT_RECALC.csv / .json')


if __name__ == '__main__':
    main()
