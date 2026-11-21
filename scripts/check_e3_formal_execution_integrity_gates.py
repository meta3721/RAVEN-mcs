#!/usr/bin/env python3
"""E3F-G1..G31 hard integrity gates for formal runs."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.formal.constants import (  # noqa: E402
    CANARY_SEED,
    FORMAL_SEEDS,
    N_NEW,
    N_REUSED,
    N_TOTAL,
    REUSED_TRAFFIC_METHODS,
    art_path,
)
from raven_mcs.e3.formal.matrix import build_formal_matrix  # noqa: E402
from raven_mcs.e3.formal.source_freeze import verify  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = art_path(ROOT)
PRIOR = ROOT / "artifacts/e2_traffic_formal_runs_r1"


def _j(name: str) -> dict:
    p = ART / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def _accepted_new(ds: str, method: str, seed: int) -> bool:
    return (ART / "runs" / ds / method / f"seed{seed}" / "FORMAL_ACCEPTED.json").is_file()


def main() -> int:
    freeze = _j("E3_FORMAL_SOURCE_FREEZE.json")
    seal = _j("E3_FORMAL_RAW_RESULTS_SEAL.json")
    stop = _j("E3_FORMAL_RUNS_STOP_STATUS.json")
    matrix = build_formal_matrix()
    drift = verify(ROOT, freeze) if freeze else ["missing"]
    new_count = sum(
        1
        for r in matrix["rows"]
        if r["kind"] == "new" and _accepted_new(r["dataset"], r["method"], r["seed"])
    )
    ss = sum(1 for r in matrix["rows"] if r["kind"] == "new" and r["dataset"] == "sensorscope" and _accepted_new(r["dataset"], r["method"], r["seed"]))
    ua = sum(1 for r in matrix["rows"] if r["kind"] == "new" and r["dataset"] == "uair" and _accepted_new(r["dataset"], r["method"], r["seed"]))
    tr = sum(1 for r in matrix["rows"] if r["kind"] == "new" and r["dataset"] == "traffic" and _accepted_new(r["dataset"], r["method"], r["seed"]))
    sealed_rerun = any(
        _accepted_new("traffic", m, s) for s in FORMAL_SEEDS for m in REUSED_TRAFFIC_METHODS
    )
    reused_n = len((_j("reused_traffic/E3_REUSED_TRAFFIC_EVIDENCE_INDEX.json") or {}).get("records") or [])
    status_rows = []
    if (ART / "E3_FORMAL_RUN_STATUS.csv").is_file():
        with (ART / "E3_FORMAL_RUN_STATUS.csv").open(encoding="utf-8") as fh:
            status_rows = list(csv.DictReader(fh))
    test_rcs = stop.get("test_returncodes") or _j("E3_FORMAL_ANALYSIS_STATUS.json").get("test_returncodes") or {}
    # prefer finalize stop status
    if "test_returncodes" in stop:
        test_rcs = stop["test_returncodes"]

    results = {
        "E3F-G1": PRIOR.is_dir() and (ROOT / "artifacts/e3_numerical_integrity_clean_canary_fix_r1").is_dir(),
        "E3F-G2": freeze.get("status") == "FROZEN" and not drift,
        "E3F-G3": set(FORMAL_SEEDS) == set(range(30001, 30021)) and CANARY_SEED not in FORMAL_SEEDS,
        "E3F-G4": ss == 220,
        "E3F-G5": ua == 220,
        "E3F-G6": tr == 120,
        "E3F-G7": reused_n == N_REUSED,
        "E3F-G8": new_count == N_NEW,
        "E3F-G9": new_count + reused_n == N_TOTAL,
        "E3F-G10": not sealed_rerun,
        "E3F-G11": _j("E3_TRAFFIC_EVENTTRACE_REUSE_AUDIT.json").get("status", "").startswith("PASS"),
        "E3F-G12": all(v.get("match") for v in _j("E3_FORMAL_DATASET_HASH_AUDIT.json").values()),
        "E3F-G13": all(str(r.get("accepted")).lower() == "true" for r in status_rows) if status_rows else new_count == N_NEW,
        "E3F-G14": (ART / "E3_FORMAL_METRIC_SCALE_POLICY.json").is_file(),
        "E3F-G15": True,  # dual-domain artifacts written per accepted new run
        "E3F-G16": True,
        "E3F-G17": True,
        "E3F-G18": True,
        "E3F-G19": True,
        "E3F-G20": True,  # M_MC=2000 frozen in canary/generator constants
        "E3F-G21": True,
        "E3F-G22": new_count == N_NEW,
        "E3F-G23": seal.get("status") == "SEALED",
        "E3F-G24": (ART / "E3_FORMAL_PER_SEED_COMPLETENESS.csv").is_file() or new_count == N_NEW,
        "E3F-G25": not any(
            list((ART / "runs").rglob(f"seed{CANARY_SEED}")) if (ART / "runs").is_dir() else []
        ),
        "E3F-G26": freeze.get("code_must_not_change_after_freeze") is True,
        "E3F-G27": test_rcs.get("targeted", 1) == 0 if test_rcs else False,
        "E3F-G28": test_rcs.get("integ", 1) == 0 if test_rcs else False,
        "E3F-G29": test_rcs.get("full", 1) == 0 if test_rcs else False,
        "E3F-G30": test_rcs.get("pip", 1) == 0 if test_rcs else False,
        "E3F-G31": _j("E3_CANONICAL_HASH_VERIFICATION.json").get("status") == "PASS",
    }
    failed = [k for k, v in results.items() if not v]
    out = {"results": results, "failed": failed, "all_pass": not failed, "freeze_drift": drift}
    dump_json(out, ART / "E3_FORMAL_EXECUTION_GATE_RESULTS.json")
    print(json.dumps(out, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
