"""W4 read-only surrogate: does the P2 calibration absorb margin-estimation error?

Read-only. Reuses frozen artifacts only; no training, no solver, no writes
outside results_ceiling_class_r1/.

Mechanism under test
--------------------
The reference layer is the only place the selection margins enter.  For a
*calibrated* member (RAVEN-Design, Inst-Cal) the aggregation weights are the P2
solution, and the P2 map is non-expansive in its reference (eq. (39)), so a
reference perturbation of size e can move the weights by at most e.  For an
*uncalibrated* member (TwoStage-Hajek and Local-Hajek normalize the reference
directly) the perturbation passes through one-to-one.  The surrogate measures

    e_ref(r)  = || beta_hat(r) - beta_T(r) ||_1        reference perturbation
    d_comp(r) = || M_r (alpha_hat(r) - alpha_T(r)) ||_1 composition change

where beta_hat comes from the frozen window logs and beta_T is the reference the
same stabilization map returns at the true margins.  For the uncalibrated
members alpha = normalize(beta) holds by construction of the arm, so alpha_T is
computable exactly; for the calibrated members the same quantity is bounded by
||M_r||_2 * e_ref (no solver needed).
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402
from raven_mcs.e3.canary.dataset_load import (              # noqa: E402
    load_paper_dataset,
    load_spatial_to_client,
)

A_MAX, P_MIN, PI_MIN, D_MAX, Q_MIN = 20.0, 0.05, 1e-6, 10.0, 0.05
SEEDS = ['seed30%03d' % i for i in range(1, 21)]
OUT = ROOT / 'results_ceiling_class_r1'
CALIBRATED = ('raven', 'inst_cal')
UNCALIBRATED = ('twostage_hajek', 'local_hajek')


def pi_target_map(dataset):
    frozen = ROOT / 'configs/frozen/e1_pi_target_client_stratum.parquet'
    if dataset == 'sensorscope' and frozen.is_file():
        frame = pd.read_parquet(frozen)
    else:
        ds = load_paper_dataset(ROOT, dataset)
        atomic = ds.atomic_df.copy()
        if 'target_group_main' not in atomic.columns:
            atomic['target_group_main'] = atomic['target_group'].astype(str)
        frame = build_pi_target(atomic, load_spatial_to_client(ROOT, dataset), split='test')
    return {(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
            for r in frame.itertuples()}


def unit_group_map(dataset):
    frame = pd.read_parquet(ROOT / 'data/processed' / dataset / 'atomic_units.parquet')
    col = 'target_group' if 'target_group' in frame.columns else 'target_group_main'
    return {str(u): str(g) for u, g in zip(frame['unit_id'], frame[col])}


def harvest(dataset, seed):
    path = (ROOT / 'artifacts/e3_formal_runs_r1/eventtraces' / dataset / seed
            / 'training_eventtrace' / 'events.parquet')
    frame = pd.read_parquet(path, columns=['window_id', 'client_id',
                                           'opportunity_features', 'observed_unit_ids'])
    out = {}
    for row in frame.itertuples(index=False):
        feats = json.loads(row.opportunity_features)
        raw = row.observed_unit_ids
        units = json.loads(raw) if isinstance(raw, str) else []
        out[(int(row.window_id), str(row.client_id))] = (
            str(feats.get('opportunity_stratum')), float(feats.get('pi_opp_true')),
            float(feats.get('p_obs_true')), float(feats.get('q_use_true')),
            [str(u) for u in units])
    return out


def window_log(dataset, arm, seed):
    path = (ROOT / 'artifacts/e3_formal_runs_r1/runs' / dataset / arm / seed
            / 'window_metrics.json')
    if not path.is_file():
        return []
    return [w for w in json.loads(path.read_text()) if w.get('active')]


def true_reference(clients, meta, pi, wid):
    b = []
    for client in clients:
        cell = meta.get((wid, client))
        if cell is None or not cell[4]:
            b.append(0.0)
            continue
        stratum, pi_opp, p_obs, q_use, units = cell
        pi_tar = pi.get((client, stratum))
        if pi_tar is None:
            return None
        zeta = pi_tar / max(pi_opp, PI_MIN)
        a = min(A_MAX, zeta / max(p_obs, P_MIN))
        d = min(D_MAX, 1.0 / max(q_use, Q_MIN))
        b.append(len(units) * a * d)
    b = np.asarray(b, float)
    return b / b.sum() if b.sum() > 0 else None


def group_matrix(clients, meta, wid, groups):
    rows = []
    for client in clients:
        cell = meta.get((wid, client))
        counts = {}
        if cell is not None:
            for unit in cell[4]:
                g = groups.get(unit)
                if g is not None:
                    counts[g] = counts.get(g, 0) + 1
        total = sum(counts.values())
        rows.append({g: c / total for g, c in counts.items()} if total else {})
    all_groups = sorted({g for row in rows for g in row})
    return np.array([[row.get(g, 0.0) for g in all_groups] for row in rows])


def stats(values):
    x = np.asarray([v for v in values if v is not None], float)
    if x.size == 0:
        return None
    return {'n': int(x.size), 'median': float(np.median(x)),
            'p95': float(np.quantile(x, 0.95)), 'max': float(x.max()),
            'frac_positive': float((x > 0).mean())}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    result = {'definition': {'e_ref': '||beta_hat - beta_T||_1 per window',
                             'd_comp': '||M_r (alpha_hat - alpha_T)||_1 per window'},
              'calibrated_arms': list(CALIBRATED), 'uncalibrated_arms': list(UNCALIBRATED)}
    for dataset in ('sensorscope', 'uair'):
        pi = pi_target_map(dataset)
        groups = unit_group_map(dataset)
        per_arm = {}
        for arm in CALIBRATED + UNCALIBRATED:
            e_ref, d_exact, d_bound, norm_gap = [], [], [], []
            for seed in SEEDS:
                meta = harvest(dataset, seed)
                for window in window_log(dataset, arm, seed):
                    wid = int(window['window_id'])
                    clients = [str(c) for c in window['active_clients']]
                    beta_hat = np.asarray(window['beta_hat'], float)
                    beta_t = true_reference(clients, meta, pi, wid)
                    if beta_t is None or beta_hat.size != beta_t.size:
                        continue
                    e = float(np.abs(beta_hat - beta_t).sum())
                    e_ref.append(e)
                    M = group_matrix(clients, meta, wid, groups)
                    if M.size == 0:
                        continue
                    if arm in UNCALIBRATED:
                        a_hat = np.asarray(window['alpha'], float)
                        # validate the arm identity: its weights normalize the reference
                        norm_gap.append(float(np.abs(a_hat - beta_hat).max()))
                        a_t = beta_t / beta_t.sum()
                        d_exact.append(float(np.abs(M @ (a_hat - a_t)).sum()))
                    d_bound.append(float(np.linalg.norm(M, 2) * e))
            per_arm[arm] = {
                'e_ref': stats(e_ref),
                'd_comp_exact': stats(d_exact) if d_exact else None,
                'd_comp_bound': stats(d_bound),
                'max_abs_alpha_minus_beta_hat': (max(norm_gap) if norm_gap else None),
            }
        result[dataset] = per_arm
    (OUT / 'CALIBRATION_ABSORPTION.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
