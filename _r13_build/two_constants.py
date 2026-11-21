"""Two kinds of constant, per block, under the paper's own scoring weights.

oracle constant  = best constant fitted on the TEST labels (knows test Y) -> the metric's floor
deployable const = the TRAINING mean applied to the test set (knows only train) -> what a practitioner can ship
"""
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

N_GROUPS = {"sensorscope": 220, "uair": 144, "traffic": 172}
CK = {"sensorscope": "artifacts/e3_formal_runs_r1/runs/sensorscope/fedavg_window/seed30001/checkpoints/final.pt",
      "uair": "artifacts/e3_formal_runs_r1/runs/uair/fedavg_window/seed30001/checkpoints/final.pt",
      "traffic": "results_server_optimizer/round_v1/runs/C_raven_simoracle/traffic/raven_simoracle/seed30001/checkpoints/final.pt"}


class _Shim:
    pass


out = {}
print(f"{'block':<12}{'n_test':>7}{'test mean':>11}{'train mean':>11}"
      f"{'oracle const':>13}{'deployable const':>19}{'depl RMSE':>11}{'frozen fedavg':>14}")
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
    oracle = float(np.sqrt(np.sum(w * (y - ybar) ** 2)))
    tr = ds.atomic_df[ds.atomic_df["split"] == "train"]["target_value"].astype(float)
    tr_mean = float(tr.mean())
    deploy = float(np.sqrt(np.sum(w * (y - tr_mean) ** 2)))
    fm = json.loads((ROOT / "artifacts/e3_formal_runs_r1/runs" / b / "fedavg_window/seed30001/"
                     "final_metrics.json").read_text(encoding="utf-8"))["RMSE_mu"] if b != "traffic" else None
    out[b] = {"n_test": int(len(y)), "test_mean": ybar, "train_mean": tr_mean,
              "oracle_constant_rmse": oracle, "deployable_constant": tr_mean,
              "deployable_constant_rmse": deploy,
              "frozen_fedavg_rmse": fm,
              "frozen_vs_oracle_pct": None if fm is None else 100 * (fm / oracle - 1),
              "frozen_vs_deployable_pct": None if fm is None else 100 * (fm / deploy - 1)}
    print(f"{b:<12}{len(y):>7}{ybar:>11.4f}{tr_mean:>11.4f}{oracle:>13.4f}{tr_mean:>19.4f}"
          f"{deploy:>11.4f}{(fm if fm else float('nan')):>14.4f}")

print("\nvs the two constants (frozen fedavg_window):")
for b, v in out.items():
    if v["frozen_fedavg_rmse"]:
        print(f"  {b:<12} vs oracle (knows test Y) {v['frozen_vs_oracle_pct']:+8.1f} %   "
              f"vs deployable (train mean) {v['frozen_vs_deployable_pct']:+8.1f} %")
print("\nconfirm set (Adam), traffic:")
c = list(__import__("csv").DictReader(
    (ROOT / "results_traffic_e1/round_v1/tables/TE1_CONFIRM.csv").open(encoding="utf-8")))
fed = np.array([float(r["test_RMSE_mu_fedavg_window"]) for r in c])
sim = np.array([float(r["test_RMSE_mu_raven_simoracle"]) for r in c])
tv = out["traffic"]
print(f"  fedavg {fed.mean():.4f} | simoracle {sim.mean():.4f} | oracle const {tv['oracle_constant_rmse']:.4f} "
      f"| deployable const {tv['deployable_constant_rmse']:.4f}")
print(f"  fedavg vs deployable constant: {100*(fed.mean()/tv['deployable_constant_rmse']-1):+.1f} %")

(ROOT / "results_traffic_struct/round_v1/TWO_CONSTANTS.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("\nwrote results_traffic_struct/round_v1/TWO_CONSTANTS.json")
