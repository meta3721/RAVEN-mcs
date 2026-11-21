"""Scan all probed windows and rank the KKT stationarity diagnostics (development; writes nothing)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51a_oracle as O                                                     # noqa: E402

TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"


def main() -> None:
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rows = []
    for ds in ("sensorscope", "uair"):
        pi = W.pi_tar_for(ds)
        for arm in ("proj_beta", "proj_beta_debt"):
            for seed in range(30001, 30001 + n_runs):
                case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi)
                if case is None:
                    continue
                wm = W.load_json(TRAIN / ds / arm / ("seed%d" % seed) / "window_metrics.json")
                by = {int(w["window_id"]): w for w in W.active_windows(wm)}
                betas = [np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
                         for j in range(case["n"])]
                if arm == "proj_beta":
                    a_or, diag = O.oracle_proj_beta(betas, case)
                    qs = [None] * case["n"]
                else:
                    a_or, qs, diag = O.oracle_debt_seq(case, betas)
                off = 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    a = a_or[off:off + K]
                    off += K
                    d = diag[j]
                    if arm == "proj_beta":
                        res = O.audit_projection(a, d["v"], case["a_bar"][j], case["e_bar"][j],
                                                 d["mult"])
                    else:
                        res = O.audit_debt(a, case["M"][j], qs[j], d["beta"],
                                           case["a_bar"][j], case["e_bar"][j], d["mult"])
                    rows.append({"ds": ds, "arm": arm, "seed": seed, "j": j, "K": K,
                                 "kind": d["kind"], "stat_raw": res["stat_raw"],
                                 "stat_fit": res["stat_fit"], "cs": res["cs"],
                                 "primal": res["primal"], "n_free": res["n_free"],
                                 "n_at_hi": res["n_at_hi"], "n_at_lo": res["n_at_lo"],
                                 "u": res["u"], "tau_s": res["tau_scaled"],
                                 "tau_fit": res["tau_fit"], "lam_s": res["lam_scaled"],
                                 "norm2": res["norm2"], "target": res["norm2_target"],
                                 "sum": float(a.sum())})
    import pandas as pd
    df = pd.DataFrame(rows)
    print("windows", len(df))
    print(df.groupby("kind")[["stat_raw", "stat_fit", "cs", "primal"]].max().to_string())
    worst = df.sort_values("stat_fit", ascending=False).head(12)
    print(worst.to_string(index=False))
    print("max stat_raw", df.stat_raw.max(), "max stat_fit", df.stat_fit.max())


if __name__ == "__main__":
    main()
