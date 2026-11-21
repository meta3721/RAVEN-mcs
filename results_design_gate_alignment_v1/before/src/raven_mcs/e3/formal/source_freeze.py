"""E3 formal source freeze, including execution-critical modules."""
from __future__ import annotations
import hashlib, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

SOURCE_FILES = (
    "src/raven_mcs/e3/real_runner/runner.py",
    "src/raven_mcs/e3/real_runner/central_real.py",
    "src/raven_mcs/e3/canary/execute.py",
    "src/raven_mcs/e3/canary/dataset_load.py",
    "src/raven_mcs/e3/formal/execute.py",
    "src/raven_mcs/e3/formal/eventtrace.py",
    "src/raven_mcs/e3/formal/metric_scale.py",
    "src/raven_mcs/e3/target_pair/target_wiring.py",
    "src/raven_mcs/e3/stratum_seal/remap.py",
    "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py",
    "src/raven_mcs/e3/delta_cs_rho/atomic_rho.py",
    "src/raven_mcs/e3/numerical/finite.py",
    "src/raven_mcs/training/window_runner.py",
    "src/raven_mcs/aggregation/methods.py",
)


def _hashes(root: Path) -> dict[str, str | None]:
    return {p: sha256_file(root / p) if (root / p).is_file() else None for p in SOURCE_FILES}


def build(root: Path) -> dict:
    hashes = _hashes(root)
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
    except OSError:
        commit = None
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root, text=True
        )
    except OSError:
        status = ""
    return {
        "round": "E3-FORMAL-RUNS-R1",
        "status": "FROZEN",
        "git_commit": commit,
        "git_status_porcelain": status,
        "source_hashes": hashes,
        "source_manifest_hash": hashlib.sha256(
            json.dumps(hashes, sort_keys=True).encode()
        ).hexdigest(),
        "runner_source_hash": hashes.get("src/raven_mcs/e3/real_runner/runner.py"),
        "method_source_hash": hashes.get("src/raven_mcs/training/window_runner.py"),
        "target_code_hash": hashes.get("src/raven_mcs/e3/target_pair/target_wiring.py"),
        "stratum_code_hash": hashes.get("src/raven_mcs/e3/stratum_seal/remap.py"),
        "delta_cs_code_hash": hashes.get("src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py"),
        "atomic_rho_code_hash": hashes.get("src/raven_mcs/e3/delta_cs_rho/atomic_rho.py"),
        "metric_code_hash": hashes.get("src/raven_mcs/e3/numerical/finite.py"),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {
            "numpy": __import__("numpy").__version__,
            "pandas": __import__("pandas").__version__,
            "torch": __import__("torch").__version__,
        },
        "code_must_not_change_after_freeze": True,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
def write(root: Path, art: Path) -> dict:
    payload = build(root); dump_json(payload, art / "E3_FORMAL_SOURCE_FREEZE.json"); return payload
def verify(root: Path, payload: dict) -> list[str]:
    return [f"source_hash_mismatch:{p}" for p, h in payload.get("source_hashes", {}).items() if _hashes(root).get(p) != h]
