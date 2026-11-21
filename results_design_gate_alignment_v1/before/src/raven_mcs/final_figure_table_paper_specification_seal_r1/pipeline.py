"""Final figure–table paper specification seal R1. No experiments."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import write_json
from raven_mcs.final_figure_table_paper_specification_seal_r1.alignment import write_alignment_and_sections, write_audits_and_final
from raven_mcs.final_figure_table_paper_specification_seal_r1.constants import (
    OUT_DIR,
    ROUND,
    STATUS_A,
    STATUS_B,
    STATUS_C,
    STATUS_D,
    SUBDIRS,
)
from raven_mcs.final_figure_table_paper_specification_seal_r1.gates import run_gates
from raven_mcs.final_figure_table_paper_specification_seal_r1.package import package
from raven_mcs.final_figure_table_paper_specification_seal_r1.repairs import copy_and_repair
from raven_mcs.final_figure_table_paper_specification_seal_r1.reports import write_report
from raven_mcs.final_figure_table_paper_specification_seal_r1.specs import write_core_specs


def _ensure_tree(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for d in SUBDIRS:
        (out / d).mkdir(parents=True, exist_ok=True)


def _status_from_gates(gates: dict[str, Any]) -> tuple[str, str]:
    if gates.get("all_pass"):
        return "A", STATUS_A
    g = gates.get("gates", {})
    if not g.get("FPS-G50", {}).get("pass", True) or not g.get("FPS-G31", {}).get("pass", True):
        return "B", STATUS_B
    if not g.get("FPS-G35", {}).get("pass", True) or not g.get("FPS-G36", {}).get("pass", True):
        return "C", STATUS_C
    return "D", STATUS_D


def run(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or Path(__file__).resolve().parents[3])
    out = root / OUT_DIR
    _ensure_tree(out)

    repair = copy_and_repair(root, out)
    hashes = repair["hashes"]
    fig6 = repair["fig6"]
    write_core_specs(out, hashes)
    write_alignment_and_sections(out, hashes)
    write_audits_and_final(out, hashes, fig6)
    write_json(
        out / "12_REPORTS/PIPELINE_META.json",
        {"round": ROUND, "created_utc": datetime.now(timezone.utc).isoformat(), "fig6": fig6, "n_hashed_assets": len(hashes)},
    )
    write_report(out, status_code="A", status_name=STATUS_A, hashes=hashes, fig6=fig6, gates=None, pkg=None)
    pkg = package(root, out)
    gates = run_gates(root, out)
    status_code, status_name = _status_from_gates(gates)
    write_report(out, status_code=status_code, status_name=status_name, hashes=hashes, fig6=fig6, gates=gates, pkg=pkg)
    write_json(
        out / "12_REPORTS/FINAL_STATUS.json",
        {"status_code": status_code, "status": status_name, "gates_all_pass": gates.get("all_pass"), "tdrive": "REVIEWER_RESERVE"},
    )
    pkg = package(root, out)
    gates = run_gates(root, out)
    status_code, status_name = _status_from_gates(gates)
    write_report(out, status_code=status_code, status_name=status_name, hashes=hashes, fig6=fig6, gates=gates, pkg=pkg)
    write_json(
        out / "12_REPORTS/FINAL_STATUS.json",
        {"status_code": status_code, "status": status_name, "gates_all_pass": gates.get("all_pass"), "n_pass": gates.get("n_pass"), "n_total": gates.get("n_total"), "tdrive": "REVIEWER_RESERVE"},
    )
    pkg = package(root, out)
    return {
        "status": status_name,
        "status_code": status_code,
        "gates": gates,
        "package": pkg,
        "fig6": fig6,
        "all_gates_pass": bool(gates.get("all_pass")),
    }


if __name__ == "__main__":
    result = run()
    print(result["status"], result["gates"].get("n_pass"), "/", result["gates"].get("n_total"))
    raise SystemExit(0 if result["all_gates_pass"] else 1)
