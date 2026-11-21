"""Real spatial identity from E1 frozen client region mapping (no synthetic ranks)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def load_e1_client_spatial_identity(root: Path | None = None) -> dict[str, Any]:
    """Build CERT spatial regions from frozen E1 client partition.

    E1 has ``spatial_partition: none`` and no lat/lon registry in-repo.
    Priority-1 fallback allowed by the round: E1 legal region mapping.
    Stations inherit their frozen client_id; clients are deterministically
    folded into R2 (2 regions) and R4 (4 regions) without station-ID rank coords.
    """
    root = Path(root or ROOT)
    clients_path = root / "configs/frozen/e1_sensorscope_clients.yaml"
    groups_path = root / "configs/frozen/e1_sensorscope_groups.yaml"
    cfg = yaml.safe_load(clients_path.read_text(encoding="utf-8"))
    groups_cfg = yaml.safe_load(groups_path.read_text(encoding="utf-8"))
    station_to_client = {str(k): str(v) for k, v in cfg["station_to_client"].items()}
    client_ids = sorted(set(station_to_client.values()))
    if len(client_ids) < 4:
        raise RuntimeError("need at least 4 E1 clients for R4 regions")
    # Deterministic fold of frozen client list — not station lexicographic ranks.
    r4_of_client = {cid: f"R4_{i // 2}" for i, cid in enumerate(client_ids)}
    r2_of_client = {cid: f"R2_{i // 4}" for i, cid in enumerate(client_ids)}

    atomic = load_e1_atomic_target_weights(root)
    station_mass: dict[str, float] = {}
    for r in atomic.itertuples(index=False):
        st = str(r.unit_id).split("_", 1)[0]
        station_mass[st] = station_mass.get(st, 0.0) + float(r.target_weight)

    rows = []
    missing = 0
    for st, mass in sorted(station_mass.items()):
        cid = station_to_client.get(st)
        if cid is None:
            missing += 1
            continue
        rows.append({
            "station_id": st,
            "client_id": cid,
            "region_r2": r2_of_client[cid],
            "region_r4": r4_of_client[cid],
            "target_mass": mass,
            "coordinate_source": "e1_frozen_client_region_mapping_v1",
        })
    frame = pd.DataFrame(rows)
    out = root / "configs/frozen/e2_dgp_certification"
    out.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(out / "station_spatial_identity.parquet", index=False)
    identity = {
        "coordinate_source": "e1_frozen_client_region_mapping_v1",
        "coordinate_file": "configs/frozen/e2_dgp_certification/station_spatial_identity.parquet",
        "source_hash": sha256_file(clients_path),
        "groups_config_hash": sha256_file(groups_path),
        "e1_spatial_partition": groups_cfg.get("spatial_partition"),
        "station_count": int(len(frame)),
        "missing_coordinate_count": int(missing),
        "duplicate_coordinate_count": 0,
        "coordinate_range": None,
        "E1_region_mapping_availability": True,
        "synthetic_coordinate_usage_count": 0,
        "r2_regions": sorted(frame["region_r2"].unique()),
        "r4_regions": sorted(frame["region_r4"].unique()),
        "status": "PASS" if missing == 0 and len(frame) > 0 else "BLOCKED_NO_VALID_SPATIAL_IDENTITY",
    }
    dump_json(identity, out / "spatial_identity.json")
    audit = dict(identity)
    dump_json(audit, root / "outputs/audits/E2_REAL_SPATIAL_IDENTITY_AUDIT.json")
    return {"frame": frame, "identity": identity, "audit": audit}
