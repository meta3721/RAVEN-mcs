#!/usr/bin/env python3
"""Phase 0 static precheck + EventTrace families for E3 Canary R1."""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import (  # noqa: E402
    CANARY_SEED,
    FORMAL_SEEDS,
    M_MC,
    REGISTRY_SHA256,
    ROUND,
)
from raven_mcs.e3.canary.dataset_load import (  # noqa: E402
    load_horizon,
    load_spatial_to_client,
    verify_dataset_hash,
)
from raven_mcs.e3.canary.execute import ensure_eventtrace  # noqa: E402
from raven_mcs.e3.canary.schedule import build_canary_matrix  # noqa: E402
from raven_mcs.e3.canary.seed_audit import audit_canary_seed  # noqa: E402
from raven_mcs.e3.canary.traffic_reuse_guard import build_traffic_reuse_guard_evidence  # noqa: E402
from raven_mcs.e3.stratum_seal.constants import TRAFFIC_PUBLIC_TARGET_MAPPING_HASH  # noqa: E402
from raven_mcs.e3.stratum_seal.traffic_regions import load_frozen_traffic_station_regions  # noqa: E402
from raven_mcs.e3.target_pair.constants import FROZEN_TARGET_ARTIFACTS  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import load_frozen_target_artifact  # noqa: E402
from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    seed_audit = audit_canary_seed(CANARY_SEED)
    dump_json(seed_audit, ART / "E3_CANARY_SEED_AUDIT.json")
    if seed_audit["status"] != "PASS":
        dump_json(
            {"status": "CANARY_SEED_COLLISION", "seed_audit": seed_audit},
            ART / "E3_CANARY_STOP_STATUS.json",
        )
        print(json.dumps({"status": "CANARY_SEED_COLLISION"}, indent=2))
        return 2

    dataset_hashes = {ds: verify_dataset_hash(ROOT, ds) for ds in ("sensorscope", "uair", "traffic")}
    dump_json(dataset_hashes, ART / "E3_CANARY_DATASET_HASH_AUDIT.json")
    if not all(v["match"] for v in dataset_hashes.values()):
        dump_json(
            {
                "status": "E3_CANARY_BLOCKED_BY_SCIENTIFIC_SEMANTICS",
                "blocker": "FROZEN_DATASET_HASH_MISMATCH",
                "dataset_hashes": dataset_hashes,
            },
            ART / "E3_CANARY_STOP_STATUS.json",
        )
        print(json.dumps({"status": "FROZEN_DATASET_HASH_MISMATCH"}, indent=2))
        return 3

    target_audit = {}
    for ds, rel in FROZEN_TARGET_ARTIFACTS.items():
        art = load_frozen_target_artifact(ROOT, ds)
        target_audit[ds] = {
            "path": rel,
            "sha256": art["_artifact_sha256"],
            "n_groups": art["n_groups"],
            "status": "PASS",
        }
    target_audit["traffic"] = {
        "path": "freeze_from_atomic_at_runtime",
        "note": "Traffic uses public-target spatial×time freeze via TrafficRunnerDataset/atomic",
        "status": "PASS",
    }
    dump_json(target_audit, ART / "E3_CANARY_TARGET_HASH_AUDIT.json")

    _, tr_meta = load_frozen_traffic_station_regions(ROOT)
    stratum_audit = {
        "traffic_mapping_hash": tr_meta.get("mapping_hash"),
        "traffic_mapping_hash_expected": TRAFFIC_PUBLIC_TARGET_MAPPING_HASH,
        "traffic_4_region": tr_meta.get("mapping_hash") == TRAFFIC_PUBLIC_TARGET_MAPPING_HASH,
        "status": (
            "PASS"
            if tr_meta.get("mapping_hash") == TRAFFIC_PUBLIC_TARGET_MAPPING_HASH
            else "FAIL"
        ),
    }
    dump_json(stratum_audit, ART / "E3_CANARY_STRATUM_HASH_AUDIT.json")

    reuse = build_traffic_reuse_guard_evidence()
    dump_json(reuse, ART / "E3_CANARY_TRAFFIC_REUSE_GUARD.json")

    matrix = build_canary_matrix()
    dump_json(matrix, ART / "E3_CANARY_RUN_MATRIX.json")

    # Materialize one shared EventTrace per dataset @ seed 31001
    et_rows = []
    for ds in ("sensorscope", "uair", "traffic"):
        info = ensure_eventtrace(ROOT, ART, ds, CANARY_SEED)
        identity = info.get("identity") or json.loads(
            (ART / "eventtraces" / ds / f"seed{CANARY_SEED}" / "training_eventtrace" / "trace_identity.json").read_text(
                encoding="utf-8"
            )
        )
        horizon = load_horizon(ROOT, ds)
        et_rows.append(
            {
                "dataset": ds,
                "seed": CANARY_SEED,
                "num_windows": int(horizon["chosen_E3_formal_windows"]),
                "m_mc": M_MC,
                "trace_hash": identity.get("trace_hash") or identity.get("events_sha256"),
                "events_sha256": identity.get("events_sha256"),
                "status": info.get("status"),
                "shared_across_methods": True,
            }
        )
    dump_json({"rows": et_rows, "status": "PASS"}, ART / "E3_CANARY_EVENTTRACE_AUDIT.json")
    import csv

    with (ART / "E3_CANARY_EVENTTRACE_AUDIT.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(et_rows[0].keys()))
        w.writeheader()
        w.writerows(et_rows)

    parent = {
        "e1_r2": "FULLY_SEALED",
        "e2_traffic": "SCIENTIFICALLY_SEALED",
        "stratum_reuse_seal": "READY_FOR_E3_MULTIDATASET_REAL_RUNNER_CANARY",
        "parent_stop": "artifacts/e3_stratum_identity_and_traffic_reuse_seal_r1/E3_STRATUM_REUSE_SEAL_STOP_STATUS.json",
        "parent_stop_exists": (
            ROOT
            / "artifacts/e3_stratum_identity_and_traffic_reuse_seal_r1/E3_STRATUM_REUSE_SEAL_STOP_STATUS.json"
        ).is_file(),
        "registry_sha256_expected": REGISTRY_SHA256,
    }
    dump_json(parent, ART / "E3_CANARY_PARENT_INTEGRITY.json")

    resources = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "max_workers_default": 1,
        "note": "CPU-only; sequential logical runs by default to avoid oversubscription",
    }
    dump_json(resources, ART / "E3_CANARY_RESOURCE_PROFILE.json")

    phase0_ok = (
        seed_audit["status"] == "PASS"
        and all(v["match"] for v in dataset_hashes.values())
        and stratum_audit["status"] == "PASS"
        and reuse.get("duplicate_blocked") is True
        and parent["parent_stop_exists"]
        and len(et_rows) == 3
    )
    stop = {
        "round": ROUND,
        "phase": 0,
        "status": "PHASE0_PASS_READY_FOR_PHASE1" if phase0_ok else "E3_CANARY_BLOCKED_BY_SCIENTIFIC_SEMANTICS",
        "canary_seed": CANARY_SEED,
        "formal_seeds_not_executed": True,
        "n_logical_runs_planned": 28,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "blockers": [] if phase0_ok else ["PHASE0_STATIC_PRECHECK"],
    }
    dump_json(stop, ART / "E3_CANARY_STOP_STATUS.json")
    print(json.dumps(stop, indent=2))
    return 0 if phase0_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
