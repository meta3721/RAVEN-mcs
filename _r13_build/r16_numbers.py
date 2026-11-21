"""Numbers needed for the text repairs: the confirm-set arm levels, the DOSE bound, the central rule."""
from __future__ import annotations

import csv
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")

rows = list(csv.DictReader((ROOT / "results_traffic_e1/round_v1/tables/TE1_CONFIRM.csv").open(encoding="utf-8")))
fed = np.array([float(r["test_RMSE_mu_fedavg_window"]) for r in rows])
sim = np.array([float(r["test_RMSE_mu_raven_simoracle"]) for r in rows])
print("=== confirm-set test RMSE_mu (15 seeds) ===")
print(f"  fedavg_window   mean {fed.mean():.6f}  min {fed.min():.6f}  max {fed.max():.6f}")
print(f"  raven_simoracle mean {sim.mean():.6f}  min {sim.min():.6f}  max {sim.max():.6f}")
c = json.loads((ROOT / "results_traffic_e1/round_v1/TE1_FROZEN_CONST.json").read_text(encoding="utf-8"))
print(f"  constant predictor on the test labels (c_test = weighted sd of test target) = "
      f"{json.loads((ROOT / 'results_server_optimizer/round_v1/REVIEW_EVIDENCE_PACK.json').read_text(encoding='utf-8'))['blocks']['traffic']['H'] and ''}"
      f"see below; validation c_val = {c['c_val']:.6f}")

# test-split constant per block, through the repository scoring path
import sys
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd  # noqa: E402
from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402

N_GROUPS = {"sensorscope": 220, "uair": 144, "traffic": 172}
CK = {"sensorscope": "artifacts/e3_formal_runs_r1/runs/sensorscope/fedavg_window/seed30001/checkpoints/final.pt",
      "uair": "artifacts/e3_formal_runs_r1/runs/uair/fedavg_window/seed30001/checkpoints/final.pt",
      "traffic": "results_server_optimizer/round_v1/runs/C_raven_simoracle/traffic/raven_simoracle/seed30001/checkpoints/final.pt"}


class _Shim:
    pass


print("\n=== test-split target level and constant predictor, per block ===")
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
    const = float(np.sqrt(np.sum(w * (y - ybar) ** 2)))
    tr = ds.atomic_df[ds.atomic_df["split"] == "train"]["target_value"].astype(float)
    print(f"  {b:<12} n={len(y):<6} test weighted mean {ybar:+.4f}  constant (weighted sd) {const:.4f}  "
          f"| train mean {tr.mean():+.4f} sd {tr.std(ddof=0):.4f}")

print("\n=== the DOSE bound the manuscript prints as 0.17 % ===")
p = ROOT / "results_gate_dose/round_v2/tables/DOSE_SUMMARY.csv"
if p.is_file():
    rr = list(csv.DictReader(p.open(encoding="utf-8")))
    print("  columns:", list(rr[0].keys()))
    for r in rr[:12]:
        print("   ", json.dumps(r)[:190])

print("\n=== the centralized reference's rule (what L2219-2220 omits) ===")
src = (ROOT / "src/raven_mcs/e3/real_runner/central_real.py").read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(src, 1):
    if "optim.Adam" in ln or "randint" in ln or "def run_central_real" in ln or ln.strip().startswith("lr"):
        print(f"  central_real.py L{i}: {ln.strip()}")
r2 = (ROOT / "src/raven_mcs/e3/real_runner/runner.py").read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(r2, 1):
    if "local_steps * 10" in ln or "local_steps*10" in ln:
        print(f"  runner.py L{i}: {ln.strip()}")
