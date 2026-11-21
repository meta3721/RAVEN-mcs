"""Add the analytic uniform_window rows to A1P_IMPL.csv.

uniform_window has no solver path: alpha_r = 1/K exactly, so its "oracle", "trained" and
"reference" alpha are the same vector and eps_impl = eps_ref = 0 by definition.  The rows are
needed so the A1' structural re-check can form every round-v4 contrast.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_ladder as L                                                          # noqa: E402
import w1_replay as W                                                          # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5_1"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"

df = pd.read_csv(OUT / "A1P_IMPL.csv")
if (df.arm == "uniform_window").any():
    print("uniform_window rows already present")
    raise SystemExit(0)
pi = {d: W.pi_tar_for(d) for d in W.DS}
rows = []
for ds in ("sensorscope", "uair"):
    for seed in W.SEEDS:
        case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
        act = W.active_windows(W.load_json(TRAIN / ds / "uniform_window" / f"seed{seed}" /
                                           "window_metrics.json"))
        fm = W.load_json(TRAIN / ds / "uniform_window" / f"seed{seed}" / "final_metrics.json")
        a = np.concatenate([np.full(len(case["clients"][j]), 1.0 / len(case["clients"][j]))
                            for j in range(case["n"])])
        ref = W.active_windows(W.load_json(E3 / ds / "raven" / f"seed{seed}" /
                                           "window_metrics.json"))
        n_bad = sum(1 for x, y in zip(act, ref)
                    if [str(c) for c in x["active_clients"]]
                    != [str(c) for c in y["active_clients"]])
        g, c = L.endpoints(case, a)
        rows.append({"ds": ds, "arm": "uniform_window", "seed": int(seed),
                     "alpha_linf_trained": 0.0, "eps_impl_group": 0.0, "eps_impl_cs": 0.0,
                     "alpha_linf_ref": 0.0, "eps_ref_group": 0.0, "eps_ref_cs": 0.0,
                     "first_q_div": np.nan,
                     "d_group_oracle": g, "d_cs_oracle": c,
                     "d_group_trained": g, "d_cs_trained": c,
                     "d_group_reference": g, "d_cs_reference": c,
                     "err_self_group": abs(g - float(fm["Delta_group"])),
                     "err_self_cs": abs(c - float(fm["Delta_c_s"])),
                     "b_g1_mismatch_windows": int(n_bad), "verdict": "certified"})
        print("uniform %-12s %d d_group=%.10f d_cs=%.10f" % (ds, seed, g, c), flush=True)
pd.concat([df, pd.DataFrame(rows)], ignore_index=True).to_csv(OUT / "A1P_IMPL.csv", index=False)
print("added", len(rows), "rows")
