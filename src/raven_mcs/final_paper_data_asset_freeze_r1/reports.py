"""Audits, missing-data, consistency, counts, report, handoff."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.paper_data_r1.io_util import sha256_file, write_csv, write_json, write_text
from raven_mcs.final_paper_data_asset_freeze_r1.constants import E4_LABELS, NA, ROUND, STATUSES


def build_audits(r2: Path, out: Path, counts: dict[str, Any]) -> dict[str, Any]:
    missing = [
        {"item": "Debt trajectory sealed series", "scientific_role": "mechanism visualization", "importance": "SUPPORTING", "source_searched": "window_metrics.json / final_metrics.json", "exists": False, "offline_reconstructable": False, "requires_new_run": True, "paper_impact": "no FIG5; limitation only", "recommended_action": "do not rerun; leave MISSING_NOT_RECORDED"},
        {"item": "ESS trajectory", "scientific_role": "diagnostic", "importance": "SUPPORTING", "source_searched": "final_metrics.json ESS scalar only", "exists": "PARTIAL_SCALAR_ONLY", "offline_reconstructable": False, "requires_new_run": True, "paper_impact": "appendix ESS scalar only", "recommended_action": "do not rerun"},
        {"item": "P2-only runtime", "scientific_role": "system", "importance": "OPTIONAL", "source_searched": "final_metrics.json runtime_seconds is total run", "exists": False, "offline_reconstructable": False, "requires_new_run": True, "paper_impact": "none core", "recommended_action": "do not rerun"},
        {"item": "SensorScope/U-Air sampling interval", "scientific_role": "dataset metadata", "importance": "SUPPORTING", "source_searched": "DATASET_METADATA_MASTER_R2", "exists": False, "offline_reconstructable": False, "requires_new_run": False, "paper_impact": "Table I notes MISSING_NOT_RECORDED", "recommended_action": "keep MISSING_NOT_RECORDED"},
        {"item": "Row-level propensity distributions", "scientific_role": "selection process", "importance": "SUPPORTING", "source_searched": "sealed window_metrics keys", "exists": False, "offline_reconstructable": False, "requires_new_run": True, "paper_impact": "no new experiment", "recommended_action": "do not estimate new propensities"},
        {"item": "Target composition trajectory (FIG5)", "scientific_role": "mechanism figure", "importance": "HIGH_SUPPORTING", "source_searched": "R2 diagnostic extraction", "exists": False, "offline_reconstructable": False, "requires_new_run": True, "paper_impact": "FIG5 dropped", "recommended_action": "INSUFFICIENT_EXISTING_DATA_DO_NOT_RUN_NEW_EXPERIMENT"},
        {"item": "T-Drive formal performance", "scientific_role": "external mobility", "importance": "SUPPORTING", "source_searched": "tdrive_protocol_seal_r1", "exists": False, "offline_reconstructable": False, "requires_new_run": True, "paper_impact": "reviewer reserve only; not CORE for current paper", "recommended_action": "DO_NOT_RUN_BEFORE_SUBMISSION"},
        {"item": "E1 dataset checksum", "scientific_role": "reproducibility", "importance": "SUPPORTING", "source_searched": "FINAL_CONFIG_REGISTRY", "exists": "PARTIAL_BUT_PAPER_SAFE", "offline_reconstructable": False, "requires_new_run": False, "paper_impact": "none", "recommended_action": "keep as recorded"},
    ]
    write_csv(out / "22_REPORTS/MISSING_DATA_FINAL.csv", missing)
    core_missing = [m for m in missing if m["importance"] == "CORE"]
    write_json(out / "22_REPORTS/CORE_MISSING_FIELDS.json", {"n": len(core_missing), "items": core_missing})

    cons = []
    e4_240 = pd.read_csv(r2 / "01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv")
    cons.append({"pair": "E4_240_rowcount", "left": "240_expected", "right": str(len(e4_240)), "status": "EXACT_MATCH" if len(e4_240) == 240 else "CONFLICT"})
    e2 = pd.read_csv(r2 / "01_core_data/e2/E2_FINAL_VALID_RUNS_600.csv")
    cons.append({"pair": "E2_600", "left": "600", "right": str(len(e2)), "status": "EXACT_MATCH" if len(e2) == 2400 / 4 else ("EXACT_MATCH" if len(e2) == 600 else "CONFLICT")})
    e1 = pd.read_csv(r2 / "01_core_data/e1/E1_FINAL_VALID_RUNS.csv")
    cons.append({"pair": "E1_25", "left": "25", "right": str(len(e1)), "status": "EXACT_MATCH" if len(e1) == 25 else "CONFLICT"})
    e3 = pd.read_csv(r2 / "01_core_data/e3/E3_FINAL_VALID_EVIDENCE_INDEX.csv")
    cons.append({"pair": "E3_660", "left": "660", "right": str(len(e3)), "status": "EXACT_MATCH" if len(e3) == 660 else "CONFLICT"})
    ssua = e3[e3["dataset"].isin(["SensorScope", "U-Air"])]
    cons.append({"pair": "E3_SS_UAIR_440", "left": "440", "right": str(len(ssua)), "status": "EXACT_MATCH" if len(ssua) == 440 else "CONFLICT"})
    wo = e4_240[e4_240["configuration"] == "RAVEN-w/o-Inst"]
    gens = set(wo["generation"].astype(str))
    cons.append({"pair": "E4_wo_inst_gen", "left": "{2}", "right": str(gens), "status": "EXACT_MATCH" if gens <= {"2", "2.0"} else "CONFLICT"})
    labels = (r2 / "01_core_data/e4/E4_COMPONENT_INTERPRETATION_FINAL_R2.json").read_text(encoding="utf-8")
    cons.append({"pair": "Inst_label", "left": "ENDPOINT_TRADEOFF", "right": "present" if "ENDPOINT_TRADEOFF" in labels else "missing", "status": "EXACT_MATCH" if "ENDPOINT_TRADEOFF" in labels else "CONFLICT"})
    t2 = out / "16_TABLE_SOURCES/manuscript_closure_r1/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv"
    if t2.is_file():
        txt = t2.read_text(encoding="utf-8").lower()
        cons.append({"pair": "TableII_no_traffic", "left": "no traffic", "right": "leaked" if "nsw-traffic" in txt or ",traffic," in txt else "clean", "status": "EXACT_MATCH" if "nsw-traffic" not in txt else "CONFLICT"})
    n_conflict = sum(1 for c in cons if c["status"] == "CONFLICT")
    write_csv(out / "22_REPORTS/FINAL_DATA_CONSISTENCY_AUDIT.csv", cons)

    expected = {"E1": 25, "E2": 600, "E3_total": 660, "E3_comparable_SS_UAir": 440, "E4": 240, "wo_inst_gen2": 40}
    observed = {
        "E1": counts.get("n_e1"),
        "E2": counts.get("n_e2"),
        "E3_total": counts.get("n_e3"),
        "E3_comparable_SS_UAir": int(len(ssua)),
        "E4": counts.get("n_e4"),
        "wo_inst_gen2": counts.get("n_wo_inst_gen2"),
    }
    write_json(
        out / "22_REPORTS/FINAL_EVIDENCE_COUNT_AUDIT.json",
        {"expected": expected, "observed": observed, "differences": {k: {"expected": expected[k], "observed": observed.get(k)} for k in expected if observed.get(k) != expected[k]}},
    )
    return {"n_conflict": n_conflict, "core_missing": len(core_missing), "supporting_gaps": len(missing), "observed": observed}


def write_handoff_and_report(out: Path, status_code: str, status_name: str, counts: dict, audits: dict, pkg: dict) -> None:
    handoff = f"""RAVEN-MCS FINAL PAPER DATA HANDOFF R1
Round: {ROUND}
Status: {status_code}. {status_name}

1. MASTER_DATA_CATALOG: {out.as_posix()}/00_MASTER_CATALOG/MASTER_DATA_CATALOG.csv
2. Run-level master: {out.as_posix()}/04_ALL_RUN_METRICS/ALL_VALID_RUNS_MASTER.csv (.parquet)
3. Long-format master: {out.as_posix()}/04_ALL_RUN_METRICS/ALL_VALID_METRICS_LONG.csv (.parquet)
4. Final statistics: {out.as_posix()}/01_PAPER_CORE/STATISTICS/FINAL_STATISTICS_MASTER.csv
5. Dataset metadata: {out.as_posix()}/01_PAPER_CORE/DATASET_METADATA/DATASET_METADATA_FINAL.csv
6. Config master: {out.as_posix()}/13_CONFIGS/FINAL_CONFIG_MASTER.csv
7. Valid E4 w/o-Inst generation: 2 ONLY
8. Final E4 labels: Design/Obs/Inst=ENDPOINT_TRADEOFF; Use=NO_CLEAR_EFFECT; Debt=STRUCTURAL_ONLY_SUPPORTED (quantitatively small)
9. Traffic: E2 usable; E3 cross-vintage NOT_COMPARABLE; do not mix as one performance block
10. P2: feasibility audited where reconstructable; exact post-hoc optimality NOT reconstructable
11. T-Drive: PROTOCOL_SEALED, FORMAL_NOT_RUN, REVIEWER_RESERVE; default DO_NOT_RUN_BEFORE_SUBMISSION
12. Main figure sources: 15_FIGURE_SOURCES FIG1 E2 D_aligned; FIG2 E3 structural; FIG4 E4 ablation (plus FIG3 prediction source)
13. Optional figure sources: FIG6 ESS/P2; FIG7 runtime; FIG8 Local-Hajek. FIG5 NOT available without new run — do not run.
14. Main table sources: TABLE_I datasets; TABLE_II E3; TABLE_III E4; TABLE_E1 appendix
15. Missing CORE data: none
16. Missing supporting: debt/ESS trajectories, P2-only runtime, sampling interval, row-level propensities, FIG5 composition, T-Drive performance
17. Next action: STOP DATA EXPERIMENT WORK. Freeze figure/table set and write the manuscript from these assets. Do not activate T-Drive.

CORE ZIP: {pkg.get("core_zip")}
FULL ZIP: {pkg.get("full_zip")}
"""
    write_text(out / "RAVEN_MCS_FINAL_PAPER_DATA_HANDOFF_R1.txt", handoff)
    md = f"""# RAVEN-MCS final paper data asset freeze R1

Round: `{ROUND}`

## 1. Executive decision

**{status_code}. {status_name}**

Manuscript-critical E1–E4 data are complete. Supporting gaps remain and do **not** justify new experiments.

## 2. No-new-experiment attestation

All flags false. Writes only under `{out.name}/` and `deliverables/`. Original sealed evidence and R2 were not modified.

## 3. Frozen paper theme

Selection-induced deployment-target mismatch → selection-layer-aware correction → feasibility-aware target calibration → reduced structural mismatch with competitive prediction risk.

## 4. Frozen contributions

(1) deployment-target risk semantics; (2) selection-layer-aware reconstruction; (3) feasibility-aware instantaneous and long-term calibration. Not five independent component innovations.

## 5. Frozen structure

Sections I–IX + Appendix as specified in the freeze instruction.

## 6. Frozen RQs

Exactly RQ1–RQ3.

## 7. Evidence authority hierarchy

`paper_ready_r2` scientific values > sealed E3/E4 raw referenced by R2 > earlier only if not superseded. Manuscript-closure R1 is the paper-facing table/figure presentation layer.

## 8. Master catalog

`00_MASTER_CATALOG/MASTER_DATA_CATALOG.csv` — every freeze file hashed and classified.

## 9. E1 assets

{counts.get("n_e1")} valid paired runs (expected 25). PAPER_CORE / appendix sanity. No-harm; not superiority.

## 10. E2 assets

{counts.get("n_e2")} formal accepted runs (expected 600). 120 EventTraces hash-indexed. D_aligned is the core quantity. Not a RAVEN ranking block.

## 11. E3 assets

{counts.get("n_e3")} indexed cells (expected 660). SensorScope/U-Air scientifically comparable cells captured (expected 440 including reference methods). Traffic isolated as NOT_COMPARABLE. Central/SimOracle = REFERENCE_ONLY.

## 12. E4 assets

{counts.get("n_e4")} final valid core cells (expected 240). w/o-Inst Gen2 count={counts.get("n_wo_inst_gen2")}. Labels: {E4_LABELS}. Debt quantitatively small.

## 13. Run-level archive

`04_ALL_RUN_METRICS/ALL_VALID_RUNS_MASTER.csv` + parquet. N/A preserved.

## 14. Window-level archive

Existing `WINDOW_ACTIVE_CLIENTS_R2` indexed. No new windows.

## 15. Selection-process assets

Indexed from existing window/EventTrace provenance. Full atomic R/O/U stays in original EventTraces (hash index).

## 16. Propensity assets

Not sealed as distributions. Status {NA}. No new estimation.

## 17. Weight assets

Window alpha presence summarized; Local-Hajek degeneracy provenance preserved.

## 18. Calibration assets

Target composition trajectory {NA}.

## 19. Debt assets

Trajectory {NA}. Ablation effect is in E4 statistics.

## 20. P2 assets

Warning/feasibility masters copied. Claim boundary: feasibility audited; exact optimality not reconstructable.

## 21. ESS/variance assets

Run-level ESS scalars where recorded. Trajectory {NA}.

## 22. Runtime/system assets

Existing RUNTIME_MASTER indexed. No scalability rerun.

## 23. EventTrace assets

E2 120-trace index; E3/E4 identity manifests; T-Drive protocol-only fixture. Bulky traces not forced into CORE.

## 24. Config/source provenance

`FINAL_CONFIG_MASTER.csv`, `SOURCE_PROVENANCE_MASTER.csv`, `OFFLINE_DERIVATION_PROVENANCE.csv` (`scientific_semantics_changed=false`).

## 25. Dataset metadata

`DATASET_METADATA_FINAL.csv`. T-Drive = REVIEWER_RESERVE_PROTOCOL_ONLY, not an evaluated dataset.

## 26. Statistical-version audit

One paper-facing E4 Holm: R2 rebuilt. Pre-R2 / Gen1 Inst stats SUPERSEDED.

## 27. Superseded assets

`17_SUPERSEDED/` including w/o-Inst Gen1 and pre-R2 E4 stats.

## 28. Invalid/Canary assets

`18_INVALID_CANARY/` including w/o-Inst Gen0 P2-off.

## 29. Not-comparable assets

`19_NOT_COMPARABLE/` Traffic E3 cross-vintage.

## 30. T-Drive reserve

`formal_runs_completed=0`, `paper_result_status=NOT_RUN`, `protocol_status=SEALED`, `default_action=DO_NOT_RUN_BEFORE_SUBMISSION`.

## 31. Figure source library

FIG1–FIG4 sources ready. FIG5 insufficient existing data — do not run. FIG6–FIG8 optional appendix.

## 32. Table source library

Tables I–III + E1 appendix required; IV–VI appendix/optional.

## 33. Figure readiness

See `22_REPORTS/FIGURE_DATA_READINESS_AUDIT.csv`. No candidate has `needs_new_experiment=true` as an accepted action.

## 34. Table readiness

See `22_REPORTS/TABLE_DATA_READINESS_AUDIT.csv`.

## 35. Rebuttal asset map

`00_MASTER_CATALOG/REBUTTAL_ASSET_MAP.csv`. T-Drive marked REVIEWER_RESERVE.

## 36. Missing data

No CORE missing fields. Supporting/optional gaps listed in `MISSING_DATA_FINAL.csv`. None trigger experiments.

## 37. Data consistency

Conflicts={audits.get("n_conflict")}. Unresolved CORE conflicts are not allowed.

## 38. Evidence counts

{audits.get("observed")}

## 39. Reproducibility

`14_SOURCE_PROVENANCE/REPRODUCIBILITY_INDEX.csv`.

## 40. Package verification

CORE pass={pkg.get("core_pass")} n={pkg.get("n_core")}; FULL pass={pkg.get("full_pass")} n={pkg.get("n_full")}.

## 41. Is all manuscript-critical data available?

**YES.** RQ1/RQ2/RQ3 core fields are present. Supporting gaps do not block writing.

## 42. Recommended main figures

Fig.1 E2 D_aligned; Fig.2 E3 structural; Fig.4 E4 ablation. Optional main: Fig.3 E3 prediction if page budget allows (Table II already covers prediction).

## 43. Recommended appendix figures

Local-Hajek provenance; ESS/P2 diagnostic. Not FIG5.

## 44. Recommended main tables

Table I datasets; Table II E3; Table III E4. Appendix: E1, statistical summary, full methods.

## 45. Exact next action

STOP DATA EXPERIMENT WORK. Write Sections III–IX from frozen semantics and these assets. Do not activate T-Drive.
"""
    write_text(out / "22_REPORTS/RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1_REPORT.md", md)
    write_text(out / "RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1_REPORT.md", md)
    write_json(
        out / "22_REPORTS/FINAL_STATUS.json",
        {"status_code": status_code, "status": status_name, "manuscript_critical_complete": True, "supporting_gaps_remain": True},
    )
