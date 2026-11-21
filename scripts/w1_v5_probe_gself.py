"""W1 round v5 - diagnosis of the two A1-G-self failures (read-only, round_v5 only).

Rebuilds alpha for the failing runs and inspects the mechanism: per-window L-inf,
sum(alpha) of the logged vs rebuilt alpha (window_runner.py L1151 renormalizes when
|sum(alpha) - 1| > 1e-8), and the solving-path signature.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                     # noqa: E402
import w1_v5_a1 as A                                                      # noqa: E402
from raven_mcs.aggregation.base import WindowAggregateInput               # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5"


def main() -> None:
    pi = {d: W.pi_tar_for(d) for d in ("uair",)}
    rows = []
    for seed in (30001, 30011):
        run_dir = A.TRAIN / "uair" / "proj_beta" / f"seed{seed}"
        wm = W.load_json(run_dir / "window_metrics.json")
        act = W.active_windows(wm)
        case = W.build_case("uair", "R_on", "raven_wo_use", seed, pi["uair"])
        agg = A.CLASSES["proj_beta"]()
        first, worst = None, 0.0
        sum_dev_logged, sum_dev_rebuilt = [], []
        for j in range(case["n"]):
            b = np.asarray(act[j]["beta_hat"], dtype=float)
            K = len(case["clients"][j])
            payload = WindowAggregateInput(
                client_ids=[str(c) for c in act[j]["active_clients"]],
                raw_counts=np.zeros(K), total_masses=np.zeros(K),
                compositions=np.asarray(case["M"][j], dtype=float),
                beta_hat=b, mu=np.asarray(case["mu"], dtype=float))
            a = np.asarray(agg.compute_server_weights(payload), dtype=float)
            lg = np.asarray(act[j]["alpha"], dtype=float)
            d = float(np.max(np.abs(a - lg)))
            if first is None and d > 0.0:
                first = j
            worst = max(worst, d)
            sum_dev_logged.append(abs(float(lg.sum()) - 1.0))
            sum_dev_rebuilt.append(abs(float(a.sum()) - 1.0))
            if d > 0.0:
                rows.append({"seed": seed, "window": j, "K": K,
                             "sum_logged_minus_1": float(lg.sum()) - 1.0,
                             "sum_rebuilt_minus_1": float(a.sum()) - 1.0,
                             "linf": d,
                             "beta_sum": float(b.sum()),
                             "n_nonzero_rebuilt": int((a > 1e-12).sum()),
                             "n_nonzero_logged": int((lg > 1e-12).sum())})
        print("seed %d n_windows=%d first_diverging=%s worst_linf=%.3e "
              "max|sum_logged-1|=%.3e max|sum_rebuilt-1|=%.3e"
              % (seed, case["n"], first, worst, max(sum_dev_logged),
                 max(sum_dev_rebuilt)), flush=True)
    d = json_rows = rows[:40]
    (OUT / "A1_GSELF_FAIL_DIAG.json").write_text(
        json.dumps({"rows": json_rows}, indent=2, default=str), encoding="utf-8")
    for r in json_rows[:12]:
        print(r)


if __name__ == "__main__":
    main()
