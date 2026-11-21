"""Step 1e — theta metrics for the four remaining affected E3 U-Air arms.

FedAvg-Window, FedAsync-Window, TimeAlign-Agg and Debt-Cal also carry the
inactive-final window at 30007/30016/30018 (A1 sweep), so the per-seed values in
figure_data/FIG_E3_E3_PREDICTION_RISK.csv are mirror-based for those rows too.
This evaluates their checkpoints at the theta copy for RMSE_mu / Head / Tail.

Writes C7_E3_ARMS_THETA.csv.
"""
from __future__ import annotations

import csv
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
ARMS = ('fedavg_window', 'fedasync_window', 'flamf_timealign_adapted', 'debt_cal')


def main() -> None:
    ds = load_paper_dataset(ROOT, 'uair')
    bundle = production_target_bundle(root=ROOT, dataset_name='uair', dataset=ds)
    mu = np.asarray(bundle['mu'], dtype=np.float64)
    ht = bundle['head_tail']
    rows = []
    for arm in ARMS:
        for seed in TRIGGERED:
            ck = E3 / arm / ('seed%d' % seed) / 'checkpoints' / 'final.pt'
            model = CommonNDMF(num_spatial=ds.num_spatial)
            model.load_state_dict(load_state(ck))
            got = metrics_at_theta(predict(model, ds), mu, ht['head_group_ids'], ht['tail_group_ids'])
            rows.append({'arm': arm, 'seed': seed, **{k: float(v) for k, v in got.items()
                                                      if v is not None}})
            print('%-24s seed%d RMSE=%.6f tail=%.6f head=%.6f' %
                  (arm, seed, got['RMSE_mu'], got['Tail_RMSE'], got['Head_RMSE']))
    with (HERE / 'C7_E3_ARMS_THETA.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print('\nwrote C7_E3_ARMS_THETA.csv')


if __name__ == '__main__':
    main()
