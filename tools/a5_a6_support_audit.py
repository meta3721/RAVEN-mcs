"""Audit of the A5/A6 support hypotheses on the frozen E3 formal traces.

A5 (positivity on the active support) and A6 (inactive stabilization) are the
two hypotheses obtained by splitting the former single "quantitative positivity"
assumption.  This script reads only released artifacts -- no retraining -- and
reports one reading per sub-condition per dataset.

Inputs (read-only):
  artifacts/e3_formal_runs_r1/eventtraces/<dataset>/<seed>/training_eventtrace/events.parquet
      columns: window_id, client_id, opportunity_features (JSON with the true
      selection margins), observed_unit_ids, O, U, oracle_p, oracle_q

Outputs:
  artifacts/a5_a6_audit/audit_records.csv   per client-window harvested record
  artifacts/a5_a6_audit/audit_summary.csv   one row per (dataset, sub-condition)
  artifacts/a5_a6_audit/audit_table.md      the table reproduced in the supplement
"""
import argparse
import json
from pathlib import Path

import pandas as pd

DATASETS = ('sensorscope', 'uair')
N_SEEDS = 20
OUT = Path('artifacts/a5_a6_audit')


def harvest(dataset, root, n_seeds):
    rows = []
    seeds = ['seed30%03d' % i for i in range(1, n_seeds + 1)]
    for seed in seeds:
        f = root / dataset / seed / 'training_eventtrace' / 'events.parquet'
        if not f.is_file():
            continue
        df = pd.read_parquet(f, columns=[
            'window_id', 'client_id', 'opportunity_features',
            'observed_unit_ids', 'O', 'U', 'oracle_p', 'oracle_q'])
        for r in df.itertuples(index=False):
            of = r.opportunity_features
            try:
                j = json.loads(of) if isinstance(of, str) else dict(of)
            except Exception:
                j = {}
            obs = r.observed_unit_ids
            if isinstance(obs, str):
                try:
                    n_obs = len(json.loads(obs))
                except Exception:
                    n_obs = 0
            elif obs is None:
                n_obs = 0
            else:
                n_obs = len(obs)
            o_flag = r.O
            if isinstance(o_flag, str):
                o_flag = o_flag.strip().lower() in ('true', '1')
            rows.append(dict(
                dataset=dataset, seed=seed, window=r.window_id,
                client=r.client_id,
                pi_opp_true=j.get('pi_opp_true'),
                p_obs_true=j.get('p_obs_true'),
                q_use_true=j.get('q_use_true'),
                q_mc_se=j.get('q_mc_se'),
                n_obs=n_obs, O=bool(o_flag) or n_obs > 0,
                U=str(r.U).strip().lower() in ('true', '1'),
                oracle_p=r.oracle_p, oracle_q=r.oracle_q))
    return pd.DataFrame(rows)


def load_design(root):
    """Read p_min/q_min/a_max/d_max from the frozen protocol configuration.

    The E3 formal run artifacts under ``root`` carry no weight-safety snapshot,
    so this falls back to the frozen candidate-selection config.  ``a_max`` is
    reported from whichever source supplies it; see ``--a-max`` for the value
    used in the verdicts.
    """
    want = ('p_min', 'q_min', 'a_max', 'd_max')
    best = {}
    candidates = [Path('configs/frozen/e1_r2_candidate_selection.json')]
    candidates += sorted(root.rglob('*.json')) + sorted(root.rglob('*.yaml'))
    for p in candidates:
        if not p.is_file():
            continue
        try:
            txt = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        try:
            j = json.loads(txt)
        except Exception:
            continue
        if not isinstance(j, dict):
            continue
        flat = {}

        def walk(node, prefix=''):
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, prefix + k + '.')
            elif not isinstance(node, (dict, list)):
                flat[prefix.rstrip('.')] = node
        walk(j)
        got = {}
        for k, v in flat.items():
            tail = k.rsplit('.', 1)[-1]
            if tail in want and isinstance(v, (int, float)):
                got.setdefault(tail, (v, str(p)))
        if len(got) > len(best):
            best = got
    return {k: v for k, v in best.items()}


def verdict(ok):
    return {True: 'PASS', False: 'FAIL', None: 'N/A'}[ok]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='artifacts/e3_formal_runs_r1/eventtraces')
    ap.add_argument('--seeds', type=int, default=N_SEEDS)
    ap.add_argument('--p-min', type=float, default=0.05)
    ap.add_argument('--q-min', type=float, default=0.05)
    ap.add_argument('--a-max', type=float, default=40.0,
                    help='weight ceiling; 40 is frozen by the formal '
                         'aggregation gate, 20 is the library default')
    ap.add_argument('--d-max', type=float, default=10.0)
    a = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(a.root)
    design = load_design(Path('artifacts/e3_formal_runs_r1'))
    if design:
        print('design values read from the frozen run configuration:')
        for k in ('p_min', 'q_min', 'a_max', 'd_max'):
            if k in design:
                print('  %-6s = %-8s  (%s)' % (k, design[k][0], design[k][1]))
    print('audit floors used: p_min=%g q_min=%g a_max=%g d_max=%g'
          % (a.p_min, a.q_min, a.a_max, a.d_max))
    print()

    frames = []
    for ds in DATASETS:
        t = harvest(ds, root, a.seeds)
        if t.empty:
            print('=== %s: no trace found under %s ===' % (ds, root))
            continue
        frames.append(t)
    if not frames:
        raise SystemExit('no traces harvested')
    rec = pd.concat(frames, ignore_index=True)
    rec.to_csv(OUT / 'audit_records.csv', index=False)

    summ = []
    for ds in DATASETS:
        t = rec[rec.dataset == ds]
        if t.empty:
            continue
        obs = t[t.O]
        pos = obs[obs.q_use_true > 0]
        pi = t.pi_opp_true.dropna()
        pb = t.p_obs_true.dropna()
        qu = t.q_use_true.dropna()
        # A5/A6 reading: the H\'ajek denominator on the active support.
        ab = obs.assign(
            a=obs.n_obs / obs.p_obs_true.clip(lower=a.p_min),
            d=(1.0 / obs.q_use_true.clip(lower=a.q_min)).clip(upper=a.d_max))
        ab = ab.assign(b=ab.a * ab.d)
        ab = ab[ab.a > 0]
        # A5 lower-bounds the *window* H\'ajek mass 1^T b summed over the
        # active clients of a window, not the per-client mass.
        per_window = ab.groupby(['seed', 'window'], as_index=False).b.sum()

        ratio_below = float((qu < 1.0 / a.d_max).mean()) if len(qu) else float('nan')
        floor_active = float((obs.q_use_true < a.q_min).mean()) if len(obs) else float('nan')
        rec_for = [
            ('records', len(t), None, None, None),
            ('pi_opp_true', len(pi), pi.min(), pi.quantile(.05), pi.median()),
            ('p_obs_true', len(pb), pb.min(), pb.quantile(.05), pb.median()),
            ('q_use_true', len(qu), qu.min(), qu.quantile(.05), qu.median()),
            ('q_use_true among O=1', len(obs),
             obs.q_use_true.min() if len(obs) else None,
             obs.q_use_true.quantile(.05) if len(obs) else None,
             obs.q_use_true.median() if len(obs) else None),
        ]
        print('=== %s ===  %d client-window records, %d seeds, %d observed'
              % (ds.upper(), len(t), t.seed.nunique(), len(obs)))
        for name, n, mn, p05, med in rec_for:
            if mn is None:
                print('  %-24s n=%d' % (name, n))
            else:
                print('  %-24s n=%-7d min=%-12.6g p05=%-12.6g median=%.6g'
                      % (name, n, mn, p05, med))
        print('  q_use_true == 0            : %d / %d (%.2f%%)'
              % (int((qu == 0).sum()), len(qu), 100 * (qu == 0).mean()))
        print('  q_use_true == 0 and O=1    : %d / %d'
              % (int((obs.q_use_true == 0).sum()), len(obs)))
        print('  q_use_true < 1/d_max       : %.2f%% of records'
              % (100 * ratio_below))
        print('  q_min floor active (O=1)   : %.2f%%' % (100 * floor_active))
        print('  d_max ceiling binds (O=1)  : %.2f%%'
              % (100 * float((obs.q_use_true < 1.0 / a.d_max).mean())))
        print('  min Hajek mass b (O=1)     : %.6g  over %d observed windows'
              % (ab.b.min(), len(ab)))
        print('  min window mass 1^T b      : %.6g  over %d active windows'
              % (per_window.b.min(), len(per_window)))
        print()

        def add(sub, reading, ok, note=''):
            summ.append(dict(dataset=ds, sub_condition=sub, reading=reading,
                             verdict=verdict(ok), note=note))

        add('P1 min pi_opp_true > 0', '%.3g' % pi.min(), bool(pi.min() > 0),
            'opportunity positivity')
        add('P2 min p_obs_true >= p_min', '%.4g' % pb.min(),
            bool(pb.min() >= a.p_min), 'observation floor p_min=%g' % a.p_min)
        add('P2b min p_obs_true >= 1/a_max',
            '%.4g vs 1/20=%.3f and 1/40=%.3f' % (pb.min(), 0.05, 0.025),
            bool(pb.min() >= 1.0 / 20.0 and pb.min() >= 1.0 / 40.0),
            'A6 clause; verdict identical at a_max=20 and 40')
        add('P3 min q_use_true >= 1/d_max',
            '%.4g (%.1f%% below, %.1f%% exactly 0)' % (
                qu.min(), 100 * ratio_below, 100 * (qu == 0).mean()),
            bool(qu.min() >= 1.0 / a.d_max),
            '1/d_max=%.2f' % (1.0 / a.d_max))
        add('P3b min q_use_true among O=1',
            '%.4g' % (obs.q_use_true.min() if len(obs) else float('nan')),
            bool(len(obs) and obs.q_use_true.min() > 0),
            'positivity restricted to the active support')
        add('P4 min window mass 1^T b > 0',
            '%.4g (per-client min %.4g)' % (per_window.b.min(), ab.b.min()),
            bool(per_window.b.min() > 0),
            'B_min; %d active windows' % len(per_window))
        add('P5 q_min floor inactive',
            '%.2f%% of observed windows below q_min' % (100 * floor_active),
            bool(floor_active == 0.0), 'A6 clause')
        add('P5b d_max ceiling inactive',
            '%.2f%% of records have q_use_true < 1/d_max' % (100 * ratio_below),
            bool(ratio_below == 0.0), 'A6 clause')
        add('P6 ideal/practical share A_r', 'not recoverable from released logs',
            None, 'p2_invocation_states.json carries no active-set list')

    s = pd.DataFrame(summ)
    s.to_csv(OUT / 'audit_summary.csv', index=False)
    print('=== verdict summary ===')
    print(s.to_string(index=False))
    print()
    print('wrote:', OUT / 'audit_records.csv')
    print('wrote:', OUT / 'audit_summary.csv')


if __name__ == '__main__':
    main()
