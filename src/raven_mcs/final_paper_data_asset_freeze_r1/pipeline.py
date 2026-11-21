"""Final paper data asset freeze R1 orchestrator. No experiments."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import write_json
from raven_mcs.final_paper_data_asset_freeze_r1.catalog import build_catalog, build_indices
from raven_mcs.final_paper_data_asset_freeze_r1.collect import collect_all
from raven_mcs.final_paper_data_asset_freeze_r1.constants import OUT_DIR, ROUND, STATUSES
from raven_mcs.final_paper_data_asset_freeze_r1.gates import run_gates
from raven_mcs.final_paper_data_asset_freeze_r1.libraries import build_libraries
from raven_mcs.final_paper_data_asset_freeze_r1.masters import build_run_masters, build_statistics_and_metadata
from raven_mcs.final_paper_data_asset_freeze_r1.package import package
from raven_mcs.final_paper_data_asset_freeze_r1.reports import build_audits, write_handoff_and_report


def run(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or Path(__file__).resolve().parents[3])
    out = root / OUT_DIR
    r2 = root / "paper_ready_r2"
    mec = root / "manuscript_evidence_closure_r1"
    out.mkdir(parents=True, exist_ok=True)

    collect_all(root, out)
    counts = build_run_masters(r2, out)
    build_statistics_and_metadata(r2, mec, out)
    build_libraries(root, r2, mec, out)
    build_indices(out, r2)
    build_catalog(out, root)
    audits = build_audits(r2, out, counts)

    status_code, status_name = "B", STATUSES["B"]
    if audits.get("n_conflict"):
        status_code, status_name = "C", STATUSES["C"]
    elif audits.get("core_missing"):
        status_code, status_name = "E", STATUSES["E"]

    write_json(
        out / "22_REPORTS/PIPELINE_META.json",
        {"round": ROUND, "created_utc": datetime.now(timezone.utc).isoformat(), "counts": counts, "audits": {k: v for k, v in audits.items() if k != "observed"}},
    )
    write_handoff_and_report(out, status_code, status_name, counts, audits, {"core_zip": "", "full_zip": "", "core_pass": False, "full_pass": False, "n_core": 0, "n_full": 0})
    pkg = package(root, out)
    write_handoff_and_report(out, status_code, status_name, counts, audits, pkg)
    pkg = package(root, out)
    gates = run_gates(root, out)
    if not gates.get("all_pass") and status_code in {"A", "B"}:
        status_code, status_name = "D", STATUSES["D"]
        write_handoff_and_report(out, status_code, status_name, counts, audits, pkg)
        pkg = package(root, out)
        gates = run_gates(root, out)
    write_json(out / "22_REPORTS/FINAL_STATUS.json", {"status_code": status_code, "status": status_name, "gates_all_pass": gates.get("all_pass"), "tdrive": "REVIEWER_RESERVE"})
    return {
        "status": status_name,
        "status_code": status_code,
        "gates": gates,
        "package": pkg,
        "counts": counts,
        "all_gates_pass": bool(gates.get("all_pass")),
    }


if __name__ == "__main__":
    result = run()
    print(result["status"], result["gates"].get("n_pass"), "/", result["gates"].get("n_total"))
    raise SystemExit(0 if result["all_gates_pass"] else 1)
