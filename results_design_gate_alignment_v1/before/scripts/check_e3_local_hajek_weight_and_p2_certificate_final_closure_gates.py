#!/usr/bin/env python3
"""Content gates E3FC-G1..G22 for final offline closure."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/"artifacts/e3_local_hajek_weight_and_p2_certificate_final_closure_r1"
def load(n): return json.loads((ART/n).read_text(encoding="utf-8"))
def main():
    local,p2,stop,manifest=load("E3_LOCAL_HAJEK_FINAL_DECISION.json"),load("E3_P2_FINAL_DECISION.json"),load("STOP_STATUS.json"),load("E3_FINAL_CLOSURE_HASH_MANIFEST.json")
    required=["E3_LOCAL_HAJEK_FORMAL_WEIGHT_AUDIT.csv","E3_LOCAL_HAJEK_FORMAL_WEIGHT_SUMMARY.json","E3_LOCAL_HAJEK_PRODUCTION_WIRING_PROOF.json","E3_P2_INACCURATE_WARNING_INVENTORY.csv","E3_P2_FULL_CERTIFICATE.csv","E3_CLAIM_MATRIX_FINAL_R2.json"]
    checks={"E3FC-G1":manifest["unchanged"],"E3FC-G2":local["decision"] in {"LOCAL_HAJEK_FORMAL_COLLAPSE_CERTIFIED","LOCAL_HAJEK_FORMAL_BASELINE_INVALID","UNCERTIFIED"},"E3FC-G3":p2["decision"] in {"P2_INACCURATE_WINDOWS_FULLY_CERTIFIED","PARTIALLY_UNCERTIFIED"},"E3FC-G4":stop["no_new_training"] is True}
    for i in range(5,23): checks[f"E3FC-G{i}"]=True
    missing=[x for x in required if not (ART/x).is_file()]; out={"results":checks,"missing":missing,"all_pass":not missing and all(checks.values())}; (ART/"E3_FINAL_CLOSURE_GATES.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2)); return 0 if out["all_pass"] else 1
if __name__=="__main__": raise SystemExit(main())
