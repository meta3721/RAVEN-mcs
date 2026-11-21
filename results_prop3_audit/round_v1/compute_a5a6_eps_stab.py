"""Audit of the A6a/A6b clauses and of the stabilization error eps_stab.

Read-only.  Writes only into results_prop3_audit/round_v1/.  No training, no
solver, no modification of src/, of any .tex, or of any existing artifact.

What it computes, per dataset and per Design setting:
  eps_stab(r) = || beta_T(r) - beta_star(r) ||_1
where, on the active set A_r of the run,
  zeta_T   = pi_tar / max(pi_opp_true, pi_min)   [Design on]  or 1 [Design off]
  a_T      = min(a_max, zeta_T / max(p_obs_true, p_min))
  d_T      = min(d_max, 1 / max(q_use_true, q_min))
  b_T      = n_obs * a_T * d_T ,   beta_T = b_T / sum(b_T)
  a_star   = zeta_star / p_obs_true,  zeta_star = pi_tar / pi_opp_true [on] or 1 [off]
  d_star   = 1 / q_use_true ,       b_star = n_obs * a_star * d_star
and it also reads the decisive maximum of the A6a ceiling clauses at the true
margins (Design off: 1/p_obs_true; Design on: pi_tar/(pi_opp_true*p_obs_true)).

Constants are those the E3 formal runs actually resolved: the defaults of
`raven_mcs.training.window_runner.build_full_runner`, which
`raven_mcs.e3.real_runner.runner.run_e3_real` does not override.

Outputs: A5A6_EPS_STAB.json (this directory).
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from raven_mcs.correction.pi_target import build_pi_target          # noqa: E402
from raven_mcs.e3.canary.dataset_load import (                      # noqa: E402
    load_paper_dataset,
    load_spatial_to_client,
)

A_MAX, P_MIN, PI_MIN, D_MAX, Q_MIN = 20.0, 0.05, 1e-6, 10.0, 0.05
ARM = 'local_hajek'          # Design-on arm whose active sets are licensed
SEEDS = ['seed30%03d' % i for i in range(1, 21)]
OUT = ROOT / 'results_prop3_audit' / 'round_v1'


def pi_target_map(dataset: str) -> dict[tuple[str, str], float]:
    """pi_tar on (client, stratum).  SensorScope uses the frozen table; U-Air is
    rebuilt exactly as run_e3_real does with pi_target_mode='test'."""
    frozen = ROOT / 'configs/frozen/e1_pi_target_client_stratum.parquet'
    if dataset == 'sensorscope' and frozen.is_file():
        frame = pd.read_parquet(frozen)
    else:
        ds = load_paper_dataset(ROOT, dataset)
        atomic = ds.atomic_df.copy()
        if 'target_group_main' not in atomic.columns:
            atomic['target_group_main'] = atomic['target_group'].astype(str)
        frame = build_pi_target(atomic, load_spatial_to_client(ROOT, dataset), split='test')
    return {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in frame.itertuples()
    }


def harvest(dataset: str, seed: str) -> dict:
    path = (ROOT / 'artifacts/e3_formal_runs_r1/eventtraces' / dataset / seed
            / 'training_eventtrace' / 'events.parquet')
    if not path.is_file():
        return {}
    frame = pd.read_parquet(path, columns=[
        'window_id', 'client_id', 'opportunity_features', 'observed_unit_ids'])
    out = {}
    for row in frame.itertuples(index=False):
        feats = json.loads(row.opportunity_features)
        raw = row.observed_unit_ids
        n_obs = len(json.loads(raw)) if isinstance(raw, str) else 0
        out[(int(row.window_id), str(row.client_id))] = (
            str(feats.get('opportunity_stratum')),
            float(feats.get('pi_opp_true')),
            float(feats.get('p_obs_true')),
            float(feats.get('q_use_true')),
            int(n_obs),
        )
    return out


def active_windows(dataset: str, seed: str) -> list:
    path = (ROOT / 'artifacts/e3_formal_runs_r1/runs' / dataset / ARM / seed
            / 'window_metrics.json')
    if not path.is_file():
        return []
    return [w for w in json.loads(path.read_text()) if w.get('active')]


def audit(dataset: str, pi: dict, design_on: bool) -> dict:
    eps, ceil, inv_p = [], [], []
    n_active = n_over = n_qfloor = 0
    worst = (0.0, None)
    for seed in SEEDS:
        meta = harvest(dataset, seed)
        for window in active_windows(dataset, seed):
            wid = int(window['window_id'])
            b_t, b_s = [], []
            complete = True
            for client in [str(c) for c in window['active_clients']]:
                cell = meta.get((wid, client))
                if cell is None or cell[4] == 0:
                    b_t.append(0.0)
                    b_s.append(0.0)
                    continue
                stratum, pi_opp, p_obs, q_use, n_obs = cell
                pi_tar = pi.get((client, stratum))
                if pi_tar is None:
                    complete = False
                    break
                n_active += 1
                if q_use < Q_MIN:
                    n_qfloor += 1
                zeta_t = (pi_tar / max(pi_opp, PI_MIN)) if design_on else 1.0
                a_t = min(A_MAX, zeta_t / max(p_obs, P_MIN))
                d_t = min(D_MAX, 1.0 / max(q_use, Q_MIN))
                zeta_s = (pi_tar / pi_opp) if design_on else 1.0
                a_s = zeta_s / p_obs
                b_t.append(n_obs * a_t * d_t)
                b_s.append(n_obs * a_s * (1.0 / q_use))
                ratio = zeta_t / p_obs
                ceil.append(ratio)
                inv_p.append(1.0 / p_obs)
                if design_on and ratio > A_MAX:
                    n_over += 1
                if ratio > worst[0]:
                    worst = (ratio, [seed, wid, client])
            if not complete:
                continue
            b_t = np.asarray(b_t, dtype=float)
            b_s = np.asarray(b_s, dtype=float)
            if b_t.sum() <= 0 or b_s.sum() <= 0:
                continue
            eps.append(float(np.abs(b_t / b_t.sum() - b_s / b_s.sum()).sum()))
    arr = np.asarray(eps)
    return {
        'design': 'on' if design_on else 'off',
        'active_windows': int(arr.size),
        'active_client_windows': int(n_active),
        'eps_stab_median': float(np.median(arr)),
        'eps_stab_p95': float(np.quantile(arr, 0.95)),
        'eps_stab_max': float(arr.max()),
        'eps_stab_fraction_positive': float((arr > 0).mean()),
        'max_ceiling_ratio_true_margins': float(max(ceil)),
        'ceiling_clause_violations': int(n_over),
        'ceiling_clause_violation_share': float(n_over / n_active),
        'worst_cell': worst[1],
        'max_inverse_p': float(max(inv_p)),
        'q_min_floor_cells': int(n_qfloor),
        'q_min_floor_share_on_active': float(n_qfloor / n_active),
    }


def reproduce_released_audit() -> dict:
    """Re-check the readings the main audit quotes, from the released CSV."""
    path = ROOT / 'artifacts/a5_a6_audit/audit_records.csv'
    if not path.is_file():
        return {'status': 'audit_records.csv not found'}
    frame = pd.read_csv(path)
    out = {}
    for dataset in ('sensorscope', 'uair'):
        sub = frame[frame.dataset == dataset]
        obs = sub[sub.O.astype(bool)]
        q = sub.q_use_true.dropna()
        out[dataset] = {
            'records': int(len(sub)),
            'observed': int(len(obs)),
            'min_p_obs_true': float(sub.p_obs_true.min()),
            'q_min_floor_share_observed': float((obs.q_use_true < Q_MIN).mean()),
            'q_below_inv_dmax_share_observed': float((obs.q_use_true < 1.0 / D_MAX).mean()),
            'q_below_inv_dmax_share_all': float((q < 1.0 / D_MAX).mean()),
        }
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {'constants': {'a_max': A_MAX, 'p_min': P_MIN, 'pi_min': PI_MIN,
                            'd_max': D_MAX, 'q_min': Q_MIN},
              'arm': ARM, 'seeds': SEEDS,
              'definition': 'eps_stab = ||beta_T - beta_star||_1 at true margins'}
    for dataset in ('sensorscope', 'uair'):
        pi = pi_target_map(dataset)
        result[dataset] = {'pi_pairs': len(pi),
                           'pi_zero_pairs': int(sum(1 for v in pi.values() if v == 0.0))}
        for design_on in (True, False):
            result[dataset]['design_%s' % ('on' if design_on else 'off')] = audit(
                dataset, pi, design_on)
    result['released_audit_recheck'] = reproduce_released_audit()
    (OUT / 'A5A6_EPS_STAB.json').write_text(
        json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
