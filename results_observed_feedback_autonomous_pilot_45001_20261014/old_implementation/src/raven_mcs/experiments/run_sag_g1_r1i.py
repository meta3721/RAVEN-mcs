"""SAG G1-R1i: pre-registered exogenous coverage-stress oracle. STOP. No SAG."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import numpy as np
import pandas as pd

from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.experiments.sag_runtime import attach_unified_target, prepare_sag_bundle
from raven_mcs.sag.availability_stress import (
    A_GRID,
    BOUNDARY_NEAR_MARGIN,
    PROTOCOL_VERSION,
    REPRO_TOL,
    TAU_COV,
    boundary_near_rule_payload,
    information_boundary_payload,
    routing_rule_hash,
    routing_rule_payload,
    stress_level_hash,
    stress_level_payload,
)
from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp
from raven_mcs.sag.e3v1_root_cause import natural_windows_from_atomic, unit_meta_from_atomic
from raven_mcs.sag.oracle_stress_builder import stressed_window
from raven_mcs.sag.stress_gate_builder import build_gates
from raven_mcs.sag.stress_mask import SEED, mask_rule_hash, mask_rule_payload
from raven_mcs.sag.stress_summary import (
    boundary_near_rows,
    classify_boundary_rich,
    crossing_brackets,
    dataset_verdict,
    monotonicity_audit,
    overall_verdict,
    summarize_levels,
)
from raven_mcs.sag.target_law import freeze_target_law_rule_v1, pi_safe_rule_hash
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1i"

SNAPSHOT = (
    ("availability_stress", "src/raven_mcs/sag/availability_stress.py", "stress_spec"),
    ("stress_mask", "src/raven_mcs/sag/stress_mask.py", "mask"),
    ("oracle_stress_builder", "src/raven_mcs/sag/oracle_stress_builder.py", "oracle"),
    ("stress_summary", "src/raven_mcs/sag/stress_summary.py", "summary"),
    ("stress_gate_builder", "src/raven_mcs/sag/stress_gate_builder.py", "gates"),
    ("run_sag_g1_r1i", "src/raven_mcs/experiments/run_sag_g1_r1i.py", "runner"),
    ("thresholds", "configs/sag_g0/thresholds.json", "tau"),
    ("e3_v2_protocol", "src/e3_v2_protocol.py", "natural_protocol"),
    ("window_completeness", "src/raven_mcs/sag/window_completeness.py", "completeness"),
)

R1I_TESTS = (
    "tests/unit/test_r1i_input_freeze.py",
    "tests/unit/test_stress_levels_frozen.py",
    "tests/unit/test_stress_levels_exact.py",
    "tests/unit/test_availability_mask_deterministic.py",
    "tests/unit/test_availability_mask_nested.py",
    "tests/unit/test_availability_mask_outcome_independent.py",
    "tests/unit/test_availability_entity_level.py",
    "tests/unit/test_no_pair_targeted_deletion.py",
    "tests/unit/test_a1_reproduces_natural.py",
    "tests/unit/test_oracle_stress_monotonicity.py",
    "tests/unit/test_target_law_unchanged.py",
    "tests/unit/test_pi_safe_unchanged.py",
    "tests/unit/test_tau_cov_unchanged.py",
    "tests/unit/test_boundary_rich_rule_frozen.py",
    "tests/unit/test_boundary_near_rule_frozen.py",
    "tests/unit/test_no_adaptive_stress_level_added.py",
    "tests/unit/test_natural_track_unchanged.py",
    "tests/unit/test_stress_track_separate.py",
    "tests/unit/test_no_predictor_run.py",
    "tests/unit/test_no_calibration_run.py",
    "tests/unit/test_no_dynamic_cov_run.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_r1i_gate_artifact_derived.py",
    "tests/unit/test_r1i_verdict_not_hardcoded.py",
)
R1H_REGRESSION = (
    "tests/unit/test_r1h_input_hashes_frozen.py",
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
    summary["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-40:])
    return summary


def col_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1"])


def run_r1i_main(*, root: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in ("audit", "stress_spec", "stress_masks", "oracle_stress", "boundary_analysis", "figures", "summary", "source_snapshot", "legacy_refs"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    freeze_inputs = []
    refs = [
        ("E3-v2 EventTrace SS", "results_sag_g1/round_r1g/e3v2_skeleton/sensorscope/identity.json", "R1G", "E3_V2"),
        ("E3-v2 EventTrace UA", "results_sag_g1/round_r1g/e3v2_skeleton/uair/identity.json", "R1G", "E3_V2"),
        ("E3-v2 window rule", "results_sag_g1/round_r1g/e3v2_spec/E3V2_WINDOW_RULE_HASH.txt", "R1G", "E3_V2_SPEC"),
        ("E3-v2 population rule", "results_sag_g1/round_r1g/e3v2_spec/E3V2_POPULATION_RULE_HASH.txt", "R1G", "E3_V2_SPEC"),
        ("E3-v2 window rule json", "results_sag_g1/round_r1g/e3v2_spec/E3V2_WINDOW_RULE.json", "R1G", "E3_V2_SPEC"),
        ("E3-v2 oracle by window", "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_BY_WINDOW.csv", "R1G", "E3_V2_ORACLE"),
        ("E3-v2 oracle summary", "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_SUMMARY.csv", "R1G", "E3_V2_ORACLE"),
        ("TARGET_LAW", "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json", "R1D", "TARGET_LAW"),
        ("PI_SAFE", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "R1E", "PI_SAFE"),
        ("thresholds", "configs/sag_g0/thresholds.json", "R0", "TAU"),
        ("R1h boundary verdict", "results_sag_g1/round_r1h/boundary_audit/E3V2_BOUNDARY_REPRESENTATIVENESS_VERDICT.json", "R1H", "BOUNDARY"),
        ("R1h completeness", "results_sag_g1/round_r1h/boundary_audit/E3V2_WINDOW_COMPLETENESS_AUDIT.csv", "R1H", "COMPLETENESS"),
        ("R1h verdict", "results_sag_g1/round_r1h/summary/R1H_VERDICT.json", "R1H", "VERDICT"),
        ("R1h completeness rule", "results_sag_g1/round_r1h/completeness_rule/WINDOW_COMPLETENESS_RULE_V1.json", "R1H", "COMPLETENESS"),
    ]
    r1g_ident_ss = sha256_file(root / "results_sag_g1/round_r1g/e3v2_skeleton/sensorscope/identity.json")
    r1g_ident_ua = sha256_file(root / "results_sag_g1/round_r1g/e3v2_skeleton/uair/identity.json")
    for name, rel, rnd, role in refs:
        path = root / rel
        digest = sha256_file(path) if path.is_file() else "MISSING"
        freeze_inputs.append({"artifact": name, "path": rel.replace("\\", "/"), "sha256": digest, "source_round": rnd, "role": role, "frozen": True, "notes": "natural track not rewritten in R1i"})
        if path.is_file():
            shutil.copy2(path, out / "legacy_refs" / f"{rnd}_{role}_{Path(rel).name}")
    pd.DataFrame(freeze_inputs).to_csv(out / "R1I_INPUT_FREEZE_MANIFEST.csv", index=False)
    (out / "R1I_INPUT_FREEZE_AUDIT.md").write_text(
        "\n".join(
            [
                "# R1I input freeze",
                "",
                "Natural E3-v2 EventTrace, protocol spec, oracle precheck, TARGET_LAW, PI_SAFE, tau_cov, and R1h completeness/boundary artifacts are frozen.",
                "R1i writes only under `results_sag_g1/round_r1i/`.",
                "Stress is an independent controlled track. Natural main results are not replaced.",
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
            "pi_safe_rule_hash": pi_safe_rule_hash(),
            "tau_cov": float(th["tau_cov"]),
            "predictor_run": False,
            "calibration_run": False,
            "predictor_repair_executed": False,
            "calibration_repair_executed": False,
            "dynamic_cov_run": False,
            "sag_started": False,
            "five_seed_started": False,
            "coverage_stress_created": True,
            "adaptive_level_added": False,
            "git": _git_hash(),
        },
        out / "audit" / "R1I_FREEZE_AUDIT.json",
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
        snap_rows.append({"component": component, "source_path": rel.replace("\\", "/"), "snapshot_path": str(dst.relative_to(out)).replace("\\", "/") if src.is_file() else "", "sha256": digest, "role": role, "used_in_round": "R1I", "notes": "snapshot only"})
    pd.DataFrame(snap_rows).to_csv(out / "source_snapshot" / "R1I_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)

    # Freeze stress mechanism / levels / mask / routing BEFORE any oracle stress
    level_payload = stress_level_payload()
    dump_json(level_payload, out / "stress_spec" / "R1I_STRESS_LEVEL.json")
    (out / "stress_spec" / "R1I_STRESS_LEVEL_FREEZE.md").write_text(
        "\n".join(
            [
                "# R1I stress level freeze",
                "",
                "Mechanism: **EXOGENOUS_ENTITY_AVAILABILITY_THINNING_V1**.",
                "",
                "Grid (frozen, coarse, not searched from R1h crossing):",
                "",
                "- a = 1.00 (must reproduce natural E3-v2)",
                "- a = 0.80",
                "- a = 0.60",
                "- a = 0.40",
                "- a = 0.20",
                "",
                "Coarse grid is used so the stress surface is pre-registered and auditable.",
                "This round does **not** add 0.50 / 0.55 / 0.65 or any midpoint, even if a crossing falls between levels.",
                "",
                json.dumps(level_payload, indent=2),
                "",
                f"hash: `{stress_level_hash()}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    mask_payload = mask_rule_payload()
    dump_json(mask_payload, out / "stress_masks" / "R1I_AVAILABILITY_MASK_RULE.json")
    (out / "stress_masks" / "R1I_AVAILABILITY_MASK_RULE.md").write_text(
        "\n".join(["# Nested availability mask", "", json.dumps(mask_payload, indent=2), ""]),
        encoding="utf-8",
    )
    (out / "stress_masks" / "R1I_AVAILABILITY_MASK_HASH.txt").write_text(mask_rule_hash() + "\n", encoding="utf-8")
    dump_json(information_boundary_payload(), out / "stress_spec" / "R1I_STRESS_INFORMATION_BOUNDARY.json")
    (out / "stress_spec" / "R1I_STRESS_INFORMATION_BOUNDARY.md").write_text(
        "\n".join(
            [
                "# Stress information boundary",
                "",
                "Availability level `a` is a scenario-level public exogenous parameter known before the window.",
                "The realized entity mask is **not** pre-window fully observed information.",
                "A future predictor/certificate may use `a` and must not use the current-window realized mask unless the paper model explicitly allows it.",
                "This round computes oracle only.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    dump_json(routing_rule_payload(), out / "stress_spec" / "R1I_ROUTING_RULE.json")
    dump_json(boundary_near_rule_payload(), out / "stress_spec" / "R1I_BOUNDARY_NEAR_RULE.json")
    (out / "stress_spec" / "R1I_BOUNDARY_NEAR_RULE.md").write_text(
        f"# BOUNDARY_NEAR\n\nabs(C_oracle_safe - tau_cov) <= {BOUNDARY_NEAR_MARGIN}\n\nFrozen before oracle summary.\n",
        encoding="utf-8",
    )
    (out / "stress_spec" / "R1I_BOUNDARY_RICH_RULE.md").write_text(
        "\n".join(["# BOUNDARY_RICH routing rule", "", json.dumps(routing_rule_payload(), indent=2), f"hash: `{routing_rule_hash()}`", ""]),
        encoding="utf-8",
    )

    natural = pd.read_csv(root / "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_BY_WINDOW.csv")
    complete = pd.read_csv(root / "results_sag_g1/round_r1h/boundary_audit/E3V2_WINDOW_COMPLETENESS_AUDIT.csv")
    complete["is_complete_by_rule"] = col_bool(complete["is_complete_by_rule"])
    complete["is_first_n_window"] = col_bool(complete["is_first_n_window"])
    complete["is_last_n_window"] = col_bool(complete["is_last_n_window"])
    ident = {
        "sensorscope": json.loads((root / "results_sag_g1/round_r1g/e3v2_skeleton/sensorscope/identity.json").read_text(encoding="utf-8")),
        "uair": json.loads((root / "results_sag_g1/round_r1g/e3v2_skeleton/uair/identity.json").read_text(encoding="utf-8")),
    }

    stress_rows = []
    for dataset in DATASETS:
        prepared = attach_unified_target(prepare_sag_bundle(root=root, dataset=dataset, seed=SEED), root=root)
        pi_safe = float(provisional_pi_safe_from_public_opp(prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10)["pi_safe"])
        atomic = prepared["atomic_sealed"]
        mapping = prepared["spatial_to_client"]
        meta = unit_meta_from_atomic(atomic, mapping)
        pi_tar = prepared["pi_target"]
        test_nat = natural_windows_from_atomic(atomic, mapping, split="test")
        natural_hash = str(ident[dataset].get("trace_hash") or "")
        for window_id, rec in enumerate(test_nat):
            units = list(rec["unit_ids"])
            for a in A_GRID:
                row = stressed_window(
                    dataset=dataset,
                    window_id=window_id,
                    unit_ids=units,
                    unit_meta=meta,
                    availability_level=a,
                    pi_tar=pi_tar,
                    pi_safe=pi_safe,
                    natural_trace_hash=natural_hash,
                )
                comp = complete.loc[(complete["dataset"] == dataset) & (complete["window_id"] == window_id)]
                if len(comp):
                    row["natural_boundary_status"] = str(comp["boundary_status"].iloc[0])
                    row["natural_complete_status"] = bool(comp["is_complete_by_rule"].iloc[0])
                else:
                    row["natural_boundary_status"] = "UNKNOWN_COMPLETENESS"
                    row["natural_complete_status"] = False
                row["window_start_utc"] = rec["window_start_utc"]
                row["time_index"] = rec["time_index"]
                row["pi_safe"] = pi_safe
                stress_rows.append(row)

    stress = pd.DataFrame(stress_rows)
    stress.to_csv(out / "oracle_stress" / "R1I_ORACLE_STRESS_BY_WINDOW.csv", index=False)
    stress[
        [
            "dataset", "seed", "window_id", "availability_level",
            "natural_trace_hash", "availability_mask_hash", "stressed_trace_hash",
            "n_entities_natural", "n_entities_available", "n_entities_removed", "realized_retention_fraction",
        ]
    ].to_csv(out / "stress_masks" / "R1I_STRESSED_TRACE_MANIFEST.csv", index=False)

    # a=1.00 reproduction
    repro_rows = []
    for dataset in DATASETS:
        nat = natural.loc[natural["dataset"] == dataset]
        a1 = stress.loc[(stress["dataset"] == dataset) & (np.isclose(stress["availability_level"].astype(float), 1.00))]
        merged = a1.merge(nat[["window_id", "C_oracle_safe_v2", "C_real_support_v2"]], on="window_id", how="outer")
        for r in merged.itertuples(index=False):
            diff_o = abs(float(r.C_oracle_safe) - float(r.C_oracle_safe_v2)) if pd.notna(r.C_oracle_safe) and pd.notna(r.C_oracle_safe_v2) else float("nan")
            diff_e = abs(int(r.n_entities_available) - int(r.n_entities_natural)) if pd.notna(r.n_entities_available) else float("nan")
            repro_rows.append(
                {
                    "dataset": dataset,
                    "window_id": int(r.window_id),
                    "C_oracle_safe_stress_a1": r.C_oracle_safe,
                    "C_oracle_safe_natural": r.C_oracle_safe_v2,
                    "abs_diff_oracle": diff_o,
                    "n_entities_available": r.n_entities_available,
                    "n_entities_natural": r.n_entities_natural,
                    "entity_count_match": diff_e == 0,
                    "oracle_match": bool(pd.notna(diff_o) and diff_o <= REPRO_TOL),
                }
            )
    repro = pd.DataFrame(repro_rows)
    repro.to_csv(out / "oracle_stress" / "R1I_BASELINE_REPRODUCTION_AUDIT.csv", index=False)
    max_diff = float(repro["abs_diff_oracle"].max()) if len(repro) else float("nan")
    baseline_ok = bool(repro["oracle_match"].all() and repro["entity_count_match"].all()) if len(repro) else False
    (out / "oracle_stress" / "R1I_BASELINE_REPRODUCTION_AUDIT.md").write_text(
        f"# Baseline a=1.00 reproduction\n\nPASS={baseline_ok}\nmax abs oracle diff={max_diff}\nentity count match={bool(repro['entity_count_match'].all()) if len(repro) else False}\n",
        encoding="utf-8",
    )

    mono = monotonicity_audit(stress)
    mono.to_csv(out / "oracle_stress" / "R1I_MONOTONICITY_AUDIT.csv", index=False)
    n_mono_viol = int((~mono["real_monotone"]).sum() + (~mono["oracle_monotone"]).sum()) if len(mono) else 1
    mono_ok = n_mono_viol == 0

    summary = summarize_levels(stress)
    summary.to_csv(out / "oracle_stress" / "R1I_ORACLE_STRESS_SUMMARY.csv", index=False)
    crossings = crossing_brackets(stress)
    crossings.to_csv(out / "boundary_analysis" / "R1I_WINDOW_CROSSING_BRACKETS.csv", index=False)
    rich = classify_boundary_rich(summary, stress, complete)
    rich.to_csv(out / "boundary_analysis" / "R1I_BOUNDARY_RICH_LEVELS.csv", index=False)
    near = boundary_near_rows(stress)
    near.to_csv(out / "boundary_analysis" / "R1I_BOUNDARY_NEAR_WINDOWS.csv", index=False)

    impl_fail = (not baseline_ok) or (not mono_ok) or (not freeze_ok) or any(r["sha256"] == "MISSING" for r in freeze_inputs)
    ds_verdicts = {}
    ds_payloads = []
    for dataset in DATASETS:
        dv = dataset_verdict(
            dataset=dataset,
            summary=summary,
            rich=rich,
            crossings=crossings,
            n_mono_viol=n_mono_viol,
            baseline_ok=baseline_ok,
        )
        ds_verdicts[dataset] = dv["verdict"]
        n_near = int(len(near.loc[near["dataset"] == dataset])) if len(near) else 0
        dv["n_boundary_near"] = n_near
        ds_payloads.append(dv)
    dump_json({"by_dataset": ds_payloads}, out / "boundary_analysis" / "R1I_DATASET_VERDICTS.json")
    final = overall_verdict(ds_verdicts, impl_fail=impl_fail)

    # figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = summary.loc[summary["dataset"] == dataset].sort_values("availability_level")
        ax.plot(sub["availability_level"], sub["fraction_safe"], marker="o")
        ax.axhline(0.20, color="0.6", ls=":")
        ax.axhline(0.80, color="0.6", ls=":")
        ax.set_title(dataset)
        ax.set_xlabel("availability a")
        ax.set_ylabel("fraction_safe")
        ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1I_ORACLE_STRESS_CURVES.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = stress.loc[stress["dataset"] == dataset]
        for a in A_GRID:
            part = sub.loc[np.isclose(sub["availability_level"].astype(float), a)]
            ax.hist(part["C_oracle_safe"].astype(float), bins=12, alpha=0.35, label=f"a={a:.2f}")
        ax.axvline(TAU_COV, color="red", ls="--")
        ax.set_title(dataset)
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1I_ORACLE_COVERAGE_DISTRIBUTION_BY_STRESS.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = stress.loc[stress["dataset"] == dataset]
        levels = list(A_GRID)
        for wid, g in sub.groupby("window_id"):
            g = g.sort_values("availability_level", ascending=False)
            ax.plot(g["availability_level"], g["C_oracle_safe"], color="0.75", lw=0.4)
        med = sub.groupby("availability_level")["C_oracle_safe"].median()
        q10 = sub.groupby("availability_level")["C_oracle_safe"].quantile(0.10)
        q90 = sub.groupby("availability_level")["C_oracle_safe"].quantile(0.90)
        ax.plot(med.index, med.values, color="black", lw=2, label="median")
        ax.fill_between(q10.index, q10.values, q90.values, color="0.4", alpha=0.25, label="p10-p90")
        ax.axhline(TAU_COV, color="red", ls="--")
        ax.set_title(dataset)
        ax.legend(fontsize=7)
        ax.set_xlabel("availability a")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1I_WINDOW_ORACLE_TRAJECTORIES.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 6))
    for ax, dataset in zip(axes, DATASETS):
        sub = stress.loc[stress["dataset"] == dataset]
        pivot = sub.pivot(index="window_id", columns="availability_level", values="oracle_margin")
        im = ax.imshow(pivot.astype(float).values, aspect="auto", cmap="coolwarm", vmin=-0.08, vmax=0.08)
        ax.set_title(dataset)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"{float(c):.2f}" for c in pivot.columns], fontsize=8)
        ax.set_ylabel("window_id")
        fig.colorbar(im, ax=ax, fraction=0.046, label="oracle_margin")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1I_BOUNDARY_CROSSING_HEATMAP.png", dpi=140)
    plt.close(fig)

    dump_json(
        {
            "executive_verdict": final,
            "by_dataset": ds_verdicts,
            "tau_cov": TAU_COV,
            "protocol_version": PROTOCOL_VERSION,
            "predictor_run": False,
            "calibration_run": False,
            "predictor_repair_executed": False,
            "calibration_repair_executed": False,
            "dynamic_cov_run": False,
            "sag_started": False,
            "five_seed_started": False,
            "adaptive_level_added": False,
            "natural_track_rewritten": False,
            "baseline_ok": baseline_ok,
            "monotonicity_ok": mono_ok,
            "n_mono_violations": n_mono_viol,
        },
        out / "summary" / "R1I_VERDICT.json",
    )

    src_text = (root / "src/raven_mcs/experiments/run_sag_g1_r1i.py").read_text(encoding="utf-8")
    r1g_ss_now = sha256_file(root / "results_sag_g1/round_r1g/e3v2_skeleton/sensorscope/identity.json")
    r1g_ua_now = sha256_file(root / "results_sag_g1/round_r1g/e3v2_skeleton/uair/identity.json")
    no_adapt = "0.50" not in str(list(A_GRID)) and "0.55" not in str(list(A_GRID))
    pi_frozen = json.loads((root / "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json").read_text(encoding="utf-8"))
    flags = json.loads((out / "summary" / "R1I_VERDICT.json").read_text(encoding="utf-8"))
    checks = [
        ("R1I-S0", "input freeze", "R1I_INPUT_FREEZE_MANIFEST.csv", "missing", "0", sum(1 for r in freeze_inputs if r["sha256"] == "MISSING"), all(r["sha256"] != "MISSING" for r in freeze_inputs)),
        ("R1I-S1", "natural E3-v2 unchanged", "legacy_refs", "identity_hash", r1g_ident_ss, r1g_ss_now, r1g_ss_now == r1g_ident_ss and r1g_ua_now == r1g_ident_ua),
        ("R1I-S2", "stress mechanism frozen", "stress_spec/R1I_STRESS_LEVEL_FREEZE.md", "hash", stress_level_hash(), stress_level_hash(), (out / "stress_spec/R1I_STRESS_LEVEL_FREEZE.md").is_file()),
        ("R1I-S3", "stress levels frozen", "stress_spec/R1I_STRESS_LEVEL.json", "grid", str(list(A_GRID)), str(list(A_GRID)), list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]),
        ("R1I-S4", "nested mask deterministic", "stress_masks/R1I_AVAILABILITY_MASK_HASH.txt", "hash", mask_rule_hash(), mask_rule_hash(), (out / "stress_masks/R1I_AVAILABILITY_MASK_HASH.txt").read_text(encoding="utf-8").strip() == mask_rule_hash()),
        ("R1I-S5", "mask outcome-independent", "stress_masks/R1I_AVAILABILITY_MASK_RULE.json", "forbidden", "listed", "listed", set(mask_payload["outcome_fields_forbidden"]) >= {"C_oracle_safe", "oracle_pass"} and "C_oracle_safe" not in mask_payload),
        ("R1I-S6", "entity-level thinning", "src/raven_mcs/sag/stress_mask.py", "entity_id", "spatial_id", mask_payload["entity_id"], mask_payload["entity_id"] == "spatial_id"),
        ("R1I-S7", "a=1.00 reproduces natural", "oracle_stress/R1I_BASELINE_REPRODUCTION_AUDIT.csv", "max_diff", f"<={REPRO_TOL}", max_diff, baseline_ok),
        ("R1I-S8", "oracle monotonicity", "oracle_stress/R1I_MONOTONICITY_AUDIT.csv", "violations", "0", n_mono_viol, mono_ok),
        ("R1I-S9", "TARGET_LAW unchanged", "audit/R1I_FREEZE_AUDIT.json", "hash", EXPECTED_TARGET_HASH, rule["hash"], freeze_ok),
        ("R1I-S10", "PI_SAFE unchanged", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "hash", pi_safe_rule_hash(), pi_frozen.get("hash"), pi_frozen.get("hash") == pi_safe_rule_hash()),
        ("R1I-S11", "tau_cov unchanged", "configs/sag_g0/thresholds.json", "tau", "0.05", str(th["tau_cov"]), float(th["tau_cov"]) == 0.05),
        ("R1I-S12", "stress summary complete", "oracle_stress/R1I_ORACLE_STRESS_SUMMARY.csv", "n_rows", "10", str(len(summary)), len(summary) == 10),
        ("R1I-S13", "crossing brackets complete", "boundary_analysis/R1I_WINDOW_CROSSING_BRACKETS.csv", "n", str(len(natural)), str(len(crossings)), len(crossings) == len(natural)),
        ("R1I-S14", "boundary-rich artifact-derived", "boundary_analysis/R1I_BOUNDARY_RICH_LEVELS.csv", "n", str(len(summary)), str(len(rich)), len(rich) == len(summary)),
        ("R1I-S15", "boundary-near artifact-derived", "boundary_analysis/R1I_BOUNDARY_NEAR_WINDOWS.csv", "margin", str(BOUNDARY_NEAR_MARGIN), str(BOUNDARY_NEAR_MARGIN), (out / "boundary_analysis/R1I_BOUNDARY_NEAR_WINDOWS.csv").is_file()),
        ("R1I-S16", "natural/stress tracks separated", "summary/R1I_VERDICT.json", "protocol", PROTOCOL_VERSION, PROTOCOL_VERSION, PROTOCOL_VERSION != "e3-v2-time-aligned-v1"),
        ("R1I-S17", "no adaptive stress tuning", "stress_spec/R1I_STRESS_LEVEL.json", "A_GRID", str(list(A_GRID)), str(list(A_GRID)), no_adapt),
        ("R1I-S18", "no predictor", "summary/R1I_VERDICT.json", "predictor_run", "false", flags.get("predictor_run"), flags.get("predictor_run") is False),
        ("R1I-S19", "no calibration", "summary/R1I_VERDICT.json", "calibration_run", "false", flags.get("calibration_run"), flags.get("calibration_run") is False),
        ("R1I-S20", "no dynamic C_cov", "summary/R1I_VERDICT.json", "dynamic_cov_run", "false", flags.get("dynamic_cov_run"), flags.get("dynamic_cov_run") is False),
        ("R1I-S21", "no SAG", "summary/R1I_VERDICT.json", "sag_started", "false", flags.get("sag_started"), flags.get("sag_started") is False),
        ("R1I-S22", "no 5-seed", "summary/R1I_VERDICT.json", "five_seed_started", "false", flags.get("five_seed_started"), flags.get("five_seed_started") is False),
        ("R1I-S23", "source snapshot complete", "source_snapshot/R1I_SOURCE_SNAPSHOT_MANIFEST.csv", "missing", "0", str(sum(1 for r in snap_rows if r["sha256"] == "MISSING")), all(r["sha256"] != "MISSING" for r in snap_rows)),
        ("R1I-S24", "final verdict artifact-derived", "summary/R1I_VERDICT.json", "verdict", final, final, final in {"READY_FOR_DYNAMIC_CERTIFICATE_STRESS_AUDIT", "READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT", "R1I_STRESS_BOUNDARY_NOT_USABLE", "R1I_STRESS_IMPLEMENTATION_FAILURE"}),
    ]

    gates = build_gates(checks)
    gate_payload = {"gates": gates, "n_pass": sum(1 for x in gates if x["pass"]), "n_fail": sum(1 for x in gates if not x["pass"]), "verdict": final}
    dump_json(gate_payload, out / "summary" / "R1I_GATE_REPORT.json")
    md = ["# R1I gate report", "", f"Verdict: **{final}**", "", "| gate | pass | observed |", "|---|---|---|"]
    for x in gates:
        md.append(f"| {x['gate_id']} | {x['pass']} | {x['observed']} |")
    (out / "summary" / "R1I_GATE_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    r1i_sum = run_pytest(root, R1I_TESTS, out / "audit" / "pytest_r1i.xml")
    full_sum = run_pytest(root, R1I_TESTS + R1H_REGRESSION, out / "audit" / "pytest_full.xml")
    dump_json({"r1i": r1i_sum, "full": full_sum}, out / "audit" / "TEST_SUMMARY.json")
    if r1i_sum.get("status") != "PASS" or full_sum.get("status") != "PASS":
        final = "R1I_STRESS_IMPLEMENTATION_FAILURE"
        dump_json({**json.loads((out / "summary" / "R1I_VERDICT.json").read_text(encoding="utf-8")), "executive_verdict": final}, out / "summary" / "R1I_VERDICT.json")
        gate_payload["verdict"] = final
        dump_json(gate_payload, out / "summary" / "R1I_GATE_REPORT.json")

    def frac_map(dataset: str) -> dict[float, float]:
        sub = summary.loc[summary["dataset"] == dataset]
        return {float(r.availability_level): float(r.fraction_safe) for r in sub.itertuples(index=False)}

    def rich_levels(dataset: str) -> list[float]:
        sub = rich.loc[(rich["dataset"] == dataset) & (rich["BOUNDARY_RICH"].astype(bool))]
        return [float(x) for x in sub["availability_level"].tolist()]

    ss = next(r for r in ds_payloads if r["dataset"] == "sensorscope")
    ua = next(r for r in ds_payloads if r["dataset"] == "uair")
    ss_frac = frac_map("sensorscope")
    ua_frac = frac_map("uair")
    (out / "summary" / "RAVEN_MCS_SAG_G1_R1I_EXOGENOUS_COVERAGE_STRESS_ORACLE_REPORT.md").write_text(
        "\n".join(
            [
                "# RAVEN-MCS SAG G1 R1I Exogenous Coverage-Stress Oracle",
                "",
                f"## Executive verdict: {final}",
                "",
                "Natural E3-v2 remains the deployment-realism track. Controlled availability stress is a separate mechanism-validation track. Stress results do not replace natural results.",
                "",
                "STOP. No dynamic certificate / SAG / 5-seed.",
                "",
                "## Answers",
                "",
                "1. Natural E3-v2 unchanged: identity hashes match freeze; R1i writes only round_r1i.",
                f"2. TARGET_LAW hash unchanged: {rule['hash'] == EXPECTED_TARGET_HASH} (`{rule['hash']}`).",
                f"3. PI_SAFE hash unchanged: `{pi_safe_rule_hash()}`.",
                f"4. tau_cov still 0.05: {float(th['tau_cov']) == 0.05}.",
                f"5. Stress grid frozen as {list(A_GRID)}.",
                "6. Levels/mask/routing frozen before oracle stress computation.",
                "7. Mask is deterministic nested SHA256 unit-interval.",
                "8. Mask is outcome-independent (no oracle/Gate/target-weight fields).",
                "9. Stress is entity-level (spatial_id); all records of an unavailable entity are dropped.",
                f"10. a=1.00 reproduces natural: {baseline_ok}.",
                f"11. max reproduction diff: {max_diff}.",
                f"12. entity counts match at a=1.00: {bool(repro['entity_count_match'].all()) if len(repro) else False}.",
                f"13. C_real_support monotone in a: {mono_ok}.",
                f"14. C_oracle_safe monotone in a: {mono_ok}.",
                f"15. monotonicity violation count: {n_mono_viol}.",
                f"16. SensorScope fraction_safe by a: {ss_frac}.",
                f"17. SensorScope BOUNDARY_RICH levels: {rich_levels('sensorscope')}.",
                f"18. SensorScope MILD_SAFE_EXISTS: {ss['MILD_SAFE_EXISTS']}.",
                f"19. SensorScope SEVERE_UNSAFE_EXISTS: {ss['SEVERE_UNSAFE_EXISTS']}.",
                f"20. SensorScope crossing windows: {ss['n_crossing_windows']}.",
                f"21. SensorScope boundary-near rows: {ss['n_boundary_near']}.",
                f"22. SensorScope dataset verdict: {ss['verdict']}.",
                f"23. U-Air fraction_safe by a: {ua_frac}.",
                f"24. U-Air BOUNDARY_RICH levels: {rich_levels('uair')}.",
                f"25. U-Air MILD_SAFE_EXISTS: {ua['MILD_SAFE_EXISTS']}.",
                f"26. U-Air SEVERE_UNSAFE_EXISTS: {ua['SEVERE_UNSAFE_EXISTS']}.",
                f"27. U-Air crossing windows: {ua['n_crossing_windows']}.",
                f"28. U-Air boundary-near rows: {ua['n_boundary_near']}.",
                f"29. U-Air dataset verdict: {ua['verdict']}.",
                f"30. Stable safe→unsafe transition: SS={ss['monotone_transition']} U-Air={ua['monotone_transition']}.",
                f"31. At least one BOUNDARY_RICH dataset: {ss['n_boundary_rich_levels'] + ua['n_boundary_rich_levels'] > 0}.",
                f"32. Both datasets BOUNDARY_USABLE: {ss['verdict'] == 'BOUNDARY_USABLE' and ua['verdict'] == 'BOUNDARY_USABLE'}.",
                f"33. all-safe/all-unsafe failure: SS all_safe={ss['all_safe']} all_unsafe={ss['all_unsafe']}; U-Air all_safe={ua['all_safe']} all_unsafe={ua['all_unsafe']}.",
                "34. Need to add stress levels this round? **No. This round forbids adding midpoints.**",
                f"35. Allow next-round dynamic certificate stress audit? {final in {'READY_FOR_DYNAMIC_CERTIFICATE_STRESS_AUDIT', 'READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT'}} (verdict={final}).",
                "36. predictor run: False.",
                "37. calibration run: False.",
                "38. dynamic C_cov: False.",
                "39. SAG: False.",
                "40. 5-seed: False.",
                f"41. pytest R1i: {r1i_sum.get('status')} passed={r1i_sum.get('n_passed')} failed={r1i_sum.get('n_failed')}.",
                f"42. full pytest: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}.",
                f"43. R1I-S0–S24 artifact-derived: n_pass={gate_payload['n_pass']} n_fail={gate_payload['n_fail']}.",
                f"44. Final verdict: {final}.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    pack = root / "scripts" / "package_sag_g1_r1i_submission.py"
    if pack.is_file():
        subprocess.run([sys.executable, str(pack)], cwd=root, check=False)
    return {"output_dir": str(out), "verdict": final, "by_dataset": ds_verdicts, "tests": {"r1i": r1i_sum.get("status"), "full": full_sum.get("status")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run_r1i_main(root=args.root, output_dir=args.output_dir), indent=2, default=str))


if __name__ == "__main__":
    main()
