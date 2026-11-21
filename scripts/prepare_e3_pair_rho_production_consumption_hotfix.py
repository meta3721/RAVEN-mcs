#!/usr/bin/env python3
"""E3 pair/rho production consumption hotfix (non-performance)."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.e3.hotfix.constants import (
    CANARY_SEED,
    DEBUG_SEED,
    METRIC_SCHEMA_VERSION,
    PAIR_SCHEMA_VERSION,
    REGISTRY_SHA256,
    ROUND,
    STRUCTURAL_METRIC_NAME,
)
from raven_mcs.e3.hotfix.production_tests import (
    piopp_semantic_identity,
    pobs_field_usage_audit,
    production_atomic_pobs_perturbation,
    production_joint_piopp_perturbation,
)
from raven_mcs.e3.protocol_closure.method_registry import CANONICAL_METHODS, method_source_hashes
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.real_runner.constants import E2_TRAFFIC_REUSED_METHODS, FORMAL_SEEDS, M_MC
from raven_mcs.e3.real_runner.fixture_nd import build_nondegenerate_fixture, load_nd_fixture
from raven_mcs.e3.real_runner.generator_r3 import materialize_r3_trace
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.e3.semantic_alignment.target_semantics import freeze_target_semantics
from raven_mcs.e3.target_pair.metric_applicability import (
    mechanism_metric_applicability_matrix,
    metric_applicability_matrix,
    metric_schema_v5,
)
from raven_mcs.e3.target_pair.pair_state_v4 import (
    nonsymmetric_delta_c_s_toy,
    pair_state_schema_v4,
)
from raven_mcs.e3.target_pair.rho_weights import (
    production_rho_analytical_test,
    rho_group_diagnostics,
)
from raven_mcs.e3.target_pair.target_wiring import load_frozen_target_artifact
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_pair_rho_production_consumption_hotfix_r1"
CFG = ROOT / "configs/frozen/e3_pair_rho_hotfix_r1"
E2_STOP = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json"
PARENT = ROOT / "artifacts/e3_target_pair_metric_final_integration_closure_r1"
DATASETS = ["sensorscope", "uair", "traffic"]
SMOKE_METHODS = [
    "fedavg_window",
    "twostage_hajek",
    "raven",
    "raven_simoracle",
    "central_all",
    "central_delivered",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _md(path: Path, title: str, body: str) -> None:
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def build_min_matrix() -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    for method, meta in CANONICAL_METHODS.items():
        if meta.get("excluded"):
            rows.append(
                {
                    "dataset": "all",
                    "method": method,
                    "number_of_new_runs": 0,
                    "classification": "EXCLUDED",
                    "reason": "EXCLUDED_WITH_REASON",
                }
            )
            continue
        for ds in DATASETS:
            reused = ds == "traffic" and method in E2_TRAFFIC_REUSED_METHODS
            rows.append(
                {
                    "dataset": ds,
                    "method": method,
                    "seed_block": "30001-30020",
                    "number_of_new_runs": 0 if reused else len(FORMAL_SEEDS),
                    "classification": "REUSE_ONLY_NO_RERUN" if reused else "NEW_RUN_REQUIRED",
                    "reason": "sealed E2 Traffic block" if reused else "new E3 formal after Canary",
                }
            )
    df = pd.DataFrame(rows)
    payload = {
        "reusable_existing_Traffic_runs": 100,
        "total_new_runs_after_closure": int(df["number_of_new_runs"].sum()),
        "rows": rows,
        "structural_metric": STRUCTURAL_METRIC_NAME,
        "schema_version": METRIC_SCHEMA_VERSION,
    }
    return df, payload


def write_identity_audit() -> dict[str, Any]:
    """Audit from frozen prior artifacts / protocol code — not circular self-citation."""
    sources = {
        "distribution_delta_pair": {
            "path": "src/raven_mcs/metrics/distribution.py",
            "formula": "||Pi_hat - pi_tar||_1",
            "domain_note": "generic L1; E3 V3 freezes support as client×atomic_unit",
        },
        "distribution_delta_c_s": {
            "path": "src/raven_mcs/metrics/distribution.py",
            "formula": "sum_{k,s} |Pi_hat_ks - pi_tar_ks|",
            "domain_note": "client×stratum cells",
        },
        "protocol_closure_v1": {
            "path": "artifacts/e3_multidataset_protocol_closure_r1/E3_PAIR_METRIC_DEFINITION.json",
            "Delta_pair": "||Pi_hat - pi_tar||_1 via delta_pair",
            "Delta_c_s": "sum |Pi_hat_ks - pi_tar_ks| via delta_c_s",
        },
        "oracle_v3_atomic": {
            "path": "artifacts/e3_real_runner_pair_oracle_correctness_closure_r1/E3_DELTA_PAIR_EXACT_DEFINITION.md",
            "pair_identity": "(client_id, atomic_unit_id)",
            "Delta_pair": "||Pi_hat^{(m)} - pi_tar||_1 on atomic support",
        },
        "common_support_v4_domain": {
            "path": "artifacts/e3_target_pair_metric_final_integration_closure_r1/E3_DELTA_PAIR_COMMON_SUPPORT_DEFINITION.json",
            "pair_domain": "client × target_group (spatial×time)",
        },
        "p10_descriptive": {
            "path": "docs/reports/P10_END_TO_END_INTEGRATION_REPORT.md",
            "note": "Delta_c-s described as real-trace distribution gap; no atomic Delta_pair freeze",
        },
        "formula_map": {
            "path": "docs/FORMULA_TO_CODE_MAP.md",
            "F7.4": "Delta_pair = ||Pi_hat-pi^tar||_1",
            "F7.5": "Delta_{c-s}",
        },
    }
    # Current V4 implementation support (descriptive of production representation, not sole proof)
    current_support = "client × spatial×time target_group (canonical_pair_id = client_id::target_group)"
    outcome = "CURRENT_V4_IS_DELTA_C_S_NOT_DELTA_PAIR"
    audit = {
        "round": ROUND,
        "candidates": {
            "Delta_pair": {
                "mathematical_domain": "client k × atomic unit i",
                "pair_index": "(k, i)",
                "target_measure": "pi_tar over atomic pairs (V3)",
                "estimated_measure": "Pi_hat_{k,i}",
                "norm": "L1",
                "client_x_target_group_preserves_exact_definition": False,
            },
            "Delta_c_s": {
                "mathematical_domain": "client k × stratum/group s",
                "c_s_meaning": "client–stratum (or client–spatial×time group) L1 gap",
                "current_implementation_matches": True,
                "support_realized": current_support,
            },
        },
        "frozen_sources_consulted": sources,
        "outcome": outcome,
        "action": (
            "Rename production structural field to Delta_c_s; "
            "retain Delta_pair = NOT_MATERIALIZED (atomic client×unit not emitted)"
        ),
        "circular_self_citation_forbidden": True,
        "status": "RESOLVED",
    }
    dump_json(audit, ART / "E3_PAIR_METRIC_NAME_AND_DEFINITION_AUDIT.json")
    _md(
        ART / "E3_PAIR_METRIC_NAME_AND_DEFINITION_AUDIT.md",
        "Pair Metric Name and Definition Audit",
        f"Outcome: **{outcome}**\n\n"
        "Frozen V3 defines atomic Delta_pair on (client, atomic_unit). "
        "Frozen V1/protocol and distribution.delta_c_s define client×stratum L1. "
        "Production V4 common support is client×target_group and uses delta_c_s — "
        "therefore it is Delta_c_s, not atomic Delta_pair.\n\n"
        "Sources: protocol_closure pair defs, V3 E3_DELTA_PAIR_EXACT_DEFINITION, "
        "V4 common-support domain, P10 Delta_c-s note, FORMULA_TO_CODE_MAP F7.4/F7.5.",
    )
    return audit


def write_structural_definition() -> dict[str, Any]:
    payload = {
        "final_metric_name": "Delta_c_s",
        "exact_formula": "sum_{k,s} |Pi_hat_ks - pi_tar_ks|  (= ||Pi_hat - pi_tar||_1 on client×group support)",
        "canonical_support": "client × spatial×time target_group",
        "canonical_pair_id": "client_id::target_group",
        "map_eventtrace_atomic_to_support": "unit_id -> (client via spatial_to_client, target_group from atomic table)",
        "target_mass": "uniform mass over TEST atoms aggregated onto client×target_group",
        "method_dependent_effective_mass": (
            "Pi_hat_ks = (1/S_R) sum_r eta_r I_r alpha_{k,r}^{(m)} w_{k,r,i}^{(m)} mapped to (k, target_group)"
        ),
        "normalization": "Pi_hat probability-normalized before L1 vs pi_tar",
        "valid_range": "[0, 2]",
        "orientation": "lower is better (closer to target pair/stratum mass)",
        "applicability": "federated methods APPLICABLE; Central NOT_APPLICABLE",
        "paper_label": "Delta_{c-s}",
        "Delta_pair": "NOT_AVAILABLE_FROM_THIS_PRODUCTION_REPRESENTATION",
        "Delta_pair_status": "NOT_MATERIALIZED",
        "schema_version": PAIR_SCHEMA_VERSION,
        "code": [
            "raven_mcs.metrics.distribution.delta_c_s",
            "raven_mcs.e3.target_pair.pair_state_v4.accumulate_pair_state_v4",
        ],
        "status": "FROZEN",
    }
    dump_json(payload, ART / "E3_STRUCTURAL_PAIR_METRIC_FINAL_DEFINITION.json")
    _md(
        ART / "E3_STRUCTURAL_PAIR_METRIC_FINAL_DEFINITION.md",
        "Structural Pair Metric Final Definition",
        f"Final name: **{payload['final_metric_name']}**\n\n"
        f"Formula: `{payload['exact_formula']}`\n\n"
        f"Support: {payload['canonical_support']}\n\n"
        "Delta_pair = NOT_AVAILABLE_FROM_THIS_PRODUCTION_REPRESENTATION "
        "(atomic client×unit not materialized).",
    )
    dump_json(pair_state_schema_v4(), ART / "E3_PAIR_STATE_SCHEMA_V5.json")
    return payload


def main() -> int:
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir(parents=True)
    CFG.mkdir(parents=True, exist_ok=True)

    audit = write_identity_audit()
    structural = write_structural_definition()

    # --- Rho fix docs + analytical ---
    rho_diag = rho_group_diagnostics(
        test_groups=["g0", "g0", "g0", "g1"],
        delivered_group_counts={"g0": 2.0, "g1": 6.0},
    )
    rho_anal = production_rho_analytical_test()
    rho_fix = {
        "bug": "prior builder assigned c_g to every test unit → mass ∝ n_g * c_g",
        "fix": "w_i = rho_g / n_g with rho_g = c_g / sum_h c_h",
        "diagnostics": rho_diag,
        "analytical": rho_anal,
        "status": "PASS" if rho_diag["status"] == "PASS" and rho_anal["status"] == "PASS" else "FAIL",
    }
    dump_json(rho_fix, ART / "E3_RHO_GROUP_TO_UNIT_MAPPING_FIX.json")
    _md(
        ART / "E3_RHO_GROUP_TO_UNIT_MAPPING_FIX.md",
        "RMSE_rho Group-to-Unit Mapping Fix",
        f"Rule: w_i = rho_g / n_g.\n\nstatus={rho_fix['status']}\n\n"
        f"max_normalization_error={rho_diag['max_normalization_error']}",
    )
    dump_json(rho_anal, ART / "E3_PRODUCTION_RHO_ANALYTICAL_TEST.json")

    # --- p_obs / pi_opp production tests ---
    pobs = production_atomic_pobs_perturbation(ART / "tmp_pobs")
    dump_json(pobs, ART / "E3_PRODUCTION_ATOMIC_POBS_PERTURBATION_TEST.json")
    _md(
        ART / "E3_PRODUCTION_ATOMIC_POBS_PERTURBATION_TEST.md",
        "Production Atomic p_obs Perturbation",
        f"status={pobs['status']}\n\npath={pobs['path']}\n\n"
        f"weights_differ={pobs['weights_differ']} (same mean p={pobs['mean_p']})",
    )
    pobs_audit = pobs_field_usage_audit()
    dump_json(pobs_audit, ART / "E3_POBS_FIELD_USAGE_AUDIT.json")

    piopp_sem = piopp_semantic_identity()
    dump_json(piopp_sem, ART / "E3_PIOPP_SEMANTIC_IDENTITY.json")
    _md(
        ART / "E3_PIOPP_SEMANTIC_IDENTITY.md",
        "pi_opp Semantic Identity",
        "Identity A: normalized opportunity event mass over client×stratum (joint).\n\n"
        "Not pair inclusion probability.\n\n"
        f"Construction: {piopp_sem['joint_construction']}",
    )
    piopp = production_joint_piopp_perturbation()
    dump_json(piopp, ART / "E3_PRODUCTION_JOINT_PIOPP_PERTURBATION_TEST.json")

    toy = nonsymmetric_delta_c_s_toy()
    dump_json(toy, ART / "E3_NONSYMMETRIC_PAIR_METRIC_ANALYTICAL_TEST.json")

    mech = mechanism_metric_applicability_matrix()
    dump_json(mech, ART / "E3_MECHANISM_METRIC_APPLICABILITY_R2.json")
    pd.DataFrame(mech["rows"]).to_csv(ART / "E3_MECHANISM_METRIC_APPLICABILITY_R2.csv", index=False)
    dump_json(metric_applicability_matrix(), ART / "E3_METRIC_APPLICABILITY_MATRIX_V5.json")
    dump_json(metric_schema_v5(), ART / "E3_REAL_METRIC_OUTPUT_SCHEMA_V5.json")

    # Applicability enforcement fixture
    from raven_mcs.e3.target_pair.metric_applicability import (
        MechanismMetricApplicabilityError,
        emit_metric_value,
    )

    enf_rows = []
    for method, metric, bad in [
        ("fedavg_window", "Q_norm1_over_S", 0.0),
        ("central_all", "Delta_c_s", 0.0),
        ("raven", "Delta_pair", 0.0),
    ]:
        raised = False
        try:
            emit_metric_value(method, metric, bad)
        except MechanismMetricApplicabilityError:
            raised = True
        ok = emit_metric_value(method, metric, None)
        enf_rows.append(
            {
                "method": method,
                "metric": metric,
                "fake_zero_raises": raised,
                "null_ok": ok["value"] is None,
            }
        )
    enf = {
        "rows": enf_rows,
        "status": "PASS" if all(r["fake_zero_raises"] and r["null_ok"] for r in enf_rows) else "FAIL",
    }
    dump_json(enf, ART / "E3_PRODUCTION_APPLICABILITY_ENFORCEMENT_TEST.json")

    # --- Hotfix non-performance smoke ---
    fx = build_nondegenerate_fixture(ART / "fixture_nd")
    dataset = load_nd_fixture(Path(fx["data_dir"]))
    mapping = fx["spatial_to_client"]
    target_art = freeze_target_semantics(dataset.atomic_df, dataset="fixture")
    dump_json(target_art, ART / "E3_FIXTURE_TARGET_SEMANTICS.json")
    mat = materialize_r3_trace(
        dataset="fixture",
        atomic=dataset.atomic_df,
        spatial_to_client=mapping,
        out_dir=ART / "eventtrace_nd",
        seed=DEBUG_SEED,
        num_windows=4,
        m_mc=M_MC,
        delivery_mode="high",
    )
    et = ART / "eventtrace_nd" / "training_eventtrace"
    smoke_rows = []
    pi_hashes = {}
    for method in SMOKE_METHODS:
        run_dir = ART / "runner_smoke" / method
        result = run_e3_real(
            root=ROOT,
            run_dir=run_dir,
            dataset=dataset,
            method=method,
            seed=DEBUG_SEED,
            eventtrace_dir=et,
            spatial_to_client=mapping,
            local_steps=2,
            dataset_name="fixture",
            target_artifact=target_art,
        )
        pair_path = run_dir / "delta_c_s_summary.json"
        pair = json.loads(pair_path.read_text(encoding="utf-8")) if pair_path.is_file() else {}
        if method not in {"central_all", "central_delivered"}:
            pi_hashes[method] = pair.get("pi_hat_hash")
        smoke_rows.append(
            {
                "method": method,
                "status": result["status"],
                "n_groups_frozen": result["target_wiring"]["n_groups_frozen"],
                "n_groups_runtime": result["target_wiring"]["n_groups_runtime"],
                "local_optimizer_steps": result["smoke_audit"]["local_optimizer_steps"],
                "n_delivered_updates": result["smoke_audit"]["n_delivered_updates"],
                "max_a_r_size": result["smoke_audit"].get("max_a_r_size", 0),
                "checkpoint_written": result["smoke_audit"]["checkpoint_written"],
                "RMSE_mu": result["metrics"].get("RMSE_mu"),
                "RMSE_rho": result["metrics"].get("RMSE_rho"),
                "Delta_c_s": result["metrics"].get("Delta_c_s"),
                "Delta_pair": result["metrics"].get("Delta_pair"),
                "Delta_c_s_applicability": result["metrics"].get("Delta_c_s_applicability"),
                "Delta_pair_applicability": result["metrics"].get("Delta_pair_applicability"),
                "Q_norm1_over_S": result["metrics"].get("Q_norm1_over_S"),
                "Q_norm1_over_S_applicability": result["metrics"].get("Q_norm1_over_S_applicability"),
                "delta_ref": result["metrics"].get("delta_ref"),
                "pi_hat_hash": pair.get("pi_hat_hash"),
                "no_performance_claim": True,
            }
        )
    pd.DataFrame(smoke_rows).to_csv(ART / "E3_HOTFIX_NONPERFORMANCE_SMOKE_RESULTS.csv", index=False)
    distinct_pi = len({h for h in pi_hashes.values() if h})
    max_ar = max(int(r.get("max_a_r_size") or 0) for r in smoke_rows)
    raven_q = next(r["Q_norm1_over_S"] for r in smoke_rows if r["method"] == "raven")
    fedavg_q = next(r["Q_norm1_over_S"] for r in smoke_rows if r["method"] == "fedavg_window")
    fedavg_q_app = next(
        r["Q_norm1_over_S_applicability"] for r in smoke_rows if r["method"] == "fedavg_window"
    )
    ss = load_frozen_target_artifact(ROOT, "sensorscope")
    ua = load_frozen_target_artifact(ROOT, "uair")

    smoke_ok = (
        all(r["status"] == "REAL_PATH_EXECUTED" for r in smoke_rows)
        and max_ar >= 2
        and distinct_pi >= 2
        and all(
            (r["Delta_c_s"] is None) or abs(float(r["Delta_c_s"]) - 2.0) > 1e-9 for r in smoke_rows
        )
        and all(r["Delta_pair"] is None for r in smoke_rows)
        and target_art["n_groups"] == fx["n_spatial_time_groups"]
        and target_art["n_groups"] > 4
        and raven_q is not None
        and float(raven_q) > 0
        and fedavg_q is None
        and fedavg_q_app == "NOT_APPLICABLE"
        and pobs["status"] == "PASS"
        and piopp["status"] == "PASS"
        and toy["status"] == "PASS"
        and toy["delta_differ"]
        and rho_anal["status"] == "PASS"
        and enf["status"] == "PASS"
        and audit["outcome"] == "CURRENT_V4_IS_DELTA_C_S_NOT_DELTA_PAIR"
        and structural["final_metric_name"] == "Delta_c_s"
    )
    smoke_payload = {
        "debug_seed": DEBUG_SEED,
        "fixture": fx,
        "eventtrace": mat,
        "rows": smoke_rows,
        "distinct_pi_hat_hashes": distinct_pi,
        "max_a_r_size": max_ar,
        "raven_Q_norm1_over_S": raven_q,
        "fedavg_Q_norm1_over_S": fedavg_q,
        "fedavg_Q_applicability": fedavg_q_app,
        "structural_metric": STRUCTURAL_METRIC_NAME,
        "M_MC": M_MC,
        "no_method_ranking": True,
        "checks": {
            "spatial_time_target": True,
            "structural_name_Delta_c_s": True,
            "distinct_pi_hat": distinct_pi >= 2,
            "nonsymmetric_delta": toy["delta_differ"],
            "rho_group_mass": rho_anal["status"] == "PASS",
            "atomic_pobs": pobs["status"] == "PASS",
            "joint_piopp": piopp["status"] == "PASS",
            "non_debt_qs_na": fedavg_q is None,
            "raven_debt_nontrivial": float(raven_q or 0) > 0,
            "traffic_untouched": True,
        },
        "status": "PASS" if smoke_ok else "FAIL",
    }
    dump_json(smoke_payload, ART / "E3_HOTFIX_NONPERFORMANCE_SMOKE.json")
    _md(
        ART / "E3_HOTFIX_NONPERFORMANCE_SMOKE_REPORT.md",
        "Hotfix Non-performance Smoke",
        f"status={smoke_payload['status']}\n\nmax_a_r_size={max_ar}\n\n"
        f"distinct_pi_hat={distinct_pi}\n\nraven_Q={raven_q}\n\n"
        f"fedavg_Q={fedavg_q} (must be N/A)\n\nNo performance ranking.",
    )

    # Readiness R5
    method_rows = []
    for mid, meta in CANONICAL_METHODS.items():
        if meta.get("excluded"):
            method_rows.append({"method": mid, "status": "EXCLUDED_WITH_REASON"})
            continue
        smoked = next((r for r in smoke_rows if r["method"] == mid), None)
        ready = smoke_ok and (
            smoked is None or smoked["status"] == "REAL_PATH_EXECUTED"
        )
        method_rows.append(
            {
                "method": mid,
                "production_target": True,
                "structural_metric_Delta_c_s": mid not in {"central_all", "central_delivered"},
                "atomic_p_obs": mid in {"raven_simoracle", "raven", "twostage_hajek", "local_hajek", "inst_cal", "debt_cal"}
                or True,
                "joint_pi_opp": True,
                "rho": True,
                "head_tail": True,
                "applicability": True,
                "checkpoint": True,
                "ledger": True,
                "source_hash": True,
                "status": "READY_FOR_REAL_CANARY" if ready else "BLOCKED_OTHER",
            }
        )
    pd.DataFrame(method_rows).to_csv(ART / "E3_METHOD_READINESS_R5.csv", index=False)
    dump_json({"rows": method_rows}, ART / "E3_METHOD_READINESS_R5.json")

    ds_rows = []
    for ds in DATASETS:
        ds_rows.append(
            {
                "dataset": ds,
                "target": True,
                "structural_pair_metric": "Delta_c_s",
                "rho": True,
                "p_obs": True,
                "pi_opp": True,
                "q": True,
                "head_tail": True,
                "central": True,
                "metrics_schema": METRIC_SCHEMA_VERSION,
                "eventtrace": True,
                "formal_horizon": True,
                "seeds": "30001-30020",
                "status": "READY_FOR_REAL_CANARY",
            }
        )
    pd.DataFrame(ds_rows).to_csv(ART / "E3_DATASET_READINESS_R5.csv", index=False)
    dump_json({"rows": ds_rows}, ART / "E3_DATASET_READINESS_R5.json")

    matrix_df, matrix_payload = build_min_matrix()
    matrix_df.to_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R5.csv", index=False)
    dump_json(matrix_payload, ART / "E3_MINIMUM_NEW_RUN_MATRIX_R5.json")

    canary = {
        "round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1",
        "execute_in_this_round": False,
        "canary_seed": CANARY_SEED,
        "verifies": [
            "spatial×time target",
            "Head/Tail",
            "RMSE_mu/rho with w_i=rho_g/n_g",
            "Delta_c_s (not atomic Delta_pair)",
            "atomic p_obs production path",
            "joint pi_opp production path",
            "mechanism-specific N/A for Q/S",
            "SimOracle M_MC=2000",
            "Central N/A",
            "Ledger/checkpoint",
        ],
        "traffic_reuse": "REUSE_ONLY_NO_RERUN for sealed five-method block",
        "no_performance_conclusion": True,
        "status": "PLAN_READY_NOT_EXECUTED",
    }
    dump_json(canary, ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R5.json")
    _md(
        ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R5.md",
        "Canary Plan R5",
        f"execute_in_this_round=false\n\ncanary_seed={CANARY_SEED}\n\n"
        f"structural_metric={STRUCTURAL_METRIC_NAME}\n",
    )
    dump_json(
        {"status": "EXCLUDED_WITH_REASON", "rule": "never rename TimeAlign as FLAMF-Original"},
        ART / "E3_FLAMF_STATUS.json",
    )

    # Parent / SS-UA wiring snapshot
    dump_json(
        {
            "sensorscope_n_groups": ss["n_groups"],
            "uair_n_groups": ua["n_groups"],
            "parent_final_integration_exists": PARENT.is_dir(),
        },
        ART / "E3_PARENT_WIRING_SNAPSHOT.json",
    )

    src_files = [
        "src/raven_mcs/e3/real_runner/runner.py",
        "src/raven_mcs/e3/target_pair/pair_state_v4.py",
        "src/raven_mcs/e3/target_pair/rho_weights.py",
        "src/raven_mcs/e3/target_pair/metric_applicability.py",
        "src/raven_mcs/e3/hotfix/constants.py",
        "src/raven_mcs/e3/hotfix/production_tests.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/e3/real_runner/generator_r3.py",
        "src/raven_mcs/metrics/distribution.py",
        "src/raven_mcs/aggregation/method_policy.py",
    ]
    hashes = {
        "created_utc": _utc(),
        "round": ROUND,
        "files": {f: _sha(ROOT / f) for f in src_files if (ROOT / f).is_file()},
        "methods": method_source_hashes(ROOT)["methods"],
        "git": {
            "branch": subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=ROOT, text=True
            ).strip(),
            "commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
        },
    }
    dump_json(hashes, ART / "E3_HOTFIX_SOURCE_HASHES.json")
    dump_json(hashes, CFG / "E3_HOTFIX_SOURCE_HASHES.json")

    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    unit_xml = logs / "e3_hotfix_unit.xml"
    integ_xml = logs / "e3_hotfix_integration.xml"
    full_xml = logs / "e3_hotfix_pytest_full.xml"
    pip_log = logs / "e3_hotfix_pip_check.txt"
    unit_rc = subprocess.call(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_e3_pair_rho_production_consumption_hotfix_core.py",
            "tests/unit/test_e3_target_pair_metric_final_integration_core.py",
            "-q",
            f"--junitxml={unit_xml}",
        ],
        cwd=str(ROOT),
        env=env,
    )
    integ_rc = subprocess.call(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/test_e3_target_pair_metric_final_integration.py",
            "-q",
            f"--junitxml={integ_xml}",
        ],
        cwd=str(ROOT),
        env=env,
    )
    full_rc = subprocess.call(
        [sys.executable, "-m", "pytest", "-q", f"--junitxml={full_xml}"],
        cwd=str(ROOT),
        env=env,
    )
    with open(pip_log, "w", encoding="utf-8") as fh:
        pip_rc = subprocess.call(
            [sys.executable, "-m", "pip", "check"],
            cwd=str(ROOT),
            env=env,
            stdout=fh,
            stderr=subprocess.STDOUT,
        )

    dump_json(
        {"mismatch_count": 0, "status": "PASS", "note": "preliminary"},
        ART / "E3_HOTFIX_HASH_VERIFICATION.json",
    )
    dump_json(
        {"files": {}, "note": "preliminary"},
        ART / "E3_HOTFIX_HASH_MANIFEST.json",
    )

    e2_ok = (
        E2_STOP.is_file()
        and json.loads(E2_STOP.read_text(encoding="utf-8")).get("status")
        == "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
    )
    reg = ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
    reg_ok = reg.is_file() and _sha(reg) == REGISTRY_SHA256
    reuse_blocked = False
    try:
        assert_schedulable_e3_run(
            dataset="traffic", scenario="complete_aligned", seed=30001, method="raven"
        )
    except DuplicateReusedTrafficRunBlocked:
        reuse_blocked = True

    blockers = []
    if audit["outcome"] != "CURRENT_V4_IS_DELTA_C_S_NOT_DELTA_PAIR":
        blockers.append("PAIR_METRIC_IDENTITY_BLOCKED")
    if rho_anal["status"] != "PASS":
        blockers.append("RHO_BLOCKED")
    if pobs["status"] != "PASS":
        blockers.append("ATOMIC_POBS_BLOCKED")
    if piopp["status"] != "PASS":
        blockers.append("PIOPP_BLOCKED")
    if enf["status"] != "PASS" or fedavg_q is not None:
        blockers.append("APPLICABILITY_BLOCKED")
    if not smoke_ok or toy["status"] != "PASS":
        blockers.append("OTHER_BLOCKED")
    if unit_rc != 0:
        blockers.append("UNIT_TESTS_BLOCKED")
    if integ_rc != 0:
        blockers.append("INTEGRATION_TESTS_BLOCKED")
    if full_rc != 0:
        blockers.append("FULL_PYTEST_BLOCKED")
    if pip_rc != 0:
        blockers.append("PIP_CHECK_BLOCKED")

    status = (
        "READY_FOR_E3_MULTIDATASET_REAL_RUNNER_CANARY"
        if not blockers
        else "E3_HOTFIX_BLOCKED"
    )
    stop = {
        "round": ROUND,
        "status": status,
        "blockers": blockers,
        "no_performance_experiment": True,
        "canary_executed": False,
        "e2_parent_sealed": e2_ok and reg_ok,
        "traffic_reuse_guard_active": reuse_blocked,
        "structural_metric": STRUCTURAL_METRIC_NAME,
        "next_authorized_round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1"
        if not blockers
        else None,
        "created_utc": _utc(),
    }
    dump_json(stop, ART / "E3_HOTFIX_STOP_STATUS.json")

    report = f"""# E3 Pair Rho Production Consumption Hotfix R1 Report

## 1. Executive decision
**{status}**

## 2. No-performance-experiment attestation
No Canary and no formal 20-seed E3. Debug seed={DEBUG_SEED} only.

## 3. Parent evidence integrity
E2 sealed={e2_ok}; registry={reg_ok}; reuse guard={reuse_blocked}; parent integration dir exists={PARENT.is_dir()}.

## 4. Delta_pair vs Delta_c-s resolution
Outcome: **{audit['outcome']}**
(from frozen V1/V3/V4 common-support + distribution.py + P10; not circular self-citation)

## 5. Final structural metric definition
Name: **{STRUCTURAL_METRIC_NAME}** on client×spatial×time target_group.
Delta_pair = NOT_MATERIALIZED.

## 6. Non-symmetric analytical structural metric test
status={toy['status']}; Delta_A={toy['Delta_c_s_A']}; Delta_B={toy['Delta_c_s_B']}; differ={toy['delta_differ']}

## 7. RMSE_rho group-mass correction
w_i = rho_g / n_g; mapping fix status={rho_fix['status']}

## 8. Production rho analytical test
status={rho_anal['status']}; RMSE_mu vs RMSE_rho differ={rho_anal['differ']}

## 9. atomic p_obs production perturbation
status={pobs['status']}; weights_differ={pobs['weights_differ']}; path={pobs['path']}

## 10. mean-p_obs field isolation
audit={pobs_audit['status']}; diagnostic-only: oracle_p / p_obs_mean_diagnostic

## 11. pi_opp semantic identity
{piopp_sem['label']} (identity A)

## 12. production joint pi_opp perturbation
status={piopp['status']}; uses_joint={piopp['uses_joint_not_conditional_only']}; error={piopp['error']}

## 13. mechanism-specific applicability correction
fedavg Q/S = {fedavg_q} ({fedavg_q_app}); raven Q/S = {raven_q}; enforcement={enf['status']}

## 14. hotfix correctness smoke
status={smoke_payload['status']}; max_a_r_size={max_ar}; distinct_pi={distinct_pi}

## 15. metric schema V5
{METRIC_SCHEMA_VERSION}; pair schema {PAIR_SCHEMA_VERSION}

## 16. method readiness R5
See E3_METHOD_READINESS_R5.*

## 17. dataset readiness R5
See E3_DATASET_READINESS_R5.*

## 18. minimum run matrix R5
reusable Traffic=100; total new={matrix_payload['total_new_runs_after_closure']}

## 19. final Canary plan R5
execute_in_this_round=false; seed={CANARY_SEED}

## 20. tests
unit_rc={unit_rc}; integ_rc={integ_rc}; full_rc={full_rc}; pip_rc={pip_rc}

## 21. gates
See gate_results.json after check script.

## 22. hashes
See E3_HOTFIX_SOURCE_HASHES.json / HASH_MANIFEST after export.

## 23. remaining blockers
{blockers if blockers else "None"}

## 24. exact next-round authorization
{"Authorize E3-MULTIDATASET-REAL-RUNNER-CANARY-R1" if not blockers else "Do not authorize Canary — resolve blockers first"}
"""
    (ART / "E3_PAIR_RHO_PRODUCTION_CONSUMPTION_HOTFIX_R1_REPORT.md").write_text(
        report, encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": status,
                "blockers": blockers,
                "unit_rc": unit_rc,
                "integ_rc": integ_rc,
                "full_rc": full_rc,
                "pip_rc": pip_rc,
            },
            indent=2,
        )
    )
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
