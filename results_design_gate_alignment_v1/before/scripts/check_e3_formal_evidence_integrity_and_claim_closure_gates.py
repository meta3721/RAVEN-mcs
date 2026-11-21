#!/usr/bin/env python3
"""Hard, content-based E3IC-G1..G23 closure gates."""
from __future__ import annotations
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e3.evidence_closure.constants import ART_RELATIVE_PATH, EPS_ZERO  # noqa: E402
ART, PARENT = ROOT / ART_RELATIVE_PATH, ROOT / "artifacts/e3_formal_runs_r1"

def load(name: str) -> dict:
    path = ART / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
def rows(name: str) -> list[dict]:
    path = ART / name
    return list(csv.DictReader(path.open(encoding="utf-8"))) if path.is_file() else []
def main() -> int:
    parent = json.loads((PARENT / "E3_FORMAL_RUNS_STOP_STATUS.json").read_text(encoding="utf-8"))
    local, identity, policy, p2 = load("E3_LOCAL_HAJEK_WIRING_AUDIT.json"), load("E3_TRAFFIC_E2_E3_SCIENTIFIC_IDENTITY_AUDIT.json"), load("E3_TRAFFIC_CROSS_VINTAGE_COMPARISON_POLICY.json"), load("E3_P2_SOLVER_CERTIFICATE_AUDIT.json")
    freeze, domains, claims, stop = load("E3_SECONDARY_HOLM_FAMILY_FREEZE.json"), load("E3_METRIC_DOMAIN_REGISTRY_FINAL.json"), load("E3_CLAIM_MATRIX_FINAL.json"), load("STOP_STATUS.json")
    required = ["E3_LOCAL_HAJEK_GRADIENT_TEST.json", "E3_P2_FROZEN_TOLERANCE_AUDIT.json", "E3_SECONDARY_SUMMARY.csv", "E3_SECONDARY_PAIRED_TESTS.csv", "E3_SECONDARY_HOLM_RESULTS.csv", "E3_SECONDARY_EFFECT_SIZES.csv", "E3_CLAIM_MATRIX_FINAL.md", "E3_PAPER_MAINLINE_EVIDENCE_SYNTHESIS.md", "E3_NEED_FOR_ANY_ADDITIONAL_EXPERIMENT.json", "E3_FORMAL_EVIDENCE_INTEGRITY_AND_CLAIM_CLOSURE_R1_REPORT.md"]
    result = {
      "E3IC-G1": parent.get("accepted_new") == 560 and (PARENT / "E3_FORMAL_RAW_RESULTS_SEAL.json").is_file(),
      "E3IC-G2": stop.get("no_new_training") is True,
      "E3IC-G3": load("E3_LOCAL_HAJEK_GRADIENT_TEST.json").get("status") == "PASS",
      "E3IC-G4": local.get("classification") in {"LOCAL_HAJEK_IMPLEMENTATION_VALID", "LOCAL_HAJEK_FORMAL_BASELINE_INVALID", "LOCAL_HAJEK_IDENTITY_UNRESOLVED"},
      "E3IC-G5": bool(identity.get("checks")), "E3IC-G6": identity.get("decision") == "TRAFFIC_RMSE_MU_NOT_COMPARABLE_ACROSS_SOURCE_VINTAGES",
      "E3IC-G7": set(policy) >= {"RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE", "Delta_group", "Delta_c_s", "RMSE_rho"},
      "E3IC-G8": p2.get("n_windows", 0) > 0, "E3IC-G9": bool(p2.get("records")),
      "E3IC-G10": p2.get("final_decision") in {"P2_FORMAL_EVIDENCE_CERTIFIED", "P2_FORMAL_EVIDENCE_PARTIALLY_UNCERTIFIED", "P2_FORMAL_EVIDENCE_INVALID"},
      "E3IC-G11": any(r.get("metric") == "Tail_RMSE_phys" for r in rows("E3_SECONDARY_SUMMARY.csv")),
      "E3IC-G12": any(r.get("metric") == "Delta_group" for r in rows("E3_SECONDARY_SUMMARY.csv")),
      "E3IC-G13": any(r.get("metric") == "Delta_c_s" for r in rows("E3_SECONDARY_SUMMARY.csv")),
      "E3IC-G14": freeze.get("EPS_ZERO") == EPS_ZERO and bool(freeze.get("families")),
      "E3IC-G15": freeze.get("EPS_ZERO") == 1e-12,
      "E3IC-G16": not any(r.get("dataset") == "traffic" for r in rows("E3_SECONDARY_PAIRED_TESTS.csv")),
      "E3IC-G17": domains.get("Delta_group", "").startswith("DIMENSIONLESS") and domains.get("Delta_c_s", "").startswith("DIMENSIONLESS"),
      "E3IC-G18": set(claims) == {"C1", "C2", "C3", "C4", "C5"},
      "E3IC-G19": (ART / "E3_PAPER_MAINLINE_EVIDENCE_SYNTHESIS.md").is_file(),
      "E3IC-G20": load("E3_NEED_FOR_ANY_ADDITIONAL_EXPERIMENT.json").get("decision") == "NO_ADDITIONAL_EXPERIMENT_NEEDED",
      "E3IC-G21": load("E3_EVIDENCE_CLOSURE_HASH_VERIFICATION.json").get("parent_formal_accepted") == 560,
      "E3IC-G22": load("E3_LOCAL_HAJEK_GRADIENT_TEST.json").get("status") == "PASS",
      "E3IC-G23": load("E3_EVIDENCE_CLOSURE_HASH_VERIFICATION.json").get("status") == "PASS",
    }
    missing = [x for x in required if not (ART / x).is_file()]
    out = {"results": result, "missing_required": missing, "failed": [k for k, v in result.items() if not v] + missing}
    out["all_pass"] = not out["failed"]; (ART / "E3_FORMAL_EVIDENCE_INTEGRITY_GATES.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2)); return 0 if out["all_pass"] else 1
if __name__ == "__main__": raise SystemExit(main())
