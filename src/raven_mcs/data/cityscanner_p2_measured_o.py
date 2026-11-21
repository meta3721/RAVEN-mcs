"""NYC Pilot2 measured-O ingest: R = PM∪NO2 GPS cell-slots, Y = PM2.5 when O=1.

Does not overwrite data/processed/cityscanner_nyc_pm25/.
O=0 units are occupancy-only (no invented Y).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.cityscanner import REGION_ORDER, _grid_xy
from raven_mcs.data.controlled import public_time_features, time_of_day_block, weekday_label
from raven_mcs.data.schema import (
    normalize_atomic_units,
    normalize_client_measurements,
    write_processed_parquet,
)
from raven_mcs.data.split import TemporalSplitConfig, assign_temporal_splits
from raven_mcs.utils.serialization import load_json

PM_FILES = (
    "NYC_Pilot2_PM_Part1.csv",
    "NYC_Pilot2_PM_Part2.csv",
    "NYC_Pilot2_PM_Part3.csv",
)
NO2_FILES = (
    "NYC_Pilot2_NO2_Part1.csv",
    "NYC_Pilot2_NO2_Part2.csv",
)
CELL_METERS = 500
SLOT_MINUTES = 30


def _unix_to_utc(time_num: pd.Series) -> pd.Series:
    values = pd.to_numeric(time_num, errors="coerce")
    unit = "ms" if float(np.nanmedian(values.to_numpy(dtype=np.float64))) > 1e12 else "s"
    return pd.to_datetime(values, unit=unit, utc=True, errors="coerce"), unit


def _load_stream(raw_root: Path, files: tuple[str, ...], value_col: str) -> pd.DataFrame:
    frames = []
    n_by_file: dict[str, int] = {}
    for name in files:
        path = raw_root / name
        if not path.is_file():
            raise FileNotFoundError(path)
        header = pd.read_csv(path, nrows=0)
        cols = [c for c in ("time", "latitude", "longitude", value_col, "SensorID") if c in header.columns]
        missing = [c for c in ("time", "latitude", "longitude") if c not in header.columns]
        if missing:
            raise RuntimeError(f"{name} missing {missing}")
        if value_col not in header.columns:
            raise RuntimeError(f"{name} missing {value_col}")
        chunk = pd.read_csv(path, usecols=cols)
        n_by_file[name] = int(len(chunk))
        if "SensorID" not in chunk.columns:
            chunk["SensorID"] = "unknown"
        frames.append(chunk.rename(columns={"SensorID": "sensor_id"}))
    raw = pd.concat(frames, ignore_index=True)
    ts, unit = _unix_to_utc(raw["time"])
    out = pd.DataFrame(
        {
            "sensor_id": raw["sensor_id"].astype(str),
            "absolute_time": ts,
            "latitude": pd.to_numeric(raw["latitude"], errors="coerce"),
            "longitude": pd.to_numeric(raw["longitude"], errors="coerce"),
            "value": pd.to_numeric(raw[value_col], errors="coerce"),
        }
    )
    return out, {"n_by_file": n_by_file, "time_unit": unit, "n_raw": int(len(out))}


def prepare_p2_measured_o(raw_root: Path) -> dict[str, Any]:
    raw_root = Path(raw_root)
    license_path = raw_root / "LICENSE.json"
    if not license_path.is_file():
        raise FileNotFoundError(f"LICENSE.json missing under {raw_root}")
    license_meta = load_json(license_path)
    if str(license_meta.get("license_id") or "").lower() != "cc-by-4.0":
        raise RuntimeError("City Scanner LICENSE.json is not cc-by-4.0")

    pm, pm_meta = _load_stream(raw_root, PM_FILES, "pm25")
    no2, no2_meta = _load_stream(raw_root, NO2_FILES, "no2")

    pm_gps = (
        np.isfinite(pm["latitude"].to_numpy(dtype=np.float64))
        & np.isfinite(pm["longitude"].to_numpy(dtype=np.float64))
        & pm["absolute_time"].notna().to_numpy()
    )
    pm_keep = pm_gps & np.isfinite(pm["value"].to_numpy(dtype=np.float64))
    pm_keep &= (pm["value"].to_numpy(dtype=np.float64) >= 0.0) & (
        pm["value"].to_numpy(dtype=np.float64) <= 1000.0
    )
    no2_gps = (
        np.isfinite(no2["latitude"].to_numpy(dtype=np.float64))
        & np.isfinite(no2["longitude"].to_numpy(dtype=np.float64))
        & no2["absolute_time"].notna().to_numpy()
    )
    pm_y = pm.loc[pm_keep].copy()
    no2_r = no2.loc[no2_gps].copy()
    if pm_y.empty or no2_r.empty:
        raise RuntimeError("Pilot2 measured-O ingest aborted: empty PM-Y or NO2-GPS")

    lon0 = float(min(float(pm_y["longitude"].min()), float(no2_r["longitude"].min())))
    lat0 = float(min(float(pm_y["latitude"].min()), float(no2_r["latitude"].min())))
    lon1 = float(max(float(pm_y["longitude"].max()), float(no2_r["longitude"].max())))
    lat1 = float(max(float(pm_y["latitude"].max()), float(no2_r["latitude"].max())))

    def _assign_cells(df: pd.DataFrame) -> pd.DataFrame:
        gx, gy, spatial = _grid_xy(
            df["longitude"],
            df["latitude"],
            lon0=lon0,
            lat0=lat0,
            lon1=lon1,
            lat1=lat1,
            cell_meters=CELL_METERS,
        )
        out = df.copy()
        out["gx"] = gx
        out["gy"] = gy
        out["spatial_id"] = spatial
        out["slot_time"] = out["absolute_time"].dt.floor(f"{SLOT_MINUTES}min")
        return out

    pm_y = _assign_cells(pm_y)
    no2_r = _assign_cells(no2_r)

    pm_cells = (
        pm_y.groupby(["spatial_id", "gx", "gy", "slot_time"], as_index=False)
        .agg(
            target_value=("value", "mean"),
            support_n=("value", "size"),
            n_sensors=("sensor_id", "nunique"),
        )
    )
    pm_cells["o_observed"] = 1
    no2_keys = no2_r.groupby(["spatial_id", "gx", "gy", "slot_time"], as_index=False).size()
    no2_keys = no2_keys.rename(columns={"size": "support_n_no2_gps"})
    merged = pd.merge(
        no2_keys,
        pm_cells,
        on=["spatial_id", "gx", "gy", "slot_time"],
        how="outer",
    )
    merged["o_observed"] = merged["o_observed"].fillna(0).astype(int)
    merged["support_n"] = merged["support_n"].fillna(0).astype(int)
    merged["support_n_no2_gps"] = merged["support_n_no2_gps"].fillna(0).astype(int)
    merged["n_sensors"] = merged["n_sensors"].fillna(0).astype(int)
    n_union = int(len(merged))
    n_o0 = int((merged["o_observed"] == 0).sum())
    o0_frac = n_o0 / max(n_union, 1)
    if o0_frac < 0.02:
        raise RuntimeError(
            f"measured O=0 fraction {o0_frac:.6f} < 0.02; do not Bernoulli-substitute"
        )
    n_cells = int(merged["spatial_id"].nunique())
    n_slots = int(merged["slot_time"].nunique())
    if n_cells < 20:
        raise RuntimeError(f"unique occupied cells={n_cells} < 20")
    if n_slots < 120:
        raise RuntimeError(f"unique occupied 30min slots={n_slots} < 120")

    cells = merged.drop_duplicates("spatial_id")[["spatial_id", "gx", "gy"]]
    mx = float(cells["gx"].median())
    my = float(cells["gy"].median())
    region_map = {
        str(r.spatial_id): "region%d" % ((int(r.gx >= mx) << 1) + int(r.gy >= my))
        for r in cells.itertuples(index=False)
    }

    occ_rows: list[dict[str, object]] = []
    for record in merged.itertuples(index=False):
        spatial_id = str(record.spatial_id)
        region = region_map[spatial_id]
        absolute_time = pd.Timestamp(record.slot_time)
        if absolute_time.tzinfo is None:
            absolute_time = absolute_time.tz_localize("UTC")
        else:
            absolute_time = absolute_time.tz_convert("UTC")
        block = time_of_day_block(absolute_time)
        occ_rows.append(
            {
                "spatial_id": spatial_id,
                "absolute_time": absolute_time,
                "target_value": (
                    float(record.target_value) if int(record.o_observed) == 1 else 0.0
                ),
                "o_observed": int(record.o_observed),
                "target_group": region,
                "opportunity_stratum": (
                    f"{region}::block{block}::{weekday_label(absolute_time)}"
                ),
                "public_features": {
                    **public_time_features(absolute_time),
                    "support_n": int(record.support_n),
                    "support_n_no2_gps": int(record.support_n_no2_gps),
                    "n_sensors_audit_only": int(record.n_sensors),
                    "gx": int(record.gx),
                    "gy": int(record.gy),
                    "cell_meters": CELL_METERS,
                    "slot_minutes": SLOT_MINUTES,
                    "o_observed": int(record.o_observed),
                },
                "support_flag": True,
            }
        )
    occ = assign_temporal_splits(pd.DataFrame(occ_rows), config=TemporalSplitConfig())
    occ["unit_id"] = (
        occ["spatial_id"].astype(str)
        + "_t"
        + occ["time_index"].astype(int).map(lambda i: f"{i:05d}")
    )
    n_strata = int(occ["opportunity_stratum"].nunique())
    if n_strata > 32:
        raise RuntimeError(f"opportunity strata={n_strata} > 32")
    test = occ.loc[occ["split"].astype(str) == "test"]
    test_regions = set(test["target_group"].astype(str))
    missing_test = [r for r in REGION_ORDER if r not in test_regions]
    if missing_test:
        raise RuntimeError(f"test split missing region(s) {missing_test}")

    labeled = occ.loc[occ["o_observed"].astype(int) == 1].copy()
    labeled = labeled.drop(columns=["o_observed"])
    atomic = normalize_atomic_units(labeled)
    clients = normalize_client_measurements(
        pd.DataFrame(
            {
                "client_id": atomic["spatial_id"].astype(str),
                "unit_id": atomic["unit_id"].astype(str),
                "potential_measurement": atomic["target_value"].astype(float),
                "controlled_generator_parameters": None,
                "split": atomic["split"].astype(str),
                "source_trace_id": (
                    "cityscanner_p2_mo::cell::"
                    + atomic["spatial_id"].astype(str)
                    + "::"
                    + atomic["unit_id"].astype(str)
                ),
            }
        )
    )
    if clients["client_id"].astype(str).str.startswith("NYCP").any():
        raise RuntimeError("vehicle/SensorID used as FL client")
    occupancy = occ[
        [
            "unit_id",
            "spatial_id",
            "absolute_time",
            "time_index",
            "split",
            "target_group",
            "opportunity_stratum",
            "o_observed",
        ]
    ].copy()
    occupancy["unit_id"] = occupancy["unit_id"].astype(str)
    occupancy["spatial_id"] = occupancy["spatial_id"].astype(str)
    occupancy["client_id"] = occupancy["spatial_id"]
    if occupancy["spatial_id"].str.startswith("NYCP").any():
        raise RuntimeError("vehicle/SensorID leaked into spatial_id")

    sensors = pd.concat([pm_y["sensor_id"], no2_r["sensor_id"]], ignore_index=True)
    audit = {
        "pm_meta": pm_meta,
        "no2_meta": no2_meta,
        "n_union_cell_slots": n_union,
        "n_o0_cell_slots": n_o0,
        "measured_o0_fraction": float(o0_frac),
        "n_occupied_cells": n_cells,
        "n_occupied_slots": n_slots,
        "n_atomic_o1": int(len(atomic)),
        "n_occupancy": int(len(occupancy)),
        "n_opportunity_strata": n_strata,
        "grid_origin_lon": lon0,
        "grid_origin_lat": lat0,
        "grid_max_lon": lon1,
        "grid_max_lat": lat1,
        "median_gx": mx,
        "median_gy": my,
        "used_y_for_h": False,
        "clients_are_spatial_id": True,
        "vehicles_are_fl_clients": False,
        "n_unique_sensor_ids_audit_only": int(sensors.nunique()),
        "p_obs_bernoulli": False,
    }
    return {
        "atomic": atomic,
        "clients": clients,
        "occupancy": occupancy,
        "audit": audit,
    }


def write_p2_measured_o(raw_root: Path, processed_dir: Path) -> dict[str, Any]:
    payload = prepare_p2_measured_o(raw_root)
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    write_processed_parquet(payload["atomic"], payload["clients"], processed_dir)
    occ_path = processed_dir / "occupancy_units.parquet"
    payload["occupancy"].to_parquet(occ_path, index=False)
    return payload
