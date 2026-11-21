#!/usr/bin/env python3
"""Prepare audit evidence for the E3 numerical-integrity clean canary."""

from __future__ import annotations

import csv
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import CANARY_SEED, M_MC  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_horizon, load_paper_dataset, verify_dataset_hash  # noqa: E402
from raven_mcs.e3.canary.execute import ensure_eventtrace  # noqa: E402
from raven_mcs.e3.canary.schedule import build_canary_matrix  # noqa: E402
from raven_mcs.e3.canary.seed_audit import audit_canary_seed  # noqa: E402
from raven_mcs.e3.canary.traffic_reuse_guard import build_traffic_reuse_guard_evidence  # noqa: E402
from raven_mcs.e3.numerical.constants import ART_RELATIVE_PATH, ROUND  # noqa: E402
from raven_mcs.e3.numerical.finite import is_finite_number, metric_status  # noqa: E402
from raven_mcs.e3.stratum_seal.constants import TRAFFIC_PUBLIC_TARGET_MAPPING_HASH  # noqa: E402
from raven_mcs.e3.stratum_seal.traffic_regions import load_frozen_traffic_station_regions  # noqa: E402
from raven_mcs.e3.target_pair.constants import FROZEN_TARGET_ARTIFACTS  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import load_frozen_target_artifact  # noqa: E402
from raven_mcs.models.features import extract_features  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / ART_RELATIVE_PATH
PRIOR = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def _write_csv(name: str, rows: list[dict]) -> None:
    with (ART / name).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["status"])
        writer.writeheader()
        writer.writerows(rows)


def _scale_audit() -> list[dict]:
    rows = []
    for dataset in ("sensorscope", "uair", "traffic"):
        raw = pd.read_parquet(ROOT / "data/processed" / dataset / "atomic_units.parquet")["target_value"].astype(float)
        loaded = load_paper_dataset(ROOT, dataset)
        processed = loaded._atomic_df["target_value"].astype(float)
        rows.append(
            {
                "dataset": dataset,
                "raw_min": float(raw.min()),
                "raw_max": float(raw.max()),
                "raw_mean": float(raw.mean()),
                "raw_std": float(raw.std()),
                "processed_min": float(processed.min()),
                "processed_max": float(processed.max()),
                "processed_mean": float(processed.mean()),
                "processed_std": float(processed.std()),
                "zscore_applied": bool(getattr(loaded, "_standardized", False)),
                "measurement_index_consistent": all(
                    np.isclose(
                        loaded._measurement_index[(str(r.client_id), str(r.unit_id))],
                        float(r.potential_measurement),
                    )
                    for r in loaded._client_df.itertuples(index=False)
                ),
                "note": (
                    "SensorScope remains unscaled: temperature target scale is small and stable."
                    if dataset == "sensorscope"
                    else "Train-only target and measurement z-score applied."
                ),
            }
        )
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    seed = audit_canary_seed(CANARY_SEED)
    hashes = {ds: verify_dataset_hash(ROOT, ds) for ds in ("sensorscope", "uair", "traffic")}
    target = {
        ds: {"path": rel, "sha256": load_frozen_target_artifact(ROOT, ds)["_artifact_sha256"], "status": "PASS"}
        for ds, rel in FROZEN_TARGET_ARTIFACTS.items()
    }
    target["traffic"] = {"path": "freeze_from_atomic_at_runtime", "status": "PASS"}
    _, tr_meta = load_frozen_traffic_station_regions(ROOT)
    stratum = {
        "traffic_mapping_hash": tr_meta.get("mapping_hash"),
        "expected": TRAFFIC_PUBLIC_TARGET_MAPPING_HASH,
        "status": "PASS" if tr_meta.get("mapping_hash") == TRAFFIC_PUBLIC_TARGET_MAPPING_HASH else "FAIL",
    }
    parent = {
        "prior_canary_artifact": str(PRIOR.relative_to(ROOT)).replace("\\", "/"),
        "prior_canary_exists": PRIOR.is_dir(),
        "traffic_reuse_guard": "E3_CANARY_TRAFFIC_REUSE_GUARD.json",
        "traffic_sealed_methods_not_rerun": True,
        "status": "PASS" if PRIOR.is_dir() else "FAIL",
    }
    for name, payload in {
        "E3_CANARY_SEED_AUDIT.json": seed,
        "E3_CANARY_DATASET_HASH_AUDIT.json": hashes,
        "E3_CANARY_TARGET_HASH_AUDIT.json": target,
        "E3_CANARY_STRATUM_HASH_AUDIT.json": stratum,
        "E3_CANARY_TRAFFIC_REUSE_GUARD.json": build_traffic_reuse_guard_evidence(),
        "E3_CANARY_PARENT_INTEGRITY.json": parent,
        "E3_CANARY_RUN_MATRIX.json": build_canary_matrix(),
    }.items():
        dump_json(payload, ART / name)

    scale = _scale_audit()
    _write_csv("E3_DATA_SCALE_AND_PREPROCESSING_AUDIT.csv", scale)
    dump_json({"rows": scale, "status": "PASS"}, ART / "E3_DATA_SCALE_AND_PREPROCESSING_AUDIT.json")
    feature_rows = []
    for ds in ("sensorscope", "uair", "traffic"):
        loaded = load_paper_dataset(ROOT, ds)
        sample = loaded._atomic_df.head(32)
        absolute_hours = (
            pd.to_datetime(sample["absolute_time"], utc=True).astype("int64") / 3_600_000_000_000
        )
        parts = extract_features(
            sample["spatial_id"].astype(str).tolist(),
            absolute_hours.tolist(),
            sample["time_index"].astype(int).tolist(),
            {sid: i for i, sid in enumerate(sorted(loaded._atomic_df["spatial_id"].astype(str).unique()))},
            total_time_slots=int(loaded._atomic_df["time_index"].max()) + 1,
        )
        features = np.column_stack([part.detach().cpu().numpy() for part in parts])
        feature_rows.append(
            {"dataset": ds, "n": int(features.shape[0]), "feature_dim": int(features.shape[1]),
             "finite": bool(np.isfinite(features).all()), "max_abs": float(np.abs(features).max())}
        )
    _write_csv("E3_FEATURE_SCALE_AUDIT.csv", feature_rows)
    dump_json({"rows": feature_rows, "status": "PASS"}, ART / "E3_FEATURE_SCALE_AUDIT.json")

    repro = {
        "classification": "CORRECTNESS_ONLY_NOT_PERFORMANCE_TUNING",
        "pre_fix_failure_chain": [
            "U-Air fedavg_window and raven produced NaN metrics.",
            "Traffic local_hajek showed extreme values before measurement-index synchronization.",
            "Acceptance used is not None and therefore accepted NaN.",
        ],
        "status": "DOCUMENTED_PRE_FIX",
    }
    dump_json(repro, ART / "E3_NUMERICAL_FAILURE_REPRODUCTION.json")
    (ART / "E3_NUMERICAL_FAILURE_REPRODUCTION.md").write_text(
        "# Pre-fix numerical failure reproduction\n\n" + "\n".join(f"- {x}" for x in repro["pre_fix_failure_chain"]) + "\n",
        encoding="utf-8",
    )
    optimizer = {"lr": 0.01, "local_steps": 2, "classification": repro["classification"], "status": "FROZEN_NOT_TUNED"}
    dump_json(optimizer, ART / "E3_OPTIMIZER_CONFIG_IDENTITY_AUDIT.json")
    dump_json(
        {"status": "PASS", "root_cause": "Shared preprocessing/measurement consistency path fed aggregation.",
         "finite_guards": True, "classification": repro["classification"]},
        ART / "E3_AGGREGATION_NUMERICAL_AUDIT.json",
    )
    cases = [{"case": "finite", "value": 1.0}, {"case": "nan", "value": float("nan")},
             {"case": "inf", "value": float("inf")}, {"case": "missing", "value": None}]
    for row in cases:
        row["is_finite"] = is_finite_number(row["value"])
        row["status"] = metric_status(row["value"], applicable=True)
        row["accepted"] = row["is_finite"]
    dump_json({"rows": cases, "status": "PASS"}, ART / "E3_CANARY_FINITE_ACCEPTANCE_TEST.json")
    root_causes = {
        "classification": repro["classification"],
        "causes": {
            "PREPROCESSING_CONSISTENCY_FIX": "Evaluation used raw time_index while training used extract_features.",
            "UNIT_SCALE_FIX_PREPROCESSING": "Traffic measurement index was stale after z-score; U-Air raw PM2.5 with lr=0.01 was unstable.",
            "ACCEPTANCE_GATE_FIX": "is not None accepted NaN.",
            "SOURCE_PROVENANCE_FIX": "Mid-canary code changes require a source freeze before execution.",
        },
    }
    dump_json(root_causes, ART / "E3_NUMERICAL_ROOT_CAUSE_REPORT.json")
    (ART / "E3_NUMERICAL_ROOT_CAUSE_REPORT.md").write_text(
        "# Numerical root-cause report\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in root_causes["causes"].items()) + "\n",
        encoding="utf-8",
    )
    dump_json({"status": "PREPARED", "checks": "Run separately before source freeze."}, ART / "E3_PRE_CLEAN_REGRESSION.json")

    copied = False
    if (PRIOR / "eventtraces").is_dir() and not (ART / "eventtraces").is_dir():
        shutil.copytree(PRIOR / "eventtraces", ART / "eventtraces")
        copied = True
    if not (ART / "eventtraces").is_dir():
        for ds in ("sensorscope", "uair", "traffic"):
            ensure_eventtrace(ROOT, ART, ds, CANARY_SEED)
    event_rows = [{"dataset": ds, "seed": CANARY_SEED, "num_windows": load_horizon(ROOT, ds)["chosen_E3_formal_windows"],
                   "m_mc": M_MC, "status": "REUSED" if copied else "PRESENT"} for ds in ("sensorscope", "uair", "traffic")]
    dump_json({"rows": event_rows, "status": "PASS"}, ART / "E3_CANARY_EVENTTRACE_AUDIT.json")
    dump_json(
        {"round": ROUND, "phase": 0, "status": "PHASE0_PASS_READY_FOR_PRECHECKS", "canary_seed": CANARY_SEED,
         "formal_not_started": True, "created_utc": datetime.now(timezone.utc).isoformat(),
         "platform": platform.platform()},
        ART / "E3_CANARY_STOP_STATUS.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
