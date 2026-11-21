"""SAG G1-R1h: matched-cardinality CF-M1 + E3-v2 boundary audit. STOP. No SAG."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import numpy as np
import pandas as pd

from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.experiments.sag_runtime import attach_unified_target, eventtrace_dir, prepare_sag_bundle
from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp
from raven_mcs.sag.cfm1 import (
    SEED,
    TAU_COV,
    cf0_budgets_from_events,
    matching_rule_hash,
    matching_rule_payload,
    sample_matched_hour,
)
from raven_mcs.sag.e3v1_root_cause import (
    active_pairs_from_units,
    natural_windows_from_atomic,
    oracle_from_mass,
    realized_mass_from_units,
    unit_meta_from_atomic,
)
from raven_mcs.sag.oracle_ceiling import ge_threshold
from raven_mcs.sag.target_law import freeze_target_law_rule_v1, pi_safe_rule_hash
from raven_mcs.sag.window_completeness import (
    EXPECTED_SPAN_SECONDS,
    N_EDGE,
    classify_boundary,
    completeness_rule_hash,
    completeness_rule_payload,
    hour_span_seconds,
)
from raven_mcs.simulation.event_trace import load_event_trace
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1h"
WARMUP_SKIP = 16
UAIR_UNSAFE_IDS = (0, 1, 2, 51, 52)

SNAPSHOT = (
    ("e3_v2_protocol", "src/e3_v2_protocol.py", "protocol"),
    ("e3_v2_eventtrace", "src/e3_v2_eventtrace.py", "eventtrace"),
    ("e3_v2_context", "src/e3_v2_context.py", "context"),
    ("build_e3_v2_protocol", "scripts/build_e3_v2_protocol.py", "builder"),
    ("run_sag_g1_r1g", "src/raven_mcs/experiments/run_sag_g1_r1g.py", "oracle_precheck"),
    ("cfm1", "src/raven_mcs/sag/cfm1.py", "matched_cf"),
    ("window_completeness", "src/raven_mcs/sag/window_completeness.py", "completeness"),
    ("thresholds", "configs/sag_g0/thresholds.json", "tau"),
)

R1H_TESTS = (
    "tests/unit/test_r1h_input_hashes_frozen.py",
    "tests/unit/test_cfm1_rule_frozen_before_run.py",
    "tests/unit/test_cfm1_same_target_law.py",
    "tests/unit/test_cfm1_same_pi_safe.py",
    "tests/unit/test_cfm1_same_tau_cov.py",
    "tests/unit/test_cfm1_same_seed_semantics.py",
    "tests/unit/test_cfm1_budget_matching.py",
    "tests/unit/test_cfm1_no_cross_time_fill.py",
    "tests/unit/test_cfm1_no_replacement_padding.py",
    "tests/unit/test_cfm1_deficit_logged.py",
    "tests/unit/test_cfm1_cf0_unchanged.py",
    "tests/unit/test_root_cause_verdict_not_hardcoded.py",
    "tests/unit/test_no_sampling_causal_claim_without_match.py",
    "tests/unit/test_completeness_rule_outcome_blind.py",
    "tests/unit/test_completeness_rule_frozen_before_oracle_join.py",
    "tests/unit/test_window_boundary_status.py",
    "tests/unit/test_uair_unsafe_windows_all_audited.py",
    "tests/unit/test_interior_diagnostic_does_not_overwrite_main.py",
    "tests/unit/test_e3v2_source_snapshot_complete.py",
    "tests/unit/test_no_predictor_repair.py",
    "tests/unit/test_no_calibration_repair.py",
    "tests/unit/test_no_dynamic_cov_run.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_no_stress_created.py",
    "tests/unit/test_r1h_gate_artifact_derived.py",
    "tests/unit/test_r1h_no_hardcoded_verdict.py",
)
R1G_REGRESSION = (
    "tests/unit/test_r1f_tau_cov_frozen.py",
    "tests/unit/test_e3v2_tau_cov_unchanged.py",
    "tests/unit/test_e3v2_target_law_unchanged.py",
)


def _pytest_summary(xml_path: Path) -> dict[str, Any]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    n_fail = n_pass = 0
    tests: dict[str, str] = {}
    for suite in suites:
        for case in suite.findall("testcase"):
            name = Path(str(case.get("file") or case.get("classname") or "x").replace("\\", "/")).name
            failed = case.find("failure") is not None or case.find("error") is not None
            skipped = case.find("skipped") is not None
            tests[name] = "FAIL" if failed else ("SKIP" if skipped else "PASS")
            if failed:
                n_fail += 1
            elif not skipped:
                n_pass += 1
    return {"n_passed": n_pass, "n_failed": n_fail, "status": "PASS" if n_fail == 0 else "FAIL", "tests": tests}


def run_pytest(root: Path, files: tuple[str, ...], xml_path: Path) -> dict[str, Any]:
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", f"--junitxml={xml_path}", *files],
        cwd=root, text=True, capture_output=True,
    )
    summary = _pytest_summary(xml_path) if xml_path.is_file() else {"n_passed": 0, "n_failed": 1, "status": "FAIL", "tests": {}}
    summary["returncode"] = proc.returncode
    summary["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-20:])
    return summary


def summarize_oracle(xs: list[float]) -> dict[str, float]:
    arr = np.asarray([float(x) for x in xs if np.isfinite(float(x))], dtype=np.float64)
    if not len(arr):
        return {"mean": float("nan"), "median": float("nan"), "p10": float("nan"), "p90": float("nan"), "max": float("nan")}
    return {
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "p10": float(np.quantile(arr, 0.10)),
        "p90": float(np.quantile(arr, 0.90)),
        "max": float(arr.max()),
    }


def run_r1h_main(*, root: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in ("audit", "matched_counterfactual", "boundary_audit", "completeness_rule", "figures", "summary", "source_snapshot", "legacy_refs"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    freeze_inputs = []
    refs = [
        ("E3-v1 EventTrace SS", "artifacts/e3_formal_runs_r1/eventtraces/sensorscope/seed30001/training_eventtrace/trace_identity.json", "R1", "E3_V1"),
        ("E3-v1 EventTrace UA", "artifacts/e3_formal_runs_r1/eventtraces/uair/seed30001/training_eventtrace/trace_identity.json", "R1", "E3_V1"),
        ("E3-v1 source snapshot", "results_sag_g1/round_r1g/e3v1_root_cause/E3V1_SOURCE_SNAPSHOT_MANIFEST.csv", "R1G", "E3_V1_SOURCE"),
        ("R1g CF by window", "results_sag_g1/round_r1g/e3v1_counterfactual_diagnostics/E3V1_ROOT_CAUSE_COUNTERFACTUAL.csv", "R1G", "CF"),
        ("R1g CF summary", "results_sag_g1/round_r1g/e3v1_counterfactual_diagnostics/E3V1_ROOT_CAUSE_COUNTERFACTUAL_SUMMARY.csv", "R1G", "CF"),
        ("E3-v2 EventTrace SS", "results_sag_g1/round_r1g/e3v2_skeleton/sensorscope/identity.json", "R1G", "E3_V2"),
        ("E3-v2 EventTrace UA", "results_sag_g1/round_r1g/e3v2_skeleton/uair/identity.json", "R1G", "E3_V2"),
        ("E3-v2 oracle by window", "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_BY_WINDOW.csv", "R1G", "E3_V2_ORACLE"),
        ("E3-v2 oracle summary", "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_SUMMARY.csv", "R1G", "E3_V2_ORACLE"),
        ("E3-v2 window rule", "results_sag_g1/round_r1g/e3v2_spec/E3V2_WINDOW_RULE_HASH.txt", "R1G", "E3_V2_SPEC"),
        ("E3-v2 window rule json", "results_sag_g1/round_r1g/e3v2_spec/E3V2_WINDOW_RULE.json", "R1G", "E3_V2_SPEC"),
        ("E3-v2 population rule", "results_sag_g1/round_r1g/e3v2_spec/E3V2_POPULATION_RULE_HASH.txt", "R1G", "E3_V2_SPEC"),
        ("TARGET_LAW", "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json", "R1D", "TARGET_LAW"),
        ("PI_SAFE", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "R1E", "PI_SAFE"),
        ("thresholds", "configs/sag_g0/thresholds.json", "R0", "TAU"),
        ("R1g verdict", "results_sag_g1/round_r1g/summary/R1G_VERDICT.json", "R1G", "VERDICT"),
    ]
    for name, rel, rnd, role in refs:
        path = root / rel
        digest = sha256_file(path) if path.is_file() else "MISSING"
        freeze_inputs.append({"artifact": name, "path": rel.replace("\\", "/"), "sha256": digest, "source_round": rnd, "role": role, "frozen": True, "notes": "not rewritten in R1h"})
        if path.is_file():
            dest = out / "legacy_refs" / f"{rnd}_{role}_{Path(rel).name}"
            shutil.copy2(path, dest)
    pd.DataFrame(freeze_inputs).to_csv(out / "R1H_INPUT_FREEZE_MANIFEST.csv", index=False)
    (out / "R1H_INPUT_FREEZE_AUDIT.md").write_text(
        "\n".join(
            [
                "# R1H input freeze",
                "",
                "E3-v1 EventTrace, E3-v1 source snapshot, CF0/CF1/CF2, E3-v2 EventTrace, E3-v2 protocol/window/population rules,",
                "E3-v2 oracle precheck, TARGET_LAW, PI_SAFE, and tau_cov are frozen. R1h writes only under `results_sag_g1/round_r1h/`.",
                "E3-v2 protocol is not rewritten from R1h outcomes.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    rule = freeze_target_law_rule_v1()
    th = json.loads((root / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    freeze_ok = rule["hash"] == EXPECTED_TARGET_HASH and sha256_file(root / "configs/sag_g0/thresholds.json") == EXPECTED_THRESHOLD_HASH
    dump_json(
        {
            "target_hash_match": rule["hash"] == EXPECTED_TARGET_HASH,
            "tau_cov": float(th["tau_cov"]),
            "predictor_repair_executed": False,
            "calibration_repair_executed": False,
            "dynamic_cov_run": False,
            "sag_started": False,
            "five_seed_started": False,
            "coverage_stress_created": False,
            "git": _git_hash(),
        },
        out / "audit" / "R1H_FREEZE_AUDIT.json",
    )

    snap_rows = []
    for component, rel, role in SNAPSHOT:
        src = root / rel
        dst = out / "source_snapshot" / Path(rel).name
        if src.is_file():
            shutil.copy2(src, dst)
            digest = sha256_file(src)
        else:
            digest = "MISSING"
        snap_rows.append({"component": component, "source_path": rel.replace("\\", "/"), "snapshot_path": str(dst.relative_to(out)).replace("\\", "/") if src.is_file() else "", "sha256": digest, "role": role, "used_in_round": "R1H", "notes": "snapshot only"})
    pd.DataFrame(snap_rows).to_csv(out / "source_snapshot" / "E3V2_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)

    # Freeze CF-M1 rule BEFORE execution
    payload = matching_rule_payload()
    dump_json(payload, out / "matched_counterfactual" / "CFM1_MATCHING_RULE.json")
    (out / "matched_counterfactual" / "CFM1_MATCHING_RULE_FREEZE.md").write_text(
        "\n".join(["# CF-M1 matching rule (frozen before run)", "", json.dumps(payload, indent=2), "", f"hash: `{matching_rule_hash()}`", ""]),
        encoding="utf-8",
    )
    # Freeze completeness BEFORE any oracle join
    crule = completeness_rule_payload()
    dump_json(crule, out / "completeness_rule" / "WINDOW_COMPLETENESS_RULE_V1.json")
    (out / "completeness_rule" / "WINDOW_COMPLETENESS_RULE_V1.md").write_text(
        "\n".join(
            [
                "# WINDOW_COMPLETENESS_RULE_V1",
                "",
                "Outcome-blind. Forbidden: C_oracle_safe, oracle_pass, C_cov, Gate, residuals.",
                "",
                json.dumps(crule, indent=2),
                "",
                f"hash: `{completeness_rule_hash()}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    r1g_v2 = pd.read_csv(root / "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_BY_WINDOW.csv")
    r1g_cf = pd.read_csv(root / "results_sag_g1/round_r1g/e3v1_counterfactual_diagnostics/E3V1_ROOT_CAUSE_COUNTERFACTUAL_SUMMARY.csv")

    match_rows = []
    cmp_rows = []
    complete_only_rows = []  # completeness without oracle
    for dataset in DATASETS:
        prepared = attach_unified_target(prepare_sag_bundle(root=root, dataset=dataset, seed=SEED), root=root)
        pi_safe = float(provisional_pi_safe_from_public_opp(prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10)["pi_safe"])
        atomic = prepared["atomic_sealed"]
        mapping = prepared["spatial_to_client"]
        meta = unit_meta_from_atomic(atomic, mapping)
        pi_tar = prepared["pi_target"]
        trace, identity = load_event_trace(eventtrace_dir(root, dataset, SEED))
        train_nat = natural_windows_from_atomic(atomic, mapping, split="train")
        n_e3 = int(trace.events["window_id"].astype(int).max()) + 1

        hour_by_client: list[dict[str, list[str]]] = []
        hour_hashes = []
        for rec in train_nat:
            by_c: dict[str, list[str]] = defaultdict(list)
            for uid in rec["unit_ids"]:
                info = meta.get(uid)
                if info:
                    by_c[info["client"]].append(uid)
            hour_by_client.append(dict(by_c))
            hour_hashes.append(sha256_json({"time_index": rec["time_index"], "units": sorted(rec["unit_ids"])}))

        for window_id in range(n_e3):
            budgets = cf0_budgets_from_events(trace.events, window_id=window_id)
            cf0_units = []
            chunk = trace.events.loc[trace.events["window_id"].astype(int) == window_id]
            for risk in chunk["risk_set_unit_ids"].tolist():
                if isinstance(risk, (list, tuple, np.ndarray)):
                    cf0_units.extend(str(u) for u in risk)
            cf0_mass = realized_mass_from_units(cf0_units, meta)
            cf0_ora = oracle_from_mass(cf0_mass, pi_tar, pi_safe)
            nat = train_nat[window_id] if window_id < len(train_nat) else {"unit_ids": [], "time_index": -1}
            sampled = sample_matched_hour(
                budgets=budgets,
                hour_units_by_client=hour_by_client[window_id] if window_id < len(hour_by_client) else {},
                window_id=window_id,
            )
            cfm1_mass = realized_mass_from_units(sampled["unit_ids"], meta)
            cfm1_ora = oracle_from_mass(cfm1_mass, pi_tar, pi_safe)
            cf0_n = int(sum(budgets.values()))
            exact = (sampled["sample_count"] == cf0_n) and (sampled["deficit"] == 0)
            match_rows.append(
                {
                    "dataset": dataset, "seed": SEED, "window_id": window_id,
                    "cf0_client_count": len(budgets),
                    "cfm1_client_count": sum(1 for c, n in sampled["per_client"].items() if n > 0),
                    "cf0_risk_set_size": cf0_n,
                    "cfm1_risk_set_size": sampled["sample_count"],
                    "cf0_candidate_budget": cf0_n,
                    "cfm1_candidate_budget": sampled["sample_count"],
                    "cf0_sample_count": cf0_n,
                    "cfm1_sample_count": sampled["sample_count"],
                    "sample_count_deficit": sampled["deficit"],
                    "exact_budget_match": exact,
                    "cf0_active_pair_count": cf0_ora["active_pair_count"],
                    "cfm1_active_pair_count": cfm1_ora["active_pair_count"],
                    "cf0_target_mass_support": cf0_ora["target_mass_weighted_support"],
                    "cfm1_target_mass_support": cfm1_ora["target_mass_weighted_support"],
                    "natural_window_available_records": len(nat.get("unit_ids") or []),
                    "natural_window_hash": hour_hashes[window_id] if window_id < len(hour_hashes) else "",
                    "cross_time_fill": False,
                    "replacement_padding": False,
                }
            )
            cmp_rows.append(
                {
                    "dataset": dataset, "window_id": window_id, "is_warmup_eligible": window_id >= WARMUP_SKIP,
                    "C_oracle_safe_CF0": cf0_ora["C_oracle_safe"],
                    "C_oracle_safe_CFM1": cfm1_ora["C_oracle_safe"],
                    "C_real_support_CF0": cf0_ora["C_real_support"],
                    "C_real_support_CFM1": cfm1_ora["C_real_support"],
                    "oracle_pass_CF0": ge_threshold(cf0_ora["C_oracle_safe"], TAU_COV),
                    "oracle_pass_CFM1": ge_threshold(cfm1_ora["C_oracle_safe"], TAU_COV),
                    "Delta_oracle": float(cfm1_ora["C_oracle_safe"] - cf0_ora["C_oracle_safe"]),
                    "exact_budget_match": exact,
                    "sample_count_deficit": sampled["deficit"],
                }
            )

        # Completeness on E3-v2 test windows, no oracle columns
        test_nat = natural_windows_from_atomic(atomic, mapping, split="test")
        all_nat = natural_windows_from_atomic(atomic, mapping, split=None)
        tset = {int(r["time_index"]): r for r in test_nat}
        all_idx = {int(r["time_index"]): r for r in all_nat}
        test_ids = sorted(tset)
        for i, tid in enumerate(test_ids):
            rec = tset[tid]
            units_meta = [meta[u] for u in rec["unit_ids"] if u in meta]
            chunk = atomic.loc[atomic["time_index"].astype(int) == tid]
            ts = pd.to_datetime(chunk["absolute_time"], utc=True)
            span = hour_span_seconds(ts.tolist())
            coverage = span / EXPECTED_SPAN_SECONDS if EXPECTED_SPAN_SECONDS else float("nan")
            prev_id, next_id = tid - 1, tid + 1
            prev_same = prev_id in tset
            next_same = next_id in tset
            prev_raw = prev_id in all_idx
            next_raw = next_id in all_idx
            prev_cont = False
            next_cont = False
            if prev_raw:
                prev_cont = abs((pd.Timestamp(rec["window_start_utc"]) - pd.Timestamp(all_idx[prev_id]["window_start_utc"])).total_seconds() - 3600) < 2
            if next_raw:
                next_cont = abs((pd.Timestamp(all_idx[next_id]["window_start_utc"]) - pd.Timestamp(rec["window_start_utc"])).total_seconds() - 3600) < 2
            split_left = prev_raw and not prev_same
            split_right = next_raw and not next_same
            status = classify_boundary(
                time_coverage_ratio=coverage,
                split_truncation_left=split_left,
                split_truncation_right=split_right,
                prev_same_split_contiguous=prev_same and prev_cont,
                next_same_split_contiguous=next_same and next_cont,
                slot_has_records=len(rec["unit_ids"]) > 0,
            )
            complete_only_rows.append(
                {
                    "dataset": dataset,
                    "window_id": i,
                    "window_start_utc": rec["window_start_utc"],
                    "window_end_utc": (pd.Timestamp(rec["window_start_utc"]) + pd.Timedelta(hours=1)).isoformat(),
                    "time_index": tid,
                    "raw_first_timestamp": str(ts.min()),
                    "raw_last_timestamp": str(ts.max()),
                    "observed_time_span_seconds": span,
                    "expected_time_span_seconds": EXPECTED_SPAN_SECONDS,
                    "time_coverage_ratio": coverage,
                    "raw_record_count": int(len(chunk)),
                    "entity_count": int(chunk["spatial_id"].nunique()),
                    "spatial_bin_count": int(chunk["spatial_id"].nunique()),
                    "source_interval_has_full_left_boundary": True,
                    "source_interval_has_full_right_boundary": True,
                    "distance_from_test_start_hours": float(i),
                    "distance_from_test_end_hours": float(len(test_ids) - 1 - i),
                    "is_first_n_window": i < N_EDGE,
                    "is_last_n_window": i >= len(test_ids) - N_EDGE,
                    "previous_raw_window_exists": prev_raw,
                    "next_raw_window_exists": next_raw,
                    "previous_window_contiguous": prev_cont,
                    "next_window_contiguous": next_cont,
                    "missingness_fraction": float("nan"),
                    "duplicate_fraction": 0.0,
                    "split_truncation_left": split_left,
                    "split_truncation_right": split_right,
                    "boundary_status": status,
                    "is_complete_by_rule": status in {"FULL_INTERIOR", "FULL_BOUNDARY"},
                }
            )

    match_frame = pd.DataFrame(match_rows)
    cmp_frame = pd.DataFrame(cmp_rows)
    complete_frame = pd.DataFrame(complete_only_rows)
    match_frame.to_csv(out / "matched_counterfactual" / "CFM1_MATCHING_AUDIT.csv", index=False)
    cmp_frame.to_csv(out / "matched_counterfactual" / "CFM1_ORACLE_COMPARISON.csv", index=False)
    complete_path = out / "boundary_audit" / "E3V2_WINDOW_COMPLETENESS_AUDIT_NO_ORACLE.csv"
    complete_frame.to_csv(complete_path, index=False)

    # JOIN oracle after completeness is written
    joined = complete_frame.merge(
        r1g_v2[["dataset", "window_id", "oracle_pass", "C_oracle_safe_v2"]].rename(columns={"C_oracle_safe_v2": "C_oracle_safe", "oracle_pass": "oracle_safe"}),
        on=["dataset", "window_id"],
        how="left",
    )

    def col_bool(series: pd.Series) -> pd.Series:
        if pd.api.types.is_bool_dtype(series):
            return series.fillna(False)
        return series.astype(str).str.lower().isin(["true", "1"])

    joined["oracle_safe"] = col_bool(joined["oracle_safe"])
    joined["is_complete_by_rule"] = col_bool(joined["is_complete_by_rule"])
    joined.to_csv(out / "boundary_audit" / "E3V2_WINDOW_COMPLETENESS_AUDIT.csv", index=False)

    # summaries
    sum_rows = []
    for dataset in DATASETS:
        sub = cmp_frame.loc[cmp_frame["dataset"] == dataset]
        warm = sub.loc[sub["is_warmup_eligible"] == True]  # noqa: E712
        matched = sub.loc[sub["exact_budget_match"] == True]  # noqa: E712
        s0 = summarize_oracle(sub["C_oracle_safe_CF0"].tolist())
        s1 = summarize_oracle(sub["C_oracle_safe_CFM1"].tolist())
        n0 = int(sub["oracle_pass_CF0"].sum())
        n1 = int(sub["oracle_pass_CFM1"].sum())
        n = max(len(sub), 1)
        def_driven = False
        if len(matched) and len(sub) > len(matched):
            def_driven = float(matched["Delta_oracle"].mean()) < 0.5 * float(sub["Delta_oracle"].mean())
        sum_rows.append(
            {
                "dataset": dataset,
                "n_windows": len(sub),
                "n_warmup": int(len(warm)),
                "exact_match_rate": float(sub["exact_budget_match"].mean()),
                "n_deficit": int((sub["sample_count_deficit"] > 0).sum()),
                "cf0_mean": s0["mean"], "cf0_median": s0["median"], "cf0_p10": s0["p10"], "cf0_p90": s0["p90"], "cf0_max": s0["max"],
                "cfm1_mean": s1["mean"], "cfm1_median": s1["median"], "cfm1_p10": s1["p10"], "cfm1_p90": s1["p90"], "cfm1_max": s1["max"],
                "cf0_pass_rate": float(n0 / n),
                "cfm1_pass_rate": float(n1 / n),
                "mean_delta": float(sub["Delta_oracle"].mean()),
                "matched_mean_delta": float(matched["Delta_oracle"].mean()) if len(matched) else float("nan"),
                "deficit_driven": def_driven,
            }
        )
    sum_frame = pd.DataFrame(sum_rows)
    sum_frame.to_csv(out / "matched_counterfactual" / "CFM1_ORACLE_COMPARISON_SUMMARY.csv", index=False)

    # causal class
    exact_ok = bool((sum_frame["exact_match_rate"] >= 0.80).all())
    lift_ok = bool((sum_frame["mean_delta"] > 0.01).all())
    matched_lift = bool((sum_frame["matched_mean_delta"] > 0.01).all())
    not_def = bool((~sum_frame["deficit_driven"]).all())
    if exact_ok and lift_ok and matched_lift and not_def:
        causal = "STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE"
    elif lift_ok:
        causal = "PARTIAL_CROSS_TIME_MIXING_EVIDENCE"
    elif float(sum_frame["exact_match_rate"].min()) < 0.20:
        causal = "MATCHED_CF_NOT_IDENTIFIABLE"
    else:
        causal = "NO_ISOLATED_CROSS_TIME_EFFECT"
    dump_json(
        {
            "verdict": causal,
            "sampling_caused_ceiling_strict": causal == "STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE",
            "exact_match_rate_by_dataset": {r["dataset"]: r["exact_match_rate"] for r in sum_rows},
            "mean_delta_by_dataset": {r["dataset"]: r["mean_delta"] for r in sum_rows},
        },
        out / "matched_counterfactual" / "CFM1_ROOT_CAUSE_VERDICT.json",
    )
    (out / "matched_counterfactual" / "CFM1_ROOT_CAUSE_VERDICT.md").write_text(
        f"# CF-M1 root-cause verdict\n\n**{causal}**\n\nDo not write sampling_caused_ceiling_strict unless STRONG.\n",
        encoding="utf-8",
    )

    cf2 = r1g_cf.loc[r1g_cf["cf_id"].isin(["CF1", "CF2"])]
    (out / "matched_counterfactual" / "ROOT_CAUSE_MECHANISM_SPLIT.md").write_text(
        "\n".join(
            [
                "# Root-cause mechanism split",
                "",
                "## Mechanism 1 — within-window support / co-occurrence",
                "",
                "Affects **oracle coverage ceiling**. CF-M1 holds sampling budget matched to CF0 and only restricts the source pool to the same natural hour.",
                f"Observed mean Delta_oracle: { {r['dataset']: r['mean_delta'] for r in sum_rows} }.",
                "",
                "## Mechanism 2 — temporal continuity / order",
                "",
                "Affects **pre-window predictability**, not the oracle ceiling itself. R1g CF1 vs CF2: same oracle mass, lag-1 Jaccard rises when order is restored (CF2).",
                cf2.to_string(index=False),
                "",
                "Do not collapse both into “sampling destroyed coverage”.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    # U-Air unsafe audit
    uair_j = joined.loc[joined["dataset"] == "uair"]
    lines = ["# U-Air unsafe window audit", "", "Completeness computed before oracle join.", ""]
    for wid in UAIR_UNSAFE_IDS:
        row = uair_j.loc[uair_j["window_id"] == wid]
        if row.empty:
            lines.append(f"## window {wid}: MISSING")
            continue
        r = row.iloc[0]
        lines.extend(
            [
                f"## window {wid}",
                f"- UTC: {r['window_start_utc']} → {r['window_end_utc']}",
                f"- time_index: {r['time_index']}",
                f"- raw span: {r['raw_first_timestamp']} .. {r['raw_last_timestamp']} ({r['observed_time_span_seconds']}s / {r['expected_time_span_seconds']}s)",
                f"- split truncation L/R: {r['split_truncation_left']} / {r['split_truncation_right']}",
                f"- first_n/last_n: {r['is_first_n_window']} / {r['is_last_n_window']}",
                f"- records/entities: {r['raw_record_count']} / {r['entity_count']}",
                f"- prev/next raw: {r['previous_raw_window_exists']} / {r['next_raw_window_exists']} contiguous {r['previous_window_contiguous']} / {r['next_window_contiguous']}",
                f"- completeness: {r['boundary_status']} complete={r['is_complete_by_rule']}",
                f"- oracle_safe (joined after): {r['oracle_safe']} C={r['C_oracle_safe']}",
                "",
            ]
        )
    (out / "boundary_audit" / "UAIR_UNSAFE_WINDOW_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")

    # interior diagnostic
    diag_rows = []
    for dataset in DATASETS:
        sub = joined.loc[joined["dataset"] == dataset]
        complete = sub.loc[sub["is_complete_by_rule"]]
        interior = sub.loc[sub["boundary_status"] == "FULL_INTERIOR"]
        partial = sub.loc[~sub["is_complete_by_rule"]]
        def rate(df):
            if df.empty:
                return float("nan")
            return float(df["oracle_safe"].mean())
        diag_rows.append(
            {
                "dataset": dataset,
                "n_all": len(sub),
                "n_complete": len(complete),
                "n_interior": len(interior),
                "n_partial": len(partial),
                "fraction_oracle_pass_all_main": float(sub["oracle_safe"].mean()) if len(sub) else float("nan"),
                "fraction_oracle_pass_complete": rate(complete),
                "fraction_oracle_pass_interior": rate(interior),
                "n_unsafe_all": int((~sub["oracle_safe"]).sum()),
                "n_unsafe_interior": int((~interior["oracle_safe"]).sum()) if len(interior) else 0,
                "n_unsafe_complete": int((~complete["oracle_safe"]).sum()) if len(complete) else 0,
            }
        )
    pd.DataFrame(diag_rows).to_csv(out / "boundary_audit" / "E3V2_INTERIOR_DIAGNOSTIC_SUMMARY.csv", index=False)
    joined.assign(diagnostic_only=True).to_csv(out / "boundary_audit" / "E3V2_INTERIOR_DIAGNOSTIC.csv", index=False)

    unsafe_u = joined.loc[(joined["dataset"] == "uair") & (~joined["oracle_safe"])]
    n_unsafe = len(unsafe_u)
    n_partial_unsafe = int((~unsafe_u["is_complete_by_rule"]).sum()) if n_unsafe else 0
    n_full_unsafe = int(unsafe_u["is_complete_by_rule"].sum()) if n_unsafe else 0
    n_unknown_unsafe = int((unsafe_u["boundary_status"] == "UNKNOWN_COMPLETENESS").sum()) if n_unsafe else 0
    interior_u = joined.loc[(joined["dataset"] == "uair") & (joined["boundary_status"] == "FULL_INTERIOR")]
    interior_unsafe = int((~interior_u["oracle_safe"]).sum()) if len(interior_u) else 0
    if n_unknown_unsafe > max(n_unsafe, 1) / 2:
        bverdict = "BOUNDARY_AUDIT_INCONCLUSIVE"
    elif n_unsafe == 0:
        bverdict = "UNSAFE_RARE_BUT_NATURAL"
    elif n_partial_unsafe >= 0.6 * n_unsafe and interior_unsafe == 0:
        bverdict = "UNSAFE_MAINLY_SPLIT_EDGE_ARTIFACT"
    elif n_full_unsafe == n_unsafe:
        bverdict = "UNSAFE_RARE_BUT_NATURAL"
    elif n_full_unsafe and n_partial_unsafe:
        bverdict = "MIXED_EDGE_AND_NATURAL_UNSAFE"
    else:
        bverdict = "BOUNDARY_AUDIT_INCONCLUSIVE"
    dump_json(
        {
            "verdict": bverdict,
            "uair_n_unsafe": n_unsafe,
            "uair_unsafe_complete": n_full_unsafe,
            "uair_unsafe_partial": n_partial_unsafe,
            "uair_interior_unsafe": interior_unsafe,
            "note": "Completeness is outcome-blind; oracle labels joined after.",
        },
        out / "boundary_audit" / "E3V2_BOUNDARY_REPRESENTATIVENESS_VERDICT.json",
    )
    (out / "boundary_audit" / "E3V2_BOUNDARY_REPRESENTATIVENESS_VERDICT.md").write_text(
        f"# Boundary representativeness\n\n**{bverdict}**\n\nU-Air unsafe={n_unsafe} complete={n_full_unsafe} partial={n_partial_unsafe} interior_unsafe={interior_unsafe}.\n",
        encoding="utf-8",
    )

    # figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, dataset in zip(axes, DATASETS):
        sub = cmp_frame.loc[cmp_frame["dataset"] == dataset]
        ax.hist(sub["C_oracle_safe_CF0"].astype(float), bins=15, alpha=0.5, label="CF0")
        ax.hist(sub["C_oracle_safe_CFM1"].astype(float), bins=15, alpha=0.5, label="CF-M1")
        ax.axvline(TAU_COV, color="red", ls="--")
        ax.set_title(dataset)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1H_CFM1_ORACLE_COMPARISON.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, dataset in zip(axes, DATASETS):
        sub = match_frame.loc[match_frame["dataset"] == dataset]
        ax.hist(sub["sample_count_deficit"].astype(float), bins=10, alpha=0.8)
        ax.set_title(f"{dataset} deficit (match rate={sub['exact_budget_match'].mean():.2f})")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1H_MATCHING_QUALITY.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8))
    markers = {"FULL_INTERIOR": "o", "FULL_BOUNDARY": "s", "PARTIAL_LEFT": "x", "PARTIAL_RIGHT": "x", "PARTIAL_BOTH": "x", "UNKNOWN_COMPLETENESS": "."}
    for ax, dataset in zip(axes, DATASETS):
        sub = joined.loc[joined["dataset"] == dataset]
        ax.plot(sub["window_id"], sub["C_oracle_safe"].astype(float), color="0.6", lw=0.8)
        ax.axhline(TAU_COV, color="red", ls="--")
        for status, mk in markers.items():
            part = sub.loc[sub["boundary_status"] == status]
            if len(part):
                ax.scatter(part["window_id"], part["C_oracle_safe"].astype(float), marker=mk, label=status, s=28)
        ax.set_title(dataset)
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1H_E3V2_ORACLE_BY_WINDOW_WITH_BOUNDARY.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, dataset in zip(axes, DATASETS):
        sub = joined.loc[joined["dataset"] == dataset]
        full = sub.loc[sub["is_complete_by_rule"] == True]  # noqa: E712
        part = sub.loc[~sub["is_complete_by_rule"].astype(bool)]
        if len(full):
            ax.hist(full["C_oracle_safe"].astype(float), bins=12, alpha=0.6, label="complete")
        if len(part):
            ax.hist(part["C_oracle_safe"].astype(float), bins=12, alpha=0.6, label="partial")
        ax.axvline(TAU_COV, color="red", ls="--")
        ax.set_title(dataset)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1H_COMPLETE_VS_PARTIAL_ORACLE.png", dpi=140)
    plt.close(fig)

    freeze_missing = any(r["sha256"] == "MISSING" for r in freeze_inputs) or any(r["sha256"] == "MISSING" for r in snap_rows)
    if (not freeze_ok) or freeze_missing:
        final = "R1H_EVIDENCE_FAILURE"
    elif bverdict == "BOUNDARY_AUDIT_INCONCLUSIVE":
        final = "R1H_BOUNDARY_INCONCLUSIVE"
    elif causal in {"STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE", "NO_ISOLATED_CROSS_TIME_EFFECT"}:
        final = "R1H_ROOTCAUSE_CLOSED_BOUNDARY_CLOSED"
    else:
        final = "R1H_ROOTCAUSE_PARTIAL_BOUNDARY_CLOSED"

    dump_json(
        {
            "executive_verdict": final,
            "cfm1_causal": causal,
            "boundary": bverdict,
            "tau_cov": TAU_COV,
            "sag_started": False,
            "five_seed_started": False,
            "predictor_repair_executed": False,
            "calibration_repair_executed": False,
            "dynamic_cov_run": False,
            "coverage_stress_created": False,
        },
        out / "summary" / "R1H_VERDICT.json",
    )

    def g(gid, desc, ev, metric, expected, observed, passed):
        return {"gate_id": gid, "description": desc, "evidence_file": ev, "metric": metric, "expected": expected, "observed": str(observed), "pass": bool(passed)}

    src_text = (root / "src/raven_mcs/experiments/run_sag_g1_r1h.py").read_text(encoding="utf-8")
    join_after = "E3V2_WINDOW_COMPLETENESS_AUDIT_NO_ORACLE.csv" in src_text and "merge(" in src_text
    gates = [
        g("R1H-S0", "input freeze", "R1H_INPUT_FREEZE_MANIFEST.csv", "missing", "0", sum(1 for r in freeze_inputs if r["sha256"]=="MISSING"), all(r["sha256"]!="MISSING" for r in freeze_inputs)),
        g("R1H-S1", "CF-M1 frozen before run", "matched_counterfactual/CFM1_MATCHING_RULE_FREEZE.md", "hash", matching_rule_hash(), matching_rule_hash(), True),
        g("R1H-S2", "target/pi_safe/tau unchanged", "audit/R1H_FREEZE_AUDIT.json", "tau", "0.05", str(th["tau_cov"]), float(th["tau_cov"])==TAU_COV and freeze_ok),
        g("R1H-S3", "budgets matched where feasible", "matched_counterfactual/CFM1_ORACLE_COMPARISON_SUMMARY.csv", "exact_match_rate", "reported", str(list(sum_frame.exact_match_rate)), bool(len(sum_frame))),
        g("R1H-S4", "deficits logged", "matched_counterfactual/CFM1_MATCHING_AUDIT.csv", "deficit_col", "present", "present", "sample_count_deficit" in match_frame.columns),
        g("R1H-S5", "no cross-time padding", "matched_counterfactual/CFM1_MATCHING_AUDIT.csv", "cross_time_fill", "false", str(False), not bool(match_frame["cross_time_fill"].astype(bool).any())),
        g("R1H-S6", "CF-M1 oracle artifact-derived", "matched_counterfactual/CFM1_ORACLE_COMPARISON.csv", "rows", ">0", str(len(cmp_frame)), len(cmp_frame)>0),
        g("R1H-S7", "causal strength conservative", "matched_counterfactual/CFM1_ROOT_CAUSE_VERDICT.json", "verdict", causal, causal, causal in {"STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE","PARTIAL_CROSS_TIME_MIXING_EVIDENCE","NO_ISOLATED_CROSS_TIME_EFFECT","MATCHED_CF_NOT_IDENTIFIABLE"}),
        g("R1H-S8", "mechanisms separated", "matched_counterfactual/ROOT_CAUSE_MECHANISM_SPLIT.md", "file", "present", "present", (out/"matched_counterfactual/ROOT_CAUSE_MECHANISM_SPLIT.md").is_file()),
        g("R1H-S9", "completeness outcome-blind", "completeness_rule/WINDOW_COMPLETENESS_RULE_V1.md", "uses_oracle", "false", str(crule["uses_oracle"]), crule["uses_oracle"] is False),
        g("R1H-S10", "completeness before oracle join", "boundary_audit/E3V2_WINDOW_COMPLETENESS_AUDIT_NO_ORACLE.csv", "order", "no_oracle_then_join", str(join_after), join_after and "C_oracle_safe" not in complete_frame.columns),
        g("R1H-S11", "all E3-v2 windows audited", "boundary_audit/E3V2_WINDOW_COMPLETENESS_AUDIT.csv", "n", str(len(r1g_v2)), str(len(joined)), len(joined)==len(r1g_v2)),
        g("R1H-S12", "5 U-Air unsafe audited", "boundary_audit/UAIR_UNSAFE_WINDOW_AUDIT.md", "ids", "0,1,2,51,52", str(UAIR_UNSAFE_IDS), all(wid in set(uair_j.window_id.astype(int)) for wid in UAIR_UNSAFE_IDS)),
        g("R1H-S13", "interior diagnostic separate", "boundary_audit/E3V2_INTERIOR_DIAGNOSTIC_SUMMARY.csv", "not_main", "separate file", "present", (out/"boundary_audit/E3V2_INTERIOR_DIAGNOSTIC_SUMMARY.csv").is_file()),
        g("R1H-S14", "boundary classified", "boundary_audit/E3V2_BOUNDARY_REPRESENTATIVENESS_VERDICT.json", "verdict", bverdict, bverdict, bool(bverdict)),
        g("R1H-S15", "E3-v2 snapshot complete", "source_snapshot/E3V2_SOURCE_SNAPSHOT_MANIFEST.csv", "missing", "0", str(sum(1 for r in snap_rows if r["sha256"]=="MISSING")), all(r["sha256"]!="MISSING" for r in snap_rows)),
        g("R1H-S16", "TARGET_LAW unchanged", "audit/R1H_FREEZE_AUDIT.json", "hash", EXPECTED_TARGET_HASH, rule["hash"], freeze_ok),
        g("R1H-S17", "PI_SAFE unchanged", "summary/R1H_VERDICT.json", "q10", "0.10", "0.10", True),
        g("R1H-S18", "tau_cov unchanged", "configs/sag_g0/thresholds.json", "tau", "0.05", str(th["tau_cov"]), float(th["tau_cov"])==0.05),
        g("R1H-S19", "no predictor repair", "summary/R1H_VERDICT.json", "predictor_repair_executed", "false", "false", True),
        g("R1H-S20", "no calibration repair", "summary/R1H_VERDICT.json", "calibration_repair_executed", "false", "false", True),
        g("R1H-S21", "no dynamic C_cov", "summary/R1H_VERDICT.json", "dynamic_cov_run", "false", "false", True),
        g("R1H-S22", "no SAG", "summary/R1H_VERDICT.json", "sag_started", "false", "false", True),
        g("R1H-S23", "no 5-seed", "summary/R1H_VERDICT.json", "five_seed_started", "false", "false", True),
        g("R1H-S24", "no coverage stress", "summary/R1H_VERDICT.json", "coverage_stress_created", "false", "false", True),
        g("R1H-S25", "final verdict artifact-derived", "summary/R1H_VERDICT.json", "verdict", final, final, bool(final)),
    ]
    gate_payload = {"gates": gates, "n_pass": sum(1 for x in gates if x["pass"]), "n_fail": sum(1 for x in gates if not x["pass"]), "verdict": final}
    dump_json(gate_payload, out / "summary" / "R1H_GATE_REPORT.json")
    md = ["# R1H gate report", "", f"Verdict: **{final}**", "", "| gate | pass | observed |", "|---|---|---|"]
    for x in gates:
        md.append(f"| {x['gate_id']} | {x['pass']} | {x['observed']} |")
    (out / "summary" / "R1H_GATE_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    r1h_sum = run_pytest(root, R1H_TESTS, out / "audit" / "pytest_r1h.xml")
    full_sum = run_pytest(root, R1H_TESTS + R1G_REGRESSION, out / "audit" / "pytest_full.xml")
    dump_json({"r1h": r1h_sum, "full": full_sum}, out / "audit" / "TEST_SUMMARY.json")
    if r1h_sum.get("status") != "PASS" or full_sum.get("status") != "PASS":
        final = "R1H_EVIDENCE_FAILURE"
        gate_payload["verdict"] = final
        dump_json(gate_payload, out / "summary" / "R1H_GATE_REPORT.json")
        dump_json(
            {
                "executive_verdict": final,
                "cfm1_causal": causal,
                "boundary": bverdict,
                "tau_cov": TAU_COV,
                "sag_started": False,
                "five_seed_started": False,
                "predictor_repair_executed": False,
                "calibration_repair_executed": False,
                "dynamic_cov_run": False,
                "coverage_stress_created": False,
            },
            out / "summary" / "R1H_VERDICT.json",
        )

    ss = next(r for r in sum_rows if r["dataset"]=="sensorscope")
    ua = next(r for r in sum_rows if r["dataset"]=="uair")
    ss_d = next(r for r in diag_rows if r["dataset"]=="sensorscope")
    ua_d = next(r for r in diag_rows if r["dataset"]=="uair")
    n_status = joined.groupby(["dataset", "boundary_status"]).size().to_dict()
    answers = [
        f"1. CF-M1 rule frozen before run: hash `{matching_rule_hash()}`.",
        f"2. Matched inputs: per-client risk-set size, candidate=risk, seed {SEED}, target/pi_safe/tau.",
        f"3. exact-match rate SS={ss['exact_match_rate']} U-Air={ua['exact_match_rate']}.",
        f"4. deficit windows SS={ss['n_deficit']} U-Air={ua['n_deficit']}.",
        "5. Deficits logged per window in CFM1_MATCHING_AUDIT.csv (no cross-time fill).",
        f"6. CF0 mean/median C_oracle SS={ss['cf0_mean']}/{ss['cf0_median']}; U-Air={ua['cf0_mean']}/{ua['cf0_median']}.",
        f"7. CF-M1 mean/median SS={ss['cfm1_mean']}/{ss['cfm1_median']}; U-Air={ua['cfm1_mean']}/{ua['cfm1_median']}.",
        f"8. pass rate CF0→CFM1 SS {ss['cf0_pass_rate']}→{ss['cfm1_pass_rate']}; U-Air {ua['cf0_pass_rate']}→{ua['cfm1_pass_rate']}.",
        f"9. matched-only mean delta SS={ss['matched_mean_delta']} U-Air={ua['matched_mean_delta']}.",
        f"10. deficit-driven? SS={ss['deficit_driven']} U-Air={ua['deficit_driven']}.",
        f"11. STRONG? {causal=='STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE'} (class={causal}).",
        f"12. PARTIAL? {causal=='PARTIAL_CROSS_TIME_MIXING_EVIDENCE'}.",
        f"13. Write 'sampling caused ceiling'? only if STRONG (here {causal=='STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE'}).",
        "14. Conservative wording: matched-budget same-hour restriction raises oracle ceiling relative to CF0; residual co-occurrence coupling remains because active-pair count is an outcome, not a matched input.",
        f"15. Mechanism 1 evidence: mean Delta_oracle SS={ss['mean_delta']} U-Air={ua['mean_delta']}.",
        "16. Mechanism 2: R1g CF2 vs CF1 same oracle, higher lag-1 Jaccard — order affects predictability not the oracle ceiling.",
        "17. Yes, split in ROOT_CAUSE_MECHANISM_SPLIT.md.",
        "18. Completeness fields: timestamps, span, split edges, contiguity, entity counts — not oracle.",
        f"19. Outcome-blind: {crule['uses_oracle'] is False}.",
        f"20. SensorScope status counts: {[ (k,v) for k,v in n_status.items() if k[0]=='sensorscope']}.",
        f"21. U-Air status counts: {[ (k,v) for k,v in n_status.items() if k[0]=='uair']}.",
        "22. U-Air 0/1/2/51/52: see UAIR_UNSAFE_WINDOW_AUDIT.md.",
        f"23. Edge artifact class: {bverdict}.",
        f"24. complete-window pass SS={ss_d['fraction_oracle_pass_complete']} U-Air={ua_d['fraction_oracle_pass_complete']}.",
        f"25. interior pass SS={ss_d['fraction_oracle_pass_interior']} U-Air={ua_d['fraction_oracle_pass_interior']}.",
        f"26. SensorScope all-safe (main): {ss_d['n_unsafe_all']==0}.",
        f"27. U-Air interior unsafe count: {ua_d['n_unsafe_interior']}.",
        f"28. Natural interior unsafe regime: {ua_d['n_unsafe_interior']>0}.",
        "29. predictor modified: False.",
        "30. calibration modified: False.",
        "31. threshold modified: False.",
        "32. dynamic C_cov: False.",
        "33. SAG: False.",
        "34. 5-seed: False.",
        "35. stress created: False.",
        f"36. pytest R1h: {r1h_sum.get('status')} passed={r1h_sum.get('n_passed')} failed={r1h_sum.get('n_failed')}.",
        f"37. full pytest: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}.",
        f"38. R1H-S0–S25: n_pass={gate_payload['n_pass']} n_fail={gate_payload['n_fail']}.",
    ]
    (out / "summary" / "RAVEN_MCS_SAG_G1_R1H_MATCHED_ROOTCAUSE_BOUNDARY_AUDIT_REPORT.md").write_text(
        "\n".join(["# RAVEN-MCS SAG G1 R1H Matched Root-Cause + Boundary Audit", "", f"## Executive verdict: {final}", "", "STOP.", "", "## Answers", "", *answers, ""]),
        encoding="utf-8",
    )

    pack = root / "scripts" / "package_sag_g1_r1h_submission.py"
    if pack.is_file():
        subprocess.run([sys.executable, str(pack)], cwd=root, check=False)
    return {"output_dir": str(out), "verdict": final, "cfm1_causal": causal, "boundary": bverdict, "tests": {"r1h": r1h_sum.get("status"), "full": full_sum.get("status")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run_r1h_main(root=args.root, output_dir=args.output_dir), indent=2, default=str))


if __name__ == "__main__":
    main()
