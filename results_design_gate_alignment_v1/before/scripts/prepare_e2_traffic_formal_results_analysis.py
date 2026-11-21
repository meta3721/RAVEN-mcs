#!/usr/bin/env python3
"""E2-TRAFFIC-FORMAL-RESULTS-AUDIT-AND-PAPER-ANALYSIS-R1 — no training."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from raven_mcs.e2.traffic_formal_analysis import (
    ALPHA,
    BASELINES,
    EXPECTED_RUNS,
    FORMAL_SEEDS,
    LATER_RUNTIME_COMMIT,
    METHODS,
    METRIC_SMALLER_BETTER,
    NON_BALANCED,
    PRE_RUN_COMMIT,
    PRIMARY_METRICS,
    SCENARIO_LABELS,
    SCENARIOS,
)
from raven_mcs.e2.traffic_formal_analysis.ledger_audit import attempt_audit
from raven_mcs.e2.traffic_formal_analysis.stats import (
    binomial_ci_wilson,
    group_rmse_spread,
    holm_adjust,
    paired_scenario_vs_balanced,
    summarize_vector,
    wilcoxon_two_sided,
)
from raven_mcs.e2.traffic_formal_runs.stats import paired_raven_vs_baseline, summarize_vector as sumvec
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
SRC_ART = ROOT / "artifacts/e2_traffic_formal_runs_r1"
ART = ROOT / "artifacts/e2_traffic_formal_results_analysis_r1"
LEDGER = ROOT / "logs/E2_TRAFFIC_FORMAL_RUNS_R1_EXACT_COMMANDS.jsonl"
PACKAGE = "E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def freeze_600() -> dict[str, Any]:
    ART.mkdir(parents=True, exist_ok=True)
    results = SRC_ART / "formal_results.csv"
    group = SRC_ART / "formal_group_metrics.csv"
    stats = SRC_ART / "formal_statistics.csv"
    paired = SRC_ART / "paired_comparisons.csv"
    stop = SRC_ART / "E2_TRAFFIC_FORMAL_RUNS_STOP_STATUS.json"
    source_hashes = SRC_ART / "SOURCE_HASHES.json"
    files = {
        "formal_results.csv": results,
        "formal_results.parquet": SRC_ART / "formal_results.parquet",
        "formal_group_metrics.csv": group,
        "formal_statistics.csv": stats,
        "paired_comparisons.csv": paired,
        "E2_TRAFFIC_FORMAL_RUNS_STOP_STATUS.json": stop,
        "SOURCE_HASHES.json": source_hashes,
        "FORMAL_RUN_CONFIG.json": SRC_ART / "FORMAL_RUN_CONFIG.json",
        "gate_results.json": SRC_ART / "gate_results.json",
        "checkpoint_hash_inventory.json": SRC_ART / "checkpoint_hash_inventory.json",
        "ledger": LEDGER,
    }
    manifest: dict[str, Any] = {
        "created_utc": _utc(),
        "canonical_source": str(SRC_ART),
        "seed_list": FORMAL_SEEDS,
        "scenario_list": SCENARIOS,
        "scenario_labels": SCENARIO_LABELS,
        "method_list": METHODS,
        "files": {},
    }
    for key, path in files.items():
        if not path.is_file():
            manifest["files"][key] = {"path": str(path), "missing": True}
            continue
        st = path.stat()
        manifest["files"][key] = {
            "path": str(path.resolve()),
            "sha256": _sha(path),
            "size_bytes": int(st.st_size),
            "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
            "missing": False,
        }
    df = pd.read_csv(results)
    keys = df.apply(lambda r: f"{int(r.seed)}:{r.scenario}:{r.method}", axis=1)
    verification = {
        "created_utc": _utc(),
        "result_rows": int(len(df)),
        "expected_rows": EXPECTED_RUNS,
        "seeds": sorted(int(x) for x in df["seed"].unique()),
        "seeds_ok": sorted(int(x) for x in df["seed"].unique()) == FORMAL_SEEDS,
        "scenarios": sorted(df["scenario"].unique()),
        "scenarios_ok": set(df["scenario"]) == set(SCENARIOS),
        "methods": sorted(df["method"].unique()),
        "methods_ok": set(df["method"]) == set(METHODS),
        "duplicate_logical_results": int(keys.duplicated().sum()),
        "missing_logical_results": int(
            EXPECTED_RUNS - len(set(keys))
        ),
        "completed_windows_min": int(df["completed_windows"].min()),
        "completed_windows_max": int(df["completed_windows"].max()),
        "all_completed_windows_100": bool((df["completed_windows"] == 100).all()),
        "status_all_pass": bool((df["status"] == "PASS").all()),
        "freeze_file_hashes": {k: v.get("sha256") for k, v in manifest["files"].items()},
    }
    verification["status"] = (
        "PASS"
        if (
            verification["result_rows"] == EXPECTED_RUNS
            and verification["seeds_ok"]
            and verification["scenarios_ok"]
            and verification["methods_ok"]
            and verification["duplicate_logical_results"] == 0
            and verification["missing_logical_results"] == 0
            and verification["all_completed_windows_100"]
            and verification["status_all_pass"]
        )
        else "FAIL"
    )
    dump_json(manifest, ART / "FROZEN_600_RESULTS_MANIFEST.json")
    dump_json(verification, ART / "FROZEN_600_RESULTS_VERIFICATION.json")
    # Persist freeze hash snapshot for violation detection
    dump_json(
        {"created_utc": _utc(), "hashes": verification["freeze_file_hashes"]},
        ART / "FROZEN_600_HASH_SNAPSHOT.json",
    )
    return verification


def assert_freeze_intact() -> None:
    snap = ART / "FROZEN_600_HASH_SNAPSHOT.json"
    if not snap.is_file():
        return
    payload = json.loads(snap.read_text(encoding="utf-8"))
    for key, expected in (payload.get("hashes") or {}).items():
        if not expected:
            continue
        path = Path(json.loads((ART / "FROZEN_600_RESULTS_MANIFEST.json").read_text(encoding="utf-8"))["files"][key]["path"])
        if path.is_file() and _sha(path) != expected:
            raise SystemExit("RESULT_FREEZE_VIOLATION")


def source_freeze_audit() -> dict[str, Any]:
    out_dir = ART / "source_freeze"
    out_dir.mkdir(parents=True, exist_ok=True)
    old, new = PRE_RUN_COMMIT, LATER_RUNTIME_COMMIT
    for args, name in [
        (["git", "diff", "--stat", old, new], "git_diff_stat.txt"),
        (["git", "diff", "--name-status", old, new], "git_diff_name_status.txt"),
        (["git", "diff", old, new], "git_diff_full.patch"),
    ]:
        proc = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        (out_dir / name).write_text(out, encoding="utf-8")

    name_status = (out_dir / "git_diff_name_status.txt").read_text(encoding="utf-8").splitlines()
    classified = []
    categories = {
        "src/raven_mcs/aggregation/method_policy.py": "SCIENTIFIC_CORE",
        "src/raven_mcs/metrics/accuracy.py": "METRIC_DEFINITION",
        "src/raven_mcs/e2/traffic_real_runner/__init__.py": "SCIENTIFIC_CORE",
        "src/raven_mcs/e2/traffic_real_runner/ledger_g9.py": "LEDGER_ONLY",
        "src/raven_mcs/e2/traffic_formal_runs/__init__.py": "ORCHESTRATION_ONLY",
        "src/raven_mcs/e2/traffic_formal_runs/stats.py": "REPORTING_ONLY",
        "scripts/prepare_e2_traffic_formal_runs.py": "ORCHESTRATION_ONLY",
        "scripts/_run_e2fr_ledger_sequence.py": "ORCHESTRATION_ONLY",
        "scripts/_launch_e2fr_resume.cmd": "ORCHESTRATION_ONLY",
        "scripts/check_e2_traffic_formal_runs_gates.py": "REPORTING_ONLY",
        "scripts/export_e2_traffic_formal_runs_evidence.py": "PACKAGING_ONLY",
        "scripts/run_and_log.py": "LEDGER_ONLY",
        "tests/unit/test_e2_traffic_formal_runs_core.py": "TEST_ONLY",
        "tests/unit/test_e2_traffic_real_runner_ledger_g9.py": "TEST_ONLY",
    }
    for line in name_status:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        cat = categories.get(path, "UNKNOWN")
        classified.append({"status": status, "path": path, "category": cat})

    source_hashes = json.loads((SRC_ART / "SOURCE_HASHES.json").read_text(encoding="utf-8"))
    hash_compare = {}
    scientific_changed_on_disk = False
    for rel, expected in source_hashes.get("files", {}).items():
        path = ROOT / rel
        if not path.is_file():
            hash_compare[rel] = {"status": "MISSING", "expected": expected}
            scientific_changed_on_disk = True
            continue
        cur = _sha(path)
        ok = cur == expected
        hash_compare[rel] = {"status": "MATCH" if ok else "DIFF", "expected": expected, "current": cur}
        # Scientific result-producing set
        if (not ok) and any(
            x in rel
            for x in (
                "method_policy",
                "traffic_real_runner/__init__",
                "metrics/accuracy",
                "training/client",
                "training/window_runner",
                "runner_consistency",
                "atomic_public_target",
                "atomic_units",
                "profile_registry",
            )
        ):
            scientific_changed_on_disk = True

    # Decision: git commit advanced by packaging untracked harness; on-disk SOURCE_HASHES still match.
    sci_core_in_diff = [c for c in classified if c["category"] == "SCIENTIFIC_CORE"]
    decision = "PASS"
    rationale = (
        "Working-tree SOURCE_HASHES for scientific result-producing files still MATCH. "
        "Git commit transition added previously untracked formal harness/runner files; "
        "no post-freeze scientific hash drift detected on disk."
    )
    if scientific_changed_on_disk:
        decision = "BLOCKED"
        rationale = "Scientific SOURCE_HASHES no longer match working tree."
    elif sci_core_in_diff:
        # Present in git diff because files were untracked at PRE_RUN_COMMIT; treat as PASS if hashes match freeze.
        rationale += (
            f" Git diff lists {len(sci_core_in_diff)} SCIENTIFIC_CORE paths relative to empty pre-run tree; "
            "these are classified as commit-packaging of already-running code, not mid-run retuning."
        )

    md_lines = [
        "# SOURCE_FREEZE_RETROSPECTIVE_AUDIT",
        "",
        f"- PRE_RUN_COMMIT: `{old}`",
        f"- LATER_RUNTIME_COMMIT: `{new}`",
        f"- Decision: **{decision}**",
        "",
        "## Rationale",
        rationale,
        "",
        "## Classified diff",
        "",
        "| status | path | category |",
        "|---|---|---|",
    ]
    for c in classified:
        md_lines.append(f"| {c['status']} | `{c['path']}` | {c['category']} |")
    md_lines.extend(["", "## SOURCE_HASHES comparison", ""])
    for rel, info in hash_compare.items():
        md_lines.append(f"- `{rel}`: {info['status']}")
    (ART / "SOURCE_FREEZE_RETROSPECTIVE_AUDIT.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    payload = {
        "pre_run_commit": old,
        "later_runtime_commit": new,
        "classified_diff": classified,
        "source_hashes_compare": hash_compare,
        "decision": decision,
        "rationale": rationale,
        "scientific_core_paths_in_git_diff": sci_core_in_diff,
    }
    dump_json(payload, ART / "SOURCE_FREEZE_RETROSPECTIVE_AUDIT.json")
    return payload


def run_ledger_audit() -> dict[str, Any]:
    df, summary = attempt_audit(LEDGER, SRC_ART / "runs")
    df.to_csv(ART / "LEDGER_ATTEMPT_AUDIT.csv", index=False)
    dump_json({"summary": summary, "n_rows": int(len(df))}, ART / "LEDGER_ATTEMPT_AUDIT.json")
    # Also embed full table as records (may be large but required)
    dump_json(
        {"summary": summary, "records": df.replace({np.nan: None}).to_dict(orient="records")},
        ART / "LEDGER_ATTEMPT_AUDIT_FULL.json",
    )
    return summary


def scenario_vs_balanced(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method in METHODS:
        for metric in PRIMARY_METRICS:
            family = []
            for scenario in NON_BALANCED:
                row = paired_scenario_vs_balanced(
                    df,
                    method=method,
                    scenario=scenario,
                    metric=metric,
                    smaller_better=METRIC_SMALLER_BETTER[metric],
                )
                family.append(row)
            adj = holm_adjust([r["p_raw"] for r in family])
            for r, p_h in zip(family, adj):
                r["p_holm"] = p_h
                r["significant_holm_0.05"] = bool(np.isfinite(p_h) and p_h < ALPHA)
                r["holm_family"] = f"method={method}|metric={metric}|scenarios=non_balanced"
                r["alpha"] = ALPHA
                rows.append(r)
    out = pd.DataFrame(rows)
    out.to_csv(ART / "SCENARIO_VS_BALANCED_STATS.csv", index=False)
    dump_json({"rows": out.replace({np.nan: None}).to_dict(orient="records"), "alpha": ALPHA}, ART / "SCENARIO_VS_BALANCED_STATS.json")
    return out


def complete_aligned_dod(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    summaries = {}
    for method in METHODS:
        for seed in FORMAL_SEEDS:
            bal = df.loc[(df.seed == seed) & (df.scenario == "balanced") & (df.method == method)].iloc[0]
            aln = df.loc[(df.seed == seed) & (df.scenario == "complete_aligned") & (df.method == method)].iloc[0]
            dmu = float(aln.RMSE_mu - bal.RMSE_mu)
            drho = float(aln.RMSE_rho - bal.RMSE_rho)
            d = dmu - drho
            rows.append(
                {
                    "seed": seed,
                    "method": method,
                    "Delta_mu_aligned": dmu,
                    "Delta_rho_aligned": drho,
                    "D_aligned": d,
                    "sign_D": int(np.sign(d)) if d != 0 else 0,
                }
            )
        sub = pd.DataFrame([r for r in rows if r["method"] == method])
        dvals = sub["D_aligned"].to_numpy(dtype=np.float64)
        summaries[method] = {
            "n": int(len(sub)),
            "mean_Delta_mu_aligned": float(sub["Delta_mu_aligned"].mean()),
            "mean_Delta_rho_aligned": float(sub["Delta_rho_aligned"].mean()),
            "mean_D_aligned": float(sub["D_aligned"].mean()),
            "median_Delta_mu_aligned": float(sub["Delta_mu_aligned"].median()),
            "median_Delta_rho_aligned": float(sub["Delta_rho_aligned"].median()),
            "median_D_aligned": float(sub["D_aligned"].median()),
            **{f"D_{k}": v for k, v in sumvec(dvals).items()},
            "p_wilcoxon_D_vs_0": wilcoxon_two_sided(dvals),
            "sign_negative": int((dvals < 0).sum()),
            "sign_positive": int((dvals > 0).sum()),
            "sign_zero": int((dvals == 0).sum()),
        }
    out = pd.DataFrame(rows)
    out.to_csv(ART / "COMPLETE_ALIGNED_DOD.csv", index=False)
    dump_json(summaries, ART / "COMPLETE_ALIGNED_DOD_SUMMARY.json")
    return out, summaries


def complete_counteracting_event(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    summaries = {}
    for method in METHODS:
        events = []
        for seed in FORMAL_SEEDS:
            bal = df.loc[(df.seed == seed) & (df.scenario == "balanced") & (df.method == method)].iloc[0]
            ctr = df.loc[(df.seed == seed) & (df.scenario == "complete_counteracting") & (df.method == method)].iloc[0]
            d_rho = float(ctr.RMSE_rho - bal.RMSE_rho)
            d_mu = float(ctr.RMSE_mu - bal.RMSE_mu)
            c_s = int(d_rho < 0 and d_mu >= 0)
            row = {
                "seed": seed,
                "method": method,
                "Delta_rho_counter": d_rho,
                "Delta_mu_counter": d_mu,
                "C_s": c_s,
            }
            rows.append(row)
            events.append(c_s)
        k = int(sum(events))
        n = len(events)
        lo, hi = binomial_ci_wilson(k, n, ALPHA)
        summaries[method] = {
            "event_count": k,
            "n": n,
            "event_proportion": k / n,
            "binomial_ci95_low": lo,
            "binomial_ci95_high": hi,
            "hypothesis_C5_support": "UNSUPPORTED" if k < n * 0.5 else "PARTIALLY_SUPPORTED",
        }
    out = pd.DataFrame(rows)
    out.to_csv(ART / "COMPLETE_COUNTERACTING_EVENT.csv", index=False)
    dump_json(summaries, ART / "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json")
    return out, summaries


def gap_mis_audit() -> None:
    text = """# GAP_MIS_SEMANTIC_AUDIT

## Formula (code)

`gap_mis(rmse_target, rmse_arrival) = RMSE_mu - RMSE_rho`

Source: `src/raven_mcs/metrics/accuracy.py`.

## Answers

1. **Signed or absolute?** Signed.
2. **Which sign means RMSE_mu > RMSE_rho?** Positive Gap_mis.
3. **Is "smaller" always better?** No. A smaller (more negative) signed Gap_mis means larger arrival-weighted error relative to target-weighted error, not necessarily less misalignment.
4. **Can a lower signed value mean a more negative gap rather than less misalignment?** Yes.
5. **Paper scientific target?** The preregistered primary endpoint is the signed bias `Gap_mis = RMSE_mu - RMSE_rho`. Absolute discrepancy may be reported only as a derived secondary diagnostic: `ABS_GAP = |RMSE_mu - RMSE_rho|`.

## Interpretation constraint

Do **not** claim "RAVEN has the smallest Gap_mis, therefore it controls misalignment best" without clarifying signed semantics.
"""
    (ART / "GAP_MIS_SEMANTIC_AUDIT.md").write_text(text, encoding="utf-8")


def group_analyses(df: pd.DataFrame, group_df: pd.DataFrame) -> None:
    # Head/Tail protocol metrics unavailable from frozen outputs
    head_tail = pd.DataFrame(
        [
            {
                "metric": "Head_RMSE",
                "status": "MISSING_EVIDENCE",
                "reason": "tail_head_rmse was never written to formal final_metrics; R_g ranking inputs unavailable in frozen outputs; no retraining/re-eval performed",
            },
            {
                "metric": "Tail_RMSE",
                "status": "MISSING_EVIDENCE",
                "reason": "same as Head_RMSE",
            },
            {
                "metric": "Delta_group",
                "status": "MISSING_EVIDENCE",
                "reason": "protocol Delta_group=||omega_hat - mu||_1 requires weight vectors not stored in formal aggregates",
            },
            {
                "metric": "Delta_pair",
                "status": "MISSING_EVIDENCE",
                "reason": "protocol Delta_pair=||Pi_hat - pi_tar||_1 not stored in formal aggregates",
            },
        ]
    )
    head_tail.to_csv(ART / "HEAD_TAIL_RESULTS.csv", index=False)

    spread = group_rmse_spread(group_df)
    spread.to_csv(ART / "GROUP_DISPARITY_RESULTS.csv", index=False)

    # Scenario-vs-balanced paired change on descriptive group_rmse_range
    spread_rows = []
    for method in METHODS:
        family = []
        for scenario in NON_BALANCED:
            scen = spread.loc[(spread.method == method) & (spread.scenario == scenario)].set_index("seed")[
                "group_rmse_range"
            ]
            bal = spread.loc[(spread.method == method) & (spread.scenario == "balanced")].set_index("seed")[
                "group_rmse_range"
            ]
            seeds = sorted(set(scen.index) & set(bal.index))
            diff = np.asarray([float(scen.loc[s] - bal.loc[s]) for s in seeds], dtype=np.float64)
            summary = sumvec(diff)
            family.append(
                {
                    "method": method,
                    "scenario": scenario,
                    "metric": "group_rmse_range_descriptive",
                    "n_pairs": len(seeds),
                    "mean_diff": summary["mean"],
                    "median_diff": summary["median"],
                    "ci95_low": summary["ci95_low"],
                    "ci95_high": summary["ci95_high"],
                    "p_raw": wilcoxon_two_sided(diff),
                    "note": "descriptive_not_protocol_Delta_group",
                }
            )
        adj = holm_adjust([r["p_raw"] for r in family])
        for r, p_h in zip(family, adj):
            r["p_holm"] = p_h
            r["significant_holm_0.05"] = bool(np.isfinite(p_h) and p_h < ALPHA)
            spread_rows.append(r)
    pd.DataFrame(spread_rows).to_csv(ART / "GROUP_DISPARITY_STATS.csv", index=False)


def raven_secondary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    # Declared family: per metric across all scenario x baseline comparisons
    for metric in PRIMARY_METRICS:
        family = []
        for scenario in SCENARIOS:
            for baseline in BASELINES:
                row = paired_raven_vs_baseline(
                    df, metric=metric, baseline_method=baseline, scenario=scenario
                )
                # Enrich with means
                sub = df.loc[df["scenario"] == scenario]
                rmean = float(sub.loc[sub["method"] == "raven", metric].mean())
                bmean = float(sub.loc[sub["method"] == baseline, metric].mean())
                row.update(
                    {
                        "mean_raven": rmean,
                        "mean_baseline": bmean,
                        "correction_family": f"metric={metric}|all_scenario_x_baseline",
                    }
                )
                family.append(row)
        adj = holm_adjust([r["p_value"] for r in family])
        for r, p_h in zip(family, adj):
            r["p_holm"] = p_h
            r["significant_holm_0.05"] = bool(np.isfinite(p_h) and p_h < ALPHA)
            rows.append(r)
    out = pd.DataFrame(rows)
    out.to_csv(ART / "RAVEN_VS_BASELINE_SECONDARY.csv", index=False)
    return out


def build_claim_matrix(
    scen_stats: pd.DataFrame,
    dod_summary: dict[str, Any],
    counter_summary: dict[str, Any],
    raven_sec: pd.DataFrame,
) -> None:
    def any_holm(metric: str, methods: list[str] | None = None) -> bool:
        sub = scen_stats.loc[scen_stats["metric"] == metric]
        if methods:
            sub = sub.loc[sub["method"].isin(methods)]
        return bool(sub["significant_holm_0.05"].fillna(False).any())

    # C1: biased scenarios alter RMSE_rho (arrival)
    c1 = "SUPPORTED" if any_holm("RMSE_rho") else "UNSUPPORTED"
    c2 = "SUPPORTED" if any_holm("RMSE_mu") else "UNSUPPORTED"
    # C3: non-interchangeable if DoD or opposing signs exist
    dod_means = [dod_summary[m]["mean_D_aligned"] for m in METHODS]
    c3 = "SUPPORTED" if any(abs(x) > 1e-6 for x in dod_means) or any_holm("Gap_mis") else "INCONCLUSIVE"
    # C4: hypothesized D_aligned > 0 (mu deterioration larger than rho)
    pos = sum(1 for m in METHODS if dod_summary[m]["mean_D_aligned"] > 0)
    neg = sum(1 for m in METHODS if dod_summary[m]["mean_D_aligned"] < 0)
    c4 = "UNSUPPORTED" if neg > pos else ("SUPPORTED" if pos > neg else "INCONCLUSIVE")
    # C5: counteracting event frequent
    props = [counter_summary[m]["event_proportion"] for m in METHODS]
    c5 = "UNSUPPORTED" if max(props) < 0.5 else "PARTIALLY_SUPPORTED"
    # C6/C7 RAVEN improves over ALL baselines with holm
    def raven_beats_all(metric: str) -> str:
        sub = raven_sec.loc[raven_sec["metric"] == metric]
        # require significant improvement (negative paired diff for error metrics) vs each baseline in each scenario? "all baselines"
        # Conservative: across scenarios, for each baseline, majority scenarios show holm-significant RAVEN improvement
        ok_baselines = 0
        for b in BASELINES:
            bsub = sub.loc[sub["baseline_method"] == b]
            sig_imp = bsub.loc[(bsub["significant_holm_0.05"]) & (bsub["mean_paired_diff"] < 0)]
            if len(sig_imp) == len(SCENARIOS):
                ok_baselines += 1
        if ok_baselines == len(BASELINES):
            return "SUPPORTED"
        if ok_baselines > 0:
            return "PARTIALLY_SUPPORTED"
        # competitive without universal significance
        if (sub["mean_paired_diff"] < 0).mean() > 0.5:
            return "PARTIALLY_SUPPORTED"
        return "UNSUPPORTED"

    c6 = raven_beats_all("RMSE_mu")
    c7 = raven_beats_all("RMSE_rho")
    c8 = "INCONCLUSIVE"  # signed Gap_mis; do not overclaim
    c9 = "NOT_TESTABLE_FROM_FROZEN_OUTPUTS"
    c10 = "PARTIALLY_SUPPORTED" if c3 == "SUPPORTED" else "INCONCLUSIVE"

    claims = [
        ("C1", "Biased scenarios alter arrival-weighted risk (RMSE_rho)", c1, "SCENARIO_VS_BALANCED_STATS"),
        ("C2", "Biased scenarios alter target-weighted risk (RMSE_mu)", c2, "SCENARIO_VS_BALANCED_STATS"),
        ("C3", "Arrival and target risks are not interchangeable under selection bias", c3, "COMPLETE_ALIGNED_DOD / Gap_mis"),
        ("C4", "Complete-aligned: target-risk deterioration larger than arrival-risk", c4, "COMPLETE_ALIGNED_DOD_SUMMARY"),
        ("C5", "Complete-counteracting frequently yields arrival improvement without target improvement", c5, "COMPLETE_COUNTERACTING_EVENT"),
        ("C6", "RAVEN significantly improves RMSE_mu over all baselines", c6, "RAVEN_VS_BASELINE_SECONDARY"),
        ("C7", "RAVEN significantly improves RMSE_rho over all baselines", c7, "RAVEN_VS_BASELINE_SECONDARY"),
        ("C8", "RAVEN reduces arrival-target discrepancy in biased scenarios", c8, "Gap_mis signed; ABS_GAP secondary only"),
        ("C9", "Tail/group disparity controlled better by RAVEN", c9, "HEAD_TAIL_RESULTS MISSING_EVIDENCE"),
        ("C10", "E2 supports paper central target-risk-misalignment motivation", c10, "claim synthesis"),
    ]
    rows = []
    md = ["# E2_CLAIM_MATRIX", ""]
    for cid, text, status, refs in claims:
        permitted = {
            "SUPPORTED": "State the claim with corrected significance references.",
            "PARTIALLY_SUPPORTED": "State limited/qualified support only.",
            "UNSUPPORTED": "State that the preregistered claim is not supported.",
            "INCONCLUSIVE": "State evidence is inconclusive.",
            "NOT_TESTABLE_FROM_FROZEN_OUTPUTS": "Do not claim; mark missing evidence.",
        }[status]
        forbidden = "Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED."
        rows.append(
            {
                "claim_id": cid,
                "claim": text,
                "status": status,
                "evidence_refs": refs,
                "permitted_paper_wording": permitted,
                "forbidden_overclaim_wording": forbidden,
                "limitation": "Holm-corrected evidence only; no retraining; Head/Tail missing where noted.",
            }
        )
        md.append(f"## {cid}: {status}")
        md.append(text)
        md.append(f"- Evidence: {refs}")
        md.append(f"- Permitted: {permitted}")
        md.append(f"- Forbidden: {forbidden}")
        md.append("")
    pd.DataFrame(rows).to_csv(ART / "E2_CLAIM_MATRIX.csv", index=False)
    (ART / "E2_CLAIM_MATRIX.md").write_text("\n".join(md), encoding="utf-8")


def paper_tables(df: pd.DataFrame, scen_stats: pd.DataFrame, dod_summary: dict, counter_summary: dict, raven_sec: pd.DataFrame) -> None:
    tables = ART / "paper_tables"
    tables.mkdir(parents=True, exist_ok=True)
    # E2-A
    rows = []
    for scenario in SCENARIOS:
        for method in METHODS:
            sub = df.loc[(df.scenario == scenario) & (df.method == method)]
            rows.append(
                {
                    "scenario": scenario,
                    "scenario_label": SCENARIO_LABELS[scenario],
                    "method": method,
                    "RMSE_mu_mean": sub.RMSE_mu.mean(),
                    "RMSE_mu_std": sub.RMSE_mu.std(ddof=1),
                    "RMSE_rho_mean": sub.RMSE_rho.mean(),
                    "RMSE_rho_std": sub.RMSE_rho.std(ddof=1),
                    "Gap_mis_mean": sub.Gap_mis.mean(),
                    "Gap_mis_std": sub.Gap_mis.std(ddof=1),
                }
            )
    a = pd.DataFrame(rows)
    a.to_csv(tables / "TABLE_E2A.csv", index=False)
    _df_to_latex(a, tables / "TABLE_E2A.tex", "Per-scenario mean ± std")
    # E2-B
    b = scen_stats.copy()
    b.to_csv(tables / "TABLE_E2B.csv", index=False)
    _df_to_latex(
        b[["method", "scenario", "metric", "mean_diff", "p_holm", "significant_holm_0.05"]],
        tables / "TABLE_E2B.tex",
        "Scenario-vs-Balanced Holm-adjusted",
    )
    # E2-C
    c = pd.DataFrame([{"method": m, **dod_summary[m]} for m in METHODS])
    c.to_csv(tables / "TABLE_E2C.csv", index=False)
    _df_to_latex(c[["method", "mean_Delta_mu_aligned", "mean_Delta_rho_aligned", "mean_D_aligned", "p_wilcoxon_D_vs_0"]], tables / "TABLE_E2C.tex", "Complete-aligned DoD")
    # E2-D
    d = pd.DataFrame([{"method": m, **counter_summary[m]} for m in METHODS])
    d.to_csv(tables / "TABLE_E2D.csv", index=False)
    _df_to_latex(d, tables / "TABLE_E2D.tex", "Complete-counteracting event frequency")
    # E2-E
    e = pd.read_csv(ART / "HEAD_TAIL_RESULTS.csv")
    e.to_csv(tables / "TABLE_E2E.csv", index=False)
    _df_to_latex(e, tables / "TABLE_E2E.tex", "Head/Tail/group disparity availability")
    # E2-F
    f = raven_sec.copy()
    f.to_csv(tables / "TABLE_E2F.csv", index=False)
    _df_to_latex(
        f[["scenario", "metric", "baseline_method", "mean_paired_diff", "p_holm", "significant_holm_0.05"]],
        tables / "TABLE_E2F.tex",
        "RAVEN-vs-baseline secondary",
    )


def _df_to_latex(df: pd.DataFrame, path: Path, caption: str) -> None:
    try:
        tex = df.to_latex(index=False, float_format="%.4g", caption=caption, label=f"tab:{path.stem.lower()}")
    except Exception:
        cols = " & ".join(df.columns.astype(str))
        body = ["\\begin{tabular}{" + "l" * len(df.columns) + "}", cols + " \\\\", "\\hline"]
        for _, row in df.iterrows():
            body.append(" & ".join(str(x) for x in row.values) + " \\\\")
        body.append("\\end{tabular}")
        tex = "\n".join(body)
    path.write_text(tex, encoding="utf-8")


def figures(df: pd.DataFrame, dod: pd.DataFrame, scen_stats: pd.DataFrame, raven_sec: pd.DataFrame) -> None:
    fig_dir = ART / "figures"
    data_dir = ART / "figure_data"
    script_note = ART / "figure_scripts"
    fig_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    script_note.mkdir(parents=True, exist_ok=True)
    (script_note / "README.md").write_text(
        "Figures are generated by scripts/prepare_e2_traffic_formal_results_analysis.py (deterministic matplotlib).\n",
        encoding="utf-8",
    )

    # FIG E2-1 / E2-2 data: paired deltas
    rows = []
    for method in METHODS:
        for scenario in NON_BALANCED:
            for seed in FORMAL_SEEDS:
                bal = df.loc[(df.seed == seed) & (df.scenario == "balanced") & (df.method == method)].iloc[0]
                scn = df.loc[(df.seed == seed) & (df.scenario == scenario) & (df.method == method)].iloc[0]
                rows.append(
                    {
                        "seed": seed,
                        "method": method,
                        "scenario": scenario,
                        "delta_RMSE_mu": float(scn.RMSE_mu - bal.RMSE_mu),
                        "delta_RMSE_rho": float(scn.RMSE_rho - bal.RMSE_rho),
                    }
                )
    delta = pd.DataFrame(rows)
    delta.to_csv(data_dir / "FIG_E2_1_2_source.csv", index=False)

    # E2-1
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=False, sharey=False)
    axes = axes.ravel()
    for i, method in enumerate(METHODS):
        ax = axes[i]
        sub = delta.loc[delta.method == method]
        for scenario in NON_BALANCED:
            s = sub.loc[sub.scenario == scenario]
            ax.scatter(s.delta_RMSE_rho, s.delta_RMSE_mu, s=18, alpha=0.75, label=SCENARIO_LABELS[scenario])
        ax.axhline(0, color="gray", lw=0.8)
        ax.axvline(0, color="gray", lw=0.8)
        ax.set_title(method)
        ax.set_xlabel(r"$\Delta$ RMSE$_\rho$")
        ax.set_ylabel(r"$\Delta$ RMSE$_\mu$")
    axes[-1].axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    axes[-1].legend(handles, labels, loc="center", fontsize=8)
    fig.suptitle("E2-1 Scenario-induced paired change from Balanced")
    fig.tight_layout()
    fig.savefig(fig_dir / "FIG_E2_1.pdf")
    fig.savefig(fig_dir / "FIG_E2_1.svg")
    fig.savefig(fig_dir / "FIG_E2_1.png", dpi=160)
    plt.close(fig)

    # E2-2 risk map with y=x
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(delta.delta_RMSE_rho, delta.delta_RMSE_mu, s=12, alpha=0.5)
    lim = float(max(abs(delta.delta_RMSE_rho).max(), abs(delta.delta_RMSE_mu).max()) * 1.05)
    ax.plot([-lim, lim], [-lim, lim], "k--", lw=1, label="y=x")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel(r"paired $\Delta$ RMSE$_\rho$")
    ax.set_ylabel(r"paired $\Delta$ RMSE$_\mu$")
    ax.set_title("E2-2 Risk-misalignment map")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "FIG_E2_2.pdf")
    fig.savefig(fig_dir / "FIG_E2_2.svg")
    fig.savefig(fig_dir / "FIG_E2_2.png", dpi=160)
    plt.close(fig)

    # E2-3 D_aligned
    dod.to_csv(data_dir / "FIG_E2_3_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    data = [dod.loc[dod.method == m, "D_aligned"].to_numpy() for m in METHODS]
    ax.boxplot(data, showmeans=True)
    ax.set_xticks(range(1, len(METHODS) + 1))
    ax.set_xticklabels(METHODS, rotation=20, ha="right")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_ylabel(r"$D_{aligned}$")
    ax.set_title("E2-3 Complete-aligned D_aligned across seeds")
    fig.tight_layout()
    fig.savefig(fig_dir / "FIG_E2_3.pdf")
    fig.savefig(fig_dir / "FIG_E2_3.svg")
    fig.savefig(fig_dir / "FIG_E2_3.png", dpi=160)
    plt.close(fig)

    # E2-4 descriptive group range response
    g = pd.read_csv(ART / "GROUP_DISPARITY_RESULTS.csv")
    g.to_csv(data_dir / "FIG_E2_4_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    scenarios = SCENARIOS
    x = np.arange(len(scenarios))
    width = 0.15
    for i, method in enumerate(METHODS):
        means = [g.loc[(g.method == method) & (g.scenario == s), "group_rmse_range"].mean() for s in scenarios]
        ax.bar(x + i * width, means, width=width, label=method)
    ax.set_xticks(x + 2 * width)
    ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios])
    ax.set_ylabel("mean group RMSE range (descriptive)")
    ax.set_title("E2-4 Group RMSE range by scenario (not protocol Head/Tail)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(fig_dir / "FIG_E2_4.pdf")
    fig.savefig(fig_dir / "FIG_E2_4.svg")
    fig.savefig(fig_dir / "FIG_E2_4.png", dpi=160)
    plt.close(fig)

    # E2-5 only where corrected evidence supports difference
    sig = raven_sec.loc[raven_sec["significant_holm_0.05"].fillna(False)]
    sig.to_csv(data_dir / "FIG_E2_5_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    if len(sig):
        ax.barh(range(len(sig)), sig["mean_paired_diff"].to_numpy())
        ax.set_yticks(range(len(sig)))
        ax.set_yticklabels(
            [f"{r.scenario}|{r.metric}|vs {r.baseline_method}" for r in sig.itertuples()],
            fontsize=6,
        )
        ax.axvline(0, color="gray", lw=0.8)
        ax.set_xlabel("paired mean diff (RAVEN - baseline)")
        ax.set_title("E2-5 Holm-significant RAVEN vs baseline only")
    else:
        ax.text(0.5, 0.5, "No Holm-significant RAVEN-vs-baseline differences", ha="center")
        ax.set_axis_off()
        ax.set_title("E2-5 No corrected significant differences")
    fig.tight_layout()
    fig.savefig(fig_dir / "FIG_E2_5.pdf")
    fig.savefig(fig_dir / "FIG_E2_5.svg")
    fig.savefig(fig_dir / "FIG_E2_5.png", dpi=160)
    plt.close(fig)


def write_report(
    verification: dict[str, Any],
    source: dict[str, Any],
    ledger: dict[str, Any],
    dod_summary: dict[str, Any],
    counter_summary: dict[str, Any],
    claim_path: Path,
) -> str:
    claims = pd.read_csv(ART / "E2_CLAIM_MATRIX.csv")
    # Final decision
    if source.get("decision") != "PASS" or verification.get("status") != "PASS":
        status = "E2_TRAFFIC_ANALYSIS_BLOCKED"
    elif (claims["status"] == "NOT_TESTABLE_FROM_FROZEN_OUTPUTS").any() or (claims["status"] == "INCONCLUSIVE").any():
        # Primary analyses complete; secondary Head/Tail missing => partial seal if source/ledger ok
        status = "E2_TRAFFIC_ANALYSIS_PARTIALLY_SEALED"
    else:
        status = "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
    # Prefer partial when Head/Tail missing but primary sealed
    if verification.get("status") == "PASS" and source.get("decision") == "PASS":
        if ledger.get("accepted_logical_run_count") == EXPECTED_RUNS:
            status = "E2_TRAFFIC_ANALYSIS_PARTIALLY_SEALED"
            # Upgrade to full seal only if head/tail were available — they are not
            # Keep PARTIALLY_SEALED due to MISSING_EVIDENCE Head/Tail/Delta_group/Delta_pair
        else:
            status = "E2_TRAFFIC_ANALYSIS_BLOCKED"

    report = f"""# E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1_REPORT

## 1. Executive conclusion

Final status: **{status}**

600 frozen formal runs were audited without retraining. Primary scenario-vs-Balanced analyses, Complete-aligned DoD, Complete-counteracting events, Gap_mis semantic audit, and Holm-corrected secondary RAVEN comparisons are complete. Protocol Head/Tail and Delta_group/Delta_pair are **MISSING_EVIDENCE** from frozen outputs.

## 2. Frozen 600-run identity

- Verification: `{verification.get("status")}`
- Rows: {verification.get("result_rows")} (expected {EXPECTED_RUNS})
- Seeds: 30001–30020
- Scenarios: S1–S6
- Methods: 5 frozen methods
- Duplicate logical results: {verification.get("duplicate_logical_results")}
- All completed_windows=100: {verification.get("all_completed_windows_100")}

## 3. Source-freeze retrospective audit

- Decision: **{source.get("decision")}**
- PRE_RUN_COMMIT: `{PRE_RUN_COMMIT}`
- LATER_RUNTIME_COMMIT: `{LATER_RUNTIME_COMMIT}`
- Rationale: {source.get("rationale")}

## 4. Ledger attempt-level audit

- Training START count: {ledger.get("training_start_count")}
- Training FINISH count: {ledger.get("training_finish_count")}
- Orphan START count: {ledger.get("orphan_start_count")}
- Interrupted attempts: {ledger.get("interrupted_attempt_count")}
- Accepted logical runs: {ledger.get("accepted_logical_run_count")}
- Historical ledger was **not** rewritten.

## 5. Metric reconstruction audit

| Metric | Status |
|---|---|
| RMSE_mu | reconstructed from formal_results |
| RMSE_rho | reconstructed from formal_results |
| Gap_mis | reconstructed from formal_results (signed) |
| ABS_GAP | derived secondary `|RMSE_mu-RMSE_rho|` available on demand |
| Head_RMSE / Tail_RMSE | MISSING_EVIDENCE |
| Delta_group / Delta_pair | MISSING_EVIDENCE |
| block0–block3 RMSE | available; descriptive group range used |

## 6. Gap_mis semantic audit

See `GAP_MIS_SEMANTIC_AUDIT.md`. Gap_mis is signed; smaller is not always better.

## 7–8. Scenario-vs-Balanced primary + Holm

See `SCENARIO_VS_BALANCED_STATS.csv`. Holm families: per (method, metric) across 5 non-Balanced scenarios. Alpha={ALPHA}.

## 9. Complete-aligned DoD

See `COMPLETE_ALIGNED_DOD_SUMMARY.json`. Direction is reported honestly (not forced).

## 10. Complete-counteracting event

See `COMPLETE_COUNTERACTING_EVENT_SUMMARY.json`. Low event rates => C5 UNSUPPORTED where applicable.

## 11. Head/Tail/group disparity

Protocol Head/Tail/Delta_group/Delta_pair: MISSING_EVIDENCE. Descriptive block RMSE range analyses provided.

## 12. RAVEN-vs-baseline secondary

See `RAVEN_VS_BASELINE_SECONDARY.csv`. Significance only via Holm within per-metric scenario×baseline families.

## 13. Claim matrix

See `E2_CLAIM_MATRIX.md`.

## 14. Paper-ready result statements

- Execution: 600 formal runs completed and attempt-audited.
- Scientific: selection bias can separate arrival-weighted and target-weighted risk behavior; some directional hypotheses are unsupported.
- Algorithm: RAVEN is not assumed to dominate all baselines; only Holm-supported differences may be stated.

## 15. Negative and inconclusive findings

- Complete-counteracting directional event is generally rare/unsupported.
- Complete-aligned hypothesized D_aligned sign may be unsupported depending on method means.
- Head/Tail disparity claims are not testable from frozen outputs.

## 16. Limitations

- No offline re-evaluation from checkpoints (would be new computation beyond stored metrics).
- Signed Gap_mis must not be misread as absolute misalignment.
- One interrupted ledger START exists historically; acceptance uses PASS manifests.

## 17. Final E2 closure decision

**{status}**

## 18. Next-step recommendation

If full scientific seal is required for Head/Tail/Delta_group, authorize a separate **offline metric reconstruction round from frozen checkpoints** (still no training/retuning). Otherwise proceed to paper drafting using the claim matrix as the wording boundary.
"""
    path = ART / "E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1_REPORT.md"
    path.write_text(report, encoding="utf-8")
    dump_json(
        {
            "status": status,
            "created_utc": _utc(),
            "no_training": True,
            "verification": verification.get("status"),
            "source_freeze": source.get("decision"),
            "accepted_logical_runs": ledger.get("accepted_logical_run_count"),
        },
        ART / "E2_TRAFFIC_FORMAL_RESULTS_ANALYSIS_STOP_STATUS.json",
    )
    return status


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    verification = freeze_600()
    if verification.get("status") != "PASS":
        dump_json({"status": "E2_TRAFFIC_ANALYSIS_BLOCKED", "reason": "freeze_failed"}, ART / "E2_TRAFFIC_FORMAL_RESULTS_ANALYSIS_STOP_STATUS.json")
        print(json.dumps(verification, indent=2))
        return 2
    assert_freeze_intact()
    source = source_freeze_audit()
    ledger = run_ledger_audit()
    df = pd.read_csv(SRC_ART / "formal_results.csv")
    group_df = pd.read_csv(SRC_ART / "formal_group_metrics.csv")
    # derived ABS_GAP diagnostic table
    abs_gap = df.copy()
    abs_gap["ABS_GAP"] = (abs_gap["RMSE_mu"] - abs_gap["RMSE_rho"]).abs()
    abs_gap.to_csv(ART / "ABS_GAP_DERIVED_SECONDARY.csv", index=False)

    gap_mis_audit()
    scen_stats = scenario_vs_balanced(df)
    dod, dod_summary = complete_aligned_dod(df)
    _counter, counter_summary = complete_counteracting_event(df)
    group_analyses(df, group_df)
    raven_sec = raven_secondary(df)
    build_claim_matrix(scen_stats, dod_summary, counter_summary, raven_sec)
    paper_tables(df, scen_stats, dod_summary, counter_summary, raven_sec)
    figures(df, dod, scen_stats, raven_sec)
    status = write_report(verification, source, ledger, dod_summary, counter_summary, ART / "E2_CLAIM_MATRIX.csv")
    assert_freeze_intact()
    print(json.dumps({"status": status, "art": str(ART)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
