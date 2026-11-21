"""E3-v2 EventTrace schema + deterministic builder. Isolated from E3-v1 artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from e3_v2_context import public_context_from_start
from e3_v2_protocol import PROTOCOL_VERSION, SEED, TAU_COV, population_rule_hash, window_rule_hash
from raven_mcs.sag.e3v1_root_cause import natural_windows_from_atomic, realized_mass_from_units, unit_meta_from_atomic
from raven_mcs.utils.hashing import sha256_json, sha256_text

SCHEMA_FIELDS = (
    "protocol_version",
    "dataset",
    "seed",
    "split_id",
    "window_id",
    "window_start_utc",
    "window_end_utc",
    "timezone",
    "public_context_hash",
    "risk_set_hash",
    "candidate_set_hash",
    "target_law_hash",
    "pi_safe_rule_hash",
    "tau_cov",
    "raw_window_source_hash",
    "event_count",
    "user_count",
    "spatial_support",
    "logical_deadline_fields",
    "optional_original_record_ids_hash",
)


def _hash_ids(ids: list[str]) -> str:
    return sha256_json(sorted(str(x) for x in ids))


def build_e3v2_windows(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    target_law_hash: str,
    pi_safe_rule_hash: str,
    split: str | None = "test",
    seed: int = SEED,
) -> pd.DataFrame:
    meta = unit_meta_from_atomic(atomic, spatial_to_client)
    natural = natural_windows_from_atomic(atomic, spatial_to_client, split=split)
    rows: list[dict[str, Any]] = []
    for window_id, rec in enumerate(natural):
        ctx = public_context_from_start(rec["window_start_utc"])
        units = list(rec["unit_ids"])
        by_client: dict[str, list[str]] = {}
        spatials: set[str] = set()
        for uid in units:
            info = meta.get(uid)
            if info is None:
                continue
            by_client.setdefault(info["client"], []).append(uid)
            spatials.add(info["spatial"])
        risk_hash = _hash_ids(units)
        ctx_hash = sha256_json(ctx)
        source_hash = sha256_json(
            {
                "time_index": rec["time_index"],
                "window_start_utc": rec["window_start_utc"],
                "unit_ids": sorted(units),
            }
        )
        for client in sorted(by_client):
            risk = sorted(set(by_client[client]))
            rows.append(
                {
                    "protocol_version": PROTOCOL_VERSION,
                    "dataset": dataset,
                    "seed": int(seed),
                    "split_id": str(rec["split"]),
                    "window_id": int(window_id),
                    "time_index": int(rec["time_index"]),
                    "window_start_utc": ctx["window_start_utc"],
                    "window_end_utc": ctx["window_end_utc"],
                    "timezone": "UTC",
                    "hour_of_day": ctx["hour_of_day"],
                    "weekday": ctx["weekday"],
                    "weekend_flag": ctx["weekend_flag"],
                    "public_context_hash": ctx_hash,
                    "client_id": client,
                    "risk_set_unit_ids": risk,
                    "candidate_set_unit_ids": list(risk),
                    "risk_set_hash": _hash_ids(risk),
                    "candidate_set_hash": _hash_ids(risk),
                    "target_law_hash": target_law_hash,
                    "pi_safe_rule_hash": pi_safe_rule_hash,
                    "tau_cov": TAU_COV,
                    "raw_window_source_hash": source_hash,
                    "event_count": len(risk),
                    "user_count": len(spatials),
                    "spatial_support": len(spatials),
                    "logical_deadline_fields": json.dumps(
                        {
                            "window_deadline_utc": ctx["window_end_utc"],
                            "window_duration_hours": 1,
                            "abstract_index_clock": False,
                        }
                    ),
                    "optional_original_record_ids_hash": _hash_ids(risk),
                    "window_rule_hash": window_rule_hash(),
                    "population_rule_hash": population_rule_hash(),
                }
            )
    return pd.DataFrame(rows)


def freeze_e3v2_trace(frame: pd.DataFrame, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "e3v2_eventtrace.parquet"
    frame.to_parquet(path, index=False)
    identity = {
        "protocol_version": PROTOCOL_VERSION,
        "n_rows": int(len(frame)),
        "n_windows": int(frame["window_id"].nunique()) if len(frame) else 0,
        "dataset": str(frame["dataset"].iloc[0]) if len(frame) else "",
        "window_rule_hash": window_rule_hash(),
        "population_rule_hash": population_rule_hash(),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "schema_fields": list(SCHEMA_FIELDS),
    }
    payload = frame.to_json(orient="split")
    identity["trace_hash"] = sha256_text(payload)
    (out_dir / "identity.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    return identity
