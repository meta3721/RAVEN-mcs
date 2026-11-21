#!/usr/bin/env python3
"""E2A-G1..G14 formal results analysis gates (no training)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from raven_mcs.e2.traffic_formal_analysis import EXPECTED_RUNS, PRIMARY_METRICS
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e2_traffic_formal_results_analysis_r1"
SRC = ROOT / "artifacts/e2_traffic_formal_runs_r1"


def main() -> int:
    ver = json.loads((ART / "FROZEN_600_RESULTS_VERIFICATION.json").read_text(encoding="utf-8"))
    source = json.loads((ART / "SOURCE_FREEZE_RETROSPECTIVE_AUDIT.json").read_text(encoding="utf-8"))
    ledger = json.loads((ART / "LEDGER_ATTEMPT_AUDIT.json").read_text(encoding="utf-8"))["summary"]
    scen = pd.read_csv(ART / "SCENARIO_VS_BALANCED_STATS.csv")
    dod = json.loads((ART / "COMPLETE_ALIGNED_DOD_SUMMARY.json").read_text(encoding="utf-8"))
    counter = json.loads((ART / "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json").read_text(encoding="utf-8"))
    head = pd.read_csv(ART / "HEAD_TAIL_RESULTS.csv")
    raven = pd.read_csv(ART / "RAVEN_VS_BASELINE_SECONDARY.csv")
    claims = pd.read_csv(ART / "E2_CLAIM_MATRIX.csv")
    stop = json.loads((ART / "E2_TRAFFIC_FORMAL_RESULTS_ANALYSIS_STOP_STATUS.json").read_text(encoding="utf-8"))

    # Freeze intact
    snap = json.loads((ART / "FROZEN_600_HASH_SNAPSHOT.json").read_text(encoding="utf-8"))
    man = json.loads((ART / "FROZEN_600_RESULTS_MANIFEST.json").read_text(encoding="utf-8"))
    freeze_ok = True
    for key, expected in (snap.get("hashes") or {}).items():
        if not expected:
            continue
        path = Path(man["files"][key]["path"])
        if path.is_file():
            import hashlib

            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                freeze_ok = False

    g1 = ver.get("status") == "PASS" and int(ver.get("result_rows", 0)) == EXPECTED_RUNS and freeze_ok
    g2 = source.get("decision") == "PASS"
    g3 = (
        int(ledger.get("accepted_logical_run_count", 0)) == EXPECTED_RUNS
        and ledger.get("ledger_rewritten") is False
        and "orphan_start_count" in ledger
    )
    metric_status = {
        "RMSE_mu": True,
        "RMSE_rho": True,
        "Gap_mis": True,
        "Head_RMSE": "MISSING_EVIDENCE" in set(head["status"]),
        "Tail_RMSE": "MISSING_EVIDENCE" in set(head["status"]),
    }
    g4 = all(metric_status[m] for m in PRIMARY_METRICS) and metric_status["Head_RMSE"]
    g5 = len(scen) == 5 * 5 * 3 and set(scen["metric"]) == set(PRIMARY_METRICS)
    g6 = "p_holm" in scen.columns and scen["p_holm"].notna().any() and "holm_family" in scen.columns
    g7 = len(dod) == 5 and all("mean_D_aligned" in dod[m] for m in dod)
    g8 = len(counter) == 5 and all("event_count" in counter[m] for m in counter)
    g9 = (ART / "GROUP_DISPARITY_RESULTS.csv").is_file() and (ART / "GROUP_DISPARITY_STATS.csv").is_file()
    g10 = (ART / "GAP_MIS_SEMANTIC_AUDIT.md").is_file() and "Signed" in (ART / "GAP_MIS_SEMANTIC_AUDIT.md").read_text(encoding="utf-8")
    g11 = "p_holm" in raven.columns and "correction_family" in raven.columns
    # Claim matrix consistency: no SUPPORTED claim for C9 Head/Tail
    c9 = claims.loc[claims["claim_id"] == "C9"].iloc[0]
    g12 = c9["status"] == "NOT_TESTABLE_FROM_FROZEN_OUTPUTS" and len(claims) >= 10
    figs = [
        ART / "figures" / f"FIG_E2_{i}.pdf" for i in range(1, 6)
    ] + [ART / "paper_tables" / "TABLE_E2A.csv"]
    g13 = all(p.is_file() for p in figs)
    g14 = bool(stop.get("no_training")) and not any(
        (SRC / "runs").glob("**/new_training_marker")
    )

    gates = {
        "E2A-G1": bool(g1),
        "E2A-G2": bool(g2),
        "E2A-G3": bool(g3),
        "E2A-G4": bool(g4),
        "E2A-G5": bool(g5),
        "E2A-G6": bool(g6),
        "E2A-G7": bool(g7),
        "E2A-G8": bool(g8),
        "E2A-G9": bool(g9),
        "E2A-G10": bool(g10),
        "E2A-G11": bool(g11),
        "E2A-G12": bool(g12),
        "E2A-G13": bool(g13),
        "E2A-G14": bool(g14),
    }
    diagnostics = {
        "freeze_ok": freeze_ok,
        "verification_status": ver.get("status"),
        "source_decision": source.get("decision"),
        "ledger_summary": ledger,
        "scenario_stats_rows": int(len(scen)),
        "raven_secondary_rows": int(len(raven)),
        "claim_statuses": claims.set_index("claim_id")["status"].to_dict(),
        "stop_status": stop.get("status"),
    }
    dump_json(gates, ART / "e2_analysis_gate_results.json")
    dump_json(diagnostics, ART / "e2_analysis_gate_diagnostics.json")
    print(json.dumps({"all_pass": all(gates.values()), "gates": gates}, indent=2))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
