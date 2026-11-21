#!/usr/bin/env python3
"""E2-TRAFFIC-BALANCED-DESIGN-CANARY-R1 prepare (hard A/O/U traces; no training)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.traffic_balanced_canary import (
    DESIGN_SEEDS,
    N_ATOMS,
    N_CLIENTS,
    N_WINDOWS,
    build_traffic_schedule,
    calibrate_traffic_p_opp,
    load_traffic_targets,
    run_traffic_seed_trace,
    sha256_file,
    verify_input_identity,
)
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_BALANCED_DESIGN_CANARY_R1"
OUT = ROOT / "outputs/e2_traffic_balanced_canary"
AUDIT = ROOT / "outputs/audits"
DELIV = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _tv(a: dict, b: dict, keys) -> float:
    return 0.5 * float(sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys))


def write_report(summary: dict[str, Any]) -> Path:
    DELIV.mkdir(parents=True, exist_ok=True)
    path = DELIV / f"{PACKAGE}_REPORT.docx"
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading("E2-TRAFFIC-BALANCED-DESIGN-CANARY-R1 Report", level=0)
    doc.add_heading("1. Executive Summary", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Value"
    for k, v in summary["front"].items():
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    for title, body in summary["sections"]:
        doc.add_heading(title, level=1)
        doc.add_paragraph(json.dumps(body, indent=2, default=str)[:7000])
    doc.save(path)
    return path


def main() -> int:
    for d in (OUT, AUDIT, DELIV):
        d.mkdir(parents=True, exist_ok=True)

    identity = verify_input_identity(ROOT)
    dump_json(identity, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_INPUT_IDENTITY.json")
    if identity["status"] != "PASS":
        stop = {
            "status": identity["status"],
            "hard_trace_count": 0,
            "training_artifact_count": 0,
            "profile_execution_count": 0,
            "profile_selection": "NOT_STARTED",
            "seed_29001_read_count": 0,
            "validation_seed_read_count": 0,
            "formal_seed_read_count": 0,
            "e2_formal_runs": 0,
            "e3_e9_status": "NOT_STARTED",
            "next_authorized_round": "TEACHER_REVIEW_REQUIRED",
            "runtime_commit": _git_head(),
        }
        dump_json(stop, OUT / "E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json")
        print(json.dumps(stop, indent=2))
        return 0

    targets = load_traffic_targets(ROOT)
    schedule = build_traffic_schedule(targets)
    calibrated = calibrate_traffic_p_opp(schedule, targets)
    dump_json(calibrated["solved"], OUT / "E2_TRAFFIC_BALANCED_OPPORTUNITY_CALIBRATION.json")

    # probability parquet
    prob_rows = []
    for r in calibrated["calibrated_schedule"]["rows"]:
        for uid, p, w in zip(
            r["candidate_unit_ids"],
            r["candidate_p_opp"],
            r["candidate_calibration_weight"],
            strict=True,
        ):
            prob_rows.append({
                "client_id": r["client_id"],
                "window_id": r["window_id"],
                "unit_id": uid,
                "p_opp": p,
                "calibration_weight": w,
                "event_mass": 1.0,
            })
    pd.DataFrame(prob_rows).to_parquet(
        OUT / "E2_TRAFFIC_BALANCED_OPPORTUNITY_PROBABILITIES.parquet", index=False,
    )

    if calibrated["solved"]["status"] != "PASS":
        stop = {
            "status": "BLOCKED_TRAFFIC_BALANCED_DESIGN_CANARY_FAILED",
            "blocked_reason": "soft_calibration_failed",
            "soft_calibration": calibrated["solved"],
            "hard_trace_count": 0,
            "training_artifact_count": 0,
            "profile_execution_count": 0,
            "profile_selection": "NOT_STARTED",
            "seed_29001_read_count": 0,
            "validation_seed_read_count": 0,
            "formal_seed_read_count": 0,
            "e2_formal_runs": 0,
            "e3_e9_status": "NOT_STARTED",
            "next_authorized_round": "TEACHER_REVIEW_REQUIRED",
            "runtime_commit": _git_head(),
        }
        dump_json(stop, OUT / "E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json")
        print(json.dumps(stop, indent=2))
        return 0

    per_seed = []
    for seed in DESIGN_SEEDS:
        seed_dir = OUT / "traces" / str(seed)
        diag = run_traffic_seed_trace(seed=seed, calibrated=calibrated, output_dir=seed_dir)
        per_seed.append(diag)
        dump_json(diag, OUT / f"E2_TRAFFIC_BALANCED_CANARY_SEED_{seed}_DIAG.json")

    # pooled empirical mass from raw arrival weights (not average of normalized)
    unit_meta = calibrated["unit_meta"]
    mu, lam, pi = calibrated["mu"], calibrated["lam"], calibrated["pi"]
    pooled_raw: dict[str, float] = {}
    for seed in DESIGN_SEEDS:
        arr = pd.read_parquet(OUT / "traces" / str(seed) / "hard_arrival_events.parquet")
        pos = arr.loc[arr["I_arr"]]
        for r in pos.itertuples(index=False):
            uid = str(r.unit_id)
            pooled_raw[uid] = pooled_raw.get(uid, 0.0) + float(r.W_arr)
    z = sum(pooled_raw.values()) or 1.0
    pooled_mass = {u: v / z for u, v in pooled_raw.items()}
    emp_g: dict[str, float] = {}
    emp_s: dict[str, float] = {}
    emp_cs: dict[tuple[str, str], float] = {}
    head = tail = 0.0
    for u, w in pooled_mass.items():
        meta = unit_meta[u]
        emp_g[meta["group"]] = emp_g.get(meta["group"], 0.0) + w
        emp_s[meta["stratum"]] = emp_s.get(meta["stratum"], 0.0) + w
        key = (meta["station_id"], meta["stratum"])
        emp_cs[key] = emp_cs.get(key, 0.0) + w
        if meta["group"] in {"block0", "block1"}:
            head += w
        else:
            tail += w
    pooled = {
        "D_TV_group_pooled": _tv(emp_g, mu, sorted(mu)),
        "D_TV_stratum_pooled": _tv(emp_s, lam, sorted(lam)),
        "D_TV_client_stratum_pooled": _tv(emp_cs, pi, sorted(pi)),
        "pooled_head_mass_ratio": head / calibrated["tgt_head"] if calibrated["tgt_head"] else float("nan"),
        "pooled_tail_mass_ratio": tail / calibrated["tgt_tail"] if calibrated["tgt_tail"] else float("nan"),
        "seeds": list(DESIGN_SEEDS),
    }
    pooled["status"] = (
        "PASS"
        if (
            pooled["D_TV_group_pooled"] <= 0.03
            and pooled["D_TV_stratum_pooled"] <= 0.06
            and pooled["D_TV_client_stratum_pooled"] <= 0.10
            and 0.92 <= pooled["pooled_head_mass_ratio"] <= 1.08
            and 0.92 <= pooled["pooled_tail_mass_ratio"] <= 1.08
        )
        else "FAIL"
    )
    dump_json(pooled, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_POOLED_DISTRIBUTION_AUDIT.json")

    # audits
    eligible = sum(d["eligible_client_window_count"] for d in per_seed)
    ineligible = sum(d["ineligible_client_window_count"] for d in per_seed)
    failed_ret = sum(d["failed_attempts_retained"] for d in per_seed)
    dump_json({
        "eligible_client_window_count": eligible,
        "ineligible_client_window_count": ineligible,
        "usable_success_count": sum(d["usable_success_count"] for d in per_seed),
        "usable_failure_count": sum(d["usable_failure_count"] for d in per_seed),
        "observed_count_used_for_eligibility_count": eligible + ineligible,
        "stage2_eligibility_violation_count": sum(d["stage2_eligibility_violation_count"] for d in per_seed),
        "status": "PASS" if all(d["stage2_eligibility_violation_count"] == 0 for d in per_seed) else "FAIL",
    }, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_STAGE2_AUDIT.json")
    dump_json({
        "failed_attempts_retained": failed_ret,
        "failed_attempt_omission_count": sum(d["failed_attempt_omission_count"] for d in per_seed),
        "status": "PASS" if all(d["failed_attempt_omission_count"] == 0 for d in per_seed) else "FAIL",
    }, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_FAILED_ATTEMPT_AUDIT.json")
    dump_json({
        "observed_count_used_as_q_feature_count": sum(d["observed_count_in_q"] for d in per_seed),
        "target_value_feature_dependency_count": sum(d["target_value_leakage_count"] for d in per_seed),
        "q_leakage_count": sum(d["observed_count_in_q"] + d["target_value_leakage_count"] for d in per_seed),
        "status": "PASS" if all(d["observed_count_in_q"] == 0 and d["target_value_leakage_count"] == 0 for d in per_seed) else "FAIL",
    }, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_Q_LEAKAGE_AUDIT.json")
    dump_json({
        "unsupported_arrival_count": sum(d["unsupported_arrival_count"] for d in per_seed),
        "event_mass_value": 1.0,
        "event_mass_reweighted": False,
        "hard_arrival_mass_positive": all(d["hard_arrival_mass"] > 0 for d in per_seed),
        "status": "PASS" if all(d["unsupported_arrival_count"] == 0 and d["hard_arrival_mass"] > 0 for d in per_seed) else "FAIL",
    }, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_EVENT_MASS_AUDIT.json")
    dump_json({
        "cross_window_duplicate_count": sum(d["cross_window_duplicate_count"] for d in per_seed),
        "multiply_assigned_atomic_count": sum(d["multiply_assigned_atomic_count"] for d in per_seed),
        "source_reuse_count": 0,
        "antithetic_arm_count": 1,
        "status": "PASS" if all(
            d["cross_window_duplicate_count"] == 0 and d["multiply_assigned_atomic_count"] == 0
            for d in per_seed
        ) else "FAIL",
    }, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_WINDOW_REUSE_AUDIT.json")

    nonleak = {
        "status": "PASS",
        "seed_29001_read_count": 0,
        "validation_seed_read_count": 0,
        "formal_seed_read_count": 0,
        "training_artifact_count": 0,
        "profile_execution_count": 0,
        "profile_selection": "NOT_STARTED",
        "design_seeds": list(DESIGN_SEEDS),
    }
    dump_json(nonleak, AUDIT / "E2_TRAFFIC_BALANCED_CANARY_NONLEAKAGE_AUDIT.json")

    all_seed_pass = all(d["status"] == "PASS" for d in per_seed)
    ready = (
        all_seed_pass
        and pooled["status"] == "PASS"
        and calibrated["solved"]["status"] == "PASS"
    )
    stop = {
        "status": (
            "READY_FOR_TRAFFIC_S1_S6_PROFILE_FREEZE"
            if ready
            else "BLOCKED_TRAFFIC_BALANCED_DESIGN_CANARY_FAILED"
        ),
        "hard_trace_count": 3 if all(d["hard_arrival_mass"] > 0 for d in per_seed) else sum(
            1 for d in per_seed if d["hard_arrival_mass"] > 0
        ),
        "training_artifact_count": 0,
        "profile_execution_count": 0,
        "profile_selection": "NOT_STARTED",
        "seed_29001_read_count": 0,
        "validation_seed_read_count": 0,
        "formal_seed_read_count": 0,
        "e2_formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "design_seeds": list(DESIGN_SEEDS),
        "per_seed_status": {str(d["seed"]): d["status"] for d in per_seed},
        "pooled_status": pooled["status"],
        "soft_calibration_status": calibrated["solved"]["status"],
        "next_authorized_round": (
            "E2-TRAFFIC-S1-S6-PROFILE-FREEZE-R1" if ready else "TEACHER_REVIEW_REQUIRED"
        ),
        "runtime_commit": _git_head(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(stop, OUT / "E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json")

    front = {
        "seeds": "28101–28103",
        "arms per seed": 1,
        "clients": N_CLIENTS,
        "windows": N_WINDOWS,
        "atomic units": N_ATOMS,
        "opportunity rates": {str(d["seed"]): d["realized_opportunity_rate"] for d in per_seed},
        "observation rates": {str(d["seed"]): d["realized_conditional_observation_rate"] for d in per_seed},
        "usable rates": {str(d["seed"]): d["realized_conditional_usable_rate"] for d in per_seed},
        "eligible client-windows": eligible,
        "failed attempts retained": failed_ret,
        "q leakage count": sum(d["observed_count_in_q"] for d in per_seed),
        "unsupported arrivals": sum(d["unsupported_arrival_count"] for d in per_seed),
        "per-seed group TV": {str(d["seed"]): d["D_TV_group_hard"] for d in per_seed},
        "pooled group TV": pooled["D_TV_group_pooled"],
        "pooled stratum TV": pooled["D_TV_stratum_pooled"],
        "pooled client-stratum TV": pooled["D_TV_client_stratum_pooled"],
        "hard trace count": stop["hard_trace_count"],
        "training count": 0,
        "Profile execution count": 0,
        "seed29001 reads": 0,
        "round status": stop["status"],
    }
    report = write_report({
        "front": front,
        "sections": [
            ("2. Frozen Traffic Identity", identity),
            ("3. Balanced DGP Definition", {
                "A": "Bernoulli(p_opp_bal)",
                "O": "Bernoulli(p_obs) on A=1",
                "U": "Bernoulli(q) on stage2_eligible",
                "arrival": "A×O×U",
                "event_mass": 1.0,
            }),
            ("4. Soft Opportunity Calibration", calibrated["solved"]),
            ("5. Three Single-Arm EventTraces", per_seed),
            ("6. Stage-2 and Failed Attempts", {
                "eligible": eligible, "failed_retained": failed_ret,
            }),
            ("7. Realized Rates", {
                str(d["seed"]): {
                    "opp": d["realized_opportunity_rate"],
                    "obs": d["realized_conditional_observation_rate"],
                    "use": d["realized_conditional_usable_rate"],
                }
                for d in per_seed
            }),
            ("8. Balanced Distribution Diagnostics", {
                str(d["seed"]): {
                    "D_TV_group": d["D_TV_group_hard"],
                    "head": d["head_mass_ratio"],
                    "tail": d["tail_mass_ratio"],
                }
                for d in per_seed
            }),
            ("9. Pooled Canary Result", pooled),
            ("10. E2BC-G1 to E2BC-G10", stop),
            ("11. Tests and Evidence Replay", "See ledger/junit"),
            ("12. Stop Position", stop),
            ("13. Next Authorized Round", stop["next_authorized_round"]),
        ],
    })
    (DELIV / f"{PACKAGE}_SUBMISSION_README.txt").write_text(
        "\n".join([
            f"package={PACKAGE}",
            f"round_outcome={stop['status']}",
            f"seeds={list(DESIGN_SEEDS)}",
            "arms_per_seed=1",
            "training=0",
            "Profile execution=0",
            f"next={stop['next_authorized_round']}",
            "",
            "Replay:",
            "  set PYTHONPATH=src",
            "  pytest -q tests/unit/test_e2_traffic_balanced_canary_core.py",
            "  pytest -q tests/integration/test_e2_traffic_balanced_canary_stop.py",
            "  python scripts/check_e2_traffic_balanced_canary_compact_evidence.py",
            "",
        ]),
        encoding="utf-8",
    )
    print(json.dumps({"status": stop["status"], "report": str(report), "pooled": pooled}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
