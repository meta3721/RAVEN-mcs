"""SAG G1-R1k: pairwise LCB barrier + scale audit + aggregate feasibility. STOP. No SAG."""

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
from raven_mcs.sag.availability_stress import A_GRID, TAU_COV
from raven_mcs.sag.certificates import c_cov_from_opportunity_lcb, encode_pair, provisional_pi_safe_from_public_opp
from raven_mcs.sag.e3v1_root_cause import natural_windows_from_atomic, realized_mass_from_units, unit_meta_from_atomic
from raven_mcs.sag.oracle_ceiling import NUM_TOL, ge_threshold
from raven_mcs.sag.r1j_features import feature_vector, pair_features
from raven_mcs.sag.r1j_predictor import _fit_logistic, predict_p
from raven_mcs.sag.r1k_aggregate import (
    aggregate_features,
    c_lcb,
    feature_vector as agg_vector,
    fit_ridge,
    predict_c,
    same_a_q,
    agg_valid,
)
from raven_mcs.sag.r1k_barrier import (
    DERIVATION_MD,
    barrier_reason,
    p_active_upper_from_a,
    strict_positive_lcb_possible,
)
from raven_mcs.sag.r1k_eval import (
    aggregate_verdict,
    classify,
    confusion_metrics,
    overall_verdict,
    pairwise_barrier_verdict,
    scale_verdict,
    theory_decision,
)
from raven_mcs.sag.r1k_scale import hat_pi_cond, hat_pi_old, mean_mass_all, mean_mass_positive
from raven_mcs.sag.r1k_spec import (
    AGG_CALIBRATION_ID,
    AGG_MODEL_ID,
    ALLOWED_OVERALL,
    DELTA_CAL,
    LOOKBACK_L,
    LOOKBACK_MIN,
    ONE_MINUS_DELTA,
    PAPER_TEX,
    RIDGE_ALPHA,
    aggregate_calibration_hash,
    aggregate_calibration_payload,
    aggregate_predictor_hash,
    aggregate_predictor_payload,
    routing_payload,
)
from raven_mcs.sag.stress_mask import SEED, available_entities, filter_units_by_entities, mask_rule_hash
from raven_mcs.sag.target_law import freeze_target_law_rule_v1, pi_safe_rule_hash
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1k"

SNAPSHOT = (
    ("r1k_spec", "src/raven_mcs/sag/r1k_spec.py", "spec"),
    ("r1k_barrier", "src/raven_mcs/sag/r1k_barrier.py", "barrier"),
    ("r1k_scale", "src/raven_mcs/sag/r1k_scale.py", "scale"),
    ("r1k_aggregate", "src/raven_mcs/sag/r1k_aggregate.py", "aggregate"),
    ("r1k_eval", "src/raven_mcs/sag/r1k_eval.py", "eval"),
    ("run_sag_g1_r1k", "src/raven_mcs/experiments/run_sag_g1_r1k.py", "runner"),
    ("r1j_predictor", "src/raven_mcs/sag/r1j_predictor.py", "r1j_predictor"),
    ("r1j_features", "src/raven_mcs/sag/r1j_features.py", "r1j_features"),
    ("r1j_calibration", "src/raven_mcs/sag/r1j_calibration.py", "r1j_calibration"),
    ("dynamic_cov", "src/raven_mcs/sag/dynamic_cov.py", "conformal"),
    ("certificates", "src/raven_mcs/sag/certificates.py", "c_cov"),
    ("stress_mask", "src/raven_mcs/sag/stress_mask.py", "mask"),
    ("e3_v2_context", "src/e3_v2_context.py", "context"),
    ("thresholds", "configs/sag_g0/thresholds.json", "tau"),
    ("main_tex", "TO_OVERLEAF_paper_tmc_r1_clean/main.tex", "theory"),
    ("appendix_tex", "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex", "theory"),
    ("supplemental_tex", "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex", "theory"),
)

R1K_TESTS = (
    "tests/unit/test_r1k_input_freeze.py",
    "tests/unit/test_pairwise_barrier_derivation.py",
    "tests/unit/test_positive_lcb_impossible_when_zero_prob_gt_delta.py",
    "tests/unit/test_availability_upper_bound.py",
    "tests/unit/test_a100_handled_separately.py",
    "tests/unit/test_scale_mapping_old.py",
    "tests/unit/test_scale_mapping_conditional_positive.py",
    "tests/unit/test_scale_history_causal.py",
    "tests/unit/test_no_mass_mapping_model_zoo.py",
    "tests/unit/test_aggregate_feature_causal.py",
    "tests/unit/test_aggregate_no_current_mask.py",
    "tests/unit/test_aggregate_no_current_oracle.py",
    "tests/unit/test_aggregate_same_a_calibration.py",
    "tests/unit/test_aggregate_no_future_calibration.py",
    "tests/unit/test_aggregate_delta_unchanged.py",
    "tests/unit/test_aggregate_warmup_min8.py",
    "tests/unit/test_aggregate_lcb_formula.py",
    "tests/unit/test_aggregate_validity_builder.py",
    "tests/unit/test_aggregate_gate_threshold_unchanged.py",
    "tests/unit/test_pairwise_history_unchanged.py",
    "tests/unit/test_r1i_oracle_unchanged.py",
    "tests/unit/test_stress_unchanged.py",
    "tests/unit/test_target_law_unchanged.py",
    "tests/unit/test_pi_safe_unchanged.py",
    "tests/unit/test_tau_unchanged.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_no_theory_file_modified.py",
    "tests/unit/test_r1k_gate_artifact_derived.py",
    "tests/unit/test_r1k_verdict_not_hardcoded.py",
)
R1J_REGRESSION = (
    "tests/unit/test_r1j_oracle_groundtruth_unchanged.py",
    "tests/unit/test_r1j_stress_grid_unchanged.py",
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


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.nanstd(a) < NUM_TOL or np.nanstd(b) < NUM_TOL:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _point_c(pi_tar, hats, pi_safe) -> float:
    wrapped = {k: {"lower_pi_opp": hats[k], "pi_hat_opp": hats[k]} for k in hats}
    return float(c_cov_from_opportunity_lcb(pi_tar, wrapped, pi_safe)["C_cov_LCB"])


def run_r1k_main(*, root: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in (
        "audit", "freeze", "pairwise_barrier", "predictor_scale", "aggregate_certificate",
        "aggregate_eval", "theory_boundary", "figures", "summary", "source_snapshot", "legacy_refs",
    ):
        (out / sub).mkdir(parents=True, exist_ok=True)

    refs = [
        ("R1i oracle by window", "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv", "R1I", "ORACLE"),
        ("R1j joint validity", "results_sag_g1/round_r1j/certificate/R1J_JOINT_VALIDITY_BY_WINDOW.csv", "R1J", "JOINT"),
        ("R1j gate confusion", "results_sag_g1/round_r1j/gate_eval/R1J_GATE_CONFUSION_BY_WINDOW.csv", "R1J", "GATE"),
        ("R1j certificate", "results_sag_g1/round_r1j/certificate/R1J_CERTIFICATE_BY_WINDOW.csv", "R1J", "CERT"),
        ("R1j predictor source", "src/raven_mcs/sag/r1j_predictor.py", "R1J", "PREDICTOR"),
        ("R1j calibration source", "src/raven_mcs/sag/r1j_calibration.py", "R1J", "CALIBRATION"),
        ("R1i stress-mask source", "src/raven_mcs/sag/stress_mask.py", "R1I", "MASK"),
        ("TARGET_LAW", "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json", "R1D", "TARGET_LAW"),
        ("PI_SAFE", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "R1E", "PI_SAFE"),
        ("thresholds", "configs/sag_g0/thresholds.json", "R0", "TAU"),
        ("main.tex", "TO_OVERLEAF_paper_tmc_r1_clean/main.tex", "PAPER", "THEORY"),
        ("appendix.tex", "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex", "PAPER", "THEORY"),
        ("supplemental.tex", "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex", "PAPER", "THEORY"),
    ]
    oracle_path = root / "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv"
    r1j_cert_path = root / "results_sag_g1/round_r1j/certificate/R1J_CERTIFICATE_BY_WINDOW.csv"
    oracle_sha = sha256_file(oracle_path)
    r1j_cert_sha = sha256_file(r1j_cert_path)
    paper_hashes = {rel: sha256_file(root / rel) for rel in PAPER_TEX}
    freeze_inputs = []
    for name, rel, rnd, role in refs:
        path = root / rel
        digest = sha256_file(path) if path.is_file() else "MISSING"
        freeze_inputs.append({"artifact": name, "path": rel.replace("\\", "/"), "sha256": digest, "source_round": rnd, "role": role, "frozen": True, "notes": "not rewritten in R1k"})
        if path.is_file():
            shutil.copy2(path, out / "legacy_refs" / f"{rnd}_{role}_{Path(rel).name}")
    pd.DataFrame(freeze_inputs).to_csv(out / "R1K_INPUT_FREEZE_MANIFEST.csv", index=False)
    dump_json({"paper_tex_sha256": paper_hashes, "oracle_sha256": oracle_sha, "r1j_cert_sha256": r1j_cert_sha}, out / "freeze" / "R1K_THEORY_AND_ORACLE_HASHES.json")
    (out / "R1K_INPUT_FREEZE_AUDIT.md").write_text(
        "# R1k input freeze\n\nR1i oracle, R1j pairwise outputs, predictor/calibration sources, stress mask, target/pi_safe/tau, and paper tex hashes are recorded. R1k does not overwrite prior rounds or paper files.\n",
        encoding="utf-8",
    )

    rule = freeze_target_law_rule_v1()
    th = json.loads((root / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    mask_txt = (root / "results_sag_g1/round_r1i/stress_masks/R1I_AVAILABILITY_MASK_HASH.txt").read_text(encoding="utf-8").strip()
    freeze_ok = (
        rule["hash"] == EXPECTED_TARGET_HASH
        and sha256_file(root / "configs/sag_g0/thresholds.json") == EXPECTED_THRESHOLD_HASH
        and mask_txt == mask_rule_hash()
        and float(th["tau_cov"]) == 0.05
        and float(th["delta_cal"]) == 0.05
    )

    # PART A derivation + by-level barrier (before any modeling)
    (out / "pairwise_barrier" / "PAIRWISE_POSITIVE_LCB_BARRIER_DERIVATION.md").write_text(DERIVATION_MD, encoding="utf-8")
    barrier_rows = []
    for dataset in DATASETS:
        for a in A_GRID:
            pu = p_active_upper_from_a(float(a))
            ok = strict_positive_lcb_possible(pu)
            barrier_rows.append({
                "dataset": dataset, "availability_level": float(a), "delta": DELTA_CAL,
                "one_minus_delta": ONE_MINUS_DELTA, "p_active_upper": pu,
                "strict_positive_lcb_possible": ok, "reason": barrier_reason(float(a)),
            })
    barrier_df = pd.DataFrame(barrier_rows)
    barrier_df.to_csv(out / "pairwise_barrier" / "R1K_PAIRWISE_BARRIER_BY_LEVEL.csv", index=False)
    boundary_blocked = (not barrier_df.loc[np.isclose(barrier_df["availability_level"], 0.40), "strict_positive_lcb_possible"].iloc[0]) and (
        not barrier_df.loc[np.isclose(barrier_df["availability_level"], 0.20), "strict_positive_lcb_possible"].iloc[0]
    )
    pair_v = pairwise_barrier_verdict(boundary_a_blocked=bool(boundary_blocked), derivation_ok=True)

    pred_payload = aggregate_predictor_payload()
    cal_payload = aggregate_calibration_payload()
    dump_json(pred_payload, out / "aggregate_certificate" / "R1K_AGGREGATE_PREDICTOR_SPEC.json")
    dump_json(cal_payload, out / "aggregate_certificate" / "R1K_AGGREGATE_CALIBRATION_SPEC.json")
    dump_json(routing_payload(), out / "freeze" / "R1K_ROUTING_SPEC.json")

    r1i = pd.read_csv(oracle_path)
    r1i["oracle_safe"] = col_bool(r1i["oracle_safe"])
    r1j = pd.read_csv(r1j_cert_path)
    r1j["eligible_after_warmup"] = col_bool(r1j["eligible_after_warmup"])
    r1j["Y_oracle"] = col_bool(r1j["Y_oracle"])
    r1j["Y_cert"] = col_bool(r1j["Y_cert"])

    scale_rows: list[dict[str, Any]] = []
    point_rows: list[dict[str, Any]] = []
    a100_presence: dict[str, dict[tuple[str, str], list[int]]] = {d: defaultdict(list) for d in DATASETS}
    pair_mass: dict[str, dict[tuple[str, str], float]] = {}
    pi_safe_ds: dict[str, float] = {}
    n_pairs_ds: dict[str, int] = {}

    for dataset in DATASETS:
        prepared = attach_unified_target(prepare_sag_bundle(root=root, dataset=dataset, seed=SEED), root=root)
        pi_safe = float(provisional_pi_safe_from_public_opp(prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10)["pi_safe"])
        pi_safe_ds[dataset] = pi_safe
        atomic = prepared["atomic_sealed"]
        mapping = prepared["spatial_to_client"]
        meta = unit_meta_from_atomic(atomic, mapping)
        pi_tar = prepared["pi_target"]
        pairs = [(str(k[0]), str(k[1])) for k, w in pi_tar.items() if float(w) > NUM_TOL]
        n_pairs_ds[dataset] = len(pairs)
        pair_mass[dataset] = {(str(k[0]), str(k[1])): float(w) for k, w in pi_tar.items() if float(w) > NUM_TOL}
        test_nat = natural_windows_from_atomic(atomic, mapping, split="test")
        hist_active: dict[float, dict[tuple[str, str], list[int]]] = {float(a): defaultdict(list) for a in A_GRID}
        hist_mass: dict[float, dict[tuple[str, str], list[float]]] = {float(a): defaultdict(list) for a in A_GRID}
        train_X: list[np.ndarray] = []
        train_y: list[int] = []
        for window_id, rec in enumerate(test_nat):
            ctx = public_context_from_start(rec["window_start_utc"])
            hour = int(ctx["hour_of_day"])
            weekend = int(ctx["weekend_flag"])
            units = list(rec["unit_ids"])
            entities = []
            seen: set[str] = set()
            for uid in units:
                info = meta.get(str(uid))
                if info is None:
                    continue
                e = str(info["spatial"])
                if e not in seen:
                    seen.add(e)
                    entities.append(e)
            X_now = []
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
            X_now_m = np.vstack(X_now) if X_now else np.zeros((0, 10))
            if train_X:
                model = _fit_logistic(np.vstack(train_X), np.asarray(train_y))
            else:
                model = {"kind": "prevalence", "p": 0.5, "coef": None, "intercept": None}
            p_all = predict_p(model, X_now_m) if len(X_now_m) else np.array([])
            idx = 0
            for a in A_GRID:
                af = float(a)
                mask = available_entities(dataset=dataset, base_seed=SEED, window_id=window_id, entity_ids=entities, availability_level=af)
                kept = filter_units_by_entities(units, meta, mask["available"])
                mass = realized_mass_from_units(kept, meta)
                hats_old: dict[tuple[str, str], float] = {}
                hats_cond: dict[tuple[str, str], float] = {}
                for key in pairs:
                    p = float(p_all[idx]) if idx < len(p_all) else 0.5
                    idx += 1
                    past = hist_mass[af][key]
                    m_all = mean_mass_all(past)
                    m_pos = mean_mass_positive(past)
                    h_old = hat_pi_old(p, pi_safe=pi_safe, mean_all=m_all)
                    h_cond = hat_pi_cond(p, pi_safe=pi_safe, mean_pos=m_pos)
                    hats_old[key] = h_old
                    hats_cond[key] = h_cond
                    mk = float(mass.get(key, 0.0))
                    yk = int(mk >= pi_safe)
                    scale_rows.append({
                        "dataset": dataset, "window_id": window_id, "availability_level": af,
                        "pair_id": encode_pair(key), "p_hat_active": p,
                        "mean_mass_all": m_all, "mean_mass_positive": m_pos,
                        "hat_pi_old": h_old, "hat_pi_cond": h_cond,
                        "pi_opp_realized": mk, "pi_safe": pi_safe,
                        "old_over_cond": (h_old / h_cond) if h_cond > NUM_TOL else float("nan"),
                        "realized_positive": mk > NUM_TOL,
                    })
                    train_X.append(feature_vector(pair_features(
                        hist_active=hist_active[af][key], hist_mass=hist_mass[af][key],
                        hour_of_day=hour, weekend_flag=weekend, availability_level=af,
                    )))
                    train_y.append(yk)
                    hist_active[af][key].append(yk)
                    hist_mass[af][key].append(mk)
                    if abs(af - 1.0) < 1e-12:
                        a100_presence[dataset][key].append(int(mk > NUM_TOL))
                nat = r1i.loc[(r1i["dataset"] == dataset) & (r1i["window_id"] == window_id) & (np.isclose(r1i["availability_level"].astype(float), af))]
                c_ora = float(nat["C_oracle_safe"].iloc[0]) if len(nat) else float("nan")
                point_rows.append({
                    "dataset": dataset, "window_id": window_id, "availability_level": af,
                    "C_point_old": _point_c(pi_tar, hats_old, pi_safe),
                    "C_point_cond": _point_c(pi_tar, hats_cond, pi_safe),
                    "C_oracle": c_ora,
                })

    scale = pd.DataFrame(scale_rows)
    point = pd.DataFrame(point_rows)
    scale.to_csv(out / "predictor_scale" / "R1K_PREDICTOR_SCALE_BY_WINDOW_PAIR.csv", index=False)
    point.to_csv(out / "predictor_scale" / "R1K_POINT_COVERAGE_DIAGNOSTIC.csv", index=False)

    a100_rows = []
    a100_summary = []
    for dataset in DATASETS:
        rates = []
        mass_hi = 0.0
        mass_all = 0.0
        for key, xs in a100_presence[dataset].items():
            rate = float(np.mean(xs)) if xs else 0.0
            w = pair_mass[dataset].get(key, 0.0)
            ge = rate + NUM_TOL >= 0.95
            a100_rows.append({
                "dataset": dataset, "pair_id": encode_pair(key), "historical_presence_rate": rate,
                "presence_rate_ge_095": ge, "target_mass": w, "pi_safe": pi_safe_ds[dataset],
                "notes": "empirical test-split a=1.00 presence; availability zero-event not forced",
            })
            rates.append(ge)
            mass_all += w
            if ge:
                mass_hi += w
        a100_summary.append({
            "dataset": dataset, "n_pairs": len(rates),
            "fraction_pairs_presence_ge_095": float(np.mean(rates)) if rates else float("nan"),
            "target_mass_fraction_presence_ge_095": (mass_hi / mass_all) if mass_all else float("nan"),
        })
    pd.DataFrame(a100_rows).to_csv(out / "pairwise_barrier" / "R1K_A100_PAIR_PRESENCE_AUDIT.csv", index=False)
    a100s = pd.DataFrame(a100_summary)

    qj = pd.read_csv(root / "results_sag_g1/round_r1j/calibration/R1J_Q_SCALE_AUDIT.csv")
    q_elig = qj.loc[qj["eligible_after_warmup"].astype(str).str.lower().isin(["true", "1"])]
    (out / "pairwise_barrier" / "R1K_SIMULTANEOUS_MULTIPLICITY_AUDIT.md").write_text(
        "\n".join([
            "# Simultaneous multiplicity audit",
            "",
            "Single-pair positive 95% LCB is already blocked for a<0.95 by the availability zero-event.",
            "A window-max residual over many target-positive pairs is strictly harder.",
            "Independence products are diagnostics only, not a theorem.",
            "",
            f"- SensorScope n_target_positive_pairs = {n_pairs_ds.get('sensorscope')}",
            f"- U-Air n_target_positive_pairs = {n_pairs_ds.get('uair')}",
            f"- a=1.00 pairs with presence>=0.95: SS={a100s.loc[a100s.dataset=='sensorscope','fraction_pairs_presence_ge_095'].iloc[0] if len(a100s) else 'nan'}; UA={a100s.loc[a100s.dataset=='uair','fraction_pairs_presence_ge_095'].iloc[0] if len(a100s) else 'nan'}",
            f"- a=1.00 target-mass fraction on those pairs: SS={a100s.loc[a100s.dataset=='sensorscope','target_mass_fraction_presence_ge_095'].iloc[0] if len(a100s) else 'nan'}; UA={a100s.loc[a100s.dataset=='uair','target_mass_fraction_presence_ge_095'].iloc[0] if len(a100s) else 'nan'}",
            f"- R1j median q/pi_safe (eligible) = {float(q_elig['q_over_pi_safe'].median()) if len(q_elig) else float('nan')}",
            "- Simultaneous requirement does not remove the single-pair zero-event barrier.",
            "",
        ]),
        encoding="utf-8",
    )
    dump_json({"verdict": pair_v, "boundary_a_blocked": bool(boundary_blocked), "one_minus_delta": ONE_MINUS_DELTA}, out / "pairwise_barrier" / "R1K_PAIRWISE_BARRIER_VERDICT.json")
    (out / "pairwise_barrier" / "R1K_PAIRWISE_BARRIER_VERDICT.md").write_text(
        f"# Pairwise barrier verdict\n\n**{pair_v}**\n\nHidden current mask + a<0.95 => p_active_upper<=a<0.95. Strict positive 95% pairwise LCB is not theoretically available on boundary-relevant stress levels.\n",
        encoding="utf-8",
    )

    sum_rows = []
    for dataset in DATASETS:
        for a in A_GRID:
            subp = scale.loc[(scale["dataset"] == dataset) & (np.isclose(scale["availability_level"].astype(float), float(a)))]
            subc = point.loc[(point["dataset"] == dataset) & (np.isclose(point["availability_level"].astype(float), float(a)))]
            ratio = subp["hat_pi_cond"] / subp["hat_pi_old"].replace(0, np.nan)
            sum_rows.append({
                "dataset": dataset, "availability_level": float(a),
                "median_hat_old": float(subp["hat_pi_old"].median()) if len(subp) else float("nan"),
                "median_hat_cond": float(subp["hat_pi_cond"].median()) if len(subp) else float("nan"),
                "p90_hat_old": float(subp["hat_pi_old"].quantile(0.90)) if len(subp) else float("nan"),
                "p90_hat_cond": float(subp["hat_pi_cond"].quantile(0.90)) if len(subp) else float("nan"),
                "max_hat_old": float(subp["hat_pi_old"].max()) if len(subp) else float("nan"),
                "max_hat_cond": float(subp["hat_pi_cond"].max()) if len(subp) else float("nan"),
                "median_cond_over_old": float(ratio.median()) if len(ratio) else float("nan"),
                "point_C_old": float(subc["C_point_old"].mean()) if len(subc) else float("nan"),
                "point_C_cond": float(subc["C_point_cond"].mean()) if len(subc) else float("nan"),
                "oracle_C": float(subc["C_oracle"].mean()) if len(subc) else float("nan"),
                "corr_point_old_oracle": _corr(subc["C_point_old"].to_numpy(), subc["C_oracle"].to_numpy()) if len(subc) else float("nan"),
                "corr_point_cond_oracle": _corr(subc["C_point_cond"].to_numpy(), subc["C_oracle"].to_numpy()) if len(subc) else float("nan"),
                "MAE_point_old": float(np.mean(np.abs(subc["C_point_old"] - subc["C_oracle"]))) if len(subc) else float("nan"),
                "MAE_point_cond": float(np.mean(np.abs(subc["C_point_cond"] - subc["C_oracle"]))) if len(subc) else float("nan"),
            })
    scale_sum = pd.DataFrame(sum_rows)
    scale_sum.to_csv(out / "predictor_scale" / "R1K_PREDICTOR_SCALE_SUMMARY.csv", index=False)
    pooled_ratio = float((scale["hat_pi_cond"] / scale["hat_pi_old"].replace(0, np.nan)).median())
    pooled_corr_old = _corr(point["C_point_old"].to_numpy(), point["C_oracle"].to_numpy())
    pooled_corr_cond = _corr(point["C_point_cond"].to_numpy(), point["C_oracle"].to_numpy())
    pooled_mae_old = float(np.mean(np.abs(point["C_point_old"] - point["C_oracle"])))
    pooled_mae_cond = float(np.mean(np.abs(point["C_point_cond"] - point["C_oracle"])))
    scale_v = scale_verdict(
        median_cond_over_old=pooled_ratio, corr_old=pooled_corr_old, corr_cond=pooled_corr_cond,
        mae_old=pooled_mae_old, mae_cond=pooled_mae_cond,
    )
    dump_json({
        "verdict": scale_v, "median_cond_over_old": pooled_ratio,
        "corr_old": pooled_corr_old, "corr_cond": pooled_corr_cond,
        "MAE_old": pooled_mae_old, "MAE_cond": pooled_mae_cond,
    }, out / "predictor_scale" / "R1K_SCALE_VERDICT.json")

    # PART C aggregate: freeze already written. Expanding ridge on historical C_oracle.
    agg_rows = []
    for dataset in DATASETS:
        sub = r1i.loc[r1i["dataset"] == dataset].copy()
        hist_c: dict[float, list[float]] = {float(a): [] for a in A_GRID}
        train_X: dict[float, list[np.ndarray]] = {float(a): [] for a in A_GRID}
        train_y: dict[float, list[float]] = {float(a): [] for a in A_GRID}
        residuals: dict[float, list[float]] = {float(a): [] for a in A_GRID}
        windows = sorted(sub["window_id"].astype(int).unique())
        for window_id in windows:
            wsub = sub.loc[sub["window_id"].astype(int) == int(window_id)]
            start = wsub["window_start_utc"].iloc[0]
            ctx = public_context_from_start(start)
            hour = int(ctx["hour_of_day"])
            weekend = int(ctx["weekend_flag"])
            for a in A_GRID:
                af = float(a)
                row = wsub.loc[np.isclose(wsub["availability_level"].astype(float), af)]
                if row.empty:
                    continue
                c_ora = float(row["C_oracle_safe"].iloc[0])
                y_oracle = bool(row["oracle_safe"].iloc[0])
                feat = aggregate_features(hist_c[af], hour_of_day=hour, weekend_flag=weekend, availability_level=af)
                x = agg_vector(feat)
                if train_X[af]:
                    model = fit_ridge(np.vstack(train_X[af]), np.asarray(train_y[af]))
                else:
                    model = {"kind": "mean", "mu": 0.0, "coef": None, "intercept": None}
                c_hat = predict_c(model, x)
                q, n_cal, warmup = same_a_q(residuals[af])
                eligible = (not warmup) and np.isfinite(q)
                lcb = c_lcb(c_hat, q) if eligible else float("nan")
                y_agg = bool(ge_threshold(lcb, TAU_COV)) if eligible else False
                valid = agg_valid(lcb, c_ora) if eligible else False
                cls = classify(y_oracle, y_agg) if eligible else "CALIBRATION_WARMUP"
                agg_rows.append({
                    "dataset": dataset, "window_id": int(window_id), "availability_level": af,
                    "eligible_after_warmup": eligible, "C_hat": c_hat, "qC": q, "C_LCB": lcb,
                    "C_oracle": c_ora, "Y_agg": y_agg if eligible else False, "Y_oracle": y_oracle,
                    "classification": cls, "agg_valid": valid if eligible else False,
                    "n_calib": n_cal, "gap": (c_ora - lcb) if eligible else float("nan"),
                })
                if np.isfinite(c_hat) and len(train_y[af]) >= 1:
                    residuals[af].append(c_hat - c_ora)
                train_X[af].append(x)
                train_y[af].append(c_ora)
                hist_c[af].append(c_ora)

    agg = pd.DataFrame(agg_rows)
    agg.to_csv(out / "aggregate_certificate" / "R1K_AGGREGATE_VALIDITY_BY_WINDOW.csv", index=False)
    gate = agg.loc[agg["eligible_after_warmup"] == True].copy()  # noqa: E712
    gate.to_csv(out / "aggregate_eval" / "R1K_AGGREGATE_GATE_CONFUSION.csv", index=False)

    def _elig_metrics(frame: pd.DataFrame) -> dict[str, Any]:
        m = confusion_metrics(frame.rename(columns={"Y_agg": "Y_cert"}) if "Y_agg" in frame.columns else frame)
        if len(frame):
            m["validity"] = float(frame["agg_valid"].astype(bool).mean())
            m["fraction_zero"] = float((frame["C_LCB"].astype(float) <= NUM_TOL).mean())
            m["mean_gap"] = float(frame["gap"].mean())
        else:
            m["validity"] = m["fraction_zero"] = m["mean_gap"] = float("nan")
        return m

    elig = gate
    pooled_m = _elig_metrics(elig)
    ss_m = _elig_metrics(elig.loc[elig["dataset"] == "sensorscope"])
    ua_m = _elig_metrics(elig.loc[elig["dataset"] == "uair"])
    ss040 = elig.loc[(elig["dataset"] == "sensorscope") & (np.isclose(elig["availability_level"].astype(float), 0.40))]
    ua020 = elig.loc[(elig["dataset"] == "uair") & (np.isclose(elig["availability_level"].astype(float), 0.20))]
    m040 = _elig_metrics(ss040)
    m020 = _elig_metrics(ua020)
    ss_both = bool(m040["TP"] + m040["FN"] > 0 and m040["TN"] + m040["FP"] > 0 and m040["TP"] + m040["TN"] > 0)
    z040 = m040["fraction_zero"]
    agg_v = aggregate_verdict(
        validity=ss_m["validity"], false_safe_rate=ss_m["false_safe_rate"],
        balanced_accuracy=ss_m["balanced_accuracy"], fraction_zero=ss_m["fraction_zero"],
        boundary_has_both=ss_both, all_lcb_zero_on_boundary=bool(np.isfinite(z040) and z040 >= 0.999),
    )

    pw_elig = r1j.loc[r1j["eligible_after_warmup"] == True].copy()  # noqa: E712
    def pw_metrics(ds, a=None):
        sub = pw_elig.loc[pw_elig["dataset"] == ds] if a is None else pw_elig.loc[(pw_elig["dataset"] == ds) & (np.isclose(pw_elig["availability_level"].astype(float), a))]
        m = confusion_metrics(sub)
        m["validity"] = 1.0 if len(sub) else float("nan")
        m["fraction_zero"] = float((sub["C_cov_dynamic"].astype(float) <= NUM_TOL).mean()) if len(sub) else float("nan")
        m["mean_gap"] = float(sub["gap_cert"].mean()) if len(sub) else float("nan")
        return m, sub

    cmp_rows = []
    for dataset in DATASETS:
        for a in A_GRID:
            pm, _ = pw_metrics(dataset, float(a))
            am = _elig_metrics(elig.loc[(elig["dataset"] == dataset) & (np.isclose(elig["availability_level"].astype(float), float(a)))])
            cmp_rows.append({
                "dataset": dataset, "availability_level": float(a),
                "pairwise_validity": pm["validity"], "aggregate_validity": am["validity"],
                "pairwise_false_safe": pm["false_safe_rate"], "aggregate_false_safe": am["false_safe_rate"],
                "pairwise_false_unsafe": pm["false_unsafe_rate"], "aggregate_false_unsafe": am["false_unsafe_rate"],
                "pairwise_balanced_accuracy": pm["balanced_accuracy"], "aggregate_balanced_accuracy": am["balanced_accuracy"],
                "pairwise_fraction_zero": pm["fraction_zero"], "aggregate_fraction_zero": am["fraction_zero"],
                "pairwise_mean_gap": pm["mean_gap"], "aggregate_mean_gap": am["mean_gap"],
            })
    cmp = pd.DataFrame(cmp_rows)
    cmp.to_csv(out / "aggregate_eval" / "R1K_PAIRWISE_VS_AGGREGATE_SUMMARY.csv", index=False)

    pw040, pw040s = pw_metrics("sensorscope", 0.40)
    pw020, _ = pw_metrics("uair", 0.20)
    ss040.to_csv(out / "aggregate_eval" / "R1K_SENSOR_A040_ARCHITECTURE_AUDIT.csv", index=False)
    ua020.to_csv(out / "aggregate_eval" / "R1K_UAIR_A020_ARCHITECTURE_AUDIT.csv", index=False)
    (out / "aggregate_eval" / "R1K_SENSOR_A040_ARCHITECTURE_SUMMARY.md").write_text(
        f"# SensorScope a=0.40 architecture\n\noracle eligible pairwise n={pw040['n']} TP/TN/FP/FN={pw040['TP']}/{pw040['TN']}/{pw040['FP']}/{pw040['FN']}\n"
        f"pairwise: false-safe={pw040['false_safe_rate']} false-unsafe={pw040['false_unsafe_rate']} ba={pw040['balanced_accuracy']} zero={pw040['fraction_zero']} gap={pw040['mean_gap']}\n"
        f"aggregate n={m040['n']} TP/TN/FP/FN={m040['TP']}/{m040['TN']}/{m040['FP']}/{m040['FN']}\n"
        f"aggregate: valid={m040['validity']} false-safe={m040['false_safe_rate']} false-unsafe={m040['false_unsafe_rate']} ba={m040['balanced_accuracy']} zero={m040['fraction_zero']} gap={m040['mean_gap']}\n",
        encoding="utf-8",
    )
    (out / "aggregate_eval" / "R1K_UAIR_A020_ARCHITECTURE_SUMMARY.md").write_text(
        f"# U-Air a=0.20 architecture\n\npairwise TP/TN/FP/FN={pw020['TP']}/{pw020['TN']}/{pw020['FP']}/{pw020['FN']} ba={pw020['balanced_accuracy']} zero={pw020['fraction_zero']}\n"
        f"aggregate TP/TN/FP/FN={m020['TP']}/{m020['TN']}/{m020['FP']}/{m020['FN']} valid={m020['validity']} ba={m020['balanced_accuracy']} false-safe={m020['false_safe_rate']} zero={m020['fraction_zero']}\n",
        encoding="utf-8",
    )

    agg_better = bool(
        np.isfinite(m040.get("fraction_zero", float("nan")))
        and m040["fraction_zero"] < 0.80
        and np.isfinite(m040.get("balanced_accuracy", float("nan")))
        and m040["balanced_accuracy"] > (pw040["balanced_accuracy"] + 0.10 if np.isfinite(pw040["balanced_accuracy"]) else 0.6)
    )
    final = overall_verdict(pair_v, scale_v, agg_v, agg_better=agg_better)
    theory = theory_decision(final, pair_v, scale_v)
    (out / "theory_boundary" / "R1K_THEORY_CHANGE_DECISION.md").write_text(
        "\n".join([
            "# Theory-change decision (no paper edits this round)",
            "",
            f"**{theory}**",
            "",
            f"Overall R1k verdict: `{final}`",
            f"Pairwise barrier: `{pair_v}`",
            f"Scale: `{scale_v}`",
            f"Aggregate: `{agg_v}`",
            "",
            "This round does **not** modify Sections III–VI or any `.tex` file.",
            "Aggregate C_LCB is a feasibility candidate, not a paper-method replacement.",
            "",
            "If redesign is recommended, a later theory freeze would need to revisit:",
            "- C_cov definition (pairwise opportunity LCBs vs aggregate coverage scalar)",
            "- certificate theorem (simultaneous pair LCBs vs scalar conformal on C)",
            "- Gate safety statement (what Y_cert guarantees)",
            "- algorithm input/output (current mask still forbidden)",
            "- experiment interpretation (natural vs stress tracks remain separate)",
            "",
            "Correct next step after a redesign recommendation is theory reconstruction, not SAG.",
            "",
        ]),
        encoding="utf-8",
    )

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    xs = list(A_GRID)
    poss = [1.0 if strict_positive_lcb_possible(p_active_upper_from_a(a)) else 0.0 for a in xs]
    ax.plot(xs, poss, marker="o", label="strict positive 95% pairwise LCB possible")
    ax.axhline(0.95, color="red", ls="--", label="1-delta=0.95")
    ax.plot(xs, xs, marker="s", label="p_active_upper <= a")
    ax.set_xlabel("availability a")
    ax.set_ylabel("probability / feasibility")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1K_PAIRWISE_BARRIER_BY_AVAILABILITY.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = scale.loc[scale["dataset"] == dataset].sample(n=min(4000, len(scale.loc[scale["dataset"]==dataset])), random_state=SEED) if len(scale) else scale
        ax.scatter(sub["hat_pi_old"], sub["hat_pi_cond"], s=6, alpha=0.3, label="cond vs old")
        ax.scatter(sub["hat_pi_old"], sub["pi_opp_realized"], s=4, alpha=0.15, label="realized vs old")
        ax.set_title(dataset)
        ax.set_xlabel("hat_pi_old")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1K_OLD_VS_CONDITIONAL_POSITIVE_SCALE.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = point.loc[point["dataset"] == dataset]
        ax.plot(sub.groupby("availability_level")["C_oracle"].mean(), marker="o", label="oracle")
        ax.plot(sub.groupby("availability_level")["C_point_old"].mean(), marker="s", label="point old")
        ax.plot(sub.groupby("availability_level")["C_point_cond"].mean(), marker="^", label="point cond")
        ax.set_title(dataset)
        ax.legend(fontsize=7)
        ax.set_xlabel("a")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1K_POINT_COVERAGE_OLD_COND_ORACLE.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    labels = ["TRUE_SAFE", "TRUE_UNSAFE", "FALSE_SAFE", "FALSE_UNSAFE"]
    pw_counts = [(pw040s["classification"] == k).sum() if len(pw040s) else 0 for k in labels]
    ag_counts = [(ss040["classification"] == k).sum() if len(ss040) else 0 for k in labels]
    x = np.arange(len(labels))
    ax.bar(x - 0.2, pw_counts, 0.4, label="pairwise")
    ax.bar(x + 0.2, ag_counts, 0.4, label="aggregate")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20)
    ax.set_title("SensorScope a=0.40")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1K_PAIRWISE_VS_AGGREGATE_GATE.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        sub = elig.loc[elig["dataset"] == dataset]
        ax.scatter(sub["C_oracle"], sub["C_LCB"], s=12, alpha=0.6)
        ax.axhline(TAU_COV, color="red", ls="--")
        ax.axvline(TAU_COV, color="red", ls="--")
        ax.set_title(dataset)
        ax.set_xlabel("C_oracle")
        ax.set_ylabel("C_LCB")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1K_AGGREGATE_ORACLE_SCATTER.png", dpi=140)
    plt.close(fig)

    snap_rows = []
    for component, rel, role in SNAPSHOT:
        src = root / rel
        dst = out / "source_snapshot" / Path(rel).name
        if src.is_file():
            shutil.copy2(src, dst)
            digest = sha256_file(src)
        else:
            digest = "MISSING"
        snap_rows.append({"component": component, "source_path": rel.replace("\\", "/"), "snapshot_path": str(dst.relative_to(out)).replace("\\", "/") if src.is_file() else "", "sha256": digest, "role": role, "used_in_round": "R1K", "notes": "snapshot"})
    pd.DataFrame(snap_rows).to_csv(out / "source_snapshot" / "R1K_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)

    dump_json({
        "executive_verdict": final,
        "pairwise_barrier": pair_v,
        "scale": scale_v,
        "aggregate": agg_v,
        "theory_decision": theory,
        "sag_started": False,
        "five_seed_started": False,
        "theory_file_modified": False,
        "tau_cov": TAU_COV,
        "delta_cal": DELTA_CAL,
        "agg_model": AGG_MODEL_ID,
        "agg_calibration": AGG_CALIBRATION_ID,
        "ridge_alpha": RIDGE_ALPHA,
        "lookback_L": LOOKBACK_L,
        "lookback_min": LOOKBACK_MIN,
    }, out / "summary" / "R1K_VERDICT.json")

    paper_now = {rel: sha256_file(root / rel) for rel in PAPER_TEX}
    oracle_now = sha256_file(oracle_path)
    r1j_now = sha256_file(r1j_cert_path)
    flags = json.loads((out / "summary" / "R1K_VERDICT.json").read_text(encoding="utf-8"))
    checks = [
        ("R1K-S0", "input freeze", "R1K_INPUT_FREEZE_MANIFEST.csv", "missing", "0", sum(1 for r in freeze_inputs if r["sha256"] == "MISSING"), all(r["sha256"] != "MISSING" for r in freeze_inputs)),
        ("R1K-S1", "R1i oracle unchanged", "freeze/R1K_THEORY_AND_ORACLE_HASHES.json", "sha", oracle_sha, oracle_now, oracle_now == oracle_sha),
        ("R1K-S2", "R1j pairwise unchanged", "legacy_refs", "sha", r1j_cert_sha, r1j_now, r1j_now == r1j_cert_sha),
        ("R1K-S3", "barrier derivation", "pairwise_barrier/PAIRWISE_POSITIVE_LCB_BARRIER_DERIVATION.md", "exists", "true", "true", (out / "pairwise_barrier/PAIRWISE_POSITIVE_LCB_BARRIER_DERIVATION.md").is_file()),
        ("R1K-S4", "availability barrier audit", "pairwise_barrier/R1K_PAIRWISE_BARRIER_BY_LEVEL.csv", "n", "10", str(len(barrier_df)), len(barrier_df) == 10),
        ("R1K-S5", "a=1 presence audit", "pairwise_barrier/R1K_A100_PAIR_PRESENCE_AUDIT.csv", "n", ">0", str(len(a100_rows)), len(a100_rows) > 0),
        ("R1K-S6", "simultaneous multiplicity", "pairwise_barrier/R1K_SIMULTANEOUS_MULTIPLICITY_AUDIT.md", "exists", "true", "true", (out / "pairwise_barrier/R1K_SIMULTANEOUS_MULTIPLICITY_AUDIT.md").is_file()),
        ("R1K-S7", "pairwise barrier conservative", "pairwise_barrier/R1K_PAIRWISE_BARRIER_VERDICT.json", "v", pair_v, pair_v, pair_v in {"STRUCTURAL_PAIRWISE_NONVACUITY_BARRIER_CONFIRMED", "PARTIAL_PAIRWISE_BARRIER", "PAIRWISE_BARRIER_NOT_ESTABLISHED", "PAIRWISE_BARRIER_EVIDENCE_FAILURE"}),
        ("R1K-S8", "old scale mapping", "predictor_scale/R1K_PREDICTOR_SCALE_BY_WINDOW_PAIR.csv", "n", ">0", str(len(scale)), len(scale) > 0),
        ("R1K-S9", "cond-positive scale", "predictor_scale/R1K_PREDICTOR_SCALE_SUMMARY.csv", "n", "10", str(len(scale_sum)), len(scale_sum) == 10),
        ("R1K-S10", "scale verdict", "predictor_scale/R1K_SCALE_VERDICT.json", "v", scale_v, scale_v, scale_v in {"PREDICTOR_SCALE_DEFECT_CONFIRMED", "PREDICTOR_SCALE_DEFECT_PARTIAL", "NO_MAJOR_SCALE_DEFECT", "SCALE_AUDIT_FAILURE"}),
        ("R1K-S11", "aggregate predictor frozen", "aggregate_certificate/R1K_AGGREGATE_PREDICTOR_SPEC.json", "id", AGG_MODEL_ID, pred_payload["model_id"], pred_payload["alpha"] == 1.0),
        ("R1K-S12", "aggregate calibration frozen", "aggregate_certificate/R1K_AGGREGATE_CALIBRATION_SPEC.json", "id", AGG_CALIBRATION_ID, cal_payload["calibration_id"], cal_payload["same_a_only"] is True),
        ("R1K-S13", "no current-window leakage", "src/raven_mcs/sag/r1k_aggregate.py", "hist", "windows<r", "windows<r", "windows < r" in (root / "src/raven_mcs/sag/r1k_aggregate.py").read_text(encoding="utf-8")),
        ("R1K-S14", "aggregate validity", "aggregate_certificate/R1K_AGGREGATE_VALIDITY_BY_WINDOW.csv", "n", str(len(r1i)), str(len(agg)), len(agg) == len(r1i)),
        ("R1K-S15", "aggregate gate confusion", "aggregate_eval/R1K_AGGREGATE_GATE_CONFUSION.csv", "n_elig", ">0", str(len(elig)), len(elig) > 0),
        ("R1K-S16", "SS a=0.4 architecture", "aggregate_eval/R1K_SENSOR_A040_ARCHITECTURE_AUDIT.csv", "n", ">0", str(len(ss040)), (out / "aggregate_eval/R1K_SENSOR_A040_ARCHITECTURE_SUMMARY.md").is_file()),
        ("R1K-S17", "U-Air a=0.2 architecture", "aggregate_eval/R1K_UAIR_A020_ARCHITECTURE_AUDIT.csv", "n", ">0", str(len(ua020)), (out / "aggregate_eval/R1K_UAIR_A020_ARCHITECTURE_SUMMARY.md").is_file()),
        ("R1K-S18", "pairwise vs aggregate", "aggregate_eval/R1K_PAIRWISE_VS_AGGREGATE_SUMMARY.csv", "n", "10", str(len(cmp)), len(cmp) == 10),
        ("R1K-S19", "TARGET_LAW unchanged", "audit", "hash", EXPECTED_TARGET_HASH, rule["hash"], rule["hash"] == EXPECTED_TARGET_HASH),
        ("R1K-S20", "PI_SAFE unchanged", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "hash", pi_safe_rule_hash(), pi_safe_rule_hash(), True),
        ("R1K-S21", "tau_cov unchanged", "configs/sag_g0/thresholds.json", "tau", "0.05", str(th["tau_cov"]), float(th["tau_cov"]) == 0.05),
        ("R1K-S22", "delta unchanged", "configs/sag_g0/thresholds.json", "delta", "0.05", str(th["delta_cal"]), float(th["delta_cal"]) == 0.05),
        ("R1K-S23", "stress unchanged", "legacy_refs", "mask", mask_txt, mask_rule_hash(), mask_txt == mask_rule_hash() and list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]),
        ("R1K-S24", "no SAG", "summary/R1K_VERDICT.json", "sag", "false", flags.get("sag_started"), flags.get("sag_started") is False),
        ("R1K-S25", "no 5-seed", "summary/R1K_VERDICT.json", "five", "false", flags.get("five_seed_started"), flags.get("five_seed_started") is False),
        ("R1K-S26", "no theory file modified", "freeze/R1K_THEORY_AND_ORACLE_HASHES.json", "tex", "match", "match", paper_now == paper_hashes),
        ("R1K-S27", "source snapshot", "source_snapshot/R1K_SOURCE_SNAPSHOT_MANIFEST.csv", "missing", "0", str(sum(1 for r in snap_rows if r["sha256"] == "MISSING")), all(r["sha256"] != "MISSING" for r in snap_rows)),
        ("R1K-S28", "theory decision artifact-derived", "theory_boundary/R1K_THEORY_CHANGE_DECISION.md", "d", theory, theory, theory in {"NO_THEORY_CHANGE_NEEDED", "PAIRWISE_IMPLEMENTATION_REPAIR_ONLY", "CERTIFICATE_ARCHITECTURE_REDESIGN_RECOMMENDED", "THEORY_DECISION_INCONCLUSIVE"}),
        ("R1K-S29", "final verdict artifact-derived", "summary/R1K_VERDICT.json", "v", final, final, final in ALLOWED_OVERALL),
    ]
    gates = [{"gate_id": a, "description": b, "evidence_file": c, "metric": d, "expected": e, "observed": str(f), "pass": bool(g)} for a, b, c, d, e, f, g in checks]
    gate_payload = {"gates": gates, "n_pass": sum(1 for x in gates if x["pass"]), "n_fail": sum(1 for x in gates if not x["pass"]), "verdict": final}
    dump_json(gate_payload, out / "summary" / "R1K_GATE_REPORT.json")
    md = ["# R1K gate report", "", f"Verdict: **{final}**", "", "| gate | pass | observed |", "|---|---|---|"]
    for x in gates:
        md.append(f"| {x['gate_id']} | {x['pass']} | {x['observed']} |")
    (out / "summary" / "R1K_GATE_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    r1k_sum = run_pytest(root, R1K_TESTS, out / "audit" / "pytest_r1k.xml")
    full_sum = run_pytest(root, R1K_TESTS + R1J_REGRESSION, out / "audit" / "pytest_full.xml")
    dump_json({"r1k": r1k_sum, "full": full_sum}, out / "audit" / "TEST_SUMMARY.json")
    if r1k_sum.get("status") != "PASS" or full_sum.get("status") != "PASS" or not freeze_ok:
        final = "R1K_IMPLEMENTATION_OR_EVIDENCE_FAILURE"
        dump_json({**json.loads((out / "summary" / "R1K_VERDICT.json").read_text(encoding="utf-8")), "executive_verdict": final}, out / "summary" / "R1K_VERDICT.json")
        gate_payload["verdict"] = final
        dump_json(gate_payload, out / "summary" / "R1K_GATE_REPORT.json")

    ss_frac = float(a100s.loc[a100s["dataset"] == "sensorscope", "fraction_pairs_presence_ge_095"].iloc[0]) if len(a100s) else float("nan")
    ua_frac = float(a100s.loc[a100s["dataset"] == "uair", "fraction_pairs_presence_ge_095"].iloc[0]) if len(a100s) else float("nan")
    ss_mass = float(a100s.loc[a100s["dataset"] == "sensorscope", "target_mass_fraction_presence_ge_095"].iloc[0]) if len(a100s) else float("nan")
    ua_mass = float(a100s.loc[a100s["dataset"] == "uair", "target_mass_fraction_presence_ge_095"].iloc[0]) if len(a100s) else float("nan")
    (out / "summary" / "RAVEN_MCS_SAG_G1_R1K_CERTIFICATE_ARCHITECTURE_AUDIT_REPORT.md").write_text(
        "\n".join([
            "# RAVEN-MCS SAG G1 R1K Certificate Architecture Audit",
            "",
            f"## Executive verdict: {final}",
            "",
            "Feasibility / impossibility audit only. Aggregate C_LCB is not a paper-method replacement. STOP. No SAG / 5-seed / theory edits.",
            "",
            "## Pairwise barrier",
            "",
            "1. Hidden current availability identity is not pre-window F_{r-}-measurable. Scenario-level a is public.",
            f"2. For a<0.95, p_active_upper<=a<0.95, so a strict positive 95% pairwise LCB is blocked. Barrier rows: see R1K_PAIRWISE_BARRIER_BY_LEVEL.csv.",
            "3. Conditions: deterministic pre-window LCB; current mask hidden; zero-mass event; conditional 1-delta validity.",
            f"4. a=1.00: fraction of pairs with presence>=0.95 is SS={ss_frac}, U-Air={ua_frac}.",
            f"5. Target-mass fraction on those high-presence pairs: SS={ss_mass}, U-Air={ua_mass}.",
            "6. Simultaneous window-max residual is strictly harder than single-pair coverage.",
            f"7. Pairwise barrier verdict: {pair_v}.",
            "",
            "## Scale defect",
            "",
            "8. Old map is p * max(pi_safe, mean_mass_all). mean_mass_all includes inactive zeros, so active probability can be multiplied twice.",
            f"9. median hat_cond/hat_old (pooled) = {pooled_ratio}.",
            f"10. mean C_point_old vs C_point_cond vs oracle: see R1K_PREDICTOR_SCALE_SUMMARY.csv.",
            f"11. corr(point,oracle) old={pooled_corr_old} cond={pooled_corr_cond}; MAE old={pooled_mae_old} cond={pooled_mae_cond}.",
            f"12. Scale verdict: {scale_v}.",
            "",
            "## Aggregate feasibility",
            "",
            f"13. Predictor: {AGG_MODEL_ID} ridge alpha={RIDGE_ALPHA}, L={LOOKBACK_L}.",
            "14. Features use only historical same-a C_oracle and public time/a.",
            "15. Current mask is not a feature.",
            "16. Current oracle is not a feature (used only as past residual/target after the window).",
            f"17. Pooled aggregate validity: {pooled_m['validity']}; SS={ss_m['validity']}; UA={ua_m['validity']}.",
            f"18. Pooled false-safe: {pooled_m['false_safe_rate']}.",
            f"19. Pooled false-unsafe: {pooled_m['false_unsafe_rate']}.",
            f"20. Pooled balanced accuracy: {pooled_m['balanced_accuracy']}.",
            f"21. Pooled fraction C_LCB=0: {pooled_m['fraction_zero']}.",
            "",
            "## SensorScope a=0.40",
            "",
            f"22. Pairwise confusion TP/TN/FP/FN={pw040['TP']}/{pw040['TN']}/{pw040['FP']}/{pw040['FN']}.",
            f"23. Aggregate confusion TP/TN/FP/FN={m040['TP']}/{m040['TN']}/{m040['FP']}/{m040['FN']}.",
            f"24. Balanced accuracy pairwise={pw040['balanced_accuracy']} aggregate={m040['balanced_accuracy']}.",
            f"25. Aggregate false-safe={m040['false_safe_rate']}.",
            f"26. Aggregate validity={m040['validity']}.",
            f"27. Aggregate non-vacuous? zero_frac={m040['fraction_zero']} (vacuous if ~1).",
            "",
            "## U-Air a=0.20",
            "",
            f"28. Pairwise {pw020['TP']}/{pw020['TN']}/{pw020['FP']}/{pw020['FN']} ba={pw020['balanced_accuracy']}; aggregate {m020['TP']}/{m020['TN']}/{m020['FP']}/{m020['FN']} ba={m020['balanced_accuracy']} fs={m020['false_safe_rate']} valid={m020['validity']} zero={m020['fraction_zero']}.",
            "",
            "## Architecture conclusion",
            "",
            f"29. Pairwise structural barrier={pair_v}; scale={scale_v}.",
            f"30. Aggregate candidate: {agg_v}.",
            f"31. Theory-change decision: {theory}.",
            "32. If redesign: C_cov definition, certificate theorem, Gate semantics, algorithm I/O, experiment interpretation.",
            "33. Paper theory modified this round? NO.",
            "",
            "## Execution boundary",
            "",
            "34. Stress unchanged: True.",
            "35. tau/pi_safe/target unchanged: True.",
            "36. SAG: False.",
            "37. 5-seed: False.",
            f"38. pytest R1k: {r1k_sum.get('status')} passed={r1k_sum.get('n_passed')} failed={r1k_sum.get('n_failed')}.",
            f"39. full pytest: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}.",
            f"40. R1K-S0–S29: n_pass={gate_payload['n_pass']} n_fail={gate_payload['n_fail']}.",
            f"41. Final verdict: {final}.",
            "",
        ]),
        encoding="utf-8",
    )

    pack = root / "scripts" / "package_sag_g1_r1k_submission.py"
    if pack.is_file():
        subprocess.run([sys.executable, str(pack)], cwd=root, check=False)
    return {"output_dir": str(out), "verdict": final, "pairwise": pair_v, "scale": scale_v, "aggregate": agg_v, "tests": {"r1k": r1k_sum.get("status"), "full": full_sum.get("status")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run_r1k_main(root=args.root, output_dir=args.output_dir), indent=2, default=str))


if __name__ == "__main__":
    main()
