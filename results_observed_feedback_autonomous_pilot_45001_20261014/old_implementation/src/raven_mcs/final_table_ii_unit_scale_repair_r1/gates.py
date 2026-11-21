"""T2R-G1 … T2R-G28."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.paper_data_r1.io_util import read_json, write_json
from raven_mcs.final_table_ii_unit_scale_repair_r1.constants import STATUS_A, UAIR_STALE_FLOOR


def _p(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "detail": detail}


def _exists(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def run_gates(root: Path, out: Path) -> dict[str, Any]:
    root, out = Path(root), Path(out)
    r: dict[str, dict[str, Any]] = {}
    att = read_json(out / "00_AUDIT/NO_NEW_EXPERIMENT_ATTESTATION.json") if (out / "00_AUDIT/NO_NEW_EXPERIMENT_ATTESTATION.json").is_file() else {}
    r["T2R-G1"] = _p(att.get("training_started") is False and att.get("formal_run_started") is False and att.get("new_scientific_runs", 0) in {0, False, None}, "runs=0")
    r["T2R-G2"] = _p(att.get("tdrive_run_started") is False, "T-Drive=0")
    r["T2R-G3"] = _p(att.get("original_scientific_data_unchanged", True) is True and att.get("metric_definition_changed") is False, "originals unchanged")
    uair = pd.read_csv(out / "00_AUDIT/UAIR_TABLEII_SCALE_AUDIT.csv") if (out / "00_AUDIT/UAIR_TABLEII_SCALE_AUDIT.csv").is_file() else pd.DataFrame()
    r["T2R-G4"] = _p(len(uair) > 0, f"uair audit n={len(uair)}")
    ss = pd.read_csv(out / "00_AUDIT/SENSORSCOPE_TABLEII_CONTROL_AUDIT.csv") if (out / "00_AUDIT/SENSORSCOPE_TABLEII_CONTROL_AUDIT.csv").is_file() else pd.DataFrame()
    r["T2R-G5"] = _p(len(ss) > 0, f"ss audit n={len(ss)}")
    rebuilt = pd.read_csv(out / "01_REBUILT_TABLE_II/UAIR_PREDICTION_METRICS_FINAL.csv") if (out / "01_REBUILT_TABLE_II/UAIR_PREDICTION_METRICS_FINAL.csv").is_file() else pd.DataFrame()
    r["T2R-G6"] = _p(len(rebuilt) > 0, f"rebuilt n={len(rebuilt)}")
    t2 = pd.read_csv(out / "01_REBUILT_TABLE_II/TABLE_II_MAIN_EFFECTIVENESS_REPAIRED_R1.csv") if (out / "01_REBUILT_TABLE_II/TABLE_II_MAIN_EFFECTIVENESS_REPAIRED_R1.csv").is_file() else pd.DataFrame()
    u2 = t2[t2["dataset"].astype(str) == "U-Air"] if len(t2) else t2
    stale_left = False
    if len(u2):
        for col in ("RMSE_mu_mean", "RMSE_mu_std", "Tail_RMSE_mean", "Tail_RMSE_std"):
            vals = pd.to_numeric(u2[col], errors="coerce")
            if (vals > UAIR_STALE_FLOOR).any():
                stale_left = True
    r["T2R-G7"] = _p(len(u2) > 0 and not stale_left, "no U-Air 20.x remains")
    ss_pred = ss[ss["field"].astype(str).str.contains("rmse|tail", case=False, na=False)] if len(ss) and "field" in ss.columns else ss
    if len(ss) and "classification" in ss.columns:
        r["T2R-G8"] = _p((ss["classification"].astype(str) == "MATCH_FINAL_SEED_SCALE").all(), "SensorScope MATCH")
    else:
        r["T2R-G8"] = _p(False, "SensorScope audit missing classification")
    e2a = pd.read_csv(out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_FIGE2_STRUCTURAL_AUDIT.csv") if (out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_FIGE2_STRUCTURAL_AUDIT.csv").is_file() else pd.DataFrame()
    r["T2R-G9"] = _p(len(e2a) > 0 and not e2a["status"].astype(str).isin(["SCALE_MISMATCH", "UNEXPLAINED_CONFLICT", "UNRESOLVED_CONFLICT"]).any(), "structural vs FIG-E2")
    e3a = pd.read_csv(out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_FIGE3_PREDICTION_AUDIT.csv") if (out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_FIGE3_PREDICTION_AUDIT.csv").is_file() else pd.DataFrame()
    r["T2R-G10"] = _p(len(e3a) > 0 and e3a["status"].astype(str).isin(["EXACT_MATCH", "ROUNDING_MATCH"]).all(), "vs FIG-E3")
    r["T2R-G11"] = _p(len(e2a) > 0 and e2a["status"].astype(str).isin(["EXACT_MATCH", "ROUNDING_MATCH"]).all(), "vs FIG-E2")
    t3a = pd.read_csv(out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_TABLEIII_FULL_RAVEN_AUDIT.csv") if (out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_TABLEIII_FULL_RAVEN_AUDIT.csv").is_file() else pd.DataFrame()
    r["T2R-G12"] = _p(len(t3a) > 0 and t3a["status"].astype(str).isin(["EXACT_MATCH", "ROUNDING_MATCH"]).all(), "vs Table III")
    masta = pd.read_csv(out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_MASTER_EVIDENCE_AUDIT.csv") if (out / "03_CROSS_ARTIFACT_CHECKS/TABLEII_VS_MASTER_EVIDENCE_AUDIT.csv").is_file() else pd.DataFrame()
    r["T2R-G13"] = _p(len(masta) > 0 and masta["status"].astype(str).isin(["EXACT_MATCH", "ROUNDING_MATCH"]).all(), "vs master evidence")
    r["T2R-G14"] = _p(att.get("statistical_protocol_changed") is False, "stats unchanged")
    r["T2R-G15"] = _p(att.get("holm_families_changed", False) is False, "Holm unchanged")
    link = pd.read_csv(out / "02_STATISTICS_LINKAGE/TABLEII_FINAL_STATISTICAL_LINKAGE.csv") if (out / "02_STATISTICS_LINKAGE/TABLEII_FINAL_STATISTICAL_LINKAGE.csv").is_file() else pd.DataFrame()
    r["T2R-G16"] = _p(len(link) > 0 and _exists(out / "02_STATISTICS_LINKAGE/TABLEII_MARKER_SEMANTICS.md"), "markers linked")
    sup = read_json(out / "06_PROVENANCE/TABLEII_SUPERSESSION_RECORD.json") if (out / "06_PROVENANCE/TABLEII_SUPERSESSION_RECORD.json").is_file() else {}
    r["T2R-G17"] = _p(sup.get("reason") == "SUPERSEDED_SCALE_VERSION_MISMATCH" and sup.get("scientific_runs_changed") is False, "old Table II superseded")
    r["T2R-G18"] = _p(_exists(out / "01_REBUILT_TABLE_II/TABLE_II_MAIN_EFFECTIVENESS_REPAIRED_R1.meta.json"), "meta complete")
    ureg = pd.read_csv(out / "00_AUDIT/FINAL_PREDICTION_UNIT_SCALE_REGISTRY.csv") if (out / "00_AUDIT/FINAL_PREDICTION_UNIT_SCALE_REGISTRY.csv").is_file() else pd.DataFrame()
    r["T2R-G19"] = _p(len(ureg) > 0 and "20.x" in ureg.to_csv(index=False), "unit/scale registry")
    mt = pd.read_csv(out / "04_REGISTRY_UPDATES/FINAL_MAIN_TABLE_REGISTRY_REPAIRED_R1.csv") if (out / "04_REGISTRY_UPDATES/FINAL_MAIN_TABLE_REGISTRY_REPAIRED_R1.csv").is_file() else pd.DataFrame()
    r["T2R-G20"] = _p(len(mt) == 3 and mt.loc[mt["table_id"] == "TABLE-II", "source_csv"].astype(str).str.contains("REPAIRED_R1").any(), "main table registry")
    ft = pd.read_csv(out / "04_REGISTRY_UPDATES/FINAL_FIGURE_TABLE_REGISTRY_REPAIRED_R1.csv") if (out / "04_REGISTRY_UPDATES/FINAL_FIGURE_TABLE_REGISTRY_REPAIRED_R1.csv").is_file() else pd.DataFrame()
    r["T2R-G21"] = _p(len(ft) > 0 and ft.loc[ft["artifact_id"] == "TABLE-II", "source_file"].astype(str).str.contains("REPAIRED_R1").any(), "figure-table registry")
    figw = (out / "04_REGISTRY_UPDATES/FINAL_FIGURE_COUNT_WORDING_REPAIR.md").read_text(encoding="utf-8") if (out / "04_REGISTRY_UPDATES/FINAL_FIGURE_COUNT_WORDING_REPAIR.md").is_file() else ""
    r["T2R-G22"] = _p("E2 risk non-interchangeability" in figw and "E3 prediction risk" in figw and "E4 component ablation" in figw, "figure-count wording")
    nam = pd.read_csv(out / "05_SYMBOL_NAMING_REPAIR/SECTION_VI_THEOREM_NAMING_REPAIR.csv") if (out / "05_SYMBOL_NAMING_REPAIR/SECTION_VI_THEOREM_NAMING_REPAIR.csv").is_file() else pd.DataFrame()
    r["T2R-G23"] = _p(len(nam) >= 3 and (nam["new_identifier"].astype(str) == "P2").sum() == 0, "P2 naming conflict removed")
    r["T2R-G24"] = _p(len(nam) > 0 and nam["math_changed"].astype(str).str.lower().isin(["false", "0"]).all(), "math unchanged")
    master = read_json(out / "04_REGISTRY_UPDATES/FROZEN_PAPER_SPECIFICATION_MASTER_R1_REPAIRED.json") if (out / "04_REGISTRY_UPDATES/FROZEN_PAPER_SPECIFICATION_MASTER_R1_REPAIRED.json").is_file() else {}
    r["T2R-G25"] = _p(master.get("title") and master.get("tdrive") and "TABLE_II" in str(master.get("figure_table_hashes", {})), "spec master patched")
    td = read_json(out / "00_AUDIT/TDRIVE_STATUS_RECONFIRMATION.json") if (out / "00_AUDIT/TDRIVE_STATUS_RECONFIRMATION.json").is_file() else {}
    r["T2R-G26"] = _p(td.get("paper_role") == "REVIEWER_RESERVE" and td.get("formal_status") == "FORMAL_NOT_RUN", "T-Drive reserve")
    mx = pd.read_csv(out / "03_CROSS_ARTIFACT_CHECKS/FINAL_MAIN_ARTIFACT_CONSISTENCY_MATRIX.csv") if (out / "03_CROSS_ARTIFACT_CHECKS/FINAL_MAIN_ARTIFACT_CONSISTENCY_MATRIX.csv").is_file() else pd.DataFrame()
    bad = {"SCALE_MISMATCH", "STALE_VERSION", "UNRESOLVED_CONFLICT"}
    r["T2R-G27"] = _p(len(mx) > 0 and not mx["status"].astype(str).isin(bad).any(), "no main-text numeric conflict")
    r["T2R-G28"] = _p(att.get("core_data_gap_introduced", False) is False, "no CORE gap introduced")

    n_pass = sum(1 for x in r.values() if x["pass"])
    payload = {"gates": r, "n_pass": n_pass, "n_total": len(r), "all_pass": n_pass == len(r) == 28, "status_if_pass": STATUS_A}
    write_json(out / "07_REPORT/T2R_GATES_R1.json", payload)
    return payload
