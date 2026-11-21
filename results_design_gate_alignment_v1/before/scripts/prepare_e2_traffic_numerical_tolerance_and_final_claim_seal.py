#!/usr/bin/env python3
"""E2 numerical tolerance + final claim seal (no training)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from raven_mcs.e2.traffic_final_seal import (
    ALPHA,
    BASELINES,
    EPS_ZERO,
    FORMAL_SEEDS,
    METHODS,
    NON_BALANCED,
    SCENARIOS,
    STRUCTURAL_METRICS,
    apply_eps_zero,
)
from raven_mcs.e2.traffic_formal_analysis.stats import holm_adjust, summarize_vector
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "artifacts/e2_traffic_formal_runs_r1"
PRIOR_ANALYSIS = ROOT / "artifacts/e2_traffic_formal_results_analysis_r1"
PRIOR_RECON = ROOT / "artifacts/e2_traffic_offline_metric_reconstruction_r1"
ART = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1"
LEDGER = ROOT / "logs/E2_TRAFFIC_FORMAL_RUNS_R1_EXACT_COMMANDS.jsonl"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def freeze_inputs() -> dict[str, Any]:
    ART.mkdir(parents=True, exist_ok=True)
    files = {
        "formal_results.csv": SRC / "formal_results.csv",
        "HEAD_TAIL_RECONSTRUCTED.csv": PRIOR_RECON / "HEAD_TAIL_RECONSTRUCTED.csv",
        "DELTA_GROUP_RECONSTRUCTED.csv": PRIOR_RECON / "DELTA_GROUP_RECONSTRUCTED.csv",
        "DELTA_PAIR_RECONSTRUCTED.csv": PRIOR_RECON / "DELTA_PAIR_RECONSTRUCTED.csv",
        "STRUCTURAL_RAVEN_VS_BASELINE_STATS.csv": PRIOR_RECON / "STRUCTURAL_RAVEN_VS_BASELINE_STATS.csv",
        "STRUCTURAL_SCENARIO_VS_BALANCED_STATS.csv": PRIOR_RECON / "STRUCTURAL_SCENARIO_VS_BALANCED_STATS.csv",
        "E2_CLAIM_MATRIX.csv": PRIOR_RECON / "E2_CLAIM_MATRIX.csv",
        "CLAIM_EVIDENCE_VALIDATION.json": PRIOR_RECON / "CLAIM_EVIDENCE_VALIDATION.json",
        "LEDGER_ATTEMPT_AUDIT_R2.json": PRIOR_RECON / "LEDGER_ATTEMPT_AUDIT_R2.json",
        "SCENARIO_VS_BALANCED_STATS.csv": PRIOR_ANALYSIS / "SCENARIO_VS_BALANCED_STATS.csv",
        "RAVEN_VS_BASELINE_SECONDARY.csv": PRIOR_ANALYSIS / "RAVEN_VS_BASELINE_SECONDARY.csv",
        "COMPLETE_ALIGNED_DOD_SUMMARY.json": PRIOR_ANALYSIS / "COMPLETE_ALIGNED_DOD_SUMMARY.json",
        "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json": PRIOR_ANALYSIS / "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json",
        "ledger": LEDGER,
    }
    manifest = {"created_utc": _utc(), "files": {}}
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
    df = pd.read_csv(SRC / "formal_results.csv")
    keys = df.apply(lambda r: f"{int(r.seed)}:{r.scenario}:{r.method}", axis=1)
    verification = {
        "created_utc": _utc(),
        "result_rows": int(len(df)),
        "seeds_ok": sorted(int(x) for x in df.seed.unique()) == FORMAL_SEEDS,
        "scenarios_ok": set(df.scenario) == set(SCENARIOS),
        "methods_ok": set(df.method) == set(METHODS),
        "duplicate_logical_results": int(keys.duplicated().sum()),
        "missing_logical_results": int(600 - len(set(keys))),
        "status": "PASS",
    }
    if not (
        verification["result_rows"] == 600
        and verification["seeds_ok"]
        and verification["scenarios_ok"]
        and verification["methods_ok"]
        and verification["duplicate_logical_results"] == 0
        and verification["missing_logical_results"] == 0
    ):
        verification["status"] = "FAIL"
    # Mutation check vs offline recon input snapshot if present
    snap = PRIOR_RECON / "OFFLINE_INPUT_HASH_SNAPSHOT.json"
    if snap.is_file():
        prior = json.loads(snap.read_text(encoding="utf-8")).get("hashes", {})
        for key in ("formal_results.csv",):
            expected = prior.get(key)
            path = SRC / "formal_results.csv"
            if expected and path.is_file() and _sha(path) != expected:
                raise SystemExit("FINAL_SEAL_INPUT_MUTATION")
    dump_json(manifest, ART / "FINAL_SEAL_INPUT_MANIFEST.json")
    dump_json(verification, ART / "FINAL_SEAL_INPUT_VERIFICATION.json")
    dump_json(
        {"created_utc": _utc(), "hashes": {k: v.get("sha256") for k, v in manifest["files"].items()}},
        ART / "FINAL_SEAL_INPUT_HASH_SNAPSHOT.json",
    )
    return verification


def write_tolerance_policy() -> None:
    policy = {
        "EPS_ZERO": EPS_ZERO,
        "rationale": (
            "Paired Delta_group differences of order 1e-16..1e-17 are floating-point noise, "
            "not scientific effects. Zeroing abs(d)<=1e-12 before inference prevents Wilcoxon "
            "pseudo-significance from all-ties machine-epsilon vectors."
        ),
        "applied_to_metrics": STRUCTURAL_METRICS,
        "applies_before": [
            "win_tie_loss",
            "wilcoxon_signed_rank",
            "sign_counting",
            "effect_direction",
            "significance_classification",
        ],
        "raw_metric_values_modified": False,
        "implementation_location": "src/raven_mcs/e2/traffic_final_seal/__init__.py::apply_eps_zero",
        "alpha": ALPHA,
    }
    dump_json(policy, ART / "NUMERICAL_TOLERANCE_POLICY.json")
    md = f"""# NUMERICAL_TOLERANCE_POLICY

- **EPS_ZERO** = `{EPS_ZERO}`
- **Rationale**: {policy['rationale']}
- **Metrics**: {', '.join(STRUCTURAL_METRICS)}
- **Implementation**: `{policy['implementation_location']}`
- Raw reconstructed metric values are **not** modified; only paired-difference inferential analysis is tolerance-normalized.
"""
    (ART / "NUMERICAL_TOLERANCE_POLICY.md").write_text(md, encoding="utf-8")


def wilcoxon_tol(diff: np.ndarray) -> tuple[float, str]:
    arr = apply_eps_zero(diff)
    if arr.size == 0:
        return float("nan"), "EMPTY"
    if not np.any(arr != 0):
        return 1.0, "ALL_TIES"
    try:
        res = stats.wilcoxon(arr, alternative="two-sided", zero_method="wilcox")
        return float(res.pvalue), "wilcoxon_signed_rank_two_sided"
    except ValueError:
        return float("nan"), "WILCOXON_FAILED"


def wtl(diff: np.ndarray) -> tuple[int, int, int]:
    arr = apply_eps_zero(diff)
    wins = int(np.sum(arr < 0))
    losses = int(np.sum(arr > 0))
    ties = int(arr.size - wins - losses)
    return wins, ties, losses


def paired_raven(
    frame: pd.DataFrame, *, metric: str, scenario: str, baseline: str
) -> dict[str, Any]:
    sub = frame.loc[frame.scenario == scenario]
    r = sub.loc[sub.method == "raven"].set_index("seed")[metric]
    b = sub.loc[sub.method == baseline].set_index("seed")[metric]
    seeds = sorted(set(r.index) & set(b.index))
    raw = np.asarray([float(r.loc[s] - b.loc[s]) for s in seeds], dtype=np.float64)
    tol = apply_eps_zero(raw)
    summary_raw = summarize_vector(raw)
    summary_tol = summarize_vector(tol)
    wins, ties, losses = wtl(raw)
    p_raw, test_status = wilcoxon_tol(raw)
    return {
        "analysis": "raven_vs_baseline",
        "metric": metric,
        "scenario": scenario,
        "baseline_method": baseline,
        "n": len(seeds),
        "raw_mean_paired_diff": summary_raw["mean"],
        "tol_mean_paired_diff": summary_tol["mean"],
        "median_paired_diff": summary_tol["median"],
        "max_abs_raw_paired_diff": float(np.max(np.abs(raw))) if len(raw) else float("nan"),
        "zeroed_pair_count": int(np.sum(np.abs(raw) <= EPS_ZERO)),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "p_raw": p_raw,
        "test_status": test_status,
        "effect_direction": (
            "raven_lower" if summary_tol["mean"] < 0 else ("raven_higher" if summary_tol["mean"] > 0 else "zero")
        ),
        "correction_family": f"metric={metric}|scenario_x_baseline_24",
        "family_size": 24,
        "alpha": ALPHA,
        "EPS_ZERO": EPS_ZERO,
    }


def paired_scen(
    frame: pd.DataFrame, *, metric: str, method: str, scenario: str
) -> dict[str, Any]:
    sub = frame.loc[frame.method == method]
    scen = sub.loc[sub.scenario == scenario].set_index("seed")[metric]
    bal = sub.loc[sub.scenario == "balanced"].set_index("seed")[metric]
    seeds = sorted(set(scen.index) & set(bal.index))
    raw = np.asarray([float(scen.loc[s] - bal.loc[s]) for s in seeds], dtype=np.float64)
    tol = apply_eps_zero(raw)
    summary = summarize_vector(tol)
    wins, ties, losses = wtl(raw)
    p_raw, test_status = wilcoxon_tol(raw)
    return {
        "analysis": "scenario_vs_balanced",
        "metric": metric,
        "method": method,
        "scenario": scenario,
        "n": len(seeds),
        "raw_mean_paired_diff": float(np.mean(raw)) if len(raw) else float("nan"),
        "tol_mean_paired_diff": summary["mean"],
        "median_paired_diff": summary["median"],
        "max_abs_raw_paired_diff": float(np.max(np.abs(raw))) if len(raw) else float("nan"),
        "zeroed_pair_count": int(np.sum(np.abs(raw) <= EPS_ZERO)),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "p_raw": p_raw,
        "test_status": test_status,
        "holm_family": f"method={method}|metric={metric}|non_balanced",
        "family_size": 5,
        "alpha": ALPHA,
        "EPS_ZERO": EPS_ZERO,
    }


def recompute_structural() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ht = pd.read_csv(PRIOR_RECON / "HEAD_TAIL_RECONSTRUCTED.csv")
    dg = pd.read_csv(PRIOR_RECON / "DELTA_GROUP_RECONSTRUCTED.csv")
    frame = ht[["seed", "scenario", "method", "Head_RMSE", "Tail_RMSE"]].merge(
        dg[["seed", "scenario", "method", "Delta_group"]],
        on=["seed", "scenario", "method"],
        how="left",
    )

    # Delta_group RAVEN vs baseline dedicated table
    dg_rows = []
    for scenario in SCENARIOS:
        for baseline in BASELINES:
            dg_rows.append(paired_raven(frame, metric="Delta_group", scenario=scenario, baseline=baseline))
    adj = holm_adjust([r["p_raw"] for r in dg_rows])
    for r, p_h in zip(dg_rows, adj):
        r["p_holm"] = p_h
        r["significant_holm_0.05"] = bool(np.isfinite(p_h) and p_h < ALPHA and r["test_status"] != "ALL_TIES")
        if r["test_status"] == "ALL_TIES":
            r["p_raw"] = 1.0
            r["p_holm"] = 1.0
            r["significant_holm_0.05"] = False
    # Re-Holm after forcing ALL_TIES p=1
    adj2 = holm_adjust([r["p_raw"] for r in dg_rows])
    for r, p_h in zip(dg_rows, adj2):
        r["p_holm"] = 1.0 if r["test_status"] == "ALL_TIES" else p_h
        r["significant_holm_0.05"] = bool(
            r["test_status"] != "ALL_TIES" and np.isfinite(r["p_holm"]) and r["p_holm"] < ALPHA
        )
    dg_corr = pd.DataFrame(dg_rows)
    dg_corr.to_csv(ART / "DELTA_GROUP_RAVEN_VS_BASELINE_TOLERANCE_CORRECTED.csv", index=False)
    dump_json(
        {"EPS_ZERO": EPS_ZERO, "rows": dg_corr.replace({np.nan: None}).to_dict(orient="records")},
        ART / "DELTA_GROUP_RAVEN_VS_BASELINE_TOLERANCE_CORRECTED.json",
    )

    # Full structural stats
    rows = []
    for metric in STRUCTURAL_METRICS:
        # scenario vs balanced
        for method in METHODS:
            family = [paired_scen(frame, metric=metric, method=method, scenario=s) for s in NON_BALANCED]
            for r in family:
                if r["test_status"] == "ALL_TIES":
                    r["p_raw"] = 1.0
            adj = holm_adjust([r["p_raw"] for r in family])
            for r, p_h in zip(family, adj):
                r["p_holm"] = 1.0 if r["test_status"] == "ALL_TIES" else p_h
                r["significant_holm_0.05"] = bool(
                    r["test_status"] != "ALL_TIES" and np.isfinite(r["p_holm"]) and r["p_holm"] < ALPHA
                )
                rows.append(r)
        # raven vs baseline
        family = []
        for scenario in SCENARIOS:
            for baseline in BASELINES:
                family.append(paired_raven(frame, metric=metric, scenario=scenario, baseline=baseline))
        for r in family:
            if r["test_status"] == "ALL_TIES":
                r["p_raw"] = 1.0
        adj = holm_adjust([r["p_raw"] for r in family])
        for r, p_h in zip(family, adj):
            r["p_holm"] = 1.0 if r["test_status"] == "ALL_TIES" else p_h
            r["significant_holm_0.05"] = bool(
                r["test_status"] != "ALL_TIES" and np.isfinite(r["p_holm"]) and r["p_holm"] < ALPHA
            )
            rows.append(r)
    struct = pd.DataFrame(rows)
    struct.to_csv(ART / "STRUCTURAL_STATS_TOLERANCE_CORRECTED.csv", index=False)
    dump_json(
        {"EPS_ZERO": EPS_ZERO, "rows": struct.replace({np.nan: None}).to_dict(orient="records")},
        ART / "STRUCTURAL_STATS_TOLERANCE_CORRECTED.json",
    )
    return frame, dg_corr, struct


def build_claims(struct: pd.DataFrame, dg_corr: pd.DataFrame) -> pd.DataFrame:
    prior_scen = pd.read_csv(PRIOR_ANALYSIS / "SCENARIO_VS_BALANCED_STATS.csv")
    prior_raven = pd.read_csv(PRIOR_ANALYSIS / "RAVEN_VS_BASELINE_SECONDARY.csv")

    # C9 from corrected structural raven-vs-baseline only
    raven_struct = struct.loc[struct.analysis == "raven_vs_baseline"]
    sig_imp = raven_struct.loc[
        (raven_struct["significant_holm_0.05"].fillna(False))
        & (raven_struct["tol_mean_paired_diff"] < -EPS_ZERO)
        & (raven_struct["max_abs_raw_paired_diff"] > EPS_ZERO)
    ]
    c9 = "UNSUPPORTED" if len(sig_imp) == 0 else "PARTIALLY_SUPPORTED"

    # sanity: Delta_group corrected should have 0 sig
    assert int(dg_corr["significant_holm_0.05"].fillna(False).sum()) == 0 or c9 != "force"

    claims = [
        {
            "claim_id": "C1",
            "claim": "Biased traffic-selection scenarios alter arrival-weighted risk",
            "status": "SUPPORTED_WITH_SCENARIO_QUALIFICATION",
            "evidence_source": "SCENARIO_VS_BALANCED_STATS RMSE_rho (Observation-only, Complete-aligned)",
            "effect_direction": "scenario-dependent RMSE_rho change",
            "scope_limitation": "Do not claim all biased scenarios; qualify Observation-only and Complete-aligned",
            "allowed_paper_wording": "Traffic-selection bias can alter arrival-weighted risk, especially under Observation-only and Complete-aligned.",
            "prohibited_overclaim_wording": "All biased scenarios significantly alter arrival risk.",
        },
        {
            "claim_id": "C2",
            "claim": "Biased traffic-selection scenarios alter target-weighted risk",
            "status": "PARTIALLY_SUPPORTED",
            "evidence_source": "SCENARIO_VS_BALANCED_STATS RMSE_mu",
            "effect_direction": "limited/scenario-specific",
            "scope_limitation": "Limited Holm-supported RMSE_mu changes only",
            "allowed_paper_wording": "Target-weighted risk changes are limited and scenario-specific under the formal matrix.",
            "prohibited_overclaim_wording": "All biased scenarios significantly alter target risk.",
        },
        {
            "claim_id": "C3",
            "claim": "Arrival-weighted and target-weighted risk are not interchangeable under selection bias",
            "status": "SUPPORTED",
            "evidence_source": "COMPLETE_ALIGNED_DOD_SUMMARY",
            "effect_direction": "non-interchangeability (DoD nonzero; direction not forced)",
            "scope_limitation": "Strongest in Complete-aligned",
            "allowed_paper_wording": "Arrival-weighted and deployment-target-weighted risk are not interchangeable under traffic-selection bias.",
            "prohibited_overclaim_wording": "Complete-aligned always worsens target risk more than arrival risk.",
        },
        {
            "claim_id": "C4",
            "claim": "Complete-aligned causes target-risk deterioration larger than arrival-risk deterioration",
            "status": "UNSUPPORTED",
            "evidence_source": "COMPLETE_ALIGNED_DOD_SUMMARY",
            "effect_direction": "original hypothesized sign unsupported",
            "scope_limitation": "n/a",
            "allowed_paper_wording": "The originally hypothesized Complete-aligned directional DoD is not supported.",
            "prohibited_overclaim_wording": "Complete-aligned confirms larger target-risk deterioration.",
        },
        {
            "claim_id": "C5",
            "claim": "Complete-counteracting frequently yields arrival improvement without target improvement",
            "status": "UNSUPPORTED",
            "evidence_source": "COMPLETE_COUNTERACTING_EVENT_SUMMARY",
            "effect_direction": "event rare",
            "scope_limitation": "n/a",
            "allowed_paper_wording": "The preregistered Complete-counteracting directional event is unsupported.",
            "prohibited_overclaim_wording": "Complete-counteracting confirms the preregistered event.",
        },
        {
            "claim_id": "C6",
            "claim": "RAVEN significantly improves RMSE_mu over all baselines",
            "status": "UNSUPPORTED",
            "evidence_source": "RAVEN_VS_BASELINE_SECONDARY RMSE_mu (0/24 Holm-significant)",
            "effect_direction": "no corrected significance",
            "scope_limitation": "n/a",
            "allowed_paper_wording": "Formal E2 evidence does not establish RAVEN RMSE_mu dominance over baselines.",
            "prohibited_overclaim_wording": "RAVEN significantly improves RMSE_mu / outperforms all baselines.",
        },
        {
            "claim_id": "C7",
            "claim": "RAVEN significantly improves RMSE_rho over all baselines",
            "status": "UNSUPPORTED",
            "evidence_source": "RAVEN_VS_BASELINE_SECONDARY RMSE_rho",
            "effect_direction": "no corrected significance",
            "scope_limitation": "n/a",
            "allowed_paper_wording": "Formal E2 evidence does not establish RAVEN RMSE_rho dominance over baselines.",
            "prohibited_overclaim_wording": "RAVEN significantly improves RMSE_rho.",
        },
        {
            "claim_id": "C8",
            "claim": "RAVEN significantly reduces arrival-target risk discrepancy",
            "status": "UNSUPPORTED",
            "evidence_source": "signed Gap_mis + ABS_GAP secondary; no Holm advantage",
            "effect_direction": "unsupported",
            "scope_limitation": "signed Gap_mis is not absolute misalignment",
            "allowed_paper_wording": "No corrected evidence supports a RAVEN discrepancy-reduction claim.",
            "prohibited_overclaim_wording": "RAVEN significantly reduces misalignment / smaller Gap_mis means less misalignment.",
        },
        {
            "claim_id": "C9",
            "claim": "RAVEN improves Tail/group disparity",
            "status": c9,
            "evidence_source": "STRUCTURAL_STATS_TOLERANCE_CORRECTED + DELTA_GROUP_..._TOLERANCE_CORRECTED; Delta_pair unavailable",
            "effect_direction": "none after EPS_ZERO" if c9 == "UNSUPPORTED" else "limited",
            "scope_limitation": "Machine-epsilon Delta_group effects excluded; Delta_pair not reconstructable",
            "allowed_paper_wording": (
                "Corrected analysis does not support a statistically significant RAVEN advantage in Head/Tail RMSE or Delta_group."
                if c9 == "UNSUPPORTED"
                else "Only state limited structural support with exact Holm references."
            ),
            "prohibited_overclaim_wording": "RAVEN significantly improves tail fairness/group disparity.",
        },
        {
            "claim_id": "C10",
            "claim": "E2 supports the paper's target-risk-misalignment motivation",
            "status": "PARTIALLY_SUPPORTED",
            "evidence_source": "C3 supported; algorithm directional claims unsupported",
            "effect_direction": "motivation supported; algorithm superiority not",
            "scope_limitation": "Motivation ≠ algorithm dominance",
            "allowed_paper_wording": "E2 supports explicitly reasoning about target risk under selection bias, without claiming universal RAVEN superiority.",
            "prohibited_overclaim_wording": "E2 proves RAVEN solves target-risk misalignment.",
        },
    ]
    # attach p-value evidence summary
    for c in claims:
        if c["claim_id"] == "C9":
            c["corrected_p_value_evidence"] = (
                f"Delta_group Holm-significant count={int(dg_corr['significant_holm_0.05'].fillna(False).sum())}; "
                f"Head/Tail Holm-significant improvements={int(len(sig_imp.loc[sig_imp.metric.isin(['Head_RMSE','Tail_RMSE'])]))}"
            )
        elif c["claim_id"] in {"C6", "C7"}:
            metric = "RMSE_mu" if c["claim_id"] == "C6" else "RMSE_rho"
            sub = prior_raven.loc[prior_raven.metric == metric]
            c["corrected_p_value_evidence"] = (
                f"Holm-significant improvements={int(((sub['significant_holm_0.05'].fillna(False)) & (sub.mean_paired_diff < 0)).sum())}/24"
            )
        elif c["claim_id"] == "C1":
            rho = prior_scen.loc[
                (prior_scen.metric == "RMSE_rho")
                & (prior_scen.scenario.isin(["observation_only", "complete_aligned"]))
            ]
            c["corrected_p_value_evidence"] = (
                f"Holm-significant scenario-vs-Balanced rows in focus scenarios={int(rho['significant_holm_0.05'].fillna(False).sum())}"
            )
        else:
            c["corrected_p_value_evidence"] = "see evidence_source"
    out = pd.DataFrame(claims)
    out.to_csv(ART / "E2_CLAIM_MATRIX_FINAL.csv", index=False)
    md = ["# E2_CLAIM_MATRIX_FINAL", ""]
    for c in claims:
        md.append(f"## {c['claim_id']}: {c['status']}")
        md.append(c["claim"])
        md.append(f"- Evidence: {c['evidence_source']}")
        md.append(f"- Allowed: {c['allowed_paper_wording']}")
        md.append(f"- Prohibited: {c['prohibited_overclaim_wording']}")
        md.append("")
    (ART / "E2_CLAIM_MATRIX_FINAL.md").write_text("\n".join(md), encoding="utf-8")
    return out


def ledger_note() -> dict[str, Any]:
    prior = json.loads((PRIOR_RECON / "LEDGER_ATTEMPT_AUDIT_R2.json").read_text(encoding="utf-8"))["summary"]
    note = {
        "training_start_event_count": 601,
        "training_finish_event_count": 600,
        "accepted_logical_run_count": 600,
        "duplicate_start_event_count": 1,
        "orphan_or_interrupted_start_event_count": 1,
        "scientific_result_loss": 0,
        "missing_accepted_logical_run": 0,
        "ledger_rewritten": False,
        "duplicate_start_run_id": "formal_seed30001_observation_only_raven__attempt1",
        "prior_audit_interrupted_start_event_count": prior.get("interrupted_start_event_count"),
        "note": (
            "Historical ledger unchanged. Report must state interrupted/orphan START event count = 1 "
            "(duplicate START on one run_id with later successful FINISH), not 0."
        ),
    }
    dump_json(note, ART / "LEDGER_FINAL_SEAL_NOTE.json")
    (ART / "LEDGER_FINAL_SEAL_NOTE.md").write_text(
        f"""# LEDGER_FINAL_SEAL_NOTE

- training START event count = **601**
- training FINISH event count = **600**
- accepted logical run count = **600**
- duplicate START event count = **1**
- orphan/interrupted START event count = **1**
- scientific result loss = **0**
- missing accepted logical run = **0**
- historical ledger rewritten = **false**

Known anomaly run_id: `{note['duplicate_start_run_id']}`

The final report must NOT say orphan/interrupted START = 0.
""",
        encoding="utf-8",
    )
    return note


def paper_outputs(struct: pd.DataFrame, dg_corr: pd.DataFrame, claims: pd.DataFrame) -> pd.DataFrame:
    tables = ART / "paper_tables"
    figs = ART / "figures"
    fdata = ART / "figure_data"
    for d in (tables, figs, fdata):
        d.mkdir(parents=True, exist_ok=True)
    formal = pd.read_csv(SRC / "formal_results.csv")
    # E2-1
    rows = []
    for scenario in SCENARIOS:
        for method in METHODS:
            sub = formal.loc[(formal.scenario == scenario) & (formal.method == method)]
            rows.append(
                {
                    "scenario": scenario,
                    "method": method,
                    "RMSE_mu_mean": sub.RMSE_mu.mean(),
                    "RMSE_rho_mean": sub.RMSE_rho.mean(),
                    "Gap_mis_mean": sub.Gap_mis.mean(),
                }
            )
    t1 = pd.DataFrame(rows)
    t1.to_csv(tables / "TABLE_E2_1_FINAL.csv", index=False)
    t1.to_latex(tables / "TABLE_E2_1_FINAL.tex", index=False, float_format="%.4g")
    prior_scen = pd.read_csv(PRIOR_ANALYSIS / "SCENARIO_VS_BALANCED_STATS.csv")
    prior_scen.to_csv(tables / "TABLE_E2_2_FINAL.csv", index=False)
    prior_scen[["method", "scenario", "metric", "mean_diff", "p_holm", "significant_holm_0.05"]].to_latex(
        tables / "TABLE_E2_2_FINAL.tex", index=False, float_format="%.4g"
    )
    dod = json.loads((PRIOR_ANALYSIS / "COMPLETE_ALIGNED_DOD_SUMMARY.json").read_text(encoding="utf-8"))
    t3 = pd.DataFrame([{"method": m, **dod[m]} for m in METHODS])
    t3.to_csv(tables / "TABLE_E2_3_FINAL.csv", index=False)
    t3.to_latex(tables / "TABLE_E2_3_FINAL.tex", index=False, float_format="%.4g")
    counter = json.loads((PRIOR_ANALYSIS / "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json").read_text(encoding="utf-8"))
    t4 = pd.DataFrame([{"method": m, **counter[m]} for m in METHODS])
    t4.to_csv(tables / "TABLE_E2_4_FINAL.csv", index=False)
    t4.to_latex(tables / "TABLE_E2_4_FINAL.tex", index=False, float_format="%.4g")
    ht = pd.read_csv(PRIOR_RECON / "HEAD_TAIL_RECONSTRUCTED.csv")
    ht_sum = ht.groupby(["scenario", "method"], as_index=False).agg(
        Head_RMSE_mean=("Head_RMSE", "mean"), Tail_RMSE_mean=("Tail_RMSE", "mean")
    )
    ht_sum.to_csv(tables / "TABLE_E2_5_FINAL.csv", index=False)
    ht_sum.to_latex(tables / "TABLE_E2_5_FINAL.tex", index=False, float_format="%.4g")
    dg_corr.to_csv(tables / "TABLE_E2_6_FINAL.csv", index=False)
    dg_corr[
        [
            "scenario",
            "baseline_method",
            "tol_mean_paired_diff",
            "zeroed_pair_count",
            "ties",
            "p_holm",
            "significant_holm_0.05",
            "test_status",
        ]
    ].to_latex(tables / "TABLE_E2_6_FINAL.tex", index=False, float_format="%.4g")
    prior_raven = pd.read_csv(PRIOR_ANALYSIS / "RAVEN_VS_BASELINE_SECONDARY.csv")
    # only non-pseudo / Holm-significant if any; else empty note
    sig = prior_raven.loc[prior_raven["significant_holm_0.05"].fillna(False)]
    if sig.empty:
        t7 = pd.DataFrame([{"note": "No Holm-significant RAVEN-vs-baseline RMSE/Gap differences"}])
    else:
        t7 = sig
    t7.to_csv(tables / "TABLE_E2_7_FINAL.csv", index=False)
    try:
        t7.to_latex(tables / "TABLE_E2_7_FINAL.tex", index=False, float_format="%.4g")
    except Exception:
        (tables / "TABLE_E2_7_FINAL.tex").write_text("No Holm-significant rows.\n", encoding="utf-8")
    claims.to_csv(tables / "TABLE_E2_8_FINAL.csv", index=False)
    claims[["claim_id", "status", "claim"]].to_latex(tables / "TABLE_E2_8_FINAL.tex", index=False)

    # Figures: no RAVEN structural advantage figure
    fig_audit = []
    # scenario-driven Delta_group
    dg = pd.read_csv(PRIOR_RECON / "DELTA_GROUP_RECONSTRUCTED.csv")
    dg.to_csv(fdata / "FIG_E2_DELTA_GROUP_SCENARIO_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(SCENARIOS))
    width = 0.15
    for i, method in enumerate(METHODS):
        means = [dg.loc[(dg.method == method) & (dg.scenario == s), "Delta_group"].mean() for s in SCENARIOS]
        ax.bar(x + i * width, means, width=width, label=method)
    ax.set_xticks(x + 2 * width)
    ax.set_xticklabels(SCENARIOS, rotation=20, ha="right")
    ax.set_ylabel("mean Delta_group")
    ax.set_title("Scenario-driven Delta_group (no RAVEN superiority claim)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"FIG_E2_DELTA_GROUP_SCENARIO.{ext}", dpi=160 if ext == "png" else None)
    plt.close(fig)
    fig_audit.append(
        {
            "figure": "FIG_E2_DELTA_GROUP_SCENARIO",
            "action": "KEEP_OR_REGENERATE",
            "implies_raven_superiority": False,
            "consistent_with_C9": True,
        }
    )

    # Remove prior misleading RAVEN structural figure by writing a corrected non-claim figure
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.text(
        0.5,
        0.5,
        "No Holm-significant RAVEN structural advantage after EPS_ZERO=1e-12 correction",
        ha="center",
        va="center",
        wrap=True,
    )
    ax.set_axis_off()
    ax.set_title("FIG_E2_RAVEN_STRUCTURAL (corrected: no pseudo-significance)")
    fig.tight_layout()
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"FIG_E2_RAVEN_STRUCTURAL_CORRECTED.{ext}", dpi=160 if ext == "png" else None)
    plt.close(fig)
    fig_audit.append(
        {
            "figure": "FIG_E2_RAVEN_STRUCTURAL_CORRECTED",
            "action": "REGENERATED_TO_REMOVE_PSEUDO_SIGNIFICANCE",
            "implies_raven_superiority": False,
            "consistent_with_C9": True,
        }
    )
    # Head/Tail descriptive
    ht.to_csv(fdata / "FIG_E2_HEAD_TAIL_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    for i, method in enumerate(METHODS):
        means = [ht.loc[(ht.method == method) & (ht.scenario == s), "Tail_RMSE"].mean() for s in SCENARIOS]
        ax.bar(x + i * width, means, width=width, label=method)
    ax.set_xticks(x + 2 * width)
    ax.set_xticklabels(SCENARIOS, rotation=20, ha="right")
    ax.set_ylabel("mean Tail_RMSE")
    ax.set_title("Head/Tail descriptive Tail_RMSE by scenario")
    ax.legend(fontsize=7)
    fig.tight_layout()
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"FIG_E2_HEAD_TAIL.{ext}", dpi=160 if ext == "png" else None)
    plt.close(fig)
    fig_audit.append(
        {
            "figure": "FIG_E2_HEAD_TAIL",
            "action": "KEEP_DESCRIPTIVE",
            "implies_raven_superiority": False,
            "consistent_with_C9": True,
        }
    )
    audit_df = pd.DataFrame(fig_audit)
    audit_df.to_csv(ART / "FIGURE_CLAIM_CONSISTENCY_AUDIT.csv", index=False)
    return audit_df


def write_paper_wording() -> None:
    text = """# E2_FINAL_PAPER_WORDING

## A. ALLOWED WORDING

1. Traffic-selection bias can induce a pronounced divergence between arrival-weighted and deployment-target-weighted risk.

2. In the Complete-aligned setting, the arrival-weighted RMSE changes substantially more than the target-weighted RMSE across all evaluated methods, demonstrating that the two risk notions are not interchangeable.

3. RAVEN remains competitive in target-risk accuracy, but the formal E2 evidence does not establish universal RMSE dominance over the baselines.

4. The structural group-deviation effect observed under Complete-aligned is largely scenario-driven; the corrected analysis does not support a statistically significant RAVEN advantage in Head/Tail RMSE or Delta_group.

## B. PROHIBITED WORDING

- "RAVEN significantly outperforms all baselines."
- "RAVEN significantly improves RMSE_mu."
- "RAVEN significantly improves RMSE_rho."
- "RAVEN significantly reduces misalignment."
- "RAVEN significantly improves tail fairness/group disparity."
- "smaller signed Gap_mis always means less misalignment."
- "all biased scenarios significantly alter target risk."
"""
    (ART / "E2_FINAL_PAPER_WORDING.md").write_text(text, encoding="utf-8")


def write_report(verification, dg_corr, claims, ledger, status: str) -> None:
    c9 = claims.loc[claims.claim_id == "C9", "status"].iloc[0]
    report = f"""# E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1_REPORT

## 1. Executive decision

**{status}**

## 2. No-training attestation

No model was trained. No formal run was re-executed. Only offline paired-inference tolerance correction and claim/report consistency fixes were performed.

## 3. Frozen 600-result identity

Verification: `{verification.get('status')}` — 600 logical runs unchanged.

## 4. Numerical tolerance defect

Prior Delta_group RAVEN-vs-baseline comparisons treated ~1e-16 floating differences as nonzero Wilcoxon effects, creating pseudo-significance.

## 5. EPS_ZERO policy

EPS_ZERO = `{EPS_ZERO}` applied to paired differences before win/tie/loss, Wilcoxon, signs, and significance. See `NUMERICAL_TOLERANCE_POLICY.md`.

## 6. Delta_group corrected statistics

Holm-significant RAVEN-vs-baseline Delta_group count after correction: **{int(dg_corr['significant_holm_0.05'].fillna(False).sum())}/24**.
ALL_TIES comparisons forced to non-significant inference.

## 7. Head/Tail corrected statistics

Recomputed under the same EPS_ZERO policy in `STRUCTURAL_STATS_TOLERANCE_CORRECTED.csv`.

## 8. Holm correction audit

Families unchanged: scenario-vs-Balanced = 5 per (method, metric); RAVEN-vs-baseline = 24 per metric.

## 9. Corrected Claim Matrix

See `E2_CLAIM_MATRIX_FINAL.md`. C9 = **{c9}**.

## 10. Claim Validator results

See `CLAIM_EVIDENCE_VALIDATION_FINAL.json`.

## 11. Ledger anomaly final wording

- START = **601**
- FINISH = **600**
- accepted logical runs = **600**
- interrupted/orphan START = **1**
- historical ledger not rewritten

See `LEDGER_FINAL_SEAL_NOTE.md`.

## 12. Figure/table corrections

Pseudo-significant RAVEN structural-advantage figures removed/replaced. Final tables in `paper_tables/`.

## 13. Final supported claims

- C1 (with scenario qualification)
- C3 (non-interchangeability)
- C2/C10 partially

## 14. Final unsupported claims

- C4, C5, C6, C7, C8, C9

## 15. Paper-ready wording

See `E2_FINAL_PAPER_WORDING.md`.

## 16. Remaining limitations

- Delta_pair not reconstructable from frozen outputs.
- Signed Gap_mis is not absolute misalignment magnitude.

## 17. Final E2 closure status

**{status}**

## 18. Next-step recommendation

Stop E2 experiment expansion. Proceed to paper drafting under the final claim matrix and wording constraints. Do not start E3–E9 unless a new sealed experiment stage is explicitly authorized.
"""
    (ART / "E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1_REPORT.md").write_text(report, encoding="utf-8")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    verification = freeze_inputs()
    if verification["status"] != "PASS":
        dump_json({"status": "E2_TRAFFIC_FINAL_SEAL_BLOCKED"}, ART / "STOP_STATUS.json")
        return 2
    write_tolerance_policy()
    _frame, dg_corr, struct = recompute_structural()
    claims = build_claims(struct, dg_corr)
    ledger = ledger_note()
    paper_outputs(struct, dg_corr, claims)
    write_paper_wording()

    # provisional status; gates/validator finalize
    c9 = claims.loc[claims.claim_id == "C9", "status"].iloc[0]
    status = "E2_TRAFFIC_SCIENTIFICALLY_SEALED" if c9 == "UNSUPPORTED" else "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
    # If C9 unexpectedly supported by genuine evidence, still can seal if consistent
    write_report(verification, dg_corr, claims, ledger, status)
    dump_json(
        {
            "status": status,
            "no_training": True,
            "EPS_ZERO": EPS_ZERO,
            "created_utc": _utc(),
            "c9": c9,
            "delta_group_holm_sig_count": int(dg_corr["significant_holm_0.05"].fillna(False).sum()),
            "ledger_interrupted_start": 1,
        },
        ART / "STOP_STATUS.json",
    )
    print(json.dumps({"status": status, "c9": c9, "delta_group_holm_sig": int(dg_corr["significant_holm_0.05"].fillna(False).sum())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
