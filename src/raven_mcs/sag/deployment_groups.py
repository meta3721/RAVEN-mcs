"""Paper deployment-group map h(i): four UTC time-of-day blocks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder
from raven_mcs.utils.hashing import sha256_json

GROUP_LABELS = {
    0: "H1:00-06",
    1: "H2:06-12",
    2: "H3:12-18",
    3: "H4:18-24",
}
N_H_GROUPS = 4
MAP_FILENAMES = {
    "sensorscope": "SensorScope_h_map.json",
    "uair": "UAir_h_map.json",
}
SOURCE = (
    "FINAL_H_S_MANUSCRIPT_SEMANTICS_R1.json + TABLE_I + "
    "RepeatableTimeOfDayMapper (UTC hour // 6)"
)


def utc_tod_block(absolute_time: pd.Series) -> pd.Series:
    mapper = RepeatableTimeOfDayMapper()
    frame = pd.DataFrame({"absolute_time": absolute_time})
    return mapper.map(frame).astype("int64")


def build_paper_h_payload(atomic: pd.DataFrame, *, dataset: str) -> dict[str, Any]:
    if "unit_id" not in atomic.columns or "absolute_time" not in atomic.columns:
        raise ValueError("atomic table must contain unit_id and absolute_time")
    blocks = utc_tod_block(atomic["absolute_time"])
    if not set(int(x) for x in blocks.unique()).issubset({0, 1, 2, 3}):
        raise ValueError("RepeatableTimeOfDayMapper produced a block outside {0,1,2,3}")
    unit_to_h = {
        str(uid): int(h)
        for uid, h in zip(atomic["unit_id"].astype(str).tolist(), blocks.tolist())
    }
    frame = atomic.copy()
    frame["target_group_main"] = blocks.astype(str)
    masses = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(
        frame, split="train",
    )
    mu = np.zeros(N_H_GROUPS, dtype=np.float64)
    for key, value in masses.group_mass.items():
        g = int(key)
        if g < 0 or g >= N_H_GROUPS:
            raise ValueError(f"unexpected train group id {key}")
        mu[g] = float(value)
    total = float(mu.sum())
    if total <= 0:
        raise ValueError("train-split paper-h mu sums to 0")
    mu = mu / total
    payload = {
        "dataset": str(dataset).lower(),
        "n_groups": N_H_GROUPS,
        "rule": "RepeatableTimeOfDayMapper_UTC_hour_floordiv_6",
        "source": SOURCE,
        "mu_construction": "train_split_supported_atomic_uniform_then_marginalize",
        "uses_labels": False,
        "uses_test": False,
        "uses_current_window": False,
        "group_labels": {str(k): v for k, v in GROUP_LABELS.items()},
        "mu": mu.tolist(),
        "unit_to_h": unit_to_h,
        "n_units": len(unit_to_h),
    }
    payload["map_hash"] = sha256_json(
        {"unit_to_h": unit_to_h, "rule": payload["rule"], "mu": payload["mu"]}
    )
    return payload


def map_path(root: Path, dataset: str) -> Path:
    name = MAP_FILENAMES.get(str(dataset).lower())
    if name is None:
        raise KeyError(f"no paper h-map filename for dataset={dataset}")
    return Path(root) / "configs" / "deployment_group_map" / name


def write_paper_h_map(root: Path, atomic: pd.DataFrame, *, dataset: str) -> dict[str, Any]:
    payload = build_paper_h_payload(atomic, dataset=dataset)
    path = map_path(root, dataset)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    payload["path"] = str(path.relative_to(root)).replace("\\", "/")
    return payload


def load_paper_h_map(root: Path, dataset: str) -> dict[str, Any]:
    path = map_path(root, dataset)
    if not path.is_file():
        raise FileNotFoundError(f"paper h-map missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if int(payload.get("n_groups", 0)) != N_H_GROUPS:
        raise ValueError("paper h-map n_groups must be 4")
    payload["path"] = str(path.relative_to(root)).replace("\\", "/")
    return payload


def unit_to_h(payload: Mapping[str, Any]) -> dict[str, int]:
    raw = payload.get("unit_to_h") or {}
    return {str(k): int(v) for k, v in raw.items()}


def paper_mu(payload: Mapping[str, Any]) -> np.ndarray:
    mu = np.asarray(payload.get("mu"), dtype=np.float64).reshape(-1)
    if mu.size != N_H_GROUPS:
        raise ValueError("paper mu must have 4 entries")
    if abs(float(mu.sum()) - 1.0) > 1e-8:
        raise ValueError("paper mu must be normalized")
    return mu
