"""Load frozen paper datasets + client mappings for E3 Canary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.data.base import DatasetMetadata
from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.e3.canary.constants import FROZEN_DATASET_HASHES, HORIZON_JSON
from raven_mcs.e3.semantic_alignment.client_mapping import (
    build_uair_mapping,
    load_sensorscope_mapping,
)
from raven_mcs.utils.hashing import sha256_file


def apply_train_zscore_standardization(dataset: ProcessedDataset) -> dict[str, float]:
    """Train-only z-score on atomic targets + client measurements (shared scale).

    UNIT_SCALE_FIX / PREPROCESSING_CONSISTENCY_FIX:
    Fit mean/std on train atomic targets only; apply to all splits' atomic
    ``target_value`` and client ``potential_measurement``; rebuild measurement
    index so training observations match metric evaluation targets.
    """
    mean = float(dataset.target_mean)
    std = float(dataset.target_std) if float(dataset.target_std) > 0 else 1.0
    dataset._client_df = dataset._client_df.copy()
    dataset._client_df["potential_measurement"] = (
        dataset._client_df["potential_measurement"].astype(float) - mean
    ) / std
    dataset._atomic_df = dataset._atomic_df.copy()
    dataset._atomic_df["target_value"] = (
        dataset._atomic_df["target_value"].astype(float) - mean
    ) / std
    dataset._measurement_index = {
        (str(row["client_id"]), str(row["unit_id"])): float(row["potential_measurement"])
        for _, row in dataset._client_df.iterrows()
    }
    dataset._standardized = True
    dataset._scaler_mean = mean
    dataset._scaler_std = std
    return {"scaler_mean": mean, "scaler_std": std, "status": "APPLIED"}


def load_horizon(root: Path, dataset: str) -> dict[str, Any]:
    path = Path(root) / HORIZON_JSON[dataset]
    return json.loads(path.read_text(encoding="utf-8"))


def verify_dataset_hash(root: Path, dataset: str) -> dict[str, Any]:
    path = Path(root) / f"data/processed/{dataset}/atomic_units.parquet"
    got = sha256_file(path)
    expected = FROZEN_DATASET_HASHES[dataset]
    ok = got == expected
    return {
        "dataset": dataset,
        "path": str(path.relative_to(root)).replace("\\", "/"),
        "expected": expected,
        "got": got,
        "match": ok,
        "status": "PASS" if ok else "FROZEN_DATASET_HASH_MISMATCH",
    }


def traffic_spatial_to_client(root: Path) -> dict[str, str]:
    """E2/E3 sealed identity: each station is its own client."""
    atomic = pd.read_parquet(Path(root) / "data/processed/traffic/atomic_units.parquet")
    spatials = sorted(atomic["spatial_id"].astype(str).unique().tolist())
    return {sid: sid for sid in spatials}


def load_spatial_to_client(root: Path, dataset: str) -> dict[str, str]:
    name = str(dataset).lower()
    if name == "sensorscope":
        return load_sensorscope_mapping(root)
    if name == "uair":
        atomic = pd.read_parquet(Path(root) / "data/processed/uair/atomic_units.parquet")
        return build_uair_mapping(atomic, n_clients=8)
    if name == "traffic":
        return traffic_spatial_to_client(root)
    raise ValueError(f"unknown dataset {dataset}")


class TrafficE3Dataset(ProcessedDataset):
    """Traffic paper data with station=client measurements and spatial×time h(i).

    Unlike E2 TrafficRunnerDataset, do NOT collapse target_group to block0..3 —
    E3 requires spatial×time target semantics; opportunity stratum is remapped
    to the sealed 4-region identity inside ``run_e3_real``.
    """

    def __init__(self, root: Path) -> None:
        root = Path(root)
        metadata = DatasetMetadata(
            dataset="traffic",
            target_name="average_speed",
            target_unit="km_per_h",
            spatial_unit="traffic_station",
            time_unit="hour",
            source_name="Traffic dense MCS matrix",
            source_url="https://local.traffic.protocol/e3",
            raw_license="research-internal",
            filtering_rules=("Dense 43x720 protocol matrix; E3 spatial×time target",),
        )
        metadata.validate()
        data_dir = root / "data/processed/traffic"
        atomic = pd.read_parquet(data_dir / "atomic_units.parquet")
        staging = root / "artifacts/e3_multidataset_real_runner_canary_r1/_traffic_e3_staging"
        staging.mkdir(parents=True, exist_ok=True)
        atomic_out = staging / "atomic_units.parquet"
        client_out = staging / "client_measurements.parquet"
        if not atomic_out.is_file():
            atomic.to_parquet(atomic_out, index=False)
        if not client_out.is_file():
            rows = [
                {
                    "client_id": str(r.spatial_id),
                    "unit_id": str(r.unit_id),
                    "potential_measurement": float(r.target_value),
                    "controlled_generator_parameters": "{}",
                    "split": str(r.split),
                    "source_trace_id": f"station::{r.spatial_id}::{r.unit_id}",
                }
                for r in atomic.itertuples(index=False)
            ]
            pd.DataFrame(rows).to_parquet(client_out, index=False)
        super().__init__(staging, metadata)
        apply_train_zscore_standardization(self)


def load_paper_dataset(root: Path, dataset: str) -> ProcessedDataset:
    name = str(dataset).lower()
    root = Path(root)
    if name == "sensorscope":
        meta = DatasetMetadata(
            dataset="sensorscope",
            target_name="temperature",
            target_unit="C",
            spatial_unit="station",
            time_unit="hour",
            source_name="EPFL/Zenodo SensorScope Data",
            source_url="https://zenodo.org/records/2654726",
            raw_license="cc-by-4.0",
            filtering_rules=("Drop non-finite temperature", "Keep [-40, 60] C"),
        )
        meta.validate()
        return ProcessedDataset(root / "data/processed/sensorscope", meta)
    if name == "uair":
        meta = DatasetMetadata(
            dataset="uair",
            target_name="pm25",
            target_unit="ug_m3",
            spatial_unit="station",
            time_unit="hour",
            source_name="U-Air",
            source_url="https://local.uair.protocol/e3",
            raw_license="research-internal",
            filtering_rules=("Frozen E3 processed matrix",),
        )
        meta.validate()
        ds = ProcessedDataset(root / "data/processed/uair", meta)
        # UNIT_SCALE_FIX: raw PM2.5 (~1-210) explodes frozen lr=0.01; use train z-score
        # identical to Traffic E2/E3 convention. Metrics stay on the same scaled space.
        apply_train_zscore_standardization(ds)
        return ds
    if name == "traffic":
        return TrafficE3Dataset(root)
    raise ValueError(f"unknown dataset {dataset}")
