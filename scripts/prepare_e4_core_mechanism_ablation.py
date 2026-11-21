#!/usr/bin/env python3
"""Prepare E4 only; does not execute scientific runs."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e4.constants import ROUND, art_path
from raven_mcs.e4.matrix import build_matrix
from raven_mcs.e4.reference_audit import audit
from raven_mcs.e4.semantics import freeze
from raven_mcs.utils.serialization import dump_json
def main():
    art = art_path(ROOT); art.mkdir(parents=True, exist_ok=True)
    refs = audit(ROOT); dump_json(freeze(), art / "E4_ABLATION_SEMANTICS_FREEZE.json")
    dump_json(refs, art / "E4_FULL_RAVEN_REFERENCE_IDENTITY_AUDIT.json")
    dump_json(refs, art / "E4_EVENTTRACE_IDENTITY_AUDIT.json")
    dump_json(build_matrix(), art / "E4_FORMAL_RUN_MATRIX.json")
    dump_json({"round": ROUND, "status": "PREPARED", "smoke_ready": True,
               "formal_execution_started": False}, art / "E4_STOP_STATUS.json")
    return 0 if refs["status"] == "PASS" else 2
if __name__ == "__main__": raise SystemExit(main())
