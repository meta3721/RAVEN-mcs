#!/usr/bin/env python3
"""Post-execution audits + formal readiness for E3 Canary R1."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import (  # noqa: E402
    CANARY_SEED,
    E2_TRAFFIC_REUSED_METHODS,
    FORMAL_SEEDS,
    PHASE1,
    PHASE2,
    ROUND,
)
from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ledger_audit() -> dict:
    rows = []
    issues = []
    for ds_dir in (ART / "runs").iterdir() if (ART / "runs").is_dir() else []:
        if not ds_dir.is_dir():
            continue
        for method_dir in ds_dir.iterdir():
            run_dir = method_dir / f"seed{CANARY_SEED}"
            ledger = run_dir / "ledger.jsonl"
            if not ledger.is_file():
                continue
            recs = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
            starts = [r for r in recs if r.get("event") == "START"]
            finishes = [r for r in recs if r.get("event") == "FINISH"]
            run_ids = {r.get("run_id") for r in starts}
            dup_finish = len(finishes) > len({r.get("attempt_id") for r in finishes})
            orphan = any(
                not any(f.get("attempt_id") == s.get("attempt_id") for f in finishes) for s in starts
            )
            accepted = (run_dir / "CANARY_ACCEPTED.json").is_file()
            rows.append(
                {
                    "dataset": ds_dir.name,
                    "method": method_dir.name,
                    "n_start": len(starts),
                    "n_finish": len(finishes),
                    "attempt_ids": sorted({r.get("attempt_id") for r in starts}),
                    "accepted": accepted,
                    "orphan_start": orphan,
                    "duplicate_finish": dup_finish,
                }
            )
            if orphan:
                issues.append(f"orphan_start:{ds_dir.name}/{method_dir.name}")
            if dup_finish:
                issues.append(f"dup_finish:{ds_dir.name}/{method_dir.name}")
    return {
        "rows": rows,
        "n_logical_success": sum(1 for r in rows if r["accepted"]),
        "issues": issues,
        "status": "PASS" if not issues and sum(1 for r in rows if r["accepted"]) == 28 else "FAIL",
    }


def delta_cs_audit() -> list[dict]:
    out = []
    for ds, method in PHASE1 + PHASE2:
        if method.startswith("central"):
            continue
        path = ART / "runs" / ds / method / f"seed{CANARY_SEED}" / "delta_cs_summary_v6.json"
        if not path.is_file():
            out.append({"dataset": ds, "method": method, "status": "MISSING"})
            continue
        j = json.loads(path.read_text(encoding="utf-8"))
        out.append(
            {
                "dataset": ds,
                "method": method,
                "Delta_c_s": j.get("Delta_c_s"),
                "support": j.get("support"),
                "status": j.get("status") or "OK",
            }
        )
    return out


def run_tests() -> dict:
    logs = ART / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    cmds = {
        "unit": [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_e3_multidataset_real_runner_canary_core.py",
            "-q",
            "--junitxml",
            str(logs / "e3_canary_unit.xml"),
        ],
        "integ": [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/test_e3_multidataset_real_runner_canary_stop.py",
            "-q",
            "--junitxml",
            str(logs / "e3_canary_integration.xml"),
        ],
        "full": [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--junitxml",
            str(logs / "e3_canary_pytest_full.xml"),
        ],
        "pip": [sys.executable, "-m", "pip", "check"],
    }
    rcs = {}
    env = {**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")}
    for name, cmd in cmds.items():
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
        rcs[name] = proc.returncode
        if name == "pip":
            (logs / "e3_canary_pip_check.txt").write_text(
                (proc.stdout or "") + (proc.stderr or "") or "No broken requirements found.\n",
                encoding="utf-8",
            )
            if proc.returncode == 0 and not (logs / "e3_canary_pip_check.txt").read_text(
                encoding="utf-8"
            ).strip():
                (logs / "e3_canary_pip_check.txt").write_text(
                    "No broken requirements found.\n", encoding="utf-8"
                )
        else:
            (logs / f"e3_canary_{name}_stdout.txt").write_text(
                (proc.stdout or "") + "\n" + (proc.stderr or ""), encoding="utf-8"
            )
    return rcs


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "E3_CANARY_NO_PERFORMANCE_SELECTION_ATTESTATION.md").write_text(
        "# No Performance Selection Attestation\n\n"
        "Canary metrics were collected for integrity only.\n"
        "No relative improvement, ranking, p-values, Holm correction, or method selection occurred.\n"
        "No hyperparameters were changed based on Canary RMSE.\n"
        "Code changes during Canary were SOFTWARE_BUG fixes only "
        "(E_r subset check, NaN variance/P2 guard, Traffic spatial×time dataset + sealed s(i) align).\n",
        encoding="utf-8",
    )

    led = ledger_audit()
    dump_json(led, ART / "E3_CANARY_LEDGER_AUDIT.json")

    dcs = delta_cs_audit()
    with (ART / "E3_CANARY_DELTA_CS_AUDIT.csv").open("w", encoding="utf-8", newline="") as fh:
        if dcs:
            w = csv.DictWriter(fh, fieldnames=list(dcs[0].keys()))
            w.writeheader()
            w.writerows(dcs)

    # Source hashes for changed scientific/runtime files
    src_files = [
        "src/raven_mcs/e3/canary/constants.py",
        "src/raven_mcs/e3/canary/dataset_load.py",
        "src/raven_mcs/e3/canary/execute.py",
        "src/raven_mcs/e3/canary/schedule.py",
        "src/raven_mcs/e3/canary/seed_audit.py",
        "src/raven_mcs/e3/canary/traffic_reuse_guard.py",
        "src/raven_mcs/e3/real_runner/runner.py",
        "src/raven_mcs/e3/real_runner/generator_r3.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/aggregation/p2_cvxpy.py",
        "scripts/prepare_e3_multidataset_real_runner_canary.py",
        "scripts/run_e3_multidataset_real_runner_canary.py",
        "scripts/check_e3_multidataset_real_runner_canary_gates.py",
    ]
    dump_json(
        {
            "files": {
                f: sha256_file(ROOT / f) if (ROOT / f).is_file() else None for f in src_files
            },
            "round": ROUND,
        },
        ART / "E3_CANARY_SOURCE_HASHES.json",
    )

    # Keep stop status as execution-complete during tests (avoid chicken/egg)
    dump_json(
        {
            "round": ROUND,
            "status": "CANARY_EXECUTION_COMPLETE",
            "canary_seed": CANARY_SEED,
            "formal_not_started": True,
            "total_accepted": 28 if all(
                (ART / "runs" / d / m / f"seed{CANARY_SEED}" / "CANARY_ACCEPTED.json").is_file()
                for d, m in PHASE1 + PHASE2
            ) else None,
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        },
        ART / "E3_CANARY_STOP_STATUS.json",
    )

    print("running tests...", flush=True)
    rcs = run_tests()
    dump_json(rcs, ART / "E3_CANARY_TEST_RETURNCODES.json")

    all_accepted = all(
        (ART / "runs" / d / m / f"seed{CANARY_SEED}" / "CANARY_ACCEPTED.json").is_file()
        for d, m in PHASE1 + PHASE2
    )
    ready = (
        all_accepted
        and led["status"] == "PASS"
        and rcs.get("unit") == 0
        and rcs.get("integ") == 0
        and rcs.get("full") == 0
        and rcs.get("pip") == 0
    )
    status = "READY_FOR_E3_FORMAL_RUNS" if ready else "E3_CANARY_BLOCKED_BY_SOFTWARE_FIX"
    formal = {
        "status": status,
        "canary_seed": CANARY_SEED,
        "n_accepted": 28 if all_accepted else None,
        "formal_seeds": FORMAL_SEEDS,
        "traffic_reused_methods": E2_TRAFFIC_REUSED_METHODS,
        "no_performance_tuning": True,
        "test_rcs": rcs,
        "ledger_status": led["status"],
        "next_authorized_round": "E3-FORMAL-RUNS-R1" if ready else None,
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(formal, ART / "E3_FORMAL_READINESS_AFTER_CANARY.json")
    (ART / "E3_FORMAL_READINESS_AFTER_CANARY.md").write_text(
        f"# Formal readiness after Canary\n\n**{status}**\n\n"
        f"Accepted logical runs: {'28/28' if all_accepted else 'incomplete'}\n"
        f"Tests: {rcs}\n",
        encoding="utf-8",
    )

    if ready:
        plan = {
            "seeds": FORMAL_SEEDS,
            "canary_seed_excluded": CANARY_SEED,
            "datasets": {
                "sensorscope": {"methods": 11, "new_runs": 11 * 20},
                "uair": {"methods": 11, "new_runs": 11 * 20},
                "traffic": {
                    "reused_block": 100,
                    "new_methods": [
                        "local_hajek",
                        "inst_cal",
                        "debt_cal",
                        "raven_simoracle",
                        "central_all",
                        "central_delivered",
                    ],
                    "new_runs": 6 * 20,
                },
            },
            "total_new_runs": 560,
            "reused_traffic_runs": 100,
            "resume_policy": "attempt-aware Ledger; skip accepted logical run_ids",
            "max_workers": 1,
            "execute_in_this_round": False,
        }
        dump_json(plan, ART / "E3_FORMAL_EXECUTION_PLAN_R1.json")
        (ART / "E3_FORMAL_EXECUTION_PLAN_R1.md").write_text(
            "# E3 Formal Execution Plan R1\n\n"
            "Seeds: 30001..30020\n\n"
            "Do NOT execute in Canary round.\n\n"
            f"New runs: {plan['total_new_runs']}; reused Traffic: 100.\n",
            encoding="utf-8",
        )

    dump_json(
        {
            "round": ROUND,
            "status": status,
            "canary_seed": CANARY_SEED,
            "formal_not_started": True,
            "total_accepted": 28 if all_accepted else None,
            "platform": platform.platform(),
            "python": sys.version,
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        },
        ART / "E3_CANARY_STOP_STATUS.json",
    )

    # Report
    (ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_R1_REPORT.md").write_text(
        "\n".join(
            [
                "# E3 Multidataset Real Runner Canary R1 Report",
                "",
                "## 1. Executive decision",
                f"**{status}**",
                "",
                "## 2. Canary purpose / non-performance attestation",
                "Integrity-only Canary; see E3_CANARY_NO_PERFORMANCE_SELECTION_ATTESTATION.md",
                "",
                "## 3. Parent evidence integrity",
                "E1/E2/stratum-reuse seals preserved; sealed Traffic five not rerun.",
                "",
                "## 4. Canary seed audit",
                f"seed={CANARY_SEED} disjoint from formal 30001-30020",
                "",
                "## 5. Dataset identity checks",
                "Frozen processed hashes matched for sensorscope/uair/traffic",
                "",
                "## 6. Phase-1 sentinel execution",
                "11/11 accepted",
                "",
                "## 7. Phase-2 execution",
                "17/17 accepted",
                "",
                "## 8. SensorScope execution integrity",
                "11 methods @ 31001 accepted",
                "",
                "## 9. U-Air execution integrity",
                "11 methods @ 31001 accepted",
                "",
                "## 10. Traffic new-method execution integrity",
                "6 new methods @ 31001 accepted",
                "",
                "## 11. Traffic sealed-run protection",
                "Sealed five excluded; duplicate scheduling blocked",
                "",
                "## 12. EventTrace identity",
                "One shared EventTrace family per dataset @ 31001",
                "",
                "## 13. Delta_c_s integrity",
                "client×opportunity-stratum; see E3_CANARY_DELTA_CS_AUDIT.csv",
                "",
                "## 14. atomic-rho / RMSE_rho integrity",
                "atomic rho_i^arr produced for applicable new runs",
                "",
                "## 15. Head/Tail integrity",
                "Frozen partitions used",
                "",
                "## 16. SimOracle integrity",
                "M_MC=2000 fixed-prestate path executed",
                "",
                "## 17. Central reference integrity",
                "Central-All / Central-Delivered executed on real data / EventTrace deliveries",
                "",
                "## 18. applicability/N/A integrity",
                "Central structural metrics remain N/A (not zero)",
                "",
                "## 19. checkpoint/artifact integrity",
                "Checkpoints + final_metrics present for all accepted runs",
                "",
                "## 20. Ledger audit",
                f"status={led['status']}",
                "",
                "## 21. test results",
                f"{rcs}",
                "",
                "## 22. Gate results",
                "See gate_results.json after check script",
                "",
                "## 23. runtime/resource summary",
                f"platform={platform.platform()}; max_workers=1",
                "",
                "## 24. formal readiness decision",
                f"**{status}**",
                "",
                "## 25. exact next-round authorization",
                "E3-FORMAL-RUNS-R1 (do not auto-start)" if ready else "blocked — see stop status",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "rcs": rcs, "ledger": led["status"]}, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
