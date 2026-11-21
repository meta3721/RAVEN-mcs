#!/usr/bin/env python3
"""Seal evidence, recompute Inst stats/claims, gates, report, package."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.wo_inst_final.constants import art_path  # noqa: E402
from raven_mcs.e4.wo_inst_final.corrective import write_eventtrace_identity  # noqa: E402
from raven_mcs.e4.wo_inst_final.evidence import (  # noqa: E402
    seal_corrective,
    seal_evidence_r2,
    summarize_inst,
    write_claim_matrix_r3,
    write_e4_to_e5,
    write_evidence_index,
    write_inst_claim,
    write_superseded_provenance,
    write_synthesis,
)
from raven_mcs.e4.wo_inst_final.gates import run_gates, write_hash_manifest  # noqa: E402
from raven_mcs.e4.wo_inst_final.package import (  # noqa: E402
    export_package,
    write_report,
    write_stop_status,
)


def main() -> int:
    art = art_path(ROOT)
    branch = json.loads(
        (art / "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json").read_text(encoding="utf-8")
    )
    b = branch.get("branch")
    if b == "B":
        seal_corrective(ROOT)
        write_eventtrace_identity(ROOT)
    write_superseded_provenance(ROOT)
    index = write_evidence_index(ROOT, b)
    seal_evidence_r2(ROOT, index)
    inst_rows = summarize_inst(ROOT, b)
    inst_claim = write_inst_claim(ROOT, inst_rows)
    claims = write_claim_matrix_r3(ROOT, inst_claim)
    write_synthesis(ROOT, claims)
    write_e4_to_e5(ROOT)

    # provisional report for hash manifest, then gates, then final report/package
    write_report(ROOT, {"pass_count": 0, "total_count": 30, "all_pass": False, "failed": ["pending"]})
    write_hash_manifest(ROOT)
    gates = run_gates(ROOT)
    write_report(ROOT, gates)
    write_hash_manifest(ROOT)
    gates = run_gates(ROOT)
    stop = write_stop_status(ROOT, gates)
    write_report(ROOT, gates)
    write_hash_manifest(ROOT)
    gates = run_gates(ROOT)
    stop = write_stop_status(ROOT, gates)
    zip_path = export_package(ROOT)
    print(
        json.dumps(
            {
                "gates_all_pass": gates.get("all_pass"),
                "failed": gates.get("failed"),
                "stop": stop.get("status"),
                "package": str(zip_path),
            },
            indent=2,
        )
    )
    return 0 if gates.get("all_pass") and stop.get("status") == "E4_CORE_MECHANISM_ABLATION_FINAL_SEALED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
