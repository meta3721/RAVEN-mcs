"""FDAF-G1 … FDAF-G52."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.paper_data_r1.io_util import read_json, write_json
from raven_mcs.final_paper_data_asset_freeze_r1.constants import E4_LABELS


def _p(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "detail": detail}


def run_gates(root: Path, out: Path) -> dict[str, Any]:
    root, out = Path(root), Path(out)
    r: dict[str, dict[str, Any]] = {}
    att = read_json(out / "22_REPORTS/NO_NEW_EXPERIMENT_ATTESTATION.json")
    r["FDAF-G1"] = _p(att.get("formal_run_started") is False and att.get("training_started") is False, "no new runs")
    r["FDAF-G2"] = _p(att.get("tdrive_run_started") is False, "no T-Drive runs")
    r["FDAF-G3"] = _p(att.get("original_evidence_unchanged") is True, "originals unchanged")
    r["FDAF-G4"] = _p(att.get("r2_authority_preserved") is True, "R2 authority")
    cat = out / "00_MASTER_CATALOG/MASTER_DATA_CATALOG.csv"
    r["FDAF-G5"] = _p(cat.is_file(), "catalog exists")
    cdf = pd.read_csv(cat) if cat.is_file() else pd.DataFrame()
    r["FDAF-G6"] = _p(len(cdf) > 0 and cdf["evidence_status"].notna().all() and not (cdf["evidence_status"].astype(str) == "").any(), f"n={len(cdf)}")
    core = cdf[cdf["evidence_status"] == "PAPER_CORE"] if len(cdf) else cdf
    r["FDAF-G7"] = _p(len(core) == 0 or (core["paper_role"].astype(str) != "").all(), "paper_role")
    r["FDAF-G8"] = _p(len(core) == 0 or (core["sha256"].astype(str).str.len() >= 64).all(), "sha256")
    r["FDAF-G9"] = _p(len(core) == 0 or (core["provenance_status"].astype(str) != "").all(), "provenance")
    e1 = pd.read_csv(out / "01_PAPER_CORE/E1/E1_FINAL_VALID_RUNS.csv")
    r["FDAF-G10"] = _p(len(e1) == 25, f"e1={len(e1)}")
    e2 = pd.read_csv(out / "01_PAPER_CORE/E2/E2_FINAL_VALID_RUNS_600.csv")
    r["FDAF-G11"] = _p(len(e2) == 600, f"e2={len(e2)}")
    e3 = pd.read_csv(out / "01_PAPER_CORE/E3/E3_FINAL_VALID_EVIDENCE_INDEX.csv")
    ssua = e3[e3["dataset"].isin(["SensorScope", "U-Air"])]
    r["FDAF-G12"] = _p(len(ssua) == 440, f"ssua={len(ssua)}")
    nc = (out / "19_NOT_COMPARABLE/NOT_COMPARABLE_MASTER.csv").read_text(encoding="utf-8")
    r["FDAF-G13"] = _p("NOT_COMPARABLE" in nc and "Traffic" in nc, "traffic isolated")
    e4 = pd.read_csv(out / "01_PAPER_CORE/E4/E4_FINAL_VALID_EVIDENCE_240.csv")
    r["FDAF-G14"] = _p(len(e4) == 240, f"e4={len(e4)}")
    wo = e4[e4["configuration"] == "RAVEN-w/o-Inst"]
    r["FDAF-G15"] = _p(len(wo) > 0 and set(wo["generation"].astype(str)) <= {"2", "2.0"}, f"gens={set(wo['generation'].astype(str))}")
    r["FDAF-G16"] = _p((out / "18_INVALID_CANARY/INVALID_CANARY_MASTER.csv").is_file() and any((out / "18_INVALID_CANARY").rglob("*")), "gen0 isolated")
    r["FDAF-G17"] = _p((out / "17_SUPERSEDED/SUPERSEDED_MASTER.csv").is_file() and any((out / "17_SUPERSEDED").rglob("*")), "gen1 isolated")
    labels = read_json(out / "01_PAPER_CORE/E4/E4_FINAL_LABELS.json")
    r["FDAF-G18"] = _p(labels.get("Inst") == "ENDPOINT_TRADEOFF", str(labels.get("Inst")))
    r["FDAF-G19"] = _p(labels.get("Use") == "NO_CLEAR_EFFECT", str(labels.get("Use")))
    disc = (out / "22_REPORTS/RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1_REPORT.md").read_text(encoding="utf-8").lower()
    r["FDAF-G20"] = _p("quantitatively small" in disc, "debt wording")
    hs = read_json(out / "14_SOURCE_PROVENANCE/FINAL_H_S_SEMANTICS.json")
    r["FDAF-G21"] = _p(hs.get("h_equals_s") is False, "h!=s")
    r["FDAF-G22"] = _p((out / "04_ALL_RUN_METRICS/ALL_VALID_RUNS_MASTER.csv").is_file(), "run master")
    r["FDAF-G23"] = _p((out / "04_ALL_RUN_METRICS/ALL_VALID_METRICS_LONG.csv").is_file(), "long master")
    r["FDAF-G24"] = _p((out / "05_WINDOW_LEVEL/WINDOW_LEVEL_ASSET_INDEX.csv").is_file(), "window index")
    r["FDAF-G25"] = _p((out / "06_SELECTION_PROCESS/SELECTION_PROCESS_ASSET_INDEX.csv").is_file(), "selection index")
    r["FDAF-G26"] = _p((out / "07_WEIGHTS/WEIGHT_ASSET_INDEX.csv").is_file(), "weight index")
    r["FDAF-G27"] = _p((out / "08_CALIBRATION_DEBT/CALIBRATION_ASSET_INDEX.csv").is_file() and (out / "08_CALIBRATION_DEBT/DEBT_ASSET_INDEX.csv").is_file(), "cal/debt")
    r["FDAF-G28"] = _p((out / "09_P2_SOLVER/P2_ASSET_INDEX.csv").is_file(), "P2 index")
    r["FDAF-G29"] = _p((out / "10_ESS_VARIANCE/ESS_VARIANCE_ASSET_INDEX.csv").is_file(), "ESS index")
    r["FDAF-G30"] = _p((out / "11_RUNTIME_SYSTEM/RUNTIME_SYSTEM_ASSET_INDEX.csv").is_file(), "runtime index")
    r["FDAF-G31"] = _p((out / "12_EVENTTRACES/EVENTTRACE_MASTER_INDEX.csv").is_file(), "eventtrace index")
    r["FDAF-G32"] = _p((out / "13_CONFIGS/FINAL_CONFIG_MASTER.csv").is_file(), "config master")
    r["FDAF-G33"] = _p((out / "14_SOURCE_PROVENANCE/SOURCE_PROVENANCE_MASTER.csv").is_file(), "source provenance")
    r["FDAF-G34"] = _p((out / "01_PAPER_CORE/STATISTICS/FINAL_STATISTICS_MASTER.csv").is_file(), "stats master")
    sva = pd.read_csv(out / "22_REPORTS/STATISTICAL_VERSION_AUDIT.csv")
    bad = sva[(sva["paper_eligible"].astype(str).str.lower().isin(["true", "1"])) & (sva["superseded_by"].astype(str).str.len() > 0)]
    r["FDAF-G35"] = _p(len(bad) == 0 and (sva["paper_eligible"].astype(str).str.lower() == "false").any(), "one paper-facing E4")
    r["FDAF-G36"] = _p((out / "15_FIGURE_SOURCES/FIGURE_CANDIDATE_REGISTRY.csv").is_file(), "fig lib")
    r["FDAF-G37"] = _p((out / "16_TABLE_SOURCES/TABLE_CANDIDATE_REGISTRY.csv").is_file(), "table lib")
    freg = pd.read_csv(out / "15_FIGURE_SOURCES/FIGURE_CANDIDATE_REGISTRY.csv")
    core_ids = {"FIG1_E2_RISK_NONINTERCHANGEABILITY", "FIG2_E3_STRUCTURAL_MISMATCH", "FIG3_E3_PREDICTION_RISK", "FIG4_E4_COMPONENT_ABLATION"}
    r["FDAF-G38"] = _p(core_ids.issubset(set(freg["figure_id"].astype(str))), "four core figs classified")
    fig5 = freg[freg["figure_id"] == "FIG5_SELECTION_TARGET_COMPOSITION"].iloc[0]
    r["FDAF-G39"] = _p(str(fig5["recommendation"]) == "INSUFFICIENT_EXISTING_DATA_DO_NOT_RUN_NEW_EXPERIMENT", str(fig5["recommendation"]))
    r["FDAF-G40"] = _p(not freg["needs_new_experiment"].astype(str).str.lower().isin(["true", "1"]).any(), "no fig triggers run")
    r["FDAF-G41"] = _p((out / "00_MASTER_CATALOG/REBUTTAL_ASSET_MAP.csv").is_file(), "rebuttal")
    r["FDAF-G42"] = _p((out / "00_MASTER_CATALOG/FINAL_DATA_DICTIONARY.csv").is_file(), "dictionary")
    r["FDAF-G43"] = _p((out / "00_MASTER_CATALOG/SECTION_DATA_REQUIREMENTS.csv").is_file(), "section req")
    r["FDAF-G44"] = _p((out / "00_MASTER_CATALOG/ASSET_TO_CLAIM_MAP.csv").is_file(), "claim map")
    runs = pd.read_csv(out / "04_ALL_RUN_METRICS/ALL_VALID_RUNS_MASTER.csv")
    e1m = runs[runs["round"] == "E1"]
    mae_bad = e1m["MAE_mu"].astype(str).isin(["0", "0.0"])
    r["FDAF-G45"] = _p(not mae_bad.any(), "E1 MAE not zero-filled")
    r["FDAF-G46"] = _p("MISSING_NOT_RECORDED" in e1m["MAE_mu"].astype(str).values, "N/A preserved")
    cons = pd.read_csv(out / "22_REPORTS/FINAL_DATA_CONSISTENCY_AUDIT.csv")
    r["FDAF-G47"] = _p(not (cons["status"] == "CONFLICT").any(), f"conflicts={(cons['status']=='CONFLICT').sum()}")
    td = read_json(out / "20_TDRIVE_RESERVE/TDRIVE_RESERVE_STATUS.json")
    r["FDAF-G48"] = _p(td.get("formal_runs_completed") == 0 and td.get("paper_result_status") == "NOT_RUN" and td.get("default_action") == "DO_NOT_RUN_BEFORE_SUBMISSION", "tdrive reserve")
    cv = out / "21_MANIFESTS/CORE_ZIP_VERIFICATION.json"
    fv = out / "21_MANIFESTS/FULL_ZIP_VERIFICATION.json"
    r["FDAF-G49"] = _p(cv.is_file() and read_json(cv).get("pass") is True, "core zip")
    r["FDAF-G50"] = _p(fv.is_file() and read_json(fv).get("pass") is True, "full zip")
    ho = (out / "RAVEN_MCS_FINAL_PAPER_DATA_HANDOFF_R1.txt").read_text(encoding="utf-8")
    r["FDAF-G51"] = _p(all(x in ho for x in ["MASTER_DATA_CATALOG", "w/o-Inst generation: 2", "T-Drive", "Next action"]), "handoff")
    r["FDAF-G52"] = _p("manuscript-critical data available" in disc and "yes." in disc, "report completeness statement")

    n_pass = sum(1 for x in r.values() if x["pass"])
    payload = {"gates": r, "n_pass": n_pass, "n_total": len(r), "all_pass": n_pass == len(r) == 52}
    write_json(out / "22_REPORTS/FDAF_GATES_R1.json", payload)
    write_json(out / "FDAF_GATES_R1.json", payload)
    return payload
