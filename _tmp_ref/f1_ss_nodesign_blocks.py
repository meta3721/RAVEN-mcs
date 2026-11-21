"""Recompute the four-block RMSE row for SensorScope RAVEN-NoDesign.

No retraining: loads the saved checkpoints and the G2 eval pack, exactly as
scripts/run_int_r_v2.py::_worst_group_rmse does.  Validates against the published
Table tab:app_block_rmse row for RAVEN-Design before reporting the new row.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_int_r_v2 import _g2_eval_pack, _wrmse_block  # noqa: E402

PUBLISHED_SS_DESIGN = [7.4903, 7.5864, 8.6707, 8.2075]

CASES = [
    ("SS raven (Design ON, validation)",
     ROOT / "artifacts" / "e3_formal_runs_r1" / "runs" / "sensorscope" / "raven"),
    ("SS raven_wo_design (Design OFF, new row)",
     ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs" / "sensorscope" / "raven_wo_design"),
]


def ckpt_of(run_dir: Path) -> Path | None:
    for cand in (run_dir / "checkpoints" / "final.pt", run_dir / "final.pt"):
        if cand.is_file():
            return cand
    return None


def main() -> int:
    import torch
    from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt

    pack = _g2_eval_pack("sensorscope")
    y_true, mu_w, blocks = pack["y_true"], pack["mu_w"], pack["blocks"]
    sp_idx, hour_t, wday_t, trend_t = pack["features"]

    for label, base in CASES:
        rows = []
        for seed in sorted(base.glob("seed*")):
            ckpt = ckpt_of(seed)
            if ckpt is None:
                print(f"  no checkpoint: {seed}")
                continue
            model = CommonNDMF_from_ckpt(ckpt, pack["num_spatial"])
            model.eval()
            with torch.no_grad():
                pred = model(sp_idx, hour_t, wday_t, trend_t).cpu().numpy().reshape(-1)
            vals = [_wrmse_block(y_true, pred, blocks == g, mu_w) for g in range(4)]
            rows.append(vals)
        if not rows:
            print(f"{label}: no rows")
            continue
        A = np.array(rows, dtype=float)
        mean = A.mean(axis=0)
        sd = A.std(axis=0, ddof=1)
        wg_mean = float(np.max(mean))
        wg_sd = float(A.max(axis=1).std(ddof=1))
        print(f"\n{label}   n={len(rows)}")
        print("   per-block mean : " + " ".join(f"{m:.4f}" for m in mean))
        print("   per-block sd   : " + " ".join(f"{s:.4f}" for s in sd))
        print(f"   WG (max of means) = {wg_mean:.4f}   sd of per-seed max = {wg_sd:.4f}")
        if "validation" in label:
            dev = [abs(m - p) for m, p in zip(mean, PUBLISHED_SS_DESIGN)]
            print(f"   published row  : {PUBLISHED_SS_DESIGN}")
            print(f"   max |dev| vs published = {max(dev):.5f}")
            print(f"   published WG   : 8.6707  -> match: {abs(wg_mean - 8.6707) < 5e-4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
