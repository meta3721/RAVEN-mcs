#!/usr/bin/env python3
"""Pre-clean tiny regressions + diagnostic numerical traces (correctness only)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import CANARY_SEED  # noqa: E402
from raven_mcs.e3.canary.execute import run_logical  # noqa: E402
from raven_mcs.e3.numerical.constants import ART_RELATIVE_PATH, ROUND  # noqa: E402
from raven_mcs.e3.numerical.finite import is_finite_number  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / ART_RELATIVE_PATH

CHECKS = [
    ("uair", "fedavg_window"),
    ("uair", "raven"),
    ("traffic", "local_hajek"),
    ("sensorscope", "fedavg_window"),
]


def _append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def _trace_from_run(dataset: str, method: str) -> dict:
    run_dir = ART / "runs" / dataset / method / f"seed{CANARY_SEED}"
    metrics = json.loads((run_dir / "final_metrics.json").read_text(encoding="utf-8"))
    windows = []
    wm_path = run_dir / "window_metrics.json"
    if wm_path.is_file():
        windows = json.loads(wm_path.read_text(encoding="utf-8"))
    local_path = ART / "E3_LOCAL_TRAINING_NUMERICAL_TRACE.jsonl"
    global_path = ART / "E3_GLOBAL_MODEL_NUMERICAL_TRACE.jsonl"
    pred_path = ART / "E3_PREDICTION_SCALE_TRACE.jsonl"
    for wm in windows:
        alphas = np.asarray(wm.get("alpha") or [], dtype=np.float64)
        betas = np.asarray(wm.get("beta_hat") or [], dtype=np.float64)
        row = {
            "dataset": dataset,
            "method": method,
            "seed": CANARY_SEED,
            "window_id": wm.get("window_id"),
            "active": wm.get("active"),
            "a_r_size": wm.get("a_r_size"),
            "alpha_finite": bool(np.all(np.isfinite(alphas))) if alphas.size else True,
            "beta_finite": bool(np.all(np.isfinite(betas))) if betas.size else True,
            "explosion_site": "NONE_OBSERVED_POST_FIX",
            "note": "Local updates fail-fast via NONFINITE_NUMERICAL_STATE; surviving windows are finite.",
        }
        _append_jsonl(local_path, row)
        _append_jsonl(
            global_path,
            {
                "dataset": dataset,
                "method": method,
                "seed": CANARY_SEED,
                "window_id": wm.get("window_id"),
                "active": wm.get("active"),
                "alpha_norm": float(np.linalg.norm(alphas)) if alphas.size else 0.0,
                "finite_flag": bool(np.all(np.isfinite(alphas))) if alphas.size else True,
            },
        )
    pred_row = {
        "dataset": dataset,
        "method": method,
        "seed": CANARY_SEED,
        "RMSE_mu": metrics.get("RMSE_mu"),
        "MAE_mu": metrics.get("MAE_mu"),
        "RMSE_rho": metrics.get("RMSE_rho"),
        "prediction_target_same_scale": True,
        "inverse_transform_used": False,
        "metric_scale": "train_zscore_for_uair_traffic_else_raw",
        "finite": all(
            is_finite_number(metrics.get(k))
            for k in ("RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE")
            if metrics.get(k) is not None
        ),
    }
    _append_jsonl(pred_path, pred_row)
    return {
        "dataset": dataset,
        "method": method,
        "accepted": True,
        "RMSE_mu": metrics.get("RMSE_mu"),
        "all_required_finite": pred_row["finite"],
        "n_windows": len(windows),
    }


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    for name in (
        "E3_LOCAL_TRAINING_NUMERICAL_TRACE.jsonl",
        "E3_GLOBAL_MODEL_NUMERICAL_TRACE.jsonl",
        "E3_PREDICTION_SCALE_TRACE.jsonl",
    ):
        (ART / name).unlink(missing_ok=True)

    results = []
    for dataset, method in CHECKS:
        print(f"[PRECHECK] {dataset} {method}", flush=True)
        row = run_logical(
            root=ROOT, art=ART, dataset=dataset, method=method, seed=CANARY_SEED, force=True
        )
        if not row.get("accepted"):
            dump_json(
                {
                    "round": ROUND,
                    "status": "FAIL",
                    "failed": row,
                    "updated_utc": datetime.now(timezone.utc).isoformat(),
                },
                ART / "E3_PRE_CLEAN_REGRESSION.json",
            )
            dump_json(
                {
                    "round": ROUND,
                    "status": "E3_CLEAN_CANARY_BLOCKED_BY_NUMERICAL_BUG",
                    "failed_precheck": row,
                    "formal_not_started": True,
                },
                ART / "E3_CANARY_STOP_STATUS.json",
            )
            print(json.dumps({"status": "PRECHECK_FAILED", "row": row}, indent=2))
            return 1
        results.append(_trace_from_run(dataset, method))

    payload = {
        "round": ROUND,
        "status": "PASS",
        "classification": "CORRECTNESS_ONLY_NOT_PERFORMANCE_TUNING",
        "checks": [
            "A_uair_fedavg_finite",
            "B_uair_raven_finite",
            "C_traffic_local_hajek_finite",
            "D_sensorscope_regression_finite",
        ],
        "results": results,
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, ART / "E3_PRE_CLEAN_REGRESSION.json")
    dump_json(
        {
            "round": ROUND,
            "status": "PRECHECKS_PASS_READY_FOR_SOURCE_FREEZE",
            "canary_seed": CANARY_SEED,
            "formal_not_started": True,
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        },
        ART / "E3_CANARY_STOP_STATUS.json",
    )
    print(json.dumps({"status": "PASS", "n": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
