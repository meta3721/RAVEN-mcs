"""One-cell diagnostic: is the frozen c-s normalization a no-op, and where does the
LP-vs-frozen c-s difference at the lambda=inf optimum come from?"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client  # noqa: E402
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import build_pi_tar_client_stratum          # noqa: E402
import w1_replay as W                                                                  # noqa: E402

d, ruler, src, seed = "sensorscope", "R_on", "raven_wo_debt", 30001
pi = pi_tar_for = build_pi_tar_client_stratum(
    pd.read_parquet(ROOT / "data/processed" / d / "atomic_units.parquet"),
    load_spatial_to_client(ROOT, d), split="test")
case = W.build_case(d, ruler, src, seed, pi)

ps = case["pair_state"]
S = case["n"]


def raw_and_norm(alpha, label):
    amap = {}
    off = 0
    for j in range(S):
        K = len(case["clients"][j])
        amap[case["wids"][j]] = {c: float(alpha[off + i]) for i, c in enumerate(case["clients"][j])}
        off += K
    sub = ps.copy()
    sub["a"] = [float(amap.get(int(w), {}).get(str(c), np.nan))
                for w, c in zip(sub["window"], sub["client_id"])]
    sub = sub[sub["a"].notna()]
    key = sub["client_id"].astype(str) + "::" + sub["opportunity_stratum_id"].astype(str)
    agg = (sub["a"] * sub["w_atomic"].astype(float)).groupby(key).sum() / float(S)
    tot = float(agg.sum())
    normalised = W.delta_cs(ps, amap, S, pi)
    raw = float(sum(abs(float(agg.get(k, 0.0)) - float(pi.get(k, 0.0)))
                    for k in set(agg.index) | set(pi.keys())))
    # per-window alpha mass
    masses, off = [], 0
    for j in range(S):
        K = len(case["clients"][j])
        masses.append(float(alpha[off:off + K].sum()))
        off += K
    print(f"{label}: tot={tot:.17g}  |tot-1|={abs(tot-1):.3e}  "
          f"raw={raw:.15g}  normalised={normalised:.15g}  |raw-norm|={abs(raw-normalised):.3e}")
    print(f"    per-window sum alpha: max|sum-1|={max(abs(m-1) for m in masses):.3e}  "
          f"n_keys_agg={len(agg)} n_keys_pi={len(pi)} n_keys_union={len(set(agg.index)|set(pi.keys()))}")


unif = np.concatenate([np.full(len(c), 1.0 / len(c)) for c in case["clients"]])
raw_and_norm(unif, "uniform      ")
raw_and_norm(case["alpha_arm"], "ruler arm    ")

# lambda=inf optimum re-solved here so alpha is available
sweep = W.solve_joint(case, lams=[float("inf")])
a_inf = sweep[0]["alpha"]
print("lambda=inf: front_cs(LP raw) =", sweep[0]["front_cs"], "status", sweep[0]["status"])
raw_and_norm(a_inf, "lambda=inf opt")
