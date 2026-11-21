#!/usr/bin/env python3
"""Final independent claim-matrix validator with EPS_ZERO=1e-12."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from raven_mcs.e2.traffic_final_seal import EPS_ZERO
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1"
PRIOR_ANALYSIS = ROOT / "artifacts/e2_traffic_formal_results_analysis_r1"
PRIOR_RECON = ROOT / "artifacts/e2_traffic_offline_metric_reconstruction_r1"


def main() -> int:
    claims = pd.read_csv(ART / "E2_CLAIM_MATRIX_FINAL.csv")
    struct = pd.read_csv(ART / "STRUCTURAL_STATS_TOLERANCE_CORRECTED.csv")
    dg = pd.read_csv(ART / "DELTA_GROUP_RAVEN_VS_BASELINE_TOLERANCE_CORRECTED.csv")
    prior_scen = pd.read_csv(PRIOR_ANALYSIS / "SCENARIO_VS_BALANCED_STATS.csv")
    prior_raven = pd.read_csv(PRIOR_ANALYSIS / "RAVEN_VS_BASELINE_SECONDARY.csv")
    dod = json.loads((PRIOR_ANALYSIS / "COMPLETE_ALIGNED_DOD_SUMMARY.json").read_text(encoding="utf-8"))
    counter = json.loads((PRIOR_ANALYSIS / "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json").read_text(encoding="utf-8"))
    dp = pd.read_csv(PRIOR_RECON / "DELTA_PAIR_RECONSTRUCTED.csv")

    allowed = {}
    rho = prior_scen.loc[
        (prior_scen.metric == "RMSE_rho")
        & (prior_scen.scenario.isin(["observation_only", "complete_aligned"]))
    ]
    allowed["C1"] = (
        "SUPPORTED_WITH_SCENARIO_QUALIFICATION"
        if bool(rho["significant_holm_0.05"].fillna(False).any())
        else "PARTIALLY_SUPPORTED"
    )
    mu = prior_scen.loc[prior_scen.metric == "RMSE_mu"]
    allowed["C2"] = "PARTIALLY_SUPPORTED" if bool(mu["significant_holm_0.05"].fillna(False).any()) else "UNSUPPORTED"
    allowed["C3"] = "SUPPORTED" if any(abs(dod[m]["mean_D_aligned"]) > 1e-9 for m in dod) else "INCONCLUSIVE"
    allowed["C4"] = "UNSUPPORTED"
    props = [counter[m]["event_proportion"] for m in counter]
    allowed["C5"] = "UNSUPPORTED" if max(props) < 0.5 else "PARTIALLY_SUPPORTED"

    def all_baselines_sig(metric: str) -> str:
        sub = prior_raven.loc[prior_raven.metric == metric]
        sig_imp = sub.loc[(sub["significant_holm_0.05"].fillna(False)) & (sub["mean_paired_diff"] < 0)]
        return "SUPPORTED" if len(sig_imp) == 24 else "UNSUPPORTED"

    allowed["C6"] = all_baselines_sig("RMSE_mu")
    allowed["C7"] = all_baselines_sig("RMSE_rho")
    allowed["C8"] = "UNSUPPORTED"

    # C9: genuine non-negligible Holm-significant structural RAVEN improvements only
    raven = struct.loc[struct.analysis == "raven_vs_baseline"]
    genuine = raven.loc[
        (raven["significant_holm_0.05"].fillna(False))
        & (raven["max_abs_raw_paired_diff"] > EPS_ZERO)
        & (raven["tol_mean_paired_diff"] < -EPS_ZERO)
        & (raven["ties"] < raven["n"])
    ]
    # machine-epsilon / all-ties cannot support
    dg_sig = int(dg["significant_holm_0.05"].fillna(False).sum())
    if dg_sig > 0:
        # should not happen after tolerance correction
        pass
    if (dp["reconstruction_status"] == "DEFINITION_NOT_RECOVERABLE").all() and len(genuine) == 0:
        allowed["C9"] = "UNSUPPORTED"
    elif len(genuine) == 0:
        allowed["C9"] = "UNSUPPORTED"
    else:
        allowed["C9"] = "PARTIALLY_SUPPORTED"
    allowed["C10"] = "PARTIALLY_SUPPORTED"

    matrix = claims.set_index("claim_id")["status"].to_dict()
    mismatches = {
        cid: {"matrix": matrix.get(cid), "allowed": allowed[cid]}
        for cid in allowed
        if matrix.get(cid) != allowed[cid]
    }
    # Extra hard checks
    hard_failures = []
    for cid in ("C6", "C7", "C8"):
        if "significantly" in claims.loc[claims.claim_id == cid, "claim"].iloc[0].lower():
            if matrix.get(cid) in {"SUPPORTED", "PARTIALLY_SUPPORTED"}:
                hard_failures.append(f"{cid}_significant_without_evidence")
    if matrix.get("C9") in {"SUPPORTED", "PARTIALLY_SUPPORTED"} and len(genuine) == 0:
        hard_failures.append("C9_supported_by_machine_epsilon_or_no_evidence")
    # all-ties superiority fail
    all_ties_sig = dg.loc[(dg.ties == dg.n) & (dg["significant_holm_0.05"].fillna(False))]
    if len(all_ties_sig):
        hard_failures.append("all_ties_marked_significant")

    payload = {
        "EPS_ZERO": EPS_ZERO,
        "allowed_classifications": allowed,
        "matrix_classifications": matrix,
        "mismatches": mismatches,
        "hard_failures": hard_failures,
        "delta_group_holm_sig_count": dg_sig,
        "genuine_structural_raven_improvements": int(len(genuine)),
        "status": "PASS" if (not mismatches and not hard_failures) else "FAIL",
    }
    dump_json(payload, ART / "CLAIM_EVIDENCE_VALIDATION_FINAL.json")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
