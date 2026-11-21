#!/usr/bin/env python3
"""Hard gates E3CNY-G1..G33 for E3 multidataset real-runner Canary R1."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import (  # noqa: E402
    CANARY_SEED,
    E2_TRAFFIC_REUSED_METHODS,
    FORMAL_SEEDS,
    FROZEN_DATASET_HASHES,
    PHASE1,
    PHASE2,
)
from raven_mcs.e3.canary.dataset_load import verify_dataset_hash  # noqa: E402
from raven_mcs.e3.canary.seed_audit import audit_canary_seed  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def _load(name: str):
    path = ART / name
    if not path.is_file():
        return None
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")


def _accepted_rows() -> list[dict]:
    path = ART / "E3_CANARY_RUN_STATUS.csv"
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _run_accepted(dataset: str, method: str) -> bool:
    marker = ART / "runs" / dataset / method / f"seed{CANARY_SEED}" / "CANARY_ACCEPTED.json"
    return marker.is_file()


def check_gates() -> dict:
    results: dict[str, bool] = {}
    parent = _load("E3_CANARY_PARENT_INTEGRITY.json") or {}
    results["E3CNY-G1"] = bool(parent.get("parent_stop_exists"))

    seed = _load("E3_CANARY_SEED_AUDIT.json") or audit_canary_seed()
    results["E3CNY-G2"] = seed.get("status") == "PASS" and CANARY_SEED not in FORMAL_SEEDS

    dh = _load("E3_CANARY_DATASET_HASH_AUDIT.json") or {
        ds: verify_dataset_hash(ROOT, ds) for ds in FROZEN_DATASET_HASHES
    }
    results["E3CNY-G3"] = all(v.get("match") for v in dh.values())

    th = _load("E3_CANARY_TARGET_HASH_AUDIT.json") or {}
    results["E3CNY-G4"] = all(
        (th.get(ds) or {}).get("status") == "PASS" for ds in ("sensorscope", "uair", "traffic")
    )

    sh = _load("E3_CANARY_STRATUM_HASH_AUDIT.json") or {}
    results["E3CNY-G5"] = sh.get("status") == "PASS"
    results["E3CNY-G6"] = bool(sh.get("traffic_4_region"))

    guard = _load("E3_CANARY_TRAFFIC_REUSE_GUARD.json") or {}
    results["E3CNY-G7"] = bool(guard.get("duplicate_blocked")) and not any(
        _run_accepted("traffic", m) for m in E2_TRAFFIC_REUSED_METHODS
    )

    et = _load("E3_CANARY_EVENTTRACE_AUDIT.json") or {}
    et_rows = et.get("rows") or []
    results["E3CNY-G8"] = len(et_rows) == 3 and all(r.get("shared_across_methods") for r in et_rows)

    # Sample federated smoke audit integrity from accepted Phase-1 fedavg
    fed = ART / "runs/sensorscope/fedavg_window/seed31001/method_smoke_audit.json"
    fed_j = json.loads(fed.read_text(encoding="utf-8")) if fed.is_file() else {}
    results["E3CNY-G9"] = int(fed_j.get("local_optimizer_steps") or 0) > 0
    results["E3CNY-G10"] = bool(fed_j.get("aggregation_invoked"))

    raven = ART / "runs/sensorscope/raven/seed31001/method_smoke_audit.json"
    raven_j = json.loads(raven.read_text(encoding="utf-8")) if raven.is_file() else {}
    results["E3CNY-G11"] = bool(raven_j.get("P2_invoked"))

    so = ART / "runs/sensorscope/raven_simoracle/seed31001/config_snapshot.json"
    results["E3CNY-G12"] = so.is_file()

    # Atomic path / joint pi / Delta_c_s / rho from an accepted federated run
    rho = ART / "runs/sensorscope/fedavg_window/seed31001/atomic_rho_summary.json"
    rho_j = json.loads(rho.read_text(encoding="utf-8")) if rho.is_file() else {}
    results["E3CNY-G13"] = rho.is_file()
    results["E3CNY-G14"] = (
        ART / "runs/sensorscope/fedavg_window/seed31001/delta_cs_summary_v6.json"
    ).is_file()
    dcs = ART / "runs/sensorscope/fedavg_window/seed31001/delta_cs_summary_v6.json"
    dcs_j = json.loads(dcs.read_text(encoding="utf-8")) if dcs.is_file() else {}
    results["E3CNY-G15"] = "opportunity_stratum" in str(dcs_j.get("support") or dcs_j)
    results["E3CNY-G16"] = abs(float(rho_j.get("sum_rho") or 0) - 1.0) < 1e-6
    metrics = ART / "runs/sensorscope/fedavg_window/seed31001/final_metrics.json"
    met = json.loads(metrics.read_text(encoding="utf-8")) if metrics.is_file() else {}
    results["E3CNY-G17"] = met.get("RMSE_rho") is not None
    results["E3CNY-G18"] = met.get("Head_RMSE") is not None and met.get("Tail_RMSE") is not None

    central_all = ART / "runs/sensorscope/central_all/seed31001/CANARY_ACCEPTED.json"
    # may be phase2 — check traffic/sensorscope presence when available
    ca_metrics_path = ART / "runs/sensorscope/central_all/seed31001/final_metrics.json"
    if ca_metrics_path.is_file():
        ca = json.loads(ca_metrics_path.read_text(encoding="utf-8"))
        results["E3CNY-G19"] = ca.get("RMSE_mu") is not None
    else:
        results["E3CNY-G19"] = False

    cd = ART / "runs/sensorscope/central_delivered/seed31001/final_metrics.json"
    results["E3CNY-G20"] = cd.is_file() and json.loads(cd.read_text(encoding="utf-8")).get("RMSE_mu") is not None

    # N/A not converted to 0 for central Delta_c_s
    cd_m = json.loads(cd.read_text(encoding="utf-8")) if cd.is_file() else {}
    results["E3CNY-G21"] = cd_m.get("Delta_c_s") is None and cd_m.get("solver_status") == "CENTRAL_NO_P2"

    rows = _accepted_rows()
    accepted = [r for r in rows if str(r.get("accepted")).lower() in {"true", "1"}]
    results["E3CNY-G22"] = all(
        (ART / "runs" / r["dataset"] / r["method"] / f"seed{CANARY_SEED}" / "checkpoints" / "final.pt").is_file()
        for r in accepted
    ) and len(accepted) > 0
    results["E3CNY-G23"] = all(
        (ART / "runs" / r["dataset"] / r["method"] / f"seed{CANARY_SEED}" / "final_metrics.json").is_file()
        for r in accepted
    ) and len(accepted) > 0

    # Ledger audit
    ledger_ok = True
    for r in accepted:
        ledger = ART / "runs" / r["dataset"] / r["method"] / f"seed{CANARY_SEED}" / "ledger.jsonl"
        if not ledger.is_file():
            ledger_ok = False
            break
        lines = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
        if not any(x.get("event") == "START" for x in lines) or not any(
            x.get("event") == "FINISH" for x in lines
        ):
            ledger_ok = False
            break
    results["E3CNY-G24"] = ledger_ok

    results["E3CNY-G25"] = all(_run_accepted(d, m) for d, m in PHASE1)
    results["E3CNY-G26"] = all(_run_accepted(d, m) for d, m in PHASE2)

    # no formal seed runs
    formal_hit = False
    runs_root = ART / "runs"
    if runs_root.is_dir():
        for p in runs_root.rglob("config_snapshot.json"):
            cfg = json.loads(p.read_text(encoding="utf-8"))
            if int(cfg.get("seed", -1)) in set(FORMAL_SEEDS):
                formal_hit = True
                break
    results["E3CNY-G27"] = not formal_hit
    results["E3CNY-G28"] = (ART / "E3_CANARY_NO_PERFORMANCE_SELECTION_ATTESTATION.md").is_file()

    # tests — checked by prepare/export with recorded rc files when present
    unit = ART / "logs/e3_canary_unit.xml"
    integ = ART / "logs/e3_canary_integration.xml"
    full = ART / "logs/e3_canary_pytest_full.xml"
    pip = ART / "logs/e3_canary_pip_check.txt"
    results["E3CNY-G29"] = unit.is_file()
    results["E3CNY-G30"] = integ.is_file()
    results["E3CNY-G31"] = full.is_file()
    results["E3CNY-G32"] = pip.is_file() and "No broken requirements" in pip.read_text(encoding="utf-8")

    verify = _load("E3_CANARY_HASH_VERIFICATION.json") or {}
    results["E3CNY-G33"] = verify.get("status") == "PASS"

    failed = [k for k, v in results.items() if not v]
    stop = _load("E3_CANARY_STOP_STATUS.json") or {}
    all_pass = len(failed) == 0
    out = {
        "round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1",
        "results": results,
        "failed": failed,
        "all_pass": all_pass,
        "n_accepted": len(accepted),
        "stop_status": stop.get("status"),
    }
    dump_json(out, ART / "gate_results.json")
    return out


def main() -> int:
    out = check_gates()
    print(json.dumps(out, indent=2))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
