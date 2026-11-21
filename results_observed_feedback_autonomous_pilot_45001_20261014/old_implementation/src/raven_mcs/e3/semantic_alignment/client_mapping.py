"""Freeze E3 client count and spatial→client mapping before performance results."""

from __future__ import annotations

from typing import Any

import yaml

from raven_mcs.utils.hashing import sha256_json


def load_sensorscope_mapping(root) -> dict[str, str]:
    from pathlib import Path

    path = Path(root) / "configs/frozen/e1_sensorscope_clients.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in payload["station_to_client"].items()}


def build_uair_mapping(atomic, *, n_clients: int = 8) -> dict[str, str]:
    spatials = sorted(atomic["spatial_id"].astype(str).unique().tolist())
    mapping = {}
    for i, sid in enumerate(spatials):
        mapping[sid] = f"client-{i % n_clients:03d}"
    return mapping


def traffic_mapping_note() -> dict[str, Any]:
    return {
        "dataset": "traffic",
        "n_spatial_units": 43,
        "n_logical_fl_clients": 43,
        "mapping_rule": "formal E2: each station is its own client (PROFILE-S1 sealed)",
        "one_client_owns_multiple_spatial": False,
        "public_frozen": True,
        "justification": "Preserve sealed Traffic formal identity; do not collapse to K=8",
    }


def freeze_client_mappings(root, atomic_by_dataset: dict) -> dict[str, Any]:
    ss_map = load_sensorscope_mapping(root)
    ua_map = build_uair_mapping(atomic_by_dataset["uair"], n_clients=8)
    payload = {
        "choice": "A_KEEP_K8_FOR_SENSORSCOPE_UAIR",
        "justification": (
            "Keep K=8 for SensorScope/U-Air as the computationally frozen RAVEN client "
            "implementation path (E1 SensorScope mapping reused). Early design K=50 is not "
            "adopted. Traffic retains sealed 43-station client identity."
        ),
        "datasets": {
            "sensorscope": {
                "n_spatial_units": 55,
                "n_logical_fl_clients": 8,
                "spatial_to_client": ss_map,
                "one_client_owns_multiple_spatial": True,
                "mapping_construction_rule": "frozen E1 station_to_client (configs/frozen/e1_sensorscope_clients.yaml)",
                "public_frozen": True,
                "hash": sha256_json(ss_map),
            },
            "uair": {
                "n_spatial_units": 36,
                "n_logical_fl_clients": 8,
                "spatial_to_client": ua_map,
                "one_client_owns_multiple_spatial": True,
                "mapping_construction_rule": "deterministic round-robin of sorted spatial_id into client-000..007",
                "public_frozen": True,
                "hash": sha256_json(ua_map),
            },
            "traffic": {
                **traffic_mapping_note(),
                "spatial_to_client": {str(i): f"station-{i}" for i in range(43)},
                "hash": sha256_json({"n_clients": 43, "rule": "1:1 station"}),
            },
        },
        "all_methods_use_identical_mapping_per_dataset": True,
        "frozen_before_performance_results": True,
    }
    return payload
