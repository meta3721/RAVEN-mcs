"""Source-provenance helpers for the clean numerical-integrity canary."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from raven_mcs.e3.numerical.constants import ROUND, SOURCE_FREEZE_FILE
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

SOURCE_FILES = (
    "src/raven_mcs/e3/numerical/finite.py",
    "src/raven_mcs/e3/canary/dataset_load.py",
    "src/raven_mcs/e3/canary/execute.py",
    "src/raven_mcs/e3/real_runner/runner.py",
    "src/raven_mcs/e3/real_runner/central_real.py",
    "src/raven_mcs/training/window_runner.py",
    "src/raven_mcs/e3/canary/constants.py",
    "src/raven_mcs/e3/canary/schedule.py",
)


def get_git_commit(root: Path) -> str | None:
    """Return HEAD revision, preserving a usable payload outside git."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def get_git_status(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root, text=True, stderr=subprocess.DEVNULL
        )
    except (OSError, subprocess.CalledProcessError):
        return ""


def hash_source_files(root: Path, files: Iterable[str] = SOURCE_FILES) -> dict[str, str | None]:
    return {
        str(rel).replace("\\", "/"): sha256_file(root / rel) if (root / rel).is_file() else None
        for rel in files
    }


def source_manifest_hash(source_hashes: dict[str, str | None]) -> str:
    payload = json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_source_freeze_payload(root: Path, *, force: bool = False) -> dict[str, Any]:
    hashes = hash_source_files(root)
    return {
        "round": ROUND,
        "status": "FROZEN",
        "git_commit": get_git_commit(root),
        "git_status_porcelain": get_git_status(root),
        "source_hashes": hashes,
        "source_manifest_hash": source_manifest_hash(hashes),
        "method_source_hash": hashes.get("src/raven_mcs/aggregation/methods.py")
        or hashes.get("src/raven_mcs/training/window_runner.py"),
        "runner_source_hash": hashes.get("src/raven_mcs/e3/real_runner/runner.py"),
        "force_clean_run": bool(force),
        "code_must_not_change_after_freeze": True,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }


def verify_freeze_matches_workspace(root: Path, freeze: dict[str, Any]) -> list[str]:
    """Return mismatch messages if workspace drifted after freeze."""
    issues: list[str] = []
    current = hash_source_files(root)
    for rel, expected in (freeze.get("source_hashes") or {}).items():
        got = current.get(rel)
        if got != expected:
            issues.append(f"source_hash_mismatch:{rel}")
    if freeze.get("git_commit") and freeze.get("git_commit") != get_git_commit(root):
        issues.append("git_commit_mismatch")
    return issues


def load_freeze(art: Path) -> dict[str, Any] | None:
    path = Path(art) / SOURCE_FREEZE_FILE
    if not path.is_file():
        return None
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def write_source_freeze(root: Path, art: Path, *, force: bool = False) -> dict[str, Any]:
    payload = build_source_freeze_payload(root, force=force)
    dump_json(payload, Path(art) / SOURCE_FREEZE_FILE)
    (Path(art) / "E3_CLEAN_CANARY_CODE_CHANGE_LOCK.md").write_text(
        "# Source freeze lock\n\nCode must not change after this source freeze. "
        "A changed hash requires a new preparation and freeze.\n",
        encoding="utf-8",
    )
    return payload
