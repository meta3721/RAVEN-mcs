"""Validation support counts only. No model, no score, no training."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("C:/Cursor/raven.mcs")
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data/processed/cityscanner_nyc_p2_measured_o"
P0 = ROOT / "ccf-review-report/active_participation_p0_20261020_1605"
REGIONS = ("region0", "region1", "region2", "region3")
WARMUP_BOUND = pd.Timestamp("2021-09-22 23:00:00", tz="UTC")

occupancy = pd.read_parquet(
    DATA / "occupancy_units.parquet",
    columns=["unit_id", "spatial_id", "client_id", "absolute_time", "split", "target_group", "o_observed"],
)
atomic = pd.read_parquet(
    DATA / "atomic_units.parquet",
    columns=["unit_id", "spatial_id", "absolute_time", "split", "target_group", "target_value", "is_warmup"],
)
clients = pd.read_parquet(
    DATA / "client_measurements.parquet",
    columns=["client_id", "unit_id", "potential_measurement", "split"],
)
occupancy["absolute_time"] = pd.to_datetime(occupancy["absolute_time"], utc=True)
atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
for frame in (occupancy, atomic, clients):
    for column in ("unit_id", "spatial_id", "client_id", "split", "target_group"):
        if column in frame.columns:
            frame[column] = frame[column].astype(str)

warmup = atomic.loc[atomic["split"].eq("train") & atomic["is_warmup"].map(lambda value: bool(value))]
vocab = sorted(set(warmup["spatial_id"]))
if warmup["absolute_time"].max() != WARMUP_BOUND:
    raise SystemExit("warmup bound mismatch")
if len(vocab) != 118:
    raise SystemExit(f"vocab {len(vocab)} != 118")

validation = occupancy.loc[
    occupancy["split"].eq("validation") & occupancy["o_observed"].astype(int).eq(1)
].copy()
atomic_val = atomic.loc[atomic["split"].eq("validation")].set_index("unit_id", drop=False)
client_val = clients.loc[clients["split"].eq("validation")].set_index("unit_id", drop=False)

rows = []
for record in validation.itertuples(index=False):
    reasons = []
    unit_id = str(record.unit_id)
    if str(record.spatial_id) not in set(vocab):
        reasons.append("unknown_spatial")
    if str(record.client_id) != str(record.spatial_id) or str(record.spatial_id).startswith("NYCP"):
        reasons.append("illegal_id")
    if str(record.target_group) not in REGIONS:
        reasons.append("unknown_group")
    finite = False
    if unit_id not in atomic_val.index:
        reasons.append("missing_atomic")
    else:
        atomic_row = atomic_val.loc[unit_id]
        if str(atomic_row["spatial_id"]) != str(record.spatial_id):
            reasons.append("spatial_mismatch")
        target = float(atomic_row["target_value"])
        finite = bool(np.isfinite(target))
        if not finite:
            reasons.append("nonfinite_label")
    if unit_id not in client_val.index:
        reasons.append("missing_client_measurement")
    else:
        measured = client_val.loc[unit_id]
        if str(measured["client_id"]) != str(record.client_id):
            reasons.append("client_id_mismatch")
        label = float(measured["potential_measurement"])
        if not np.isfinite(label):
            reasons.append("nonfinite_client_label")
            finite = False
    kept = len(reasons) == 0 and finite and str(record.spatial_id) in set(vocab)
    rows.append(
        {
            "unit_id": unit_id,
            "group": str(record.target_group),
            "kept": kept,
            "reasons": reasons,
        }
    )

frame = pd.DataFrame(rows)
kept = frame.loc[frame["kept"]]
reason_counts = {}
for reasons in frame.loc[~frame["kept"], "reasons"]:
    for reason in reasons:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

by_group = {}
for region in REGIONS:
    block = frame.loc[frame["group"].eq(region)]
    by_group[region] = {
        "validation_o1": int(len(block)),
        "kept": int(block["kept"].sum()),
        "excluded": int((~block["kept"]).sum()),
    }

payload = {
    "source": "occupancy validation O=1 joined to atomic and client_measurements; test rows were not read for this file",
    "vocabulary": "sorted train warmup spatial ids; n=118",
    "validation_o1_records": int(len(frame)),
    "kept_records": int(len(kept)),
    "kept_fraction": float(len(kept) / len(frame)) if len(frame) else None,
    "by_group": by_group,
    "exclusion_counts": reason_counts,
    "evaluation_unit_ids": kept["unit_id"].tolist(),
    "same_list_for_both_arms": True,
    "arm_lists_differ": False,
    "scores_computed": False,
    "regions_all_supported": all(by_group[region]["kept"] > 0 for region in REGIONS),
}
(OUT / "EVALUATION_SUPPORT.json").write_text(
    json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(json.dumps({
    "validation_o1": payload["validation_o1_records"],
    "kept": payload["kept_records"],
    "kept_fraction": payload["kept_fraction"],
    "by_group": {region: by_group[region]["kept"] for region in REGIONS},
    "regions_all_supported": payload["regions_all_supported"],
}, ensure_ascii=False))
