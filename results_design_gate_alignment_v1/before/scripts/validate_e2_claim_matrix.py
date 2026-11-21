#!/usr/bin/env python3
"""Independent claim-matrix validator for E2 offline correction round."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e2_traffic_offline_metric_reconstruction_r1"
PRIOR = ROOT / "artifacts/e2_traffic_formal_results_analysis_r1"


def main() -> int:
    claims = pd.read_csv(ART / "E2_CLAIM_MATRIX.csv")
    prior_scen = pd.read_csv(PRIOR / "SCENARIO_VS_BALANCED_STATS.csv")
    prior_raven = pd.read_csv(PRIOR / "RAVEN_VS_BASELINE_SECONDARY.csv")
    struct_raven = pd.read_csv(ART / "STRUCTURAL_RAVEN_VS_BASELINE_STATS.csv")
    dod = json.loads((PRIOR / "COMPLETE_ALIGNED_DOD_SUMMARY.json").read_text(encoding="utf-8"))
    counter = json.loads((PRIOR / "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json").read_text(encoding="utf-8"))
    dp = pd.read_csv(ART / "DELTA_PAIR_RECONSTRUCTED.csv")

    allowed = {}
    # C1
    rho = prior_scen.loc[
        (prior_scen.metric == "RMSE_rho")
        & (prior_scen.scenario.isin(["observation_only", "complete_aligned"]))
    ]
    allowed["C1"] = "SUPPORTED" if bool(rho["significant_holm_0.05"].fillna(False).any()) else "PARTIALLY_SUPPORTED"
    # C2
    mu = prior_scen.loc[prior_scen.metric == "RMSE_mu"]
    allowed["C2"] = "PARTIALLY_SUPPORTED" if bool(mu["significant_holm_0.05"].fillna(False).any()) else "UNSUPPORTED"
    # C3 from DoD non-zero
    allowed["C3"] = "SUPPORTED" if any(abs(dod[m]["mean_D_aligned"]) > 1e-9 for m in dod) else "INCONCLUSIVE"
    allowed["C4"] = "UNSUPPORTED"
    props = [counter[m]["event_proportion"] for m in counter]
    allowed["C5"] = "UNSUPPORTED" if max(props) < 0.5 else "PARTIALLY_SUPPORTED"
    # C6/C7: "significantly improves ... over all baselines" requires all 24 Holm-significant improvements
    def all_baselines_sig(metric: str) -> str:
        sub = prior_raven.loc[prior_raven.metric == metric]
        sig_imp = sub.loc[(sub["significant_holm_0.05"].fillna(False)) & (sub["mean_paired_diff"] < 0)]
        if len(sig_imp) == len(sub) and len(sub) == 24:
            return "SUPPORTED"
        return "UNSUPPORTED"

    allowed["C6"] = all_baselines_sig("RMSE_mu")
    allowed["C7"] = all_baselines_sig("RMSE_rho")
    # C8
    gap = prior_raven.loc[prior_raven.metric == "Gap_mis"]
    allowed["C8"] = "UNSUPPORTED"  # signed + no ABS_GAP holm advantage in prior round
    # C9
    if (dp["reconstruction_status"] == "DEFINITION_NOT_RECOVERABLE").all() and not np.isfinite(
        struct_raven["p_holm"]
    ).any():
        allowed["C9"] = "NOT_TESTABLE_FROM_FROZEN_OUTPUTS"
    else:
        sig = struct_raven.loc[
            (struct_raven["significant_holm_0.05"].fillna(False)) & (struct_raven["mean_paired_diff"] < 0)
        ]
        allowed["C9"] = "PARTIALLY_SUPPORTED" if len(sig) else "UNSUPPORTED"
    allowed["C10"] = "PARTIALLY_SUPPORTED"

    matrix = claims.set_index("claim_id")["status"].to_dict()
    mismatches = {cid: {"matrix": matrix.get(cid), "allowed": allowed[cid]} for cid in allowed if matrix.get(cid) != allowed[cid]}
    payload = {
        "allowed_classifications": allowed,
        "matrix_classifications": matrix,
        "mismatches": mismatches,
        "status": "PASS" if not mismatches else "FAIL",
    }
    dump_json(payload, ART / "CLAIM_EVIDENCE_VALIDATION.json")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
