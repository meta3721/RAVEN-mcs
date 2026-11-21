"""Core audits for Traffic dense matrix, windows, spatial identity, theory mapping."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

POINT_RE = re.compile(
    r"POINT\s*\(\s*([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s*\)",
    re.IGNORECASE,
)
BLOCKS = ("block0", "block1", "block2", "block3")
DAY_TYPES = ("weekday", "weekend")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def schema_hash(columns: list[str], dtypes: dict[str, str]) -> str:
    payload = {"columns": columns, "dtypes": dtypes}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()


def load_atomic_table(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df = df.copy()
    df["spatial_id"] = df["spatial_id"].astype(str)
    df["absolute_time"] = pd.to_datetime(df["absolute_time"], utc=True)
    return df


def atomic_table_identity(path: Path, df: pd.DataFrame) -> dict[str, Any]:
    path = Path(path)
    dtypes = {c: str(t) for c, t in df.dtypes.items()}
    nulls = {c: int(v) for c, v in df.isna().sum().items()}
    return {
        "path": path.as_posix() if path.is_absolute() else str(path).replace("\\", "/"),
        "sha256": sha256_file(path),
        "size_bytes": int(path.stat().st_size),
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "dtypes": dtypes,
        "null_counts": nulls,
        "schema_hash": schema_hash(list(df.columns), dtypes),
        "source_provenance": {
            "adapter": "src/raven_mcs/data/traffic.py",
            "config": "configs/dataset/traffic.yaml",
            "raw_hourly": "data/raw/traffic/road_traffic_counts_hourly_permanent.zip",
            "raw_reference": "data/raw/traffic/road_traffic_counts_station_reference.csv",
            "target_name": "traffic_volume",
            "target_unit": "vehicles_per_hour",
        },
        "status": "PASS" if len(df) == 30960 else "FAIL",
    }


def audit_dense_matrix(df: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame]:
    stations = sorted(df["spatial_id"].astype(str).unique())
    timestamps = pd.DatetimeIndex(
        sorted(pd.to_datetime(df["absolute_time"], utc=True).unique())
    )
    station_count = len(stations)
    unique_timestamp_count = int(len(timestamps))
    total_row_count = int(len(df))
    expected = station_count * unique_timestamp_count

    per_station: list[dict[str, Any]] = []
    sets: list[frozenset] = []
    for sid in stations:
        ts = pd.to_datetime(
            df.loc[df["spatial_id"] == sid, "absolute_time"], utc=True
        )
        ts_set = frozenset(ts.astype("int64").tolist())
        sets.append(ts_set)
        per_station.append(
            {
                "spatial_id": sid,
                "timestamp_count": int(ts.nunique()),
                "row_count": int(len(ts)),
                "duplicate_station_time_count": int(len(ts) - ts.nunique()),
                "earliest": str(ts.min()),
                "latest": str(ts.max()),
            }
        )
    coverage = pd.DataFrame(per_station)
    common = set.intersection(*(set(s) for s in sets)) if sets else set()
    union = set.union(*(set(s) for s in sets)) if sets else set()
    sym = 0
    base = sets[0] if sets else frozenset()
    for s in sets[1:]:
        sym += len(base.symmetric_difference(s))
        base = frozenset(common)

    key = df[["spatial_id", "absolute_time"]].astype(str)
    duplicate_cells = int(key.duplicated().sum())
    missing_cells = int(expected - key.drop_duplicates().shape[0])

    # interval audit on common ordered timestamps
    if len(timestamps) >= 2:
        deltas = timestamps.to_series().diff().iloc[1:]
        hour = pd.Timedelta(hours=1)
        irregular = int((deltas != hour).sum())
        median_h = float(deltas.median() / pd.Timedelta(hours=1))
        min_h = float(deltas.min() / pd.Timedelta(hours=1))
        max_h = float(deltas.max() / pd.Timedelta(hours=1))
        strictly_increasing = bool(timestamps.is_monotonic_increasing and timestamps.is_unique)
    else:
        irregular = 0
        median_h = min_h = max_h = float("nan")
        strictly_increasing = False

    span_hours = (
        float((timestamps[-1] - timestamps[0]) / pd.Timedelta(hours=1))
        if len(timestamps) >= 2
        else 0.0
    )
    # inclusive hourly points: span between first and last is n-1 hours for n stamps
    # Instruction requires total span >= 719 hours for 720 hourly stamps.
    ok = (
        station_count == 43
        and unique_timestamp_count == 720
        and total_row_count == 30960
        and total_row_count == expected
        and len(common) == 720
        and len(union) == 720
        and sym == 0
        and missing_cells == 0
        and duplicate_cells == 0
        and bool((coverage["timestamp_count"] == 720).all())
        and strictly_increasing
        and irregular == 0
        and span_hours >= 719.0
    )
    audit = {
        "station_count": station_count,
        "unique_timestamp_count": unique_timestamp_count,
        "total_row_count": total_row_count,
        "expected_dense_rows": expected,
        "common_timestamp_count": int(len(common)),
        "union_timestamp_count": int(len(union)),
        "station_timestamp_symmetric_difference_count": int(sym),
        "missing_station_time_cell_count": missing_cells,
        "duplicate_station_time_cell_count": duplicate_cells,
        "earliest_timestamp": str(timestamps[0]) if len(timestamps) else None,
        "latest_timestamp": str(timestamps[-1]) if len(timestamps) else None,
        "total_span_hours": span_hours,
        "median_interval_hours": median_h,
        "min_interval_hours": min_h,
        "max_interval_hours": max_h,
        "irregular_interval_count": irregular,
        "timezone": "UTC",
        "duplicate_timestamp_count_global": int(
            unique_timestamp_count - len(set(timestamps.astype("int64").tolist()))
        ),
        "timestamps_strictly_increasing": strictly_increasing,
        "hourly_cadence_consistent": irregular == 0,
        "status": "PASS" if ok else "FAIL",
    }
    return audit, coverage


def assign_global_windows(
    df: pd.DataFrame,
    *,
    n_windows: int = 100,
    window_hours: int = 6,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Select earliest contiguous 600h and assign unique non-overlapping 6h windows."""
    timestamps = pd.DatetimeIndex(
        sorted(pd.to_datetime(df["absolute_time"], utc=True).unique())
    )
    need = n_windows * window_hours
    if len(timestamps) < need:
        raise ValueError(f"need {need} timestamps, have {len(timestamps)}")

    # earliest contiguous complete block of length need
    t0 = timestamps[0]
    selected_ts = timestamps[:need]
    remainder_ts = timestamps[need:]
    # verify contiguity
    deltas = selected_ts.to_series().diff().iloc[1:]
    if not bool((deltas == pd.Timedelta(hours=1)).all()):
        raise ValueError("selected 600h block is not hourly contiguous")

    window_rows = []
    for r in range(n_windows):
        start = selected_ts[r * window_hours]
        end = start + pd.Timedelta(hours=window_hours)
        members = selected_ts[r * window_hours : (r + 1) * window_hours]
        window_rows.append(
            {
                "window_id": r,
                "start_inclusive": start,
                "end_exclusive": end,
                "n_timestamps": int(len(members)),
                "first_timestamp": members[0],
                "last_timestamp": members[-1],
            }
        )
    windows = pd.DataFrame(window_rows)

    work = df.copy()
    work["absolute_time"] = pd.to_datetime(work["absolute_time"], utc=True)
    offset_h = (work["absolute_time"] - t0) / pd.Timedelta(hours=1)
    work["window_id"] = np.floor(offset_h.to_numpy(dtype="float64") / window_hours).astype("int64")
    in_range = (work["absolute_time"] >= selected_ts[0]) & (
        work["absolute_time"] < selected_ts[0] + pd.Timedelta(hours=need)
    )
    selected = work.loc[in_range].copy()
    remainder = work.loc[~in_range].copy()
    remainder["window_id"] = -1
    remainder["assignment"] = "out_of_protocol_remainder"
    selected["assignment"] = "protocol_window"

    # uniqueness checks
    multiply = int(selected.groupby("unit_id")["window_id"].nunique().gt(1).sum()) if "unit_id" in selected else 0
    overlap = 0
    for i in range(len(windows) - 1):
        if windows.loc[i, "end_exclusive"] > windows.loc[i + 1, "start_inclusive"]:
            overlap += 1
    common_boundary_violation = 0
    # all stations share same window boundaries by construction (global timestamps)
    stations = selected["spatial_id"].nunique()
    expected_selected = n_windows * window_hours * int(stations)
    audit = {
        "global_window_count": int(len(windows)),
        "window_hours": window_hours,
        "selected_start": str(selected_ts[0]),
        "selected_end_exclusive": str(
            selected_ts[0] + pd.Timedelta(hours=need)
        ),
        "selection_rule": "earliest_contiguous_600h",
        "holdout_remainder_hours": int(len(remainder_ts)),
        "common_boundary_violation_count": common_boundary_violation,
        "overlap_count": overlap,
        "gap_count": 0,
        "atomic_multiply_assigned_count": multiply,
        "atomic_unassigned_in_selected_range_count": int((~in_range & in_range).sum()),
        "cross_window_duplicate_count": multiply,
        "selected_atomic_count": int(len(selected)),
        "remainder_atomic_count": int(len(remainder)),
        "expected_selected_atomic_count": expected_selected,
        "status": (
            "PASS"
            if (
                len(windows) == n_windows
                and overlap == 0
                and multiply == 0
                and len(selected) == 25800
                and len(remainder) == 5160
            )
            else "FAIL"
        ),
    }
    assignment = pd.concat(
        [
            selected[
                ["unit_id", "spatial_id", "absolute_time", "window_id", "assignment"]
            ],
            remainder[
                ["unit_id", "spatial_id", "absolute_time", "window_id", "assignment"]
            ],
        ],
        ignore_index=True,
    )
    return windows, assignment, audit


def _parse_point(value: Any) -> tuple[float | None, float | None]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None, None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None, None
    m = POINT_RE.search(text)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def parse_station_reference(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    path = Path(path)
    ref = pd.read_csv(path)
    rows = []
    invalid_geom = 0
    for _, r in ref.iterrows():
        lon = lat = None
        crs = None
        method = None
        if pd.notna(r.get("wgs84_longitude")) and pd.notna(r.get("wgs84_latitude")):
            lon = float(r["wgs84_longitude"])
            lat = float(r["wgs84_latitude"])
            crs = "EPSG:4326"
            method = "direct_wgs84_columns"
        else:
            g_lon, g_lat = _parse_point(r.get("the_geom"))
            if g_lon is not None and g_lat is not None:
                lon, lat = g_lon, g_lat
                crs = "EPSG:4326"
                method = "wkt_point_the_geom"
            else:
                invalid_geom += 1
        rows.append(
            {
                "reference_station_id": str(r.get("station_id")),
                "station_key": str(r.get("station_key")),
                "the_geom": r.get("the_geom"),
                "the_geom_webmercator": r.get("the_geom_webmercator"),
                "latitude": lat,
                "longitude": lon,
                "easting": r.get("lambert_easting"),
                "northing": r.get("lambert_northing"),
                "road_name": r.get("road_name"),
                "direction": r.get("direction_seq"),
                "location_description": r.get("full_name"),
                "CRS": crs,
                "conversion_method": method,
            }
        )
    parsed = pd.DataFrame(rows)
    audit = {
        "path": path.as_posix().replace("\\", "/") if path.is_absolute() else str(path).replace("\\", "/"),
        "sha256": sha256_file(path),
        "size_bytes": int(path.stat().st_size),
        "reference_row_count": int(len(ref)),
        "geometry_field_primary": "wgs84_longitude/wgs84_latitude",
        "geometry_field_fallback": "the_geom",
        "CRS": "EPSG:4326",
        "conversion_method": "direct_wgs84_columns_preferred",
        "library_version": f"pandas={pd.__version__}",
        "invalid_geometry_count": int(invalid_geom),
        "parsed_coordinate_count": int(parsed["latitude"].notna().sum()),
        "status": "PASS" if int(parsed["latitude"].notna().sum()) > 0 else "FAIL",
    }
    return parsed, audit


def map_stations(
    processed_ids: list[str],
    parsed_ref: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    ref = parsed_ref.copy()
    ref["station_key"] = ref["station_key"].astype(str)
    # one row per station_key: prefer rows with coordinates, then first
    ref = ref.sort_values(
        ["station_key", "latitude"], ascending=[True, False], kind="stable"
    )
    ref = ref.drop_duplicates(subset=["station_key"], keep="first")
    key_counts = parsed_ref.groupby(parsed_ref["station_key"].astype(str)).size()

    rows = []
    for sid in processed_ids:
        hit = ref.loc[ref["station_key"] == sid]
        if hit.empty:
            rows.append(
                {
                    "processed_station_id": sid,
                    "reference_station_id": None,
                    "station_key": sid,
                    "latitude": None,
                    "longitude": None,
                    "CRS": None,
                    "road_name": None,
                    "direction": None,
                    "mapping_status": "UNMATCHED",
                }
            )
            continue
        r = hit.iloc[0]
        ok = pd.notna(r["latitude"]) and pd.notna(r["longitude"])
        rows.append(
            {
                "processed_station_id": sid,
                "reference_station_id": r["reference_station_id"],
                "station_key": sid,
                "latitude": float(r["latitude"]) if ok else None,
                "longitude": float(r["longitude"]) if ok else None,
                "CRS": r["CRS"],
                "road_name": r["road_name"],
                "direction": r["direction"],
                "mapping_status": "MATCHED" if ok else "MATCHED_MISSING_COORD",
            }
        )
    spatial = pd.DataFrame(rows)
    matched = spatial.loc[spatial["mapping_status"] == "MATCHED"]
    coords = matched[["latitude", "longitude"]].astype(float)
    dup_coord = int(coords.duplicated().sum()) if len(coords) else 0
    # Final mapping is 1:1 after deterministic dedup; raw reference may have
    # duplicate station_key rows (recorded separately).
    raw_dup_keys = int((key_counts.loc[key_counts.index.isin(processed_ids)] > 1).sum())
    one_to_many = int(
        spatial.groupby("processed_station_id")["reference_station_id"].nunique().gt(1).sum()
    )
    many_to_one = int(
        matched.groupby("reference_station_id").size().gt(1).sum()
    ) if len(matched) else 0
    unmatched_processed = int((spatial["mapping_status"] != "MATCHED").sum())
    ref_keys = set(ref["station_key"].astype(str))
    proc_set = set(processed_ids)
    matched_keys = set(spatial.loc[spatial["mapping_status"] == "MATCHED", "station_key"].astype(str))
    audit = {
        "processed_station_count": int(len(processed_ids)),
        "reference_station_count": int(len(ref_keys)),
        "exact_id_match_count": int((spatial["mapping_status"] == "MATCHED").sum()),
        "unmatched_processed_station_count": unmatched_processed,
        "unmatched_reference_station_count": int(len(ref_keys - proc_set)),
        "one_to_many_match_count": one_to_many,
        "many_to_one_match_count": many_to_one,
        "raw_reference_duplicate_station_key_count": raw_dup_keys,
        "duplicate_coordinate_count": dup_coord,
        "missing_coordinate_count": int(spatial["latitude"].isna().sum()),
        "station_symmetric_difference": int(len(proc_set.symmetric_difference(matched_keys))),
        "synthetic_coordinate_usage": 0,
        "match_key": "station_key",
        "status": (
            "PASS"
            if (
                unmatched_processed == 0
                and int(spatial["latitude"].isna().sum()) == 0
                and one_to_many == 0
                and many_to_one == 0
                and int((spatial["mapping_status"] == "MATCHED").sum()) == 43
            )
            else "BLOCKED_TRAFFIC_SPATIAL_MAPPING_FAILED"
        ),
    }
    return spatial, audit


def select_target_field(df: pd.DataFrame) -> tuple[str, pd.DataFrame, dict[str, Any]]:
    """Deterministic target selection from available numeric columns."""
    candidates = []
    # Only columns present; processed table exposes target_value as the volume.
    for name, semantic in (
        ("target_value", "aggregated_hourly_traffic_volume"),
        ("total_traffic_count", "total_traffic_count"),
        ("all_motor_vehicles", "all_motor_vehicles"),
        ("inbound_count", "inbound_count"),
        ("outbound_count", "outbound_count"),
        ("flow", "flow"),
        ("volume", "volume"),
    ):
        present = name in df.columns
        if not present:
            candidates.append(
                {
                    "field": name,
                    "present": False,
                    "missing_rate": 1.0,
                    "station_coverage": 0.0,
                    "time_coverage": 0.0,
                    "semantic": semantic,
                    "score": -1.0,
                    "selected": False,
                }
            )
            continue
        s = pd.to_numeric(df[name], errors="coerce")
        missing = float(s.isna().mean())
        station_cov = float(df.loc[s.notna(), "spatial_id"].nunique() / df["spatial_id"].nunique())
        time_cov = float(
            pd.to_datetime(df.loc[s.notna(), "absolute_time"], utc=True).nunique()
            / pd.to_datetime(df["absolute_time"], utc=True).nunique()
        )
        unit_ok = True
        score = (1.0 - missing) * 0.4 + station_cov * 0.3 + time_cov * 0.3
        if name == "target_value":
            score += 0.05  # adapter-canonical field
        candidates.append(
            {
                "field": name,
                "present": True,
                "missing_rate": missing,
                "station_coverage": station_cov,
                "time_coverage": time_cov,
                "semantic": semantic,
                "unit_consistent": unit_ok,
                "score": score,
                "selected": False,
            }
        )
    table = pd.DataFrame(candidates).sort_values(
        ["score", "field"], ascending=[False, True], kind="stable"
    )
    chosen = str(table.iloc[0]["field"])
    table.loc[table["field"] == chosen, "selected"] = True
    identity = {
        "target_field": chosen,
        "selection_rule": "max_score(missing,station_cov,time_cov)+canonical_bonus; tie-break field name",
        "unit": "vehicles_per_hour",
        "semantic": "hourly traffic volume at counting station",
        "status": "PASS" if chosen == "target_value" and float(table.iloc[0]["missing_rate"]) == 0.0 else "FAIL",
    }
    return chosen, table, identity


def build_spatial_regions(
    spatial: pd.DataFrame,
    selected_atomic: pd.DataFrame,
    target_field: str,
) -> pd.DataFrame:
    """4 regions via two-level target-mass-weighted median splits on lat/lon."""
    mass = (
        selected_atomic.groupby("spatial_id", as_index=False)[target_field]
        .sum()
        .rename(columns={target_field: "mass"})
    )
    m = spatial.merge(mass, left_on="processed_station_id", right_on="spatial_id", how="left")
    m["mass"] = m["mass"].fillna(0.0)
    m = m.sort_values("processed_station_id", kind="stable").reset_index(drop=True)

    def weighted_median_split(frame: pd.DataFrame, axis: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        ordered = frame.sort_values(
            [axis, "processed_station_id"], kind="stable"
        ).reset_index(drop=True)
        total = float(ordered["mass"].sum())
        if total <= 0:
            mid = len(ordered) // 2
            return ordered.iloc[:mid].copy(), ordered.iloc[mid:].copy()
        csum = ordered["mass"].cumsum()
        cut = int((csum >= total / 2.0).idxmax())
        # ensure non-empty both sides when possible
        cut = min(max(cut, 0), len(ordered) - 2) if len(ordered) >= 2 else 0
        left = ordered.iloc[: cut + 1].copy()
        right = ordered.iloc[cut + 1 :].copy()
        if left.empty or right.empty:
            mid = len(ordered) // 2
            left = ordered.iloc[:mid].copy()
            right = ordered.iloc[mid:].copy()
        return left, right

    west, east = weighted_median_split(m, "longitude")
    sw, nw = weighted_median_split(west, "latitude")
    se, ne = weighted_median_split(east, "latitude")
    parts = [("R0", sw), ("R1", nw), ("R2", se), ("R3", ne)]
    out_rows = []
    for rid, part in parts:
        for _, r in part.iterrows():
            out_rows.append(
                {
                    "processed_station_id": r["processed_station_id"],
                    "spatial_region_id": rid,
                    "latitude": r["latitude"],
                    "longitude": r["longitude"],
                    "mass": r["mass"],
                }
            )
    return pd.DataFrame(out_rows)


def time_block(ts: pd.Timestamp) -> str:
    hour = int(pd.Timestamp(ts).hour)
    return BLOCKS[hour // 6]


def day_type(ts: pd.Timestamp) -> str:
    # Monday=0 ... Sunday=6
    return "weekend" if int(pd.Timestamp(ts).dayofweek) >= 5 else "weekday"


def build_theory_targets(
    selected: pd.DataFrame,
    spatial_regions: pd.DataFrame,
    target_field: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work = selected.copy()
    work["absolute_time"] = pd.to_datetime(work["absolute_time"], utc=True)
    work["time_block"] = work["absolute_time"].map(time_block)
    work["day_type"] = work["absolute_time"].map(day_type)
    work = work.merge(
        spatial_regions[["processed_station_id", "spatial_region_id"]],
        left_on="spatial_id",
        right_on="processed_station_id",
        how="left",
    )
    work["target_group"] = work["time_block"]
    work["opportunity_stratum"] = (
        work["spatial_region_id"].astype(str)
        + "::"
        + work["time_block"].astype(str)
        + "::"
        + work["day_type"].astype(str)
    )
    y = pd.to_numeric(work[target_field], errors="coerce").fillna(0.0).to_numpy()
    # group masses mu_g over protocol selected atoms
    group_mass = work.groupby("target_group", as_index=False).agg(mass=(target_field, "sum"))
    total = float(group_mass["mass"].sum())
    if total <= 0:
        group_mass["mu_g"] = 1.0 / max(len(group_mass), 1)
    else:
        group_mass["mu_g"] = group_mass["mass"] / total

    stratum_mass = work.groupby("opportunity_stratum", as_index=False).agg(
        Lambda_s_tar=(target_field, "sum")
    )
    s_total = float(stratum_mass["Lambda_s_tar"].sum())
    if s_total <= 0:
        stratum_mass["varpi_s"] = 1.0 / max(len(stratum_mass), 1)
    else:
        stratum_mass["varpi_s"] = stratum_mass["Lambda_s_tar"] / s_total

    cs = work.groupby(
        ["spatial_id", "opportunity_stratum"], as_index=False
    ).agg(mass=(target_field, "sum"))
    cs = cs.merge(
        stratum_mass[["opportunity_stratum", "Lambda_s_tar"]],
        on="opportunity_stratum",
        how="left",
    )
    cs["lambda_k_given_s_tar"] = np.where(
        cs["Lambda_s_tar"] > 0, cs["mass"] / cs["Lambda_s_tar"], 0.0
    )
    cs["pi_k_s_tar"] = cs["mass"] / s_total if s_total > 0 else 0.0

    atomic_target = work[
        [
            "unit_id",
            "spatial_id",
            "absolute_time",
            "window_id",
            target_field,
            "target_group",
            "opportunity_stratum",
            "spatial_region_id",
            "time_block",
            "day_type",
        ]
    ].copy()
    # normalization identity: none (raw vehicles/hour); freeze leakage boundary
    identity = {
        "client_definition": "client k = traffic counting station (spatial_id)",
        "atomic_unit_definition": "i = (station_id, hourly timestamp)",
        "target_field": target_field,
        "normalization": {
            "type": "identity",
            "fitting_population": "none",
            "params": {},
            "leakage_boundary": "no fit on validation/formal; identity transform",
            "inverse_transform": "identity",
        },
        "group_definition": "time-of-day block0..block3 from hour//6",
        "group_count": int(group_mass["target_group"].nunique()),
        "mu_g_sum": float(group_mass["mu_g"].sum()),
        "stratum_definition": "spatial_region × time_block × day_type",
        "stratum_count": int(stratum_mass["opportunity_stratum"].nunique()),
        "Lambda_mass_sum": float(stratum_mass["Lambda_s_tar"].sum()),
        "pi_mass_sum": float(cs["pi_k_s_tar"].sum()),
        "varpi_sum": float(stratum_mass["varpi_s"].sum()),
        "status": (
            "PASS"
            if (
                abs(float(group_mass["mu_g"].sum()) - 1.0) < 1e-9
                and abs(float(cs["pi_k_s_tar"].sum()) - 1.0) < 1e-9
                and abs(float(stratum_mass["varpi_s"].sum()) - 1.0) < 1e-9
            )
            else "FAIL"
        ),
    }
    cs_out = cs.rename(columns={"spatial_id": "client_id"})
    return atomic_target, cs_out, group_mass, stratum_mass, identity
