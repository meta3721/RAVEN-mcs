"""Minimal: what does the trained aggregator return for one logged window?"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51_oracle as O                                                      # noqa: E402
import w1_v4_train as T                                                        # noqa: E402
from raven_mcs.aggregation.base import WindowAggregateInput                    # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound        # noqa: E402

ds, arm, seed = "sensorscope", "proj_beta", 30001
pi = {d: W.pi_tar_for(d) for d in W.DS}
ri = O.run_inputs(ds, arm, seed, pi[ds])
case, act = ri["case"], ri["act"]
for j in (0, 1, 2, 3, 4):
    K = len(case["clients"][j])
    b = np.asarray(act[j]["beta_hat"], dtype=float)
    bn = b / b.sum()
    payload = WindowAggregateInput(
        client_ids=[str(c) for c in act[j]["active_clients"]],
        raw_counts=np.zeros(K), total_masses=np.zeros(K),
        compositions=np.asarray(case["M"][j], dtype=float), beta_hat=b,
        mu=np.asarray(case["mu"], dtype=float))
    agg = T.ProjBetaAggregator()
    a_agg = np.asarray(agg.compute_server_weights(payload), dtype=float)
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    a_or, kind, mult = O.project_Cr(bn, ab, eb)
    import w1_v4_proj as P
    a_proj = np.asarray(P.proj_Cr(bn, ab, eb, K), dtype=float)
    print("win=%d K=%d win_id=%s" % (j, K, act[j].get("window_id")))
    print("   logged alpha = %s  sum=%.10f" % (np.round(np.asarray(act[j]["alpha"], dtype=float), 8),
                                               float(np.sum(act[j]["alpha"]))))
    print("   aggregator   = %s" % np.round(a_agg, 8))
    print("   oracle       = %s kind=%s" % (np.round(a_or, 8), kind))
    print("   v4_proj_Cr   = %s" % np.round(a_proj, 8))
    print("   beta/        = %s sum=%.6f   M rowsum=%s" %
          (np.round(bn, 8), bn.sum(), np.round(np.asarray(case["M"][j]).sum(axis=1), 4)))
