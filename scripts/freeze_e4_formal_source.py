#!/usr/bin/env python3
"""Freeze E4 execution-critical source after smoke passes."""
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e4.constants import art_path
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json
FILES = ("src/raven_mcs/aggregation/method_policy.py", "src/raven_mcs/aggregation/methods.py",
         "src/raven_mcs/training/window_runner.py", "src/raven_mcs/e3/real_runner/runner.py",
         "src/raven_mcs/e4/execute.py")
if __name__ == "__main__":
    hashes={f:sha256_file(ROOT/f) for f in FILES}
    dump_json({"status":"FROZEN","source_hashes":hashes,
      "source_manifest_hash":hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),
      "created_utc":datetime.now(timezone.utc).isoformat()}, art_path(ROOT)/"E4_FORMAL_SOURCE_FREEZE.json")
