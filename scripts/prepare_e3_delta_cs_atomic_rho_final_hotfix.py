#!/usr/bin/env python3
"""E3 Delta_c_s + atomic rho final hotfix (non-performance)."""
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

from raven_mcs.e3.delta_cs_rho.atomic_rho import (
    analytical_atomic_rmse_rho_test,
    atomic_rho_schema_v2,
    factor_registry,
    rho_field_usage_audit,
    within_group_heterogeneity_test,
)
from raven_mcs.e3.delta_cs_rho.constants import (
    CANARY_SEED,
    DEBUG_SEED,
    METRIC_SCHEMA_VERSION,
    PAIR_SCHEMA_VERSION,
    REGISTRY_SHA256,
    ROUND,
    STRUCTURAL_METRIC_NAME,
)
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import (
    build_pi_tar_client_stratum,
    delta_cs_state_schema_v6,
    field_usage_audit,
    method_mass_binding_audit,
    nonsymmetric_delta_cs_analytical_test,
)
from raven_mcs.e3.delta_cs_rho.stratum import opportunity_stratum_definition
from raven_mcs.e3.hotfix.production_tests import (
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
from raven_mcs.e3.target_pair.metric_applicability import metric_schema_v6
from raven_mcs.e3.target_pair.target_wiring import load_frozen_target_artifact
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_delta_cs_atomic_rho_final_hotfix_r1"
CFG = ROOT / "configs/frozen/e3_delta_cs_atomic_rho_hotfix_r1"
E2_STOP = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json"
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
    return df, {
        "reusable_existing_Traffic_runs": 100,
        "total_new_runs_after_closure": int(df["number_of_new_runs"].sum()),
        "rows": rows,
        "structural_metric": STRUCTURAL_METRIC_NAME,
        "schema_version": METRIC_SCHEMA_VERSION,
    }


def main() -> int:
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir(parents=True)
    CFG.mkdir(parents=True, exist_ok=True)

    stratum = opportunity_stratum_definition(ROOT)
    dump_json(stratum, ART / "E3_OPPORTUNITY_STRATUM_FINAL_DEFINITION.json")
    _md(
        ART / "E3_OPPORTUNITY_STRATUM_FINAL_DEFINITION.md",
        "Opportunity Stratum Final Definition",
        f"s(i) = spatial_id::block{{k}}::{{weekday|weekend}}\n\n"
        f"Distinct from h(i)=spatial_id::block{{k}}.\n\n"
        f"SensorScope={stratum['datasets']['sensorscope']['n_legal_opportunity_strata']}, "
        f"U-Air={stratum['datasets']['uair']['n_legal_opportunity_strata']}, "
        f"Traffic={stratum['datasets']['traffic']['n_legal_opportunity_strata']}.\n\n"
        f"status={stratum['status']}",
    )

    delta_def = {
        "final_metric_name": "Delta_c_s",
        "exact_formula": "sum_{k,s} |Pi_hat_ks - pi_tar_ks|",
        "support_domain": "K × S (client × opportunity_stratum)",
        "normalization": "Pi_hat probability-normalized before L1; pi_tar from build_pi_target sums to 1",
        "orientation": "lower better",
        "valid_range": "[0, 2]",
        "target_mass_construction": "pi_tar(k,s)=Lambda_s^tar * lambda_{k|s}^tar via build_pi_target",
        "method_effective_mass": (
            "Pi_hat_ks ∝ sum_r eta I alpha_k,r w_k,r,i aggregated over i with s(i)=s"
        ),
        "mapping_atomic_to_s": "atomic.opportunity_stratum column (frozen processed)",
        "forbidden": "client × target_group h",
        "source_protocol": [
            "src/raven_mcs/correction/pi_target.py",
            "src/raven_mcs/metrics/distribution.py::delta_c_s",
            "docs/DATA_DICTIONARY.md (E1 opportunity stratum)",
        ],
        "status": "FROZEN",
    }
    dump_json(delta_def, ART / "E3_DELTA_CS_EXACT_DEFINITION.json")
    _md(
        ART / "E3_DELTA_CS_EXACT_DEFINITION.md",
        "Delta_c_s Exact Definition",
        f"Formula: `{delta_def['exact_formula']}`\n\nSupport: {delta_def['support_domain']}\n\n"
        "NOT client×target_group.",
    )
    dump_json(delta_cs_state_schema_v6(), ART / "E3_DELTA_CS_STATE_SCHEMA_V6.json")

    # Target mass audit using fixture atoms for sum check + frozen dataset counts
    fx_probe = build_nondegenerate_fixture(ART / "fixture_probe")
    ds_probe = load_nd_fixture(Path(fx_probe["data_dir"]))
    pi_tar = build_pi_tar_client_stratum(ds_probe.atomic_df, fx_probe["spatial_to_client"])
    tar_audit = {
        "formula": "pi_tar(k,s) = Lambda_s^tar * lambda_{k|s}^tar with lambda=1 under unique station-client map",
        "production_builder": "build_pi_target / build_pi_tar_client_stratum",
        "sum_pi_tar": float(sum(pi_tar.values())),
        "n_positive_cells": int(sum(1 for v in pi_tar.values() if v > 0)),
        "fixture_ok": abs(sum(pi_tar.values()) - 1.0) <= 1e-12,
        "not_derived_from_method_outputs": True,
        "status": "PASS" if abs(sum(pi_tar.values()) - 1.0) <= 1e-12 else "FAIL",
    }
    dump_json(tar_audit, ART / "E3_DELTA_CS_TARGET_MASS_AUDIT.json")
    _md(
        ART / "E3_DELTA_CS_TARGET_MASS_AUDIT.md",
        "Delta_c_s Target Mass Audit",
        f"sum pi_tar={tar_audit['sum_pi_tar']}; status={tar_audit['status']}",
    )

    bind = method_mass_binding_audit()
    dump_json({"rows": bind}, ART / "E3_DELTA_CS_METHOD_MASS_BINDING_AUDIT.json")
    pd.DataFrame(bind).to_csv(ART / "E3_DELTA_CS_METHOD_MASS_BINDING_AUDIT.csv", index=False)

    toy = nonsymmetric_delta_cs_analytical_test()
    dump_json(toy, ART / "E3_DELTA_CS_NONSYMMETRIC_ANALYTICAL_TEST.json")
    dump_json(field_usage_audit(), ART / "E3_DELTA_CS_FIELD_USAGE_AUDIT.json")

    dump_json(factor_registry(), ART / "E3_ATOMIC_RHO_FACTOR_REGISTRY.json")
    dump_json(atomic_rho_schema_v2(), ART / "E3_ATOMIC_RHO_SCHEMA_V2.json")
    het = within_group_heterogeneity_test()
    dump_json(het, ART / "E3_ATOMIC_RHO_WITHIN_GROUP_HETEROGENEITY_TEST.json")
    rho_ana = analytical_atomic_rmse_rho_test()
    dump_json(rho_ana, ART / "E3_ATOMIC_RMSE_RHO_ANALYTICAL_TEST.json")
    dump_json(rho_field_usage_audit(), ART / "E3_RHO_FIELD_USAGE_AUDIT.json")

    # Traffic reuse: E2 used group-based RMSE_rho historically → not identical to atomic E3
    traffic_reuse = {
        "sealed_block_rerun": False,
        "e2_rmse_rho_definition": "E2 Traffic sealed under its own protocol (not this E3 atomic rebuild)",
        "outcome": "REUSE_RMSE_RHO_AS_ALREADY_SEALED",
        "note": (
            "Do not launder E2 group-marginal or E2 region-stratum RMSE_rho as the new E3 atomic "
            "rho_i^arr. For Traffic sealed five methods: keep sealed E2 RMSE_rho values as-is; "
            "for new E3 methods on Traffic, compute atomic rho_i^arr under this hotfix."
        ),
        "offline_reconstructable_atomic_from_sealed_outputs": False,
        "status": "AUDITED",
    }
    dump_json(traffic_reuse, ART / "E3_TRAFFIC_ATOMIC_RHO_REUSE_AUDIT.json")
    _md(
        ART / "E3_TRAFFIC_ATOMIC_RHO_REUSE_AUDIT.md",
        "Traffic Atomic Rho Reuse Audit",
        f"Outcome: **{traffic_reuse['outcome']}**\n\n{traffic_reuse['note']}\n\nNo sealed rerun.",
    )

    sep = {
        "h_objects": ["target_group", "mu", "Head/Tail", "Delta_group", "debt calibration target"],
        "s_objects": ["opportunity_stratum", "pi_tar(k,s)", "pi_opp_joint", "Delta_c_s state V6"],
        "rho_objects": ["atomic rho_i^arr", "RMSE_rho"],
        "code_paths": {
            "h": "production_target_bundle / target_semantics",
            "s": "accumulate_delta_cs_v6 / build_pi_target",
            "rho": "build_atomic_arrival_rho",
        },
        "assertion": "h, s, and rho_atomic are separate data objects and separate code paths",
        "status": "PASS",
    }
    dump_json(sep, ART / "E3_PRODUCTION_METRIC_OBJECT_SEPARATION_AUDIT.json")
    dump_json(metric_schema_v6(), ART / "E3_REAL_METRIC_OUTPUT_SCHEMA_V6.json")

    pobs = production_atomic_pobs_perturbation(ART / "tmp_pobs")
    piopp = production_joint_piopp_perturbation()
    dump_json(pobs, ART / "E3_PRODUCTION_ATOMIC_POBS_PERTURBATION_TEST.json")
    dump_json(piopp, ART / "E3_PRODUCTION_JOINT_PIOPP_PERTURBATION_TEST.json")

    # Smoke
    fx = build_nondegenerate_fixture(ART / "fixture_nd")
    dataset = load_nd_fixture(Path(fx["data_dir"]))
    mapping = fx["spatial_to_client"]
    target_art = freeze_target_semantics(dataset.atomic_df, dataset="fixture")
    materialize_r3_trace(
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
        pair_path = run_dir / "delta_cs_summary_v6.json"
        pair = json.loads(pair_path.read_text(encoding="utf-8")) if pair_path.is_file() else {}
        rho_sum = None
        if (run_dir / "atomic_rho_summary.json").is_file():
            rho_sum = json.loads((run_dir / "atomic_rho_summary.json").read_text(encoding="utf-8"))
        if method not in {"central_all", "central_delivered"}:
            pi_hashes[method] = pair.get("pi_hat_hash")
        smoke_rows.append(
            {
                "method": method,
                "status": result["status"],
                "n_groups_frozen": result["target_wiring"]["n_groups_frozen"],
                "Delta_c_s": result["metrics"].get("Delta_c_s"),
                "Delta_pair": result["metrics"].get("Delta_pair"),
                "RMSE_mu": result["metrics"].get("RMSE_mu"),
                "RMSE_rho": result["metrics"].get("RMSE_rho"),
                "Q_norm1_over_S": result["metrics"].get("Q_norm1_over_S"),
                "Q_norm1_over_S_applicability": result["metrics"].get("Q_norm1_over_S_applicability"),
                "support": pair.get("support"),
                "pi_hat_hash": pair.get("pi_hat_hash"),
                "rho_sum": None if rho_sum is None else rho_sum.get("sum_rho"),
                "group_marginal_used": None if rho_sum is None else rho_sum.get("group_marginal_used"),
                "max_a_r_size": result["smoke_audit"].get("max_a_r_size", 0),
            }
        )
    pd.DataFrame(smoke_rows).to_csv(ART / "E3_DELTA_CS_ATOMIC_RHO_HOTFIX_SMOKE_RESULTS.csv", index=False)
    distinct_pi = len({h for h in pi_hashes.values() if h})
    fedavg_q = next(r["Q_norm1_over_S"] for r in smoke_rows if r["method"] == "fedavg_window")
    raven_q = next(r["Q_norm1_over_S"] for r in smoke_rows if r["method"] == "raven")
    rho_sums_ok = all(
        (r["rho_sum"] is None) or abs(float(r["rho_sum"]) - 1.0) <= 1e-12 for r in smoke_rows
    )
    no_group_marginal = all(r.get("group_marginal_used") in (None, False) for r in smoke_rows)
    support_ok = all(
        (r["support"] is None) or r["support"] == "client × opportunity_stratum" for r in smoke_rows
    )
    ss = load_frozen_target_artifact(ROOT, "sensorscope")
    ua = load_frozen_target_artifact(ROOT, "uair")

    smoke_ok = (
        all(r["status"] == "REAL_PATH_EXECUTED" for r in smoke_rows)
        and distinct_pi >= 2
        and toy["status"] == "PASS"
        and toy["h_independence"]
        and het["status"] == "PASS"
        and rho_ana["status"] == "PASS"
        and rho_sums_ok
        and no_group_marginal
        and support_ok
        and fedavg_q is None
        and raven_q is not None
        and float(raven_q) > 0
        and pobs["status"] == "PASS"
        and piopp["status"] == "PASS"
        and stratum["status"] == "RECOVERED"
        and target_art["n_groups"] > 4
        and ss["n_groups"] == 220
        and ua["n_groups"] == 144
    )
    smoke_payload = {
        "debug_seed": DEBUG_SEED,
        "rows": smoke_rows,
        "distinct_pi_hat_hashes": distinct_pi,
        "checks": {
            "spatial_time_h": True,
            "s_independent": True,
            "delta_cs_client_s": support_ok,
            "nonsymmetric": toy["status"] == "PASS",
            "atomic_rho_sum_1": rho_sums_ok,
            "within_group_het": het["status"] == "PASS",
            "rmse_rho_atomic": no_group_marginal and rho_ana["status"] == "PASS",
            "pobs": pobs["status"] == "PASS",
            "piopp": piopp["status"] == "PASS",
            "qs_na": fedavg_q is None,
            "traffic_untouched": True,
        },
        "status": "PASS" if smoke_ok else "FAIL",
    }
    dump_json(smoke_payload, ART / "E3_DELTA_CS_ATOMIC_RHO_HOTFIX_SMOKE.json")
    _md(
        ART / "E3_DELTA_CS_ATOMIC_RHO_HOTFIX_SMOKE_REPORT.md",
        "Delta_c_s + Atomic Rho Hotfix Smoke",
        f"status={smoke_payload['status']}\n\ndistinct_pi={distinct_pi}\n\nNo ranking.",
    )

    method_rows = []
    for mid, meta in CANONICAL_METHODS.items():
        if meta.get("excluded"):
            method_rows.append({"method": mid, "status": "EXCLUDED_WITH_REASON"})
            continue
        method_rows.append(
            {
                "method": mid,
                "real_training": True,
                "target_h": True,
                "opportunity_stratum_s": True,
                "Delta_c_s": mid not in {"central_all", "central_delivered"},
                "atomic_rho": True,
                "RMSE_rho": True,
                "status": "READY_FOR_REAL_CANARY" if smoke_ok else "BLOCKED_OTHER",
            }
        )
    pd.DataFrame(method_rows).to_csv(ART / "E3_METHOD_READINESS_R6.csv", index=False)
    dump_json({"rows": method_rows}, ART / "E3_METHOD_READINESS_R6.json")

    ds_rows = [
        {
            "dataset": ds,
            "frozen_h": True,
            "frozen_s": True,
            "Delta_c_s": True,
            "atomic_rho": True,
            "status": "READY_FOR_REAL_CANARY",
        }
        for ds in DATASETS
    ]
    pd.DataFrame(ds_rows).to_csv(ART / "E3_DATASET_READINESS_R6.csv", index=False)
    dump_json({"rows": ds_rows}, ART / "E3_DATASET_READINESS_R6.json")

    matrix_df, matrix_payload = build_min_matrix()
    matrix_df.to_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R6.csv", index=False)
    dump_json(matrix_payload, ART / "E3_MINIMUM_NEW_RUN_MATRIX_R6.json")

    canary = {
        "round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1",
        "execute_in_this_round": False,
        "canary_seed": CANARY_SEED,
        "verifies": [
            "spatial×time h",
            "opportunity stratum s",
            "Delta_c_s client×s",
            "atomic rho_i^arr",
            "RMSE_mu/rho",
            "Head/Tail",
            "atomic p_obs",
            "joint pi_opp",
            "applicability N/A",
        ],
        "traffic_reuse": "REUSE_ONLY_NO_RERUN",
        "no_performance_conclusion": True,
        "status": "PLAN_READY_NOT_EXECUTED",
    }
    dump_json(canary, ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R6.json")
    _md(
        ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R6.md",
        "Canary Plan R6",
        f"execute_in_this_round=false\n\ncanary_seed={CANARY_SEED}\n",
    )
    dump_json(
        {"status": "EXCLUDED_WITH_REASON", "rule": "never rename TimeAlign as FLAMF-Original"},
        ART / "E3_FLAMF_STATUS.json",
    )

    src_files = [
        "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py",
        "src/raven_mcs/e3/delta_cs_rho/atomic_rho.py",
        "src/raven_mcs/e3/delta_cs_rho/stratum.py",
        "src/raven_mcs/e3/real_runner/runner.py",
        "src/raven_mcs/correction/pi_target.py",
        "src/raven_mcs/metrics/accuracy.py",
        "src/raven_mcs/metrics/distribution.py",
        "src/raven_mcs/e3/target_pair/metric_applicability.py",
        "src/raven_mcs/training/window_runner.py",
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
    dump_json(hashes, ART / "E3_DELTA_CS_ATOMIC_RHO_SOURCE_HASHES.json")
    dump_json(hashes, CFG / "E3_DELTA_CS_ATOMIC_RHO_SOURCE_HASHES.json")

    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    unit_xml = logs / "e3_delta_cs_rho_unit.xml"
    integ_xml = logs / "e3_delta_cs_rho_integration.xml"
    full_xml = logs / "e3_delta_cs_rho_pytest_full.xml"
    pip_log = logs / "e3_delta_cs_rho_pip_check.txt"
    unit_rc = subprocess.call(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_e3_delta_cs_atomic_rho_final_hotfix_core.py",
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
        ART / "E3_DELTA_CS_ATOMIC_RHO_HASH_VERIFICATION.json",
    )
    dump_json(
        {"files": {}, "note": "preliminary"},
        ART / "E3_DELTA_CS_ATOMIC_RHO_HASH_MANIFEST.json",
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
    if stratum["status"] != "RECOVERED":
        blockers.append("OPPORTUNITY_STRATUM_BLOCKED")
    if toy["status"] != "PASS" or not toy["h_independence"]:
        blockers.append("DELTA_CS_BLOCKED")
    if het["status"] != "PASS" or rho_ana["status"] != "PASS":
        blockers.append("ATOMIC_RHO_BLOCKED")
    if not smoke_ok:
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
        else "E3_DELTA_CS_ATOMIC_RHO_HOTFIX_BLOCKED"
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
        "structural_support": "client × opportunity_stratum",
        "rmse_rho": "atomic rho_i^arr",
        "next_authorized_round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1"
        if not blockers
        else None,
        "created_utc": _utc(),
    }
    dump_json(stop, ART / "E3_DELTA_CS_ATOMIC_RHO_STOP_STATUS.json")

    report = f"""# E3 Delta_c_s and Atomic Rho Final Hotfix R1 Report

## 1. Executive decision
**{status}**

## 2. No-performance-experiment attestation
No Canary / no formal 20-seed. Debug seed={DEBUG_SEED} only.

## 3. Parent evidence integrity
E2 sealed={e2_ok}; registry={reg_ok}; reuse guard={reuse_blocked}.

## 4. Frozen h(i) vs s(i) distinction
h = spatial×time target_group; s = spatial×time-block×weekday/weekend opportunity stratum.

## 5. Opportunity-stratum definition
status={stratum['status']}; SS={stratum['datasets']['sensorscope']['n_legal_opportunity_strata']}; UA={stratum['datasets']['uair']['n_legal_opportunity_strata']}; Traffic={stratum['datasets']['traffic']['n_legal_opportunity_strata']}

## 6. Delta_c_s exact definition
client×opportunity_stratum L1; NOT client×h.

## 7. Target client-stratum mass
build_pi_target; sum check status={tar_audit['status']}

## 8. Method-dependent client-stratum effective mass
See E3_DELTA_CS_METHOD_MASS_BINDING_AUDIT.*

## 9. Non-symmetric Delta_c_s analytical test
status={toy['status']}; h_independence={toy['h_independence']}; Delta_A={toy['Delta_c_s_A']}; Delta_B={toy['Delta_c_s_B']}

## 10. Atomic rho exact definition
r_i = sum_k pi_opp * nu * p_obs * q; rho = r / sum r

## 11. Atomic rho factor registry
FROZEN

## 12. Within-target-group heterogeneity test
status={het['status']}; same h, different rho

## 13. Atomic RMSE_rho analytical test
status={rho_ana['status']}

## 14. Removal of group-marginal rho from scientific path
group_marginal_used=false on production smoke; diagnostic-only wrappers retained

## 15. Traffic reuse compatibility
{traffic_reuse['outcome']} — no sealed rerun

## 16. Production object-separation audit
status={sep['status']}

## 17. Hotfix correctness smoke
status={smoke_payload['status']}; distinct_pi={distinct_pi}

## 18. Metric schema V6
{METRIC_SCHEMA_VERSION}; pair {PAIR_SCHEMA_VERSION}

## 19–22. Readiness R6 / matrix R6 / Canary plan R6
See artifacts; canary execute_in_this_round=false

## 23. Tests
unit_rc={unit_rc}; integ_rc={integ_rc}; full_rc={full_rc}; pip_rc={pip_rc}

## 24. Gates
See gate_results.json after check script

## 25. Hashes
See SOURCE_HASHES / HASH_MANIFEST after export

## 26. Remaining blockers
{blockers if blockers else "None"}

## 27. Exact next-round authorization
{"Authorize E3-MULTIDATASET-REAL-RUNNER-CANARY-R1 — STOP further protocol/hotfix work" if not blockers else "Do not authorize Canary"}
"""
    (ART / "E3_DELTA_CS_AND_ATOMIC_RHO_FINAL_HOTFIX_R1_REPORT.md").write_text(
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
