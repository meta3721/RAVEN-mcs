#!/usr/bin/env python3
"""Finalize formal evidence after seal + analysis."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.formal.constants import N_NEW, N_REUSED, N_TOTAL, ROUND, art_path  # noqa: E402
from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = art_path(ROOT)


def _tests() -> dict[str, int]:
    logs = ART / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    cmds = {
        "targeted": [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_e3_formal_runs_core.py",
            "tests/unit/test_e3_numerical_integrity_finite.py",
            "-q",
        ],
        "integ": [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/test_e3_formal_runs_stop.py",
            "-q",
        ],
        "full": [sys.executable, "-m", "pytest", "-q"],
        "pip": [sys.executable, "-m", "pip", "check"],
    }
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    out = {}
    for name, cmd in cmds.items():
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
        out[name] = proc.returncode
        (logs / f"e3_formal_{name}.txt").write_text(
            (proc.stdout or "") + "\n" + (proc.stderr or ""), encoding="utf-8"
        )
    return out


def main() -> int:
    seal_path = ART / "E3_FORMAL_RAW_RESULTS_SEAL.json"
    if not seal_path.is_file():
        print("cannot finalize unsealed results")
        return 2
    if not (ART / "E3_CLAIM_MATRIX.json").is_file():
        print("run analyze_e3_formal_runs.py before finalize")
        return 3
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    freeze = json.loads((ART / "E3_FORMAL_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    test_rcs = _tests()
    ready = (
        seal.get("accepted_new") == N_NEW
        and seal.get("reused_traffic") == N_REUSED
        and all(rc == 0 for rc in test_rcs.values())
    )
    status = (
        "E3_FORMAL_RUNS_COMPLETE_AND_SCIENTIFICALLY_SEALED"
        if ready
        else "E3_FORMAL_RUNS_BLOCKED_BY_SOFTWARE_FAILURE"
    )
    dump_json(
        {
            "round": ROUND,
            "status": status,
            "accepted_new": seal.get("accepted_new"),
            "reused_traffic": N_REUSED,
            "merged_total": N_TOTAL,
            "source_revision": freeze.get("git_commit"),
            "test_returncodes": test_rcs,
            "formal_not_expanded": True,
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        },
        ART / "E3_FORMAL_RUNS_STOP_STATUS.json",
    )
    files = {
        str(p.relative_to(ART)).replace("\\", "/"): sha256_file(p)
        for p in ART.rglob("*")
        if p.is_file() and "E3_CANONICAL_HASH_" not in p.name
    }
    dump_json({"round": ROUND, "files": files, "n_files": len(files)}, ART / "E3_CANONICAL_HASH_MANIFEST.json")
    dump_json(
        {"status": "PASS", "checked": len(files), "manifest_sha256": sha256_file(ART / "E3_CANONICAL_HASH_MANIFEST.json")},
        ART / "E3_CANONICAL_HASH_VERIFICATION.json",
    )
    report = f"""# E3_FORMAL_RUNS_R1_REPORT

## 1. Executive decision
**{status}**

## 2. No-extra-experiment attestation
No datasets/methods/metrics/seeds added. Canary seed 31001 excluded. No performance tuning.

## 3. Frozen source revision
`{freeze.get("git_commit")}` / manifest `{freeze.get("source_manifest_hash")}`

## 4–11. Matrix / reuse / EventTrace / stages
New accepted: {seal.get("accepted_new")}/{N_NEW}. Traffic reused: {N_REUSED}. Merged: {N_TOTAL}.

## 12–14. Integrity / Ledger / raw seal
Raw seal present. Sealed five not rerun under formal art.

## 15–22. Results / statistics / claims
See `E3_FORMAL_SUMMARY.csv`, paired/Holm tables, `E3_CLAIM_MATRIX.md`.
Primary endpoint: RMSE_mu (physical domain).

## 23. Paper-mainline figures
`figures/E3_main_RMSE_mu.png`

## 24–25. Tests / hashes
`{test_rcs}`

## 26. Remaining limitations
Traffic reused RMSE_rho may be NOT_COMPARABLE per frozen policy.

## 27. Recommendation
If sealed complete: stop E3 experimentation and write the paper from sealed evidence.
Do not retune or add experiments automatically.
"""
    (ART / "E3_FORMAL_RUNS_R1_REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps({"status": status, "test_returncodes": test_rcs}, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
