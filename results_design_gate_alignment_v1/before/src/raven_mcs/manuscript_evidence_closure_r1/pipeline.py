"""Manuscript evidence closure R1 orchestrator. No experiments."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import ensure_dir, sha256_file, write_csv, write_json, write_text
from raven_mcs.manuscript_evidence_closure_r1.audits import (
    write_audits,
    write_claim_alignment,
    write_completeness_and_quality,
    write_tdrive_decision,
)
from raven_mcs.manuscript_evidence_closure_r1.constants import FORBIDDEN_PHRASES, ROUND, STATUSES
from raven_mcs.manuscript_evidence_closure_r1.figures import fig1, fig2, fig3
from raven_mcs.manuscript_evidence_closure_r1.gates import run_gates
from raven_mcs.manuscript_evidence_closure_r1.package import package_zip
from raven_mcs.manuscript_evidence_closure_r1.prose import write_prose
from raven_mcs.manuscript_evidence_closure_r1.report import write_report
from raven_mcs.manuscript_evidence_closure_r1.tables import table_e1, table_i, table_ii, table_iii


def _scan_forbidden(out: Path) -> list[str]:
    hits = []
    skip_dirs = ("ABSTRACT_RESULT_CEILING", "CLAIM", "GATES", "AUDIT", "LIMITATIONS", "constants", "INTRODUCTION")
    for p in out.rglob("*"):
        if p.suffix.lower() not in {".md", ".tex", ".json", ".csv"}:
            continue
        posix = p.as_posix()
        if any(x in posix for x in skip_dirs):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in FORBIDDEN_PHRASES:
            idx = txt.find(phrase.lower())
            if idx < 0:
                continue
            window = txt[max(0, idx - 120) : idx + 80]
            if any(w in window for w in ("do not", "not claim", "forbidden", "excludes", "without", "no universal")):
                continue
            hits.append(f"{posix}: {phrase}")
    return hits


def write_provenance(root: Path, out: Path) -> None:
    artifacts = [
        {
            "artifact_id": "TABLE_I",
            "paper_role": "Table I datasets",
            "source_csv": "01_table_sources/TABLE_I_DATASETS.csv",
            "original_evidence": "paper_ready_r2/06_table_sources/TABLE_DATASET_SUMMARY_R2.csv",
            "dataset": "SensorScope,U-Air,NSW-Traffic",
            "methods": "n/a",
            "seeds": "n/a",
            "metric": "setup",
            "filters": "T-Drive excluded",
            "aggregation": "projection",
            "test": "n/a",
            "Holm_family": "n/a",
            "claim_ceiling": "setup only",
            "excluded_evidence": "T-Drive evaluated results",
        },
        {
            "artifact_id": "TABLE_II",
            "paper_role": "Table II E3 effectiveness",
            "source_csv": "01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv",
            "original_evidence": "paper_ready_r2/04_statistics/E3_FINAL_STATISTICS.csv",
            "dataset": "SensorScope,U-Air",
            "methods": "primary E3 + reference-only",
            "seeds": "30001-30020",
            "metric": "RMSE_mu,Tail_RMSE,Delta_group,Delta_c_s",
            "filters": "no Traffic E3",
            "aggregation": "mean±std",
            "test": "paired Wilcoxon",
            "Holm_family": "E3 primary RMSE + secondary structural/Tail",
            "claim_ceiling": "C3/C4",
            "excluded_evidence": "E3 Traffic",
        },
        {
            "artifact_id": "TABLE_III",
            "paper_role": "Table III E4 ablation",
            "source_csv": "01_table_sources/TABLE_III_E4_CORE_ABLATION_FINAL.csv",
            "original_evidence": "paper_ready_r2/06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv",
            "dataset": "SensorScope,U-Air",
            "methods": "RAVEN + five w/o-X",
            "seeds": "30001-30020",
            "metric": "Delta_group,Delta_c_s,RMSE_mu,Tail_RMSE",
            "filters": "240 cells; w/o-Inst gen 2",
            "aggregation": "mean±std",
            "test": "paired Wilcoxon+Holm in E4_FINAL_STATISTICS_R2",
            "Holm_family": "per dataset×metric five-component family",
            "claim_ceiling": "C5-C8",
            "excluded_evidence": "superseded w/o-Inst generations",
        },
        {
            "artifact_id": "FIG1",
            "paper_role": "Fig. 1 E2 risk non-interchangeability",
            "source_csv": "03_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.csv",
            "original_evidence": "paper_ready_r2/07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv",
            "dataset": "NSW-Traffic",
            "methods": "five E2 formal",
            "seeds": "30001-30020",
            "metric": "D_aligned",
            "filters": "complete_aligned",
            "aggregation": "seed-level boxplot",
            "test": "sign/direction of D_aligned (E2_D_ALIGNED_SUMMARY)",
            "Holm_family": "n/a for figure",
            "claim_ceiling": "C1/C2; not RAVEN ranking",
            "excluded_evidence": "E3 Traffic",
        },
        {
            "artifact_id": "FIG2",
            "paper_role": "Fig. 2 E3 structural mismatch",
            "source_csv": "03_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.csv",
            "original_evidence": "paper_ready_r2/01_core_data/e3/E3_STRUCTURAL_METRICS_MASTER.csv",
            "dataset": "SensorScope,U-Air",
            "methods": "five baselines + RAVEN",
            "seeds": "30001-30020",
            "metric": "Delta_group,Delta_c_s",
            "filters": "drop missing structural; no Traffic",
            "aggregation": "seed-level boxplot",
            "test": "E3 secondary Holm (table, not stars on figure)",
            "Holm_family": "per dataset×metric vs five baselines",
            "claim_ceiling": "C3",
            "excluded_evidence": "E3 Traffic; Central",
        },
        {
            "artifact_id": "FIG3",
            "paper_role": "Fig. 3 E4 component removal",
            "source_csv": "03_figure_sources/FIG3_E4_COMPONENT_REMOVAL_FINAL.csv",
            "original_evidence": "paper_ready_r2/04_statistics/E4_FINAL_STATISTICS_R2.csv",
            "dataset": "SensorScope,U-Air",
            "methods": "five w/o-X vs RAVEN",
            "seeds": "30001-30020",
            "metric": "relative_change_percent",
            "filters": "240 cells; Inst gen 2",
            "aggregation": "paired relative change",
            "test": "E4 Holm in source CSV (not starred on figure)",
            "Holm_family": "per dataset×metric five-component",
            "claim_ceiling": "C5-C8",
            "excluded_evidence": "old Inst STRUCTURAL_ONLY_SUPPORTED as paper-facing",
        },
    ]
    script = root / "src/raven_mcs/manuscript_evidence_closure_r1/pipeline.py"
    for row in artifacts:
        src = out / row["source_csv"]
        row["source_sha256"] = sha256_file(src) if src.is_file() else ""
        row["script"] = "src/raven_mcs/manuscript_evidence_closure_r1/pipeline.py"
        row["script_sha256"] = sha256_file(script) if script.is_file() else ""
        fig_map = {
            "FIG1": "04_figures/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.pdf",
            "FIG2": "04_figures/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.pdf",
            "FIG3": "04_figures/FIG3_E4_COMPONENT_REMOVAL_FINAL.pdf",
        }
        extra = fig_map.get(row["artifact_id"])
        row["output_hash"] = sha256_file(out / extra) if extra and (out / extra).is_file() else row["source_sha256"]
    write_csv(out / "08_provenance/FINAL_FIGURE_TABLE_PROVENANCE.csv", artifacts)


def run(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or Path(__file__).resolve().parents[3])
    r2 = root / "paper_ready_r2"
    out = root / "manuscript_evidence_closure_r1"
    ensure_dir(out)
    write_json(
        out / "00_audit/MEC_NO_RUN_ATTESTATION.json",
        {
            "round": ROUND,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "training_started": False,
            "formal_runs_started": False,
            "canary_started": False,
            "tdrive_formal_started": False,
            "e1_e2_e3_e4_reruns": 0,
            "r2_unmodified": True,
        },
    )
    write_audits(r2, out)
    table_i(r2, out)
    table_e1(r2, out)
    table_ii(r2, out)
    table_iii(r2, out)
    fig1(r2, out)
    fig2(r2, out)
    fig3(r2, out)
    write_prose(out)
    write_claim_alignment(out)
    tdrive = write_tdrive_decision(out)
    write_completeness_and_quality(out, tdrive)
    write_provenance(root, out)
    write_text(
        out / "08_provenance/R2_SOURCE_IMMUTABILITY.md",
        "R2 `paper_ready_r2/` was read-only in this round. No E1–E4 reruns. No T-Drive runs.\n",
    )
    forbidden_hits = _scan_forbidden(out)
    write_json(out / "07_claim_alignment/FORBIDDEN_PHRASE_SCAN.json", {"hits": forbidden_hits, "n": len(forbidden_hits)})

    status_code = "A"
    status_name = STATUSES["A"]
    if forbidden_hits:
        status_code, status_name = "D", STATUSES["D"]
    if tdrive["decision_code"] == "A":
        status_code, status_name = "B", STATUSES["B"]

    write_json(
        out / "10_report/FINAL_STATUS.json",
        {
            "status_code": status_code,
            "status": status_name,
            "tdrive": tdrive["decision"],
            "experiment_stop": "STOP_ALL_NEW_EXPERIMENTS_WRITE_MANUSCRIPT",
        },
    )
    write_report(out, status_code, status_name, tdrive)
    package_zip(root, out)
    gates = run_gates(root, out)
    if not gates.get("all_pass") and status_code == "A":
        status_code, status_name = "D", STATUSES["D"]
        write_json(
            out / "10_report/FINAL_STATUS.json",
            {
                "status_code": status_code,
                "status": status_name,
                "tdrive": tdrive["decision"],
                "experiment_stop": "STOP_ALL_NEW_EXPERIMENTS_WRITE_MANUSCRIPT",
                "gate_failure": True,
            },
        )
        write_report(out, status_code, status_name, tdrive)
        gates = run_gates(root, out)
    pkg = package_zip(root, out)
    return {
        "status": status_name,
        "status_code": status_code,
        "gates": gates,
        "package": pkg,
        "all_gates_pass": bool(gates.get("all_pass")),
        "tdrive": tdrive["decision"],
    }


if __name__ == "__main__":
    result = run()
    print(result["status"], result["gates"].get("n_pass"), "/", result["gates"].get("n_total"))
    raise SystemExit(0 if result["all_gates_pass"] else 1)
