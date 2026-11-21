"""T-Drive readiness audit only (no formal runs)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import read_json, write_csv, write_json, write_text


METHODS = [
    "FedAvg-Window",
    "FedAsync-Window",
    "TimeAlign-Agg",
    "TwoStage-Hajek",
    "RAVEN-MCS",
]


def audit_tdrive(root: Path, paper: Path) -> dict[str, Any]:
    root = Path(root)
    out = paper / "08_tdrive_readiness"
    out.mkdir(parents=True, exist_ok=True)

    checks = {
        "raw_trajectory": (root / "data" / "raw" / "tdrive_speed").exists(),
        "checksum_manifest": (root / "data" / "manifests" / "tdrive_speed_manifest.json").is_file(),
        "adapter_or_config": (root / "configs" / "dataset" / "tdrive_speed.yaml").is_file(),
        "preprocessing_processed": (root / "data" / "processed" / "tdrive_speed").exists(),
        "atomic_units": (root / "data" / "processed" / "tdrive_speed" / "atomic_units.parquet").is_file(),
        "client_measurements": (
            root / "data" / "processed" / "tdrive_speed" / "client_measurements.parquet"
        ).is_file(),
        "interim": (root / "data" / "interim" / "tdrive_speed").exists(),
        "experiment_config_e9": (root / "configs" / "experiment" / "E9_tdrive.yaml").is_file(),
    }

    inventory = []
    for name, ok in checks.items():
        path = ""
        if name == "raw_trajectory":
            path = "data/raw/tdrive_speed"
        elif name == "checksum_manifest":
            path = "data/manifests/tdrive_speed_manifest.json"
        elif name == "adapter_or_config":
            path = "configs/dataset/tdrive_speed.yaml"
        elif name == "preprocessing_processed":
            path = "data/processed/tdrive_speed"
        elif name == "atomic_units":
            path = "data/processed/tdrive_speed/atomic_units.parquet"
        elif name == "client_measurements":
            path = "data/processed/tdrive_speed/client_measurements.parquet"
        elif name == "interim":
            path = "data/interim/tdrive_speed"
        elif name == "experiment_config_e9":
            path = "configs/experiment/E9_tdrive.yaml"
        inventory.append(
            {
                "item": name,
                "present": ok,
                "path": path,
                "notes": "",
            }
        )

    # Probe processed contents for readiness depth
    blockers: list[str] = []
    if not checks["raw_trajectory"]:
        blockers.append("Missing raw T-Drive trajectory directory")
    if not checks["checksum_manifest"]:
        blockers.append("Missing T-Drive checksum manifest")
    if not checks["atomic_units"] or not checks["client_measurements"]:
        blockers.append("Processed T-Drive artifacts incomplete")

    # Method compatibility: code exists in aggregation methods for E3/E4 methods
    method_rows = []
    methods_py = root / "src" / "raven_mcs" / "aggregation" / "methods.py"
    methods_txt = methods_py.read_text(encoding="utf-8") if methods_py.is_file() else ""
    for m in METHODS:
        token = {
            "FedAvg-Window": "fedavg",
            "FedAsync-Window": "fedasync",
            "TimeAlign-Agg": "timealign",
            "TwoStage-Hajek": "twostage",
            "RAVEN-MCS": "raven",
        }[m]
        present = token in methods_txt.lower()
        method_rows.append(
            {
                "method": m,
                "implementation_present": present,
                "metric_schema_compatible_with_e3_e4": "LIKELY" if present else "UNKNOWN",
                "notes": "No T-Drive formal runs authorized this round",
            }
        )
    if not all(r["implementation_present"] for r in method_rows):
        blockers.append("One or more required methods missing in aggregation/methods.py")

    # Frozen EventTrace / split / formal readiness — typically missing for T-Drive
    advanced = {
        "speed_target_construction": checks["atomic_units"],
        "spatial_grid": False,
        "time_slot": False,
        "opportunity_definition": False,
        "client_assignment": checks["client_measurements"],
        "eventtrace_generation": False,
        "train_val_test_split_frozen": False,
        "seed_handling_frozen": False,
        "validation_only_tuning_artifacts": False,
        "frozen_formal_config": checks["experiment_config_e9"],
        "formal_tdrive_runs_started": False,
    }
    for k, v in advanced.items():
        inventory.append({"item": k, "present": v, "path": "", "notes": "readiness probe"})
        if k in {
            "eventtrace_generation",
            "train_val_test_split_frozen",
            "opportunity_definition",
        } and not v:
            blockers.append(f"Not ready: {k}")

    # Determine status
    if blockers:
        # Prefer most specific
        if not checks["raw_trajectory"] or not checks["checksum_manifest"]:
            status = "NOT_READY_MISSING_DATA"
        elif not checks["atomic_units"]:
            status = "NOT_READY_PREPROCESSING_UNFROZEN"
        else:
            status = "NOT_READY_OTHER"
    else:
        status = "READY_FOR_SEPARATE_50_RUN_AUTHORIZATION"

    # Even with data present, EventTrace/split freeze absence => not ready
    if status == "READY_FOR_SEPARATE_50_RUN_AUTHORIZATION":
        # unreachable currently due to advanced False flags
        pass
    if any(
        not advanced[k]
        for k in ("eventtrace_generation", "train_val_test_split_frozen", "opportunity_definition")
    ):
        status = "NOT_READY_OTHER"
        if "EventTrace / split / opportunity freeze incomplete" not in blockers:
            blockers.append("EventTrace / split / opportunity freeze incomplete")

    write_csv(out / "TDRIVE_DATASET_INVENTORY.csv", inventory)
    write_csv(out / "TDRIVE_METHOD_COMPATIBILITY.csv", method_rows)
    write_text(
        out / "TDRIVE_PREPROCESSING_AUDIT.md",
        "\n".join(
            [
                "# T-Drive preprocessing audit",
                "",
                f"- Raw present: {checks['raw_trajectory']}",
                f"- Manifest present: {checks['checksum_manifest']}",
                f"- Processed atomic_units: {checks['atomic_units']}",
                f"- Processed client_measurements: {checks['client_measurements']}",
                f"- Config: {checks['adapter_or_config']}",
                "",
                "This round does **not** authorize T-Drive formal runs.",
                "",
            ]
        ),
    )
    write_text(
        out / "TDRIVE_BLOCKERS.md",
        "\n".join(["# T-Drive blockers", ""] + [f"- {b}" for b in blockers] + [""]),
    )
    readiness = {
        "status": status,
        "formal_tdrive_runs_authorized": False,
        "formal_tdrive_runs_started": False,
        "blockers": blockers,
        "checks": checks,
        "advanced": advanced,
        "minimal_50_run_ready": status == "READY_FOR_SEPARATE_50_RUN_AUTHORIZATION",
    }
    write_json(out / "TDRIVE_MINIMAL_50_RUN_READINESS.json", readiness)

    # Manifest checksum note
    man = root / "data" / "manifests" / "tdrive_speed_manifest.json"
    if man.is_file():
        try:
            write_json(out / "TDRIVE_MANIFEST_SNAPSHOT.json", read_json(man))
        except Exception as exc:  # noqa: BLE001
            write_json(out / "TDRIVE_MANIFEST_SNAPSHOT.json", {"error": str(exc)})

    return readiness
