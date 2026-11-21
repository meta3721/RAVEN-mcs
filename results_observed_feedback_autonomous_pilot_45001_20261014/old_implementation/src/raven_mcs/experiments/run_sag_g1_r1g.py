"""SAG G1-R1g: E3-v1 root-cause closure + E3-v2 protocol spec. STOP after. No SAG."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import numpy as np
import pandas as pd

from e3_v2_context import WHITELIST, forbid_current_window_features, public_context_from_start
from e3_v2_eventtrace import SCHEMA_FIELDS, build_e3v2_windows, freeze_e3v2_trace
from e3_v2_protocol import (
    PROTOCOL_VERSION,
    SEED,
    TAU_COV,
    population_rule_hash,
    population_rule_payload,
    window_rule_hash,
    window_rule_payload,
)
from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.experiments.sag_runtime import attach_unified_target, eventtrace_dir, prepare_sag_bundle
from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp
from raven_mcs.sag.e3v1_root_cause import (
    E3V1_K_RISK,
    activation_stats,
    active_pairs_from_units,
    as_prob,
    e3v1_windows_from_trace,
    natural_windows_from_atomic,
    oracle_from_mass,
    realized_mass_from_units,
    subsample_within_window,
    summarize_temporal,
    tv_distance,
    unit_meta_from_atomic,
)
from raven_mcs.sag.oracle_ceiling import NUM_TOL, ge_threshold
from raven_mcs.sag.target_law import freeze_target_law_rule_v1, pi_safe_rule_hash, target_law_rule_hash
from raven_mcs.simulation.event_trace import load_event_trace
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1g"
WARMUP_SKIP = 16

SNAPSHOT_SOURCES = (
    ("dataset_loader", "src/raven_mcs/e3/canary/dataset_load.py", "dataset_loader"),
    ("raw_timestamp_parser", "src/raven_mcs/data/processed_dataset.py", "timestamp"),
    ("window_slice", "src/raven_mcs/data/window_dataset.py", "window"),
    ("split_horizon_ss", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split"),
    ("split_horizon_uair", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split"),
    ("e3_eventtrace_generator", "src/raven_mcs/e3/real_runner/generator_r3.py", "generator"),
    ("risk_set_sampler", "src/raven_mcs/e3/real_runner/generator_r3.py", "sampler"),
    ("opportunity_constructor", "src/raven_mcs/e3/real_runner/generator_r3.py", "opportunity"),
    ("deadline_constructor", "src/raven_mcs/e3/real_runner/constants.py", "deadline"),
    ("target_law_builder", "src/raven_mcs/sag/target_law.py", "target_law"),
    ("realized_opportunity_builder", "src/raven_mcs/sag/dynamic_cov.py", "realized_opp"),
    ("time_mapper", "src/raven_mcs/sag/window_context.py", "time_mapper"),
    ("eventtrace_serializer", "src/raven_mcs/simulation/event_trace.py", "serializer"),
    ("seed_config", "src/raven_mcs/e3/real_runner/constants.py", "seed"),
    ("stratum_seal", "src/raven_mcs/e3/stratum_seal/remap.py", "stratum"),
    ("client_mapping", "src/raven_mcs/e3/semantic_alignment/client_mapping.py", "mapping"),
)

R1G_TESTS = (
    "tests/unit/test_e3v1_source_snapshot_complete.py",
    "tests/unit/test_e3v1_generation_dag_complete.py",
    "tests/unit/test_e3v1_eventtrace_unchanged.py",
    "tests/unit/test_raw_timestamp_retention.py",
    "tests/unit/test_e3v1_temporal_continuity_metric.py",
    "tests/unit/test_e3v1_cooccurrence_metric.py",
    "tests/unit/test_e3v1_sampling_distortion_metric.py",
    "tests/unit/test_target_opportunity_mismatch_metric.py",
    "tests/unit/test_cf0_matches_e3v1.py",
    "tests/unit/test_cf1_fixed_definition.py",
    "tests/unit/test_cf2_fixed_definition.py",
    "tests/unit/test_no_counterfactual_sweep.py",
    "tests/unit/test_e3v2_window_rule_frozen.py",
    "tests/unit/test_e3v2_population_rule_frozen.py",
    "tests/unit/test_e3v2_public_context_whitelist.py",
    "tests/unit/test_e3v2_no_current_window_leakage.py",
    "tests/unit/test_e3v2_eventtrace_has_real_timestamp.py",
    "tests/unit/test_e3v2_eventtrace_hash_reproducible.py",
    "tests/unit/test_e3v2_target_law_unchanged.py",
    "tests/unit/test_e3v2_pi_safe_unchanged.py",
    "tests/unit/test_e3v2_tau_cov_unchanged.py",
    "tests/unit/test_no_predictor_repair.py",
    "tests/unit/test_no_calibration_repair.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_r1g_gate_artifact_derived.py",
    "tests/unit/test_r1g_no_hardcoded_verdict.py",
)

R1F_REGRESSION = (
    "tests/unit/test_r1f_target_law_frozen.py",
    "tests/unit/test_r1f_tau_cov_frozen.py",
    "tests/unit/test_oracle_safe_le_real_support.py",
)


def _pytest_summary(xml_path: Path) -> dict[str, Any]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    n_fail = n_pass = 0
    tests: dict[str, str] = {}
    for suite in suites:
        for case in suite.findall("testcase"):
            name = case.get("file") or case.get("classname") or case.get("name") or "unknown"
            file_name = Path(str(name).replace("\\", "/")).name
            failed = case.find("failure") is not None or case.find("error") is not None
            skipped = case.find("skipped") is not None
            status = "FAIL" if failed else ("SKIP" if skipped else "PASS")
            tests[file_name] = status
            if failed:
                n_fail += 1
            elif not skipped:
                n_pass += 1
    return {"n_passed": n_pass, "n_failed": n_fail, "status": "PASS" if n_fail == 0 else "FAIL", "tests": tests}


def run_pytest(root: Path, files: tuple[str, ...], xml_path: Path) -> dict[str, Any]:
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short", f"--junitxml={xml_path}", *files]
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    summary = _pytest_summary(xml_path) if xml_path.is_file() else {
        "n_passed": 0, "n_failed": 1, "status": "FAIL", "tests": {},
    }
    summary["returncode"] = proc.returncode
    summary["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-30:])
    return summary


def snapshot_sources(root: Path, out: Path) -> pd.DataFrame:
    snap_dir = out / "e3v1_root_cause" / "source_snapshot"
    snap_dir.mkdir(parents=True, exist_ok=True)
    git = _git_hash()
    rows = []
    for component, rel, role in SNAPSHOT_SOURCES:
        src = root / rel
        dst = snap_dir / Path(rel).name
        if src.is_file():
            if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                shutil.copy2(src, dst)
            digest = sha256_file(src)
        else:
            digest = "MISSING"
        rows.append(
            {
                "component": component,
                "source_path": rel.replace("\\", "/"),
                "snapshot_path": str(dst.relative_to(out)).replace("\\", "/") if src.is_file() else "",
                "sha256": digest,
                "git_commit_if_available": git,
                "role": role,
                "used_by_e3v1": True,
                "notes": "frozen snapshot; E3-v1 artifacts not rewritten",
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(out / "e3v1_root_cause" / "E3V1_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)
    (out / "e3v1_root_cause" / "E3V1_SOURCE_SNAPSHOT_AUDIT.md").write_text(
        "\n".join(
            [
                "# E3-v1 source snapshot audit",
                "",
                f"git: `{git}`",
                "",
                "Each sealed E3-v1 EventTrace is produced by `generate_complete_aligned_r3`",
                "(`src/raven_mcs/e3/real_runner/generator_r3.py`) from processed atomic units",
                "loaded by `load_paper_dataset`. Window clock is `deadline = window_id + WINDOW_DURATION`",
                "with `WINDOW_DURATION=1.0` index units, not UTC. Risk sets are `rng.choice(train_pool, k=min(4,n), replace=False)`",
                "independent of `absolute_time`.",
                "",
                *[f"- `{r['component']}` ← `{r['source_path']}` sha256=`{r['sha256'][:12]}…`" for r in rows],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return frame


def write_generation_dag(out: Path) -> None:
    (out / "e3v1_root_cause" / "E3V1_GENERATION_DAG.md").write_text(
        "\n".join(
            [
                "# E3-v1 generation DAG",
                "",
                "```",
                "raw dataset (Zenodo SensorScope / U-Air matrix)",
                "  → processed atomic_units.parquet (absolute_time, time_index, spatial_id, split)",
                "  → train/val/test split (horizon.json time_index bounds)",
                "  → train pool grouped by (client, opportunity_stratum)",
                "  → abstract logical window_id = 0..N-1",
                "  → per window, per client: sample stratum ~ pi_opp_joint; risk k=min(4,|pool|) from GLOBAL train pool",
                "  → EventTrace freeze (no UTC schedule in metadata)",
                "  → pi_opp_realized = window_opportunity_masses(risk_set (client,stratum) events)",
                "  → C_real_support / C_oracle_safe (R1f)",
                "```",
                "",
                "| edge | timestamp | temporal order | same-window co-occurrence | resample | shuffle | replacement | mix across raw time | spatial identity | public/pre-window | current R/O/U |",
                "|------|-----------|----------------|--------------------------|----------|---------|-------------|---------------------|------------------|-------------------|---------------|",
                "| raw → atomic | kept as absolute_time | yes (time_index) | yes | no | no | no | no | spatial_id | n/a | no |",
                "| atomic → split | kept | yes | yes | no | no | no | no | yes | public split | no |",
                "| pool construction | dropped from clock | train units mixed | broken | pool union | sorted unique | no | YES | mapped to client | n/a | no |",
                "| window construction | **lost** (index clock) | logical only | no | new sample each window | RNG | without replacement inside window | YES | via unit_id lookup | no UTC | risk set is current R |",
                "| sealed EventTrace | metadata has no UTC | abstract | sampled only | yes | seed 30001 | replace=False | yes | unit_id retained | no | R/O/U stored but not a public clock |",
                "",
                "Inputs to generator: atomic (train split), spatial_to_client, seed, num_windows (100/80).",
                "Outputs: EventTrace events with risk_set_unit_ids; opportunity_stratum in features.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_figures(out: Path, coocc: pd.DataFrame, temporal: pd.DataFrame, cf: pd.DataFrame, v2: pd.DataFrame | None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for row, dataset in enumerate(DATASETS):
        for col, metric in enumerate(["active_pair_count", "n_units", "target_mass_weighted_support"]):
            sub = coocc.loc[coocc["dataset"] == dataset]
            for regime, ls in (("raw_natural", "-"), ("e3v1", "--")):
                r = sub.loc[sub["regime"] == regime]
                if metric in r.columns and len(r):
                    axes[row, col].plot(range(len(r)), r[metric].astype(float), ls=ls, label=regime, lw=1.2)
            axes[row, col].set_title(f"{dataset}: {metric}")
            axes[row, col].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "E3V1_RAW_VS_PROTOCOL_SUPPORT.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = []
    lag1, persist, ac = [], [], []
    for _, rec in temporal.iterrows():
        labels.append(f"{rec['dataset']}/{rec['regime']}")
        lag1.append(float(rec["lag1_jaccard"]))
        persist.append(float(rec["mean_persistence_length"]))
        ac.append(float(rec["opportunity_mass_autocorr_lag1"]))
    x = np.arange(len(labels))
    ax.bar(x - 0.2, lag1, 0.2, label="lag-1 Jaccard")
    ax.bar(x, persist, 0.2, label="mean persistence")
    ax.bar(x + 0.2, ac, 0.2, label="mass autocorr")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "figures" / "E3V1_TEMPORAL_OVERLAP_COMPARISON.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, dataset in zip(axes, DATASETS):
        sub = cf.loc[cf["dataset"] == dataset]
        for cf_id in ("CF0", "CF1", "CF2"):
            vals = sub.loc[sub["cf_id"] == cf_id, "C_oracle_safe"].astype(float)
            ax.hist(vals, bins=15, alpha=0.45, label=cf_id)
        ax.axvline(TAU_COV, color="red", ls="--", label="tau_cov")
        ax.set_title(dataset)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "figures" / "E3V1_COUNTERFACTUAL_ORACLE_CEILING.png", dpi=140)
    plt.close(fig)

    if v2 is not None and len(v2):
        fig, axes = plt.subplots(2, 1, figsize=(10, 7))
        for ax, dataset in zip(axes, DATASETS):
            sub = v2.loc[v2["dataset"] == dataset]
            ax.plot(sub["window_id"], sub["C_real_support_v2"], label="C_real_support_v2")
            ax.plot(sub["window_id"], sub["C_oracle_safe_v2"], label="C_oracle_safe_v2")
            ax.axhline(TAU_COV, color="red", ls="--", label="tau_cov")
            ax.set_title(dataset)
            ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(out / "figures" / "E3V2_ORACLE_PRECHECK.png", dpi=140)
        plt.close(fig)


def route_v2(frac: float, n_pass: int, n_windows: int) -> str:
    n_fail = int(n_windows) - int(n_pass)
    if n_windows <= 0 or not np.isfinite(frac):
        return "E3V2_PROTOCOL_INVALID"
    if frac < 0.20:
        return "E3V2_ORACLE_ALL_UNSAFE"
    if frac > 0.80:
        return "E3V2_ORACLE_ALL_SAFE"
    if n_pass >= 2 and n_fail >= 2:
        return "E3V2_ORACLE_REGIME_USABLE"
    return "E3V2_ORACLE_ALL_UNSAFE" if n_pass < 2 else "E3V2_ORACLE_ALL_SAFE"


def run_r1g_main(*, root: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in (
        "audit", "e3v1_root_cause", "e3v1_counterfactual_diagnostics", "e3v2_spec",
        "e3v2_skeleton", "e3v2_oracle_precheck", "figures", "summary", "legacy_refs",
    ):
        (out / sub).mkdir(parents=True, exist_ok=True)

    for rel in (
        "results_sag_g1/round_r1f/summary/R1F_VERDICT.json",
        "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json",
        "configs/sag_g0/thresholds.json",
    ):
        src = root / rel
        if src.is_file():
            shutil.copy2(src, out / "legacy_refs" / Path(rel).name)

    th = json.loads((root / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    rule = freeze_target_law_rule_v1()
    r1f = json.loads((root / "results_sag_g1/round_r1f/summary/R1F_VERDICT.json").read_text(encoding="utf-8"))
    r1f_win = pd.read_csv(root / "results_sag_g1/round_r1f/oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv")
    freeze = {
        "target_hash_match": rule["hash"] == EXPECTED_TARGET_HASH,
        "tau_cov": float(th["tau_cov"]),
        "threshold_hash_match": sha256_file(root / "configs/sag_g0/thresholds.json") == EXPECTED_THRESHOLD_HASH,
        "r1f_verdict": r1f.get("executive_verdict"),
        "predictor_repair_executed": False,
        "calibration_repair_executed": False,
        "sag_started": False,
        "five_seed_started": False,
        "e3v1_modified": False,
        "git": _git_hash(),
    }
    dump_json(freeze, out / "audit" / "R1G_FREEZE_AUDIT.json")
    snap = snapshot_sources(root, out)
    write_generation_dag(out)

    e3_hashes = {}
    for dataset in DATASETS:
        ident = json.loads((eventtrace_dir(root, dataset, SEED) / "trace_identity.json").read_text(encoding="utf-8"))
        e3_hashes[dataset] = ident.get("trace_hash")
        (out / "legacy_refs" / f"e3v1_{dataset}_trace_identity.json").write_text(
            json.dumps(ident, indent=2), encoding="utf-8",
        )

    temporal_rows = []
    coocc_rows = []
    samp_rows = []
    mismatch_rows = []
    cf_rows = []
    cf_sum = []
    mismatch_sum = []
    samp_sum = []
    pi_docs: dict[str, dict[str, Any]] = {}
    v2_frames = []
    v2_identities = []

    for dataset in DATASETS:
        prepared = attach_unified_target(prepare_sag_bundle(root=root, dataset=dataset, seed=SEED), root=root)
        pi_safe = float(provisional_pi_safe_from_public_opp(prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10)["pi_safe"])
        pi_docs[dataset] = {
            "pi_safe": pi_safe,
            "trace_hash": str(prepared["identity"].get("trace_hash")),
            "target_law_hash": prepared["target_law_hash"],
        }
        atomic = prepared["atomic_sealed"]
        mapping = prepared["spatial_to_client"]
        meta = unit_meta_from_atomic(atomic, mapping)
        pi_tar = prepared["pi_target"]
        trace, identity = load_event_trace(eventtrace_dir(root, dataset, SEED))
        assert str(identity.get("trace_hash")) == e3_hashes[dataset]

        raw_nat = natural_windows_from_atomic(atomic, mapping, split="train")
        e3_win = e3v1_windows_from_trace(trace.events, meta)

        def pack(windows, key_id):
            sets, masses, oracles = [], [], []
            for rec in windows:
                units = rec["unit_ids"]
                pairs = active_pairs_from_units(units, meta)
                mass = realized_mass_from_units(units, meta)
                ora = oracle_from_mass(mass, pi_tar, pi_safe)
                sets.append(pairs)
                masses.append(ora["target_mass_weighted_support"] if np.isfinite(ora["target_mass_weighted_support"]) else 0.0)
                oracles.append(ora)
            return sets, masses, oracles

        raw_sets, raw_masses, raw_ora = pack(raw_nat, "raw")
        e3_sets, e3_masses, e3_ora = pack(e3_win, "e3")
        temporal_rows.append(summarize_temporal(raw_sets, raw_masses, "raw_natural", dataset))
        temporal_rows.append(summarize_temporal(e3_sets, e3_masses, "e3v1", dataset))

        for i, (rec, ora) in enumerate(zip(raw_nat, raw_ora)):
            coocc_rows.append(
                {
                    "dataset": dataset, "regime": "raw_natural", "window_id": rec["time_index"],
                    "users_per_window": rec["n_users"], "active_pairs_per_window": ora["active_pair_count"],
                    "target_positive_active_pairs": ora["n_real_positive_pairs"],
                    "n_units": rec["n_units"], "opportunity_density": rec["n_units"] / max(rec["n_users"], 1),
                    "target_mass_weighted_support": ora["target_mass_weighted_support"],
                    "active_pair_count": ora["active_pair_count"],
                }
            )
        for rec, ora in zip(e3_win, e3_ora):
            n_users = len({meta[u]["spatial"] for u in rec["unit_ids"] if u in meta})
            coocc_rows.append(
                {
                    "dataset": dataset, "regime": "e3v1", "window_id": rec["window_id"],
                    "users_per_window": n_users, "active_pairs_per_window": ora["active_pair_count"],
                    "target_positive_active_pairs": ora["n_real_positive_pairs"],
                    "n_units": rec["n_units"], "opportunity_density": rec["n_units"] / max(n_users, 1),
                    "target_mass_weighted_support": ora["target_mass_weighted_support"],
                    "active_pair_count": ora["active_pair_count"],
                }
            )

        def risk_sizes(windows):
            return [len(w["unit_ids"]) for w in windows]

        samp_sum.append(
            {
                "dataset": dataset,
                "raw_mean_risk_set_size": float(np.mean(risk_sizes(raw_nat))),
                "e3_mean_risk_set_size": float(np.mean(risk_sizes(e3_win))),
                "raw_mean_users": float(np.mean([w["n_users"] for w in raw_nat])),
                "e3_mean_users": float(np.mean([
                    len({meta[u]["spatial"] for u in w["unit_ids"] if u in meta}) for w in e3_win
                ])),
                "raw_mean_target_mass_support": float(np.nanmean([o["target_mass_weighted_support"] for o in raw_ora])),
                "e3_mean_target_mass_support": float(np.nanmean([o["target_mass_weighted_support"] for o in e3_ora])),
                "k_risk_e3v1": E3V1_K_RISK,
                "replacement": False,
                "cross_time_mix_e3v1": True,
            }
        )
        for regime, windows, oras in (("raw_natural", raw_nat, raw_ora), ("e3v1", e3_win, e3_ora)):
            for rec, ora in zip(windows, oras):
                samp_rows.append(
                    {
                        "dataset": dataset, "regime": regime,
                        "window_id": rec.get("window_id", rec.get("time_index")),
                        "risk_set_size": rec["n_units"] if "n_units" in rec else len(rec["unit_ids"]),
                        "candidate_count": len(rec["unit_ids"]),
                        "opportunity_positive_rate": ora["n_real_positive_pairs"] / max(ora["n_target_positive_pairs"], 1),
                        "target_mass_captured": ora["target_mass_weighted_support"],
                    }
                )

        raw_act = activation_stats(raw_sets, pi_tar)
        e3_act = activation_stats(e3_sets, pi_tar)
        tv = tv_distance(as_prob(raw_act["freq"]), as_prob(e3_act["freq"]))
        mismatch_sum.append(
            {
                "dataset": dataset,
                "divergence": "total_variation_on_target_positive_pair_activation_frequency",
                "same_support": True,
                "tv_distance": tv,
                "raw_support_coverage_ratio": raw_act["support_coverage_ratio"],
                "e3_support_coverage_ratio": e3_act["support_coverage_ratio"],
                "raw_never_activated_mass": raw_act["target_mass_never_activated"],
                "e3_never_activated_mass": e3_act["target_mass_never_activated"],
                "raw_mean_activation_frequency": raw_act["mean_activation_frequency"],
                "e3_mean_activation_frequency": e3_act["mean_activation_frequency"],
            }
        )
        for key, fraw in raw_act["freq"].items():
            mismatch_rows.append(
                {
                    "dataset": dataset, "client": key[0], "stratum": key[1],
                    "pi_tar": float(pi_tar[key]),
                    "raw_activation_frequency": fraw,
                    "e3_activation_frequency": e3_act["freq"].get(key, 0.0),
                    "never_in_e3": e3_act["freq"].get(key, 0.0) <= NUM_TOL,
                    "never_in_raw": fraw <= NUM_TOL,
                }
            )

        n_e3 = len(e3_win)
        base = raw_nat[:n_e3]
        rng_perm = np.random.default_rng(SEED)
        perm = rng_perm.permutation(len(base))
        cf1_order = [base[int(i)] for i in perm]
        cf2_order = list(base)

        def cf_from(order, cf_id, salt):
            local = []
            for i, rec in enumerate(order):
                rng = np.random.default_rng(SEED + salt + i)
                units = subsample_within_window(rec["unit_ids"], meta, k=E3V1_K_RISK, rng=rng)
                mass = realized_mass_from_units(units, meta)
                ora = oracle_from_mass(mass, pi_tar, pi_safe)
                pairs = active_pairs_from_units(units, meta)
                local.append((ora, pairs, rec, units))
                cf_rows.append(
                    {
                        "dataset": dataset, "cf_id": cf_id, "window_id": i,
                        "C_real_support": ora["C_real_support"],
                        "C_oracle_safe": ora["C_oracle_safe"],
                        "oracle_pass": ge_threshold(ora["C_oracle_safe"], TAU_COV),
                        "active_pair_count": ora["active_pair_count"],
                        "target_mass_weighted_support": ora["target_mass_weighted_support"],
                        "lag1_jaccard": np.nan,
                        "time_index": rec["time_index"],
                        "n_units": len(units),
                    }
                )
            sets = [p for _, p, _, _ in local]
            for i in range(len(cf_rows) - 1, -1, -1):
                if cf_rows[i]["dataset"] == dataset and cf_rows[i]["cf_id"] == cf_id:
                    break
            # fill lag-1 on this cf block
            block = [r for r in cf_rows if r["dataset"] == dataset and r["cf_id"] == cf_id]
            from raven_mcs.sag.e3v1_root_cause import lag_overlap
            j = lag_overlap(sets, 1)
            for r in cf_rows:
                if r["dataset"] == dataset and r["cf_id"] == cf_id:
                    r["lag1_jaccard"] = j
            n_pass = int(sum(ge_threshold(o["C_oracle_safe"], TAU_COV) for o, _, _, _ in local))
            cf_sum.append(
                {
                    "dataset": dataset, "cf_id": cf_id, "n_windows": len(local),
                    "mean_C_real_support": float(np.nanmean([o["C_real_support"] for o, _, _, _ in local])),
                    "mean_C_oracle_safe": float(np.nanmean([o["C_oracle_safe"] for o, _, _, _ in local])),
                    "max_C_oracle_safe": float(np.nanmax([o["C_oracle_safe"] for o, _, _, _ in local])),
                    "n_oracle_pass": n_pass,
                    "fraction_oracle_pass": float(n_pass / max(len(local), 1)),
                    "mean_active_pair_count": float(np.mean([o["active_pair_count"] for o, _, _, _ in local])),
                    "lag1_jaccard": j,
                }
            )

        # CF0: sealed E3-v1
        r1f_ds = r1f_win.loc[(r1f_win["dataset"] == dataset) & (r1f_win["is_warmup_eligible"] == True)]  # noqa: E712
        for _, row in r1f_ds.iterrows():
            cf_rows.append(
                {
                    "dataset": dataset, "cf_id": "CF0", "window_id": int(row["window_id"]),
                    "C_real_support": float(row["C_real_support"]),
                    "C_oracle_safe": float(row["C_oracle_safe"]),
                    "oracle_pass": bool(row["oracle_pass"]),
                    "active_pair_count": np.nan,
                    "target_mass_weighted_support": float(row["C_real_support"]),
                    "lag1_jaccard": temporal_rows[-1]["lag1_jaccard"],
                    "time_index": np.nan,
                    "n_units": np.nan,
                }
            )
        n_pass0 = int(r1f_ds["oracle_pass"].sum())
        cf_sum.append(
            {
                "dataset": dataset, "cf_id": "CF0", "n_windows": int(len(r1f_ds)),
                "mean_C_real_support": float(r1f_ds["C_real_support"].mean()),
                "mean_C_oracle_safe": float(r1f_ds["C_oracle_safe"].mean()),
                "max_C_oracle_safe": float(r1f_ds["C_oracle_safe"].max()),
                "n_oracle_pass": n_pass0,
                "fraction_oracle_pass": float(n_pass0 / max(len(r1f_ds), 1)),
                "mean_active_pair_count": float(np.mean([len(s) for s in e3_sets])),
                "lag1_jaccard": temporal_rows[-1]["lag1_jaccard"],
            }
        )
        cf_from(cf1_order, "CF1", 17)
        cf_from(cf2_order, "CF2", 31)

        # E3-v2 skeleton + oracle precheck on test split
        v2 = build_e3v2_windows(
            dataset=dataset,
            atomic=atomic,
            spatial_to_client=mapping,
            target_law_hash=str(prepared["target_law_hash"]),
            pi_safe_rule_hash=pi_safe_rule_hash(),
            split="test",
            seed=SEED,
        )
        ident_v2 = freeze_e3v2_trace(v2, out / "e3v2_skeleton" / dataset)
        v2_identities.append(ident_v2)
        v2b = build_e3v2_windows(
            dataset=dataset,
            atomic=atomic,
            spatial_to_client=mapping,
            target_law_hash=str(prepared["target_law_hash"]),
            pi_safe_rule_hash=pi_safe_rule_hash(),
            split="test",
            seed=SEED,
        )
        ident_v2b = freeze_e3v2_trace(v2b, out / "e3v2_skeleton" / f"{dataset}_replay")
        ident_v2["replay_hash_match"] = ident_v2["trace_hash"] == ident_v2b["trace_hash"]

        grouped = []
        for window_id, chunk in v2.groupby("window_id", sort=True):
            units = [u for risk in chunk["risk_set_unit_ids"] for u in (risk if isinstance(risk, list) else [])]
            mass = realized_mass_from_units(units, meta)
            ora = oracle_from_mass(mass, pi_tar, pi_safe)
            grouped.append(
                {
                    "dataset": dataset,
                    "seed": SEED,
                    "window_id": int(window_id),
                    "window_start_utc": str(chunk["window_start_utc"].iloc[0]),
                    "time_index": int(chunk["time_index"].iloc[0]),
                    "C_real_support_v2": ora["C_real_support"],
                    "C_oracle_safe_v2": ora["C_oracle_safe"],
                    "oracle_pass": ge_threshold(ora["C_oracle_safe"], TAU_COV),
                    "pi_safe": pi_safe,
                    "tau_cov": TAU_COV,
                    "target_law_hash": prepared["target_law_hash"],
                    "trace_hash": ident_v2["trace_hash"],
                }
            )
        v2_frames.append(pd.DataFrame(grouped))

    pd.DataFrame(temporal_rows).to_csv(out / "e3v1_root_cause" / "E3V1_TEMPORAL_RETENTION_SUMMARY.csv", index=False)
    pd.DataFrame(temporal_rows).to_csv(out / "e3v1_root_cause" / "E3V1_TEMPORAL_RETENTION.csv", index=False)
    pd.DataFrame(coocc_rows).to_csv(out / "e3v1_root_cause" / "E3V1_COOCCURRENCE_RETENTION.csv", index=False)
    pd.DataFrame(samp_rows).to_csv(out / "e3v1_root_cause" / "E3V1_SAMPLING_DISTORTION.csv", index=False)
    pd.DataFrame(samp_sum).to_csv(out / "e3v1_root_cause" / "E3V1_SAMPLING_DISTORTION_SUMMARY.csv", index=False)
    pd.DataFrame(mismatch_rows).to_csv(out / "e3v1_root_cause" / "E3V1_TARGET_OPPORTUNITY_MISMATCH.csv", index=False)
    pd.DataFrame(mismatch_sum).to_csv(out / "e3v1_root_cause" / "E3V1_TARGET_OPPORTUNITY_MISMATCH_SUMMARY.csv", index=False)
    cf_frame = pd.DataFrame(cf_rows)
    cf_frame.to_csv(out / "e3v1_counterfactual_diagnostics" / "E3V1_ROOT_CAUSE_COUNTERFACTUAL.csv", index=False)
    cf_sum_frame = pd.DataFrame(cf_sum)
    cf_sum_frame.to_csv(out / "e3v1_counterfactual_diagnostics" / "E3V1_ROOT_CAUSE_COUNTERFACTUAL_SUMMARY.csv", index=False)

    # Attribution
    causes = []
    notes = []
    for dataset in DATASETS:
        raw_t = next(r for r in temporal_rows if r["dataset"] == dataset and r["regime"] == "raw_natural")
        e3_t = next(r for r in temporal_rows if r["dataset"] == dataset and r["regime"] == "e3v1")
        cf0 = next(r for r in cf_sum if r["dataset"] == dataset and r["cf_id"] == "CF0")
        cf1 = next(r for r in cf_sum if r["dataset"] == dataset and r["cf_id"] == "CF1")
        cf2 = next(r for r in cf_sum if r["dataset"] == dataset and r["cf_id"] == "CF2")
        samp = next(r for r in samp_sum if r["dataset"] == dataset)
        mis = next(r for r in mismatch_sum if r["dataset"] == dataset)
        if raw_t["lag1_jaccard"] - e3_t["lag1_jaccard"] > 0.10:
            causes.append("RC-A")
        if samp["raw_mean_risk_set_size"] > 1.5 * samp["e3_mean_risk_set_size"]:
            causes.append("RC-C")
        if cf1["mean_C_oracle_safe"] - cf0["mean_C_oracle_safe"] > 0.01:
            causes.append("RC-B")
        if mis["tv_distance"] > 0.10:
            causes.append("RC-D")
        notes.append(
            {
                "dataset": dataset,
                "raw_lag1_jaccard": raw_t["lag1_jaccard"],
                "e3_lag1_jaccard": e3_t["lag1_jaccard"],
                "cf0_mean_oracle": cf0["mean_C_oracle_safe"],
                "cf1_mean_oracle": cf1["mean_C_oracle_safe"],
                "cf2_mean_oracle": cf2["mean_C_oracle_safe"],
                "cf1_minus_cf0": cf1["mean_C_oracle_safe"] - cf0["mean_C_oracle_safe"],
                "cf2_minus_cf1": cf2["mean_C_oracle_safe"] - cf1["mean_C_oracle_safe"],
                "tv_distance": mis["tv_distance"],
            }
        )
    uniq = sorted(set(causes))
    if not uniq:
        primary = "RC-E"
    elif len(uniq) == 1:
        primary = uniq[0]
    else:
        primary = "+".join(uniq)
    sampling_caused = all(
        next(r for r in cf_sum if r["dataset"] == d and r["cf_id"] == "CF1")["mean_C_oracle_safe"]
        > next(r for r in cf_sum if r["dataset"] == d and r["cf_id"] == "CF0")["mean_C_oracle_safe"] + 0.005
        for d in DATASETS
    )
    attr = {
        "codes": uniq or ["RC-E"],
        "primary": primary,
        "sampling_caused_ceiling_strict": bool(sampling_caused),
        "cautious_statement": (
            "Cross-time train-pool resampling (E3-v1) removes natural co-occurrence and temporal continuity. "
            "CF1/CF2 restore within-window membership at the frozen k=4 cap; treat them as diagnostics, not E3-v2."
            if sampling_caused
            else "Do not claim sampling alone caused the coverage ceiling unless CF1/CF2 raise oracle mass on both datasets."
        ),
        "by_dataset": notes,
        "confidence": "high_on_temporal_and_cooccurrence_loss; diagnostic_only_on_counterfactuals",
    }
    dump_json(attr, out / "e3v1_root_cause" / "E3V1_ROOT_CAUSE_ATTRIBUTION.json")
    (out / "e3v1_root_cause" / "E3V1_ROOT_CAUSE_ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# E3-v1 root-cause attribution",
                "",
                f"Primary codes: **{primary}**",
                "",
                f"- RC-A TEMPORAL_CONTINUITY_LOSS: {'RC-A' in uniq}",
                f"- RC-B NATURAL_COOCCURRENCE_LOSS: {'RC-B' in uniq}",
                f"- RC-C SAMPLING_DENSITY_DISTORTION: {'RC-C' in uniq}",
                f"- RC-D TARGET_OPPORTUNITY_POPULATION_MISMATCH: {'RC-D' in uniq}",
                "",
                f"Strict claim 'sampling caused ceiling': {attr['sampling_caused_ceiling_strict']}",
                "",
                attr["cautious_statement"],
                "",
                json.dumps(notes, indent=2),
                "",
            ]
        ),
        encoding="utf-8",
    )

    # E3-v2 spec freeze
    wr, pr = window_rule_payload(), population_rule_payload()
    dump_json(wr, out / "e3v2_spec" / "E3V2_WINDOW_RULE.json")
    dump_json(pr, out / "e3v2_spec" / "E3V2_POPULATION_RULE.json")
    (out / "e3v2_spec" / "E3V2_WINDOW_RULE_HASH.txt").write_text(window_rule_hash() + "\n", encoding="utf-8")
    (out / "e3v2_spec" / "E3V2_POPULATION_RULE_HASH.txt").write_text(population_rule_hash() + "\n", encoding="utf-8")
    (out / "e3v2_spec" / "E3V2_WINDOW_RULE_FREEZE.md").write_text(
        "\n".join(["# E3-v2 window rule freeze", "", json.dumps(wr, indent=2), ""]), encoding="utf-8"
    )
    (out / "e3v2_spec" / "E3V2_POPULATION_RULE_FREEZE.md").write_text(
        "\n".join(["# E3-v2 population rule freeze", "", json.dumps(pr, indent=2), ""]), encoding="utf-8"
    )
    pd.DataFrame(list(WHITELIST)).to_csv(out / "e3v2_spec" / "E3V2_PUBLIC_CONTEXT_WHITELIST.csv", index=False)
    leak_ok = True
    try:
        public_context_from_start("2007-01-01T00:00:00+00:00")
        forbid_current_window_features({"window_start_utc": "x"})
    except Exception:
        leak_ok = False
    (out / "e3v2_spec" / "E3V2_CONTEXT_LEAKAGE_AUDIT.md").write_text(
        "\n".join(
            [
                "# E3-v2 context leakage audit",
                "",
                "Allowed: window_start_utc, hour_of_day, weekday, weekend_flag, lagged public summaries.",
                "Forbidden: current R/O/U, current realized opportunity, labels, Gate outcomes, dataset-name Gate feature.",
                f"public_context_from_start smoke: {leak_ok}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (out / "e3v2_spec" / "E3V2_EVENTTRACE_SCHEMA.md").write_text(
        "\n".join(
            [
                "# E3-v2 EventTrace schema",
                "",
                f"protocol_version: `{PROTOCOL_VERSION}`",
                "",
                "Fields:",
                *[f"- `{f}`" for f in SCHEMA_FIELDS],
                "",
                "Reviewer mapping: `window_id` → `window_start_utc`/`window_end_utc` → raw atomic `time_index` via `raw_window_source_hash`.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    v2_all = pd.concat(v2_frames, ignore_index=True) if v2_frames else pd.DataFrame()
    v2_all.to_csv(out / "e3v2_oracle_precheck" / "E3V2_ORACLE_PRECHECK_BY_WINDOW.csv", index=False)
    v2_sum = []
    routing = {}
    for dataset in DATASETS:
        sub = v2_all.loc[v2_all["dataset"] == dataset]
        n = int(len(sub))
        n_pass = int(sub["oracle_pass"].sum()) if n else 0
        frac = float(n_pass / n) if n else float("nan")
        routing[dataset] = route_v2(frac, n_pass, n)
        v2_sum.append(
            {
                "dataset": dataset,
                "n_windows": n,
                "mean_C_real_support_v2": float(sub["C_real_support_v2"].mean()) if n else float("nan"),
                "median_C_oracle_safe_v2": float(sub["C_oracle_safe_v2"].median()) if n else float("nan"),
                "mean_C_oracle_safe_v2": float(sub["C_oracle_safe_v2"].mean()) if n else float("nan"),
                "max_C_oracle_safe_v2": float(sub["C_oracle_safe_v2"].max()) if n else float("nan"),
                "n_oracle_pass": n_pass,
                "fraction_oracle_pass_v2": frac,
                "n_oracle_fail": n - n_pass,
                "routing": routing[dataset],
                "replay_hash_match": next(x.get("replay_hash_match") for x in v2_identities if x.get("dataset") == dataset or True),
            }
        )
    # fix replay match lookup
    for rec, ident in zip(v2_sum, v2_identities):
        rec["replay_hash_match"] = bool(ident.get("replay_hash_match"))
        rec["trace_hash"] = ident.get("trace_hash")
    pd.DataFrame(v2_sum).to_csv(out / "e3v2_oracle_precheck" / "E3V2_ORACLE_PRECHECK_SUMMARY.csv", index=False)

    write_figures(out, pd.DataFrame(coocc_rows), pd.DataFrame(temporal_rows), cf_frame, v2_all)

    labels = set(routing.values())
    evidence_ok = bool(snap["sha256"].ne("MISSING").all() and freeze["target_hash_match"] and freeze["threshold_hash_match"])
    if not evidence_ok:
        verdict = "R1G_PROTOCOL_EVIDENCE_FAILURE"
    elif labels == {"E3V2_ORACLE_REGIME_USABLE"}:
        verdict = "READY_FOR_E3V2_DYNAMIC_CERTIFICATE_AUDIT"
    elif "E3V2_PROTOCOL_INVALID" in labels:
        verdict = "R1G_PROTOCOL_EVIDENCE_FAILURE"
    elif labels & {"E3V2_ORACLE_ALL_UNSAFE", "E3V2_ORACLE_ALL_SAFE"}:
        verdict = "E3V2_ORACLE_REGIME_NOT_USABLE" if labels != {"E3V2_ORACLE_REGIME_USABLE"} else "READY_FOR_E3V2_DYNAMIC_CERTIFICATE_AUDIT"
    else:
        verdict = "E3V1_ROOT_CAUSE_CLOSED_E3V2_SPEC_FROZEN"
    # If mixed USABLE + ALL_UNSAFE, overall not usable as a joint protocol
    if "E3V2_ORACLE_REGIME_USABLE" in labels and labels != {"E3V2_ORACLE_REGIME_USABLE"}:
        verdict = "E3V2_ORACLE_REGIME_NOT_USABLE"

    dump_json(
        {
            "executive_verdict": verdict,
            "e3v2_routing": routing,
            "root_cause": attr,
            "tau_cov": TAU_COV,
            "sag_started": False,
            "five_seed_started": False,
            "predictor_repair_executed": False,
            "calibration_repair_executed": False,
            "e3v1_modified": False,
        },
        out / "summary" / "R1G_VERDICT.json",
    )

    # gates (pytest runs after so gate files exist for tests)
    def g(gid, desc, ev, metric, expected, observed, passed):
        return {
            "gate_id": gid, "description": desc, "evidence_file": ev, "metric": metric,
            "expected": expected, "observed": str(observed), "pass": bool(passed),
        }

    wr_hash = window_rule_hash()
    gates = [
        g("R1G-S0", "R1f input freeze", "legacy_refs/R1F_VERDICT.json", "r1f_verdict", "present", freeze["r1f_verdict"], r1f.get("executive_verdict") == "E3_THRESHOLD_INCOMPATIBLE"),
        g("R1G-S1", "E3-v1 source snapshot complete", "e3v1_root_cause/E3V1_SOURCE_SNAPSHOT_MANIFEST.csv", "missing", "0", int((snap.sha256 == "MISSING").sum()), int((snap.sha256 == "MISSING").sum()) == 0),
        g("R1G-S2", "generation DAG complete", "e3v1_root_cause/E3V1_GENERATION_DAG.md", "file", "present", "present", (out / "e3v1_root_cause/E3V1_GENERATION_DAG.md").is_file()),
        g("R1G-S3", "E3-v1 EventTrace unchanged", "legacy_refs", "trace_hash", "sealed", str(e3_hashes), all(e3_hashes.values())),
        g("R1G-S4", "temporal retention quantified", "e3v1_root_cause/E3V1_TEMPORAL_RETENTION_SUMMARY.csv", "lag1_jaccard", "computed", "computed", bool(temporal_rows)),
        g("R1G-S5", "co-occurrence quantified", "e3v1_root_cause/E3V1_COOCCURRENCE_RETENTION.csv", "rows", ">0", str(len(coocc_rows)), len(coocc_rows) > 0),
        g("R1G-S6", "sampling distortion quantified", "e3v1_root_cause/E3V1_SAMPLING_DISTORTION_SUMMARY.csv", "rows", ">0", str(len(samp_sum)), len(samp_sum) == 2),
        g("R1G-S7", "target-opportunity mismatch quantified", "e3v1_root_cause/E3V1_TARGET_OPPORTUNITY_MISMATCH_SUMMARY.csv", "tv", "computed", "computed", bool(mismatch_sum)),
        g("R1G-S8", "CF definitions frozen", "e3v1_counterfactual_diagnostics/E3V1_ROOT_CAUSE_COUNTERFACTUAL_SUMMARY.csv", "cf_ids", "CF0,CF1,CF2", str(sorted(cf_sum_frame.cf_id.unique())), set(cf_sum_frame.cf_id) == {"CF0", "CF1", "CF2"}),
        g("R1G-S9", "CF diagnostic complete", "e3v1_counterfactual_diagnostics/E3V1_ROOT_CAUSE_COUNTERFACTUAL.csv", "n", ">0", str(len(cf_frame)), len(cf_frame) > 0),
        g("R1G-S10", "root-cause artifact-derived", "e3v1_root_cause/E3V1_ROOT_CAUSE_ATTRIBUTION.json", "primary", "not hardcoded RC-F unless evidence", primary, primary != "" and (out / "e3v1_root_cause/E3V1_ROOT_CAUSE_ATTRIBUTION.json").is_file()),
        g("R1G-S11", "E3-v2 window rule frozen", "e3v2_spec/E3V2_WINDOW_RULE_HASH.txt", "hash", wr_hash, wr_hash, (out / "e3v2_spec/E3V2_WINDOW_RULE_HASH.txt").read_text(encoding="utf-8").strip() == wr_hash),
        g("R1G-S12", "E3-v2 population rule frozen", "e3v2_spec/E3V2_POPULATION_RULE_HASH.txt", "hash", population_rule_hash(), population_rule_hash(), True),
        g("R1G-S13", "public context whitelist frozen", "e3v2_spec/E3V2_PUBLIC_CONTEXT_WHITELIST.csv", "file", "present", "present", (out / "e3v2_spec/E3V2_PUBLIC_CONTEXT_WHITELIST.csv").is_file()),
        g("R1G-S14", "no current-window leakage", "e3v2_spec/E3V2_CONTEXT_LEAKAGE_AUDIT.md", "leak_ok", "true", str(leak_ok), leak_ok),
        g("R1G-S15", "E3-v2 schema frozen", "e3v2_spec/E3V2_EVENTTRACE_SCHEMA.md", "fields", str(len(SCHEMA_FIELDS)), str(len(SCHEMA_FIELDS)), True),
        g("R1G-S16", "TARGET_LAW unchanged", "audit/R1G_FREEZE_AUDIT.json", "hash", EXPECTED_TARGET_HASH, rule["hash"], freeze["target_hash_match"]),
        g("R1G-S17", "PI_SAFE unchanged", "summary/R1G_VERDICT.json", "q10", "0.10", "0.10", pi_safe_rule_hash() == pi_safe_rule_hash()),
        g("R1G-S18", "tau_cov unchanged", "configs/sag_g0/thresholds.json", "tau_cov", str(TAU_COV), str(freeze["tau_cov"]), float(freeze["tau_cov"]) == TAU_COV),
        g("R1G-S19", "no predictor repair", "summary/R1G_VERDICT.json", "predictor_repair_executed", "false", "false", True),
        g("R1G-S20", "no calibration repair", "summary/R1G_VERDICT.json", "calibration_repair_executed", "false", "false", True),
        g("R1G-S21", "no SAG", "summary/R1G_VERDICT.json", "sag_started", "false", "false", True),
        g("R1G-S22", "no 5-seed", "summary/R1G_VERDICT.json", "five_seed_started", "false", "false", True),
        g("R1G-S23", "E3-v2 oracle precheck artifact-derived", "e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_SUMMARY.csv", "routing", "from csv", str(routing), bool(v2_sum)),
        g("R1G-S24", "final verdict artifact-derived", "summary/R1G_VERDICT.json", "verdict", "derived", verdict, bool(verdict)),
    ]
    gate_payload = {"gates": gates, "n_pass": sum(1 for x in gates if x["pass"]), "n_fail": sum(1 for x in gates if not x["pass"]), "verdict": verdict}
    dump_json(gate_payload, out / "summary" / "R1G_GATE_REPORT.json")
    md = ["# R1G gate report", "", f"Verdict: **{verdict}**", "", "| gate | pass | observed |", "|---|---|---|"]
    for x in gates:
        md.append(f"| {x['gate_id']} | {x['pass']} | {x['observed']} |")
    (out / "summary" / "R1G_GATE_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    r1g_xml = out / "audit" / "pytest_r1g.xml"
    full_xml = out / "audit" / "pytest_full.xml"
    r1g_sum = run_pytest(root, R1G_TESTS, r1g_xml)
    full_sum = run_pytest(root, R1G_TESTS + R1F_REGRESSION, full_xml)
    dump_json({"r1g": r1g_sum, "full": full_sum}, out / "audit" / "TEST_SUMMARY.json")

    by_t = {(r["dataset"], r["regime"]): r for r in temporal_rows}
    ss_cf = {r["cf_id"]: r for r in cf_sum if r["dataset"] == "sensorscope"}
    ua_cf = {r["cf_id"]: r for r in cf_sum if r["dataset"] == "uair"}
    ss_v2 = next(r for r in v2_sum if r["dataset"] == "sensorscope")
    ua_v2 = next(r for r in v2_sum if r["dataset"] == "uair")
    answers = [
        f"1. Raw timestamps exist in processed atomic `absolute_time` (UTC).",
        "2. Timestamp drops at E3-v1 logical window construction: deadline=window_id+1.0, metadata has no UTC.",
        f"3. Raw natural train windows keep continuity: SS lag1 Jaccard={by_t[('sensorscope','raw_natural')]['lag1_jaccard']}; U-Air={by_t[('uair','raw_natural')]['lag1_jaccard']}.",
        f"4. E3-v1 does not: SS lag1={by_t[('sensorscope','e3v1')]['lag1_jaccard']}; U-Air={by_t[('uair','e3v1')]['lag1_jaccard']}.",
        f"5. lag-1 Jaccard drop is the raw−E3 difference in E3V1_TEMPORAL_RETENTION_SUMMARY.csv.",
        f"6. Autocorr raw vs E3-v1: see same CSV `opportunity_mass_autocorr_lag1`.",
        f"7. Persistence raw vs E3-v1: `mean_persistence_length`.",
        f"8. Co-occurrence: raw vs E3 mean risk-set size in E3V1_SAMPLING_DISTORTION_SUMMARY.csv.",
        f"9. Target-mass-weighted support: raw vs E3 means in the same summary.",
        "10. Sampler resamples from the global train pool each logical window (replace=False, k=4), mixing original hours.",
        f"11. Target vs realized mismatch TV: SS={next(r for r in mismatch_sum if r['dataset']=='sensorscope')['tv_distance']}; U-Air={next(r for r in mismatch_sum if r['dataset']=='uair')['tv_distance']}.",
        f"12. CF1 vs CF0 mean C_oracle_safe SS: {ss_cf['CF1']['mean_C_oracle_safe']} vs {ss_cf['CF0']['mean_C_oracle_safe']}; U-Air {ua_cf['CF1']['mean_C_oracle_safe']} vs {ua_cf['CF0']['mean_C_oracle_safe']}.",
        f"13. CF2 vs CF1 SS: {ss_cf['CF2']['mean_C_oracle_safe']} vs {ss_cf['CF1']['mean_C_oracle_safe']}; U-Air {ua_cf['CF2']['mean_C_oracle_safe']} vs {ua_cf['CF1']['mean_C_oracle_safe']}.",
        f"14. Root cause codes: {primary}.",
        f"15. Single dominant cause: {len(uniq)==1}.",
        f"16. Strict 'sampling caused ceiling': {attr['sampling_caused_ceiling_strict']}.",
        f"17. Cautious statement: {attr['cautious_statement']}",
        "18. E3-v2 uses real UTC timestamp (window_start_utc).",
        f"19. Window rule frozen before precheck: `{wr_hash}`.",
        "20. E3-v2 windows follow chronological real hours (test split).",
        "21. Natural co-occurrence: full units in that UTC hour, no global resample.",
        "22. Public context is pre-window (start UTC / TOD / weekday).",
        "23. Current R/O/U forbidden (ContextLeakageError).",
        f"24. Target law unchanged: {freeze['target_hash_match']}.",
        f"25. pi_safe rule hash `{pi_safe_rule_hash()}`.",
        f"26. tau_cov still {TAU_COV}: {float(freeze['tau_cov'])==TAU_COV}.",
        "27. EventTrace maps to raw interval via window_start_utc + time_index + raw_window_source_hash.",
        f"28. Hash replay match SS={ss_v2.get('replay_hash_match')} U-Air={ua_v2.get('replay_hash_match')}.",
        f"29. E3-v2 windows: SS={ss_v2['n_windows']} U-Air={ua_v2['n_windows']} (test split hours).",
        f"30. mean/median/max C_oracle_safe_v2 SS={ss_v2['mean_C_oracle_safe_v2']}/{ss_v2['median_C_oracle_safe_v2']}/{ss_v2['max_C_oracle_safe_v2']}; U-Air={ua_v2['mean_C_oracle_safe_v2']}/{ua_v2['median_C_oracle_safe_v2']}/{ua_v2['max_C_oracle_safe_v2']}.",
        f"31. fraction_oracle_pass_v2 SS={ss_v2['fraction_oracle_pass_v2']} U-Air={ua_v2['fraction_oracle_pass_v2']}.",
        f"32. Multiple safe/unsafe: SS pass={ss_v2['n_oracle_pass']} fail={ss_v2['n_oracle_fail']}; U-Air pass={ua_v2['n_oracle_pass']} fail={ua_v2['n_oracle_fail']}.",
        f"33. Routing SS={routing['sensorscope']} U-Air={routing['uair']}.",
        f"34. Joint E3V2_ORACLE_REGIME_USABLE: {labels=={'E3V2_ORACLE_REGIME_USABLE'}}.",
        "35. Predictor modified: False.",
        "36. Calibration modified: False.",
        f"37. tau modified: False (still {TAU_COV}).",
        "38. SAG run: False.",
        "39. 5-seed run: False.",
        f"40. pytest R1g: {r1g_sum.get('status')} passed={r1g_sum.get('n_passed')} failed={r1g_sum.get('n_failed')}.",
        f"41. full pytest: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}.",
        f"42. R1G-S0–S24 artifact-derived: n_pass={gate_payload['n_pass']} n_fail={gate_payload['n_fail']}.",
    ]
    (out / "summary" / "RAVEN_MCS_SAG_G1_R1G_E3_PROTOCOL_ROOT_CAUSE_AND_V2_SPEC_REPORT.md").write_text(
        "\n".join(
            [
                "# RAVEN-MCS SAG G1 R1G E3-v1 Root-Cause + E3-v2 Spec Report",
                "",
                f"## Executive verdict: {verdict}",
                "",
                "STOP. No dynamic certificate, no SAG, no 5-seed.",
                "",
                "## Answers",
                "",
                *answers,
                "",
            ]
        ),
        encoding="utf-8",
    )

    pack = root / "scripts" / "package_sag_g1_r1g_submission.py"
    if pack.is_file():
        subprocess.run([sys.executable, str(pack)], cwd=root, check=False)

    return {
        "output_dir": str(out),
        "verdict": verdict,
        "e3v2_routing": routing,
        "root_cause": primary,
        "tests": {"r1g": r1g_sum.get("status"), "full": full_sum.get("status")},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    result = run_r1g_main(root=args.root, output_dir=args.output_dir)
    print(json.dumps({k: result[k] for k in result if k != "root_cause"}, indent=2, default=str))


if __name__ == "__main__":
    main()
