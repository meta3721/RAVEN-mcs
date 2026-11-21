"""Tombstone invalid prior antithetic / future-suffix certification results."""
from __future__ import annotations

from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def write_prior_tombstone(root: Path | None = None) -> dict:
    root = Path(root or ROOT)
    payload = {
        "prior_package": "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1",
        "prior_certification_level": "CERT-L32",
        "prior_balanced_pass": "5/5",
        "prior_status": "INVALID_DUE_TO_DGP_AND_ANTITHETIC_MAIN_ESTIMATOR",
        "invalid_reason_future_suffix_candidate_pool": True,
        "invalid_reason_calibration_in_event_mass": True,
        "invalid_reason_two_arm_confirmatory_estimator": True,
        "invalid_reason_synthetic_spatial_coordinates": True,
        "must_revalidate_single_arm": True,
        "status": "TOMBSTONED",
    }
    out = root / "outputs/audits/E2_PRIOR_ANTITHETIC_CERTIFICATION_TOMBSTONE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, out)
    return payload
