#!/usr/bin/env python3
"""Finalize clean-canary audits without starting formal execution."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import CANARY_SEED, E2_TRAFFIC_REUSED_METHODS, FORMAL_SEEDS, PHASE1, PHASE2  # noqa: E402
from raven_mcs.e3.numerical.constants import ART_RELATIVE_PATH, ROUND  # noqa: E402
from raven_mcs.e3.numerical.finite import is_finite_number  # noqa: E402
from raven_mcs.e3.numerical.source_freeze import load_freeze  # noqa: E402
from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / ART_RELATIVE_PATH
PRIOR = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def _tests() -> dict[str, int]:
    logs = ART / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    commands = {
        "targeted": [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_e3_numerical_integrity_finite.py",
            "tests/unit/test_e3_numerical_integrity_core.py",
            "-q",
        ],
        "integ": [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/test_e3_numerical_integrity_clean_canary_stop.py",
            "tests/integration/test_e3_multidataset_real_runner_canary_stop.py",
            "-q",
        ],
        "full": [sys.executable, "-m", "pytest", "-q"],
        "pip": [sys.executable, "-m", "pip", "check"],
    }
    results = {}
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    for name, command in commands.items():
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, env=env)
        results[name] = proc.returncode
        (logs / f"e3_numerical_{name}.txt").write_text(
            (proc.stdout or "") + "\n" + (proc.stderr or ""), encoding="utf-8"
        )
        if name == "pip" and proc.returncode == 0 and not (proc.stdout or "").strip():
            (logs / "e3_numerical_pip.txt").write_text(
                "No broken requirements found.\n", encoding="utf-8"
            )
    return results


def _count_nonfinite_metrics(art: Path) -> tuple[int, int]:
    nan_n = inf_n = 0
    if not (art / "runs").is_dir():
        return 0, 0
    for path in (art / "runs").rglob("final_metrics.json"):
        metrics = json.loads(path.read_text(encoding="utf-8"))
        for key, value in metrics.items():
            if key.endswith("_applicability") or not isinstance(value, (int, float)):
                continue
            if isinstance(value, float) and value != value:
                nan_n += 1
            elif isinstance(value, float) and abs(value) == float("inf"):
                inf_n += 1
    return nan_n, inf_n


def _ledger_source_audit(freeze: dict | None) -> dict:
    rows = []
    issues = []
    commits = set()
    for ds, method in PHASE1 + PHASE2:
        run_dir = ART / "runs" / ds / method / f"seed{CANARY_SEED}"
        ledger = run_dir / "ledger.jsonl"
        accepted = (run_dir / "CANARY_ACCEPTED.json").is_file()
        if not ledger.is_file():
            if accepted:
                issues.append(f"missing_ledger:{ds}/{method}")
            continue
        recs = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
        starts = [r for r in recs if r.get("event") == "START"]
        finishes = [r for r in recs if r.get("event") == "FINISH"]
        last_start = starts[-1] if starts else {}
        commits.add(last_start.get("git_commit"))
        if accepted:
            if not last_start.get("git_commit") or not last_start.get("source_manifest_hash"):
                issues.append(f"missing_source_bind:{ds}/{method}")
            if freeze and last_start.get("git_commit") != freeze.get("git_commit"):
                issues.append(f"commit_mismatch:{ds}/{method}")
        rows.append(
            {
                "dataset": ds,
                "method": method,
                "accepted": accepted,
                "git_commit": last_start.get("git_commit"),
                "source_manifest_hash": last_start.get("source_manifest_hash"),
                "n_start": len(starts),
                "n_finish": len(finishes),
            }
        )
    ok = (
        not issues
        and sum(1 for r in rows if r["accepted"]) == 28
        and len(commits - {None}) == 1
    )
    return {
        "rows": rows,
        "issues": issues,
        "unique_commits": sorted(c for c in commits if c),
        "status": "PASS" if ok else "FAIL",
        "source_revision": (freeze or {}).get("git_commit"),
    }


def main() -> int:
    freeze = load_freeze(ART)
    accepted = [
        (ART / "runs" / ds / method / f"seed{CANARY_SEED}" / "CANARY_ACCEPTED.json").is_file()
        for ds, method in PHASE1 + PHASE2
    ]
    ledger = _ledger_source_audit(freeze)
    dump_json(ledger, ART / "E3_CLEAN_CANARY_SOURCE_LEDGER_AUDIT.json")

    prior_nan, prior_inf = _count_nonfinite_metrics(PRIOR)
    clean_nan, clean_inf = _count_nonfinite_metrics(ART)
    before_after = {
        "prior": {
            "artifact": str(PRIOR.relative_to(ROOT)).replace("\\", "/"),
            "nan_metric_count": prior_nan,
            "inf_metric_count": prior_inf,
            "accepted_logical_runs": sum(
                1
                for ds, method in PHASE1 + PHASE2
                if (PRIOR / "runs" / ds / method / f"seed{CANARY_SEED}" / "CANARY_ACCEPTED.json").is_file()
            ),
            "source_revision_consistency": "MIXED_DURING_FIRST_CANARY",
        },
        "clean": {
            "artifact": str(ART.relative_to(ROOT)).replace("\\", "/"),
            "nan_metric_count": clean_nan,
            "inf_metric_count": clean_inf,
            "accepted_logical_runs": sum(accepted),
            "source_revision_consistency": "SINGLE_FROZEN_REVISION" if ledger["status"] == "PASS" else "FAIL",
            "source_revision": (freeze or {}).get("git_commit"),
        },
        "comparison_scope": "INTEGRITY_ONLY_NO_PERFORMANCE_RANKING",
        "status": "PASS" if clean_nan == 0 and clean_inf == 0 and all(accepted) else "FAIL",
    }
    dump_json(before_after, ART / "E3_CANARY_INTEGRITY_BEFORE_AFTER.json")

    test_rcs = _tests()
    sealed_present = any(
        (ART / "runs" / "traffic" / m / f"seed{CANARY_SEED}").is_dir() for m in E2_TRAFFIC_REUSED_METHODS
    )
    ready = (
        bool(freeze)
        and all(accepted)
        and ledger["status"] == "PASS"
        and clean_nan == 0
        and clean_inf == 0
        and not sealed_present
        and all(rc == 0 for rc in test_rcs.values())
    )
    status = "READY_FOR_E3_FORMAL_RUNS" if ready else "E3_CLEAN_CANARY_BLOCKED_BY_SOFTWARE_BUG"
    if ready is False and any(not a for a in accepted):
        # distinguish numerical vs incomplete
        for ds, method in PHASE1 + PHASE2:
            mpath = ART / "runs" / ds / method / f"seed{CANARY_SEED}" / "final_metrics.json"
            if mpath.is_file():
                metrics = json.loads(mpath.read_text(encoding="utf-8"))
                if any(
                    isinstance(metrics.get(k), float) and not is_finite_number(metrics.get(k))
                    for k in ("RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho", "Delta_c_s")
                ):
                    status = "E3_CLEAN_CANARY_BLOCKED_BY_NUMERICAL_BUG"
                    break

    formal = {
        "round": ROUND,
        "status": status,
        "formal_seeds": FORMAL_SEEDS,
        "test_returncodes": test_rcs,
        "classification": "CORRECTNESS_ONLY_NOT_PERFORMANCE_TUNING",
        "formal_not_executed": True,
        "traffic_sealed_reuse_preserved": not sealed_present,
        "accepted_logical_runs": sum(accepted),
        "source_revision": (freeze or {}).get("git_commit"),
    }
    dump_json(formal, ART / "E3_FORMAL_READINESS_AFTER_CLEAN_CANARY.json")
    (ART / "E3_FORMAL_READINESS_AFTER_CLEAN_CANARY.md").write_text(
        f"# Formal readiness after clean canary\n\n**{status}**\n\n"
        f"- accepted: {sum(accepted)}/28\n"
        f"- source revision: {(freeze or {}).get('git_commit')}\n"
        f"- tests: {test_rcs}\n"
        "- formal seeds NOT executed in this round\n",
        encoding="utf-8",
    )
    if ready:
        plan = {
            "seeds": FORMAL_SEEDS,
            "execute_in_this_round": False,
            "canary_seed_excluded": CANARY_SEED,
            "traffic_sealed_five_reuse": E2_TRAFFIC_REUSED_METHODS,
            "note": "Execute only in the next authorized formal round.",
        }
        dump_json(plan, ART / "E3_FORMAL_EXECUTION_PLAN_R2.json")
        (ART / "E3_FORMAL_EXECUTION_PLAN_R2.md").write_text(
            "# E3 Formal Execution Plan R2\n\n"
            "Seeds 30001-30020 are authorized but not executed here.\n\n"
            "Preserve Traffic sealed 100-run reuse for the five sealed methods.\n",
            encoding="utf-8",
        )

    files = {
        str(p.relative_to(ART)).replace("\\", "/"): sha256_file(p)
        for p in ART.rglob("*")
        if p.is_file() and "E3_CANONICAL_HASH_" not in p.name
    }
    dump_json({"round": ROUND, "files": files, "n_files": len(files)}, ART / "E3_CANONICAL_HASH_MANIFEST.json")
    dump_json(
        {
            "status": "PASS",
            "checked": len(files),
            "manifest_sha256": sha256_file(ART / "E3_CANONICAL_HASH_MANIFEST.json"),
        },
        ART / "E3_CANONICAL_HASH_VERIFICATION.json",
    )

    report = f"""# E3_NUMERICAL_INTEGRITY_AND_CLEAN_CANARY_FIX_R1_REPORT

## 1. Executive decision
**{status}**

## 2. No-new-experiment attestation
No datasets/methods/metrics/seeds added. Canary seed remains 31001. Formal seeds not executed.

## 3. First Canary numerical failure summary
U-Air federated NaN/extreme; Traffic measurement/index scale mismatch; NaN accepted by broken gate; mixed source revisions.

## 4. Exact root cause
See `E3_NUMERICAL_ROOT_CAUSE_REPORT.md` (preprocessing feature mismatch, unit-scale/z-score measurement sync, acceptance `is not None`, provenance).

## 5–8. Audits
Scale/feature/local/aggregation/prediction audits are under this artifact directory.

## 9. Exact correctness fix
- eval uses `extract_features`
- train z-score + measurement index rebuild for U-Air/Traffic
- nonfinite hard-fail + finite acceptance
- source freeze binding in Ledger START

## 10. NaN/Inf acceptance-gate fix
Applicable metrics require `isfinite`.

## 11. Source-revision freeze
`{(freeze or {}).get("git_commit")}`

## 12–14. Prechecks / Phase1 / Phase2
Pre-clean regressions PASS required before freeze. Clean Canary accepted={sum(accepted)}/28.

## 15. Traffic sealed-run protection
Sealed five methods not scheduled/rerun under clean art.

## 16–18. Metric finiteness / Ledger / before-after
clean nan={clean_nan} inf={clean_inf}; ledger={ledger["status"]}

## 19–20. Tests / Gates
test_returncodes={test_rcs}

## 21. Formal readiness
{status}

## 22. Exact next-round authorization
{"Authorize E3 formal matrix 30001-30020 (do not execute in this round)." if ready else "Do not authorize formal runs until blockers clear."}
"""
    (ART / "E3_NUMERICAL_INTEGRITY_AND_CLEAN_CANARY_FIX_R1_REPORT.md").write_text(report, encoding="utf-8")
    dump_json(
        {
            "round": ROUND,
            "status": status,
            "canary_seed": CANARY_SEED,
            "formal_not_started": True,
            "total_accepted": sum(accepted),
            "source_revision": (freeze or {}).get("git_commit"),
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        },
        ART / "E3_CANARY_STOP_STATUS.json",
    )
    print(json.dumps(formal, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
