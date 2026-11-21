"""FPS-G1 … FPS-G54."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.paper_data_r1.io_util import read_json, sha256_file, write_json
from raven_mcs.final_figure_table_paper_specification_seal_r1.constants import (
    EXPECTED_COPY_SHA256,
    PLACEHOLDER_ESS_SHA256,
    STATUS_A,
    TITLE,
)


def _p(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "detail": detail}


def _exists(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _truthy_false(series: pd.Series) -> bool:
    s = series.astype(str).str.strip().str.lower()
    return bool(s.isin(["false", "0", "no"]).all())


def _scan_absolute_paths(out: Path) -> list[str]:
    abs_re = re.compile(r"(?:[A-Za-z]:\\|D:/|C:/|/home/)", re.I)
    hits: list[str] = []
    skip_names = {
        "ABSOLUTE_TO_RELATIVE_PATH_REPAIR.csv",
        "TO_SUBMIT_RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1.zip",
    }
    text_suffix = {".csv", ".json", ".md", ".txt"}
    for p in out.rglob("*"):
        if not p.is_file() or p.name in skip_names or p.suffix.lower() not in text_suffix:
            continue
        if p.suffix.lower() == ".csv":
            with p.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                fields = reader.fieldnames or []
                for i, row in enumerate(reader, start=2):
                    for k, v in row.items():
                        if k in {"old_path", "original_path"}:
                            continue
                        if v and abs_re.search(str(v)):
                            hits.append(f"{p.relative_to(out).as_posix()}:{i}:{k}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if abs_re.search(text):
            hits.append(p.relative_to(out).as_posix())
    return hits


def run_gates(root: Path, out: Path) -> dict[str, Any]:
    root, out = Path(root), Path(out)
    r: dict[str, dict[str, Any]] = {}
    att_p = out / "12_REPORTS/NO_NEW_EXPERIMENT_ATTESTATION.json"
    att = read_json(att_p) if att_p.is_file() else {}
    r["FPS-G1"] = _p(
        att.get("training_started") is False
        and att.get("formal_run_started") is False
        and att.get("canary_started") is False
        and att.get("new_scientific_runs", 0) in {0, False, None},
        "new scientific runs = 0",
    )
    r["FPS-G2"] = _p(att.get("tdrive_run_started") is False, "T-Drive runs = 0")
    r["FPS-G3"] = _p(att.get("original_scientific_data_unchanged") is True and att.get("scientific_metric_changed") is False, "original scientific data unchanged")

    g52 = read_json(out / "02_PACKAGING_REPAIR/FDAF_G52_REPAIR_AUDIT.json") if (out / "02_PACKAGING_REPAIR/FDAF_G52_REPAIR_AUDIT.json").is_file() else {}
    r["FPS-G4"] = _p(
        g52.get("scientific_data_changed") is False and "bookkeeping" in str(g52.get("cause", "")).lower(),
        "G52 documented; scientific_data_changed=false",
    )

    abs_hits = _scan_absolute_paths(out)
    r["FPS-G5"] = _p(len(abs_hits) == 0, f"absolute path hits={len(abs_hits)} {abs_hits[:5]}")

    fig6 = read_json(out / "02_PACKAGING_REPAIR/FIG6_READINESS_REPAIR_R1.json") if (out / "02_PACKAGING_REPAIR/FIG6_READINESS_REPAIR_R1.json").is_file() else {}
    app_f2 = out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/APP_F2_P2_FEASIBILITY_SUMMARY.csv"
    app_sha = sha256_file(app_f2) if app_f2.is_file() else ""
    fig6_ok = (
        fig6.get("final_status") == "APPENDIX_READY"
        and fig6.get("option_a_used") is True
        and app_f2.is_file()
        and app_sha
        and app_sha != PLACEHOLDER_ESS_SHA256
        and "MISSING_NOT_RECORDED" not in app_f2.read_text(encoding="utf-8")[:200]
    )
    r["FPS-G6"] = _p(fig6_ok, f"FIG6={fig6.get('final_status')} sha={app_sha[:12] if app_sha else 'missing'}")

    pos = read_json(out / "00_SPECIFICATION/FINAL_PAPER_POSITIONING_R1.json") if (out / "00_SPECIFICATION/FINAL_PAPER_POSITIONING_R1.json").is_file() else {}
    r["FPS-G7"] = _p(pos.get("title") == TITLE, "title frozen")

    contrib = pd.read_csv(out / "00_SPECIFICATION/FINAL_CONTRIBUTION_REGISTRY_R1.csv") if (out / "00_SPECIFICATION/FINAL_CONTRIBUTION_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    r["FPS-G8"] = _p(len(contrib) == 3 and set(contrib["contribution_id"].astype(str)) == {"C1", "C2", "C3"}, f"n_contrib={len(contrib)}")

    rq = pd.read_csv(out / "00_SPECIFICATION/FINAL_RQ_REGISTRY_R1.csv") if (out / "00_SPECIFICATION/FINAL_RQ_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    r["FPS-G9"] = _p(len(rq) == 3 and set(rq["rq_id"].astype(str)) == {"RQ1", "RQ2", "RQ3"}, f"n_rq={len(rq)}")

    sec = pd.read_csv(out / "00_SPECIFICATION/FINAL_SECTION_STRUCTURE_R1.csv") if (out / "00_SPECIFICATION/FINAL_SECTION_STRUCTURE_R1.csv").is_file() else pd.DataFrame()
    ids = set(sec["section"].astype(str)) if len(sec) else set()
    r["FPS-G10"] = _p({"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"}.issubset(ids), f"sections={sorted(ids)}")

    hs = read_json(out / "01_SEMANTICS/FINAL_H_S_MANUSCRIPT_SEMANTICS_R1.json") if (out / "01_SEMANTICS/FINAL_H_S_MANUSCRIPT_SEMANTICS_R1.json").is_file() else {}
    r["FPS-G11"] = _p(hs.get("h_equals_s") is False, "h!=s")

    roles = pd.read_csv(out / "01_SEMANTICS/FINAL_EXPERIMENT_ROLE_REGISTRY_R1.csv") if (out / "01_SEMANTICS/FINAL_EXPERIMENT_ROLE_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    blocks = set(roles["block"].astype(str)) if len(roles) else set()
    r["FPS-G12"] = _p({"E1", "E2", "E3", "E4"}.issubset(blocks), f"blocks={sorted(blocks)}")

    claim = read_json(out / "00_SPECIFICATION/FINAL_CLAIM_CEILING_R1.json") if (out / "00_SPECIFICATION/FINAL_CLAIM_CEILING_R1.json").is_file() else {}
    traffic_role = ""
    if len(roles):
        tr = roles[roles["block"].astype(str) == "Traffic"]
        traffic_role = " ".join(tr.astype(str).fillna("").agg(" ".join, axis=1).tolist()) if len(tr) else ""
    r["FPS-G13"] = _p("NOT_COMPARABLE" in str(claim.get("allowed", {}).get("C9", "")) and "NOT_COMPARABLE" in traffic_role, "Traffic E3 NOT_COMPARABLE")

    td = read_json(out / "10_AUDIT/TDRIVE_FINAL_RESERVE_STATUS_R1.json") if (out / "10_AUDIT/TDRIVE_FINAL_RESERVE_STATUS_R1.json").is_file() else {}
    r["FPS-G14"] = _p(
        td.get("protocol_status") == "PROTOCOL_SEALED"
        and td.get("formal_status") == "FORMAL_NOT_RUN"
        and td.get("paper_role") == "REVIEWER_RESERVE"
        and td.get("in_main_results") is False,
        "T-Drive reviewer reserve",
    )

    t3p = out / "05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_III_CORE_ABLATION.csv"
    t3_ok = False
    if t3p.is_file():
        t3 = pd.read_csv(t3p)
        wo = t3[t3["configuration"].astype(str).str.contains("w/o-Inst", regex=False)]
        gens = set(wo["generation"].astype(str)) if len(wo) else set()
        t3_ok = len(wo) > 0 and gens <= {"2", "2.0"}
    r["FPS-G15"] = _p(t3_ok, "E4 w/o-Inst Gen2 only")

    e4_txt = (out / "03_FIGURE_SPEC/FIG_E4_E4_COMPONENT_ABLATION_FINAL_SPEC.md").read_text(encoding="utf-8") if (out / "03_FIGURE_SPEC/FIG_E4_E4_COMPONENT_ABLATION_FINAL_SPEC.md").is_file() else ""
    ceiling_txt = (out / "00_SPECIFICATION/FINAL_CLAIM_CEILING_R1.md").read_text(encoding="utf-8") if (out / "00_SPECIFICATION/FINAL_CLAIM_CEILING_R1.md").is_file() else ""
    handoff = (out / "11_FINAL/RAVEN_MCS_WRITING_HANDOFF_R1.txt").read_text(encoding="utf-8") if (out / "11_FINAL/RAVEN_MCS_WRITING_HANDOFF_R1.txt").is_file() else ""
    r["FPS-G16"] = _p("ENDPOINT_TRADEOFF" in e4_txt and "Inst" in str(claim.get("allowed", {}).get("C8", "")), "Inst=ENDPOINT_TRADEOFF")
    r["FPS-G17"] = _p("NO_CLEAR_EFFECT" in e4_txt and "NO_CLEAR_EFFECT" in str(claim.get("allowed", {}).get("C6", "")), "Use=NO_CLEAR_EFFECT")
    r["FPS-G18"] = _p("quantitatively small" in (ceiling_txt + handoff + e4_txt).lower(), "Debt quantitatively small")

    r["FPS-G19"] = _p(_exists(out / "03_FIGURE_SPEC/FIG_C1_PROBLEM_SELECTION_TARGET_MISMATCH_SPEC.md"), "FIG-C1 spec")
    r["FPS-G20"] = _p(_exists(out / "03_FIGURE_SPEC/FIG_C2_RAVEN_ARCHITECTURE_SPEC.md"), "FIG-C2 spec")
    r["FPS-G21"] = _p(_exists(out / "03_FIGURE_SPEC/FIG_E1_E2_RISK_NONINTERCHANGEABILITY_FINAL_SPEC.md") and _exists(out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv"), "FIG-E1 frozen")
    r["FPS-G22"] = _p(_exists(out / "03_FIGURE_SPEC/FIG_E2_E3_STRUCTURAL_ALIGNMENT_FINAL_SPEC.md") and _exists(out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv"), "FIG-E2 frozen")
    r["FPS-G23"] = _p(_exists(out / "03_FIGURE_SPEC/FIG_E3_E3_PREDICTION_RISK_FINAL_SPEC.md") and _exists(out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E3_E3_PREDICTION_RISK.csv"), "FIG-E3 frozen")
    r["FPS-G24"] = _p(_exists(out / "03_FIGURE_SPEC/FIG_E4_E4_COMPONENT_ABLATION_FINAL_SPEC.md") and _exists(out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E4_E4_COMPONENT_ABLATION.csv"), "FIG-E4 frozen")

    freg = pd.read_csv(out / "03_FIGURE_SPEC/FINAL_MAIN_FIGURE_REGISTRY_R1.csv") if (out / "03_FIGURE_SPEC/FINAL_MAIN_FIGURE_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    ftreg = pd.read_csv(out / "11_FINAL/FINAL_FIGURE_TABLE_REGISTRY_R1.csv") if (out / "11_FINAL/FINAL_FIGURE_TABLE_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    no_new = True
    if len(freg):
        no_new = no_new and _truthy_false(freg["new_experiment_required"])
    if len(ftreg):
        no_new = no_new and _truthy_false(ftreg["new_experiment_required"])
    r["FPS-G25"] = _p(no_new and len(freg) > 0 and len(ftreg) > 0, "no selected figure requires new experiment")

    areg = pd.read_csv(out / "03_FIGURE_SPEC/FINAL_APPENDIX_FIGURE_REGISTRY_R1.csv") if (out / "03_FIGURE_SPEC/FINAL_APPENDIX_FIGURE_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    allowed = {"APPENDIX_READY", "OPTIONAL_APPENDIX", "DROP_LOW_VALUE", "INSUFFICIENT_EXISTING_DATA_DO_NOT_RUN"}
    r["FPS-G26"] = _p(len(areg) > 0 and set(areg["final_status"].astype(str)).issubset(allowed), f"appendix fig statuses={set(areg['final_status'].astype(str)) if len(areg) else set()}")

    r["FPS-G27"] = _p(_exists(out / "04_TABLE_SPEC/TABLE_I_DATASET_PROTOCOL_SPEC.md") and _exists(out / "05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_I_DATASET_PROTOCOL.csv"), "Table I")
    r["FPS-G28"] = _p(_exists(out / "04_TABLE_SPEC/TABLE_II_MAIN_EFFECTIVENESS_SPEC.md") and _exists(out / "05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_II_MAIN_EFFECTIVENESS.csv"), "Table II")
    r["FPS-G29"] = _p(_exists(out / "04_TABLE_SPEC/TABLE_III_CORE_ABLATION_SPEC.md") and t3p.is_file(), "Table III")

    atreg = pd.read_csv(out / "04_TABLE_SPEC/FINAL_APPENDIX_TABLE_REGISTRY_R1.csv") if (out / "04_TABLE_SPEC/FINAL_APPENDIX_TABLE_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    r["FPS-G30"] = _p(len(atreg) >= 4 and set(atreg["final_status"].astype(str)).issubset(allowed | {"APPENDIX_READY"}), f"n_app_tables={len(atreg)}")

    hash_ok = True
    hash_detail = []
    if len(freg):
        for _, row in freg.iterrows():
            if str(row["figure_id"]) == "FIG-C":
                continue
            sha = str(row.get("source_sha256", ""))
            if len(sha) != 64:
                hash_ok = False
                hash_detail.append(str(row["figure_id"]))
    treg = pd.read_csv(out / "04_TABLE_SPEC/FINAL_MAIN_TABLE_REGISTRY_R1.csv") if (out / "04_TABLE_SPEC/FINAL_MAIN_TABLE_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    if len(treg):
        for _, row in treg.iterrows():
            sha = str(row.get("source_sha256", ""))
            if len(sha) != 64:
                hash_ok = False
                hash_detail.append(str(row["table_id"]))
    copy_ok = True
    for key, expected in EXPECTED_COPY_SHA256.items():
        dest_map = {
            "FIG_E1": out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv",
            "FIG_E2": out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv",
            "FIG_E3": out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E3_E3_PREDICTION_RISK.csv",
            "FIG_E4": out / "05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E4_E4_COMPONENT_ABLATION.csv",
            "TABLE_I": out / "05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_I_DATASET_PROTOCOL.csv",
            "TABLE_II": out / "05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_II_MAIN_EFFECTIVENESS.csv",
            "TABLE_III": out / "05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_III_CORE_ABLATION.csv",
            "APP_T1": out / "05_PROVENANCE/FINAL_TABLE_SOURCES/APP_T1_E1_BALANCED_SANITY.csv",
        }
        pth = dest_map[key]
        got = sha256_file(pth) if pth.is_file() else ""
        if got != expected:
            copy_ok = False
            hash_detail.append(f"{key}:{got[:12]}")
    r["FPS-G31"] = _p(hash_ok and copy_ok, f"hashes ok={hash_ok and copy_ok} {hash_detail[:6]}")

    ident = pd.read_csv(out / "05_PROVENANCE/FINAL_FIGURE_TABLE_DATA_IDENTITY_AUDIT.csv") if (out / "05_PROVENANCE/FINAL_FIGURE_TABLE_DATA_IDENTITY_AUDIT.csv").is_file() else pd.DataFrame()
    r["FPS-G32"] = _p(len(ident) > 0 and _truthy_false(ident["superseded_e4_stats"]), "no superseded E4 in identity audit")
    r["FPS-G33"] = _p(len(ident) > 0 and _truthy_false(ident["canary_invalid"]), "no canary")
    r["FPS-G34"] = _p(len(ident) > 0 and _truthy_false(ident["tdrive_result"]), "no T-Drive results")

    cmap = pd.read_csv(out / "06_ALIGNMENT/CONTRIBUTION_THEORY_EVIDENCE_MAP.csv") if (out / "06_ALIGNMENT/CONTRIBUTION_THEORY_EVIDENCE_MAP.csv").is_file() else pd.DataFrame()
    r["FPS-G35"] = _p(
        len(cmap) == 3
        and cmap["theorem_or_proposition"].astype(str).str.len().gt(0).all()
        and cmap["empirical_rq"].astype(str).str.len().gt(0).all()
        and cmap["primary_figure"].astype(str).str.len().gt(0).all(),
        "contribution-theory-evidence map",
    )
    rqmap = pd.read_csv(out / "06_ALIGNMENT/RQ_EVIDENCE_MAP.csv") if (out / "06_ALIGNMENT/RQ_EVIDENCE_MAP.csv").is_file() else pd.DataFrame()
    r["FPS-G36"] = _p(len(rqmap) == 3 and set(rqmap["rq"].astype(str)) == {"RQ1", "RQ2", "RQ3"}, "RQ-evidence map")

    r["FPS-G37"] = _p(_exists(out / "07_SECTION_SPEC/SECTION_III_SPEC_R1.md") and "h(i)" in (out / "07_SECTION_SPEC/SECTION_III_SPEC_R1.md").read_text(encoding="utf-8"), "Section III")
    r["FPS-G38"] = _p(_exists(out / "07_SECTION_SPEC/SECTION_IV_SPEC_R1.md") and "Hajek" in (out / "07_SECTION_SPEC/SECTION_IV_SPEC_R1.md").read_text(encoding="utf-8"), "Section IV")
    r["FPS-G39"] = _p(_exists(out / "07_SECTION_SPEC/SECTION_V_SPEC_R1.md") and "P2" in (out / "07_SECTION_SPEC/SECTION_V_SPEC_R1.md").read_text(encoding="utf-8"), "Section V")
    th = pd.read_csv(out / "07_SECTION_SPEC/SECTION_VI_THEOREM_REGISTRY_R1.csv") if (out / "07_SECTION_SPEC/SECTION_VI_THEOREM_REGISTRY_R1.csv").is_file() else pd.DataFrame()
    r["FPS-G40"] = _p(len(th) >= 3 and {"theorem_name", "assumptions", "exact_claim", "proof_location"}.issubset(set(th.columns)), "Section VI theorems")
    r["FPS-G41"] = _p(_exists(out / "07_SECTION_SPEC/SECTION_VII_SPEC_R1.md") and "RQ1" in (out / "07_SECTION_SPEC/SECTION_VII_SPEC_R1.md").read_text(encoding="utf-8"), "Section VII")
    r["FPS-G42"] = _p(_exists(out / "07_SECTION_SPEC/SECTION_VIII_SPEC_R1.md") and "T-Drive" in (out / "07_SECTION_SPEC/SECTION_VIII_SPEC_R1.md").read_text(encoding="utf-8"), "Section VIII")
    r["FPS-G43"] = _p(_exists(out / "08_WRITING_BOUNDARY/INTRODUCTION_CONTRIBUTION_WORDING_SEAL.md") and "universally superior" in (out / "08_WRITING_BOUNDARY/INTRODUCTION_CONTRIBUTION_WORDING_SEAL.md").read_text(encoding="utf-8"), "Intro wording")
    r["FPS-G44"] = _p(_exists(out / "08_WRITING_BOUNDARY/ABSTRACT_CLAIM_CEILING_R1.md") and "Forbidden" in (out / "08_WRITING_BOUNDARY/ABSTRACT_CLAIM_CEILING_R1.md").read_text(encoding="utf-8"), "Abstract ceiling")
    r["FPS-G45"] = _p(_exists(out / "08_WRITING_BOUNDARY/CONCLUSION_CLAIM_CEILING_R1.md") and "structural alignment" in (out / "08_WRITING_BOUNDARY/CONCLUSION_CLAIM_CEILING_R1.md").read_text(encoding="utf-8").lower(), "Conclusion ceiling")
    r["FPS-G46"] = _p(_exists(out / "09_APPENDIX/FINAL_APPENDIX_STRUCTURE_R1.md") and "Appendix A" in (out / "09_APPENDIX/FINAL_APPENDIX_STRUCTURE_R1.md").read_text(encoding="utf-8"), "Appendix structure")

    gaps = pd.read_csv(out / "10_AUDIT/FINAL_DATA_GAP_DECISION_R1.csv") if (out / "10_AUDIT/FINAL_DATA_GAP_DECISION_R1.csv").is_file() else pd.DataFrame()
    r["FPS-G47"] = _p(len(gaps) > 0 and not (gaps["class"].astype(str) == "CORE_BLOCKER").any(), "no CORE_BLOCKER")
    r["FPS-G48"] = _p(len(gaps) > 0 and _truthy_false(gaps["triggers_new_experiment"]), "supporting gaps do not trigger experiments")

    repro = pd.read_csv(out / "10_AUDIT/FINAL_MAIN_ARTIFACT_REPRODUCIBILITY_AUDIT.csv") if (out / "10_AUDIT/FINAL_MAIN_ARTIFACT_REPRODUCIBILITY_AUDIT.csv").is_file() else pd.DataFrame()
    r["FPS-G49"] = _p(len(repro) >= 7 and repro["gap"].astype(str).str.lower().isin(["none", ""]).all(), "reproducibility PASS")
    cons = pd.read_csv(out / "10_AUDIT/FINAL_MAIN_ARTIFACT_NUMERIC_CONSISTENCY.csv") if (out / "10_AUDIT/FINAL_MAIN_ARTIFACT_NUMERIC_CONSISTENCY.csv").is_file() else pd.DataFrame()
    r["FPS-G50"] = _p(len(cons) > 0 and not (cons["status"].astype(str) == "CONFLICT").any(), "numeric consistency PASS")

    r["FPS-G51"] = _p(
        _exists(out / "11_FINAL/FRAZEN_PAPER_SPECIFICATION_MASTER_R1.json") and _exists(out / "11_FINAL/FRAZEN_PAPER_SPECIFICATION_MASTER_R1.md"),
        "FRAZEN master",
    )
    r["FPS-G52"] = _p(len(ftreg) >= 8 and {"artifact_id", "source_sha256", "new_experiment_required"}.issubset(set(ftreg.columns)), "figure-table registry")
    r["FPS-G53"] = _p("WRITE SECTION III–VI USING FROZEN SPECIFICATION" in handoff, "writing handoff")

    report_p = out / "12_REPORTS/RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1_REPORT.md"
    report = report_p.read_text(encoding="utf-8") if report_p.is_file() else ""
    r["FPS-G54"] = _p("new experiments required = false" in report.lower(), "report new experiments required = false")

    n_pass = sum(1 for x in r.values() if x["pass"])
    payload = {"gates": r, "n_pass": n_pass, "n_total": len(r), "all_pass": n_pass == len(r) == 54, "status_if_pass": STATUS_A}
    write_json(out / "12_REPORTS/FPS_GATES_R1.json", payload)
    return payload
