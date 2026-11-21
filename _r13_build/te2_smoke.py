"""TE2 smoke: one cell on the single changed critical path, then verify the injection actually took."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"
sys.path.insert(0, str(OUT / "driver"))
sys.path.insert(0, str(ROOT / "src"))
import s1p_driver as D  # noqa: E402

art = json.loads((OUT / "TE2_TARGET_ARTIFACT_KAPPA5.json").read_text(encoding="utf-8"))
D.TARGET_ARTIFACT = art
d = D.run_one("traffic", "local_hajek", 30001, 2, "K5_smoke", "off", force=True)

from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import align_mu_to_dataset, freeze_fixture_target  # noqa: E402

ds = load_paper_dataset(ROOT, "traffic")
mu5 = np.asarray(align_mu_to_dataset(ds, art)[0], dtype=np.float64)
mu1 = np.asarray(align_mu_to_dataset(ds, freeze_fixture_target(ds.atomic_df, dataset="traffic"))[0],
                 dtype=np.float64)


def score(ck, mu):
    class _S:
        pass
    s = _S()
    s.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
    p = _predict(s, ds, split="test")
    w = np.asarray(_mu_weights_for_test(p, mu), dtype=np.float64)
    w = w / w.sum()
    return float(np.sqrt(np.sum(w * (np.asarray(p["y_pred"], float) - np.asarray(p["y_true"], float)) ** 2)))


ck = d / "checkpoints/final.pt"
stored = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))["RMSE_mu"]
recon5 = score(ck, mu5)
recon1 = score(ck, mu1)
cfg = json.loads((d / "config_snapshot.json").read_text(encoding="utf-8"))
frozen = ROOT / "artifacts/e3_formal_runs_r1/runs/traffic/local_hajek/seed30001/final_metrics.json"
frozen_rmse = json.loads(frozen.read_text(encoding="utf-8"))["RMSE_mu"]

print("\n=== smoke verification ===")
print(f"  config target_artifact_path   = {cfg.get('target_artifact_path')!r}  "
      f"(expect 'inline_fixture_freeze(kappa5_region1)')")
print(f"  config target_artifact_sha256 = {cfg.get('target_artifact_sha256')}")
print(f"  stored RMSE_mu                = {stored}")
print(f"  manual rescore, kappa=5 mu    = {recon5}   equal: {abs(stored - recon5) < 1e-12}")
print(f"  manual rescore, frozen mu     = {recon1}   differs from stored: {abs(stored - recon1) > 1e-9}")
print(f"  frozen uniform-target run     = {frozen_rmse} (different vintage, for context)")
ok = (cfg.get("target_artifact_path") == "inline_fixture_freeze(kappa5_region1)"
      and abs(stored - recon5) < 1e-12 and abs(stored - recon1) > 1e-9)
print(f"\nSMOKE: {'PASS - the injected target is in force and the metric uses the new weights' if ok else 'FAIL'}")
raise SystemExit(0 if ok else 2)
