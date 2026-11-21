"""Split the phi zero set into (i) keys absent from the test-split target map and
(ii) keys present with an explicit zero value.

Reuses the same construction path as scripts/compute_scd_phi.py so the numbers are
comparable to the manuscript's frozen table.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path('.').resolve()
sys.path.insert(0, str(ROOT / 'src'))

from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_spatial_to_client  # noqa: E402
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402

for dataset in ('sensorscope', 'uair'):
    atomic = pd.read_parquet(ROOT / 'data' / 'processed' / dataset / 'atomic_units.parquet')
    atomic_sealed, _ = apply_sealed_opportunity_stratum(atomic, dataset=dataset, root=ROOT)
    spatial_to_client = load_spatial_to_client(ROOT, dataset)
    frame = atomic_sealed.copy()
    if 'target_group_main' not in frame.columns:
        frame['target_group_main'] = frame['target_group'].astype(str)

    pi_frame = build_pi_target(frame, spatial_to_client, split='test')
    pi_target = {(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
                 for r in pi_frame.itertuples()}

    keys = list(pi_target)
    n_pos = sum(1 for v in pi_target.values() if v > 0)
    n_zero_present = len(keys) - n_pos

    unit_stratum = {str(r.unit_id): str(r.opportunity_stratum) for r in atomic_sealed.itertuples(index=False)}
    unit_client = {str(r.unit_id): str(spatial_to_client[str(r.spatial_id)]) for r in atomic_sealed.itertuples(index=False)}

    train = atomic_sealed.loc[atomic_sealed['split'].astype(str) == 'train']
    train_test = atomic_sealed.loc[atomic_sealed['split'].astype(str) == 'test']

    # pair-level coverage
    train_pairs = {(unit_client[str(u)], unit_stratum[str(u)]) for u in train['unit_id'].astype(str)}
    test_pairs = {(unit_client[str(u)], unit_stratum[str(u)]) for u in train_test['unit_id'].astype(str)}

    # unit-level partition of the zero set
    n = missing = explicit = pos = 0
    for uid in train['unit_id'].astype(str).unique():
        k, s = unit_client[uid], unit_stratum[uid]
        n += 1
        if (k, s) not in pi_target:
            missing += 1
        elif pi_target[(k, s)] <= 0.0:
            explicit += 1
        else:
            pos += 1

    print('=' * 74)
    print(dataset.upper())
    print('=' * 74)
    print('  pi_target map (built from TEST split)')
    print('    distinct (k,s) keys      : %d' % len(keys))
    print('    keys with pi_tar > 0     : %d' % n_pos)
    print('    keys present with 0      : %d' % n_zero_present)
    print('    == test-split pair set?  : %s   (test pairs = %d)'
          % (set(keys) == test_pairs, len(test_pairs)))
    print()
    print('  train risk units: %d' % n)
    print('    pi_tar > 0               : %6d  (%.2f%%)' % (pos, 100 * pos / n))
    print('    KEY ABSENT from map      : %6d  (%.2f%%)   <-- coverage artifact'
          % (missing, 100 * missing / n))
    print('    present but zero         : %6d  (%.2f%%)' % (explicit, 100 * explicit / n))
    print('    phi as published         : %6d  (%.2f%%)  = absent + present-zero'
          % (missing + explicit, 100 * (missing + explicit) / n))
    print('    phi if absent keys were  : %6d  (%.2f%%)'
          % (explicit, 100 * explicit / n))
    print()
    print('  pair coverage: train pairs %d, test pairs %d, train-only %d'
          % (len(train_pairs), len(test_pairs), len(train_pairs - test_pairs)))
    print()
    sys.stdout.flush()
