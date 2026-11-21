#!/usr/bin/env python3
"""Offline prepare: phase0, recovery, branch, design 774 audit, fix regression, freeze."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.wo_inst_final.branch import (  # noqa: E402
    audit_current_wo_inst,
    write_branch_decision,
    write_one_factor_spec,
)
from raven_mcs.e4.wo_inst_final.corrective import (  # noqa: E402
    freeze_corrective_source,
    write_final_one_factor_regression,
)
from raven_mcs.e4.wo_inst_final.design_audit import run_design_774_audit  # noqa: E402
from raven_mcs.e4.wo_inst_final.recovery import (  # noqa: E402
    recover_e3_lambda_beta,
    write_consistency_audit,
    write_p2_parameter_identity,
    write_phase0,
)
from raven_mcs.e4.wo_inst_final.constants import art_path  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402


def main() -> int:
    write_phase0(ROOT)
    recovery = recover_e3_lambda_beta(ROOT)
    consistency = write_consistency_audit(ROOT, recovery)
    write_p2_parameter_identity(ROOT, recovery)
    audit = audit_current_wo_inst(ROOT, recovery)
    write_one_factor_spec(ROOT, recovery)
    branch = write_branch_decision(ROOT, recovery, audit, consistency)
    design = run_design_774_audit(ROOT)

    if branch.get("branch") == "C":
        dump_json(
            {
                "status": "BLOCKED",
                "reason": "E3 lambda_beta not recoverable",
                "authorize_40_final_reruns": False,
            },
            art_path(ROOT) / "E4_PREPARE_STATUS.json",
        )
        print(json.dumps({"branch": "C", "blocked": True}, indent=2))
        return 2

    if design["decision"].get("stop_for_teacher_review"):
        dump_json(
            {
                "status": "BLOCKED",
                "reason": design["decision"]["decision"],
                "authorize_40_final_reruns": False,
            },
            art_path(ROOT) / "E4_PREPARE_STATUS.json",
        )
        print(json.dumps({"design_blocked": True, "decision": design["decision"]}, indent=2))
        return 3

    beta = float(recovery["recovered_lambda_beta"])
    regression = write_final_one_factor_regression(ROOT, beta)
    if not regression.get("passes"):
        dump_json(
            {
                "status": "BLOCKED",
                "reason": "one-factor regression failed",
                "authorize_40_final_reruns": False,
            },
            art_path(ROOT) / "E4_PREPARE_STATUS.json",
        )
        return 4

    authorize = branch.get("branch") == "B"
    if authorize:
        freeze_corrective_source(ROOT, regression)

    dump_json(
        {
            "status": "READY",
            "branch": branch.get("branch"),
            "recovered_lambda_beta": beta,
            "authorize_40_final_reruns": authorize,
            "design_decision": design["decision"]["decision"],
            "design_scope_leakage": design["summary"]["counts"]["scope_leakage"],
            "design_unresolved": design["summary"]["counts"]["unresolved"],
            "regression_passes": True,
        },
        art_path(ROOT) / "E4_PREPARE_STATUS.json",
    )
    print(
        json.dumps(
            {
                "branch": branch.get("branch"),
                "lambda_beta": beta,
                "authorize_40": authorize,
                "design": design["decision"]["decision"],
                "design_rows": design["n_rows"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
