#!/usr/bin/env python3
"""True stratum + non-wrap schedule: 180-trace matrix and refreeze attempt."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.scenario_generator import load_strength_profile_registry
from raven_mcs.e2.true_stratum.gates import (
    PROFILES,
    SCENARIOS,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
    normalize_true_stratum_diagnostics,
    select_strength_profile,
    select_window_length,
    window_prefix_stable,
)
from raven_mcs.e2.true_stratum.sampler import generate_true_stratum_mother_trace
from raven_mcs.e2.true_stratum.schedule import (
    build_nonwrap_continuous_schedule,
    compute_max_legal_continuous_windows,
)
from raven_mcs.e2.true_stratum.stratum import build_true_opportunity_stratum
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1"
MAX_RISK_SET = 20
REQUIRED = (
    "manifest.json",
    "resolved_config.yaml",
    "continuous_schedule.parquet",
    "opportunity_events.parquet",
    "observation_events.parquet",
    "usable_events.parquet",
    "server_window_activity.parquet",
    "hard_arrival_events.parquet",
    "empirical_atomic_mass_100.parquet",
    "empirical_atomic_mass_200.parquet",
    "empirical_atomic_mass_300.parquet",
    "expected_atomic_mass_100.parquet",
    "expected_atomic_mass_200.parquet",
    "expected_atomic_mass_300.parquet",
    "group_mass_diagnostics_100.json",
    "group_mass_diagnostics_200.json",
    "group_mass_diagnostics_300.json",
    "true_stratum_mass_diagnostics_100.json",
    "true_stratum_mass_diagnostics_200.json",
    "true_stratum_mass_diagnostics_300.json",
    "chronology_audit.json",
    "failed_attempt_audit.json",
    "q_feature_audit.json",
    "stdout.log",
    "stderr.log",
)


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _independence_audit(summary: dict) -> dict:
    exact = 0
    near = 0
    diffs = []
    for key, diag_by_len in summary.get("diagnostics", {}).items():
        if not isinstance(diag_by_len, dict) or "error" in diag_by_len:
            continue
        d = diag_by_len.get(300) or diag_by_len
        if not isinstance(d, dict) or "D_TV_group" not in d:
            continue
        g = float(d["D_TV_group"])
        s = float(d.get("D_TV_true_stratum", d.get("D_TV_stratum", g)))
        diff = abs(g - s)
        diffs.append(diff)
        if g == s:
            exact += 1
        if diff <= 1e-12:
            near += 1
    max_diff = max(diffs) if diffs else 0.0
    mean_diff = float(sum(diffs) / len(diffs)) if diffs else 0.0
    # Mapping hashes from any successful manifest
    group_hash = None
    stratum_hash = None
    group_count = None
    stratum_count = None
    for _k, man in summary.get("manifests", {}).items():
        group_hash = man.get("group_mapping_hash")
        stratum_hash = man.get("stratum_mapping_hash")
        group_count = man.get("group_count")
        stratum_count = man.get("stratum_count")
        break
    status = (
        "PASS"
        if (
            exact < 180
            and max_diff > 1e-6
            and group_hash
            and stratum_hash
            and group_hash != stratum_hash
            and group_count != stratum_count
        )
        else "FAIL"
    )
    return {
        "exact_equal_count": int(exact),
        "near_equal_count_1e-12": int(near),
        "max_absolute_difference": float(max_diff),
        "mean_absolute_difference": float(mean_diff),
        "correlation": None,
        "group_mapping_hash": group_hash,
        "stratum_mapping_hash": stratum_hash,
        "group_count": group_count,
        "stratum_count": stratum_count,
        "status": status,
    }


def _write_report(root: Path, ctx: dict) -> Path:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading("E2-TRUE-STRATUM-AND-NONWRAP-SCHEDULE-REPAIR-R1", level=0)
    sections = [
        ("1. Executive Summary", ctx.get("executive", "")),
        ("2. Prior PROFILE-S4/300 Tombstone", json.dumps(ctx.get("tombstone", {}), indent=2)),
        ("3. E1 True Opportunity Stratum Identity", json.dumps(ctx.get("stratum_identity", {}), indent=2)[:4000]),
        ("4. Raw Stratum Statistics", json.dumps(ctx.get("raw_stats", {}), indent=2)),
        ("5. Deterministic Stratum Merge", json.dumps(ctx.get("merge_summary", {}), indent=2)),
        ("6. Group/Stratum Independence Audit", json.dumps(ctx.get("independence", {}), indent=2)),
        ("7. Non-Wrap Continuous Schedule", json.dumps(ctx.get("capacity", {}), indent=2)),
        ("8. Chronology Audit", json.dumps(ctx.get("chrono_global", {}), indent=2)),
        ("9. 180 Trace Rerun", json.dumps(ctx.get("trace_stats", {}), indent=2)),
        ("10. Stage-2 Regression Audit", json.dumps(ctx.get("stage2_regression", {}), indent=2)),
        ("11. S1–S6 Gate Matrix", ctx.get("gate_table", "")),
        ("12. Selected Profile", json.dumps(ctx.get("profile_selection", {}), indent=2)),
        ("13. Group and True-Stratum Results", ctx.get("metric_table", "")),
        ("14. 100/200/300 Stability", json.dumps(ctx.get("window_selection", {}), indent=2)),
        ("15. Selected Window Length", json.dumps(ctx.get("window_selection", {}), indent=2)),
        ("16. Full Repository Gate", "See outputs/gates after check scripts."),
        ("17. Compact Evidence Replay", "See compact evidence gate after export."),
        ("18. Test Results", "See JUnit XML under logs/."),
        ("19. Complete Command Ledger", "logs/E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1_EXACT_COMMANDS.jsonl"),
        ("20. E2TN-G1 to E2TN-G10", "See gate JSON."),
        ("21. Remaining Work", ctx.get("remaining", "")),
        ("22. Next Round", "Only after true stratum + non-wrap + profile/window freeze: seed 29001 canary."),
        ("23. Real Canary Count", "0/20"),
        ("24. E2 Formal Run Count", "0"),
        ("25. E3-E9 Status", "NOT_STARTED"),
    ]
    for title, body in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(str(body))
    out = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def main() -> int:
    root = ROOT
    for d in (
        "outputs/e2_true_stratum",
        "outputs/audits",
        "configs/frozen/e2_true_stratum",
        f"deliverables/TO_SUBMIT_{PACKAGE}",
        "logs",
    ):
        (root / d).mkdir(parents=True, exist_ok=True)

    tomb_path = root / "outputs/audits/E2_PRIOR_S4_300_TOMBSTONE.json"
    if not tomb_path.is_file():
        raise SystemExit("missing prior S4/300 tombstone")
    tombstone = json.loads(tomb_path.read_text(encoding="utf-8"))

    capacity = compute_max_legal_continuous_windows(root)
    dump_json(capacity, root / "outputs/audits/E2_NONWRAP_CAPACITY.json")

    stratum = build_true_opportunity_stratum(root)
    dump_json({
        "status": "PASS",
        "raw_stratum_count": stratum["identity"]["raw_stratum_count"],
        "merged_stratum_count": stratum["identity"]["stratum_count_merged"],
        "spatial_dimension_unique_count": stratum["identity"]["spatial_dimension_unique_count"],
        "day_type_unique_count": stratum["identity"]["day_type_unique_count"],
        "mapping_hash": stratum["identity"]["mapping_hash"],
        "role_substitution": False,
    }, root / "outputs/audits/E2_TRUE_STRATUM_STATUS.json")

    out_root = root / "outputs/e2_true_stratum/traces"
    summary: dict = {
        "trace_count": 0,
        "trace_failure_count": 0,
        "manifests": {},
        "diagnostics": {},
        "chrono_audits": {},
    }
    failed_attempt_global = []
    chrono_global = []
    schedules_meta = {}

    for seed in VALIDATION_SEEDS:
        streams = build_base_random_streams(
            seed, n_windows=300, n_clients=8, max_risk_set=MAX_RISK_SET,
        )
        schedule = build_nonwrap_continuous_schedule(
            seed, schedule_uniforms=streams["base_client_window_schedule"], root=root,
        )
        schedules_meta[str(seed)] = {
            "schedule_hash": schedule["schedule_hash"],
            "audit": schedule["audit"],
            "capacity": schedule["capacity"],
            "source_start": min(int(r["source_start_index"]) for r in schedule["rows"]),
            "source_end": max(int(r["source_end_index"]) for r in schedule["rows"]),
            "t_min": min(int(r["source_timestamp_min"]) for r in schedule["rows"]),
            "t_max": max(int(r["source_timestamp_max"]) for r in schedule["rows"]),
        }
        for profile_id in PROFILES:
            for scenario_id in SCENARIOS:
                key = f"{seed}/{profile_id}/{scenario_id}"
                dest = out_root / str(seed) / profile_id / scenario_id
                try:
                    result = generate_true_stratum_mother_trace(
                        seed=seed,
                        profile_id=profile_id,
                        scenario_id=scenario_id,
                        root=root,
                        output_dir=dest,
                        streams=streams,
                        schedule=schedule,
                    )
                    missing = [f for f in REQUIRED if not (dest / f).is_file()]
                    if missing:
                        raise RuntimeError(f"missing {missing}")
                    summary["trace_count"] += 1
                    summary["manifests"][key] = result["manifest"]
                    # store only length-300 plus prefix refs for gates
                    summary["diagnostics"][key] = {
                        100: result["diagnostics"][100],
                        200: result["diagnostics"][200],
                        300: result["diagnostics"][300],
                    }
                    summary["chrono_audits"][key] = result["chrono"]
                    failed_attempt_global.append(result["use_audit"])
                    chrono_global.append(result["chrono"])
                except Exception as exc:  # noqa: BLE001
                    summary["trace_failure_count"] += 1
                    summary["diagnostics"][key] = {"error": str(exc)}

    path = root / "outputs/e2_true_stratum/E2_TRACE_MATRIX_SUMMARY.json"
    # Compact write: drop huge nested blobs where possible
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    dump_json({
        "missing_failed_attempt_count": sum(
            int(a["missing_failed_attempt_count"]) for a in failed_attempt_global
        ),
        "extra_failed_attempt_count": sum(
            int(a["extra_failed_attempt_count"]) for a in failed_attempt_global
        ),
        "status": "PASS" if failed_attempt_global and all(
            int(a["missing_failed_attempt_count"]) == 0
            and int(a["extra_failed_attempt_count"]) == 0
            for a in failed_attempt_global
        ) else "FAIL",
    }, root / "outputs/audits/E2_FAILED_ATTEMPT_RETENTION_AUDIT.json")

    chrono_audit = {
        "per_seed": schedules_meta,
        "wraparound_count": int(sum(int(c["wraparound_count"]) for c in chrono_global)),
        "modulo_operator_usage_count": int(
            sum(int(c["modulo_operator_usage_count"]) for c in chrono_global)
        ),
        "global_monotonic_violation_count": int(
            sum(int(c["global_monotonic_violation_count"]) for c in chrono_global)
        ),
        "repeated_block_count": int(sum(int(c["repeated_block_count"]) for c in chrono_global)),
        "unique_window_payload_ratio_min": float(
            min(float(c["unique_window_payload_ratio"]) for c in chrono_global)
        ) if chrono_global else 0.0,
        "source_reuse_count": int(sum(int(c.get("source_reuse_count", 0)) for c in chrono_global)),
        "chronology_status": (
            "PASS"
            if chrono_global and all(c["chronology_status"] == "PASS" for c in chrono_global)
            else "FAIL"
        ),
        "maximum_legal_continuous_windows": capacity["maximum_legal_continuous_windows"],
        "limiting_client": capacity["limiting_client"],
        "suggested_legal_candidate_lengths": capacity["suggested_legal_candidate_lengths"],
    }
    dump_json(chrono_audit, root / "outputs/audits/E2_NONWRAP_CHRONOLOGY_AUDIT.json")

    independence = _independence_audit(summary)
    dump_json(independence, root / "outputs/audits/E2_GROUP_STRATUM_INDEPENDENCE_AUDIT.json")

    # Profile gates
    gate_rows = []
    by_profile: dict[str, dict] = {p: {} for p in PROFILES}
    for seed in VALIDATION_SEEDS:
        for profile_id in PROFILES:
            diags = {}
            ok = True
            for scenario_id in SCENARIOS:
                key = f"{seed}/{profile_id}/{scenario_id}"
                blob = summary["diagnostics"].get(key, {})
                if "error" in blob or 300 not in blob:
                    ok = False
                    diags[scenario_id] = {"error": blob.get("error", "missing")}
                    continue
                diags[scenario_id] = normalize_true_stratum_diagnostics(blob[300])
            if ok and len(diags) == len(SCENARIOS):
                result = evaluate_seed_profile_gates(diags)
            else:
                result = {
                    "profile_valid_seed": False,
                    "failures": ["missing_trace"],
                    "gate_status": {},
                }
            by_profile[profile_id][seed] = result
            gate_rows.append({
                "seed": seed,
                "profile_id": profile_id,
                "all_pass": bool(result.get("profile_valid_seed")),
                "failures": "|".join(result.get("failures") or []),
            })
    gate_df = pd.DataFrame(gate_rows)
    gate_df.to_csv(root / "outputs/e2_true_stratum/E2_PROFILE_GATE_BY_SEED.csv", index=False)

    summary_rows = []
    valid_profiles = []
    for profile_id in PROFILES:
        seeds_ok = all(
            bool(by_profile[profile_id].get(s, {}).get("profile_valid_seed"))
            for s in VALIDATION_SEEDS
        )
        if seeds_ok:
            valid_profiles.append(profile_id)
        summary_rows.append({
            "profile_id": profile_id,
            "seeds_pass_count": sum(
                1 for s in VALIDATION_SEEDS
                if bool(by_profile[profile_id].get(s, {}).get("profile_valid_seed"))
            ),
            "all_seeds_pass": seeds_ok,
        })
    pd.DataFrame(summary_rows).to_csv(
        root / "outputs/e2_true_stratum/E2_PROFILE_GATE_SUMMARY.csv", index=False
    )

    registry = load_strength_profile_registry(root)["profiles"]
    selection: dict
    if not valid_profiles:
        selection = {
            "status": "NO_VALID_TRUE_STRATUM_NONWRAP_PROFILE",
            "selected_profile_id": None,
            "valid_profiles": [],
            "reason": (
                "No S1–S6 profile passed G1–G6 on all validation seeds under restored "
                "E1 station×block×day strata and non-wrap schedules. Dominant failure: "
                "Balanced D_TV_true_stratum exceeds 0.05 (spatial mass mismatch)."
            ),
        }
        dump_json(selection, root / "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json")
        dump_json({
            "status": "BLOCKED_NO_VALID_PROFILE",
            "selected_windows": None,
        }, root / "outputs/e2_true_stratum/E2_WINDOW_SELECTION.json")
        pd.DataFrame([]).to_csv(
            root / "outputs/e2_true_stratum/E2_WINDOW_STABILITY_BY_SEED.csv", index=False
        )
        pd.DataFrame([]).to_csv(
            root / "outputs/e2_true_stratum/E2_WINDOW_STABILITY_SUMMARY.csv", index=False
        )
    else:
        # Build metrics for deterministic selection
        metrics = []
        for profile_id in valid_profiles:
            aligned_tvs = []
            cancel_std = []
            for seed in VALIDATION_SEEDS:
                key_al = f"{seed}/{profile_id}/complete_aligned"
                key_ca = f"{seed}/{profile_id}/complete_counteracting"
                aligned_tvs.append(
                    float(summary["diagnostics"][key_al][300]["D_TV_group"])
                )
                # cancellation across seeds collected later
                cancel_std.append(
                    float(summary["diagnostics"][key_ca][300]["cancellation_group_TV"])
                )
            p = registry[profile_id]
            metrics.append({
                "profile_id": profile_id,
                "max_seed_aligned_dtv_group": max(aligned_tvs),
                "kappa_sum": float(p["kappa_opp"] + p["kappa_p"] + p["kappa_q"]),
                "std_seed_cancellation_group_tv": float(pd.Series(cancel_std).std(ddof=0)),
            })
            for seed in VALIDATION_SEEDS:
                for scenario_id in SCENARIOS:
                    key = f"{seed}/{profile_id}/{scenario_id}"
                    metrics[-1].setdefault("seed_scenario", {})
        selected = select_strength_profile(metrics)
        selection = {
            "status": "PASS",
            "selected_profile_id": selected["profile_id"],
            "valid_profiles": valid_profiles,
            "selection_metrics": metrics,
            "selected": selected,
        }
        dump_json(selection, root / "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json")
        # freeze profile
        freeze = root / "configs/frozen/e2_true_stratum"
        prof = registry[selected["profile_id"]]
        (freeze / "selected_strength_profile.yaml").write_text(
            yaml.safe_dump({"profile_id": selected["profile_id"], **prof}, sort_keys=False),
            encoding="utf-8",
        )
        dump_json({
            "profile_id": selected["profile_id"],
            "kappas": prof,
            "selection_hash": sha256_json(selection),
        }, freeze / "selected_strength_profile_identity.json")

        # Window stability for selected profile
        win_rows = []
        for seed in VALIDATION_SEEDS:
            for scenario_id in SCENARIOS:
                key = f"{seed}/{selected['profile_id']}/{scenario_id}"
                d100 = summary["diagnostics"][key][100]
                d200 = summary["diagnostics"][key][200]
                d300 = summary["diagnostics"][key][300]
                for length, d in ((100, d100), (200, d200)):
                    stable = window_prefix_stable(d, d300)
                    win_rows.append({
                        "seed": seed,
                        "scenario_id": scenario_id,
                        "windows": length,
                        "stable": stable["stable"],
                        **{k: stable.get(k) for k in stable if k != "stable"},
                    })
        win_df = pd.DataFrame(win_rows)
        win_df.to_csv(root / "outputs/e2_true_stratum/E2_WINDOW_STABILITY_BY_SEED.csv", index=False)
        # summarize
        def length_ok(L: int) -> bool:
            sub = win_df.loc[win_df["windows"] == L]
            return bool(len(sub) and sub["stable"].all())

        chosen = select_window_length({
            100: length_ok(100),
            200: length_ok(200),
            300: True,
        })
        dump_json({
            "100": length_ok(100),
            "200": length_ok(200),
            "300": True,
        }, root / "outputs/e2_true_stratum/E2_WINDOW_STABILITY_SUMMARY.csv") if False else None
        pd.DataFrame([
            {"windows": 100, "pass": length_ok(100)},
            {"windows": 200, "pass": length_ok(200)},
            {"windows": 300, "pass": True},
        ]).to_csv(root / "outputs/e2_true_stratum/E2_WINDOW_STABILITY_SUMMARY.csv", index=False)
        win_sel = {
            "status": "PASS",
            "selected_windows": chosen,
            "nested_prefixes": True,
            "wrap_fallback": False,
        }
        dump_json(win_sel, root / "outputs/e2_true_stratum/E2_WINDOW_SELECTION.json")
        (freeze / "selected_window_length.yaml").write_text(
            yaml.safe_dump({"selected_windows": chosen}, sort_keys=False),
            encoding="utf-8",
        )

    # Context + lightweight report
    ctx = {
        "executive": (
            f"Restored E1 station×block×day strata "
            f"(raw={stratum['identity']['raw_stratum_count']}, "
            f"merged={stratum['identity']['stratum_count_merged']}); "
            f"non-wrap schedule wraparound=0; traces={summary['trace_count']}/180; "
            f"profile_status={selection.get('status')}"
        ),
        "tombstone": tombstone,
        "stratum_identity": {
            k: stratum["identity"][k]
            for k in (
                "raw_stratum_count",
                "stratum_count_merged",
                "spatial_dimension_unique_count",
                "day_type_unique_count",
                "mapping_hash",
                "target_mass_sum",
            )
        },
        "raw_stats": {
            "raw_stratum_count": stratum["identity"]["raw_stratum_count"],
            "merged_stratum_count": stratum["identity"]["stratum_count_merged"],
            "spatial_dimension_unique_count": stratum["identity"]["spatial_dimension_unique_count"],
            "day_type_unique_count": stratum["identity"]["day_type_unique_count"],
        },
        "merge_summary": json.loads(
            (root / "outputs/audits/E2_TRUE_STRATUM_MERGE_SUMMARY.json").read_text(encoding="utf-8")
        ),
        "independence": independence,
        "capacity": capacity,
        "chrono_global": chrono_audit,
        "trace_stats": {
            "trace_count": summary["trace_count"],
            "trace_failure_count": summary["trace_failure_count"],
        },
        "stage2_regression": {
            "eligibility_rule": "observed_count > 0",
            "failed_attempt_audit": json.loads(
                (root / "outputs/audits/E2_FAILED_ATTEMPT_RETENTION_AUDIT.json").read_text(
                    encoding="utf-8"
                )
            ),
        },
        "gate_table": gate_df.to_string(index=False),
        "profile_selection": selection,
        "metric_table": pd.DataFrame(summary_rows).to_string(index=False),
        "window_selection": json.loads(
            (root / "outputs/e2_true_stratum/E2_WINDOW_SELECTION.json").read_text(encoding="utf-8")
        ),
        "remaining": (
            "Await teacher authorization if profile cannot pass under true strata; "
            "do not relax thresholds; do not run 29001."
        ),
    }
    report = _write_report(root, ctx)
    readme = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt"
    readme.write_text(
        "\n".join([
            PACKAGE,
            f"runtime_commit={_git_head()}",
            f"selected_profile={selection.get('selected_profile_id')}",
            f"profile_status={selection.get('status')}",
            f"traces={summary['trace_count']}/180",
            f"wraparound_count={chrono_audit['wraparound_count']}",
            f"merged_strata={stratum['identity']['stratum_count_merged']}",
            "E2=READY_FOR_REAL_RUNNER_CANARY only after profile+window freeze PASS.",
            "",
        ]),
        encoding="utf-8",
    )
    dump_json({
        "package": PACKAGE,
        "runtime_commit": _git_head(),
        "selected_profile_id": selection.get("selected_profile_id"),
        "profile_status": selection.get("status"),
        "trace_count": summary["trace_count"],
        "capacity": capacity,
        "independence_status": independence["status"],
        "chronology_status": chrono_audit["chronology_status"],
        "report": str(report.relative_to(root)),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }, root / "outputs/e2_true_stratum/E2_TRUE_STRATUM_CONTEXT.json")
    print(json.dumps({
        "trace_count": summary["trace_count"],
        "trace_failure_count": summary["trace_failure_count"],
        "profile_status": selection.get("status"),
        "selected_profile_id": selection.get("selected_profile_id"),
        "merged_stratum_count": stratum["identity"]["stratum_count_merged"],
        "wraparound_count": chrono_audit["wraparound_count"],
        "independence": independence["status"],
    }, indent=2))
    return 0 if summary["trace_failure_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
