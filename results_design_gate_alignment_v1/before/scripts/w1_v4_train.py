"""Part B (round v4): train three new rules with policy identical to `raven`.

Arms (server weights only; policy copied from `raven`):
  uniform_window  : alpha = 1/K
  proj_beta       : alpha = proj_Cr(beta_hat)
  proj_beta_debt  : argmin_{C_r} -kappa Q^T M a + 1/2||a - beta_hat||^2,
                    Q_{r+1} = max(Q_r + 0.01 (mu - M a), 0), Q_0 = 0, kappa = 1000

Registration is class/dict-level only (patches window_runner.get_aggregator and POLICY_MAP);
src/ is not modified.

Phases:
  --phase g0     : B-G0, re-run the frozen `raven` arm with the same driver (2 runs)
  --phase train  : the arm grid
  --phase check  : B-G1/B-G2/B-G3 against the round-v3/v4 read-only replays
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import raven_mcs.training.window_runner as wr                                  # noqa: E402
from raven_mcs.aggregation import method_policy as mp                          # noqa: E402
from raven_mcs.aggregation.base import Aggregator, WindowAggregateInput        # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound        # noqa: E402
from w1_v4_proj import proj_Cr                                                 # noqa: E402

ARMS = ("uniform_window", "proj_beta", "proj_beta_debt")
KAPPA = 1000.0
ETA = 0.01
ALPHA_MAX, E_MIN = 0.5, 3.0


class _CrMixin:
    def _cr(self, payload: WindowAggregateInput) -> tuple:
        K = len(payload.client_ids)
        return alpha_bar(alpha_max=ALPHA_MAX, n_active=K), ess_ball_bound(e_min=E_MIN, n_active=K)


class UniformWindowAggregator(_CrMixin, Aggregator):
    name = "uniform_window"

    def compute_server_weights(self, payload: WindowAggregateInput) -> np.ndarray:
        K = len(payload.client_ids)
        return np.full(K, 1.0 / K, dtype=np.float64)


class ProjBetaAggregator(_CrMixin, Aggregator):
    name = "proj_beta"

    def compute_server_weights(self, payload: WindowAggregateInput) -> np.ndarray:
        beta = np.asarray(payload.beta_hat, dtype=np.float64)
        ab, eb = self._cr(payload)
        return proj_Cr(beta / beta.sum(), ab, eb, len(beta))


class ProjBetaDebtAggregator(_CrMixin, Aggregator):
    name = "proj_beta_debt"

    def __init__(self, kappa: float = KAPPA) -> None:
        self.kappa = float(kappa)
        self._Q: np.ndarray | None = None

    def _state(self, G: int) -> np.ndarray:
        if self._Q is None or self._Q.shape[0] != G:
            self._Q = np.zeros(G, dtype=np.float64)
        return self._Q

    def compute_server_weights(self, payload: WindowAggregateInput) -> np.ndarray:
        import cvxpy as cp
        beta = np.asarray(payload.beta_hat, dtype=np.float64)
        beta = beta / beta.sum()
        M = np.asarray(payload.compositions, dtype=np.float64)
        mu = np.asarray(payload.mu, dtype=np.float64)
        ab, eb = self._cr(payload)
        Q = self._state(M.shape[0])
        K = M.shape[1]
        if self.kappa <= 0:
            a = proj_Cr(beta, ab, eb, K)
        else:
            x = cp.Variable(K)
            pr = cp.Problem(cp.Minimize(-(Q @ (M @ x)) + (1.0 / self.kappa) * 0.5
                                        * cp.sum_squares(x - beta)),
                            [cp.sum(x) == 1.0, x >= 0.0, x <= ab,
                             cp.sum_squares(x) <= 1.0 / eb])
            a = None
            for solver in (cp.CLARABEL, cp.SCS):
                try:
                    pr.solve(solver=solver, verbose=False)
                    a = np.asarray(x.value, dtype=np.float64).clip(0.0, None)
                    break
                except Exception:
                    a = None
            if a is None or not np.isfinite(a).all():
                a = proj_Cr(beta, ab, eb, K)
        self._Q = np.maximum(Q + ETA * (mu - M @ a), 0.0)
        return a


_ORIG_GET = wr.get_aggregator
_INSTANCES = {}


def _patched(name: str):
    if name == "uniform_window":
        return UniformWindowAggregator()
    if name == "proj_beta":
        return ProjBetaAggregator()
    if name == "proj_beta_debt":
        return ProjBetaDebtAggregator()      # fresh Q state per run (no cross-seed leakage)
    return _ORIG_GET(name)


wr.get_aggregator = _patched
for _arm in ARMS:
    mp.POLICY_MAP[_arm] = mp.POLICY_MAP["raven"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="g0", choices=["g0", "train", "check"])
    ap.add_argument("--seeds", default="all")
    ap.add_argument("--arms", default=",".join(ARMS))
    args = ap.parse_args()
    sys.path.insert(0, str(ROOT / "scripts"))
    import run_h_headroom as h

    h.OUT = ROOT / "results_w1_ladder/round_v4/train"
    h.OUT.mkdir(parents=True, exist_ok=True)
    seeds = (list(range(30001, 30011)) + list(range(30011, 30021))) if args.seeds == "all" \
        else [int(x) for x in args.seeds.split(",")]
    out = []
    if args.phase == "g0":
        for ds in ("sensorscope", "uair"):
            r = h.run_arm("C0_frozen", ds, "raven", 30001, tag="bg0")
            new = json.loads((h.OUT / "bg0" / "C0_frozen" / ds / "raven" / "seed30001" /
                              "final_metrics.json").read_text(encoding="utf-8"))
            frozen = json.loads((ROOT / "artifacts/e3_formal_runs_r1/runs" / ds / "raven" /
                                 "seed30001" / "final_metrics.json").read_text(encoding="utf-8"))
            cmp = {k: None if new.get(k) is None or frozen.get(k) is None
                   else abs(float(new[k]) - float(frozen[k]))
                   for k in ("RMSE_mu", "Delta_group", "Delta_c_s")}
            out.append({"ds": ds, "seed": 30001, "abs_diff": cmp,
                        "pass": bool(all(v is not None and v <= 1e-12 for v in cmp.values()))})
    elif args.phase == "train":
        arms = [a for a in args.arms.split(",") if a]
        for ds in ("sensorscope", "uair"):
            for arm in arms:
                for seed in seeds:
                    r = h.run_arm("C0_frozen", ds, arm, seed, tag="v4")
                    out.append(r)
                    print("done", ds, arm, seed, flush=True)
    else:
        from w1_v4_check import main as check_main          # noqa: F401
        check_main()
    (ROOT / "results_w1_ladder/round_v4" / f"TRAIN_{args.phase}.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out[:4], indent=2, default=str))


if __name__ == "__main__":
    main()
