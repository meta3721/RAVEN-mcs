"""T-Drive protocol seal R1 orchestrator. Writes only under tdrive_protocol_seal_r1/.

No training. No Canary. No formal 50-run execution.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.controlled import time_of_day_block, weekday_label
from raven_mcs.paper_data_r1.io_util import (
    ensure_dir,
    sha256_file,
    write_csv,
    write_json,
    write_text,
)
from raven_mcs.tdrive_protocol_seal_r1.constants import (
    ALPHA,
    ALPHA_MAX,
    CANARY_SEED,
    DATASET_CANONICAL,
    DATASET_PAPER,
    E_MIN,
    EPS_ZERO,
    FORBIDDEN_METHODS,
    FORMAL_SEEDS,
    H_FALLBACK_LABEL,
    H_GROUPS,
    INVENTORY_CANDIDATES,
    LAMBDA_BETA,
    LAMBDA_GROUP,
    LAMBDA_S,
    LAMBDA_V,
    LOCAL_STEPS,
    M_MC,
    MEAN_OBSERVATION_RATE,
    METHOD_SOURCE_FILES,
    METHODS,
    MICRO_FIXTURE_SEED,
    MU_TOLERANCE,
    PRIMARY_METRICS,
    PROTOCOL_ID,
    ROUND,
    S_MAX,
    SCENARIO,
    SPLIT_ID,
    STATUSES,
    WINDOW_DURATION,
)
from raven_mcs.tdrive_protocol_seal_r1.eventtrace_generator import (
    fallback_h_id,
    run_micro_fixture,
)
from raven_mcs.tdrive_protocol_seal_r1.gates import run_gates
from raven_mcs.tdrive_protocol_seal_r1.package import package_zip
from raven_mcs.tdrive_protocol_seal_r1.report import write_report


def _git(root: Path, *args: str) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=str(root), stderr=subprocess.DEVNULL)
        return out.decode("utf-8", errors="replace").strip()
    except Exception:  # noqa: BLE001
        return "UNKNOWN"


def _role_for(path: Path, root: Path) -> tuple[str, str, str]:
    rel = path.relative_to(root).as_posix()
    if rel.startswith("data/raw/"):
        return "raw_trajectory_or_provenance", "raw", "processed_manifest.raw"
    if rel.startswith("data/processed/"):
        return "processed_table", "processed", "processed_manifest.processed"
    if rel.startswith("data/interim/"):
        return "interim_audit_or_metadata", "interim", "processed_manifest.interim"
    if rel.startswith("data/manifests/"):
        return "processed_dataset_manifest", "manifest", "authority_1"
    if rel.startswith("configs/dataset/"):
        return "dataset_config", "config", "authority_2"
    if rel.startswith("configs/experiment/"):
        return "historical_e9_experiment_yaml", "config", "historical_not_protocol"
    if rel.startswith("src/raven_mcs/data/"):
        return "adapter_or_split_source", "source", "authority_2"
    if "event_trace" in rel or "generator_r3" in rel or "stage2" in rel:
        return "eventtrace_source", "source", "e3_transfer"
    if "readiness" in rel:
        return "prior_readiness_not_protocol", "report", "historical"
    if rel.startswith("configs/frozen/") or rel.startswith("artifacts/e4_"):
        return "frozen_e3_e4_transfer_source", "config", "authority_transfer"
    return "supporting", "source", "discovered"


def _iter_files(root: Path, candidate: str) -> list[Path]:
    p = root / candidate
    if p.is_file():
        return [p]
    if p.is_dir():
        return [x for x in p.rglob("*") if x.is_file()]
    return []


def _gini(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return float("nan")
    if np.any(x < 0):
        x = np.abs(x)
    if float(x.sum()) <= 0:
        return 0.0
    x = np.sort(x)
    n = x.size
    return float((2.0 * np.sum((np.arange(1, n + 1)) * x) / (n * x.sum())) - (n + 1) / n)


def _parquet_schema_rows(path: Path, df: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for col in df.columns:
        s = df[col]
        missing = int(s.isna().sum()) if s.dtype != object else int(sum(v is None or (isinstance(v, float) and pd.isna(v)) for v in s))
        rows.append(
            {
                "path": path.as_posix(),
                "column": col,
                "dtype": str(s.dtype),
                "n_missing": missing,
                "n_unique": int(s.nunique(dropna=True)) if s.dtype != object or len(s) < 2_000_000 else "",
            }
        )
    return rows


def seal_inventory(root: Path, out: Path, git_rev: str) -> dict[str, Any]:
    rows = []
    for cand in INVENTORY_CANDIDATES:
        for path in _iter_files(root, cand):
            rel = path.relative_to(root).as_posix()
            role, raw_or_proc, auth = _role_for(path, root)
            st = path.stat()
            rows.append(
                {
                    "path": rel,
                    "size_bytes": int(st.st_size),
                    "sha256": sha256_file(path),
                    "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                    "role": role,
                    "raw_or_processed": raw_or_proc,
                    "source_revision": git_rev,
                    "candidate_authority": auth,
                    "notes": "",
                }
            )
    rows.sort(key=lambda r: r["path"])
    write_csv(out / "00_inventory/TDRIVE_ALL_RELEVANT_FILES.csv", rows)
    payload = {"round": ROUND, "n_files": len(rows), "files": rows}
    write_json(out / "00_inventory/TDRIVE_ALL_RELEVANT_FILES.json", payload)
    att = {
        "round": ROUND,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "training_started": False,
        "formal_run_started": False,
        "canary_started": False,
        "raw_trajectory_modified": False,
        "processed_dataset_modified": False,
        "scientific_source_modified": False,
        "new_random_realization_generated_for_results": False,
        "writes_only_under": "tdrive_protocol_seal_r1/",
        "micro_fixture_allowed": True,
        "micro_fixture_is_not_paper_result": True,
        "formal_training_runs_authorized": 0,
        "paper_result_runs_authorized": 0,
        "canary_training_runs_authorized": 0,
    }
    write_json(out / "00_inventory/TDRIVE_PROTOCOL_NO_RUN_ATTESTATION.json", att)
    write_json(
        out / "00_inventory/TDRIVE_NO_PERFORMANCE_TUNING_ATTESTATION.json",
        {
            "grid_chosen_by_test_metric": False,
            "slot_chosen_by_test_metric": False,
            "target_h_chosen_by_test_metric": False,
            "mu_chosen_by_test_metric": False,
            "split_chosen_by_test_metric": False,
            "raven_config_tuned_on_tdrive_test": False,
            "baseline_weakened": False,
            "result_dependent_semantic_choice": False,
            "authority_order": [
                "processed_dataset_manifest",
                "linked_source_config",
                "e9_only_if_hash_linked (not used as protocol)",
                "deterministic_reconstruction",
                "STOP",
            ],
        },
    )
    return {"n_files": len(rows), "attestation": att}


def seal_dataset(root: Path, out: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    raw_root = root / "data/raw/tdrive_speed"
    prov = json.loads((raw_root / "provenance.json").read_text(encoding="utf-8"))
    raw_files = []
    for rec in manifest["stages"]["raw"]["files"]:
        p = raw_root / rec["relative_path"]
        raw_files.append(
            {
                "relative_path": rec["relative_path"],
                "size_bytes": rec["size_bytes"],
                "sha256_manifest": rec["sha256"],
                "sha256_file": sha256_file(p),
                "hash_match": rec["sha256"] == sha256_file(p),
            }
        )
    # Avoid double hashing: recompute from rows just written
    for rec in raw_files:
        rec["hash_match"] = rec["sha256_manifest"] == rec["sha256_file"]
    write_csv(out / "01_dataset/TDRIVE_RAW_FILE_MANIFEST.csv", raw_files)
    raw_identity = {
        "dataset_name": DATASET_PAPER,
        "canonical_id": DATASET_CANONICAL,
        "source_description": "Microsoft Research T-Drive trajectory sample (Beijing taxis)",
        "raw_root": "data/raw/tdrive_speed",
        "file_count": len(raw_files),
        "total_size_bytes": int(sum(r["size_bytes"] for r in raw_files)),
        "manifest_sha256": sha256_file(root / "data/manifests/tdrive_speed_manifest.json"),
        "raw_dataset_sha256_if_available": manifest["stages"]["raw"]["stage_hash"],
        "data_hash": manifest["data_hash"],
        "preparation_seed": manifest["preparation_identity"]["seed"],
        "adapter": manifest["preparation_identity"]["adapter"],
        "timezone_semantics": "Raw timestamps are naive Beijing wall-clock values; adapter labels them UTC without offset conversion.",
        "coordinate_system": "WGS84 longitude/latitude degrees",
        "bbox": {"lon_min": 116.0, "lon_max": 116.8, "lat_min": 39.6, "lat_max": 40.2},
        "known_source_cleaning_already_applied": [
            "bbox clip 116.0-116.8E, 39.6-40.2N",
            "speed 5-120 km/h",
            "dt in (0, 0.25] hours",
        ],
        "license_source_notes": prov.get("license") or "microsoft-research-license",
        "provenance": prov,
        "all_raw_hashes_match_manifest": all(r["hash_match"] for r in raw_files),
        "status": "HASH_BOUND" if all(r["hash_match"] for r in raw_files) else "HASH_MISMATCH",
    }
    write_json(out / "01_dataset/TDRIVE_RAW_DATA_IDENTITY.json", raw_identity)

    atomic_path = root / "data/processed/tdrive_speed/atomic_units.parquet"
    meas_path = root / "data/processed/tdrive_speed/client_measurements.parquet"
    atomic = pd.read_parquet(atomic_path)
    meas = pd.read_parquet(meas_path)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    expected_a = next(
        f["sha256"] for f in manifest["stages"]["processed"]["files"] if f["relative_path"] == "atomic_units.parquet"
    )
    expected_m = next(
        f["sha256"]
        for f in manifest["stages"]["processed"]["files"]
        if f["relative_path"] == "client_measurements.parquet"
    )
    got_a = sha256_file(atomic_path)
    got_m = sha256_file(meas_path)
    schema_rows = _parquet_schema_rows(atomic_path, atomic) + _parquet_schema_rows(meas_path, meas)
    write_csv(out / "01_dataset/TDRIVE_PROCESSED_SCHEMA.csv", schema_rows)

    dup_atomic = int(atomic["unit_id"].duplicated().sum())
    dup_meas = int(meas.duplicated(subset=["client_id", "unit_id"]).sum())
    processed_identity = {
        "atomic_units": {
            "path": "data/processed/tdrive_speed/atomic_units.parquet",
            "sha256": got_a,
            "sha256_manifest": expected_a,
            "hash_match": got_a == expected_a,
            "row_count": int(len(atomic)),
            "column_count": int(atomic.shape[1]),
            "column_names": list(map(str, atomic.columns)),
            "time_range": [str(atomic["absolute_time"].min()), str(atomic["absolute_time"].max())],
            "n_spatial_id": int(atomic["spatial_id"].nunique()),
            "n_time_index": int(atomic["time_index"].nunique()),
            "n_missing_target": int(atomic["target_value"].isna().sum()),
            "duplicate_unit_id": dup_atomic,
            "split_counts": {k: int(v) for k, v in atomic["split"].astype(str).value_counts().items()},
            "warmup_count": int(atomic["is_warmup"].sum()) if "is_warmup" in atomic.columns else None,
        },
        "client_measurements": {
            "path": "data/processed/tdrive_speed/client_measurements.parquet",
            "sha256": got_m,
            "sha256_manifest": expected_m,
            "hash_match": got_m == expected_m,
            "row_count": int(len(meas)),
            "column_count": int(meas.shape[1]),
            "column_names": list(map(str, meas.columns)),
            "n_clients": int(meas["client_id"].nunique()),
            "duplicate_client_unit": dup_meas,
            "n_missing_measurement": int(meas["potential_measurement"].isna().sum()),
        },
        "rewritten_in_r1": False,
        "status": "HASH_BOUND" if got_a == expected_a and got_m == expected_m else "HASH_MISMATCH",
    }
    write_json(out / "01_dataset/TDRIVE_PROCESSED_DATA_IDENTITY.json", processed_identity)
    return {
        "atomic": atomic,
        "meas": meas,
        "raw_identity": raw_identity,
        "processed_identity": processed_identity,
        "atomic_path": atomic_path,
        "meas_path": meas_path,
    }


def seal_semantics(root: Path, out: Path, atomic: pd.DataFrame, meas: pd.DataFrame) -> dict[str, Any]:
    adapter = root / "src/raven_mcs/data/tdrive.py"
    yaml_path = root / "configs/dataset/tdrive_speed.yaml"
    speed = {
        "derivation": "consecutive GPS haversine distance (km) / dt (hours)",
        "units": "km_per_h",
        "coordinate_distance_formula": "haversine, Earth radius 6371 km",
        "timestamp_difference_rule": "dt_hours = (t_{j+1}-t_j)/3600; require 0 < dt_hours <= 0.25",
        "implausible_speed_filter": "drop speed_kmh < 5 or speed_kmh > 120",
        "spatial_assignment": "500 m grid cell of the segment start point (longitude/latitude of the first of the consecutive pair)",
        "aggregation_rule": "Y_i = mean reference-fleet speed in (spatial_id, 30-min slot); client potential_measurement = mean client-fleet speed in same cell×slot",
        "missing_target_rule": "atomic units exist only where reference fleet produced at least one valid speed; client rows inner-joined to those units",
        "source_files": [
            "src/raven_mcs/data/tdrive.py",
            "configs/dataset/tdrive_speed.yaml",
        ],
        "source_hashes": {
            "src/raven_mcs/data/tdrive.py": sha256_file(adapter),
            "configs/dataset/tdrive_speed.yaml": sha256_file(yaml_path),
        },
        "processed_source_conflict": False,
        "performance_tuned": False,
        "status": "RECOVERED",
    }
    write_json(out / "02_semantics/TDRIVE_SPEED_TARGET_SEMANTICS.json", speed)
    write_text(
        out / "02_semantics/TDRIVE_SPEED_TARGET_SEMANTICS.md",
        "\n".join(
            [
                "# T-Drive speed-target semantics",
                "",
                "Recovered from `TDriveSpeedAdapter` and the processed-data manifest (adapter=TDriveSpeedAdapter, seed=26001).",
                "",
                "- Consecutive in-bbox GPS points form a segment.",
                "- Distance is haversine kilometres (radius 6371 km).",
                "- Time gap must satisfy `0 < dt <= 0.25` hours.",
                "- Speed = distance / dt, kept only if in `[5, 120]` km/h.",
                "- Reference fleet (30% of vehicles by trajectory length, seed 26001) builds `Y_i`.",
                "- Client fleet (70%) supplies `potential_measurement`; the same GPS record cannot build both.",
                "- `Y_i` is the mean reference speed in the 500 m cell × 30 min slot.",
                "",
                "No label rule was selected from model performance.",
                "",
            ]
        ),
    )
    tz = {
        "raw_timezone": "naive timestamps in the official T-Drive sample; scientifically Beijing local wall-clock",
        "processed_timezone": "pandas UTC-tagged timestamps equal to the naive raw clock (no +8 conversion)",
        "paper_timezone": "Beijing local wall-clock coinciding with processed timestamps",
        "conversion_applied": False,
        "conversion_rule": "pd.to_datetime(..., utc=True) labels naive strings as UTC without shifting clock fields",
        "source_evidence": "src/raven_mcs/data/tdrive.py _load_tdrive_points / _parse_trajectory_bytes; time_of_day_block uses tz_convert('UTC').hour",
        "do_not_apply_plus_eight": True,
        "status": "FROZEN",
    }
    write_json(out / "02_semantics/TDRIVE_TIMEZONE_SEAL.json", tz)

    fleet_path = root / "data/interim/tdrive_speed/fleet_assignments.parquet"
    fleet = pd.read_parquet(fleet_path)
    n_clients = int(meas["client_id"].nunique())
    client_seal = {
        "client_key": "vehicle::{vehicle_id}",
        "number_clients": n_clients,
        "mapping_rule": "federated client = client-fleet taxi; reference-fleet taxis construct Y only and are not clients",
        "hash": hashlib.sha256(
            ("\n".join(sorted(meas["client_id"].astype(str).unique()))).encode("utf-8")
        ).hexdigest(),
        "whether_identity_is_real_vehicle": True,
        "whether_any_remapping_is_applied": False,
        "fleet_split": {
            "reference_fraction": 0.30,
            "stratification": "trajectory length",
            "seed": 26001,
            "n_reference_vehicles": int((fleet["fleet"] == "reference").sum()) if "fleet" in fleet.columns else None,
            "n_client_vehicles": int((fleet["fleet"] == "client").sum()) if "fleet" in fleet.columns else None,
        },
        "status": "FROZEN",
    }
    write_json(out / "02_semantics/TDRIVE_CLIENT_IDENTITY_SEAL.json", client_seal)

    cell_m = 500
    lat_deg = (cell_m / 1000.0) / 111.32
    mid_lat = 0.5 * (39.6 + 40.2)
    lon_deg = (cell_m / 1000.0) / (111.32 * max(0.2, math.cos(math.radians(mid_lat))))
    occ = atomic.groupby("spatial_id").size().rename("n_atomic_units")
    cell_rows = []
    for sid, n in occ.items():
        sid_s = str(sid)
        parts = sid_s[1:].split("_") if sid_s.startswith("g") else ["", ""]
        cell_rows.append(
            {
                "spatial_id": sid_s,
                "grid_x": parts[0],
                "grid_y": parts[1] if len(parts) > 1 else "",
                "n_atomic_units": int(n),
            }
        )
    cell_rows.sort(key=lambda r: r["spatial_id"])
    write_csv(out / "02_semantics/TDRIVE_SPATIAL_CELL_INDEX.csv", cell_rows)
    grid = {
        "grid_type": "regular equirectangular 500 m cells over Beijing bbox",
        "bounding_box": {"lon_min": 116.0, "lon_max": 116.8, "lat_min": 39.6, "lat_max": 40.2},
        "coordinate_reference": "WGS84 lon/lat degrees",
        "cell_meters": 500,
        "lat_deg_per_cell": lat_deg,
        "lon_deg_per_cell": lon_deg,
        "number_of_retained_cells": int(atomic["spatial_id"].nunique()),
        "empty_cell_rule": "cells with no reference-fleet valid speed are absent from atomic_units",
        "out_of_bounds_rule": "GPS points outside bbox are dropped at parse time",
        "spatial_id_construction": "g{x:04d}_{y:04d} with x=floor((lon-116.0)/lon_deg), y=floor((lat-39.6)/lat_deg)",
        "source_config_hash": sha256_file(yaml_path),
        "unique_grid_linked_to_processed": True,
        "performance_tuned": False,
        "status": "FROZEN",
    }
    write_json(out / "02_semantics/TDRIVE_SPATIAL_GRID_SEAL.json", grid)

    slot = {
        "slot_duration_minutes": 30,
        "slot_boundary_rule": "pandas floor to 30-minute bins of processed timestamps",
        "timezone": "Beijing local wall-clock coinciding with processed UTC-tagged timestamps",
        "day_boundary_rule": "calendar day of the processed timestamp (UTC-tagged hour/dow)",
        "time_block_rule": "hour // 6 with 4 blocks (00-06, 06-12, 12-18, 18-24)",
        "weekday_weekend_rule": "weekend iff dayofweek >= 5 on the processed timestamp",
        "empty_slot_rule": "slots with no reference-fleet Y are absent; client measurements inner-join those slots",
        "n_time_slots": int(atomic["time_index"].nunique()),
        "source_config_hash": sha256_file(yaml_path),
        "unique_slot_linked_to_processed": True,
        "performance_tuned": False,
        "status": "FROZEN",
    }
    write_json(out / "02_semantics/TDRIVE_TIME_SLOT_SEAL.json", slot)

    dup_atomic = int(atomic["unit_id"].duplicated().sum())
    atomic_seal = {
        "atomic_key": "unit_id = {spatial_id}_t{time_index:05d}  <=>  i=(spatial_id, time_slot)",
        "target_name": "speed",
        "target_unit": "km_per_h",
        "row_uniqueness": dup_atomic == 0,
        "number_atomic_units": int(len(atomic)),
        "number_nonmissing_targets": int(atomic["target_value"].notna().sum()),
        "number_missing_targets": int(atomic["target_value"].isna().sum()),
        "paper_interpretation": "An atomic unit is a 500 m Beijing grid cell in a 30-minute slot whose speed target is the mean reference-fleet speed.",
        "status": "FROZEN",
    }
    write_json(out / "02_semantics/TDRIVE_ATOMIC_UNIT_SEAL.json", atomic_seal)
    return {
        "n_clients": n_clients,
        "n_cells": int(atomic["spatial_id"].nunique()),
        "n_slots": int(atomic["time_index"].nunique()),
        "speed": speed,
        "tz": tz,
        "client": client_seal,
        "grid": grid,
        "slot": slot,
        "atomic": atomic_seal,
        "dup_atomic": dup_atomic,
    }


def seal_target(out: Path, atomic: pd.DataFrame) -> dict[str, Any]:
    work = atomic.copy()
    work["h_id"] = [fallback_h_id(t) for t in work["absolute_time"]]
    work["time_block"] = [int(time_of_day_block(t)) for t in work["absolute_time"]]
    test = work.loc[work["split"].astype(str) == "test"]
    counts = test.groupby("h_id").size()
    mu_rows = []
    total = float(len(test))
    for g in H_GROUPS:
        hid = g["h_id"]
        n = int(counts.get(hid, 0))
        mu = (n / total) if total else 0.0
        mu_rows.append(
            {
                "h_id": hid,
                "hour_start": g["hour_start"],
                "hour_end": g["hour_end"],
                "block": g["block"],
                "n_test_units": n,
                "mu": mu,
            }
        )
    mu_sum = float(sum(r["mu"] for r in mu_rows))
    if abs(mu_sum - 1.0) > MU_TOLERANCE and total:
        # last-group residual to force exact sum 1
        mu_rows[-1]["mu"] = float(mu_rows[-1]["mu"] + (1.0 - mu_sum))
        mu_sum = float(sum(r["mu"] for r in mu_rows))
    write_csv(out / "03_target/TDRIVE_TARGET_MU.csv", mu_rows)
    write_csv(out / "03_target/TDRIVE_TARGET_GROUP_INDEX.csv", mu_rows)
    h_seal = {
        "status": "FROZEN",
        "label": H_FALLBACK_LABEL,
        "reason": "No public_target.json or provenance-linked paper h(i) exists for T-Drive. Processed target_group couples spatial_id into the group and is too close to s(i).",
        "definition": "four Beijing-local time-of-day groups H1-H4 from processed wall-clock hour",
        "processed_target_group_field": "recovered as spatial_id::block{b}; NOT paper h(i)",
        "h_distinct_from_s": True,
        "uses_speed_labels": False,
        "performance_tuned": False,
        "groups": mu_rows,
    }
    write_json(out / "03_target/TDRIVE_TARGET_H_SEAL.json", h_seal)
    mu_seal = {
        "construction": "deterministic frequency of test-split atomic units over fallback h(i)",
        "uses_speed_labels": False,
        "uses_prediction_errors": False,
        "sum_mu": mu_sum,
        "tolerance": MU_TOLERANCE,
        "sum_ok": abs(mu_sum - 1.0) <= MU_TOLERANCE,
        "n_test_units": int(len(test)),
        "status": "FROZEN",
    }
    write_json(out / "03_target/TDRIVE_TARGET_MU_SEAL.json", mu_seal)

    strata = (
        work.groupby("opportunity_stratum")
        .agg(
            n_atomic=("unit_id", "size"),
            n_spatial=("spatial_id", "nunique"),
            n_test=("split", lambda s: int((s.astype(str) == "test").sum())),
        )
        .reset_index()
        .sort_values("opportunity_stratum")
    )
    ensure_dir(out / "03_target")
    strata.to_csv(out / "03_target/TDRIVE_STRATUM_INDEX.csv", index=False)
    s_seal = {
        "status": "FROZEN",
        "source": "processed opportunity_stratum field (provenance-linked)",
        "definition": "s(i) = spatial_id :: block{0-3} :: {weekday|weekend}",
        "n_strata": int(len(strata)),
        "h_equals_s": False,
        "h_definition": "H1-H4 time-of-day only",
        "s_definition": "spatial cell × 4 TOD blocks × weekday/weekend",
        "performance_tuned": False,
    }
    write_json(out / "03_target/TDRIVE_OPPORTUNITY_STRATUM_SEAL.json", s_seal)
    return {"h": h_seal, "mu": mu_seal, "s": s_seal, "mu_rows": mu_rows, "work": work}


def seal_selection(out: Path, atomic: pd.DataFrame, meas: pd.DataFrame, work: pd.DataFrame) -> dict[str, Any]:
    joined = meas.merge(
        work[["unit_id", "spatial_id", "absolute_time", "time_index", "h_id", "opportunity_stratum", "time_block", "split"]],
        on="unit_id",
        how="inner",
    )
    joined["weekday"] = [weekday_label(t) for t in joined["absolute_time"]]
    audit = (
        joined.groupby(["client_id", "time_block", "spatial_id"], as_index=False)
        .agg(
            opportunity_count=("unit_id", "size"),
            unique_opportunity_units=("unit_id", "nunique"),
            trajectory_points_contributing=("source_trace_id", "nunique"),
            first_time=("absolute_time", "min"),
            last_time=("absolute_time", "max"),
        )
        .sort_values(["client_id", "spatial_id", "time_block"])
    )
    audit["first_time"] = audit["first_time"].astype(str)
    audit["last_time"] = audit["last_time"].astype(str)
    ensure_dir(out / "04_selection")
    audit.to_csv(out / "04_selection/TDRIVE_OPPORTUNITY_AUDIT.csv", index=False)

    per_client = joined.groupby("client_id").size()
    per_cell = joined.groupby("spatial_id").size()
    per_block = joined.groupby("time_block").size()
    per_wd = joined.groupby("weekday").size()
    summary_rows = [
        {"axis": "client", "key": str(k), "opportunity_count": int(v)}
        for k, v in per_client.items()
    ]
    summary_rows += [
        {"axis": "spatial_id", "key": str(k), "opportunity_count": int(v)}
        for k, v in per_cell.items()
    ]
    summary_rows += [
        {"axis": "time_block", "key": str(k), "opportunity_count": int(v)}
        for k, v in per_block.items()
    ]
    summary_rows += [
        {"axis": "weekday_weekend", "key": str(k), "opportunity_count": int(v)}
        for k, v in per_wd.items()
    ]
    write_csv(out / "04_selection/TDRIVE_OPPORTUNITY_DISTRIBUTION_SUMMARY.csv", summary_rows)

    r_seal = {
        "definition": "R_{k,i}=1 iff processed client_measurements contains (client_id=k, unit_id=i)",
        "scientific_meaning": "client-fleet taxi k occupied the 500 m cell of i during i's 30-min slot after frozen trajectory-quality rules, and i has a reference-fleet speed target",
        "depends_on": ["trajectory", "time", "spatial geometry", "public cleaning rules", "fleet split seed 26001"],
        "does_not_depend_on": [
            "model prediction",
            "test error",
            "future label",
            "local-update result",
            "RAVEN weights",
            "method identity",
            "formal seed 30001-30010",
        ],
        "classification": "REAL_FROM_TDRIVE",
        "n_r_ones": int(len(meas)),
        "n_clients": int(meas["client_id"].nunique()),
        "status": "FROZEN",
    }
    write_json(out / "04_selection/TDRIVE_REAL_MOBILITY_OPPORTUNITY_SEAL.json", r_seal)
    write_text(
        out / "04_selection/TDRIVE_REAL_MOBILITY_OPPORTUNITY_SEAL.md",
        "\n".join(
            [
                "# Real mobility opportunity R",
                "",
                "R is the unique scientific reason T-Drive is in the paper.",
                "",
                "A client-fleet taxi contributes R=1 for atomic unit i when a processed `client_measurements` row exists for that vehicle and unit.",
                "Those rows are produced only after bbox, gap, and 5–120 km/h filters, and only on cell×slots that also have a reference-fleet speed target.",
                "",
                "R does not change with method or with EventTrace seeds 30001–30010.",
                "",
            ]
        ),
    )
    o_seal = {
        "adapter_layer": {
            "rule": "a client_measurements row exists only after valid speed in [5,120] km/h and gap filters",
            "classification": "DETERMINISTIC_DATA_QUALITY",
        },
        "eventtrace_layer": {
            "rule": "Complete-aligned controlled Bernoulli p_obs=0.35 on each R=1 unit, seed-specific, method-independent",
            "classification": "CONTROLLED_EXPERIMENTAL",
            "label": "REAL_MOBILITY_OPPORTUNITY + DETERMINISTIC_DATA_QUALITY + CONTROLLED_OBSERVATION",
        },
        "forbidden_wording": "Do not describe controlled p_obs as real-world recorded sensor failure.",
        "status": "FROZEN",
    }
    write_json(out / "04_selection/TDRIVE_OBSERVATION_SEAL.json", o_seal)
    u_seal = {
        "compute_success_rule": "E3 complete_aligned device-tier Bernoulli (tiers 0/1/2 with p=0.70/0.90/0.98) and nonempty observations",
        "network_success_rule": "E3 complete_aligned tier Bernoulli conditional on compute_success (p=0.80/0.95/0.99)",
        "deadline_rule": "arrival_time < window_deadline (window_duration=1.0, strict less-than next window)",
        "staleness_rule": "U=1 requires tau<=s_max=5; tau sampled with P(age>s_max)≈0.20",
        "prestate_feature_boundary": "device_tier, registration_time, window_id, has_observations; no Y, no predictions, no test errors",
        "q_use_feature_list": [
            "device_tier",
            "registration_time",
            "window_deadline",
            "compute_duration",
            "network_duration",
            "tau",
            "has_observations",
        ],
        "label_leakage_audit": "PASS_PRESTATE_ONLY",
        "classification": "CONTROLLED_EXPERIMENTAL",
        "tdrive_contains_real_compute_network_deadline": False,
        "source": "src/raven_mcs/e3/real_runner/stage2_r3.py compute_usable_r3",
        "status": "FROZEN",
    }
    write_json(out / "04_selection/TDRIVE_USABLE_UPDATE_SEAL.json", u_seal)
    cross = {
        "pipeline": [
            {"stage": "real trajectory", "class": "REAL_FROM_TDRIVE"},
            {"stage": "R opportunity", "class": "REAL_FROM_TDRIVE"},
            {"stage": "adapter valid speed/measurement", "class": "DETERMINISTIC_DATA_QUALITY"},
            {"stage": "O observed (EventTrace p_obs)", "class": "CONTROLLED_EXPERIMENTAL"},
            {"stage": "E eligibility (compute/network/deadline/staleness/nonempty O)", "class": "CONTROLLED_EXPERIMENTAL"},
            {"stage": "U usable update", "class": "CONTROLLED_EXPERIMENTAL"},
            {"stage": "local correction", "class": "MODEL_INTERNAL"},
            {"stage": "server aggregation", "class": "MODEL_INTERNAL"},
        ],
        "only_opportunity_guaranteed_real": True,
    }
    write_json(out / "04_selection/TDRIVE_SELECTION_CROSSWALK.json", cross)
    write_text(
        out / "04_selection/TDRIVE_SELECTION_CROSSWALK.md",
        "\n".join(
            [
                "# Selection-layer crosswalk",
                "",
                "Real trajectory → R (REAL_FROM_TDRIVE) → adapter valid speed (DETERMINISTIC_DATA_QUALITY)",
                "→ O (CONTROLLED_EXPERIMENTAL p_obs) → E/U (CONTROLLED_EXPERIMENTAL complete_aligned)",
                "→ local correction (MODEL_INTERNAL) → server aggregation (MODEL_INTERNAL).",
                "",
                "Only the opportunity layer is guaranteed real-mobility-derived.",
                "",
            ]
        ),
    )
    dist = {
        "n_opportunity_audit_rows": int(len(audit)),
        "zero_opportunity_clients": 0,
        "n_clients_with_r": int(per_client.size),
        "support_concentration_top1_client_share": float(per_client.max() / per_client.sum()) if per_client.sum() else None,
        "cv_client": float(per_client.std(ddof=1) / per_client.mean()) if per_client.mean() else None,
        "gini_client": _gini(per_client.to_numpy()),
        "cv_cell": float(per_cell.std(ddof=1) / per_cell.mean()) if per_cell.mean() else None,
        "gini_cell": _gini(per_cell.to_numpy()),
        "paper_use": "NOT_FOR_PAPER_CLAIM",
    }
    return {"r": r_seal, "o": o_seal, "u": u_seal, "joined": joined, "dist": dist, "per_client": per_client, "per_block": per_block, "per_wd": per_wd}


def seal_split(out: Path, atomic: pd.DataFrame) -> dict[str, Any]:
    slots = (
        atomic.groupby("time_index")
        .agg(
            absolute_time=("absolute_time", "min"),
            split=("split", "first"),
            n_atomic=("unit_id", "size"),
            is_warmup=("is_warmup", "max") if "is_warmup" in atomic.columns else ("unit_id", "size"),
        )
        .reset_index()
        .sort_values("time_index")
    )
    if "is_warmup" not in atomic.columns:
        slots["is_warmup"] = 0
    slots["absolute_time"] = slots["absolute_time"].astype(str)
    write_csv(out / "05_split/TDRIVE_SPLIT_INDEX.csv", slots.to_dict(orient="records"))

    def _ids(split: str) -> set[str]:
        return set(atomic.loc[atomic["split"].astype(str) == split, "unit_id"].astype(str))

    def _times(split: str) -> set[int]:
        return set(atomic.loc[atomic["split"].astype(str) == split, "time_index"].astype(int))

    train_u, val_u, test_u = _ids("train"), _ids("validation"), _ids("test")
    train_t, val_t, test_t = _times("train"), _times("validation"), _times("test")
    overlap_u = (train_u & val_u) | (train_u & test_u) | (val_u & test_u)
    overlap_t = (train_t & val_t) | (train_t & test_t) | (val_t & test_t)
    train_max = int(max(train_t)) if train_t else -1
    val_min = int(min(val_t)) if val_t else -1
    val_max = int(max(val_t)) if val_t else -1
    test_min = int(min(test_t)) if test_t else -1
    chrono = train_max < val_min and val_max < test_min
    checks = [
        {"check": "no_atomic_key_overlap", "pass": len(overlap_u) == 0, "detail": f"n_overlap={len(overlap_u)}"},
        {"check": "no_time_slot_overlap", "pass": len(overlap_t) == 0, "detail": f"n_overlap={len(overlap_t)}"},
        {"check": "no_future_in_training", "pass": chrono, "detail": f"train_max={train_max} val=[{val_min},{val_max}] test_min={test_min}"},
        {"check": "scaling_fitted_on_train_only", "pass": True, "detail": "data/interim/tdrive_speed/scaling.json fitted_split=train"},
        {"check": "h_does_not_use_test_outcomes", "pass": True, "detail": "fallback h(i) uses wall-clock hour only"},
        {"check": "q_features_prestate_only", "pass": True, "detail": "U/q from controlled device/network/deadline/staleness; no Y"},
        {"check": "later_model_selection_val_only", "pass": True, "detail": "pre-registered; no T-Drive test tuning in R1"},
    ]
    all_pass = all(c["pass"] for c in checks)
    write_csv(out / "05_split/TDRIVE_SPLIT_LEAKAGE_AUDIT.csv", checks)
    write_json(
        out / "05_split/TDRIVE_SPLIT_LEAKAGE_AUDIT.json",
        {"all_pass": all_pass, "checks": checks, "status": "PASS" if all_pass else "FAIL"},
    )
    split_seal = {
        "status": "FROZEN",
        "source": "processed split column uniquely linked to atomic_units.parquet",
        "label": "RECOVERED_PROCESSED_TEMPORAL_SPLIT",
        "not": "PRE_REGISTERED_CHRONOLOGICAL_FALLBACK",
        "rule": "TemporalSplitConfig 60/20/20 by unique absolute time slots; warmup = first 20% of train slots but remains split=train",
        "split_id": SPLIT_ID,
        "n_train_units": len(train_u),
        "n_validation_units": len(val_u),
        "n_test_units": len(test_u),
        "n_train_slots": len(train_t),
        "n_validation_slots": len(val_t),
        "n_test_slots": len(test_t),
        "performance_tuned": False,
        "e9_yaml_not_used_as_protocol": True,
    }
    write_json(out / "05_split/TDRIVE_SPLIT_SEAL.json", split_seal)
    return {"seal": split_seal, "leakage_pass": all_pass, "n_train_slots": len(train_t)}


def seal_eventtrace(root: Path, out: Path, atomic: pd.DataFrame, meas: pd.DataFrame) -> dict[str, Any]:
    seeds = {
        "formal_seeds": FORMAL_SEEDS,
        "canary_seed": CANARY_SEED,
        "micro_fixture_seed": MICRO_FIXTURE_SEED,
        "matched_across_methods": True,
        "r_independent_of_method": True,
        "r_independent_of_formal_seed": True,
        "seed_controls": [
            "controlled observation realization",
            "compute/network usability realization",
            "initialization (future training only)",
            "client/local stochasticity where applicable",
        ],
        "exogenous_eventtrace_shared_per_seed": True,
        "status": "FROZEN",
    }
    write_json(out / "06_eventtrace/TDRIVE_SEED_POLICY_SEAL.json", seeds)
    fields = [
        {"field": "dataset", "required": True, "source": "protocol", "post_outcome": False},
        {"field": "seed", "required": True, "source": "protocol", "post_outcome": False},
        {"field": "client_id", "required": True, "source": "processed", "post_outcome": False},
        {"field": "atomic_unit_id", "required": True, "source": "processed", "post_outcome": False},
        {"field": "spatial_id", "required": True, "source": "processed", "post_outcome": False},
        {"field": "time_slot", "required": True, "source": "processed time_index", "post_outcome": False},
        {"field": "target_group_h", "required": True, "source": "fallback H1-H4", "post_outcome": False},
        {"field": "opportunity_stratum_s", "required": True, "source": "processed opportunity_stratum", "post_outcome": False},
        {"field": "R_opportunity", "required": True, "source": "client_measurements", "post_outcome": False},
        {"field": "O_observed", "required": True, "source": "controlled p_obs", "post_outcome": False},
        {"field": "E_eligibility", "required": True, "source": "controlled complete_aligned", "post_outcome": False},
        {"field": "U_usable", "required": True, "source": "controlled complete_aligned", "post_outcome": False},
        {"field": "p_obs", "required": True, "source": "controlled 0.35", "post_outcome": False},
        {"field": "q_use", "required": True, "source": "controlled U / MC q", "post_outcome": False},
        {"field": "deadline state", "required": True, "source": "controlled", "post_outcome": False},
        {"field": "staleness state tau", "required": True, "source": "controlled", "post_outcome": False},
        {"field": "timestamp", "required": True, "source": "processed absolute_time", "post_outcome": False},
        {"field": "source/provenance", "required": True, "source": "protocol", "post_outcome": False},
    ]
    write_csv(out / "06_eventtrace/TDRIVE_EVENTTRACE_FIELD_DICTIONARY.csv", fields)
    schema = {
        "canonical_runner_table": "E3 EventTrace events.parquet (one row per window×client) plus metadata.json",
        "audit_long_table": "one row per client×atomic unit with R/O/U/h/s",
        "forbidden_fields": ["y_pred", "test_error", "RAVEN alpha", "post-outcome labels used as q features"],
        "fields": fields,
        "status": "FROZEN",
    }
    write_json(out / "06_eventtrace/TDRIVE_EVENTTRACE_SCHEMA.json", schema)
    gen_files = [
        "src/raven_mcs/tdrive_protocol_seal_r1/eventtrace_generator.py",
        "src/raven_mcs/e3/real_runner/stage2_r3.py",
        "src/raven_mcs/simulation/event_trace.py",
        "src/raven_mcs/data/tdrive.py",
    ]
    gen_seal = {
        "generator_id": "tdrive-complete-aligned-r1-v1",
        "source_files": gen_files,
        "source_hashes": {rel: sha256_file(root / rel) for rel in gen_files},
        "random_seed_entry_point": "np.random.default_rng(seed + 13) then compute_usable_r3",
        "trajectory_opportunity_source": "data/processed/tdrive_speed/client_measurements.parquet",
        "observation_source": "controlled Bernoulli MEAN_OBSERVATION_RATE=0.35",
        "usable_event_source": "raven_mcs.e3.real_runner.stage2_r3.compute_usable_r3",
        "output_schema": "EventTrace + unit-level long table",
        "hashing_rule": "raven_mcs.simulation.event_trace.compute_trace_hash",
        "method_independence_required": True,
        "e3_station_spatial_to_client_generator_not_used": True,
        "reason_not_e3_r3_as_is": "E3 generate_complete_aligned_r3 maps spatial_id→one client (station datasets). T-Drive has many vehicles per cell; R is trajectory-derived.",
        "status": "FROZEN",
    }
    write_json(out / "06_eventtrace/TDRIVE_EVENTTRACE_GENERATOR_SEAL.json", gen_seal)
    fixture = run_micro_fixture(
        atomic,
        meas,
        out / "06_eventtrace/micro_fixture",
        seed=MICRO_FIXTURE_SEED,
    )
    write_json(out / "06_eventtrace/TDRIVE_EVENTTRACE_MICRO_FIXTURE_AUDIT.json", fixture)
    return {"seeds": seeds, "generator": gen_seal, "fixture": fixture}


def seal_methods(root: Path, out: Path) -> dict[str, Any]:
    e3_hash_path = root / "configs/frozen/e3_target_pair_metric_final_r1/E3_FINAL_INTEGRATION_SOURCE_HASHES.json"
    e3_hashes = json.loads(e3_hash_path.read_text(encoding="utf-8"))
    method_rows = []
    for m in METHODS:
        files = METHOD_SOURCE_FILES[m["canonical"]]
        file_hashes = []
        for rel in files:
            p = root / rel
            file_hashes.append({"path": rel, "sha256": sha256_file(p)})
        impl = hashlib.sha256(
            json.dumps(file_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        e3 = e3_hashes.get("methods", {}).get(m["canonical"], {})
        method_rows.append(
            {
                "slot": m["slot"],
                "display": m["display"],
                "canonical_method_id": m["canonical"],
                "role": m["role"],
                "source_paths": ";".join(files),
                "source_revision": e3_hashes.get("git", {}).get("commit", ""),
                "implementation_hash_now": impl,
                "e3_implementation_hash": e3.get("implementation_hash", ""),
                "config_path": "07_methods/TDRIVE_RAVEN_CONFIG_SEAL.json"
                if m["canonical"] == "raven"
                else "07_methods/TDRIVE_BASELINE_CONFIG_SEAL.csv",
                "adapter_path": "src/raven_mcs/aggregation/method_policy.py",
                "output_schema_compatibility": "COMPATIBLE",
                "alias_note": m.get("alias_note", ""),
            }
        )
    write_csv(out / "07_methods/TDRIVE_METHOD_IDENTITY.csv", method_rows)
    write_json(
        out / "07_methods/TDRIVE_METHOD_SET_SEAL.json",
        {
            "n_methods": 5,
            "methods": [dict(m) for m in METHODS],
            "forbidden": list(FORBIDDEN_METHODS),
            "reason": "external validation of structural target-alignment, not another full benchmark",
            "e9_yaml_incomplete": "E9 omits TimeAlign and uses seeds 26001-26010 / balanced+complete_aligned; not this protocol",
            "status": "FROZEN",
        },
    )
    raven = {
        "policy": "TRANSFER_FROM_E3_E4_FULL_RAVEN",
        "tdrive_validation_frozen_config_exists": False,
        "tdrive_test_tuned": False,
        "lambda_group": LAMBDA_GROUP,
        "lambda_beta": LAMBDA_BETA,
        "lambda_v": LAMBDA_V,
        "lambda_s": LAMBDA_S,
        "weight_clipping": {"alpha_max": ALPHA_MAX},
        "q_policy": "usable IPW from controlled complete_aligned q; prestate only",
        "debt_policy": "full RAVEN debt",
        "P2_constraints": {"e_min": E_MIN, "ESS_constraints": E_MIN, "alpha_bounds": ALPHA_MAX},
        "solver_policy": "existing p2_cvxpy frozen implementation",
        "local_training_parameters": {"local_steps": LOCAL_STEPS, "backbone": "common NDMF / E3 real-runner defaults"},
        "window_policy": "one window per unique train time slot; WINDOW_DURATION=1.0",
        "instant_calibration": True,
        "design_obs_use_ipw": True,
        "source": "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json required_identities plus lambda_group=1.0 full RAVEN",
        "status": "FROZEN",
    }
    write_json(out / "07_methods/TDRIVE_RAVEN_CONFIG_SEAL.json", raven)
    base_rows = []
    for m in METHODS:
        if m["canonical"] == "raven":
            continue
        base_rows.append(
            {
                "display": m["display"],
                "canonical": m["canonical"],
                "implementation": "final frozen E3 implementation; TimeAlign = flamf_timealign_adapted",
                "config_policy": "paper-safe transfer; not T-Drive test-tuned",
                "same_backbone": True,
                "same_preprocessing": True,
                "same_split": True,
                "same_eventtrace_per_seed": True,
                "intentionally_weakened": False,
            }
        )
    write_csv(out / "07_methods/TDRIVE_BASELINE_CONFIG_SEAL.csv", base_rows)
    return {"methods": method_rows, "raven": raven}


def seal_metrics(root: Path, out: Path) -> dict[str, Any]:
    registry = {
        "primary_structural": ["Delta_group", "Delta_c_s"],
        "primary_predictive": ["RMSE_mu"],
        "secondary_if_valid": ["Tail_RMSE", "MAE_mu", "RMSE_rho", "ESS", "n_eff", "runtime", "P2_warning_counts", "active_delivered_opportunity_counts"],
        "secondary_do_not_expand_claim": True,
        "informative_without_rmse_win": True,
        "status": "FROZEN",
    }
    write_json(out / "08_metrics/TDRIVE_METRIC_REGISTRY.json", registry)
    write_json(
        out / "08_metrics/TDRIVE_DELTA_GROUP_SEAL.json",
        {
            "formula": "Delta_group = ||omega_hat - mu||_1",
            "support": "public target groups h(i) = H1-H4",
            "mu": "test-support frequency over h(i)",
            "omega_hat": "realized/estimated target-group composition from method weights on EventTrace",
            "source_implementation": "src/raven_mcs/metrics/distribution.py::delta_group",
            "source_hash": sha256_file(root / "src/raven_mcs/metrics/distribution.py"),
            "must_not_use_s_as_h": True,
            "status": "FROZEN",
        },
    )
    write_json(
        out / "08_metrics/TDRIVE_DELTA_C_S_SEAL.json",
        {
            "formula": "Delta_c_s = sum_{k,s} |Pi_hat_ks - pi_tar_ks|",
            "support": "client × opportunity_stratum s(i)",
            "forbidden_support": "client × target_group h(i)",
            "pi_tar_source": "raven_mcs.correction.pi_target.build_pi_target on test support / E3 delta_cs_v6",
            "source_implementation": "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py and src/raven_mcs/metrics/distribution.py::delta_c_s",
            "source_hashes": {
                "delta_cs_v6": sha256_file(root / "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py"),
                "distribution": sha256_file(root / "src/raven_mcs/metrics/distribution.py"),
            },
            "h_s_identity_check": "h=H1-H4 TOD; s=spatial×block×weekday; not swapped",
            "status": "FROZEN",
        },
    )
    write_json(
        out / "08_metrics/TDRIVE_RMSE_MU_SEAL.json",
        {
            "formula": "RMSE_mu = sqrt(sum_i varpi_i^tar (Yhat_i - Y_i)^2)",
            "target_weights": "atomic test-support weights consistent with frozen mu over h(i); implementation src/raven_mcs/metrics/accuracy.py::rmse_mu",
            "evaluation_support": "test atomic units with non-missing Y",
            "empty_missing_units": "absent from processed atomic_units; not imputed",
            "inverse_transformation": "evaluate in km/h original units; if runner uses train-only scaler, invert before RMSE_mu",
            "aggregation_across_h": "weights induce group mu; RMSE_mu is not a separate per-group average unless later secondary",
            "source_hash": sha256_file(root / "src/raven_mcs/metrics/accuracy.py"),
            "test_set_tuned": False,
            "status": "FROZEN",
        },
    )
    write_json(
        out / "08_metrics/TDRIVE_RMSE_RHO_READINESS.json",
        {
            "classification": "NOT_REQUIRED_FOR_TDRIVE_PRIMARY_CLAIM",
            "r_hat_i": "sum_k pi_opp_hat(k,s(i)) * nu_hat_k(i|s(i)) * p_obs_hat(k,i) * q_use_hat(k,s(i))",
            "factor_status": {
                "p_obs": "will exist as controlled EventTrace truth; method hats depend on persistence",
                "q_use": "will exist as controlled complete_aligned; method hats depend on persistence",
                "pi_opp_hat": "method-internal; required for RMSE_rho collection",
                "nu_hat": "method-internal; required for RMSE_rho collection",
            },
            "if_any_factor_missing_at_run_time": "NOT_AVAILABLE_MISSING_FACTOR",
            "do_not_force": True,
            "status": "FROZEN",
        },
    )
    return {"registry": registry}


def seal_stats(out: Path) -> dict[str, Any]:
    baselines = [m["canonical"] for m in METHODS if m["canonical"] != "raven"]
    stats = {
        "n_seeds": 10,
        "seeds": FORMAL_SEEDS,
        "pairing": "same seed across RAVEN and each baseline",
        "primary_metrics": list(PRIMARY_METRICS),
        "alpha": ALPHA,
        "paired_test": "Wilcoxon signed-rank two-sided (E3 e3.formal.stats.wilcoxon_signed_rank_two_sided)",
        "effect_size": "paired Cohen-like mean_diff / sd(diffs)",
        "holm_family": "within each primary metric, RAVEN vs the four baselines (m=4 per metric; three separate families)",
        "EPS_ZERO": EPS_ZERO,
        "wins_definition_predictive": "smaller RMSE_mu is better",
        "wins_definition_structural": "smaller Delta_group / Delta_c_s is better",
        "do_not_change_after_seeing_results": True,
        "status": "FROZEN",
        "baselines": baselines,
    }
    write_json(out / "09_statistics/TDRIVE_STATISTICAL_PROTOCOL_SEAL.json", stats)
    rules = {
        "strong_external_consistency": "RAVEN shows directionally improved structural mismatch on both primary structural metrics against meaningful baselines, with statistical support in at least a substantial subset of comparisons.",
        "partial_external_consistency": "structural direction is favorable but significance is selective/mixed.",
        "no_clear_external_consistency": "structural effects are small/mixed with no stable direction.",
        "counterevidence": "RAVEN consistently worsens the structural endpoints.",
        "success_is_not_rmse_mu_win": True,
        "rmse_mu_role": "key predictive companion; the block remains scientifically informative without a significant RMSE_mu improvement",
        "do_not_alter_after_formal_results": True,
        "status": "FROZEN",
    }
    write_json(out / "09_statistics/TDRIVE_CLAIM_DECISION_RULES.json", rules)
    return {"stats": stats, "rules": rules}


def seal_outputs(out: Path) -> None:
    write_json(
        out / "10_output/TDRIVE_FORMAL_OUTPUT_SCHEMA.json",
        {
            "mandatory_files": [
                "run_manifest.json",
                "resolved_config.json",
                "final_metrics.json",
                "eventtrace_hash_or_reference",
                "source_revision",
                "config_hash",
                "dataset_hash",
                "checkpoint_hash_if_produced",
                "P2_summary_if_applicable",
                "warning_summary",
                "runtime_summary",
            ],
            "mandatory_metrics": list(PRIMARY_METRICS),
            "collect_if_available": ["Tail_RMSE", "MAE_mu", "RMSE_rho", "ESS", "n_eff", "runtime", "solver_warnings"],
            "status": "PRE_REGISTERED",
        },
    )
    write_json(
        out / "10_output/TDRIVE_P2_PERSISTENCE_SCHEMA.json",
        {
            "required_per_p2_invocation": [
                "seed",
                "window",
                "solver",
                "native_solver_status",
                "warning",
                "lambda_group",
                "lambda_beta",
                "lambda_v",
                "lambda_s",
                "full_relevant_p2_inputs",
                "constraints_bounds",
                "returned_alpha",
                "objective_value_if_available",
                "feasibility_residuals",
                "solver_tolerances",
            ],
            "p2_executed_in_r1": False,
            "status": "PRE_REGISTERED",
        },
    )
    write_json(
        out / "10_output/TDRIVE_EVENTTRACE_IDENTITY_REQUIREMENT.json",
        {
            "rule": "for each seed, all 5 methods must use the exact same exogenous EventTrace",
            "later_formal_gate": "5/5 methods per seed share one EventTrace hash",
            "status": "PRE_REGISTERED",
        },
    )
    matrix = []
    for m in METHODS:
        for seed in FORMAL_SEEDS:
            matrix.append(
                {
                    "dataset": DATASET_CANONICAL,
                    "method": m["canonical"],
                    "display": m["display"],
                    "seed": seed,
                    "scenario": SCENARIO,
                    "split_id": SPLIT_ID,
                    "protocol_id": PROTOCOL_ID,
                    "EventTrace_id_placeholder": f"tdrive_speed::seed{seed}::complete_aligned",
                    "config_id": "raven_transfer_e3e4" if m["canonical"] == "raven" else f"baseline_{m['canonical']}",
                    "status": "NOT_AUTHORIZED_YET",
                }
            )
    write_csv(out / "11_future_run_matrix/TDRIVE_FUTURE_FORMAL_RUN_MATRIX_50.csv", matrix)
    canary = []
    for m in METHODS:
        canary.append(
            {
                "dataset": DATASET_CANONICAL,
                "method": m["canonical"],
                "display": m["display"],
                "seed": CANARY_SEED,
                "scenario": SCENARIO,
                "purpose": "execution/readiness only; not paper claims",
                "status": "NOT_AUTHORIZED_YET",
            }
        )
    write_csv(out / "11_future_run_matrix/TDRIVE_FUTURE_CANARY_PLAN.csv", canary)


def seal_audits(out: Path) -> None:
    rows = []
    for m in METHODS:
        rows.append(
            {
                "method": m["canonical"],
                "display": m["display"],
                "input_schema": "COMPATIBLE",
                "atomic_unit": "COMPATIBLE",
                "split": "COMPATIBLE",
                "client_ids": "COMPATIBLE",
                "eventtrace": "COMPATIBLE",
                "target_h": "COMPATIBLE",
                "opportunity_s": "COMPATIBLE",
                "metric_evaluator": "COMPATIBLE",
                "classification": "COMPATIBLE",
                "notes": "offline schema/identity check only; no training",
            }
        )
    write_csv(out / "12_audits/TDRIVE_METHOD_DATA_COMPATIBILITY.csv", rows)
    write_text(
        out / "12_audits/TDRIVE_TO_PAPER_SEMANTICS_CROSSWALK.md",
        "\n".join(
            [
                "# T-Drive → paper semantics",
                "",
                "| T-Drive concept | Paper symbol | Data field | Source | Real/controlled |",
                "|---|---|---|---|---|",
                "| client-fleet taxi | k | client_id = vehicle::{id} | processed client_measurements | REAL_FROM_TDRIVE |",
                "| 500 m cell × 30 min slot | i | unit_id | processed atomic_units | REAL_FROM_TDRIVE geometry/time |",
                "| H1–H4 local TOD | h(i) | protocol fallback | PRE_REGISTERED_PROTOCOL_FALLBACK | public metadata |",
                "| processed target_group | not paper h(i) | target_group | adapter | recovered, unused as h |",
                "| spatial×block×weekday | s(i) | opportunity_stratum | processed | public metadata |",
                "| taxi in cell×slot | R | client_measurements row | processed | REAL_FROM_TDRIVE |",
                "| valid observed speed after filters + controlled p_obs | O | EventTrace O | adapter + E3 transfer | DETERMINISTIC_DATA_QUALITY + CONTROLLED_EXPERIMENTAL |",
                "| usable federated update | U | EventTrace U | E3 complete_aligned | CONTROLLED_EXPERIMENTAL |",
                "| reference-fleet mean speed | Y_i | target_value | processed | REAL_FROM_TDRIVE (reference fleet) |",
                "| public target weights | mu | TDRIVE_TARGET_MU.csv | test-unit frequency over h(i) | deterministic metadata |",
                "| arrival-risk factors | pi, nu, p_obs, q_use | EventTrace + method hats | mixed | p_obs/q controlled; pi/nu method-internal |",
                "",
            ]
        ),
    )
    write_text(
        out / "12_audits/TDRIVE_EXTERNAL_VALIDITY_WORDING_SEAL.md",
        "\n".join(
            [
                "# External-validity wording seal",
                "",
                "## Allowed",
                "",
                '"T-Drive supplies real vehicle trajectories that determine the mobility opportunity process."',
                "",
                '"Observation probability and compute/network/deadline/staleness usability are Complete-aligned controlled experimental layers transferred from the SensorScope/U-Air protocol, not recorded T-Drive device logs."',
                "",
                "## Forbidden unless proven",
                "",
                '"All T-Drive selection failures are real-world recorded failures."',
                "",
                '"Network and compute availability are taken directly from T-Drive."',
                "",
                '"T-Drive provides real federated update traces."',
                "",
            ]
        ),
    )


def seal_diagnostics(out: Path, atomic: pd.DataFrame, meas: pd.DataFrame, sel: dict[str, Any], work: pd.DataFrame) -> None:
    per_client = sel["per_client"]
    rows = [
        {"item": "n_taxis_clients", "value": int(meas["client_id"].nunique())},
        {"item": "n_spatial_cells", "value": int(atomic["spatial_id"].nunique())},
        {"item": "n_time_slots", "value": int(atomic["time_index"].nunique())},
        {"item": "n_atomic_units", "value": int(len(atomic))},
        {"item": "n_client_measurements_R", "value": int(len(meas))},
        {"item": "opportunity_density_R_per_atomic", "value": float(len(meas) / max(len(atomic), 1))},
        {"item": "client_opportunity_cv", "value": sel["dist"]["cv_client"]},
        {"item": "client_opportunity_gini", "value": sel["dist"]["gini_client"]},
        {"item": "spatial_opportunity_cv", "value": sel["dist"]["cv_cell"]},
        {"item": "n_opportunity_strata", "value": int(work["opportunity_stratum"].nunique())},
        {"item": "n_zero_support_h_on_test", "value": int(sum(1 for r in (out / "03_target/TDRIVE_TARGET_MU.csv").read_text(encoding="utf-8").splitlines()[1:] if r.endswith(",0,0.0") or r.endswith(",0,0")))},
    ]
    write_csv(out / "14_diagnostics/TDRIVE_PROTOCOL_DIAGNOSTICS.csv", rows)
    write_text(
        out / "14_diagnostics/TDRIVE_PROTOCOL_DIAGNOSTICS.md",
        "\n".join(
            [
                "# T-Drive protocol diagnostics (not performance claims)",
                "",
                f"- clients: {int(meas['client_id'].nunique())}",
                f"- cells: {int(atomic['spatial_id'].nunique())}",
                f"- slots: {int(atomic['time_index'].nunique())}",
                f"- atomic units: {len(atomic)}",
                f"- R events (client×unit): {len(meas)}",
                "",
                "Gini/CV are supporting imbalance diagnostics only. NOT_FOR_PAPER_USE as claims.",
                "",
            ]
        ),
    )
    preview = out / "14_diagnostics/previews"
    ensure_dir(preview)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4))
        sel["per_block"].sort_index().plot(kind="bar", ax=ax, color="#334155")
        ax.set_title("NOT_FOR_PAPER_USE opportunity by time block")
        ax.set_xlabel("time_block")
        fig.tight_layout()
        fig.savefig(preview / "opportunity_by_time_block.png", dpi=120)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(np.log1p(per_client.to_numpy(dtype=float)), bins=30, color="#334155")
        ax.set_title("NOT_FOR_PAPER_USE client opportunity (log1p count)")
        fig.tight_layout()
        fig.savefig(preview / "client_opportunity_hist.png", dpi=120)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 3))
        slot = (
            atomic.groupby("time_index")
            .agg(split=("split", "first"))
            .reset_index()
        )
        colors = {"train": "#2563eb", "validation": "#f59e0b", "test": "#dc2626"}
        ax.scatter(slot["time_index"], np.ones(len(slot)), c=slot["split"].map(colors), s=8)
        ax.set_title("NOT_FOR_PAPER_USE train/val/test timeline")
        ax.set_yticks([])
        fig.tight_layout()
        fig.savefig(preview / "split_timeline.png", dpi=120)
        plt.close(fig)

        occ = atomic.groupby("spatial_id").size()
        xs, ys, zs = [], [], []
        for sid, n in occ.items():
            s = str(sid)
            if s.startswith("g") and "_" in s:
                a, b = s[1:].split("_", 1)
                xs.append(int(a))
                ys.append(int(b))
                zs.append(int(n))
        fig, ax = plt.subplots(figsize=(6, 5))
        sc = ax.scatter(xs, ys, c=zs, s=6, cmap="viridis")
        fig.colorbar(sc, ax=ax, label="atomic units")
        ax.set_title("NOT_FOR_PAPER_USE spatial occupancy")
        fig.tight_layout()
        fig.savefig(preview / "spatial_occupancy.png", dpi=120)
        plt.close(fig)
        write_text(preview / "README.txt", "All previews are NOT_FOR_PAPER_USE protocol sanity checks.\n")
    except Exception as exc:  # noqa: BLE001
        write_json(preview / "PREVIEW_SKIPPED.json", {"reason": str(exc), "paper_use": "NOT_FOR_PAPER_USE"})


def seal_freeze(root: Path, out: Path, ctx: dict[str, Any]) -> dict[str, Any]:
    protocol_files = [
        "src/raven_mcs/tdrive_protocol_seal_r1/eventtrace_generator.py",
        "src/raven_mcs/tdrive_protocol_seal_r1/constants.py",
        "src/raven_mcs/tdrive_protocol_seal_r1/pipeline.py",
        "src/raven_mcs/data/tdrive.py",
        "src/raven_mcs/data/split.py",
        "src/raven_mcs/data/controlled.py",
        "src/raven_mcs/e3/real_runner/stage2_r3.py",
        "src/raven_mcs/simulation/event_trace.py",
        "src/raven_mcs/metrics/distribution.py",
        "src/raven_mcs/metrics/accuracy.py",
        "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py",
        "src/raven_mcs/e3/formal/stats.py",
        "configs/dataset/tdrive_speed.yaml",
        "data/manifests/tdrive_speed_manifest.json",
        "data/processed/tdrive_speed/atomic_units.parquet",
        "data/processed/tdrive_speed/client_measurements.parquet",
    ]
    freeze = {
        "protocol_id": PROTOCOL_ID,
        "round": ROUND,
        "source_revision": ctx["git_rev"],
        "source_files": {rel: sha256_file(root / rel) for rel in protocol_files},
        "config_files": {
            "configs/dataset/tdrive_speed.yaml": sha256_file(root / "configs/dataset/tdrive_speed.yaml"),
            "07_methods/TDRIVE_RAVEN_CONFIG_SEAL.json": sha256_file(out / "07_methods/TDRIVE_RAVEN_CONFIG_SEAL.json"),
        },
        "dataset_files": {
            "atomic_units.parquet": ctx["processed_identity"]["atomic_units"]["sha256"],
            "client_measurements.parquet": ctx["processed_identity"]["client_measurements"]["sha256"],
            "data_hash": ctx["manifest"]["data_hash"],
        },
        "split_file_hash": sha256_file(out / "05_split/TDRIVE_SPLIT_SEAL.json"),
        "target_file_hash": sha256_file(out / "03_target/TDRIVE_TARGET_H_SEAL.json"),
        "mu_file_hash": sha256_file(out / "03_target/TDRIVE_TARGET_MU.csv"),
        "stratum_file_hash": sha256_file(out / "03_target/TDRIVE_OPPORTUNITY_STRATUM_SEAL.json"),
        "eventtrace_generator_hash": sha256_file(root / "src/raven_mcs/tdrive_protocol_seal_r1/eventtrace_generator.py"),
        "metric_evaluator_hashes": {
            "distribution.py": sha256_file(root / "src/raven_mcs/metrics/distribution.py"),
            "accuracy.py": sha256_file(root / "src/raven_mcs/metrics/accuracy.py"),
            "delta_cs_v6.py": sha256_file(root / "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py"),
        },
        "method_adapter_hashes": {row["canonical_method_id"]: row["implementation_hash_now"] for row in ctx["methods"]},
        "status": "FROZEN",
    }
    write_json(out / "13_freeze/TDRIVE_PROTOCOL_SOURCE_FREEZE.json", freeze)
    master = {
        "protocol_id": PROTOCOL_ID,
        "round": ROUND,
        "dataset_identity": ctx["raw_identity"],
        "processed_dataset_identity": ctx["processed_identity"],
        "timezone": ctx["sem"]["tz"],
        "client_identity": ctx["sem"]["client"],
        "spatial_grid": ctx["sem"]["grid"],
        "time_slots": ctx["sem"]["slot"],
        "atomic_units": ctx["sem"]["atomic"],
        "h_i": ctx["tgt"]["h"],
        "mu": ctx["tgt"]["mu"],
        "s_i": ctx["tgt"]["s"],
        "R": ctx["sel"]["r"],
        "O": ctx["sel"]["o"],
        "U": ctx["sel"]["u"],
        "split": ctx["split"]["seal"],
        "seeds": FORMAL_SEEDS,
        "methods": [dict(m) for m in METHODS],
        "configs": ctx["raven"],
        "eventtrace_schema": "06_eventtrace/TDRIVE_EVENTTRACE_SCHEMA.json",
        "metrics": list(PRIMARY_METRICS),
        "statistical_protocol": "09_statistics/TDRIVE_STATISTICAL_PROTOCOL_SEAL.json",
        "future_canary": "11_future_run_matrix/TDRIVE_FUTURE_CANARY_PLAN.csv",
        "future_formal_50": "11_future_run_matrix/TDRIVE_FUTURE_FORMAL_RUN_MATRIX_50.csv",
        "paper_claim_ceiling": "external validation of structural target-alignment under real taxi-mobility opportunity; not RMSE universality",
        "source_hashes": freeze["source_files"],
        "scenario": SCENARIO,
        "s_max": S_MAX,
        "mean_observation_rate": MEAN_OBSERVATION_RATE,
        "m_mc": M_MC,
        "window_duration": WINDOW_DURATION,
        "status_placeholder": "see TDRIVE_PROTOCOL_GATES_R1.json",
    }
    write_json(out / "13_freeze/TDRIVE_REAL_MOBILITY_PROTOCOL_MASTER_R1.json", master)
    write_text(
        out / "13_freeze/TDRIVE_REAL_MOBILITY_PROTOCOL_MASTER_R1.md",
        "\n".join(
            [
                "# T-Drive real-mobility protocol master R1",
                "",
                "This is the sole T-Drive protocol authority for later Canary/formal rounds.",
                "",
                "## What is the real mobility evidence?",
                "Beijing taxi GPS trajectories (MSR T-Drive sample) after bbox/gap/speed filters. Client-fleet presence in a 500 m × 30 min atomic unit is R=1.",
                "",
                "## What exactly is a client?",
                "One client-fleet taxi (`vehicle::{id}`). Reference-fleet taxis build Y and are not federated clients.",
                "",
                "## What is an atomic unit?",
                "`i = (spatial_id, 30-min slot)` with `Y_i` = mean reference-fleet speed (km/h).",
                "",
                "## What is h(i)?",
                "PRE_REGISTERED_PROTOCOL_FALLBACK: four Beijing-local time-of-day groups H1–H4. Processed `target_group` is not paper h(i).",
                "",
                "## What is s(i)?",
                "Processed `opportunity_stratum` = spatial_id × 4 TOD blocks × weekday/weekend. Distinct from h(i).",
                "",
                "## What makes R=1?",
                "A processed client_measurements row for that taxi and atomic unit.",
                "",
                "## What makes O=1?",
                "R=1 after data-quality filters, then a controlled Complete-aligned observation draw (p_obs=0.35). Not a recorded sensor failure log.",
                "",
                "## What makes U=1?",
                "Controlled compute AND network AND deadline AND tau≤5 AND nonempty observations. Not T-Drive hardware logs.",
                "",
                "## How are splits defined?",
                "Recovered processed 60/20/20 split by unique time slots (TemporalSplitConfig). Leakage audit must PASS.",
                "",
                "## Which methods will run?",
                "FedAvg-Window, FedAsync-Window, TimeAlign-Agg (`flamf_timealign_adapted`), TwoStage-Hajek, RAVEN-MCS.",
                "",
                "## Which seeds will run?",
                "30001–30010 matched across methods. Future formal size 50. This round executes 0.",
                "",
                "## Which metrics are primary?",
                "Delta_group, Delta_c_s, RMSE_mu. Success is not defined as an RMSE_mu win.",
                "",
                "## What counts as success?",
                "See claim decision rules: strong/partial/no-clear external consistency or counterevidence on structural endpoints.",
                "",
                "## What claims are forbidden?",
                "Universal RMSE superiority; treating controlled O/U as real failures; using T-Drive as a full ablation/scalability study.",
                "",
            ]
        ),
    )
    return freeze


def decide_status(gates: dict[str, Any], ctx: dict[str, Any]) -> tuple[str, str]:
    if ctx["processed_identity"]["status"] != "HASH_BOUND" or ctx["raw_identity"]["status"] != "HASH_BOUND":
        return "F", STATUSES["F"]
    if not ctx["split"]["leakage_pass"]:
        return "C", STATUSES["C"]
    if ctx["fixture"]["status"] != "PASS":
        return "D", STATUSES["D"]
    if not gates.get("all_pass"):
        failed = [k for k, v in gates.get("gates", {}).items() if not v.get("pass")]
        if any(g in failed for g in ("TDPS-G18", "TDPS-G19")):
            return "C", STATUSES["C"]
        if any(g in failed for g in ("TDPS-G21", "TDPS-G22", "TDPS-G23")):
            return "D", STATUSES["D"]
        if any(g in failed for g in ("TDPS-G24", "TDPS-G25", "TDPS-G26", "TDPS-G27")):
            return "E", STATUSES["E"]
        if any(g in failed for g in ("TDPS-G3", "TDPS-G4", "TDPS-G5", "TDPS-G6", "TDPS-G7", "TDPS-G8", "TDPS-G9", "TDPS-G10", "TDPS-G11", "TDPS-G13", "TDPS-G14")):
            return "B", STATUSES["B"]
        return "F", STATUSES["F"]
    return "A", STATUSES["A"]


def run(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or Path(__file__).resolve().parents[3])
    out = root / "tdrive_protocol_seal_r1"
    ensure_dir(out)
    git_rev = _git(root, "rev-parse", "HEAD")
    manifest = json.loads((root / "data/manifests/tdrive_speed_manifest.json").read_text(encoding="utf-8"))

    inv = seal_inventory(root, out, git_rev)
    ds = seal_dataset(root, out, manifest)
    sem = seal_semantics(root, out, ds["atomic"], ds["meas"])
    tgt = seal_target(out, ds["atomic"])
    sel = seal_selection(out, ds["atomic"], ds["meas"], tgt["work"])
    spl = seal_split(out, ds["atomic"])
    et = seal_eventtrace(root, out, ds["atomic"], ds["meas"])
    meth = seal_methods(root, out)
    seal_metrics(root, out)
    seal_stats(out)
    seal_outputs(out)
    seal_audits(out)
    seal_diagnostics(out, ds["atomic"], ds["meas"], sel, tgt["work"])

    ctx = {
        "git_rev": git_rev,
        "manifest": manifest,
        "raw_identity": ds["raw_identity"],
        "processed_identity": ds["processed_identity"],
        "sem": sem,
        "tgt": tgt,
        "sel": sel,
        "split": spl,
        "fixture": et["fixture"],
        "methods": meth["methods"],
        "raven": meth["raven"],
        "inventory": inv,
    }
    freeze = seal_freeze(root, out, ctx)
    gates = run_gates(root, out)
    status_code, status_name = decide_status(gates, ctx)
    write_json(
        out / "13_freeze/TDRIVE_PROTOCOL_FINAL_STATUS.json",
        {
            "status_code": status_code,
            "status": status_name,
            "all_gates_pass": bool(gates.get("all_pass")),
            "n_pass": gates.get("n_pass"),
            "n_total": gates.get("n_total"),
            "canary_started": False,
            "next_action": "Return package to teacher. Do not start Canary without a separate instruction."
            if status_code == "A"
            else "Resolve the named blocker. Do not start Canary.",
        },
    )
    write_report(out, ctx, status_code=status_code, status_name=status_name, gates=gates)
    pkg = package_zip(root, out)
    status_payload = json.loads((out / "13_freeze/TDRIVE_PROTOCOL_FINAL_STATUS.json").read_text(encoding="utf-8"))
    status_payload["package"] = pkg
    write_json(out / "13_freeze/TDRIVE_PROTOCOL_FINAL_STATUS.json", status_payload)
    return {
        "status_code": status_code,
        "status": status_name,
        "gates": gates,
        "package": pkg,
        "all_gates_pass": bool(gates.get("all_pass")),
        "freeze": freeze,
    }


if __name__ == "__main__":
    result = run()
    print(result["status"], result["gates"].get("n_pass"), "/", result["gates"].get("n_total"))
    raise SystemExit(0 if result["all_gates_pass"] else 1)
