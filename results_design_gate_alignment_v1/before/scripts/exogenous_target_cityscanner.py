"""Exogenous target map for the City Scanner block — execution of the preregistered protocol.

Protocol: ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md
(sha256 7773296BA4718866..., frozen before any rho_r computation; §10 records the
manual landing of the frozen sources).

Stages
  --grid-only   grid-alignment check + frozen key universe + control row (no external data)
  --build       everything above, plus M1 (ACS 2021 B01003 block-group population,
                area-weighted apportionment onto the 446 stored 500 m cells) and
                M2 (NYC 311 counts, 2020-01-01..2022-01-01 local, converted to UTC),
                then the three rows of MAP_SUMMARY.csv.

Read-only with respect to the repository: writes only results_exogenous_target/round_v1/.
No training, no manuscript edits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import sys
import zipfile
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402

RAW = ROOT / "data/raw/cityscanner_nyc_pm25"
LANDING = ROOT / "data/raw/exogenous_target"
PROCESSED = ROOT / "data/processed/cityscanner_nyc_pm25/atomic_units.parquet"
TRACES = ROOT / "artifacts/e3_c1_cityscanner_eventtraces_v1/cityscanner_nyc_pm25"
RUNS = ROOT / "results_c1_cityscanner/round_v1/runs/cityscanner_nyc_pm25"
OUT = ROOT / "results_exogenous_target/round_v1"
EXTRACT = OUT / "extracted"

CELL_KM = 0.5
EARTH_KM_PER_DEG_LAT = 111.32
REGION_ORDER = ("region0", "region1", "region2", "region3")
BLOCKS = (0, 1, 2, 3)
LABELS = ("weekday", "weekend")
COUNTIES = ("36005", "36047", "36061", "36081", "36085")
PM_FILES = ("NYC_Pilot1_PM.csv", "NYC_Pilot2_PM_Part1.csv",
            "NYC_Pilot2_PM_Part2.csv", "NYC_Pilot2_PM_Part3.csv")
ACS_FILES = tuple(f"acs2021_b01003_bg_{c}.json" for c in COUNTIES)
TIGER_ZIPS = tuple(f"tl_2021_{c}_bg.zip" for c in COUNTIES)
NYC311 = "nyc311_2020_2021.csv"


# --------------------------------------------------------------------------- helpers
def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_points() -> pd.DataFrame:
    frames = []
    for name in PM_FILES:
        d = pd.read_csv(RAW / name, usecols=["time", "latitude", "longitude", "pm25"])
        t = pd.to_datetime(pd.to_numeric(d["time"], errors="coerce"), unit="s", utc=True,
                           errors="coerce")
        lat = pd.to_numeric(d["latitude"], errors="coerce")
        lon = pd.to_numeric(d["longitude"], errors="coerce")
        pm = pd.to_numeric(d["pm25"], errors="coerce")
        keep = np.isfinite(lat) & np.isfinite(lon) & t.notna() & np.isfinite(pm) & (pm >= 0) & (pm <= 1000)
        frames.append(pd.DataFrame({"time": t[keep], "lat": lat[keep], "lon": lon[keep]}))
    return pd.concat(frames, ignore_index=True)


def grid_origin(points: pd.DataFrame) -> dict:
    lon0, lat0 = float(points["lon"].min()), float(points["lat"].min())
    lon1, lat1 = float(points["lon"].max()), float(points["lat"].max())
    lat_deg = CELL_KM / EARTH_KM_PER_DEG_LAT
    mid_lat = 0.5 * (lat0 + lat1)
    lon_deg = CELL_KM / (EARTH_KM_PER_DEG_LAT * max(0.2, math.cos(math.radians(mid_lat))))
    return {"lon0": lon0, "lat0": lat0, "lon1": lon1, "lat1": lat1,
            "lon_deg": lon_deg, "lat_deg": lat_deg, "n_points_kept": int(len(points))}


def to_grid_units(lon, lat, origin: dict):
    """Frozen transform: x,y in 500 m cell units relative to the frozen origin."""
    x = (np.asarray(lon, dtype=float) - origin["lon0"]) / origin["lon_deg"]
    y = (np.asarray(lat, dtype=float) - origin["lat0"]) / origin["lat_deg"]
    return x, y


def alignment(points: pd.DataFrame, origin: dict, stored: pd.DataFrame) -> dict:
    x, y = to_grid_units(points["lon"].to_numpy(), points["lat"].to_numpy(), origin)
    gx, gy = np.floor(x).astype(int), np.floor(y).astype(int)
    recomputed = {f"g{a:04d}_{b:04d}" for a, b in zip(gx, gy)}
    stored_cells = set(stored["spatial_id"].astype(str))
    stored_xy = {f"g{int(a):04d}_{int(b):04d}" for a, b in zip(stored["gx"], stored["gy"])}
    return {"n_cells_recomputed": len(recomputed), "n_cells_stored": len(stored_cells),
            "cells_equal": recomputed == stored_cells,
            "cells_missing_from_recompute": sorted(stored_cells - recomputed)[:10],
            "cells_extra_in_recompute": sorted(recomputed - stored_cells)[:10],
            "stored_xy_matches_spatial_id": stored_xy == stored_cells,
            "bbox": {"lon_min": origin["lon0"], "lon_max": origin["lon1"],
                     "lat_min": origin["lat0"], "lat_max": origin["lat1"]}}


def key_universe(atomic: pd.DataFrame) -> pd.DataFrame:
    cells = (atomic.assign(spatial_id=atomic["spatial_id"].astype(str))
             .groupby("spatial_id")["target_group"].first().reset_index())
    rows = []
    for cell, region in zip(cells["spatial_id"], cells["target_group"].astype(str)):
        for b in BLOCKS:
            for lab in LABELS:
                rows.append({"client_id": cell, "opportunity_stratum": f"{region}::block{b}::{lab}",
                             "region": region, "block": b, "weekday_label": lab})
    return pd.DataFrame(rows)


def control_map(atomic: pd.DataFrame, split: str = "test") -> pd.DataFrame:
    frame = atomic.copy()
    frame["target_group_main"] = frame["target_group"].astype(str)
    mapping = {str(s): str(s) for s in frame["spatial_id"].astype(str).unique()}
    return build_pi_target(frame, mapping, split=split)


def map_on_keys(pi: pd.DataFrame, K: pd.DataFrame, value_col: str = "pi_k_s_tar") -> np.ndarray:
    pm = pi.set_index(["client_id", "opportunity_stratum"])[value_col]
    return np.asarray([float(pm.get((c, s), 0.0))
                       for c, s in zip(K["client_id"], K["opportunity_stratum"])])


# --------------------------------------------------------------------------- M1
def _clip_ring(ring: list[tuple[float, float]], x0: float, x1: float, y0: float, y1: float):
    """Sutherland-Hodgman clip of one ring against an axis-aligned rectangle."""
    def clip(poly, inside, intersect):
        out = []
        n = len(poly)
        for i in range(n):
            cur, prv = poly[i], poly[i - 1]
            ci, pi_ = inside(cur), inside(prv)
            if ci:
                if not pi_:
                    out.append(intersect(prv, cur))
                out.append(cur)
            elif pi_:
                out.append(intersect(prv, cur))
        return out

    def ix(p, q):
        t = (x0 - p[0]) / (q[0] - p[0])
        return (x0, p[1] + t * (q[1] - p[1]))

    def jx(p, q):
        t = (x1 - p[0]) / (q[0] - p[0])
        return (x1, p[1] + t * (q[1] - p[1]))

    def iy(p, q):
        t = (y0 - p[1]) / (q[1] - p[1])
        return (p[0] + t * (q[0] - p[0]), y0)

    def jy(p, q):
        t = (y1 - p[1]) / (q[1] - p[1])
        return (p[0] + t * (q[0] - p[0]), y1)

    poly = list(ring)
    poly = clip(poly, lambda p: p[0] >= x0, ix)
    if not poly:
        return []
    poly = clip(poly, lambda p: p[0] <= x1, jx)
    if not poly:
        return []
    poly = clip(poly, lambda p: p[1] >= y0, iy)
    if not poly:
        return []
    return clip(poly, lambda p: p[1] <= y1, jy)


def _signed_area(poly: list[tuple[float, float]]) -> float:
    if len(poly) < 3:
        return 0.0
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return 0.5 * s


def apportion_population(origin: dict, cells: pd.DataFrame) -> tuple[dict, dict]:
    """Area-weighted apportionment of block-group population onto stored cells."""
    import shapefile  # pyshp

    pop = {}
    for name in ACS_FILES:
        rows = json.loads((LANDING / name).read_text())
        hdr, body = rows[0], rows[1:]
        i_pop = hdr.index("B01003_001E")
        for r in body:
            geoid = f"{r[hdr.index('state')]}{r[hdr.index('county')]}{r[hdr.index('tract')]}{r[hdr.index('block group')]}"
            pop[geoid] = float(r[i_pop])

    cell_ids = set(cells["spatial_id"].astype(str))
    acc: dict[str, float] = {}
    stats = {"n_bg_polygons": 0, "n_bg_without_pop": 0, "pop_total": float(sum(pop.values())),
             "pop_apportioned_to_stored_cells": 0.0, "pop_outside_stored_cells": 0.0,
             "n_clip_ops": 0}
    for zname in TIGER_ZIPS:
        target = EXTRACT / pathlib.Path(zname).stem
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(LANDING / zname) as zf:
            zf.extractall(target)
        shp = next(target.glob("*.shp"))
        reader = shapefile.Reader(str(shp))
        fields = [f[0] for f in reader.fields[1:]]
        i_geoid = fields.index("GEOID")
        for sr in reader.iterShapeRecords():
            geoid = str(sr.record[i_geoid])
            bg_pop = pop.get(geoid, 0.0)
            stats["n_bg_polygons"] += 1
            if bg_pop == 0.0:
                stats["n_bg_without_pop"] += 1
                continue
            rings = []
            pts = sr.shape.points
            parts = list(sr.shape.parts) + [len(pts)]
            for a, b in zip(parts[:-1], parts[1:]):
                ring = [(float(x), float(y)) for x, y in pts[a:b]]
                if len(ring) >= 4:
                    rings.append(ring)
            if not rings:
                continue
            # transform to cell units
            xy = [[((x - origin["lon0"]) / origin["lon_deg"],
                    (y - origin["lat0"]) / origin["lat_deg"]) for x, y in ring] for ring in rings]
            area_bg = abs(sum(_signed_area(r) for r in xy))
            if area_bg <= 0:
                continue
            xs = [p[0] for r in xy for p in r]
            ys = [p[1] for r in xy for p in r]
            gx0, gx1 = int(math.floor(min(xs))), int(math.floor(max(xs)))
            gy0, gy1 = int(math.floor(min(ys))), int(math.floor(max(ys)))
            for gx in range(gx0, gx1 + 1):
                for gy in range(gy0, gy1 + 1):
                    x0, x1, y0, y1 = gx, gx + 1, gy, gy + 1
                    clipped = sum(_signed_area(_clip_ring(r, x0, x1, y0, y1)) for r in xy)
                    stats["n_clip_ops"] += 1
                    ov = abs(clipped)
                    if ov <= 0:
                        continue
                    cell = f"g{gx:04d}_{gy:04d}"
                    share = bg_pop * (ov / area_bg)
                    if cell in cell_ids:
                        acc[cell] = acc.get(cell, 0.0) + share
                        stats["pop_apportioned_to_stored_cells"] += share
                    else:
                        stats["pop_outside_stored_cells"] += share
    stats["n_cells_with_population"] = len(acc)
    stats["n_stored_cells_with_zero_population"] = len(cell_ids - set(acc))
    return acc, stats


def build_m1(atomic: pd.DataFrame, K: pd.DataFrame, origin: dict, cells: pd.DataFrame):
    pop, stats = apportion_population(origin, cells)
    K = K.copy()
    legal = np.zeros(len(K), dtype=float)
    for i, (cell, region) in enumerate(zip(K["client_id"], K["region"])):
        legal[i] = pop.get(cell, 0.0)
    # positive mass of a cell split evenly over its 8 legal strata
    pi = np.zeros(len(K), dtype=float)
    cell_region = dict(zip(K["client_id"], K["region"]))
    counts = {}
    for cell in K["client_id"].unique():
        counts[cell] = 8
    for i, cell in enumerate(K["client_id"]):
        pi[i] = (legal[i] / counts[cell]) if legal[i] > 0 else 0.0
    total = pi.sum()
    if total <= 0:
        raise SystemExit("STOP: M1 map is all-zero; not changing the rule")
    pi = pi / total
    stats["pi_sum"] = float(pi.sum())
    stats["n_cells_with_positive_population"] = int(sum(1 for c in K["client_id"].unique()
                                                         if pop.get(c, 0.0) > 0))
    return pi, stats


# --------------------------------------------------------------------------- M2
def build_m2(atomic: pd.DataFrame, K: pd.DataFrame, origin: dict, cells: pd.DataFrame,
             chunksize: int = 1_000_000):
    cell_ids = set(cells["spatial_id"].astype(str))
    counts: dict[tuple[str, int, str], int] = {}
    stats = {"n_rows_read": 0, "n_rows_kept": 0, "n_rows_no_coords": 0,
             "n_rows_outside_bbox": 0, "n_rows_outside_stored_cells": 0,
             "n_rows_bad_time": 0, "t_min_utc": None, "t_max_utc": None}
    usecols = ["created_date", "latitude", "longitude"]
    for chunk in pd.read_csv(LANDING / NYC311, usecols=usecols, chunksize=chunksize,
                             dtype=str, encoding="utf-8-sig"):
        stats["n_rows_read"] += len(chunk)
        t = pd.to_datetime(chunk["created_date"], format="%Y-%m-%dT%H:%M:%S.%f",
                           errors="coerce")
        lat = pd.to_numeric(chunk["latitude"], errors="coerce")
        lon = pd.to_numeric(chunk["longitude"], errors="coerce")
        bad_time = t.isna()
        stats["n_rows_bad_time"] += int(bad_time.sum())
        no_coords = ~(lat.notna() & lon.notna())
        stats["n_rows_no_coords"] += int((no_coords & ~bad_time).sum())
        keep = (~bad_time) & (~no_coords)
        if not keep.any():
            continue
        t = t[keep]
        # DST disambiguation (operational detail, reported): the repeated autumn hour is
        # resolved as DST so the mapping stays deterministic; count those rows.
        amb = t.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").isna()
        stats["n_rows_dst_ambiguous"] = stats.get("n_rows_dst_ambiguous", 0) + int(amb.sum())
        t = t.dt.tz_localize("America/New_York", ambiguous=True,
                             nonexistent="shift_forward").dt.tz_convert("UTC")
        la = lat[keep].to_numpy()
        lo = lon[keep].to_numpy()
        inside = ((lo >= origin["lon0"]) & (lo <= origin["lon1"]) &
                  (la >= origin["lat0"]) & (la <= origin["lat1"]))
        stats["n_rows_outside_bbox"] += int((~inside).sum())
        if not inside.any():
            continue
        t = t[inside]
        x, y = to_grid_units(lo[inside], la[inside], origin)
        gx, gy = np.floor(x).astype(int), np.floor(y).astype(int)
        cell = np.asarray([f"g{a:04d}_{b:04d}" for a, b in zip(gx, gy)])
        in_cells = np.asarray([c in cell_ids for c in cell])
        stats["n_rows_outside_stored_cells"] += int((~in_cells).sum())
        t = t[in_cells]
        cell = cell[in_cells]
        if len(cell) == 0:
            continue
        hour = t.dt.hour.to_numpy()
        dow = t.dt.dayofweek.to_numpy()
        block = hour // 6
        label = np.where(dow >= 5, "weekend", "weekday")
        tmin, tmax = t.min(), t.max()
        stats["t_min_utc"] = tmin if stats["t_min_utc"] is None else min(stats["t_min_utc"], tmin)
        stats["t_max_utc"] = tmax if stats["t_max_utc"] is None else max(stats["t_max_utc"], tmax)
        df = pd.DataFrame({"cell": cell, "block": block, "label": label,
                           "n": np.ones(len(cell), dtype=np.int64)})
        for key, grp in df.groupby(["cell", "block", "label"], sort=False):
            counts[key] = counts.get(key, 0) + int(grp["n"].sum())
        stats["n_rows_kept"] += int(len(cell))
    pi = np.zeros(len(K), dtype=float)
    for i, (cell, b, lab) in enumerate(zip(K["client_id"], K["block"], K["weekday_label"])):
        pi[i] = float(counts.get((cell, int(b), lab), 0))
    total = pi.sum()
    if total <= 0:
        raise SystemExit("STOP: M2 map is all-zero; not changing the rule")
    pi = pi / total
    stats["pi_sum"] = float(pi.sum())
    stats["n_nonzero_keys"] = int((pi > 0).sum())
    return pi, stats


# --------------------------------------------------------------------------- evaluation
def trace_delivered(u_filter: bool = True):
    recs, meta = [], {}
    for seed_dir in sorted(TRACES.glob("seed*")):
        path = seed_dir / "training_eventtrace" / "events.parquet"
        if not path.is_file():
            meta[seed_dir.name] = "missing"
            continue
        ev = pd.read_parquet(path)
        meta[seed_dir.name] = {"events": int(len(ev))}
        for row in ev.itertuples(index=False):
            if (not u_filter) or bool(row.U):
                for uid in json.loads(row.risk_set_unit_ids):
                    recs.append({"seed": seed_dir.name, "window_id": int(row.window_id),
                                 "client_id": str(row.client_id), "unit_id": str(uid)})
    return pd.DataFrame(recs), meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="build M1/M2 from the landed sources")
    ap.add_argument("--dump-maps", action="store_true", help="write key-level maps and marginals")
    ap.add_argument("--stamp", default=datetime.now(timezone.utc).isoformat())
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    pts = raw_points()
    origin = grid_origin(pts)
    atomic = pd.read_parquet(PROCESSED)
    feats = atomic["public_features"].apply(lambda d: d if isinstance(d, dict) else json.loads(d))
    cells = (atomic.assign(spatial_id=atomic["spatial_id"].astype(str),
                           gx=[int(f["gx"]) for f in feats],
                           gy=[int(f["gy"]) for f in feats])
             .drop_duplicates("spatial_id")[["spatial_id", "gx", "gy"]])
    align = alignment(pts, origin, cells)
    (OUT / "GRID_ALIGNMENT.json").write_text(
        json.dumps({"stamp_utc": args.stamp, "origin": origin, "alignment": align}, indent=2),
        encoding="utf-8")

    K = key_universe(atomic)
    vocab = sorted({f"{r}::block{b}::{lab}" for r in REGION_ORDER for b in BLOCKS for lab in LABELS})
    observed = sorted(atomic["opportunity_stratum"].astype(str).unique())

    # control row
    pi_ctrl = control_map(atomic, split="test")
    ctrl_vals = map_on_keys(pi_ctrl, K)
    rows = []

    # delivered units
    delivered, trace_meta = trace_delivered(u_filter=True)
    split_of = atomic.assign(unit_id=atomic["unit_id"].astype(str)).set_index("unit_id")["split"]
    stratum_of = atomic.assign(unit_id=atomic["unit_id"].astype(str)).set_index("unit_id")["opportunity_stratum"]
    delivered["split"] = delivered["unit_id"].map(split_of).fillna("unknown")
    delivered["stratum"] = delivered["unit_id"].map(stratum_of)
    train_only = delivered[delivered["split"] != "test"].copy()
    all_events, _ = trace_delivered(u_filter=False)
    all_events["split"] = all_events["unit_id"].map(split_of).fillna("unknown")
    all_events["stratum"] = all_events["unit_id"].map(stratum_of)
    all_events = all_events[all_events["split"] != "test"]

    def rho_for(pi: np.ndarray, frame: pd.DataFrame) -> dict:
        lut = {(c, s): float(v) for (c, s), v in
               zip(zip(K["client_id"], K["opportunity_stratum"]), pi)}
        vals = np.asarray([lut.get((c, s), np.nan) for c, s in zip(frame["client_id"], frame["stratum"])])
        n = int(np.isfinite(vals).sum())
        n_zero = int(np.nansum(vals <= 0))
        return {"n_delivered": n, "n_zero": n_zero,
                "rho_delivered": (n_zero / n) if n else None,
                "gate": "on" if n and n_zero == 0 else ("off" if n else "TBD")}

    # sensitivity (control object under other splits / delivered definitions)
    sens = []
    for split_name in ("test", "train", "validation"):
        p = map_on_keys(control_map(atomic, split=split_name), K)
        for label, frame in (("delivered_U1_train", train_only), ("delivered_all_events_train", all_events)):
            r = rho_for(p, frame)
            sens.append({"pi_target_split": split_name, "delivered_definition": label,
                         "n_rows": r["n_delivered"], "n_zero": r["n_zero"],
                         "rho": r["rho_delivered"], "gate": r["gate"]})

    m1_stats = m2_stats = None
    if args.build:
        pi_m1, m1_stats = build_m1(atomic, K, origin, cells)
        pi_m2, m2_stats = build_m2(atomic, K, origin, cells)
    else:
        pi_m1 = pi_m2 = None

    def add_row(name: str, pi, note: str = ""):
        if pi is None:
            rows.append({"map": name, "n_keys": len(K), "n_zero_keys": "BLOCKED",
                         "zero_key_share": "BLOCKED", "rho_delivered": "BLOCKED", "gate": "BLOCKED",
                         "removed_unit_share": "BLOCKED", "removed_mass_share": "BLOCKED",
                         "endpoints": "TBD (no map)", "note": note})
            return None
        n_zero = int((pi <= 0).sum())
        r = rho_for(pi, train_only)
        r_all = rho_for(pi, all_events)
        per_seed = []
        for seed, sub in train_only.groupby("seed"):
            rr = rho_for(pi, sub)
            per_seed.append({"seed": seed, **rr})
        detail[name] = {"n_zero_keys": n_zero, "zero_key_share": n_zero / len(K),
                        "rho_delivered_numerator": r["n_zero"], "rho_delivered_denominator": r["n_delivered"],
                        "rho_delivered": r["rho_delivered"], "gate": r["gate"],
                        "rho_all_events": r_all["rho_delivered"], "gate_all_events": r_all["gate"],
                        "per_seed": per_seed,
                        "map_sha256": hashlib.sha256(np.asarray(pi, dtype=np.float64).tobytes()).hexdigest(),
                        "pi_sum": float(np.asarray(pi, dtype=float).sum())}
        rows.append({"map": name, "n_keys": len(K), "n_zero_keys": n_zero,
                     "zero_key_share": n_zero / len(K), "rho_delivered": r["rho_delivered"],
                     "gate": r["gate"], "removed_unit_share": r["rho_delivered"],
                     "removed_mass_share": "TBD", "endpoints": "TBD (no new mu)", "note": note})
        return r

    detail: dict[str, dict] = {}
    r_ctrl = add_row("control_evaluation_derived", ctrl_vals, "build_pi_target(split='test')")
    r_m1 = add_row("M1_spatial_population_ACS2021_B01003", pi_m1, "ACS 2021 5-yr B01003, area-weighted")
    r_m2 = add_row("M2_temporal_demand_NYC311", pi_m2, "NYC 311 counts, 2020-2021, region from cell")

    gates = [r["gate"] for r in (r_ctrl, r_m1, r_m2) if r is not None]
    reading = None
    if len(gates) >= 2 and len(set(gates)) > 1:
        reading = ("门依赖于目标图的时间边际：M1 与 M2 的 gate 不同，按预注册不选更有利的一张作为主结果"
                   if {r_m1 and r_m1["gate"], r_m2 and r_m2["gate"]} == {"on", "off"}
                   else "gate 在三个对象之间不一致（含对照），按预注册不选择")
    pd.DataFrame(rows).to_csv(OUT / "MAP_SUMMARY.csv", index=False)

    ckpts = sorted(RUNS.glob("*/seed*/checkpoints/final.pt")) if RUNS.is_dir() else []
    landed = {name: {"sha256": sha256(LANDING / name), "bytes": (LANDING / name).stat().st_size}
              for name in (*ACS_FILES, *TIGER_ZIPS, NYC311) if (LANDING / name).is_file()}
    notes_txt = LANDING / "NOTES.txt"
    (OUT / "DOWNLOAD_LOG.json").write_text(json.dumps(
        {"stamp_utc": args.stamp,
         "network_probe_conclusion": "all HTTPS blocked in-sandbox; sources landed manually (see prereg §10)",
         "landed_files": landed,
         "notes_txt_sha256": sha256(notes_txt) if notes_txt.is_file() else None,
         "raw_pm_hashes": {n: sha256(RAW / n) for n in PM_FILES},
         "preregistration": "ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md",
         "preregistration_sha256": sha256(ROOT / "ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md"),
         "grid_alignment": align, "stratum_vocabulary": vocab,
         "observed_strata_equal_vocabulary": vocab == observed,
         "trace_meta": trace_meta, "control_sensitivity": sens,
         "control_rho": r_ctrl, "m1_rho": r_m1, "m2_rho": r_m2,
         "m1_stats": m1_stats, "m2_stats": m2_stats,
         "gate_reading": reading,
         "map_detail": detail,
         "n_checkpoints": len(ckpts),
         "removed_mass_share_note": ("no stored per-key Design-on weight: the City Scanner run dirs hold only "
                                     "checkpoints and CS_ACCEPTED.json, so it is TBD per protocol")},
        indent=2, default=str), encoding="utf-8")

    if args.dump_maps and pi_m1 is not None and pi_m2 is not None:
        tbl = K.copy()
        tbl["pi_control"] = ctrl_vals
        tbl["pi_M1"] = pi_m1
        tbl["pi_M2"] = pi_m2
        tbl.to_csv(OUT / "MAPS_KEY_LEVEL.csv", index=False)
        marg = []
        for name, pi in (("control", ctrl_vals), ("M1", pi_m1), ("M2", pi_m2)):
            for region, sub in tbl.groupby("region"):
                marg.append({"map": name, "region": region, "pi_sum": float(sub["pi_" + name].sum()),
                             "n_zero_keys": int((sub["pi_" + name] <= 0).sum())})
            for block, sub in tbl.groupby("block"):
                marg.append({"map": name, "margin": f"block{block}",
                             "pi_sum": float(sub["pi_" + name].sum())})
            for lab, sub in tbl.groupby("weekday_label"):
                marg.append({"map": name, "margin": lab, "pi_sum": float(sub["pi_" + name].sum())})
        pd.DataFrame(marg).to_csv(OUT / "MAP_MARGINALS.csv", index=False)
    print(json.dumps({"grid_ok": align["cells_equal"], "rows": rows, "reading": reading,
                      "m1_stats": m1_stats, "m2_stats": m2_stats}, indent=2, default=str))


if __name__ == "__main__":
    main()
