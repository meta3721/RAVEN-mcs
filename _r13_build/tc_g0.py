"""G0: independently recompute the six constants from the scoring path and compare to the prompt."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402

EXPECTED = {  # as printed in the execution prompt, 4 dp
    "sensorscope": {"test_fitted_constant": 2.0878, "training_mean_predictor": 7.6471,
                    "test_mean": 7.6572, "train_mean": 0.3006, "ratio": 3.7},
    "uair": {"test_fitted_constant": 0.6781, "training_mean_predictor": 1.0537,
             "test_mean": -0.8066, "train_mean": 0.0000, "ratio": 1.6},
    "traffic": {"test_fitted_constant": 1.0067, "training_mean_predictor": 1.0067,
                "test_mean": 0.0027, "train_mean": 0.0000, "ratio": 1.0},
}
N_GROUPS = {"sensorscope": 220, "uair": 144, "traffic": 172}
CK = {"sensorscope": "artifacts/e3_formal_runs_r1/runs/sensorscope/fedavg_window/seed30001/checkpoints/final.pt",
      "uair": "artifacts/e3_formal_runs_r1/runs/uair/fedavg_window/seed30001/checkpoints/final.pt",
      "traffic": "results_server_optimizer/round_v1/runs/C_raven_simoracle/traffic/raven_simoracle/seed30001/checkpoints/final.pt"}


class _Shim:
    pass


out, ok = {}, True
for b, n in N_GROUPS.items():
    ds = load_paper_dataset(ROOT, b)
    atomic = ds.atomic_df.copy()
    atomic["target_group_main"] = (RepeatableTimeOfDayMapper().map(atomic) if n == 4
                                   else pd.Categorical(atomic["target_group"]).codes)
    mu = np.asarray([float(TargetBuilder(group_mapper=GroupMapper("target_group_main"))
                           .build(atomic, split="test").group_mass.get(str(g), 0.0)) for g in range(n)])
    shim = _Shim()
    shim.model = CommonNDMF_from_ckpt(ROOT / CK[b], ds.num_spatial)
    pred = _predict(shim, ds, split="test")
    w = np.asarray(_mu_weights_for_test(pred, mu), dtype=np.float64)
    w = w / w.sum()
    y = np.asarray(pred["y_true"], dtype=np.float64)
    ybar = float(np.sum(w * y))
    tfc = float(np.sqrt(np.sum(w * (y - ybar) ** 2)))
    tr = float(ds.atomic_df[ds.atomic_df["split"] == "train"]["target_value"].astype(float).mean())
    tmp = float(np.sqrt(np.sum(w * (y - tr) ** 2)))
    got = {"test_fitted_constant": round(tfc, 4), "training_mean_predictor": round(tmp, 4),
           "test_mean": round(ybar, 4), "train_mean": round(tr, 4),
           "ratio": round(tmp / tfc, 1), "n_test": int(len(y))}
    exp = EXPECTED[b]
    match = all(abs(got[k] - exp[k]) < 5e-5 for k in exp)
    ok &= match
    out[b] = {**got, "expected": exp, "match": match}
    print(f"  {b:<12} test-fitted {got['test_fitted_constant']:.4f} (exp {exp['test_fitted_constant']}) | "
          f"training-mean {got['training_mean_predictor']:.4f} (exp {exp['training_mean_predictor']}) | "
          f"ratio {got['ratio']:.1f} (exp {exp['ratio']}) | test mean {got['test_mean']:.4f} | "
          f"train mean {got['train_mean']:.4f} -> {'MATCH' if match else 'MISMATCH'}")

print("\nG0:", "PASS - all six constants reproduce the prompt" if ok else "FAIL")
print("scoring path: runner._predict + runner._mu_weights_for_test + metrics.rmse_mu, test split")
d = ROOT / "results_two_constant/round_v1"
d.mkdir(parents=True, exist_ok=True)
(d / "TC_TWO_CONSTANTS.json").write_text(json.dumps(
    {"gate": "G0", "method": "weighted standard deviation of the scored test target (test-fitted "
                             "constant) and sqrt(sum_i w_i (y_i - train_mean)^2) (training-mean "
                             "predictor), through runner._predict + runner._mu_weights_for_test",
     "scoring_path_checkpoints": CK, "blocks": out, "g0_pass": bool(ok)},
    indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("wrote", (d / "TC_TWO_CONSTANTS.json").relative_to(ROOT).as_posix())
raise SystemExit(0 if ok else 2)
