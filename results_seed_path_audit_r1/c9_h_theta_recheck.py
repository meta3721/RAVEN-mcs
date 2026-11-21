"""Residual check 1 — theta re-evaluation of the ten triggered H-grid runs.

The A1 sweep found ten U-Air runs under results_h_headroom/round_u1/runs whose
final window does not aggregate: the Design-on oracle (raven_simoracle) at
C0_frozen/C3_low_capacity/C4_block_uniform seeds 30007/30016/30018 and at
C1_tilt_strong seed 30014.  Their stored RMSE_mu is the in-memory mirror value.

This script re-evaluates those ten checkpoints at theta using the run's own
wiring (production target for C0/C1/C3, the block-uniform override built exactly
as run_h_headroom.block_uniform_target for C4; DiurnalBlindNDMF for C3), then
rebuilds the affected H_summary cells and reports the movement.

The paper prints nothing from these columns (the quoted H facts come from the
frozen-arm column, which uses the Design-off oracle), so this is a
record-hygiene check.  Read-only; writes only C9_H_THETA_RECHECK.{csv,json}.
"""
from __future__ import annotations

import copy
import csv
import json
import pathlib
import sys

import numpy as np
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / 'results_seed_path_audit_r1'
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

import run_h_headroom as h                                       # noqa: E402
from raven_mcs.correction.pi_target import build_pi_target       # noqa: E402
from raven_mcs.e3.canary.dataset_load import (load_paper_dataset,  # noqa: E402
                                              load_spatial_to_client)
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle   # noqa: E402
from raven_mcs.models.features import extract_features           # noqa: E402

RUNS = ROOT / 'results_h_headroom/round_u1/runs'
TRIGGERED = {'C0_frozen': (30007, 30016, 30018), 'C1_tilt_strong': (30014,),
             'C3_low_capacity': (30007, 30016, 30018), 'C4_block_uniform': (30007, 30016, 30018)}
COND = h.CONDITIONS


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


def rmse_mu(pred, mu):
    counts = {}
    for g in pred['groups'].tolist():
        counts[int(g)] = counts.get(int(g), 0) + 1
    w = np.asarray([mu[int(g)] / counts[int(g)] for g in pred['groups'].tolist()], dtype=float)
    w = w / w.sum()
    return float(np.sqrt(np.sum(w * (pred['y_true'] - pred['y_pred']) ** 2)))


def main() -> None:
    ds = load_paper_dataset(ROOT, 'uair')
    prod = np.asarray(production_target_bundle(root=ROOT, dataset_name='uair', dataset=ds)['mu'],
                      dtype=np.float64)
    # block-uniform override, exactly as run_h_headroom.block_uniform_target builds it
    mapping = load_spatial_to_client(ROOT, 'uair')
    atomic, _ = apply_sealed_opportunity_stratum(ds.atomic_df, dataset='uair', root=ROOT)
    frame = atomic.copy()
    frame['target_group_main'] = frame['target_group'].astype(str)
    pi = build_pi_target(frame, mapping, split='test')
    mass_b: dict[int, float] = {}
    for r in pi.itertuples():
        b = h._block_of(r.opportunity_stratum)
        mass_b[b] = mass_b.get(b, 0.0) + float(r.pi_k_s_tar)
    factor = {b: 0.25 / m for b, m in mass_b.items()}
    names = list(production_target_bundle(root=ROOT, dataset_name='uair', dataset=ds)['group_id_by_index'])
    mu_block = prod.copy()
    for i, name in enumerate(names):
        mu_block[i] *= factor[h._block_of(name)]
    mu_block = mu_block / mu_block.sum()

    rows = []
    for cond, seeds in TRIGGERED.items():
        for seed in seeds:
            run = RUNS / cond / 'uair' / 'raven_simoracle' / ('seed%d' % seed)
            ck = run / 'checkpoints' / 'final.pt'
            obj = torch.load(ck, map_location='cpu', weights_only=False)
            state = obj['state_dict'] if isinstance(obj, dict) and 'state_dict' in obj else obj
            cls = h.DiurnalBlindNDMF if COND[cond]['model'] == 'diurnal_blind' else h.CommonNDMF
            model = cls(num_spatial=ds.num_spatial)
            model.load_state_dict(state)
            mu = mu_block if COND[cond]['target'] == 'block_uniform' else prod
            pred = predict(model, ds)
            theta_val = rmse_mu(pred, mu)
            stored = json.loads((run / 'final_metrics.json').read_text())['RMSE_mu']
            rows.append({'condition': cond, 'seed': seed, 'model': COND[cond]['model'],
                         'target': COND[cond]['target'], 'stored_rmse_mu': stored,
                         'theta_rmse_mu': theta_val, 'rel_pct': 100.0 * (theta_val - stored) / stored})
            print('%-17s seed%d stored=%.6f theta=%.6f (%+.3f%%)'
                  % (cond, seed, stored, theta_val, rows[-1]['rel_pct']))

    # rebuild the affected H_summary cells
    seed_rows = list(csv.DictReader((ROOT / 'results_h_headroom/round_u1/tables/H_seed_rows.csv').open()))
    summary = list(csv.DictReader((ROOT / 'results_h_headroom/round_u1/tables/H_summary.csv').open()))
    from scipy import stats
    by_cond: dict[str, dict[str, dict[int, float]]] = {}
    for r in seed_rows:
        if r['dataset'] != 'uair':
            continue
        by_cond.setdefault(r['condition'], {}).setdefault(r['method'], {})[int(r['seed'])] = float(r['RMSE_mu'])
    for r in rows:
        by_cond[r['condition']]['raven_simoracle'][r['seed']] = r['theta_rmse_mu']
    report = []
    for cond in TRIGGERED:
        u = by_cond[cond]['fedavg_window']
        od = by_cond[cond]['raven_simoracle']
        nn = by_cond[cond]['raven_simoracle_nodesign']
        common = sorted(set(u) & set(od) & set(nn))
        uu = np.asarray([u[s] for s in common])
        dd = np.asarray([od[s] for s in common])
        nnn = np.asarray([nn[s] for s in common])

        def ci(x):
            half = float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))
            return float(x.mean()), float(x.mean() - half), float(x.mean() + half)

        hd, hd_lo, hd_hi = ci((uu - dd) / uu)
        sc, sc_lo, sc_hi = ci((dd - nnn) / nnn)
        hh, hh_lo, hh_hi = ci((uu - nnn) / uu)
        old = next(s for s in summary if s['condition'] == cond and s['dataset'] == 'uair')
        rec = {'condition': cond,
               'H_design_old': float(old['H_design_RMSE_mu']), 'H_design_new': hd,
               'H_design_ci_old': [float(old['H_design_RMSE_mu_ci_lo']), float(old['H_design_RMSE_mu_ci_hi'])],
               'H_design_ci_new': [hd_lo, hd_hi],
               'support_cost_old': float(old['design_support_cost_RMSE_mu']),
               'support_cost_new': sc,
               'support_cost_ci_old': [float(old['design_support_cost_RMSE_mu_ci_lo']),
                                       float(old['design_support_cost_RMSE_mu_ci_hi'])],
               'support_cost_ci_new': [sc_lo, sc_hi],
               'H_frozen_arm_old': float(old['H_RMSE_mu']), 'H_frozen_arm_new': hh,
               'H_frozen_arm_ci_new': [hh_lo, hh_hi]}
        report.append(rec)
        print('%-17s H_design %+.4f -> %+.4f | support cost %+.4f -> %+.4f | H(frozen arm) %+.6f -> %+.6f'
              % (cond, rec['H_design_old'], hd, rec['support_cost_old'], sc,
                 rec['H_frozen_arm_old'], hh))

    with (HERE / 'C9_H_THETA_RECHECK.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (HERE / 'C9_H_THETA_RECHECK.json').write_text(json.dumps(report, indent=2, default=float),
                                                  encoding='utf-8')
    print('\nwrote C9_H_THETA_RECHECK.csv / .json')


if __name__ == '__main__':
    main()
