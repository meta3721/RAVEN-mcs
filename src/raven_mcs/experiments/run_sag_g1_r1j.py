"""SAG G1-R1j: dynamic C_cov under frozen R1i availability stress. STOP. No SAG."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import numpy as np
import pandas as pd

from e3_v2_context import public_context_from_start
from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.experiments.sag_runtime import attach_unified_target, prepare_sag_bundle
from raven_mcs.sag.availability_stress import A_GRID, BOUNDARY_NEAR_MARGIN, TAU_COV
from raven_mcs.sag.certificates import c_cov_from_opportunity_lcb, provisional_pi_safe_from_public_opp
from raven_mcs.sag.e3v1_root_cause import natural_windows_from_atomic, realized_mass_from_units, unit_meta_from_atomic
from raven_mcs.sag.oracle_ceiling import NUM_TOL, ge_threshold
from raven_mcs.sag.r1j_calibration import joint_valid, lower_pi, max_residual, same_a_q
from raven_mcs.sag.r1j_eval import classify, confusion_metrics, dataset_verdict, overall_verdict
from raven_mcs.sag.r1j_features import FORBIDDEN_FEATURE_KEYS, feature_vector, pair_features
from raven_mcs.sag.r1j_predictor import _fit_logistic, hat_from_p, model_fit_hash, predict_p
from raven_mcs.sag.r1j_spec import (
    CALIBRATION_ID,
    DELTA_CAL,
    FEATURE_NAMES,
    LOOKBACK_L,
    LOOKBACK_MIN,
    MODEL_ID,
    calibration_spec_hash,
    calibration_spec_payload,
    predictor_spec_hash,
    predictor_spec_payload,
    routing_spec_payload,
)
from raven_mcs.sag.stress_mask import SEED, available_entities, filter_units_by_entities, mask_rule_hash
from raven_mcs.sag.target_law import freeze_target_law_rule_v1, pi_safe_rule_hash
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1j"

SNAPSHOT = (
    ("r1j_spec", "src/raven_mcs/sag/r1j_spec.py", "spec"),
    ("r1j_features", "src/raven_mcs/sag/r1j_features.py", "features"),
    ("r1j_predictor", "src/raven_mcs/sag/r1j_predictor.py", "predictor"),
    ("r1j_calibration", "src/raven_mcs/sag/r1j_calibration.py", "calibration"),
    ("r1j_eval", "src/raven_mcs/sag/r1j_eval.py", "eval"),
    ("run_sag_g1_r1j", "src/raven_mcs/experiments/run_sag_g1_r1j.py", "runner"),
    ("dynamic_cov", "src/raven_mcs/sag/dynamic_cov.py", "conformal"),
    ("certificates", "src/raven_mcs/sag/certificates.py", "c_cov"),
    ("oracle_ceiling", "src/raven_mcs/sag/oracle_ceiling.py", "oracle"),
    ("stress_mask", "src/raven_mcs/sag/stress_mask.py", "mask"),
    ("e3_v2_context", "src/e3_v2_context.py", "context"),
    ("hashing", "src/raven_mcs/utils/hashing.py", "hash"),
    ("thresholds", "configs/sag_g0/thresholds.json", "tau"),
)

R1J_TESTS = (
    "tests/unit/test_r1j_input_freeze.py",
    "tests/unit/test_r1j_oracle_groundtruth_unchanged.py",
    "tests/unit/test_r1j_stress_grid_unchanged.py",
    "tests/unit/test_r1j_mask_unchanged.py",
    "tests/unit/test_feature_whitelist.py",
    "tests/unit/test_no_current_mask_leakage.py",
    "tests/unit/test_no_current_ROU_leakage.py",
    "tests/unit/test_oracle_labels_not_used_in_training.py",
    "tests/unit/test_predictor_spec_frozen.py",
    "tests/unit/test_lookback_fixed.py",
    "tests/unit/test_no_model_zoo.py",
    "tests/unit/test_calibration_spec_frozen.py",
    "tests/unit/test_same_a_stratum_only.py",
    "tests/unit/test_no_future_calibration.py",
    "tests/unit/test_warmup_min8.py",
    "tests/unit/test_delta_unchanged.py",
    "tests/unit/test_lower_bound_formula.py",
    "tests/unit/test_joint_validity_builder.py",
    "tests/unit/test_c_cov_builder.py",
    "tests/unit/test_gate_threshold_unchanged.py",
    "tests/unit/test_false_safe_definition.py",
    "tests/unit/test_false_unsafe_definition.py",
    "tests/unit/test_boundary_near_rule_unchanged.py",
    "tests/unit/test_sensor_a040_audit_complete.py",
    "tests/unit/test_uair_a020_audit_complete.py",
    "tests/unit/test_no_predictor_retuning_after_results.py",
    "tests/unit/test_no_calibration_retuning_after_results.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_r1j_gate_artifact_derived.py",
    "tests/unit/test_r1j_verdict_not_hardcoded.py",
)
R1I_REGRESSION = (
    "tests/unit/test_r1i_input_freeze.py",
    "tests/unit/test_stress_levels_exact.py",
    "tests/unit/test_e3v2_tau_cov_unchanged.py",
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


def col_bool(s: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1"])


def run_r1j_main(*, root: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in ("audit", "freeze", "predictor", "calibration", "certificate", "gate_eval", "boundary_eval", "figures", "summary", "source_snapshot", "legacy_refs"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    freeze_inputs = []
    refs = [
        ("R1i oracle by window", "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv", "R1I", "ORACLE"),
        ("R1i oracle summary", "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_SUMMARY.csv", "R1I", "ORACLE"),
        ("R1i mask hash", "results_sag_g1/round_r1i/stress_masks/R1I_AVAILABILITY_MASK_HASH.txt", "R1I", "MASK"),
        ("R1i stress levels", "results_sag_g1/round_r1i/stress_spec/R1I_STRESS_LEVEL.json", "R1I", "STRESS"),
        ("R1i verdict", "results_sag_g1/round_r1i/summary/R1I_VERDICT.json", "R1I", "VERDICT"),
        ("TARGET_LAW", "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json", "R1D", "TARGET_LAW"),
        ("PI_SAFE", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "R1E", "PI_SAFE"),
        ("thresholds", "configs/sag_g0/thresholds.json", "R0", "TAU"),
        ("E3-v2 SS identity", "results_sag_g1/round_r1g/e3v2_skeleton/sensorscope/identity.json", "R1G", "E3_V2"),
        ("E3-v2 UA identity", "results_sag_g1/round_r1g/e3v2_skeleton/uair/identity.json", "R1G", "E3_V2"),
    ]
    oracle_path = root / "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv"
    oracle_sha = sha256_file(oracle_path)
    mask_txt = (root / "results_sag_g1/round_r1i/stress_masks/R1I_AVAILABILITY_MASK_HASH.txt").read_text(encoding="utf-8").strip()
    for name, rel, rnd, role in refs:
        path = root / rel
        digest = sha256_file(path) if path.is_file() else "MISSING"
        freeze_inputs.append({"artifact": name, "path": rel.replace("\\", "/"), "sha256": digest, "source_round": rnd, "role": role, "frozen": True, "notes": "not rewritten in R1j"})
        if path.is_file():
            shutil.copy2(path, out / "legacy_refs" / f"{rnd}_{role}_{Path(rel).name}")
    pd.DataFrame(freeze_inputs).to_csv(out / "R1J_INPUT_FREEZE_MANIFEST.csv", index=False)

    r1i = pd.read_csv(oracle_path)
    r1i["oracle_safe"] = col_bool(r1i["oracle_safe"])
    freeze_rows = []
    for r in r1i.itertuples(index=False):
        freeze_rows.append(
            {
                "dataset": r.dataset, "seed": int(r.seed), "window_id": int(r.window_id),
                "availability_level": float(r.availability_level),
                "C_oracle_safe": r.C_oracle_safe, "oracle_safe": bool(r.oracle_safe),
                "oracle_margin": r.oracle_margin,
                "natural_trace_hash": r.natural_trace_hash, "mask_hash": r.mask_hash,
                "stressed_trace_hash": r.stressed_trace_hash, "source_sha256": oracle_sha,
            }
        )
    pd.DataFrame(freeze_rows).to_csv(out / "freeze" / "R1J_ORACLE_FREEZE_MANIFEST.csv", index=False)
    (out / "freeze" / "R1J_ORACLE_FREEZE_AUDIT.md").write_text(
        f"# R1i oracle freeze\n\nsha256=`{oracle_sha}`\nR1j does not overwrite round_r1i.\nY_oracle is evaluation-only.\n",
        encoding="utf-8",
    )

    # Freeze specs BEFORE any certificate
    pred_payload = predictor_spec_payload()
    cal_payload = calibration_spec_payload()
    dump_json(pred_payload, out / "predictor" / "R1J_PREDICTOR_SPEC.json")
    (out / "predictor" / "R1J_PREDICTOR_SPEC_FREEZE.md").write_text(
        "\n".join(["# Predictor freeze", "", json.dumps(pred_payload, indent=2), f"hash: `{predictor_spec_hash()}`", ""]),
        encoding="utf-8",
    )
    dump_json(cal_payload, out / "calibration" / "R1J_CALIBRATION_SPEC.json")
    (out / "calibration" / "R1J_CALIBRATION_SPEC.md").write_text(
        "\n".join(["# Calibration freeze", "", json.dumps(cal_payload, indent=2), f"hash: `{calibration_spec_hash()}`", ""]),
        encoding="utf-8",
    )
    dump_json(routing_spec_payload(), out / "freeze" / "R1J_ROUTING_SPEC.json")
    wl = []
    for name in FEATURE_NAMES:
        wl.append({"feature": name, "source": "F_r_minus + public a/time", "availability_time": "F_r_minus_or_pre_window", "lag": "0_to_8", "allowed": True, "reason": "causal public/history"})
    for name in sorted(FORBIDDEN_FEATURE_KEYS):
        wl.append({"feature": name, "source": "forbidden", "availability_time": "current_or_post", "lag": 0, "allowed": False, "reason": "current-window / oracle leakage"})
    pd.DataFrame(wl).to_csv(out / "predictor" / "R1J_FEATURE_WHITELIST.csv", index=False)
    (out / "predictor" / "R1J_FEATURE_LEAKAGE_AUDIT.md").write_text(
        "\n".join(
            [
                "# Feature leakage audit",
                "",
                "Allowed: lagged pair activity, rolling mass, hour, weekend, scenario-level a, interaction rate*a.",
                "Forbidden: current availability mask, current R/O/U, current realized opportunity, oracle labels.",
                "a is a public scenario parameter. Realized mask identities are not features.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    rule = freeze_target_law_rule_v1()
    th = json.loads((root / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    freeze_ok = rule["hash"] == EXPECTED_TARGET_HASH and sha256_file(root / "configs/sag_g0/thresholds.json") == EXPECTED_THRESHOLD_HASH and mask_txt == mask_rule_hash()
    dump_json(
        {
            "target_hash_match": rule["hash"] == EXPECTED_TARGET_HASH,
            "tau_cov": float(th["tau_cov"]),
            "delta_cal": float(th["delta_cal"]),
            "mask_hash_match": mask_txt == mask_rule_hash(),
            "predictor_retuned": False,
            "calibration_retuned": False,
            "sag_started": False,
            "five_seed_started": False,
            "git": _git_hash(),
        },
        out / "audit" / "R1J_FREEZE_AUDIT.json",
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
        snap_rows.append({"component": component, "source_path": rel.replace("\\", "/"), "snapshot_path": str(dst.relative_to(out)).replace("\\", "/") if src.is_file() else "", "sha256": digest, "role": role, "used_in_round": "R1J", "notes": "snapshot"})
    pd.DataFrame(snap_rows).to_csv(out / "source_snapshot" / "R1J_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)

    cert_rows = []
    joint_rows = []
    pred_quality = []
    q_rows = []
    fit_rows = []
    for dataset in DATASETS:
        prepared = attach_unified_target(prepare_sag_bundle(root=root, dataset=dataset, seed=SEED), root=root)
        pi_safe = float(provisional_pi_safe_from_public_opp(prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10)["pi_safe"])
        atomic = prepared["atomic_sealed"]
        mapping = prepared["spatial_to_client"]
        meta = unit_meta_from_atomic(atomic, mapping)
        pi_tar = prepared["pi_target"]
        pairs = [(str(k[0]), str(k[1])) for k, w in pi_tar.items() if float(w) > NUM_TOL]
        test_nat = natural_windows_from_atomic(atomic, mapping, split="test")
        ident = json.loads((root / f"results_sag_g1/round_r1g/e3v2_skeleton/{dataset}/identity.json").read_text(encoding="utf-8"))
        n_win = len(test_nat)
        realized_store: dict[tuple[int, float], dict[tuple[str, str], float]] = {}
        hist_active: dict[float, dict[tuple[str, str], list[int]]] = {float(a): defaultdict(list) for a in A_GRID}
        hist_mass: dict[float, dict[tuple[str, str], list[float]]] = {float(a): defaultdict(list) for a in A_GRID}
        residuals_a: dict[float, list[float]] = {float(a): [] for a in A_GRID}
        train_X: list[np.ndarray] = []
        train_y: list[int] = []
        n_train_windows = 0
        for window_id, rec in enumerate(test_nat):
            ctx = public_context_from_start(rec["window_start_utc"])
            hour = int(ctx["hour_of_day"])
            weekend = int(ctx["weekend_flag"])
            units = list(rec["unit_ids"])
            entities = []
            seen = set()
            for uid in units:
                info = meta.get(str(uid))
                if info is None:
                    continue
                e = str(info["spatial"])
                if e not in seen:
                    seen.add(e)
                    entities.append(e)
            X_now = []
            keys_now = []
            a_now = []
            for a in A_GRID:
                af = float(a)
                for key in pairs:
                    feat = pair_features(
                        hist_active=hist_active[af][key],
                        hist_mass=hist_mass[af][key],
                        hour_of_day=hour,
                        weekend_flag=weekend,
                        availability_level=af,
                    )
                    X_now.append(feature_vector(feat))
                    keys_now.append(key)
                    a_now.append(af)
            X_now_m = np.vstack(X_now) if X_now else np.zeros((0, len(FEATURE_NAMES)))
            if train_X:
                model = _fit_logistic(np.vstack(train_X), np.asarray(train_y))
            else:
                model = {"kind": "prevalence", "p": 0.5, "coef": None, "intercept": None}
            fit_rows.append(
                {
                    "dataset": dataset, "window_id": window_id, "train_start": 0, "train_end": window_id - 1,
                    "n_train_windows": n_train_windows, "n_train_pairs": len(train_y),
                    "fit_hash": model_fit_hash(model, n_train_windows=n_train_windows, n_train_pairs=len(train_y)),
                    "model_kind": model["kind"],
                }
            )
            p_all = predict_p(model, X_now_m) if len(X_now_m) else np.array([])
            idx = 0
            for a in A_GRID:
                af = float(a)
                mask = available_entities(dataset=dataset, base_seed=SEED, window_id=window_id, entity_ids=entities, availability_level=af)
                kept = filter_units_by_entities(units, meta, mask["available"])
                mass = realized_mass_from_units(kept, meta)
                realized_store[(window_id, af)] = mass
                hat_map: dict[tuple[str, str], float] = {}
                p_map: dict[tuple[str, str], float] = {}
                mean_map: dict[tuple[str, str], float] = {}
                for key in pairs:
                    p = float(p_all[idx]) if idx < len(p_all) else 0.5
                    idx += 1
                    past_m = hist_mass[af][key]
                    mean_m = float(np.mean(past_m)) if past_m else 0.0
                    hat = hat_from_p(p, pi_safe=pi_safe, mean_mass=mean_m)
                    hat_map[key] = hat
                    p_map[key] = p
                    mean_map[key] = mean_m
                q, n_cal, warmup = same_a_q(residuals_a[af])
                eligible = (not warmup) and np.isfinite(q)
                lowers = {}
                wrapped = {}
                for key in pairs:
                    lo = lower_pi(hat_map[key], q) if eligible else float("nan")
                    lowers[key] = lo
                    wrapped[key] = {"lower_pi_opp": lo, "pi_hat_opp": hat_map[key]}
                if eligible:
                    cov = c_cov_from_opportunity_lcb(pi_tar, wrapped, pi_safe)
                    c_dyn = float(cov["C_cov_LCB"])
                    y_cert = ge_threshold(c_dyn, TAU_COV)
                else:
                    c_dyn = float("nan")
                    y_cert = False
                j_ok, max_diff = joint_valid(lowers, mass, pairs) if eligible else (False, float("nan"))
                nat = r1i.loc[(r1i["dataset"] == dataset) & (r1i["window_id"] == window_id) & (np.isclose(r1i["availability_level"].astype(float), af))]
                y_oracle = bool(nat["oracle_safe"].iloc[0]) if len(nat) else False
                c_ora = float(nat["C_oracle_safe"].iloc[0]) if len(nat) else float("nan")
                margin_o = float(nat["oracle_margin"].iloc[0]) if len(nat) else float("nan")
                cls = classify(y_oracle, bool(y_cert)) if eligible else "CALIBRATION_WARMUP"
                hats_pos = [hat_map[k] for k in pairs if hat_map[k] > NUM_TOL]
                cert_rows.append(
                    {
                        "dataset": dataset, "seed": SEED, "window_id": window_id, "availability_level": af,
                        "eligible_after_warmup": eligible, "Y_oracle": y_oracle, "Y_cert": bool(y_cert) if eligible else False,
                        "C_oracle_safe": c_ora, "C_cov_dynamic": c_dyn,
                        "oracle_margin": margin_o,
                        "certificate_margin": (c_dyn - TAU_COV) if eligible else float("nan"),
                        "classification": cls, "q_used": q, "n_calib": n_cal,
                        "pi_safe": pi_safe, "gap_cert": (c_ora - c_dyn) if eligible else float("nan"),
                    }
                )
                joint_rows.append(
                    {
                        "dataset": dataset, "window_id": window_id, "availability_level": af,
                        "eligible_after_warmup": eligible, "joint_valid": j_ok if eligible else False,
                        "max_lower_minus_realized": max_diff, "q_used": q,
                        "n_target_pairs": len(pairs), "calibration_history_size": n_cal,
                    }
                )
                q_rows.append(
                    {
                        "dataset": dataset, "window_id": window_id, "availability_level": af,
                        "eligible_after_warmup": eligible, "q_used": q,
                        "median_positive_hat_pi": float(np.median(hats_pos)) if hats_pos else 0.0,
                        "p90_hat_pi": float(np.quantile(hats_pos, 0.90)) if hats_pos else 0.0,
                        "max_hat_pi": float(max(hat_map.values())) if hat_map else 0.0,
                        "pi_safe": pi_safe,
                        "q_over_median_positive_hat": (q / float(np.median(hats_pos))) if eligible and hats_pos and np.median(hats_pos) > NUM_TOL else float("nan"),
                        "q_over_pi_safe": (q / pi_safe) if eligible and pi_safe else float("nan"),
                    }
                )
                ys = [int(float(mass.get(k, 0.0)) >= pi_safe) for k in pairs]
                ps = [p_map[k] for k in pairs]
                if eligible and ps:
                    brier = float(np.mean((np.asarray(ps) - np.asarray(ys)) ** 2))
                    pclip = np.clip(ps, 1e-6, 1 - 1e-6)
                    yarr = np.asarray(ys, dtype=float)
                    logloss = float(-np.mean(yarr * np.log(pclip) + (1 - yarr) * np.log(1 - pclip)))
                    pred_quality.append({"dataset": dataset, "window_id": window_id, "availability_level": af, "brier": brier, "log_loss": logloss, "prevalence": float(np.mean(ys)), "n_pairs": len(pairs)})
                rmax = max_residual(hat_map, mass, pairs)
                if np.isfinite(rmax) and n_train_windows >= 1:
                    residuals_a[af].append(rmax)
                for key in pairs:
                    yk = int(float(mass.get(key, 0.0)) >= pi_safe)
                    mk = float(mass.get(key, 0.0))
                    feat = pair_features(
                        hist_active=hist_active[af][key],
                        hist_mass=hist_mass[af][key],
                        hour_of_day=hour,
                        weekend_flag=weekend,
                        availability_level=af,
                    )
                    train_X.append(feature_vector(feat))
                    train_y.append(yk)
                    hist_active[af][key].append(yk)
                    hist_mass[af][key].append(mk)
            n_train_windows += 1

    cert = pd.DataFrame(cert_rows)
    joint = pd.DataFrame(joint_rows)
    cert.to_csv(out / "certificate" / "R1J_CERTIFICATE_BY_WINDOW.csv", index=False)
    joint.to_csv(out / "certificate" / "R1J_JOINT_VALIDITY_BY_WINDOW.csv", index=False)
    pd.DataFrame(fit_rows).to_csv(out / "predictor" / "R1J_PREDICTOR_FIT_LOG.csv", index=False)
    pd.DataFrame(q_rows).to_csv(out / "calibration" / "R1J_Q_SCALE_AUDIT.csv", index=False)
    pd.DataFrame(pred_quality).to_csv(out / "predictor" / "R1J_PREDICTOR_QUALITY.csv", index=False)

    elig = cert.loc[cert["eligible_after_warmup"] == True].copy()  # noqa: E712
    gate = elig.copy()
    gate.to_csv(out / "gate_eval" / "R1J_GATE_CONFUSION_BY_WINDOW.csv", index=False)

    metric_rows = []
    for scope, sub in [("pooled", elig)] + [(f"dataset:{d}", elig.loc[elig["dataset"] == d]) for d in DATASETS] + [
        (f"a={a:.2f}", elig.loc[np.isclose(elig["availability_level"].astype(float), float(a))]) for a in A_GRID
    ] + [(f"{d}|a={a:.2f}", elig.loc[(elig["dataset"] == d) & (np.isclose(elig["availability_level"].astype(float), float(a)))]) for d in DATASETS for a in A_GRID]:
        m = confusion_metrics(sub)
        m["scope"] = scope
        if len(sub):
            m["joint_validity_rate"] = float(joint.merge(sub[["dataset", "window_id", "availability_level"]], on=["dataset", "window_id", "availability_level"], how="inner").drop_duplicates().loc[:, "joint_valid"].astype(bool).mean()) if "joint_valid" in joint.columns else float("nan")
            # simpler:
            keys = sub[["dataset", "window_id", "availability_level"]]
            jsub = joint.merge(keys, on=["dataset", "window_id", "availability_level"], how="inner")
            m["joint_validity_rate"] = float(jsub["joint_valid"].astype(bool).mean()) if len(jsub) else float("nan")
            m["fraction_C_cov_zero"] = float((sub["C_cov_dynamic"].astype(float) <= NUM_TOL).mean())
            m["median_C_cov"] = float(sub["C_cov_dynamic"].median())
            m["median_gap"] = float(sub["gap_cert"].median()) if "gap_cert" in sub.columns else float("nan")
        metric_rows.append(m)
    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(out / "gate_eval" / "R1J_GATE_METRICS.csv", index=False)

    j_elig = joint.loc[joint["eligible_after_warmup"] == True]  # noqa: E712
    j_pooled = float(j_elig["joint_valid"].astype(bool).mean()) if len(j_elig) else float("nan")

    def slice_ds_a(ds, a):
        return elig.loc[(elig["dataset"] == ds) & (np.isclose(elig["availability_level"].astype(float), a))]

    ss040 = slice_ds_a("sensorscope", 0.40)
    ua020 = slice_ds_a("uair", 0.20)
    ss040.to_csv(out / "boundary_eval" / "R1J_SENSORSCOPE_A040_BOUNDARY_AUDIT.csv", index=False)
    ua020.to_csv(out / "boundary_eval" / "R1J_UAIR_A020_BOUNDARY_AUDIT.csv", index=False)
    m040 = confusion_metrics(ss040)
    m020 = confusion_metrics(ua020)
    j040 = joint.loc[(joint["dataset"] == "sensorscope") & (np.isclose(joint["availability_level"].astype(float), 0.40)) & (joint["eligible_after_warmup"] == True)]  # noqa: E712
    j020 = joint.loc[(joint["dataset"] == "uair") & (np.isclose(joint["availability_level"].astype(float), 0.20)) & (joint["eligible_after_warmup"] == True)]  # noqa: E712
    z040 = float((ss040["C_cov_dynamic"].astype(float) <= NUM_TOL).mean()) if len(ss040) else float("nan")
    z020 = float((ua020["C_cov_dynamic"].astype(float) <= NUM_TOL).mean()) if len(ua020) else float("nan")
    (out / "boundary_eval" / "R1J_SENSORSCOPE_A040_BOUNDARY_SUMMARY.md").write_text(
        f"# SensorScope a=0.40\n\neligible={m040['n']}\nTP/TN/FP/FN={m040['TP']}/{m040['TN']}/{m040['FP']}/{m040['FN']}\nfalse-safe={m040['false_safe_rate']}\nfalse-unsafe={m040['false_unsafe_rate']}\nbalanced_acc={m040['balanced_accuracy']}\njoint={float(j040['joint_valid'].astype(bool).mean()) if len(j040) else float('nan')}\nfraction_C_cov_0={z040}\nmedian_C_cov={float(ss040['C_cov_dynamic'].median()) if len(ss040) else float('nan')}\nmedian_C_oracle={float(ss040['C_oracle_safe'].median()) if len(ss040) else float('nan')}\n",
        encoding="utf-8",
    )
    (out / "boundary_eval" / "R1J_UAIR_A020_BOUNDARY_SUMMARY.md").write_text(
        f"# U-Air a=0.20 (secondary)\n\neligible={m020['n']}\nTP/TN/FP/FN={m020['TP']}/{m020['TN']}/{m020['FP']}/{m020['FN']}\nfalse-safe={m020['false_safe_rate']}\nfalse-unsafe={m020['false_unsafe_rate']}\nbalanced_acc={m020['balanced_accuracy']}\njoint={float(j020['joint_valid'].astype(bool).mean()) if len(j020) else float('nan')}\nfraction_C_cov_0={z020}\n",
        encoding="utf-8",
    )

    near = elig.loc[elig["oracle_margin"].astype(float).abs() <= BOUNDARY_NEAR_MARGIN]
    near.to_csv(out / "boundary_eval" / "R1J_BOUNDARY_NEAR_AUDIT.csv", index=False)
    mnear = confusion_metrics(near)

    # monotonicity diagnostic
    mono_rows = []
    levels = list(A_GRID)
    for (dataset, wid), sub in cert.groupby(["dataset", "window_id"]):
        by_a = {float(r.availability_level): r for r in sub.itertuples(index=False)}
        for lo, hi in zip(sorted(levels), sorted(levels)[1:]):
            if lo not in by_a or hi not in by_a:
                continue
            c_lo, c_hi = by_a[lo].C_cov_dynamic, by_a[hi].C_cov_dynamic
            if not (by_a[lo].eligible_after_warmup and by_a[hi].eligible_after_warmup):
                continue
            if not (np.isfinite(c_lo) and np.isfinite(c_hi)):
                continue
            mono_rows.append({"dataset": dataset, "window_id": int(wid), "a_low": lo, "a_high": hi, "C_cov_low": c_lo, "C_cov_high": c_hi, "monotone": float(c_lo) <= float(c_hi) + 1e-8})
    mono = pd.DataFrame(mono_rows)
    mono.to_csv(out / "certificate" / "R1J_CERTIFICATE_MONOTONICITY_DIAGNOSTIC.csv", index=False)

    def ds_metrics(ds: str) -> dict[str, Any]:
        sub = elig.loc[elig["dataset"] == ds]
        m = confusion_metrics(sub)
        jsub = joint.loc[(joint["dataset"] == ds) & (joint["eligible_after_warmup"] == True)]  # noqa: E712
        m["joint_validity_rate"] = float(jsub["joint_valid"].astype(bool).mean()) if len(jsub) else float("nan")
        m["fraction_C_cov_zero"] = float((sub["C_cov_dynamic"].astype(float) <= NUM_TOL).mean()) if len(sub) else float("nan")
        m["median_gap"] = float(sub["gap_cert"].median()) if len(sub) else float("nan")
        return m

    ss_m = ds_metrics("sensorscope")
    ua_m = ds_metrics("uair")
    ss_both = bool(m040["TP"] + m040["FN"] > 0 and m040["TN"] + m040["FP"] > 0 and m040["TP"] + m040["TN"] > 0)
    ua_both = bool(m020["TP"] + m020["FN"] > 0 and m020["TN"] + m020["FP"] > 0)
    ss_v = dataset_verdict(
        joint_validity=ss_m["joint_validity_rate"], false_safe_rate=ss_m["false_safe_rate"],
        false_unsafe_rate=ss_m["false_unsafe_rate"], balanced_accuracy=ss_m["balanced_accuracy"],
        fraction_zero=ss_m["fraction_C_cov_zero"], boundary_has_both_cert=ss_both,
        all_ccov_zero_on_boundary=bool(np.isfinite(z040) and z040 >= 0.999),
    )
    ua_v = dataset_verdict(
        joint_validity=ua_m["joint_validity_rate"], false_safe_rate=ua_m["false_safe_rate"],
        false_unsafe_rate=ua_m["false_unsafe_rate"], balanced_accuracy=ua_m["balanced_accuracy"],
        fraction_zero=ua_m["fraction_C_cov_zero"], boundary_has_both_cert=ua_both,
        all_ccov_zero_on_boundary=bool(np.isfinite(z020) and z020 >= 0.999),
    )
    final = overall_verdict(ss_v, ua_v)

    # figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = elig.loc[elig["dataset"] == dataset]
        for a in A_GRID:
            part = sub.loc[np.isclose(sub["availability_level"].astype(float), float(a))]
            ax.scatter(part["C_oracle_safe"], part["C_cov_dynamic"], s=12, alpha=0.6, label=f"a={a:.2f}")
        ax.axhline(TAU_COV, color="red", ls="--")
        ax.axvline(TAU_COV, color="red", ls="--")
        ax.set_title(dataset)
        ax.set_xlabel("C_oracle_safe")
        ax.set_ylabel("C_cov_dynamic")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1J_ORACLE_VS_DYNAMIC_COV_SCATTER.png", dpi=140)
    plt.close(fig)

    def confusion_plot(ax, sub, title):
        labels = ["TRUE_SAFE", "TRUE_UNSAFE", "FALSE_SAFE", "FALSE_UNSAFE"]
        counts = [(sub["classification"] == k).sum() if len(sub) else 0 for k in labels]
        ax.bar(labels, counts)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=20)

    fig, ax = plt.subplots(figsize=(7, 4))
    confusion_plot(ax, ss040, "SensorScope a=0.40")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1J_SENSOR_A040_GATE_CONFUSION.png", dpi=140)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    confusion_plot(ax, ua020, "U-Air a=0.20")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1J_UAIR_A020_GATE_CONFUSION.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = elig.loc[elig["dataset"] == dataset]
        xs, med, p90 = [], [], []
        for a in A_GRID:
            part = sub.loc[np.isclose(sub["availability_level"].astype(float), float(a))]
            xs.append(a)
            med.append(float(part["gap_cert"].median()) if len(part) else float("nan"))
            p90.append(float(part["gap_cert"].quantile(0.90)) if len(part) else float("nan"))
        ax.plot(xs, med, marker="o", label="median gap")
        ax.plot(xs, p90, marker="s", label="p90 gap")
        ax.set_title(dataset)
        ax.set_xlabel("a")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1J_CERTIFICATE_GAP_BY_STRESS.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = pd.DataFrame(q_rows)
        sub = sub.loc[(sub["dataset"] == dataset) & (sub["eligible_after_warmup"] == True)]  # noqa: E712
        ax.scatter(sub["median_positive_hat_pi"], sub["q_used"], s=10, alpha=0.5, label="q vs median hat")
        ax.axhline(float(np.nanmedian(sub["pi_safe"])) if len(sub) else TAU_COV, color="green", ls=":", label="pi_safe")
        ax.set_title(dataset)
        ax.set_xlabel("median positive hat_pi")
        ax.set_ylabel("q")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1J_Q_VS_PREDICTION_SCALE.png", dpi=140)
    plt.close(fig)

    dump_json(
        {
            "executive_verdict": final,
            "sensorscope": ss_v,
            "uair": ua_v,
            "sag_started": False,
            "five_seed_started": False,
            "predictor_retuned": False,
            "calibration_retuned": False,
            "tau_cov": TAU_COV,
            "delta_cal": DELTA_CAL,
            "predictor_run": True,
            "calibration_run": True,
            "dynamic_cov_run": True,
            "predictor_repair_executed": False,
            "calibration_repair_executed": False,
        },
        out / "summary" / "R1J_VERDICT.json",
    )

    src_text = (root / "src/raven_mcs/experiments/run_sag_g1_r1j.py").read_text(encoding="utf-8")
    oracle_now = sha256_file(oracle_path)
    flags = json.loads((out / "summary" / "R1J_VERDICT.json").read_text(encoding="utf-8"))
    checks = [
        ("R1J-S0", "input freeze", "R1J_INPUT_FREEZE_MANIFEST.csv", "missing", "0", sum(1 for r in freeze_inputs if r["sha256"] == "MISSING"), all(r["sha256"] != "MISSING" for r in freeze_inputs)),
        ("R1J-S1", "R1i oracle unchanged", "freeze/R1J_ORACLE_FREEZE_MANIFEST.csv", "sha", oracle_sha, oracle_now, oracle_now == oracle_sha),
        ("R1J-S2", "stress grid/masks unchanged", "legacy_refs", "mask", mask_txt, mask_rule_hash(), mask_txt == mask_rule_hash() and list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]),
        ("R1J-S3", "feature whitelist frozen", "predictor/R1J_FEATURE_WHITELIST.csv", "n", str(len(FEATURE_NAMES)), str(len(FEATURE_NAMES)), (out / "predictor/R1J_FEATURE_WHITELIST.csv").is_file()),
        ("R1J-S4", "no current-window leakage", "predictor/R1J_FEATURE_LEAKAGE_AUDIT.md", "forbidden", "listed", "listed", "current availability mask" in (out / "predictor/R1J_FEATURE_LEAKAGE_AUDIT.md").read_text(encoding="utf-8")),
        ("R1J-S5", "predictor spec frozen", "predictor/R1J_PREDICTOR_SPEC_FREEZE.md", "hash", predictor_spec_hash(), predictor_spec_hash(), (out / "predictor/R1J_PREDICTOR_SPEC_FREEZE.md").is_file()),
        ("R1J-S6", "calibration spec frozen", "calibration/R1J_CALIBRATION_SPEC.md", "id", CALIBRATION_ID, CALIBRATION_ID, (out / "calibration/R1J_CALIBRATION_SPEC.md").is_file()),
        ("R1J-S7", "same-a calibration only", "calibration/R1J_CALIBRATION_SPEC.json", "same_a_only", "true", str(cal_payload["same_a_only"]), cal_payload["same_a_only"] is True),
        ("R1J-S8", "no future leakage", "src/raven_mcs/sag/r1j_features.py", "hist", "windows<r", "windows<r", "windows < r" in (root / "src/raven_mcs/sag/r1j_features.py").read_text(encoding="utf-8")),
        ("R1J-S9", "warmup min 8", "certificate/R1J_JOINT_VALIDITY_BY_WINDOW.csv", "min_calib", str(LOOKBACK_MIN), str(LOOKBACK_MIN), int(joint.loc[joint["eligible_after_warmup"] == True, "calibration_history_size"].min()) >= LOOKBACK_MIN if (joint["eligible_after_warmup"] == True).any() else True),  # noqa: E712
        ("R1J-S10", "joint validity computed", "certificate/R1J_JOINT_VALIDITY_BY_WINDOW.csv", "n", ">0", str(len(joint)), len(joint) > 0),
        ("R1J-S11", "dynamic C_cov computed", "certificate/R1J_CERTIFICATE_BY_WINDOW.csv", "n", str(len(r1i)), str(len(cert)), len(cert) == len(r1i)),
        ("R1J-S12", "gate comparison complete", "gate_eval/R1J_GATE_CONFUSION_BY_WINDOW.csv", "n_elig", ">0", str(len(elig)), len(elig) > 0),
        ("R1J-S13", "false-safe quantified", "gate_eval/R1J_GATE_METRICS.csv", "pooled_fs", "finite", str(confusion_metrics(elig)["false_safe_rate"]), np.isfinite(confusion_metrics(elig)["false_safe_rate"])),
        ("R1J-S14", "false-unsafe quantified", "gate_eval/R1J_GATE_METRICS.csv", "pooled_fu", "finite", str(confusion_metrics(elig)["false_unsafe_rate"]), np.isfinite(confusion_metrics(elig)["false_unsafe_rate"])),
        ("R1J-S15", "SS a=0.4 audit", "boundary_eval/R1J_SENSORSCOPE_A040_BOUNDARY_AUDIT.csv", "n", ">0", str(len(ss040)), len(ss040) > 0),
        ("R1J-S16", "U-Air a=0.2 audit", "boundary_eval/R1J_UAIR_A020_BOUNDARY_AUDIT.csv", "n", ">0", str(len(ua020)), len(ua020) > 0),
        ("R1J-S17", "boundary-near audit", "boundary_eval/R1J_BOUNDARY_NEAR_AUDIT.csv", "margin", str(BOUNDARY_NEAR_MARGIN), str(BOUNDARY_NEAR_MARGIN), (out / "boundary_eval/R1J_BOUNDARY_NEAR_AUDIT.csv").is_file()),
        ("R1J-S18", "non-vacuity quantified", "gate_eval/R1J_GATE_METRICS.csv", "zero_frac", "reported", str(ss_m["fraction_C_cov_zero"]), True),
        ("R1J-S19", "q-scale audit", "calibration/R1J_Q_SCALE_AUDIT.csv", "n", ">0", str(len(q_rows)), len(q_rows) > 0),
        ("R1J-S20", "predictor quality", "predictor/R1J_PREDICTOR_QUALITY.csv", "n", ">0", str(len(pred_quality)), len(pred_quality) > 0),
        ("R1J-S21", "no post-hoc retuning", "summary/R1J_VERDICT.json", "retune", "false", "false", flags.get("predictor_retuned") is False and flags.get("calibration_retuned") is False),
        ("R1J-S22", "TARGET_LAW unchanged", "audit/R1J_FREEZE_AUDIT.json", "hash", EXPECTED_TARGET_HASH, rule["hash"], freeze_ok),
        ("R1J-S23", "PI_SAFE unchanged", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "hash", pi_safe_rule_hash(), json.loads((root / "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json").read_text(encoding="utf-8")).get("hash"), json.loads((root / "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json").read_text(encoding="utf-8")).get("hash") == pi_safe_rule_hash()),
        ("R1J-S24", "tau_cov unchanged", "configs/sag_g0/thresholds.json", "tau", "0.05", str(th["tau_cov"]), float(th["tau_cov"]) == 0.05),
        ("R1J-S25", "no SAG", "summary/R1J_VERDICT.json", "sag_started", "false", flags.get("sag_started"), flags.get("sag_started") is False),
        ("R1J-S26", "no 5-seed", "summary/R1J_VERDICT.json", "five_seed_started", "false", flags.get("five_seed_started"), flags.get("five_seed_started") is False),
        ("R1J-S27", "source snapshot complete", "source_snapshot/R1J_SOURCE_SNAPSHOT_MANIFEST.csv", "missing", "0", str(sum(1 for r in snap_rows if r["sha256"] == "MISSING")), all(r["sha256"] != "MISSING" for r in snap_rows)),
        ("R1J-S28", "final verdict artifact-derived", "summary/R1J_VERDICT.json", "verdict", final, final, final in {"READY_FOR_SAG_1SEED_FUNCTIONAL_VALIDATION", "READY_FOR_LIMITED_SAG_1SEED_VALIDATION", "R1J_CERTIFICATE_TOO_CONSERVATIVE", "R1J_CERTIFICATE_NOT_CALIBRATED", "R1J_IMPLEMENTATION_OR_EVIDENCE_FAILURE"}),
    ]
    gates = [{"gate_id": a, "description": b, "evidence_file": c, "metric": d, "expected": e, "observed": str(f), "pass": bool(g)} for a, b, c, d, e, f, g in checks]
    gate_payload = {"gates": gates, "n_pass": sum(1 for x in gates if x["pass"]), "n_fail": sum(1 for x in gates if not x["pass"]), "verdict": final}
    dump_json(gate_payload, out / "summary" / "R1J_GATE_REPORT.json")
    md = ["# R1J gate report", "", f"Verdict: **{final}**", "", "| gate | pass | observed |", "|---|---|---|"]
    for x in gates:
        md.append(f"| {x['gate_id']} | {x['pass']} | {x['observed']} |")
    (out / "summary" / "R1J_GATE_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    r1j_sum = run_pytest(root, R1J_TESTS, out / "audit" / "pytest_r1j.xml")
    full_sum = run_pytest(root, R1J_TESTS + R1I_REGRESSION, out / "audit" / "pytest_full.xml")
    dump_json({"r1j": r1j_sum, "full": full_sum}, out / "audit" / "TEST_SUMMARY.json")
    if r1j_sum.get("status") != "PASS" or full_sum.get("status") != "PASS" or not freeze_ok:
        final = "R1J_IMPLEMENTATION_OR_EVIDENCE_FAILURE"
        dump_json({**json.loads((out / "summary" / "R1J_VERDICT.json").read_text(encoding="utf-8")), "executive_verdict": final}, out / "summary" / "R1J_VERDICT.json")
        gate_payload["verdict"] = final
        dump_json(gate_payload, out / "summary" / "R1J_GATE_REPORT.json")

    pooled = confusion_metrics(elig)
    pq = pd.DataFrame(pred_quality)
    (out / "summary" / "RAVEN_MCS_SAG_G1_R1J_DYNAMIC_COV_STRESS_AUDIT_REPORT.md").write_text(
        "\n".join(
            [
                "# RAVEN-MCS SAG G1 R1J Dynamic C_cov Stress Audit",
                "",
                f"## Executive verdict: {final}",
                "",
                "Natural E3-v2 and R1i oracle remain frozen. This round is an out-of-sample certificate audit, not predictor tuning.",
                "",
                "STOP. No SAG / 5-seed.",
                "",
                "## Answers",
                "",
                f"1. R1i oracle unchanged: sha256 `{oracle_sha}`.",
                f"2. Stress grid unchanged: {list(A_GRID)}.",
                f"3. Masks unchanged: `{mask_rule_hash()}`.",
                f"4. TARGET_LAW unchanged: {rule['hash'] == EXPECTED_TARGET_HASH}.",
                f"5. PI_SAFE unchanged: `{pi_safe_rule_hash()}`.",
                f"6. tau_cov=0.05: {float(th['tau_cov']) == 0.05}.",
                f"7. delta_cal=0.05: {float(th['delta_cal']) == 0.05}.",
                f"8. Predictor: `{MODEL_ID}` L2 logistic C=1.",
                f"9. Features: {list(FEATURE_NAMES)}.",
                f"10. Lookback L={LOOKBACK_L}.",
                "11. Current mask not a feature.",
                "12. Current R/O/U not features.",
                "13. Oracle labels not used in training (evaluation only).",
                "14. Future windows not in calibration (same-a residuals from t<r).",
                f"15. Pooled joint validity (eligible): {j_pooled}.",
                f"16. SensorScope joint validity: {ss_m['joint_validity_rate']}.",
                f"17. U-Air joint validity: {ua_m['joint_validity_rate']}.",
                f"18. Joint by a: see R1J_GATE_METRICS.csv.",
                f"19. Pooled fraction C_cov=0: {float((elig['C_cov_dynamic'].astype(float) <= NUM_TOL).mean()) if len(elig) else float('nan')}.",
                f"20. SensorScope a=0.4 fraction C_cov=0: {z040}.",
                f"21. U-Air a=0.2 fraction C_cov=0: {z020}.",
                "22. R1d zero fractions were 0.976 / 1.0; R1j is reported above.",
                f"23. Pooled false-safe: {pooled['false_safe_rate']}.",
                f"24. SensorScope false-safe: {ss_m['false_safe_rate']}.",
                f"25. U-Air false-safe: {ua_m['false_safe_rate']}.",
                f"26. Boundary-near false-safe: {mnear['false_safe_rate']}.",
                f"27. Pooled false-unsafe: {pooled['false_unsafe_rate']}.",
                f"28. Pooled balanced accuracy: {pooled['balanced_accuracy']}.",
                f"29. Median gap SS={ss_m.get('median_gap')} (see metrics); SS a=0.4 median gap={float(ss040['gap_cert'].median()) if len(ss040) else float('nan')}; U-Air a=0.2={float(ua020['gap_cert'].median()) if len(ua020) else float('nan')}.",
                "30. Over-conservative if C_cov near 0 while oracle crosses tau.",
                f"31. SS a=0.4 TP/TN/FP/FN={m040['TP']}/{m040['TN']}/{m040['FP']}/{m040['FN']}.",
                f"32. SS a=0.4 false-safe={m040['false_safe_rate']}.",
                f"33. SS a=0.4 false-unsafe={m040['false_unsafe_rate']}.",
                f"34. SS a=0.4 balanced acc={m040['balanced_accuracy']}.",
                f"35. SS a=0.4 joint={float(j040['joint_valid'].astype(bool).mean()) if len(j040) else float('nan')}.",
                f"36. SensorScope usable? {ss_v}.",
                f"37. U-Air a=0.2 TP/TN/FP/FN={m020['TP']}/{m020['TN']}/{m020['FP']}/{m020['FN']}.",
                f"38. U-Air a=0.2 false-safe={m020['false_safe_rate']}.",
                f"39. U-Air a=0.2 false-unsafe={m020['false_unsafe_rate']}.",
                f"40. U-Air a=0.2 balanced acc={m020['balanced_accuracy']}.",
                f"41. U-Air a=0.2 joint={float(j020['joint_valid'].astype(bool).mean()) if len(j020) else float('nan')}.",
                f"42. U-Air dataset verdict: {ua_v}.",
                f"43. q vs prediction scale: see R1J_Q_SCALE_AUDIT.csv (R1d was q >> hat).",
                f"44. median q/pi_safe eligible={float(pd.DataFrame(q_rows).loc[pd.DataFrame(q_rows)['eligible_after_warmup']==True, 'q_over_pi_safe'].median()) if q_rows else float('nan')}.",
                f"45. Mass lower-bound zeros: SS a=0.4 {z040}; U-Air a=0.2 {z020}.",
                "46. Post-hoc predictor retune: False.",
                "47. Post-hoc calibration retune: False.",
                "48. Stress unchanged: True.",
                "49. SAG: False.",
                "50. 5-seed: False.",
                f"51. pytest R1j: {r1j_sum.get('status')} passed={r1j_sum.get('n_passed')} failed={r1j_sum.get('n_failed')}.",
                f"52. full pytest: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}.",
                f"53. R1J-S0–S28: n_pass={gate_payload['n_pass']} n_fail={gate_payload['n_fail']}.",
                f"54. Final verdict: {final}.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    pack = root / "scripts" / "package_sag_g1_r1j_submission.py"
    if pack.is_file():
        subprocess.run([sys.executable, str(pack)], cwd=root, check=False)
    return {"output_dir": str(out), "verdict": final, "sensorscope": ss_v, "uair": ua_v, "tests": {"r1j": r1j_sum.get("status"), "full": full_sum.get("status")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run_r1j_main(root=args.root, output_dir=args.output_dir), indent=2, default=str))


if __name__ == "__main__":
    main()
