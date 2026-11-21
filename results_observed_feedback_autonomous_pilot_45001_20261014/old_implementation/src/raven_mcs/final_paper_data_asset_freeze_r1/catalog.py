"""Master catalog, indices, and duplicate map."""

from __future__ import annotations

import hashlib
from pathlib import Path

from raven_mcs.paper_data_r1.io_util import sha256_file, write_csv, write_json
from raven_mcs.final_paper_data_asset_freeze_r1.constants import CATALOG_FIELDS, NA, N_A, ROUND


def _classify(rel: str) -> tuple[str, str, str]:
    p = rel.replace("\\", "/")
    if p.startswith("01_PAPER_CORE/"):
        role = "RQ2_MAIN_EFFECTIVENESS"
        if "/E1/" in p or p.endswith("/E1"):
            role = "RQ1_PROBLEM_EVIDENCE"
        elif "/E2/" in p:
            role = "RQ1_PROBLEM_EVIDENCE"
        elif "/E4/" in p:
            role = "RQ3_MECHANISM"
        elif "DATASET" in p:
            role = "DATASET_SETUP"
        elif "STATISTICS" in p:
            role = "STATISTICAL_SUPPORT"
        elif "CLAIM" in p:
            role = "REPRODUCIBILITY"
        return "PAPER_CORE", role, "STATISTICAL_RESULT" if "STATISTICS" in p else "SOURCE_SNAPSHOT"
    if p.startswith("15_FIGURE_SOURCES/"):
        return "PAPER_CORE", "RQ2_MAIN_EFFECTIVENESS", "FIGURE_SOURCE"
    if p.startswith("16_TABLE_SOURCES/"):
        return "PAPER_CORE", "DATASET_SETUP", "TABLE_SOURCE"
    if p.startswith("19_NOT_COMPARABLE/"):
        return "NOT_COMPARABLE", "NOT_FOR_PAPER", "REPORT"
    if p.startswith("17_SUPERSEDED/"):
        return "SUPERSEDED", "HISTORICAL_ONLY", "REPORT"
    if p.startswith("18_INVALID_CANARY/"):
        return "INVALID", "NOT_FOR_PAPER", "FAILED_OUTPUT"
    if p.startswith("20_TDRIVE_RESERVE/") or "TDRIVE_PROTOCOL_ONLY" in p:
        return "PROVENANCE_ONLY", "REVIEWER_RESERVE", "PROVENANCE_RECORD"
    if p.startswith("12_EVENTTRACES/"):
        return "PAPER_SUPPORTING", "REPRODUCIBILITY", "EVENTTRACE"
    if p.startswith("09_P2_SOLVER/"):
        return "PAPER_SUPPORTING", "THEORY_DIAGNOSTIC", "P2_STATE"
    if p.startswith("07_WEIGHTS/"):
        return "PAPER_SUPPORTING", "STATISTICAL_SUPPORT", "WEIGHT"
    if p.startswith("05_WINDOW_LEVEL/"):
        return "PAPER_SUPPORTING", "SYSTEM_DIAGNOSTIC", "WINDOW_METRIC"
    if p.startswith("11_RUNTIME_SYSTEM/"):
        return "PAPER_SUPPORTING", "SYSTEM_DIAGNOSTIC", "RUNTIME"
    if p.startswith("10_ESS_VARIANCE/"):
        return "PAPER_SUPPORTING", "THEORY_DIAGNOSTIC", "ESS_STATE"
    if p.startswith("08_CALIBRATION_DEBT/"):
        return "PAPER_SUPPORTING", "THEORY_DIAGNOSTIC", "DEBT_STATE"
    if p.startswith("06_SELECTION_PROCESS/"):
        return "PAPER_SUPPORTING", "THEORY_DIAGNOSTIC", "SELECTION_EVENT"
    if p.startswith("13_CONFIGS/"):
        return "PAPER_CORE", "REPRODUCIBILITY", "CONFIG"
    if p.startswith("14_SOURCE_PROVENANCE/"):
        return "PAPER_CORE", "REPRODUCIBILITY", "PROVENANCE_RECORD"
    if p.startswith("04_ALL_RUN_METRICS/"):
        return "PAPER_CORE", "STATISTICAL_SUPPORT", "RUN_METRIC"
    if p.startswith("03_APPENDIX_CANDIDATES/"):
        return "APPENDIX_CANDIDATE", "APPENDIX_ONLY", "SOURCE_SNAPSHOT"
    if p.startswith("02_PAPER_SUPPORTING/"):
        return "PAPER_SUPPORTING", "STATISTICAL_SUPPORT", "REPORT"
    if p.startswith("00_MASTER_CATALOG/") or p.startswith("22_REPORTS/") or p.startswith("21_MANIFESTS/"):
        return "PAPER_CORE", "REPRODUCIBILITY", "MANIFEST"
    return "PAPER_SUPPORTING", "APPENDIX_ONLY", "REPORT"


def build_catalog(out: Path, original_root: Path) -> list[dict]:
    rows = []
    hashes: dict[str, list[str]] = {}
    n = 0
    for p in out.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(out).as_posix()
        if rel.endswith(".zip"):
            continue
        n += 1
        digest = sha256_file(p)
        status, role, obj = _classify(rel)
        asset_id = f"A{n:05d}"
        st = p.stat()
        rec = {k: "" for k in CATALOG_FIELDS}
        rec.update(
            {
                "asset_id": asset_id,
                "relative_asset_path": rel,
                "original_path": rel,
                "filename": p.name,
                "file_type": p.suffix.lower() or "none",
                "size_bytes": st.st_size,
                "sha256": digest,
                "created_or_modified_time": str(st.st_mtime),
                "round": ROUND,
                "dataset": "",
                "scenario": "",
                "method": "",
                "configuration": "",
                "seed": "",
                "seed_range": "",
                "generation": "",
                "granularity": "file",
                "metric_family": "",
                "scientific_object": obj,
                "evidence_status": status,
                "paper_role": role,
                "paper_eligible": status in {"PAPER_CORE", "PAPER_SUPPORTING", "APPENDIX_CANDIDATE", "REFERENCE_ONLY"},
                "appendix_eligible": status in {"PAPER_CORE", "PAPER_SUPPORTING", "APPENDIX_CANDIDATE", "REFERENCE_ONLY"},
                "rebuttal_useful": status in {"PAPER_CORE", "PAPER_SUPPORTING", "NOT_COMPARABLE", "PROVENANCE_ONLY"},
                "source_authority": "paper_ready_r2" if "r2" in rel.lower() or rel.startswith("01_PAPER_CORE") else "freeze_r1",
                "supersedes": "",
                "superseded_by": "E4_R2" if status == "SUPERSEDED" else "",
                "comparability_status": "NOT_COMPARABLE" if status == "NOT_COMPARABLE" else "as_labeled",
                "claim_ids": "",
                "rq_ids": "",
                "figure_candidate": "FIG" in p.name.upper(),
                "table_candidate": "TABLE" in p.name.upper(),
                "provenance_status": "hashed",
                "notes": "",
            }
        )
        if "E1" in rel:
            rec["dataset"] = "Balanced"
            rec["seed_range"] = "28001-28005"
            rec["rq_ids"] = "RQ1"
        if "E2" in rel:
            rec["dataset"] = "NSW-Traffic"
            rec["seed_range"] = "30001-30020"
            rec["rq_ids"] = "RQ1"
        if "/E3/" in rel or "e3" in rel.lower():
            rec["seed_range"] = "30001-30020"
            rec["rq_ids"] = "RQ2"
        if "/E4/" in rel or "e4" in rel.lower():
            rec["seed_range"] = "30001-30020"
            rec["rq_ids"] = "RQ3"
            if "gen0" in rel:
                rec["generation"] = "0"
            elif "gen1" in rel:
                rec["generation"] = "1"
            elif "gen2" in rel:
                rec["generation"] = "2"
        rows.append(rec)
        hashes.setdefault(digest, []).append(rel)

    # Pointer rows for bulky EventTraces not copied into CORE
    et = original_root / "paper_ready_r2/05_provenance/E2_EVENTTRACE_INDEX_120.csv"
    if et.is_file():
        import csv as _csv

        with et.open(encoding="utf-8", newline="") as f:
            for i, r in enumerate(_csv.DictReader(f), start=1):
                n += 1
                rec = {k: "" for k in CATALOG_FIELDS}
                rec.update(
                    {
                        "asset_id": f"ET{i:03d}",
                        "relative_asset_path": r.get("source_path", ""),
                        "original_path": r.get("source_path", ""),
                        "filename": Path(r.get("source_path", "eventtrace")).name,
                        "file_type": "eventtrace",
                        "size_bytes": r.get("size") or 0,
                        "sha256": r.get("EventTrace_hash", ""),
                        "created_or_modified_time": "",
                        "round": "E2",
                        "dataset": r.get("dataset", "NSW-Traffic"),
                        "scenario": r.get("scenario", ""),
                        "method": "shared",
                        "configuration": "",
                        "seed": r.get("seed", ""),
                        "seed_range": "30001-30020",
                        "generation": N_A,
                        "granularity": "eventtrace",
                        "metric_family": "",
                        "scientific_object": "EVENTTRACE",
                        "evidence_status": "PAPER_SUPPORTING",
                        "paper_role": "REPRODUCIBILITY",
                        "paper_eligible": False,
                        "appendix_eligible": True,
                        "rebuttal_useful": True,
                        "source_authority": "paper_ready_r2",
                        "supersedes": "",
                        "superseded_by": "",
                        "comparability_status": "SCI_COMPARABLE_MAIN",
                        "claim_ids": "C1,C2",
                        "rq_ids": "RQ1",
                        "figure_candidate": False,
                        "table_candidate": False,
                        "provenance_status": "hash_index_only_not_in_CORE",
                        "notes": r.get("notes", ""),
                    }
                )
                rows.append(rec)

    write_csv(out / "00_MASTER_CATALOG/MASTER_DATA_CATALOG.csv", rows, fieldnames=CATALOG_FIELDS)
    write_json(out / "00_MASTER_CATALOG/MASTER_DATA_CATALOG.json", {"n": len(rows), "round": ROUND, "rows": rows})
    dup_rows = []
    for digest, paths in hashes.items():
        if len(paths) < 2:
            continue
        canon = sorted(paths)[0]
        for dpath in paths[1:]:
            dup_rows.append(
                {
                    "canonical_asset_id": canon,
                    "duplicate_path": dpath,
                    "same_sha256": digest,
                    "reason_kept_or_omitted": "kept both copies in classified folders; originals never deleted",
                }
            )
    write_csv(out / "21_MANIFESTS/DUPLICATE_ASSET_MAP.csv", dup_rows or [{"canonical_asset_id": "", "duplicate_path": "", "same_sha256": "", "reason_kept_or_omitted": "no intra-freeze duplicates"}])
    return rows


def build_indices(out: Path, r2: Path) -> None:
    def index_dir(folder: Path, dest: Path, extra: dict | None = None) -> None:
        rows = []
        if folder.is_dir():
            for p in folder.rglob("*"):
                if p.is_file():
                    rec = {
                        "relative_path": p.relative_to(out).as_posix(),
                        "filename": p.name,
                        "size_bytes": p.stat().st_size,
                        "sha256": sha256_file(p),
                        "status": "EXISTING",
                    }
                    if extra:
                        rec.update(extra)
                    rows.append(rec)
        if not rows:
            rows = [{"relative_path": "", "filename": "", "size_bytes": 0, "sha256": "", "status": NA}]
        write_csv(dest, rows)

    index_dir(out / "05_WINDOW_LEVEL", out / "05_WINDOW_LEVEL/WINDOW_LEVEL_ASSET_INDEX.csv")
    index_dir(out / "06_SELECTION_PROCESS", out / "06_SELECTION_PROCESS/SELECTION_PROCESS_ASSET_INDEX.csv")
    index_dir(out / "06_SELECTION_PROCESS/propensity", out / "06_SELECTION_PROCESS/PROPENSITY_ASSET_INDEX.csv")
    index_dir(out / "07_WEIGHTS", out / "07_WEIGHTS/WEIGHT_ASSET_INDEX.csv")
    win = r2 / "02_supporting_data/diagnostics_r2/WINDOW_ACTIVE_CLIENTS_R2.csv"
    wrows = []
    if win.is_file():
        import pandas as pd

        df = pd.read_csv(win)
        if "has_alpha" in df.columns:
            wrows.append({"summary": "window_alpha_present_count", "value": int(df["has_alpha"].fillna(0).astype(int).sum()), "source": str(win), "note": "deterministic count; not a new weight model"})
        wrows.append({"summary": "n_window_rows", "value": len(df), "source": str(win), "note": "existing sealed window rows"})
    write_csv(out / "07_WEIGHTS/WEIGHT_SUMMARY_EXISTING.csv", wrows or [{"summary": "none", "value": NA, "source": "", "note": NA}])
    write_csv(out / "06_SELECTION_PROCESS/SELECTION_PROCESS_MASTER.csv", wrows or [{"summary": "window_active_clients_only", "value": NA, "source": str(win), "note": "full R/O/U row-level not copied; see EventTrace hash index"}])
    index_dir(out / "08_CALIBRATION_DEBT/calibration", out / "08_CALIBRATION_DEBT/CALIBRATION_ASSET_INDEX.csv")
    index_dir(out / "08_CALIBRATION_DEBT/debt", out / "08_CALIBRATION_DEBT/DEBT_ASSET_INDEX.csv")
    index_dir(out / "09_P2_SOLVER", out / "09_P2_SOLVER/P2_ASSET_INDEX.csv")
    p2w = r2 / "02_supporting_data/solver/P2_WARNING_WINDOWS.csv"
    p2f = r2 / "02_supporting_data/solver/P2_FEASIBILITY_SUMMARY.csv"
    if p2w.is_file():
        import shutil

        shutil.copy2(p2w, out / "09_P2_SOLVER/P2_WARNING_MASTER.csv")
    else:
        write_csv(out / "09_P2_SOLVER/P2_WARNING_MASTER.csv", [{"status": NA}])
    if p2f.is_file():
        import shutil

        shutil.copy2(p2f, out / "09_P2_SOLVER/P2_FEASIBILITY_MASTER.csv")
    else:
        write_csv(out / "09_P2_SOLVER/P2_FEASIBILITY_MASTER.csv", [{"status": NA}])
    index_dir(out / "10_ESS_VARIANCE", out / "10_ESS_VARIANCE/ESS_VARIANCE_ASSET_INDEX.csv")
    scalars = r2 / "02_supporting_data/diagnostics_r2/RUNLEVEL_SEALED_SCALARS_R2.csv"
    if scalars.is_file():
        import pandas as pd
        import shutil

        shutil.copy2(scalars, out / "10_ESS_VARIANCE/ESS_VARIANCE_SUMMARY_EXISTING.csv")
    else:
        write_csv(out / "10_ESS_VARIANCE/ESS_VARIANCE_SUMMARY_EXISTING.csv", [{"ESS": NA}])
    index_dir(out / "11_RUNTIME_SYSTEM", out / "11_RUNTIME_SYSTEM/RUNTIME_SYSTEM_ASSET_INDEX.csv")
    rt = r2 / "02_supporting_data/runtime/RUNTIME_MASTER.csv"
    if rt.is_file():
        import shutil

        shutil.copy2(rt, out / "11_RUNTIME_SYSTEM/RUNTIME_SUMMARY_EXISTING.csv")
    else:
        write_csv(out / "11_RUNTIME_SYSTEM/RUNTIME_SUMMARY_EXISTING.csv", [{"runtime": NA}])
    et_rows = []
    for sub, ds in [("E2", "NSW-Traffic"), ("E3", "SensorScope/U-Air"), ("E4", "SensorScope/U-Air"), ("TDRIVE_PROTOCOL_ONLY", "T-Drive")]:
        folder = out / "12_EVENTTRACES" / sub
        if not folder.is_dir():
            continue
        for p in folder.rglob("*"):
            if p.is_file():
                et_rows.append(
                    {
                        "dataset": ds,
                        "scenario": sub,
                        "seed": "",
                        "row_count": NA,
                        "schema": p.suffix,
                        "sha256": sha256_file(p),
                        "used_by_methods": "shared",
                        "evidence_status": "PROVENANCE_ONLY" if "TDRIVE" in sub else "PAPER_SUPPORTING",
                        "path": p.relative_to(out).as_posix(),
                    }
                )
    write_csv(out / "12_EVENTTRACES/EVENTTRACE_MASTER_INDEX.csv", et_rows)
    nc = [
        {
            "asset": "E3 Traffic cross-vintage",
            "reason": "reused-old vs new-current EventTrace/preprocessing vintage",
            "scientific_validity": "valid as archived runs",
            "why_not_comparable": "NOT_COMPARABLE_CROSS_VINTAGE",
            "allowed_use": "limitation / provenance only",
            "forbidden_use": "homogeneous E3 performance table or three-dataset superiority",
        }
    ]
    write_csv(out / "19_NOT_COMPARABLE/NOT_COMPARABLE_MASTER.csv", nc)
    write_csv(
        out / "17_SUPERSEDED/SUPERSEDED_MASTER.csv",
        [
            {"asset": "E4 w/o-Inst Generation 1", "reason": "reference-penalty mismatch", "replaced_by": "Generation 2"},
            {"asset": "pre-R2 E4_FINAL_STATISTICS.csv", "reason": "rebuilt Holm in R2", "replaced_by": "E4_FINAL_STATISTICS_R2.csv"},
        ],
    )
    write_csv(
        out / "18_INVALID_CANARY/INVALID_CANARY_MASTER.csv",
        [{"asset": "E4 w/o-Inst Generation 0", "reason": "P2-off; not a one-factor Inst ablation", "paper_use": "not paper evidence"}],
    )
    write_csv(
        out / "14_SOURCE_PROVENANCE/SOURCE_PROVENANCE_MASTER.csv",
        [
            {"item": "paper_ready_r2", "role": "scientific value authority", "path": "paper_ready_r2/", "hash_policy": "per-file in catalog"},
            {"item": "manuscript_evidence_closure_r1", "role": "paper-facing table/figure presentation", "path": "manuscript_evidence_closure_r1/", "hash_policy": "copied into 15/16"},
            {"item": "tdrive_protocol_seal_r1", "role": "reviewer reserve protocol", "path": "tdrive_protocol_seal_r1/", "hash_policy": "copied into 20_TDRIVE_RESERVE"},
            {"item": "this freeze pipeline", "role": "offline packaging", "path": "src/raven_mcs/final_paper_data_asset_freeze_r1/", "hash_policy": "script hash in derivation log"},
        ],
    )
    write_csv(
        out / "14_SOURCE_PROVENANCE/OFFLINE_DERIVATION_PROVENANCE.csv",
        [
            {
                "derived_asset_id": "ALL_VALID_RUNS_MASTER",
                "input_assets": "E1_FINAL_VALID_RUNS;E2_600;E3_INDEX;E4_240",
                "input_hashes": "see catalog",
                "script_path": "src/raven_mcs/final_paper_data_asset_freeze_r1/masters.py",
                "script_hash": sha256_file(Path(__file__).resolve().parents[0] / "masters.py") if (Path(__file__).resolve().parents[0] / "masters.py").is_file() else "",
                "formula_or_operation": "row projection; N/A preserved; no metric recompute",
                "deterministic": True,
                "scientific_semantics_changed": False,
                "output_hash": "",
            }
        ],
    )
    write_csv(
        out / "14_SOURCE_PROVENANCE/REPRODUCIBILITY_INDEX.csv",
        [
            {"result": "E1 no-harm", "dataset_hash": NA, "source_hash": "E1_R2_FINAL_SEALED", "config_hash": NA, "EventTrace_hash": "per-seed in E1 CSV", "seed": "28001-28005", "metric_source": "01_PAPER_CORE/E1", "statistics_source": "E1_FINAL_STATISTICS.csv", "figure_table_source": "TABLE_E1"},
            {"result": "E2 D_aligned", "dataset_hash": "db45a2ecc66c27abeaf58b0c03ce66de7bfaf6727f4523ea06ef226a9ce3de50", "source_hash": "E2 formal", "config_hash": "5006daf9fc8337ef33ba0f6a3022e184a82d7bfb2c84d8dafb958f9157d05b1a", "EventTrace_hash": "E2_EVENTTRACE_INDEX_120", "seed": "30001-30020", "metric_source": "E2_D_ALIGNED_PER_SEED.csv", "statistics_source": "E2_FINAL_STATISTICS.csv", "figure_table_source": "FIG1"},
            {"result": "E3 structural SS/U-Air", "dataset_hash": "see DATASET_METADATA_FINAL", "source_hash": "E3_formal", "config_hash": "629b8483ca65964d6ea2028d1bfef58027465d94e260d6284ff876f24b9d2af8", "EventTrace_hash": "E3_FORMAL_EVENTTRACE_MANIFEST", "seed": "30001-30020", "metric_source": "E3_STRUCTURAL_METRICS_MASTER.csv", "statistics_source": "E3_FORMAL_HOLM + secondary Holm", "figure_table_source": "TABLE_II/FIG2"},
            {"result": "E4 ablation", "dataset_hash": "see DATASET_METADATA_FINAL", "source_hash": "E4_240_R2", "config_hash": "E4 one-factor spec", "EventTrace_hash": "E4 gen2 identity", "seed": "30001-30020", "metric_source": "E4_FINAL_VALID_EVIDENCE_240.csv", "statistics_source": "E4_FINAL_STATISTICS_R2.csv", "figure_table_source": "TABLE_III/FIG4"},
        ],
    )
    write_csv(
        out / "22_REPORTS/STATISTICAL_VERSION_AUDIT.csv",
        [
            {"metric": "RMSE_mu", "dataset": "E1", "comparison": "raven vs windows", "version": "E1_R2_FINAL_SEALED", "generation": N_A, "test": "Wilcoxon+Holm", "Holm_family": "FAMILY_RMSE_MU", "paper_eligible": True, "superseded_by": ""},
            {"metric": "D_aligned", "dataset": "NSW-Traffic", "comparison": "sign/direction", "version": "E2_D_ALIGNED_SUMMARY", "generation": N_A, "test": "direction stability", "Holm_family": "n/a", "paper_eligible": True, "superseded_by": ""},
            {"metric": "RMSE_mu_phys", "dataset": "sensorscope/uair", "comparison": "raven_vs_*", "version": "E3_FORMAL_HOLM_RESULTS", "generation": N_A, "test": "paired Wilcoxon+Holm", "Holm_family": "primary_RMSE_mu_main_baselines", "paper_eligible": True, "superseded_by": ""},
            {"metric": "Delta_group/Delta_c_s/Tail", "dataset": "sensorscope/uair", "comparison": "vs baselines", "version": "E3_SECONDARY_HOLM", "generation": N_A, "test": "paired Wilcoxon+Holm", "Holm_family": "per dataset×metric", "paper_eligible": True, "superseded_by": ""},
            {"metric": "E4 component effects", "dataset": "SensorScope/U-Air", "comparison": "w/o-X vs RAVEN", "version": "E4_FINAL_STATISTICS_R2", "generation": "2 for Inst", "test": "paired Wilcoxon+Holm", "Holm_family": "dataset×metric × 5 components", "paper_eligible": True, "superseded_by": ""},
            {"metric": "E4 old stats", "dataset": "SensorScope/U-Air", "comparison": "mixed/gen1", "version": "E4_FINAL_STATISTICS.csv", "generation": "mixed", "test": "do not use", "Holm_family": "superseded", "paper_eligible": False, "superseded_by": "E4_FINAL_STATISTICS_R2.csv"},
        ],
    )
