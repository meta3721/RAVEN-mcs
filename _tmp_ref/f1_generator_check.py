"""F-1-O generator validation.

1. theta = 0 must reproduce the published trace's RNG-driven fields bit-for-bit (proves the
   copied loop is faithful and that no extra draws were introduced).
2. theta = 1.0 must (a) keep the per-block mean of p equal to the published block rate,
   (b) create within-stratum dispersion, and (c) keep min p above p_min = 0.05.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import M_MC
from raven_mcs.e3.canary.dataset_load import (  # noqa: E402
    load_horizon, load_paper_dataset, load_spatial_to_client,
)
from raven_mcs.e3.real_runner.generator_r3_score import generate_f1o_trace  # noqa: E402
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402

PUB = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces"


def prep(dataset: str):
    ds = load_paper_dataset(ROOT, dataset)
    mapping = load_spatial_to_client(ROOT, dataset)
    atomic, _ = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset, root=ROOT)
    n_windows = int(load_horizon(ROOT, dataset)["chosen_E3_formal_windows"])
    return atomic, mapping, n_windows


def keyframe(trace) -> list[tuple]:
    ev = trace.events
    return sorted(
        (int(r.window_id), str(r.client_id), int(r.tau), int(r.U),
         round(float(r.model_age), 12), round(float(r.oracle_q), 12),
         len(r.observed_unit_ids) if r.observed_unit_ids is not None else 0)
        for r in ev.itertuples(index=False)
    )


def published_keyframe(dataset: str, seed: int) -> list[tuple]:
    f = PUB / dataset / f"seed{seed}" / "training_eventtrace" / "events.parquet"
    df = pd.read_parquet(f, columns=["window_id", "client_id", "tau", "U", "model_age",
                                     "oracle_q", "observed_unit_ids"])
    out = []
    for r in df.itertuples(index=False):
        obs = r.observed_unit_ids
        if isinstance(obs, str):
            try:
                n = len(json.loads(obs))
            except Exception:
                n = 0
        else:
            n = 0 if obs is None else len(obs)
        out.append((int(r.window_id), str(r.client_id), int(r.tau), int(r.U),
                    round(float(r.model_age), 12), round(float(r.oracle_q), 12), n))
    return sorted(out)


def report(dataset: str, theta: float, atomic, mapping, n_windows, seed=30001):
    trace, opp, pobs, audit = generate_f1o_trace(
        dataset=dataset, atomic=atomic, spatial_to_client=mapping,
        seed=seed, num_windows=n_windows, theta=theta, m_mc=M_MC,
    )
    return trace, opp, pobs, audit


def main() -> int:
    for dataset in ("sensorscope", "uair"):
        atomic, mapping, n_windows = prep(dataset)
        print(f"\n================ {dataset} (seed 30001, {n_windows} windows) ================")

        # --- 1. theta = 0 faithfulness -------------------------------------
        t0, opp0, p0, a0 = report(dataset, 0.0, atomic, mapping, n_windows)
        kf_new, kf_pub = keyframe(t0), published_keyframe(dataset, 30001)
        same = kf_new == kf_pub
        n_diff = sum(1 for a, b in zip(kf_new, kf_pub) if a != b)
        print(f"[theta=0] event rows: new={len(kf_new)} published={len(kf_pub)} "
              f"identical={same} differing={n_diff}")

        # observed-set equality
        f = PUB / dataset / "seed30001" / "training_eventtrace" / "events.parquet"
        pubdf = pd.read_parquet(f, columns=["window_id", "client_id", "observed_unit_ids"])
        pubobs = {}
        for r in pubdf.itertuples(index=False):
            ids = r.observed_unit_ids
            if isinstance(ids, str):
                ids = json.loads(ids)
            pubobs[(int(r.window_id), str(r.client_id))] = set(ids or [])
        newobs = {}
        for r in t0.events.itertuples(index=False):
            newobs[(int(r.window_id), str(r.client_id))] = set(r.observed_unit_ids or [])
        mism = sum(1 for k in pubobs if pubobs[k] != newobs.get(k, set()))
        print(f"[theta=0] observed-unit sets differing: {mism} of {len(pubobs)}")

        # --- 2. theta = 1.0 manipulation ----------------------------------
        t1, opp1, p1, a1 = report(dataset, 1.0, atomic, mapping, n_windows)
        print(f"[theta=1.0] block intercepts: "
              f"{ {k: round(v, 4) for k, v in a1['block_intercepts'].items()} }")
        print(f"[theta=1.0] published block rates: {a1['published_block_rates']}")
        pt = a1["p_by_block_tercile"]
        for b in sorted({int(k.split('|')[0]) for k in pt}):
            vals = {z: round(pt[f'{b}|{z}'], 6) for z in (-1, 0, 1)}
            mean = (vals[-1] + vals[0] + vals[1]) / 3.0
            print(f"    block {b}: p(z=-1)={vals[-1]}  p(z=0)={vals[0]}  p(z=+1)={vals[1]}"
                  f"   tercile-equal mean={mean:.6f}")

        pm = p1["p_obs_true"].to_numpy(float)
        print(f"[theta=1.0] realized atomic p: n={len(pm)} min={pm.min():.6f} "
              f"max={pm.max():.6f} mean={pm.mean():.6f}")
        # within-stratum dispersion of the realized p
        merged = p1.merge(
            atomic[["unit_id", "opportunity_stratum"]].assign(unit_id=lambda d: d["unit_id"].astype(str)),
            left_on="atomic_unit_id", right_on="unit_id", how="left")
        disp = merged.groupby("opportunity_stratum")["p_obs_true"].nunique()
        print(f"[theta=1.0] distinct p per stratum: mean={disp.mean():.2f} "
              f"max={disp.max()} (0/1 would mean stratum-constant)")
        no = t1.events["observed_unit_ids"].apply(lambda v: len(v) if v is not None else 0)
        print(f"[theta=1.0] observed units per client-window: mean={no.mean():.3f} "
              f"total={int(no.sum())}")
        n0 = t0.events["observed_unit_ids"].apply(lambda v: len(v) if v is not None else 0)
        print(f"[theta=0.0] observed units per client-window: mean={n0.mean():.3f} "
              f"total={int(n0.sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
