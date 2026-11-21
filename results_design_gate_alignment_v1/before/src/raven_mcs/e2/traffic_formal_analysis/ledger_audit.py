"""Attempt-level ledger audit (does not rewrite historical ledger)."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.e2.traffic_formal_analysis import EXPECTED_RUNS, FORMAL_SEEDS, METHODS, SCENARIOS


def load_ledger(path: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    corrupt = 0
    if not path.is_file():
        return rows, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            corrupt += 1
    return rows, corrupt


def attempt_audit(
    ledger_path: Path,
    runs_root: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows, corrupt = load_ledger(ledger_path)
    training = [r for r in rows if r.get("run_kind") == "training"]
    by_run_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in training:
        rid = str(r.get("run_id") or "")
        by_run_id[rid].append(r)

    records = []
    for run_id, events in sorted(by_run_id.items()):
        starts = [e for e in events if e.get("record_type") == "START"]
        finishes = [e for e in events if e.get("record_type") == "FINISH"]
        seed = starts[0].get("seed") if starts else (finishes[0].get("seed") if finishes else None)
        scenario = starts[0].get("scenario") if starts else (finishes[0].get("scenario") if finishes else None)
        method = starts[0].get("method") if starts else (finishes[0].get("method") if finishes else None)
        attempt = None
        if run_id and "__attempt" in run_id:
            try:
                attempt = int(run_id.rsplit("__attempt", 1)[-1])
            except ValueError:
                attempt = None
        exit_codes = [int(f.get("exit_code", 1)) for f in finishes]
        success = any(c == 0 for c in exit_codes)
        orphan_start = len(starts) > len(finishes)
        orphan_finish = len(finishes) > len(starts)
        interrupted = orphan_start and not success
        # Checkpoint / manifest hashes from accepted artifacts when present
        ckpt_hash = None
        man_hash = None
        if seed is not None and scenario and method:
            man_path = runs_root / str(seed) / str(scenario) / str(method) / "runtime_manifest.json"
            ckpt_path = runs_root / str(seed) / str(scenario) / str(method) / "checkpoints" / "final.pt"
            if man_path.is_file():
                import hashlib

                man_hash = hashlib.sha256(man_path.read_bytes()).hexdigest()
                man = json.loads(man_path.read_text(encoding="utf-8"))
                if man.get("status") == "PASS" and int(man.get("completed_windows", 0)) == 100:
                    success = True
            if ckpt_path.is_file():
                import hashlib

                ckpt_hash = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()
        # Prefer FINISH output hashes when present
        for f in finishes:
            oh = f.get("output_hashes") or {}
            man_hash = oh.get(
                f"artifacts/e2_traffic_formal_runs_r1/runs/{seed}/{scenario}/{method}/runtime_manifest.json",
                man_hash,
            )
            ckpt_hash = oh.get(
                f"artifacts/e2_traffic_formal_runs_r1/runs/{seed}/{scenario}/{method}/checkpoints/final.pt",
                ckpt_hash,
            )
        label = "interrupted_orphan_start" if orphan_start and len(finishes) == 0 else (
            "accepted_success" if success else ("failed" if finishes else "unknown")
        )
        records.append(
            {
                "run_id": run_id,
                "logical_key": f"{seed}:{scenario}:{method}",
                "seed": seed,
                "scenario": scenario,
                "method": method,
                "attempt_id": attempt,
                "start_count": len(starts),
                "finish_count": len(finishes),
                "start_time_utc": starts[0].get("start_time_utc") if starts else None,
                "finish_time_utc": finishes[-1].get("end_time_utc") if finishes else None,
                "exit_code": exit_codes[-1] if exit_codes else None,
                "stdout_log": (starts or finishes)[0].get("stdout_log") if (starts or finishes) else None,
                "stderr_log": (starts or finishes)[0].get("stderr_log") if (starts or finishes) else None,
                "checkpoint_sha256": ckpt_hash,
                "manifest_sha256": man_hash,
                "duplicate_start_count": max(0, len(starts) - 1),
                "duplicate_finish_count": max(0, len(finishes) - 1),
                "orphan_start": bool(orphan_start),
                "orphan_finish": bool(orphan_finish),
                "interrupted_attempt": bool(interrupted or (orphan_start and len(finishes) == 0)),
                "successful_attempt": bool(success and any(c == 0 for c in exit_codes)),
                "label": label,
            }
        )

    df = pd.DataFrame(records)
    # Logical acceptance: exactly one accepted PASS manifest per expected pair
    accepted = 0
    for s in FORMAL_SEEDS:
        for sc in SCENARIOS:
            for m in METHODS:
                man = runs_root / str(s) / sc / m / "runtime_manifest.json"
                if not man.is_file():
                    continue
                payload = json.loads(man.read_text(encoding="utf-8"))
                if payload.get("status") == "PASS" and int(payload.get("completed_windows", 0)) == 100:
                    accepted += 1

    summary = {
        "corrupt_ledger_lines": corrupt,
        "training_start_count": sum(1 for r in training if r.get("record_type") == "START"),
        "training_finish_count": sum(1 for r in training if r.get("record_type") == "FINISH"),
        "unique_run_id_count": int(df["run_id"].nunique()) if len(df) else 0,
        "duplicate_start_count": int(df["duplicate_start_count"].sum()) if len(df) else 0,
        "duplicate_finish_count": int(df["duplicate_finish_count"].sum()) if len(df) else 0,
        "orphan_start_count": int(df["orphan_start"].sum()) if len(df) else 0,
        "orphan_finish_count": int(df["orphan_finish"].sum()) if len(df) else 0,
        "interrupted_attempt_count": int(df["interrupted_attempt"].sum()) if len(df) else 0,
        "successful_logical_run_count": int(df.loc[df["successful_attempt"], "logical_key"].nunique())
        if len(df)
        else 0,
        "accepted_logical_run_count": accepted,
        "expected_logical_runs": EXPECTED_RUNS,
        "known_interrupted_pattern": "extra START without FINISH may exist; acceptance requires one PASS attempt",
        "ledger_rewritten": False,
    }
    return df, summary
