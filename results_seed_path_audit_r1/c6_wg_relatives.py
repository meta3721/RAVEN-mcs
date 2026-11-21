"""Step 1d — verify the §V worst-group relatives against the theta series.

Checks the four printed relatives (main.tex 1816, 1828, 1830, and 1836) under
three conventions, using the E2 theta WorstGroupRMSE cells (the column the
manuscript prints).
"""
from __future__ import annotations

import csv
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEEDS = list(range(30001, 30021))
TEST = list(range(30011, 30021))


def wg(arm):
    out = {}
    with (ROOT / 'results_active_set_repair/round_v1/E2_UAIR_CELLS.csv').open() as fh:
        for row in csv.DictReader(fh):
            if row['method'] == arm:
                out[int(row['seed'])] = float(row['WorstGroupRMSE_std'])
    return {s: out[s] for s in SEEDS}


def report(label, arm_a, arm_b, seeds):
    a, b = wg(arm_a), wg(arm_b)
    av = np.asarray([a[s] for s in seeds])
    bv = np.asarray([b[s] for s in seeds])
    psm_b = 100.0 * float(np.mean((av - bv) / bv))
    psm_a = 100.0 * float(np.mean((av - bv) / av))
    rom = 100.0 * (av.mean() - bv.mean()) / bv.mean()
    print('%-42s ratio-of-means=%+7.3f  per-seed/%s=%+7.3f  per-seed/%s=%+7.3f'
          % (label, rom, arm_b, psm_b, arm_a, psm_a))


def main() -> None:
    print('--- U-Air Design row vs same-block baselines ---')
    report('TRAIN+TEST (20 seeds) vs FedAU', 'raven', 'fedau_window', SEEDS)
    report('TRAIN+TEST (20 seeds) vs ObsUse', 'raven', 'obsuse_window', SEEDS)
    report('TEST (30011-30020) vs FedAU', 'raven', 'fedau_window', TEST)
    report('TEST (30011-30020) vs ObsUse', 'raven', 'obsuse_window', TEST)
    print('\n--- Design-on family, worst group ---')
    report('TEST vs TwoStage', 'raven', 'twostage_hajek', TEST)
    report('TEST vs Local-Hajek', 'raven', 'local_hajek', TEST)
    print('\n--- NoDesign row (the +0.5% tolerance claim) ---')
    report('ALL20 vs FedAU', 'raven_wo_design', 'fedau_window', SEEDS)
    report('ALL20 vs ObsUse', 'raven_wo_design', 'obsuse_window', SEEDS)
    report('TEST vs FedAU', 'raven_wo_design', 'fedau_window', TEST)
    report('TEST vs ObsUse', 'raven_wo_design', 'obsuse_window', TEST)


if __name__ == '__main__':
    main()
