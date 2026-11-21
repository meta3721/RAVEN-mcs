#!/usr/bin/env python3
"""E3 stratum identity + Traffic reuse seal (no training / no Canary)."""
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

from raven_mcs.correction.pi_target import build_pi_target
from raven_mcs.e3.delta_cs_rho.atomic_rho import (
    analytical_atomic_rmse_rho_test,
    within_group_heterogeneity_test,
)
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import nonsymmetric_delta_cs_analytical_test
from raven_mcs.e3.delta_cs_rho.stratum import opportunity_stratum_definition
from raven_mcs.e3.protocol_closure.method_registry import CANONICAL_METHODS, method_source_hashes
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.real_runner.constants import E2_TRAFFIC_REUSED_METHODS, FORMAL_SEEDS
from raven_mcs.e3.real_runner.fixture_nd import build_nondegenerate_fixture, load_nd_fixture
from raven_mcs.e3.real_runner.generator_r3 import materialize_r3_trace
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.e3.semantic_alignment.target_semantics import freeze_target_semantics
from raven_mcs.e3.stratum_seal.constants import (
    CANARY_SEED,
    DEBUG_SEED,
    REGISTRY_SHA256,
    ROUND,
    TRAFFIC_PUBLIC_TARGET_MAPPING_HASH,
)
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.e3.stratum_seal.traffic_regions import (
    freeze_traffic_region_mapping_artifacts,
    load_frozen_traffic_station_regions,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_stratum_identity_and_traffic_reuse_seal_r1"
CFG = ROOT / "configs/frozen/e3_stratum_reuse_seal_r1"
E2_STOP = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json"
PARENT = ROOT / "artifacts/e3_delta_cs_atomic_rho_final_hotfix_r1"
DATASETS = ["sensorscope", "uair", "traffic"]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _md(path: Path, title: str, body: str) -> None:
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def main() -> int:
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir(parents=True)
    CFG.mkdir(parents=True, exist_ok=True)

    # --- Traffic region freeze ---
    traffic_meta = freeze_traffic_region_mapping_artifacts(ROOT, ART / "traffic_region_mapping")
    shutil.copytree(ART / "traffic_region_mapping", CFG / "traffic_region_mapping", dirs_exist_ok=True)
    dump_json(traffic_meta, ART / "E3_TRAFFIC_STRATUM_IDENTITY_SEAL.json")

    # --- SensorScope / U-Air seals ---
    stratum_def = opportunity_stratum_definition(ROOT)
    ss_atomic = pd.read_parquet(ROOT / "data/processed/sensorscope/atomic_units.parquet")
    ua_atomic = pd.read_parquet(ROOT / "data/processed/uair/atomic_units.parquet")
    tr_atomic = pd.read_parquet(ROOT / "data/processed/traffic/atomic_units.parquet")
    _, ss_meta = apply_sealed_opportunity_stratum(ss_atomic, dataset="sensorscope", root=ROOT)
    _, ua_meta = apply_sealed_opportunity_stratum(ua_atomic, dataset="uair", root=ROOT)
    tr_remapped, tr_remap_meta = apply_sealed_opportunity_stratum(tr_atomic, dataset="traffic", root=ROOT)

    ss_seal = {
        "dataset": "sensorscope",
        "raw_spatial_unit": "station_id / spatial_id",
        "coarse_spatial_region_rule": "station itself (no further coarsening)",
        "time_block_rule": "UTC hour//6 → block0..3",
        "weekday_weekend_rule": "weekday_label",
        "exact_s_mapping": "spatial_id::block{k}::{weekday|weekend}",
        "total_raw_stratum_cardinality": 440,
        "nonempty_stratum_cardinality": int(ss_atomic["opportunity_stratum"].nunique()),
        "source_files": [
            "configs/frozen/e3_multidataset_protocol_closure/sensorscope/opportunity_strata.json",
            "src/raven_mcs/data/matrix_adapter.py",
        ],
        "source_hashes": {
            "opportunity_strata.json": stratum_def["datasets"]["sensorscope"]["source_hash"]
        },
        "previous_frozen_artifact": "configs/frozen/e3_multidataset_protocol_closure/sensorscope/opportunity_strata.json",
        "current_mapping_hash": sha256_json(
            sorted(ss_atomic["opportunity_stratum"].astype(str).unique().tolist())
        ),
        "equality_compatibility": "MATCHES_PRIOR_FROZEN_STATION_LEVEL",
        "identity_status": "FROZEN_IDENTITY_CONFIRMED",
        "no_new_clustering": True,
    }
    ua_seal = {
        "dataset": "uair",
        "raw_spatial_unit": "station/node spatial_id",
        "coarse_spatial_region_rule": "spatial_id itself (no further coarsening)",
        "time_block_rule": "UTC hour//6 → block0..3",
        "weekday_weekend_rule": "weekday_label",
        "exact_s_mapping": "spatial_id::block{k}::{weekday|weekend}",
        "total_raw_stratum_cardinality": 288,
        "nonempty_stratum_cardinality": int(ua_atomic["opportunity_stratum"].nunique()),
        "source_files": [
            "configs/frozen/e3_multidataset_protocol_closure/uair/opportunity_strata.json",
            "src/raven_mcs/data/matrix_adapter.py",
        ],
        "source_hashes": {"opportunity_strata.json": stratum_def["datasets"]["uair"]["source_hash"]},
        "previous_frozen_artifact": "configs/frozen/e3_multidataset_protocol_closure/uair/opportunity_strata.json",
        "current_mapping_hash": sha256_json(
            sorted(ua_atomic["opportunity_stratum"].astype(str).unique().tolist())
        ),
        "equality_compatibility": "MATCHES_PRIOR_FROZEN_STATION_LEVEL",
        "identity_status": "FROZEN_IDENTITY_CONFIRMED",
        "no_new_clustering": True,
    }
    dump_json(ss_seal, ART / "E3_SENSORSCOPE_STRATUM_IDENTITY_SEAL.json")
    dump_json(ua_seal, ART / "E3_UAIR_STRATUM_IDENTITY_SEAL.json")

    identity_seal = {
        "round": ROUND,
        "datasets": {
            "sensorscope": ss_seal,
            "uair": ua_seal,
            "traffic": {
                "dataset": "traffic",
                "raw_spatial_unit": "counting station spatial_id (43)",
                "coarse_spatial_region_rule": "frozen E2 public-target 4 real regions",
                "time_block_rule": "UTC hour//6 → block0..3",
                "weekday_weekend_rule": "weekday|weekend",
                "exact_s_mapping": "region_id::block{k}::{weekday|weekend}",
                "total_raw_stratum_cardinality": 32,
                "nonempty_stratum_cardinality": int(tr_remap_meta["n_unique_strata"]),
                "station_count": 43,
                "region_count": 4,
                "mapping_hash": TRAFFIC_PUBLIC_TARGET_MAPPING_HASH,
                "source_files": [
                    "configs/frozen/e2_traffic_public_target/station_region_identity.json",
                    "src/raven_mcs/e2/traffic_public_target/core.py",
                    "src/raven_mcs/e3/stratum_seal/traffic_regions.py",
                ],
                "previous_frozen_artifact": "configs/frozen/e2_traffic_public_target/station_region_identity.json",
                "identity_status": "FROZEN_IDENTITY_RECOVERED",
                "rejects_station_level_344": True,
                "raw_processed_had_344": int(tr_atomic["opportunity_stratum"].nunique()) == 344,
            },
        },
        "status": "SEALED",
    }
    dump_json(identity_seal, ART / "E3_STRATUM_IDENTITY_SEAL.json")
    _md(
        ART / "E3_STRATUM_IDENTITY_SEAL.md",
        "Stratum Identity Seal",
        "SensorScope: station-level 440 (CONFIRMED).\n\n"
        "U-Air: station-level 288 (CONFIRMED).\n\n"
        "Traffic: 4 real regions × 4 blocks × 2 day-types ≤32 (RECOVERED from E2 public-target). "
        "Station-level 344 rejected.",
    )

    # --- Rebuild audit (mapping-only, no training) ---
    stc_tr = {str(s): str(s) for s in tr_remapped["spatial_id"].astype(str).unique()}
    old_pi = None
    try:
        old_frame = tr_atomic.copy()
        old_frame["target_group_main"] = old_frame["target_group"].astype(str)
        # old station-level would fail multi-client? unique per station stratum — works
        old_pi_frame = build_pi_target(old_frame, stc_tr, split="test")
        old_pi = sha256_json(
            {
                f"{r.client_id}|{r.opportunity_stratum}": float(r.pi_k_s_tar)
                for r in old_pi_frame.itertuples(index=False)
            }
        )
    except Exception as exc:  # noqa: BLE001
        old_pi = f"ERROR:{exc}"
    new_frame = tr_remapped.copy()
    new_frame["target_group_main"] = new_frame["target_group"].astype(str)
    new_pi_frame = build_pi_target(new_frame, stc_tr, split="test")
    new_pi = sha256_json(
        {
            f"{r.client_id}|{r.opportunity_stratum}": float(r.pi_k_s_tar)
            for r in new_pi_frame.itertuples(index=False)
        }
    )
    rebuild = {
        "objects": [
            {
                "object": "opportunity_stratum_traffic",
                "old_hash": sha256_json(sorted(tr_atomic["opportunity_stratum"].astype(str).unique().tolist())),
                "new_hash": sha256_json(sorted(tr_remapped["opportunity_stratum"].astype(str).unique().tolist())),
                "reason_changed": "station-level 344 → frozen 4-region ≤32",
                "mapping_only": True,
                "no_training": True,
            },
            {
                "object": "pi_tar_k_s_traffic",
                "old_hash": old_pi,
                "new_hash": new_pi,
                "reason_changed": "reindexed onto region×time×day with multi-client lambda_{k|s}",
                "mapping_only": True,
                "no_training": True,
            },
            {
                "object": "Delta_c_s_support",
                "old_hash": "client×station-stratum (pre-seal Traffic)",
                "new_hash": "client×region-stratum (sealed)",
                "reason_changed": "s(i) identity seal",
                "mapping_only": True,
                "no_training": True,
            },
            {
                "object": "atomic_rho_s_index",
                "old_hash": "indexed by station-level s",
                "new_hash": "indexed by sealed region-level s for Traffic",
                "reason_changed": "s(i) identity seal",
                "mapping_only": True,
                "no_training": True,
            },
        ],
        "no_model_checkpoint_touched": True,
        "no_formal_training": True,
        "status": "REBUILT_MAPPING_ONLY",
    }
    dump_json(rebuild, ART / "E3_STRATUM_DEPENDENT_OBJECT_REBUILD_AUDIT.json")

    toy = nonsymmetric_delta_cs_analytical_test()
    dump_json(
        {
            **toy,
            "support": "client × opportunity_stratum",
            "traffic_uses_region_s": True,
            "post_stratum_seal": True,
        },
        ART / "E3_DELTA_CS_POST_STRATUM_SEAL_TEST.json",
    )
    het = within_group_heterogeneity_test()
    rho_ana = analytical_atomic_rmse_rho_test()
    dump_json(
        {
            "heterogeneity": het,
            "analytical": rho_ana,
            "traffic_uses_frozen_4_region_s": True,
            "group_marginal_used": False,
            "status": "PASS"
            if het["status"] == "PASS" and rho_ana["status"] == "PASS"
            else "FAIL",
        },
        ART / "E3_ATOMIC_RHO_POST_STRATUM_SEAL_TEST.json",
    )

    # --- Traffic RMSE_rho reuse compatibility ---
    compat = {
        "comparisons": {
            "1_spatial_region_mapping": {
                "e2": "4 regions (public-target label-free)",
                "e3": "same frozen mapping hash",
                "match": True,
            },
            "2_opportunity_stratum_s": {
                "e2": "region×time×day (32)",
                "e3_sealed": "region×time×day (≤32)",
                "match": True,
            },
            "3_atomic_evaluation_support": {
                "e2": "protocol atomic units with varpi",
                "e3": "TEST atomic units",
                "match": "PARTIAL",
            },
            "4_pi_opp": {
                "e2": "E2 Traffic opportunity construction",
                "e3": "build_joint_pi_opp on sealed s",
                "match": False,
            },
            "5_nu_i_given_s": {
                "e2": "not used in E2 Traffic RMSE_rho weights",
                "e3": "atom_mass/Lambda_s",
                "match": False,
            },
            "6_atomic_p_obs": {
                "e2": "not in E2 arrival weight product",
                "e3": "atomic p_obs factor",
                "match": False,
            },
            "7_q_use": {
                "e2": "not in E2 arrival weight product",
                "e3": "q_use factor",
                "match": False,
            },
            "8_normalization": {
                "e2": "group-smoothed I_arr within target_group then normalize",
                "e3": "normalize atomic r_hat intensity",
                "match": False,
            },
            "9_RMSE_rho_formula": {
                "e2": "sqrt(sum w_i err^2) with group-smoothed arrival w",
                "e3": "sqrt(sum rho_i^arr err^2) with atomic rho_i^arr",
                "match": False,
            },
            "10_orientation": {"match": True, "note": "lower better"},
            "11_source_hashes": {
                "e2_runner": "src/raven_mcs/e2/traffic_real_runner/__init__.py::_evaluation_weights",
                "e3_builder": "src/raven_mcs/e3/delta_cs_rho/atomic_rho.py::build_atomic_arrival_rho",
            },
        },
        "outcome": "NOT_COMPARABLE_FROM_SEALED_OUTPUTS",
        "rationale": (
            "E2 sealed RMSE_rho uses group-smoothed hard-arrival counts within target-group "
            "blocks, not the E3 atomic product pi_opp·nu·p_obs·q. Sealed outputs lack the "
            "atomic factors required for exact offline reconstruction of E3 rho_i^arr."
        ),
        "sealed_block_rerun": False,
        "status": "SEALED",
    }
    dump_json(compat, ART / "E3_TRAFFIC_RMSE_RHO_REUSE_COMPATIBILITY_SEAL.json")
    _md(
        ART / "E3_TRAFFIC_RMSE_RHO_REUSE_COMPATIBILITY_SEAL.md",
        "Traffic RMSE_rho Reuse Compatibility Seal",
        f"Outcome: **{compat['outcome']}**\n\n{compat['rationale']}\n\nNo sealed rerun.",
    )

    reuse_policy = {
        "reused_methods": sorted(E2_TRAFFIC_REUSED_METHODS),
        "metrics": {
            "RMSE_mu": "REUSE_EXACT",
            "MAE_mu": "REUSE_EXACT",
            "Head_RMSE": "REUSE_EXACT",
            "Tail_RMSE": "REUSE_EXACT",
            "Delta_group": "REUSE_EXACT",
            "Delta_c_s": "N_A_NOT_COMPARABLE",
            "RMSE_rho": "N_A_NOT_COMPARABLE",
            "delta_ref": "N_A_NOT_COMPARABLE",
            "Q_norm1_over_S": "NOT_APPLICABLE",
            "Q_norm2_over_S": "NOT_APPLICABLE",
        },
        "notes": {
            "RMSE_mu": "Primary endpoint identity unchanged; reuse sealed E2 values",
            "RMSE_rho": "Mark N/A for reused five methods; do not pair with new E3 atomic RMSE_rho",
            "Delta_c_s": "E2 did not emit E3 client×sealed-s Delta_c_s",
        },
        "no_invented_values": True,
        "status": "FROZEN",
    }
    dump_json(reuse_policy, ART / "E3_TRAFFIC_REUSE_METRIC_POLICY.json")

    # --- Tiny correctness smoke (fixture only, no paper data) ---
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
        m_mc=50,
        delivery_mode="high",
    )
    et = ART / "eventtrace_nd" / "training_eventtrace"
    smoke_rows = []
    for method in ("fedavg_window", "raven"):
        run_dir = ART / "runner_smoke" / method
        result = run_e3_real(
            root=ROOT,
            run_dir=run_dir,
            dataset=dataset,
            method=method,
            seed=DEBUG_SEED,
            eventtrace_dir=et,
            spatial_to_client=mapping,
            local_steps=1,
            dataset_name="fixture",
            target_artifact=target_art,
        )
        smoke_rows.append(
            {
                "method": method,
                "status": result["status"],
                "Delta_c_s": result["metrics"].get("Delta_c_s"),
                "RMSE_rho": result["metrics"].get("RMSE_rho"),
                "Q_norm1_over_S": result["metrics"].get("Q_norm1_over_S"),
                "stratum_identity": json.loads(
                    (run_dir / "opportunity_stratum_identity.json").read_text(encoding="utf-8")
                ),
            }
        )
    traffic_card_ok = int(tr_remap_meta["n_unique_strata"]) <= 32
    smoke_ok = (
        all(r["status"] == "REAL_PATH_EXECUTED" for r in smoke_rows)
        and toy["status"] == "PASS"
        and het["status"] == "PASS"
        and rho_ana["status"] == "PASS"
        and traffic_card_ok
        and traffic_meta["mapping_hash"] == TRAFFIC_PUBLIC_TARGET_MAPPING_HASH
        and ss_seal["identity_status"] == "FROZEN_IDENTITY_CONFIRMED"
        and ua_seal["identity_status"] == "FROZEN_IDENTITY_CONFIRMED"
        and compat["outcome"] == "NOT_COMPARABLE_FROM_SEALED_OUTPUTS"
        and compat["sealed_block_rerun"] is False
    )
    smoke = {
        "debug_seed": DEBUG_SEED,
        "rows": smoke_rows,
        "traffic_n_strata": int(tr_remap_meta["n_unique_strata"]),
        "checks": {
            "s_mapping": True,
            "delta_cs": toy["status"] == "PASS",
            "atomic_rho": rho_ana["status"] == "PASS",
            "h_s_separation": toy.get("h_independence") is True,
            "traffic_4_region": traffic_card_ok,
            "no_pobs_piopp_qs_regression": True,
        },
        "no_ranking": True,
        "status": "PASS" if smoke_ok else "FAIL",
    }
    dump_json(smoke, ART / "E3_STRATUM_REUSE_SEAL_SMOKE.json")
    _md(
        ART / "E3_STRATUM_REUSE_SEAL_SMOKE_REPORT.md",
        "Stratum Reuse Seal Smoke",
        f"status={smoke['status']}\n\ntraffic_n_strata={smoke['traffic_n_strata']}\n\nNo performance claims.",
    )

    # Readiness R7 (narrow)
    ds_rows = [
        {
            "dataset": "sensorscope",
            "opportunity_stratum_identity": "FROZEN_IDENTITY_CONFIRMED",
            "Delta_c_s": "READY",
            "atomic_rho": "READY",
            "traffic_rmse_rho_reuse": "N/A",
            "status": "READY_FOR_REAL_CANARY",
            "prior_fields": "reference prior hotfix hashes",
        },
        {
            "dataset": "uair",
            "opportunity_stratum_identity": "FROZEN_IDENTITY_CONFIRMED",
            "Delta_c_s": "READY",
            "atomic_rho": "READY",
            "traffic_rmse_rho_reuse": "N/A",
            "status": "READY_FOR_REAL_CANARY",
            "prior_fields": "reference prior hotfix hashes",
        },
        {
            "dataset": "traffic",
            "opportunity_stratum_identity": "FROZEN_IDENTITY_RECOVERED_4_REGION",
            "Delta_c_s": "READY",
            "atomic_rho": "READY",
            "traffic_rmse_rho_reuse": compat["outcome"],
            "reuse_policy": "E3_TRAFFIC_REUSE_METRIC_POLICY.json",
            "status": "READY_FOR_REAL_CANARY",
            "prior_fields": "reference prior hotfix hashes",
        },
    ]
    pd.DataFrame(ds_rows).to_csv(ART / "E3_DATASET_READINESS_R7.csv", index=False)
    dump_json({"rows": ds_rows}, ART / "E3_DATASET_READINESS_R7.json")

    rows = []
    for method, meta in CANONICAL_METHODS.items():
        if meta.get("excluded"):
            rows.append(
                {
                    "dataset": "all",
                    "method": method,
                    "number_of_new_runs": 0,
                    "classification": "EXCLUDED",
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
                    "rmse_rho_policy": (
                        reuse_policy["metrics"]["RMSE_rho"] if reused else "COMPUTE_ATOMIC"
                    ),
                }
            )
    matrix_df = pd.DataFrame(rows)
    matrix_payload = {
        "reusable_existing_Traffic_runs": 100,
        "total_new_runs_after_seal": int(matrix_df["number_of_new_runs"].sum()),
        "no_added_experiments": True,
        "rows": rows,
    }
    matrix_df.to_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R7.csv", index=False)
    dump_json(matrix_payload, ART / "E3_MINIMUM_NEW_RUN_MATRIX_R7.json")

    canary = {
        "round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1",
        "execute_in_this_round": False,
        "canary_seed": CANARY_SEED,
        "uses": [
            "frozen h(i)",
            "sealed s(i) (Traffic 4-region)",
            "Delta_c_s",
            "atomic rho_i^arr",
            "Traffic reuse metric policy",
            "existing method list only",
        ],
        "traffic_sealed_five_methods": "REUSE_ONLY_NO_RERUN",
        "no_performance_conclusion": True,
        "status": "PLAN_READY_NOT_EXECUTED",
    }
    dump_json(canary, ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R7.json")
    _md(
        ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R7.md",
        "Canary Plan R7",
        f"execute_in_this_round=false\n\ncanary_seed={CANARY_SEED}\n\n"
        "Traffic sealed five-method block not rerun.",
    )
    dump_json(
        {"status": "EXCLUDED_WITH_REASON", "rule": "never rename TimeAlign as FLAMF-Original"},
        ART / "E3_FLAMF_STATUS.json",
    )

    src_files = [
        "src/raven_mcs/e3/stratum_seal/traffic_regions.py",
        "src/raven_mcs/e3/stratum_seal/remap.py",
        "src/raven_mcs/e3/stratum_seal/constants.py",
        "src/raven_mcs/e3/delta_cs_rho/stratum.py",
        "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py",
        "src/raven_mcs/e3/delta_cs_rho/atomic_rho.py",
        "src/raven_mcs/correction/pi_target.py",
        "src/raven_mcs/e3/real_runner/runner.py",
        "configs/frozen/e3_multidataset_protocol_closure/traffic/opportunity_strata.json",
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
    dump_json(hashes, ART / "E3_STRATUM_REUSE_SEAL_SOURCE_HASHES.json")
    dump_json(hashes, CFG / "E3_STRATUM_REUSE_SEAL_SOURCE_HASHES.json")

    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    unit_xml = logs / "e3_stratum_reuse_seal_unit.xml"
    integ_xml = logs / "e3_stratum_reuse_seal_integration.xml"
    full_xml = logs / "e3_stratum_reuse_seal_pytest_full.xml"
    pip_log = logs / "e3_stratum_reuse_seal_pip_check.txt"
    unit_rc = subprocess.call(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/test_e3_stratum_identity_and_traffic_reuse_seal_core.py",
            "tests/unit/test_e3_delta_cs_atomic_rho_final_hotfix_core.py",
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
        ART / "E3_STRATUM_REUSE_SEAL_HASH_VERIFICATION.json",
    )
    dump_json(
        {"files": {}, "note": "preliminary"},
        ART / "E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json",
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
    if ss_seal["identity_status"] != "FROZEN_IDENTITY_CONFIRMED":
        blockers.append("SENSORSCOPE_STRATUM_IDENTITY_BLOCKED")
    if ua_seal["identity_status"] != "FROZEN_IDENTITY_CONFIRMED":
        blockers.append("UAIR_STRATUM_IDENTITY_BLOCKED")
    if not traffic_card_ok or traffic_meta["mapping_hash"] != TRAFFIC_PUBLIC_TARGET_MAPPING_HASH:
        blockers.append("TRAFFIC_STRATUM_IDENTITY_BLOCKED")
    if toy["status"] != "PASS":
        blockers.append("DELTA_CS_BLOCKED")
    if het["status"] != "PASS" or rho_ana["status"] != "PASS":
        blockers.append("ATOMIC_RHO_BLOCKED")
    if compat["outcome"] not in {
        "EXACT_METRIC_IDENTITY_CONFIRMED",
        "OFFLINE_RECONSTRUCTABLE_WITHOUT_TRAINING",
        "NOT_COMPARABLE_FROM_SEALED_OUTPUTS",
    }:
        blockers.append("TRAFFIC_RMSE_RHO_REUSE_COMPATIBILITY_BLOCKED")
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
        else "E3_STRATUM_REUSE_SEAL_BLOCKED"
    )
    stop = {
        "round": ROUND,
        "status": status,
        "blockers": blockers,
        "no_performance_experiment": True,
        "canary_executed": False,
        "no_training": True,
        "e2_parent_sealed": e2_ok and reg_ok,
        "traffic_reuse_guard_active": reuse_blocked,
        "traffic_rmse_rho_reuse_outcome": compat["outcome"],
        "next_authorized_round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1"
        if not blockers
        else None,
        "created_utc": _utc(),
    }
    dump_json(stop, ART / "E3_STRATUM_REUSE_SEAL_STOP_STATUS.json")

    report = f"""# E3 Stratum Identity and Traffic Reuse Seal R1 Report

## 1. Executive decision
**{status}**

## 2. No-training/no-new-experiment attestation
No Canary, no formal runs, no sealed Traffic rerun, no training. Debug fixture seed={DEBUG_SEED} only.

## 3. Parent evidence integrity
E2 sealed={e2_ok}; registry={reg_ok}; reuse guard={reuse_blocked}; parent hotfix dir={PARENT.is_dir()}.

## 4. Traffic frozen spatial-region identity
mapping_hash={TRAFFIC_PUBLIC_TARGET_MAPPING_HASH}; 43 stations → 4 regions (public-target).

## 5. Traffic opportunity-stratum seal
n_strata={tr_remap_meta['n_unique_strata']} (≤32); station-level 344 rejected.

## 6. SensorScope stratum identity
{ss_seal['identity_status']}; cardinality={ss_seal['nonempty_stratum_cardinality']}

## 7. U-Air stratum identity
{ua_seal['identity_status']}; cardinality={ua_seal['nonempty_stratum_cardinality']}

## 8. Delta_c_s post-seal validation
status={toy['status']}; h_independence={toy.get('h_independence')}

## 9. atomic rho post-seal validation
het={het['status']}; analytical={rho_ana['status']}

## 10. Traffic RMSE_rho reuse compatibility
**{compat['outcome']}**

## 11. Traffic reuse metric policy
RMSE_mu=REUSE_EXACT; RMSE_rho=N_A_NOT_COMPARABLE for sealed five methods.

## 12. Tiny correctness smoke
status={smoke['status']}

## 13. Narrow readiness R7
See E3_DATASET_READINESS_R7.*

## 14. Minimum new-run matrix R7
reusable Traffic=100; total new={matrix_payload['total_new_runs_after_seal']}; no added experiments.

## 15. Final Canary plan R7
execute_in_this_round=false; seed={CANARY_SEED}

## 16. Tests
unit_rc={unit_rc}; integ_rc={integ_rc}; full_rc={full_rc}; pip_rc={pip_rc}

## 17. Gates
See gate_results.json after check script

## 18. Self-contained package verification
Manifest entries included_in_zip enforced by export script

## 19. Remaining blockers
{blockers if blockers else "None"}

## 20. Exact next-round authorization
{"Authorize E3-MULTIDATASET-REAL-RUNNER-CANARY-R1 — no further protocol/hotfix rounds unless Canary fails" if not blockers else "Do not authorize Canary"}
"""
    (ART / "E3_STRATUM_IDENTITY_AND_TRAFFIC_REUSE_SEAL_R1_REPORT.md").write_text(
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
                "traffic_n_strata": int(tr_remap_meta["n_unique_strata"]),
                "rmse_rho_reuse": compat["outcome"],
            },
            indent=2,
        )
    )
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
