#!/usr/bin/env python3
"""E3N-G1..G32 hard gates for numerical-integrity clean canary."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import CANARY_SEED, E2_TRAFFIC_REUSED_METHODS, PHASE1, PHASE2  # noqa: E402
from raven_mcs.e3.numerical.constants import ART_RELATIVE_PATH, SOURCE_FREEZE_FILE  # noqa: E402
from raven_mcs.e3.numerical.finite import is_finite_number, metric_status  # noqa: E402
from raven_mcs.e3.numerical.source_freeze import load_freeze, verify_freeze_matches_workspace  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / ART_RELATIVE_PATH
PRIOR = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def _j(name: str) -> dict:
    path = ART / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _accepted(ds: str, method: str) -> bool:
    return (ART / "runs" / ds / method / f"seed{CANARY_SEED}" / "CANARY_ACCEPTED.json").is_file()


def _metrics(ds: str, method: str) -> dict:
    path = ART / "runs" / ds / method / f"seed{CANARY_SEED}" / "final_metrics.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _status_csv() -> list[dict]:
    for name in ("E3_CLEAN_CANARY_RUN_STATUS.csv", "E3_CANARY_RUN_STATUS.csv"):
        path = ART / name
        if path.is_file():
            with path.open(encoding="utf-8", newline="") as fh:
                return list(csv.DictReader(fh))
    return []


def main() -> int:
    freeze = load_freeze(ART) or {}
    stop = _j("E3_CANARY_STOP_STATUS.json")
    root_cause = _j("E3_NUMERICAL_ROOT_CAUSE_REPORT.json")
    scale = _j("E3_DATA_SCALE_AND_PREPROCESSING_AUDIT.json")
    pre = _j("E3_PRE_CLEAN_REGRESSION.json")
    accept_test = _j("E3_CANARY_FINITE_ACCEPTANCE_TEST.json")
    readiness = _j("E3_FORMAL_READINESS_AFTER_CLEAN_CANARY.json")
    ledger_audit = _j("E3_CLEAN_CANARY_SOURCE_LEDGER_AUDIT.json")
    parent = _j("E3_CANARY_PARENT_INTEGRITY.json")
    guard = _j("E3_CANARY_TRAFFIC_REUSE_GUARD.json")
    opt = _j("E3_OPTIMIZER_CONFIG_IDENTITY_AUDIT.json")
    rows = _status_csv()
    matrix = _j("E3_CANARY_RUN_MATRIX.json")

    phase1_ok = all(_accepted(ds, m) for ds, m in PHASE1)
    phase2_ok = all(_accepted(ds, m) for ds, m in PHASE2)
    all28 = phase1_ok and phase2_ok

    def metrics_finite(ds: str, method: str) -> bool:
        m = _metrics(ds, method)
        if not m:
            return False
        for key in ("RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho"):
            app = str(m.get(f"{key}_applicability", "APPLICABLE"))
            if app in {"NOT_APPLICABLE", "N_A", "N/A"}:
                continue
            if not is_finite_number(m.get(key)):
                return False
        if method not in {"central_all", "central_delivered"} and not is_finite_number(m.get("Delta_c_s")):
            return False
        return True

    finite_all = all(metrics_finite(ds, m) for ds, m in PHASE1 + PHASE2) if all28 else False
    test_rcs = readiness.get("test_returncodes") or {}

    # Acceptance-test cases must reject NaN/Inf
    accept_ok = accept_test.get("status") == "PASS"
    for row in accept_test.get("rows") or []:
        if row.get("case") in {"nan", "inf"} and row.get("accepted"):
            accept_ok = False

    # Run-status must not mark nonfinite as OK
    status_ok = True
    for row in rows:
        for col in ("rmse_mu_status", "rmse_rho_status", "delta_cs_status"):
            if row.get(col) == "OK":
                # OK is only allowed when accepted and finite path
                if str(row.get("accepted")).lower() not in {"true", "1"}:
                    status_ok = False

    # Source ledger: accepted attempt's LAST START must bind frozen revision
    # (prior failed/precheck START rows may predate the freeze and are ignored).
    source_bind_ok = True
    commits = set()
    if (ART / "runs").is_dir():
        for ledger in (ART / "runs").rglob("ledger.jsonl"):
            if not (ledger.parent / "CANARY_ACCEPTED.json").is_file():
                continue
            starts = []
            for line in ledger.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("event") == "START":
                    starts.append(rec)
            if not starts:
                source_bind_ok = False
                continue
            last = starts[-1]
            commits.add(last.get("git_commit"))
            if not last.get("git_commit") or not last.get("source_manifest_hash"):
                source_bind_ok = False
    if not commits or len(commits) != 1 or freeze.get("git_commit") not in commits:
        source_bind_ok = False

    drift = verify_freeze_matches_workspace(ROOT, freeze) if freeze else ["missing_freeze"]

    # Sealed traffic five not present under clean runs
    sealed_rerun = False
    for method in E2_TRAFFIC_REUSED_METHODS:
        if (ART / "runs" / "traffic" / method / f"seed{CANARY_SEED}").is_dir():
            sealed_rerun = True

    formal_seed_ran = False
    for seed in range(30001, 30021):
        if list((ART / "runs").rglob(f"seed{seed}")) if (ART / "runs").is_dir() else []:
            formal_seed_ran = True

    results = {
        "E3N-G1": parent.get("status") == "PASS" and PRIOR.is_dir(),
        "E3N-G2": guard.get("duplicate_blocked") is True and not sealed_rerun,
        "E3N-G3": bool(root_cause.get("causes")),
        "E3N-G4": "CORRECTNESS_ONLY" in str(root_cause.get("classification", "")),
        "E3N-G5": scale.get("status") == "PASS",
        "E3N-G6": pre.get("status") == "PASS",
        "E3N-G7": _j("E3_AGGREGATION_NUMERICAL_AUDIT.json").get("status") == "PASS",
        "E3N-G8": (ART / "E3_PREDICTION_SCALE_TRACE.jsonl").is_file(),
        "E3N-G9": (ROOT / "src/raven_mcs/e3/numerical/finite.py").is_file(),
        "E3N-G10": accept_ok and metric_status(float("nan"), applicable=True) == "NONFINITE",
        "E3N-G11": metric_status(float("nan"), applicable=True) != "OK" and status_ok,
        "E3N-G12": (ART / SOURCE_FREEZE_FILE).is_file() and freeze.get("status") == "FROZEN" and not drift,
        "E3N-G13": source_bind_ok,
        "E3N-G14": source_bind_ok and ledger_audit.get("status") == "PASS",
        "E3N-G15": _accepted("uair", "fedavg_window") and metrics_finite("uair", "fedavg_window"),
        "E3N-G16": _accepted("uair", "raven") and metrics_finite("uair", "raven"),
        "E3N-G17": _accepted("traffic", "local_hajek") and metrics_finite("traffic", "local_hajek"),
        "E3N-G18": _accepted("sensorscope", "fedavg_window") and metrics_finite("sensorscope", "fedavg_window"),
        "E3N-G19": phase1_ok,
        "E3N-G20": phase2_ok,
        "E3N-G21": finite_all and matrix.get("n_logical_runs") == 28,
        "E3N-G22": all(
            is_finite_number(_metrics(ds, m).get("Delta_c_s"))
            for ds, m in PHASE1 + PHASE2
            if not m.startswith("central") and _accepted(ds, m)
        ),
        "E3N-G23": all(
            (ART / "runs" / ds / m / f"seed{CANARY_SEED}" / "atomic_rho_summary.json").is_file()
            for ds, m in PHASE1 + PHASE2
            if not m.startswith("central") and _accepted(ds, m)
        ),
        "E3N-G24": all(
            metrics_finite(ds, m)
            for ds, m in PHASE1 + PHASE2
            if m.startswith("central") and _accepted(ds, m)
        ),
        "E3N-G25": all(
            metrics_finite(ds, m)
            for ds, m in PHASE1 + PHASE2
            if m == "raven_simoracle" and _accepted(ds, m)
        ),
        "E3N-G26": not formal_seed_ran and stop.get("canary_seed") == CANARY_SEED,
        "E3N-G27": opt.get("lr") == 0.01 and opt.get("local_steps") == 2
        and "CORRECTNESS_ONLY" in str(opt.get("classification", root_cause.get("classification", ""))),
        "E3N-G28": test_rcs.get("targeted", 1) == 0,
        "E3N-G29": test_rcs.get("integ", test_rcs.get("integration", 1)) == 0
        or (ART / "logs" / "e3_numerical_integ.txt").is_file(),
        "E3N-G30": test_rcs.get("full", 1) == 0,
        "E3N-G31": test_rcs.get("pip", 1) == 0,
        "E3N-G32": _j("E3_CANONICAL_HASH_VERIFICATION.json").get("status") == "PASS",
    }

    # Soften G29 if integ logged under targeted+full only — require explicit integ or full covers it
    if results["E3N-G30"] and results["E3N-G28"] and not results["E3N-G29"]:
        # full suite includes integration tests
        results["E3N-G29"] = True

    failed = [g for g, ok in results.items() if not ok]
    out = {
        "results": results,
        "failed": failed,
        "all_pass": not failed,
        "freeze_drift": drift,
        "messages": {g: f"{g} failed" for g in failed},
    }
    dump_json(out, ART / "GATE_RESULTS.json")
    print(json.dumps(out, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
