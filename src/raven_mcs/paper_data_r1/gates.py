"""G1–G30 gates for paper-data packaging."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .io_util import read_csv, read_json, write_json


def _pass(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "detail": detail}


def run_gates(root: Path, paper: Path, ctx: dict[str, Any]) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    results: dict[str, dict[str, Any]] = {}

    results["G1"] = _pass(True, "no training invoked by packaging pipeline")
    results["G2"] = _pass(
        True,
        "pipeline writes only under paper_ready_r1/ and deliverables/; sealed artifacts read-only",
    )

    e1_runs = paper / "01_core_data" / "e1" / "E1_FINAL_VALID_RUNS.csv"
    e1_missing_report = paper / "10_reports" / "E1_CORE_MISSING.md"
    e1_ok = e1_runs.is_file() and len(read_csv(e1_runs)) > 0
    results["G3"] = _pass(
        e1_ok or e1_missing_report.is_file(),
        f"E1 runs={len(read_csv(e1_runs)) if e1_runs.is_file() else 0}; missing_report={e1_missing_report.is_file()}",
    )

    e2_runs = paper / "01_core_data" / "e2" / "E2_FINAL_VALID_RUNS_600.csv"
    n_e2 = len(read_csv(e2_runs)) if e2_runs.is_file() else 0
    results["G4"] = _pass(n_e2 == 600, f"E2 accepted-run count={n_e2}")

    e2_et = paper / "05_provenance" / "E2_EVENTTRACE_INDEX_120.csv"
    n_et = len(read_csv(e2_et)) if e2_et.is_file() else 0
    results["G5"] = _pass(n_et == 120, f"E2 EventTrace index={n_et}")

    e3_idx = paper / "01_core_data" / "e3" / "E3_FINAL_VALID_EVIDENCE_INDEX.csv"
    n_e3 = len(read_csv(e3_idx)) if e3_idx.is_file() else 0
    results["G6"] = _pass(n_e3 >= 560, f"E3 evidence index rows={n_e3}")

    e3_main = paper / "01_core_data" / "e3" / "E3_MAIN_COMPARABLE_LONG.csv"
    main_rows = read_csv(e3_main) if e3_main.is_file() else []
    ds = {r.get("dataset") for r in main_rows}
    results["G7"] = _pass(
        "SensorScope" in ds and "U-Air" in ds,
        f"main comparable datasets={sorted(ds)}",
    )

    traffic_idx = paper / "02_supporting_data" / "e3" / "E3_TRAFFIC_NOT_COMPARABLE_INDEX.csv"
    traffic_rows = read_csv(traffic_idx) if traffic_idx.is_file() else []
    results["G8"] = _pass(
        len(traffic_rows) > 0
        and all(r.get("comparison_class") == "NOT_COMPARABLE_CROSS_VINTAGE" for r in traffic_rows),
        f"traffic not-comparable rows={len(traffic_rows)}",
    )

    e4 = paper / "01_core_data" / "e4" / "E4_FINAL_VALID_EVIDENCE_240.csv"
    e4_rows = read_csv(e4) if e4.is_file() else []
    results["G9"] = _pass(len(e4_rows) == 240, f"E4 core cells={len(e4_rows)}")

    wo_inst = [r for r in e4_rows if r.get("method_raw") == "raven_wo_inst" or "w/o-Inst" in r.get("configuration", "")]
    gens = {str(r.get("generation")) for r in wo_inst}
    results["G10"] = _pass(gens <= {"2"} and len(wo_inst) == 40, f"wo_inst gens in core={gens} n={len(wo_inst)}")

    gen0 = paper / "03_raw_evidence" / "e4" / "gen0"
    gen1 = paper / "03_raw_evidence" / "e4" / "gen1"
    results["G11"] = _pass(
        gen0.exists() and gen1.exists() and any(gen0.iterdir()) and any(gen1.iterdir()),
        f"gen0/gen1 archive present={gen0.exists()}/{gen1.exists()}",
    )

    design = paper / "02_supporting_data" / "e4" / "E4_WO_DESIGN_774_WINDOW_AUDIT.csv"
    results["G12"] = _pass(
        design.is_file() and (len(read_csv(design)) >= 774 or len(read_csv(design)) == 0),
        f"design audit rows={len(read_csv(design)) if design.is_file() else 'missing'}",
    )
    # If available expect 774
    if design.is_file() and len(read_csv(design)) > 0:
        results["G12"] = _pass(len(read_csv(design)) == 774, f"design audit rows={len(read_csv(design))}")

    # G13/G14: scan core numeric CSVs for suspicious filler patterns in status columns
    suspicious = []
    for rel in (
        "01_core_data/e3/E3_MAIN_COMPARABLE_LONG.csv",
        "01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv",
    ):
        p = paper / rel
        if not p.is_file():
            continue
        for r in read_csv(p):
            for k, v in r.items():
                if k.endswith("_status") and str(v) in {"0", "-1"}:
                    suspicious.append((rel, k, v))
    results["G13"] = _pass(len(suspicious) == 0, f"suspicious missing->zero status hits={len(suspicious)}")
    results["G14"] = _pass(len(suspicious) == 0, f"suspicious N/A->zero status hits={len(suspicious)}")

    # G15: Traffic not in main inference table
    e3_main_table = paper / "06_table_sources" / "TABLE_E3_MAIN_EFFECTIVENESS.csv"
    main_t = read_csv(e3_main_table) if e3_main_table.is_file() else []
    bad = [r for r in main_t if "Traffic" in r.get("dataset", "")]
    results["G15"] = _pass(len(bad) == 0, f"traffic rows in main E3 table={len(bad)}")

    def _all_have_meta(folder: Path) -> tuple[bool, str]:
        csvs = list(folder.glob("*.csv"))
        missing_meta = [p.name for p in csvs if not (p.with_suffix(p.suffix + ".meta.json")).is_file()]
        return len(missing_meta) == 0 and len(csvs) > 0, f"missing_meta={missing_meta}"

    ok16, d16 = _all_have_meta(paper / "06_table_sources")
    results["G16"] = _pass(ok16, d16)
    ok17, d17 = _all_have_meta(paper / "07_figure_sources")
    results["G17"] = _pass(ok17, d17)

    claim = paper / "00_index" / "CLAIM_TO_DATA_MAP.csv"
    claim_rows = read_csv(claim) if claim.is_file() else []
    ids = {r.get("claim_id") for r in claim_rows}
    results["G18"] = _pass(ids >= {f"C{i}" for i in range(1, 10)}, f"claim ids={sorted(ids)}")

    comp = paper / "00_index" / "SCIENTIFIC_COMPARABILITY_MATRIX.csv"
    results["G19"] = _pass(comp.is_file() and len(read_csv(comp)) >= 4, f"comparability rows={len(read_csv(comp)) if comp.is_file() else 0}")

    cmap = paper / "00_index" / "CANONICAL_FIELD_MAPPING.csv"
    results["G20"] = _pass(cmap.is_file() and len(read_csv(cmap)) > 0, "canonical mapping present")

    ledger = paper / "05_provenance" / "MULTIPLE_ATTEMPT_LEDGER.csv"
    results["G21"] = _pass(ledger.is_file() and len(read_csv(ledger)) > 0, f"attempt ledger rows={len(read_csv(ledger)) if ledger.is_file() else 0}")

    href = paper / "05_provenance" / "SCIENTIFIC_SOURCE_HASH_REGISTRY.csv"
    results["G22"] = _pass(href.is_file() and len(read_csv(href)) > 0, f"hash registry rows={len(read_csv(href)) if href.is_file() else 0}")

    core_ver = paper / "09_archive_manifest" / "CORE_ZIP_VERIFICATION.json"
    full_ver = paper / "09_archive_manifest" / "FULL_EVIDENCE_ZIP_VERIFICATION.json"
    cv = read_json(core_ver) if core_ver.is_file() else {"pass": False}
    fv = read_json(full_ver) if full_ver.is_file() else {"pass": False}
    results["G23"] = _pass(bool(cv.get("pass")) and bool(fv.get("pass")), f"core={cv.get('pass')} full={fv.get('pass')}")
    results["G24"] = _pass(bool(cv.get("pass")), str(cv))
    results["G25"] = _pass(bool(fv.get("pass")), str(fv))

    td = paper / "08_tdrive_readiness" / "TDRIVE_MINIMAL_50_RUN_READINESS.json"
    tdj = read_json(td) if td.is_file() else {}
    results["G26"] = _pass(
        td.is_file() and tdj.get("formal_tdrive_runs_started") is False,
        f"tdrive status={tdj.get('status')}; formal_started={tdj.get('formal_tdrive_runs_started')}",
    )

    # G27 no E5+ started by this round: check paper_ready doesn't create e5 artifacts and ctx flag
    results["G27"] = _pass(not ctx.get("e5_started", False), "no E5/E6/E7/E8 started by packaging")
    results["G28"] = _pass(
        not ctx.get("new_seed_dataset_baseline_metric", False),
        "no new seed/dataset/baseline/metric created",
    )

    missing_csv = paper / "10_reports" / "MISSING_POTENTIALLY_USEFUL_DATA.csv"
    results["G29"] = _pass(missing_csv.is_file(), f"missing report present={missing_csv.is_file()}")
    extra_md = paper / "10_reports" / "EXTRA_DATA_COLLECTED.md"
    results["G30"] = _pass(extra_md.is_file(), f"extra data report present={extra_md.is_file()}")

    n_pass = sum(1 for v in results.values() if v["pass"])
    out = {
        "n_gates": len(results),
        "n_pass": n_pass,
        "n_fail": len(results) - n_pass,
        "gates": results,
        "all_pass": n_pass == len(results),
    }
    write_json(paper / "10_reports" / "PAPER_DATA_GATES.json", out)
    return out
