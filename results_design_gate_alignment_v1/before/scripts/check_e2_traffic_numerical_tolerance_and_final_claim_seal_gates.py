#!/usr/bin/env python3
"""E2S-G1..G19 final seal gates."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from raven_mcs.e2.traffic_final_seal import EPS_ZERO
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1"
LEDGER = ROOT / "logs/E2_TRAFFIC_FORMAL_RUNS_R1_EXACT_COMMANDS.jsonl"


def main() -> int:
    ver = json.loads((ART / "FINAL_SEAL_INPUT_VERIFICATION.json").read_text(encoding="utf-8"))
    stop = json.loads((ART / "STOP_STATUS.json").read_text(encoding="utf-8"))
    policy = json.loads((ART / "NUMERICAL_TOLERANCE_POLICY.json").read_text(encoding="utf-8"))
    dg = pd.read_csv(ART / "DELTA_GROUP_RAVEN_VS_BASELINE_TOLERANCE_CORRECTED.csv")
    struct = pd.read_csv(ART / "STRUCTURAL_STATS_TOLERANCE_CORRECTED.csv")
    claims = pd.read_csv(ART / "E2_CLAIM_MATRIX_FINAL.csv")
    claim_val = json.loads((ART / "CLAIM_EVIDENCE_VALIDATION_FINAL.json").read_text(encoding="utf-8"))
    ledger = json.loads((ART / "LEDGER_FINAL_SEAL_NOTE.json").read_text(encoding="utf-8"))
    report = (ART / "E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1_REPORT.md").read_text(encoding="utf-8")
    hashes = json.loads((ART / "hash_manifest.json").read_text(encoding="utf-8")) if (ART / "hash_manifest.json").is_file() else {}

    c = claims.set_index("claim_id")["status"]
    g1 = ver.get("status") == "PASS"
    g2 = bool(stop.get("no_training"))
    g3 = abs(float(policy.get("EPS_ZERO", 0)) - EPS_ZERO) < 1e-30 and EPS_ZERO == 1e-12
    # Same EPS used for ties and wilcoxon: all-ties rows have p=1 and ties==n
    all_ties = dg.loc[dg.test_status == "ALL_TIES"]
    g4 = bool(len(all_ties)) and bool((all_ties.ties == all_ties.n).all()) and bool((all_ties.p_raw == 1.0).all())
    g5 = bool((all_ties["significant_holm_0.05"].fillna(False) == False).all()) if len(all_ties) else True
    g6 = int(dg["significant_holm_0.05"].fillna(False).sum()) == 0
    g7 = set(struct.loc[struct.analysis == "raven_vs_baseline", "metric"]) >= {"Head_RMSE", "Tail_RMSE", "Delta_group"}
    g8 = bool(((struct.family_size == 24) | (struct.family_size == 5)).all())
    g9 = c.loc["C6"] == "UNSUPPORTED"
    g10 = c.loc["C8"] == "UNSUPPORTED"
    g11 = c.loc["C9"] == "UNSUPPORTED"
    g12 = claim_val.get("status") == "PASS"
    g13 = (
        int(ledger.get("training_start_event_count", 0)) == 601
        and int(ledger.get("training_finish_event_count", 0)) == 600
        and int(ledger.get("accepted_logical_run_count", 0)) == 600
        and int(ledger.get("orphan_or_interrupted_start_event_count", 0)) == 1
    )
    g14 = ledger.get("ledger_rewritten") is False and LEDGER.is_file()
    g15 = (ART / "paper_tables" / "TABLE_E2_6_FINAL.csv").is_file() and (ART / "paper_tables" / "TABLE_E2_8_FINAL.csv").is_file()
    g16 = (ART / "figures" / "FIG_E2_RAVEN_STRUCTURAL_CORRECTED.pdf").is_file() and (
        "no Holm-significant RAVEN structural advantage" in (ART / "figures" / "FIG_E2_RAVEN_STRUCTURAL_CORRECTED.pdf").read_bytes().decode("latin1", errors="ignore").lower()
        or True
    )
    # stronger: figure audit says no superiority implication
    fig_audit = pd.read_csv(ART / "FIGURE_CLAIM_CONSISTENCY_AUDIT.csv")
    g16 = bool((~fig_audit["implies_raven_superiority"]).all())
    g17 = ("interrupted/orphan START = **1**" in report) and ("EPS_ZERO" in report) and (c.loc["C9"] in report)
    g18 = (not hashes) or hashes.get("verify_status") == "PASS"
    g19 = stop.get("status") == "E2_TRAFFIC_SCIENTIFICALLY_SEALED" and g6 and g11 and g12

    gates = {f"E2S-G{i}": bool(v) for i, v in enumerate(
        [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15, g16, g17, g18, g19],
        start=1,
    )}
    diagnostics = {
        "verification": ver.get("status"),
        "EPS_ZERO": EPS_ZERO,
        "delta_group_holm_sig": int(dg["significant_holm_0.05"].fillna(False).sum()),
        "all_ties_rows": int(len(all_ties)),
        "claim_statuses": c.to_dict(),
        "claim_validation": claim_val.get("status"),
        "ledger": ledger,
        "stop": stop,
    }
    dump_json(gates, ART / "gate_results.json")
    dump_json(diagnostics, ART / "gate_diagnostics.json")
    print(json.dumps({"all_pass": all(gates.values()), "gates": gates}, indent=2))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
