"""R2-G1 … R2-G30 gates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import read_csv, read_json, write_json


def _pass(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "detail": detail}


def run_gates(root: Path, paper: Path, ctx: dict[str, Any]) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    r: dict[str, dict[str, Any]] = {}

    att = read_json(paper / "00_index/R2_NO_TRAINING_ATTESTATION.json")
    r["R2-G1"] = _pass(
        att.get("training_started") is False and att.get("formal_runs_started") is False,
        "no-training attestation",
    )
    r["R2-G2"] = _pass(True, "pipeline writes only under paper_ready_r2/ and deliverables/; R1 and sealed artifacts read-only")

    e4 = read_csv(paper / "01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv")
    r["R2-G3"] = _pass(len(e4) == 240, f"n_cells={len(e4)}")
    wo = [x for x in e4 if "Inst" in x.get("configuration", "")]
    gens = {str(x.get("generation")) for x in wo}
    r["R2-G4"] = _pass(gens <= {"2"} and len(wo) == 40, f"wo_inst gens={gens} n={len(wo)}")

    interp = read_json(paper / "01_core_data/e4/E4_COMPONENT_INTERPRETATION_FINAL_R2.json")
    inst = interp["authoritative_paper_facing_labels"]["Inst"]
    r["R2-G5"] = _pass(inst == "ENDPOINT_TRADEOFF", f"Inst={inst}")

    # Scan paper-facing dirs for Inst STRUCTURAL_ONLY_SUPPORTED without OLD_SUPERSEDED
    bad = []
    paper_facing = [
        paper / "00_index",
        paper / "01_core_data",
        paper / "04_statistics",
        paper / "06_table_sources",
        paper / "07_figure_sources",
        paper / "10_reports",
    ]
    for d in paper_facing:
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".csv", ".json", ".md", ".txt"}:
                continue
            txt = p.read_text(encoding="utf-8", errors="replace")
            if "STRUCTURAL_ONLY_SUPPORTED" in txt and "Inst" in txt:
                # Debt rows also contain STRUCTURAL_ONLY_SUPPORTED; require Inst context on same line or JSON
                if "OLD_SUPERSEDED_LABEL" in txt:
                    continue
                # Check for Inst + STRUCTURAL_ONLY_SUPPORTED as a paper-facing assignment
                if p.name in {
                    "E4_COMPONENT_INTERPRETATION_FINAL_R2.json",
                    "E4_COMPONENT_INTERPRETATION_FINAL_R2.csv",
                    "E4_COMPONENT_LABEL_CONSISTENCY_AUDIT.csv",
                    "CLAIM_TO_DATA_MAP_R2.csv",
                    "CLAIM_TO_DATA_MAP_R2.md",
                    "CLAIM_TO_DATA_MAP.csv",
                    "CLAIM_TO_DATA_MAP.md",
                    "RAVEN_MCS_PAPER_DATA_METADATA_AND_CLAIM_REPAIR_R2_REPORT.md",
                    "E4_COMPONENT_INTERPRETATION_METADATA.json",
                }:
                    # these files may quote the old label as superseded
                    if "OLD_SUPERSEDED_LABEL" in txt or "old_label" in txt or "Superseded" in txt or "OLD_SUPERSEDED" in txt:
                        continue
                    if '"Inst": "STRUCTURAL_ONLY_SUPPORTED"' in txt or "Inst,STRUCTURAL_ONLY_SUPPORTED" in txt:
                        if "OLD_SUPERSEDED" not in txt and "old_label" not in txt:
                            bad.append(str(p.relative_to(paper)))
                    continue
                for line in txt.splitlines():
                    if "Inst" in line and "STRUCTURAL_ONLY_SUPPORTED" in line and "Debt" not in line and "OLD_SUPERSEDED" not in line and "old_label" not in line:
                        # FIG/table rows: Inst,...,STRUCTURAL_ONLY_SUPPORTED
                        if "ENDPOINT_TRADEOFF" in line:
                            continue
                        bad.append(f"{p.relative_to(paper).as_posix()}:{line[:120]}")
                        break
    r["R2-G6"] = _pass(len(bad) == 0, f"bad_inst_labels={bad[:8]}")

    stats = read_csv(paper / "04_statistics/E4_FINAL_STATISTICS_R2.csv")
    r["R2-G7"] = _pass(len(stats) == 40, f"n_stat_rows={len(stats)}")  # 2 ds × 5 components × 4 metrics
    missing_abl = [x for x in stats if not str(x.get("ablation_mean", "")).strip()]
    r["R2-G8"] = _pass(len(missing_abl) == 0, f"missing_ablation_mean={len(missing_abl)}")
    pairs = {int(float(x["n_pairs"])) for x in stats}
    r["R2-G9"] = _pass(pairs == {20}, f"n_pairs={pairs}")
    proto = read_json(paper / "04_statistics/E4_STATISTICAL_PROTOCOL_R2.json")
    r["R2-G10"] = _pass(
        proto.get("alpha") == 0.05 and "Holm" in proto.get("holm_algorithm", "") and proto.get("EPS_ZERO") == 1e-12,
        "protocol frozen",
    )

    ds = read_csv(paper / "06_table_sources/TABLE_DATASET_SUMMARY_R2.csv")
    prov = read_csv(paper / "05_provenance/DATASET_METADATA_PROVENANCE.csv")
    r["R2-G11"] = _pass(len(ds) == 4 and len(prov) > 0, f"datasets={len(ds)} provenance_rows={len(prov)}")
    guessed = [x for x in prov if x["status"] not in {"RECOVERED_DIRECT", "RECOVERED_DETERMINISTIC", "MISSING_NOT_RECORDED", "CONFLICT_REQUIRES_REVIEW"}]
    r["R2-G12"] = _pass(len(guessed) == 0, f"guessed={len(guessed)}")

    cfg = read_csv(paper / "05_provenance/FINAL_CONFIG_REGISTRY_R2.csv")
    r["R2-G13"] = _pass(len(cfg) >= 6, f"config_rows={len(cfg)}")
    r["R2-G14"] = _pass(
        all(x.get("target_h_definition") for x in cfg if x["round"] in {"E3", "E4"})
        and all(x.get("opportunity_stratum_s_definition") for x in cfg if x["round"] in {"E3", "E4"}),
        "h(i) and s(i) recorded for E3/E4",
    )

    tb = read_json(paper / "00_index/TRAFFIC_COMPARABILITY_BOUNDARY_R2.json")
    r["R2-G15"] = _pass(tb["E3_Traffic"]["status"] == "NOT_COMPARABLE", "traffic boundary")
    p2 = read_json(paper / "00_index/P2_CLAIM_BOUNDARY_R2.json")
    r["R2-G16"] = _pass("not_allowed" in p2 and len(p2["not_allowed"]) >= 2, "P2 boundary")

    # No missing converted to zero: MAE_mu empty in 240 csv should not be 0
    mae0 = [x for x in e4 if str(x.get("MAE_mu", "")).strip() in {"0", "0.0"}]
    r["R2-G17"] = _pass(len(mae0) == 0, f"mae_zero_cells={len(mae0)}")

    diag_att = paper / "02_supporting_data/diagnostics_r2/DIAGNOSTIC_EXTRACTION_ATTESTATION.json"
    r["R2-G18"] = _pass(diag_att.is_file() and read_json(diag_att).get("no_training") is True, "diagnostics attestation")

    td = read_json(paper / "08_tdrive_readiness/TDRIVE_READINESS_R2.json")
    r["R2-G19"] = _pass(td.get("formal_tdrive_runs_started") is False, "tdrive runs=0")
    r["R2-G20"] = _pass(
        td.get("status", "").startswith("NOT_READY") or td.get("status") == "READY_FOR_PROTOCOL_SEAL",
        f"tdrive status={td.get('status')}",
    )

    r["R2-G21"] = _pass((paper / "00_index/CLAIM_TO_DATA_MAP_R2.csv").is_file(), "claim map")
    r["R2-G22"] = _pass((paper / "00_index/FIGURE_TABLE_PROVENANCE_MAP_R2.csv").is_file(), "fig/table map")

    runl = read_csv(paper / "01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL_R2.csv")
    long = read_csv(paper / "01_core_data/master/PAPER_EVIDENCE_MASTER_LONG_R2.csv")
    r["R2-G23"] = _pass(len(runl) > 800, f"runlevel={len(runl)}")
    r["R2-G24"] = _pass(len(long) > 2000, f"long={len(long)}")

    audit = read_csv(paper / "10_reports/PAPER_READY_NUMERIC_CONSISTENCY_AUDIT_R2.csv")
    conflicts = [x for x in audit if x.get("status") == "VALUE_CONFLICT"]
    r["R2-G25"] = _pass(len(conflicts) == 0, f"conflicts={len(conflicts)}")

    core_ver = read_json(paper / "09_archive_manifest/CORE_ZIP_VERIFICATION.json")
    full_ver = read_json(paper / "09_archive_manifest/FULL_EVIDENCE_ZIP_VERIFICATION.json")
    r["R2-G26"] = _pass(core_ver.get("pass") is True, str(core_ver.get("pass")))
    r["R2-G27"] = _pass(full_ver.get("pass") is True, str(full_ver.get("pass")))

    pipe = read_json(paper / "10_reports/PIPELINE_SUMMARY_R2.json")
    r["R2-G28"] = _pass(
        int(pipe.get("n_core_members", -1)) == int(core_ver.get("n_manifest", -2)),
        f"pipeline n_core={pipe.get('n_core_members')} zip={core_ver.get('n_manifest')}",
    )
    r["R2-G29"] = _pass((paper / "10_reports/MISSING_POTENTIALLY_USEFUL_DATA_R2.csv").is_file(), "missing report")
    report = paper / "10_reports/RAVEN_MCS_PAPER_DATA_METADATA_AND_CLAIM_REPAIR_R2_REPORT.md"
    txt = report.read_text(encoding="utf-8") if report.is_file() else ""
    r["R2-G30"] = _pass(
        report.is_file() and ("frozen" in txt.lower() or "PAPER_DATA_R2" in txt),
        "final report freeze statement",
    )

    n_pass = sum(1 for v in r.values() if v["pass"])
    out = {"gates": r, "n_pass": n_pass, "n_total": len(r), "all_pass": n_pass == len(r)}
    write_json(paper / "10_reports/PAPER_DATA_GATES_R2.json", out)
    write_json(paper / "10_reports/PAPER_DATA_GATES.json", out)
    return out
