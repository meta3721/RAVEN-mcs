"""Is the 'worse than a constant' result a train/test target-location shift?

If the training targets are centred near zero while the test targets sit far away, then predicting ~0 is
correct in the training convention and the constant comparison is measuring the wrong space.  This
script prints the target location and spread per split, per block, both unweighted and under the
paper's own target-mass weights.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402

N_GROUPS = {"sensorscope": 220, "uair": 144, "traffic": 172}


def mu_for(dataset, n_groups: int, split: str):
    atomic = dataset.atomic_df.copy()
    if n_groups == 4:
        atomic["target_group_main"] = RepeatableTimeOfDayMapper().map(atomic)
    else:
        atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
    tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split=split)
    return tgt, atomic


for block in ("sensorscope", "uair", "traffic"):
    ds = load_paper_dataset(ROOT, block)
    df = ds.atomic_df
    print(f"\n=== {block} ===")
    print(f"  atomic_df columns: target_value={'target_value' in df.columns} split={'split' in df.columns}")
    print(f"  splits present: {sorted(df['split'].unique())}")
    for split in ("train", "validation", "test"):
        sub = df[df["split"] == split]
        if len(sub) == 0:
            continue
        y = sub["target_value"].astype(float)
        print(f"  {split:<11} n={len(sub):<7} mean={y.mean():+9.4f} sd={y.std(ddof=0):8.4f} "
              f"min={y.min():+9.3f} max={y.max():+9.3f}")
    # target-mass weighted location per split (the space the metric lives in)
    for split in ("train", "test"):
        tgt, atomic = mu_for(ds, N_GROUPS[block], split)
        mu = np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(N_GROUPS[block])])
        sub = df[df["split"] == split]
        # per-group weighted mean of the target using the built group masses
        tgt2 = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split=split)
        gm = np.asarray([float(tgt2.group_mass.get(str(g), 0.0)) for g in range(N_GROUPS[block])])
        gm = gm / gm.sum() if gm.sum() else gm
        print(f"  {split:<11} target-mass-weighted mean={float(np.sum(gm * gm)):.6f} "
              f"(mass vector sums to {gm.sum():.6f}, groups={len(gm)})")
    print(f"  train total target mass = {float(df[df['split']=='train']['target_value'].sum()):.4f}")
