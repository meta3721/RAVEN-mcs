#!/usr/bin/env python3
"""Ingest NYC Pilot2 measured-O occupancy. Does not train. Does not touch Table II."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.data.cityscanner_p2_measured_o import write_p2_measured_o  # noqa: E402
from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

SPEC_PATH = ROOT / "post_review" / "JOINT_MEASURED_OU_RANK" / "TARGET_SPEC.json"
RAW = ROOT / "data" / "raw" / "cityscanner_nyc_pm25"
PROCESSED = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o"
OUT = ROOT / "results_joint_ou" / "round_v1"
OLD_PROCESSED = ROOT / "data" / "processed" / "cityscanner_nyc_pm25"


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def main() -> int:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if spec.get("status") != "LOCKED":
        raise SystemExit("TARGET_SPEC.json is not LOCKED")
    if spec.get("chosen_option") != "CS_NYC_P2_DUAL_SENSOR_MEASURED_O":
        raise SystemExit("ingest only implements CS_NYC_P2_DUAL_SENSOR_MEASURED_O")
    if not spec.get("human_signoff"):
        raise SystemExit("human_signoff empty")
    OUT.mkdir(parents=True, exist_ok=True)
    payload = write_p2_measured_o(RAW, PROCESSED)
    atomic_hash = sha256_file(PROCESSED / "atomic_units.parquet")
    occ_hash = sha256_file(PROCESSED / "occupancy_units.parquet")
    meas_hash = sha256_file(PROCESSED / "client_measurements.parquet")
    if OLD_PROCESSED.joinpath("atomic_units.parquet").is_file():
        old = sha256_file(OLD_PROCESSED / "atomic_units.parquet")
        if old == atomic_hash:
            raise RuntimeError("new processed hash collided with cityscanner_nyc_pm25")
    audit = payload["audit"]
    report = {
        "experiment_id": spec["experiment_id"],
        "status": "INGEST_FROZEN",
        "dataset": spec["dataset_id"],
        "clients": "spatial_id",
        "vehicles_are_fl_clients": False,
        "r_layer": spec["r_layer"],
        "o_layer": spec["o_layer"],
        "u_layer": spec["u_layer"],
        "data_hash": atomic_hash,
        "occupancy_sha256": occ_hash,
        "measurements_sha256": meas_hash,
        "n_union_cell_slots": audit["n_union_cell_slots"],
        "n_o0_cell_slots": audit["n_o0_cell_slots"],
        "measured_o0_fraction": audit["measured_o0_fraction"],
        "n_atomic_o1": audit["n_atomic_o1"],
        "n_occupancy": audit["n_occupancy"],
        "grid_origin_lon": audit["grid_origin_lon"],
        "grid_origin_lat": audit["grid_origin_lat"],
        "p_obs_bernoulli": False,
        "phi_run": False,
        "eventtrace_run": False,
        "train_run": False,
        "git_commit": _git_commit(),
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "audit": audit,
    }
    dump_json(report, OUT / "INGEST_REPORT.json")
    dump_json(
        {"data_hash": atomic_hash, "occupancy_sha256": occ_hash},
        PROCESSED / "identity.json",
    )
    print(json.dumps({k: report[k] for k in (
        "status",
        "data_hash",
        "n_union_cell_slots",
        "measured_o0_fraction",
        "n_atomic_o1",
        "n_occupancy",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
