"""Corrected smoke verification: the runner labels the injected path itself, so the sha is the
discriminator, and the substance is the numeric agreement."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import align_mu_to_dataset, freeze_fixture_target  # noqa: E402

d = OUT / "runs/K5_smoke/traffic/local_hajek/seed30001"
art = json.loads((OUT / "TE2_TARGET_ARTIFACT_KAPPA5.json").read_text(encoding="utf-8"))
ds = load_paper_dataset(ROOT, "traffic")
mu5 = np.asarray(align_mu_to_dataset(ds, art)[0], dtype=np.float64)
mu1 = np.asarray(align_mu_to_dataset(ds, freeze_fixture_target(ds.atomic_df, dataset="traffic"))[0],
                 dtype=np.float64)


def score(mu):
    class _S:
        pass
    s = _S()
    s.model = CommonNDMF_from_ckpt(d / "checkpoints/final.pt", ds.num_spatial)
    p = _predict(s, ds, split="test")
    w = np.asarray(_mu_weights_for_test(p, mu), dtype=np.float64)
    w = w / w.sum()
    return float(np.sqrt(np.sum(w * (np.asarray(p["y_pred"], float) - np.asarray(p["y_true"], float)) ** 2)))


cfg = json.loads((d / "config_snapshot.json").read_text(encoding="utf-8"))
fm = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
stored, r5, r1 = fm["RMSE_mu"], score(mu5), score(mu1)
print(f"  runner's own label            = {cfg['target_artifact_path']!r} (set by runner.py L139)")
print(f"  recorded artifact sha256      = {cfg['target_artifact_sha256']}")
print(f"  stored RMSE_mu                = {stored}")
print(f"  rescore with the kappa=5 mu   = {r5}   identical: {abs(stored - r5) < 1e-12}")
print(f"  rescore with the frozen mu    = {r1}   different: {abs(stored - r1) > 1e-9}")
print(f"  frozen run, same cell         = "
      f"{json.loads((ROOT / 'artifacts/e3_formal_runs_r1/runs/traffic/local_hajek/seed30001/final_metrics.json').read_text())['RMSE_mu']}")
ok = abs(stored - r5) < 1e-12 and abs(stored - r1) > 1e-9 and abs(r1 - 1.0055697313116085) < 1e-12
print(f"\nSMOKE: {'PASS' if ok else 'FAIL'} - injection in force, metric uses the new weights, and the "
      f"same cell still reproduces the frozen protocol under the frozen target")
sys.exit(0 if ok else 2)
