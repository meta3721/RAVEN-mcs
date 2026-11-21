#!/usr/bin/env python3
"""Freeze Path-A2 measured-O train-unit phi. Does not train. Does not use Y."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

OUT = ROOT / "results_path_a_hajek" / "round_v1"
OCC_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o_no2" / "occupancy_units.parquet"
ATOMIC_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o_no2" / "atomic_units.parquet"
INGEST_PATH = OUT / "INGEST_REPORT.json"
SPEC_PATH = ROOT / "post_review" / "PATH_A_HAJEK" / "TARGET_SPEC.json"
REGION_ORDER = ("region0", "region1", "region2", "region3")
ZERO = 0.0


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def compute_phi(occ: pd.DataFrame) -> dict:
    train = occ.loc[occ["split"] == "train"].drop_duplicates("unit_id")
    test = occ.loc[occ["split"] == "test"].drop_duplicates("unit_id")
    n_train = int(len(train))
    n_test = int(len(test))
    if n_train <= 0 or n_test <= 0:
        raise RuntimeError("empty train or test occupancy units")
    shares = test["target_group"].value_counts(normalize=True)
    mu = {r: float(shares.get(r, 0.0)) for r in REGION_ORDER}
    if abs(sum(mu.values()) - 1.0) > 1e-12:
        raise RuntimeError(f"mu does not sum to 1: {mu}")
    if any(v <= ZERO for v in mu.values()):
        raise RuntimeError(f"empty region in test mu: {mu}")
    pi_i = train["target_group"].map(mu).astype(float)
    n_train_zero = int((pi_i <= ZERO).sum())
    phi_train_unit = n_train_zero / n_train
    design_on = bool(n_train_zero == 0)
    scd_method = "raven" if design_on else "raven_wo_design"
    return {
        "n_train_units": n_train,
        "n_train_zero": n_train_zero,
        "phi_train_unit": float(phi_train_unit),
        "n_test_units": n_test,
        "mu": mu,
        "design_on": design_on,
        "scd_method": scd_method,
        "train_full_design_extra": (not design_on),
        "rule": "Design_ON iff phi_train_unit == 0",
        "n_train_o0": int((train["o_observed"].astype(int) == 0).sum()),
        "n_train_o1": int((train["o_observed"].astype(int) == 1).sum()),
    }


def main() -> int:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ingest = json.loads(INGEST_PATH.read_text(encoding="utf-8"))
    if spec.get("status") != "LOCKED":
        raise RuntimeError("TARGET_SPEC is not LOCKED")
    if spec.get("chosen_option") != "A2":
        raise RuntimeError("phi only for locked A2")
    if ingest.get("status") != "INGEST_FROZEN":
        raise RuntimeError(f"ingest status={ingest.get('status')}")
    if ingest.get("p_obs_bernoulli"):
        raise RuntimeError("Bernoulli p_obs must not be on this ingest")
    occ = pd.read_parquet(OCC_PATH)
    occ["unit_id"] = occ["unit_id"].astype(str)
    occ["split"] = occ["split"].astype(str)
    occ["target_group"] = occ["target_group"].astype(str)
    if occ["spatial_id"].astype(str).str.startswith("NYCP").any():
        raise RuntimeError("vehicle/SensorID leaked into spatial_id")
    phi = compute_phi(occ)
    now = datetime.now(timezone.utc).isoformat()
    decision = {
        "experiment_id": spec["experiment_id"],
        "dataset": spec["dataset_id"],
        "status": "PASS",
        "phi_definition": "phi_train_unit on occupancy R=1 units",
        "h_definition": spec["h_definition"],
        "pi_i_tar": "mu_of_region_h_i",
        "mu_split": "test_occupancy_units_region_share_no_Y",
        "mu": phi["mu"],
        "n_train_units": phi["n_train_units"],
        "n_train_zero": phi["n_train_zero"],
        "phi_train_unit": phi["phi_train_unit"],
        "n_test_units": phi["n_test_units"],
        "n_train_o0": phi["n_train_o0"],
        "n_train_o1": phi["n_train_o1"],
        "design_on": phi["design_on"],
        "scd_method": phi["scd_method"],
        "train_full_design_extra": phi["train_full_design_extra"],
        "rule": phi["rule"],
        "gate_unused": True,
        "used_y_or_rmse": False,
        "used_support_compatible": False,
        "data_hash": ingest["data_hash"],
        "occupancy_sha256": sha256_file(OCC_PATH),
        "atomic_sha256": sha256_file(ATOMIC_PATH),
        "frozen_utc": now,
        "git_commit": _git_commit(),
        "note": "Frozen from occupancy-region mu on train R=1 units. Not from labels or RMSE.",
    }
    go = {
        "experiment_id": decision["experiment_id"],
        "copied_from": "PA_PHI_DECISION.json",
        "phi_train_unit": decision["phi_train_unit"],
        "n_train_units": decision["n_train_units"],
        "n_train_zero": decision["n_train_zero"],
        "design_on": decision["design_on"],
        "scd_method": decision["scd_method"],
        "train_full_design_extra": decision["train_full_design_extra"],
        "used_y_or_rmse": False,
        "created_utc": now,
    }
    dump_json(decision, OUT / "PA_PHI_DECISION.json")
    dump_json(go, OUT / "GO.json")
    ingest["phi_run"] = True
    ingest["phi_train_unit"] = phi["phi_train_unit"]
    ingest["n_train_zero"] = phi["n_train_zero"]
    ingest["n_train_units"] = phi["n_train_units"]
    ingest["n_test_units"] = phi["n_test_units"]
    ingest["design_on"] = phi["design_on"]
    ingest["scd_method"] = phi["scd_method"]
    dump_json(ingest, INGEST_PATH)
    print(json.dumps(go, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
