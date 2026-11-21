"""Step 1 — per-cell diff list for re-sourcing the affected U-Air cells to theta.

Value resolution per (arm, metric), all over the same 20 seeds:

  E2 cells        authoritative theta values (all 20 seeds re-evaluated from the
                  stored checkpoints) for the metrics it carries: RMSE_mu,
                  WorstGroupRMSE, Delta_group, Delta_c_s, per-block RMSE.
  tree + override frozen final_metrics.json with the three triggered seeds
                  (30007/30016/30018) replaced by the theta values computed in
                  C_IMPACT_RECALC.csv: Head_RMSE, Tail_RMSE, and every metric of
                  the generation-2 w/o-Inst reruns (evaluated fresh here).
  tree only       model-free structure (Delta_group, Delta_c_s of arms E2 does not
                  cover); identical either way.

Writes C3_CELL_DIFF.csv / C3_CELL_DIFF.json.  No manuscript file is touched.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from c_impact_recalc import (ROOT, TRIGGERED, load_state, metrics_at_theta,  # noqa: E402
                             predict)
from raven_mcs.e3.canary.dataset_load import load_paper_dataset              # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle  # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF                          # noqa: E402

E3 = ROOT / 'artifacts/e3_formal_runs_r1/runs/uair'
E4 = ROOT / 'artifacts/e4_core_mechanism_ablation_r1/runs/uair'
GEN2 = (ROOT / 'artifacts/e4_wo_inst_reference_penalty_final_correction_r1'
        '/final_corrective_runs/uair/raven_wo_inst')
EVIDENCE = ROOT / 'paper_ready_r1/01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv'
SEEDS = list(range(30001, 30021))
TEST_SEEDS = list(range(30011, 30021))
KEYMAP = {'RMSE': 'RMSE_mu', 'WG': 'WorstGroupRMSE_std'}


def mean_std(vals):
    a = np.asarray([v for v in vals if v is not None], dtype=float)
    if not len(a):
        return None
    return float(a.mean()), float(a.std(ddof=1))


def load_frozen(base, arm):
    out = {}
    for s in SEEDS:
        p = base / arm / ('seed%d' % s) / 'final_metrics.json'
        if p.is_file():
            j = json.loads(p.read_text())
            for k, v in j.items():
                if isinstance(v, (int, float)):
                    out.setdefault(k, {})[s] = float(v)
    return out


def main() -> None:
    ds = load_paper_dataset(ROOT, 'uair')
    bundle = production_target_bundle(root=ROOT, dataset_name='uair', dataset=ds)
    mu = np.asarray(bundle['mu'], dtype=np.float64)
    ht = bundle['head_tail']
    head_ids, tail_ids = ht['head_group_ids'], ht['tail_group_ids']

    # ---- theta values: E2 (authoritative) ----
    e2cols = {'RMSE': 'RMSE_mu_std', 'WG': 'WorstGroupRMSE_std', 'Dg': 'Delta_group',
              'Dcs': 'Delta_c_s', 'g0': 'RMSE_block0_std', 'g1': 'RMSE_block1_std',
              'g2': 'RMSE_block2_std', 'g3': 'RMSE_block3_std'}
    e2: dict[str, dict[str, list[float]]] = {}
    for row in csv.DictReader((ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv').open()):
        arm = e2.setdefault(row['method'], {})
        for k, c in e2cols.items():
            raw = (row.get(c) or '').strip()
            if raw:
                arm.setdefault(k, []).append(float(raw))
    theta_e2 = {a: {k: mean_std(v) for k, v in d.items() if v} for a, d in e2.items()}

    # ---- theta at the triggered seeds, from the A2/C run ----
    theta_triggered: dict[str, dict[int, dict[str, float]]] = {}
    for row in csv.DictReader((HERE / 'C_IMPACT_RECALC.csv').open()):
        theta_triggered.setdefault(row['arm'], {})[int(row['seed'])] = {
            'RMSE_mu': float(row['RMSE_mu']), 'WorstGroupRMSE': float(row['WorstGroupRMSE']),
            'Head_RMSE': float(row['Head_RMSE']), 'Tail_RMSE': float(row['Tail_RMSE'])}

    # ---- generation-2 w/o-Inst: fresh evaluation at the triggered seeds ----
    gen2_theta = {}
    for s in TRIGGERED:
        ck = GEN2 / ('seed%d' % s) / 'checkpoints' / 'final.pt'
        model = CommonNDMF(num_spatial=ds.num_spatial)
        model.load_state_dict(load_state(ck))
        got = metrics_at_theta(predict(model, ds), mu, head_ids, tail_ids)
        gen2_theta[s] = got
        print('gen2 wo_inst seed%d: tree=%.6f theta=%.6f (tail %.6f->%.6f)'
              % (s, json.loads((GEN2 / ('seed%d' % s) / 'final_metrics.json').read_text())['RMSE_mu'],
                 got['RMSE_mu'],
                 json.loads((GEN2 / ('seed%d' % s) / 'final_metrics.json').read_text())['Tail_RMSE'],
                 got['Tail_RMSE']))

    # ---- resolved values ----
    SPEC = {'raven': (E3, 'raven'), 'inst_cal': (E3, 'inst_cal'), 'local_hajek': (E3, 'local_hajek'),
            'twostage_hajek': (E3, 'twostage_hajek'), 'raven_simoracle': (E3, 'raven_simoracle'),
            'fedavg_window': (E3, 'fedavg_window'), 'fedasync_window': (E3, 'fedasync_window'),
            'flamf_timealign_adapted': (E3, 'flamf_timealign_adapted'), 'debt_cal': (E3, 'debt_cal'),
            'fedau_window': (ROOT / 'artifacts/e3_fedau_window_r1/runs/uair', 'fedau_window'),
            'obsuse_window': (ROOT / 'artifacts/e3_obsuse_window_r1/runs/uair', 'obsuse_window'),
            'raven_wo_design': (E4, 'raven_wo_design'), 'raven_wo_obs': (E4, 'raven_wo_obs'),
            'raven_wo_use': (E4, 'raven_wo_use'), 'raven_wo_debt': (E4, 'raven_wo_debt'),
            'raven_wo_inst': (E4, 'raven_wo_inst'), 'raven_wo_inst_gen2': (GEN2.parent.parent if False else None, None)}
    # fedau/obsuse trees resolved by search (names differ across artifacts)
    for arm in ('fedau_window', 'obsuse_window'):
        cands = list(ROOT.glob('artifacts/e3_%s*_r1/runs/uair' % arm.split('_')[0]))
        if cands:
            SPEC[arm] = (cands[0], arm)

    resolved = {}
    for arm, (base, sub) in SPEC.items():
        if base is None:
            continue
        frozen = load_frozen(base, sub)
        if not frozen:
            print('WARNING no frozen metrics for', arm, base)
            continue
        vals = {}
        for key, metric in (('RMSE', 'RMSE_mu'), ('Head', 'Head_RMSE'), ('Tail', 'Tail_RMSE'),
                            ('Dg', 'Delta_group'), ('Dcs', 'Delta_c_s'),
                            ('g0', 'RMSE_block0_std'), ('g1', 'RMSE_block1_std'),
                            ('g2', 'RMSE_block2_std'), ('g3', 'RMSE_block3_std')):
            series = dict(frozen.get(metric, {}))
            if arm in theta_triggered and metric in theta_triggered[arm].get(min(TRIGGERED), {}):
                for s in TRIGGERED:
                    if s in series and s in theta_triggered[arm]:
                        series[s] = theta_triggered[arm][s][metric]
            if metric in frozen:
                vals[key] = mean_std([series.get(s) for s in SEEDS])
        if arm in theta_e2:
            for k, v in theta_e2[arm].items():
                vals[k] = v
        resolved[arm] = vals
    # generation-2 arm: frozen + fresh theta override
    g2 = load_frozen(GEN2.parent, 'raven_wo_inst')
    vals = {}
    for key, metric in (('RMSE', 'RMSE_mu'), ('Head', 'Head_RMSE'), ('Tail', 'Tail_RMSE'),
                        ('Dg', 'Delta_group'), ('Dcs', 'Delta_c_s')):
        series = dict(g2.get(metric, {}))
        for s in TRIGGERED:
            if s in series and metric in gen2_theta[s]:
                series[s] = gen2_theta[s][metric]
        vals[key] = mean_std([series.get(s) for s in SEEDS])
    resolved['raven_wo_inst_gen2'] = vals
    # mirror-only view for classification
    mirror = {}
    for arm, (base, sub) in SPEC.items():
        if base is None:
            continue
        frozen = load_frozen(base, sub)
        if frozen:
            mirror[arm] = {k: mean_std(list(frozen.get(m, {}).values())) for k, m in
                           (('RMSE', 'RMSE_mu'), ('Head', 'Head_RMSE'), ('Tail', 'Tail_RMSE'),
                            ('Dg', 'Delta_group'), ('Dcs', 'Delta_c_s'))}

    # ---------- printed cells ----------
    cells = []

    def classify(printed, arm, key, tol=6e-4):
        th = resolved.get(arm, {}).get(key)
        mi = mirror.get(arm, {}).get(key)
        thv = th[0] if th else None
        miv = mi[0] if mi else None
        if thv is not None and abs(printed - thv) <= tol and (miv is None or abs(printed - thv) <= abs(printed - miv)):
            return 'theta (keep)', th
        if miv is not None and abs(printed - miv) <= tol:
            return 'MIRROR (replace)', th
        return 'unmatched', th

    def add(table, line, row, col, printed, arm, key, fmt='%.6f', note=''):
        action, th = classify(printed, arm, key)
        cells.append({'table': table, 'line': line, 'row': row, 'column': col,
                      'printed_old': printed, 'action': action,
                      'theta_new': (fmt % th[0]) if th else None,
                      'theta_std': ('%.4f' % th[1]) if th else None, 'arm': arm, 'note': note})

    t3 = [('FedAvg-Window', 1894, 'fedavg_window', 1.1119, 1.1690, 1.0446, 1.3138),
          ('TwoStage-Hajek', 1895, 'twostage_hajek', 1.2160, 1.2907, 1.1196, 1.2406),
          ('FedAU-Window', 1896, 'fedau_window', 1.1128, 1.1701, 1.0557, 1.3291),
          ('ObsUse-Window', 1897, 'obsuse_window', 1.1120, 1.1692, 1.0413, 1.3235),
          ('RAVEN-Design', 1898, 'raven', 1.1911, 1.2630, 1.0924, 1.2334),
          ('RAVEN-NoDesign', 1899, 'raven_wo_design', 1.1131, 1.1703, 1.0165, 1.2949)]
    for row, line, arm, r, w, dg, dcs in t3:
        add('Table III (UA)', line, row, 'RMSE_mu', r, arm, 'RMSE', '%.4f')
        add('Table III (UA)', line, row, 'WorstGroupRMSE', w, arm, 'WG', '%.4f')
        add('Table III (UA)', line, row, 'Delta_group', dg, arm, 'Dg', '%.4f')
        add('Table III (UA)', line, row, 'Delta_c_s', dcs, arm, 'Dcs', '%.4f')

    app = [('FedAvg-Window', 1877, 'fedavg_window', 1.1119, 1.0446, 1.3138),
           ('FedAsync-Window', 1878, 'fedasync_window', 1.1119, 1.0451, 1.3137),
           ('TimeAlign-Agg', 1879, 'flamf_timealign_adapted', 1.1120, 1.0448, 1.3145),
           ('Local-Hajek', 1880, 'local_hajek', 1.1882, 1.1218, 1.2621),
           ('TwoStage-Hajek', 1881, 'twostage_hajek', 1.2160, 1.1196, 1.2406),
           ('Inst-Cal', 1882, 'inst_cal', 1.1911, 1.0924, 1.2334),
           ('Debt-Cal', 1883, 'debt_cal', 1.1144, 1.0175, 1.2948),
           ('RAVEN-Design', 1884, 'raven', 1.1911, 1.0924, 1.2334),
           ('RAVEN-SimOracle', 1885, 'raven_simoracle', 1.1914, 1.0922, 1.2342)]
    for row, line, arm, r, dg, dcs in app:
        add('appendix tab:app_e3_uair', line, row, 'RMSE_mu', r, arm, 'RMSE', '%.4f')
        add('appendix tab:app_e3_uair', line, row, 'Delta_group', dg, arm, 'Dg', '%.4f')
        add('appendix tab:app_e3_uair', line, row, 'Delta_c_s', dcs, arm, 'Dcs', '%.4f')

    blocks = [('FedAvg-Window', 1985, 'fedavg_window', (1.1015, 1.1144, 1.1690, 1.0721), 1.1690),
              ('TwoStage-Hajek', 1986, 'twostage_hajek', (1.2009, 1.2194, 1.2907, 1.1800), 1.2907),
              ('FedAU-Window', 1987, 'fedau_window', (1.1023, 1.1153, 1.1701, 1.0729), 1.1701),
              ('ObsUse-Window', 1988, 'obsuse_window', (1.1016, 1.1145, 1.1692, 1.0721), 1.1692),
              ('RAVEN-Design', 1989, 'raven', (1.1779, 1.1953, 1.2630, 1.1552), 1.2630),
              ('RAVEN-NoDesign', 1990, 'raven_wo_design', (1.1025, 1.1155, 1.1703, 1.0732), 1.1703)]
    for row, line, arm, gs, wg in blocks:
        for i, g in enumerate(gs):
            add('appendix tab:app_block_rmse', line, row, 'g%d' % i, g, arm, 'g%d' % i, '%.4f')
        add('appendix tab:app_block_rmse', line, row, 'WG', wg, arm, 'WG', '%.4f')

    # Table IV: relative change (%) of the ablated arm against RAVEN-MCS
    abl = [('Design', 2002, 'raven_wo_design'), ('Obs', 2003, 'raven_wo_obs'),
           ('Use', 2004, 'raven_wo_use'), ('Inst', 2005, 'raven_wo_inst_gen2'),
           ('Debt', 2006, 'raven_wo_debt')]
    printed_t4 = {'Design': (-6.943368495586542, 4.9898350597219965, -6.553093815666225, -6.875242584162889),
                  'Obs': (0.1230828111266689, 0.0219984512770321, -0.0097196306106393, -0.0102288937108689),
                  'Use': (0.0137939238456002, -0.0135605115759798, 0.023973670577847, 0.0252184289979606),
                  'Inst': (-0.0894468167512562, -0.1428586189549358, 0.1306837550913353, 0.1363753990751629),
                  'Debt': (0.0043063951349345, 0.0023896482868883, 0.0007291917853553, 0.000775232954355)}
    full = resolved['raven']
    for comp, line, arm in abl:
        for i, (metric, key) in enumerate((('Delta_group', 'Dg'), ('Delta_c_s', 'Dcs'),
                                           ('RMSE_mu', 'RMSE'), ('Tail_RMSE', 'Tail'))):
            a = resolved.get(arm, {}).get(key)
            f = full.get(key)
            new = 100.0 * (a[0] - f[0]) / f[0] if (a and f) else None
            cells.append({'table': 'Table IV (UA)', 'line': line, 'row': comp, 'column': metric,
                          'printed_old': round(printed_t4[comp][i], 6),
                          'action': ('recompute' if (new is not None and key in ('RMSE', 'Tail'))
                                     else 'theta (keep)') if new is not None else 'needs theta eval',
                          'theta_new': ('%+.6f' % new) if new is not None else None,
                          'theta_std': None, 'arm': arm,
                          'note': 'model-free structure' if key in ('Dg', 'Dcs') else ''})

    with (HERE / 'C3_CELL_DIFF.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells[0].keys()))
        w.writeheader()
        w.writerows(cells)

    # ---- derived numbers ----
    def rel(key, arm_ablated):
        """(ablated - full) / full in %, full = RAVEN-MCS."""
        f = resolved['raven'][key][0]
        return 100.0 * (resolved[arm_ablated][key][0] - f) / f

    derived = {
        'design_cost_RMSE_pct': rel('RMSE', 'raven_wo_design'),
        'design_cost_Dg_pct': rel('Dg', 'raven_wo_design'),
        'design_cost_Dcs_pct': rel('Dcs', 'raven_wo_design'),
        'design_cost_Tail_pct': rel('Tail', 'raven_wo_design'),
        'uair_design_gate_est_RMSE_pct': 100.0 * (resolved['raven']['RMSE'][0] - resolved['raven_wo_design']['RMSE'][0]) / resolved['raven_wo_design']['RMSE'][0],
        'uair_design_gate_oracle_RMSE_pct': 100.0 * (resolved['raven_simoracle']['RMSE'][0] - resolved['raven_wo_design']['RMSE'][0]) / resolved['raven_wo_design']['RMSE'][0],
        'uair_design_gate_est_Dg_pct': 100.0 * (resolved['raven']['Dg'][0] - resolved['raven_wo_design']['Dg'][0]) / resolved['raven_wo_design']['Dg'][0],
        'uair_wg_vs_twostage_pct': 100.0 * (resolved['twostage_hajek']['WG'][0] - resolved['raven']['WG'][0]) / resolved['raven']['WG'][0],
        'uair_wg_vs_fedavg_pct': 100.0 * (resolved['raven']['WG'][0] - resolved['fedavg_window']['WG'][0]) / resolved['fedavg_window']['WG'][0],
        'uair_wg_vs_fedau_pct': 100.0 * (resolved['raven']['WG'][0] - resolved['fedau_window']['WG'][0]) / resolved['fedau_window']['WG'][0],
        'uair_wg_vs_obsuse_pct': 100.0 * (resolved['raven']['WG'][0] - resolved['obsuse_window']['WG'][0]) / resolved['obsuse_window']['WG'][0],
    }
    # TEST-seed-only worst-group comparison (the 2.46% statement)
    def wg_series(arm):
        return e2.get(arm, {}).get('WG', [])
    rv, tv = wg_series('raven'), wg_series('twostage_hajek')
    if len(rv) == len(tv) == 20:
        idx = [i for i, s in enumerate(SEEDS) if s in TEST_SEEDS]
        diff = [(tv[i] - rv[i]) / rv[i] * 100.0 for i in idx]
        derived['uair_test_wg_raven_vs_twostage_pct'] = float(np.mean(diff))
        derived['uair_test_wg_wins'] = int(sum(1 for d in diff if d > 0))
    report = {'resolved': {a: {k: list(v) for k, v in d.items()} for a, d in resolved.items()},
              'derived': derived,
              'gen2_theta_triggered': {str(k): v for k, v in gen2_theta.items()}}
    (HERE / 'C3_CELL_DIFF.json').write_text(json.dumps(report, indent=2, default=float), encoding='utf-8')

    print('\n=== resolved means (theta) ===')
    for arm in sorted(resolved):
        r = resolved[arm]
        print('%-22s RMSE=%s WG=%s Dg=%s Dcs=%s Tail=%s' % (
            arm,
            ('%.4f' % r['RMSE'][0]) if 'RMSE' in r else 'n/a',
            ('%.4f' % r['WG'][0]) if 'WG' in r else 'n/a',
            ('%.4f' % r['Dg'][0]) if 'Dg' in r else 'n/a',
            ('%.4f' % r['Dcs'][0]) if 'Dcs' in r else 'n/a',
            ('%.4f' % r['Tail'][0]) if 'Tail' in r else 'n/a'))
    print('\n=== derived ===')
    for k, v in derived.items():
        print('%-34s %s' % (k, ('%+.4f' % v) if isinstance(v, float) else v))
    print('\n=== cells to change ===')
    for c in cells:
        if c['action'].startswith(('MIRROR', 'recompute', 'needs', 'unmatched')):
            print('%-26s L%-5s %-16s %-15s printed=%-12s -> %-12s %s' %
                  (c['table'], c['line'], c['row'], c['column'], c['printed_old'],
                   c['theta_new'], c['action']))


if __name__ == '__main__':
    main()
