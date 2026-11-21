"""MEC-G1 … MEC-G33 gates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.paper_data_r1.io_util import read_csv, read_json, write_json
from raven_mcs.manuscript_evidence_closure_r1.constants import E4_LABELS


def _pass(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "detail": detail}


def run_gates(root: Path, out: Path) -> dict[str, Any]:
    root, out = Path(root), Path(out)
    r: dict[str, dict[str, Any]] = {}
    att = read_json(out / "00_audit/MEC_NO_RUN_ATTESTATION.json")
    r["MEC-G1"] = _pass(att.get("formal_runs_started") is False and att.get("e1_e2_e3_e4_reruns") == 0, "no new formal runs")
    r["MEC-G2"] = _pass(att.get("tdrive_formal_started") is False, "no T-Drive runs")
    r["MEC-G3"] = _pass(att.get("r2_unmodified") is True, "R2 unmodified attestation")
    auth = read_json(out / "00_audit/R2_AUTHORITY.json")
    r["MEC-G4"] = _pass(auth.get("do_not_use_r1_when_r2_exists") is True, "R2 sole authority")
    hs = read_json(out / "00_audit/FINAL_H_S_SEMANTICS_FOR_MANUSCRIPT.json")
    r["MEC-G5"] = _pass(hs.get("h_equals_s") is False, "h!=s")
    rq = read_json(out / "00_audit/FINAL_RQ_REGISTRY.json")
    r["MEC-G6"] = _pass(int(rq.get("n_main_empirical_rqs", 0)) == 3, str(rq.get("n_main_empirical_rqs")))
    t2 = (out / "01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv").read_text(encoding="utf-8")
    r["MEC-G7"] = _pass("NSW-Traffic" not in t2 and "traffic" not in t2.lower(), "no Traffic in Table II")
    t3 = pd.read_csv(out / "01_table_sources/TABLE_III_E4_CORE_ABLATION_FINAL.csv")
    wo = t3[t3["configuration"] == "RAVEN-w/o-Inst"]
    r["MEC-G8"] = _pass(len(wo) > 0 and set(wo["generation"].astype(str)) <= {"2"}, f"gens={set(wo['generation'].astype(str))}")
    labels = read_json(out / "10_report/E4_LABELS_USED.json")
    r["MEC-G9"] = _pass(labels.get("Inst") == "ENDPOINT_TRADEOFF", str(labels.get("Inst")))
    r["MEC-G10"] = _pass(labels.get("Use") == "NO_CLEAR_EFFECT", str(labels.get("Use")))
    disc = (out / "06_discussion/DISCUSSION_R1.md").read_text(encoding="utf-8")
    r["MEC-G11"] = _pass("quantitatively small" in disc.lower(), "Debt small-effect wording")
    r["MEC-G12"] = _pass((out / "01_table_sources/TABLE_I_DATASETS.csv").is_file(), "Table I")
    r["MEC-G13"] = _pass((out / "01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv").is_file(), "Table II")
    r["MEC-G14"] = _pass((out / "01_table_sources/TABLE_III_E4_CORE_ABLATION_FINAL.csv").is_file(), "Table III")
    r["MEC-G15"] = _pass((out / "04_figures/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.pdf").is_file(), "Fig1 pdf")
    r["MEC-G16"] = _pass((out / "04_figures/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.pdf").is_file(), "Fig2 pdf")
    r["MEC-G17"] = _pass((out / "04_figures/FIG3_E4_COMPONENT_REMOVAL_FINAL.pdf").is_file(), "Fig3 pdf")
    m1 = read_json(out / "03_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.csv.meta.json")
    m2 = read_json(out / "03_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.csv.meta.json")
    m3 = read_json(out / "03_figure_sources/FIG3_E4_COMPONENT_REMOVAL_FINAL.csv.meta.json")
    r["MEC-G18"] = _pass(all("source_files" in m for m in (m1, m2, m3)), "figure source CSVs")
    prov = read_csv(out / "08_provenance/FINAL_FIGURE_TABLE_PROVENANCE.csv")
    r["MEC-G19"] = _pass(len(prov) >= 6 and all(x.get("source_sha256") for x in prov), f"n_prov={len(prov)}")
    res = (out / "05_results/SECTION_RESULTS_R1.md").read_text(encoding="utf-8")
    r["MEC-G20"] = _pass("RQ1" in res and "RQ2" in res and "RQ3" in res and "VII-B" in res, "RQ-organized Results")
    r["MEC-G21"] = _pass("universally outperforms" not in res.lower() and "universal RMSE superiority" not in res, "no universal RMSE")
    r["MEC-G22"] = _pass("each module is individually necessary" not in res.lower() and "all five components are indispensable" not in res.lower(), "no every-component-necessary")
    r["MEC-G23"] = _pass("not reconstructable" in disc.lower() or "NOT reconstructable" in disc, "P2 boundary")
    r["MEC-G24"] = _pass((out / "06_discussion/DISCUSSION_R1.md").is_file(), "Discussion")
    r["MEC-G25"] = _pass((out / "06_discussion/LIMITATIONS_R1.md").is_file(), "Limitations")
    r["MEC-G26"] = _pass((out / "07_claim_alignment/INTRODUCTION_CONTRIBUTION_REGISTRY.json").is_file(), "Intro registry")
    r["MEC-G27"] = _pass((out / "07_claim_alignment/SECTION_III_VI_THEORY_EVIDENCE_AUDIT.csv").is_file(), "III–VI audit")
    r["MEC-G28"] = _pass((out / "07_claim_alignment/CONCLUSION_CLAIM_AUDIT.md").is_file(), "Conclusion audit")
    r["MEC-G29"] = _pass((out / "10_report/MANUSCRIPT_EVIDENCE_COMPLETENESS_MATRIX.csv").is_file(), "completeness")
    td = read_json(out / "09_tdrive_decision/TDRIVE_MANUSCRIPT_LEVEL_GO_NO_GO.json")
    r["MEC-G30"] = _pass(td.get("protocol_seal_is_not_authorization") is True and td.get("go_all_true") is False, "manuscript-level T-Drive criteria")
    stop = read_json(out / "10_report/EXPERIMENT_STOP_DECISION_R1.json")
    r["MEC-G31"] = _pass(stop.get("other_experiment_families_recommended") == [], "no non-T-Drive experiments")
    r["MEC-G32"] = _pass(
        stop.get("decision") in {"STOP_ALL_NEW_EXPERIMENTS_WRITE_MANUSCRIPT", "ONE_FINAL_TDRIVE_BLOCK_RECOMMENDED_PENDING_TEACHER_APPROVAL"},
        str(stop.get("decision")),
    )
    ver = out / "RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1_ZIP_VERIFICATION.json"
    if ver.is_file():
        v = read_json(ver)
        r["MEC-G33"] = _pass(v.get("pass") is True, f"zip n={v.get('n_members')}")
    else:
        r["MEC-G33"] = _pass(False, "zip verification missing")

    n_pass = sum(1 for x in r.values() if x["pass"])
    payload = {"gates": r, "n_pass": n_pass, "n_total": len(r), "all_pass": n_pass == len(r) == 33}
    write_json(out / "10_report/MANUSCRIPT_EVIDENCE_GATES_R1.json", payload)
    write_json(out / "MANUSCRIPT_EVIDENCE_GATES_R1.json", payload)
    return payload
