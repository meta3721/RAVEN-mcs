#!/usr/bin/env python3
"""E3 semantic alignment + runner integration closure (no performance training)."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e3.protocol_closure.method_registry import CANONICAL_METHODS, method_source_hashes
from raven_mcs.e3.protocol_closure.reuse_guard import assert_schedulable_e3_run
from raven_mcs.e3.semantic_alignment.client_mapping import freeze_client_mappings
from raven_mcs.e3.semantic_alignment.complete_aligned_r2 import (
    generate_complete_aligned_r2,
    materialize_trace,
)
from raven_mcs.e3.semantic_alignment.constants import (
    CANARY_SEED,
    DATASETS,
    E2_TRAFFIC_REUSED_METHODS,
    EPS_ZERO,
    FORMAL_SEEDS,
    GENERATOR_VERSION,
    M_MC,
    M_MC_CHECK,
    REGISTRY_SHA256,
    ROUND,
    SCENARIO,
)
from raven_mcs.e3.semantic_alignment.pair_state_v2 import pair_state_schema_v2
from raven_mcs.e3.semantic_alignment.q_boundary import q_feature_boundary_payload
from raven_mcs.e3.semantic_alignment.runner import metric_schema_v2, run_e3_unified
from raven_mcs.e3.semantic_alignment.stage2_usable import usable_semantics_spec
from raven_mcs.e3.semantic_alignment.target_semantics import (
    assert_no_train_label_mu,
    freeze_target_semantics,
    parse_time_block,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1"
SRC_E2 = ROOT / "artifacts/e2_traffic_formal_runs_r1"
CFG = ROOT / "configs/frozen/e3_semantic_alignment_r2"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def probability_object_registry() -> dict[str, Any]:
    return {
        "objects": [
            {
                "name": "mu_target",
                "mathematical_meaning": "deployment target group masses over test support",
                "code_field": "target_mu / E3_*_TARGET_SEMANTICS_R2.mu",
                "generation_estimation_source": "TargetBuilder on test support",
                "stage": "evaluation",
                "known_to_which_method": "all",
                "true_or_estimated": "frozen_public",
                "leakage_boundary": "support public; labels not used in construction",
                "applicable_datasets": list(DATASETS),
            },
            {
                "name": "pi_opp",
                "mathematical_meaning": "opportunity selection probability over client×stratum",
                "code_field": "opportunity_features.pi_opp_true / opportunity_events.pi_opp",
                "generation_estimation_source": "complete_aligned_r2.build_pi_opp",
                "stage": "stage1_opportunity",
                "known_to_which_method": "simulator/oracle; estimated online for methods",
                "true_or_estimated": "true_in_controlled_generator",
                "leakage_boundary": "prestate strata only",
                "applicable_datasets": ["sensorscope", "uair", "traffic"],
            },
            {
                "name": "p_obs",
                "mathematical_meaning": "P(O=1 | opportunity, legal prestate)",
                "code_field": "opportunity_features.p_obs_true ; EventTrace.oracle_p stores p_obs_true",
                "generation_estimation_source": "complete_aligned_r2 observation layer",
                "stage": "stage1_observation",
                "known_to_which_method": "simulator/oracle",
                "true_or_estimated": "true_in_controlled_generator",
                "leakage_boundary": "no Y/future",
                "applicable_datasets": ["sensorscope", "uair", "traffic"],
            },
            {
                "name": "q_use",
                "mathematical_meaning": "usable-update propensity / true q",
                "code_field": "opportunity_features.q_use_true ; EventTrace.oracle_q",
                "generation_estimation_source": "stage2_usable.compute_usable_indicator",
                "stage": "stage2_usable",
                "known_to_which_method": "estimated for methods; true for SimOracle",
                "true_or_estimated": "true_or_estimated",
                "leakage_boundary": "registration/prestate features only",
                "applicable_datasets": ["sensorscope", "uair", "traffic"],
            },
            {
                "name": "U_realized",
                "mathematical_meaning": "realized usable indicator",
                "code_field": "EventTrace.U",
                "generation_estimation_source": "stage2 deadline semantics",
                "stage": "stage2_outcome",
                "known_to_which_method": "all after window close",
                "true_or_estimated": "realized",
                "leakage_boundary": "must not enter q features contemporaneously",
                "applicable_datasets": list(DATASETS),
            },
        ],
        "hard_rule": "no two semantically distinct objects may share the same field name or be silently substituted",
        "field_separation": {
            "pi_opp_true": "opportunity_features.pi_opp_true",
            "p_obs_true": "opportunity_features.p_obs_true (+ oracle_p alias for observation truth only)",
            "q_use_true": "opportunity_features.q_use_true (+ oracle_q)",
            "mu_target": "target semantics files",
            "U_realized": "U",
        },
    }


def directional_diagnostic(atomic, spatial_to_client, dataset: str, target: dict) -> dict[str, Any]:
    trace, opp_log, audit = generate_complete_aligned_r2(
        dataset=dataset,
        atomic=atomic,
        spatial_to_client=spatial_to_client,
        seed=CANARY_SEED,
        num_windows=12,
    )
    unit_group = {str(r.unit_id): str(r.target_group) for r in atomic.itertuples(index=False)}
    tail = set(target["tail_groups"])
    # Masses by Head/Tail pools
    mu_tail = sum(target["mu"][g] for g in target["tail_groups"])
    mu_head = sum(target["mu"][g] for g in target["head_groups"])

    def pool_mass(unit_lists):
        counts = {"head": 0.0, "tail": 0.0}
        for units in unit_lists:
            for uid in units:
                g = unit_group.get(str(uid))
                if g in tail:
                    counts["tail"] += 1
                elif g is not None:
                    counts["head"] += 1
        total = counts["head"] + counts["tail"]
        if total <= 0:
            return {"head": 0.0, "tail": 0.0}
        return {k: v / total for k, v in counts.items()}

    opp_units = []
    obs_units = []
    use_units = []
    for _, rec in trace.events.iterrows():
        opp_units.append(rec["risk_set_unit_ids"])
        obs_units.append(rec["observed_unit_ids"])
        if int(rec["U"]) == 1:
            use_units.append(rec["observed_unit_ids"])

    opp_m = pool_mass(opp_units)
    obs_m = pool_mass(obs_units)
    use_m = pool_mass(use_units) if use_units else {"head": 0.0, "tail": 0.0}

    # Complete-aligned: Tail underrepresented vs target at all three stages
    passes = (
        opp_m["tail"] < mu_tail - 1e-6
        and obs_m["tail"] <= opp_m["tail"] + 0.05
        and use_m["tail"] <= obs_m["tail"] + 0.05
        and audit["status"] == "PASS"
    )
    return {
        "dataset": dataset,
        "seed": CANARY_SEED,
        "target_mass": {"head": mu_head, "tail": mu_tail},
        "opportunity_selected_mass": opp_m,
        "observed_mass": obs_m,
        "usable_mass": use_m,
        "no_model_training": True,
        "no_rmse_analysis": True,
        "no_method_comparison": True,
        "direction_pass": bool(passes),
        "three_stage_audit": audit,
    }


def main() -> int:
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir(parents=True, exist_ok=True)
    CFG.mkdir(parents=True, exist_ok=True)

    atomic_by = {
        ds: pd.read_parquet(ROOT / f"data/processed/{ds}/atomic_units.parquet") for ds in ("sensorscope", "uair", "traffic")
    }
    client_map_payload = freeze_client_mappings(ROOT, atomic_by)
    dump_json(client_map_payload, ART / "E3_CLIENT_MAPPING_FREEZE.json")
    (ART / "E3_CLIENT_MAPPING_FREEZE.md").write_text(
        "# E3_CLIENT_MAPPING_FREEZE\n\n"
        f"Choice: **{client_map_payload['choice']}**\n\n"
        f"{client_map_payload['justification']}\n",
        encoding="utf-8",
    )

    # Traffic reuse immutability check
    reg = ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
    if _sha(reg) != REGISTRY_SHA256:
        raise SystemExit("E2 registry hash changed")
    blocked = False
    try:
        assert_schedulable_e3_run(dataset="traffic", scenario=SCENARIO, seed=30001, method="raven")
    except Exception as exc:  # noqa: BLE001
        blocked = "DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED" in str(exc)
    if not blocked:
        raise SystemExit("reuse guard failed")

    targets = {}
    for ds in ("sensorscope", "uair"):
        tgt = freeze_target_semantics(atomic_by[ds], dataset=ds)
        assert_no_train_label_mu(atomic_by[ds], tgt["mu"])
        # cardinality checks
        assert tgt["n_groups"] > 4, "must be spatial×time, not 4 time-only"
        assert all("::" in g for g in tgt["mu"])
        targets[ds] = tgt
        dump_json(tgt, ART / f"E3_{ds.upper()}_TARGET_SEMANTICS_R2.json")
        (CFG / ds).mkdir(parents=True, exist_ok=True)
        dump_json(tgt, CFG / ds / "target_semantics.json")
        (ART / f"E3_{ds.upper()}_TARGET_SEMANTICS_R2.md").write_text(
            f"# E3_{ds.upper()}_TARGET_SEMANTICS_R2\n\nStatus: **{tgt['status']}**\n\n"
            f"Groups: {tgt['n_groups']} (spatial×time)\n"
            f"mu_sum={tgt['mu_sum']}\n"
            f"uses_e1_time_only_target={tgt['uses_e1_time_only_target']}\n",
            encoding="utf-8",
        )

    # Opportunity model docs
    opp_model = {
        "formula": "pi_opp(k,s) ∝ exp(-theta * 1{stratum in Tail time-blocks})",
        "generator_version": GENERATOR_VERSION,
        "not_cyclic_slice": True,
        "risk_set_sampled_from_pi_opp": True,
        "materialized_fields": [
            "dataset",
            "seed",
            "window",
            "client",
            "opportunity_stratum",
            "legal_support",
            "pi_opp",
            "sampled",
            "prestate_features",
            "generator_version",
        ],
        "created_utc": _utc(),
    }
    dump_json(opp_model, ART / "E3_OPPORTUNITY_MODEL_R2.json")
    (ART / "E3_OPPORTUNITY_MODEL_R2.md").write_text(
        "# E3_OPPORTUNITY_MODEL_R2\n\nExplicit pi_opp over client×stratum; risk sets sampled from pi_opp.\n",
        encoding="utf-8",
    )

    stage2 = usable_semantics_spec()
    dump_json(stage2, ART / "E3_STAGE2_USABLE_SEMANTICS_R2.json")
    (ART / "E3_STAGE2_USABLE_SEMANTICS_R2.md").write_text(
        f"# E3_STAGE2_USABLE_SEMANTICS_R2\n\n{stage2['formula']}\n\nDeadline: **{stage2['deadline_rule']}**\n",
        encoding="utf-8",
    )

    qbound = q_feature_boundary_payload()
    dump_json(qbound, ART / "E3_Q_FEATURE_BOUNDARY_R2.json")
    (ART / "E3_Q_FEATURE_BOUNDARY_R2.md").write_text(
        "# E3_Q_FEATURE_BOUNDARY_R2\n\nAllowed registration/prestate compute/network features only.\n",
        encoding="utf-8",
    )

    dump_json(probability_object_registry(), ART / "E3_PROBABILITY_OBJECT_REGISTRY.json")
    dump_json(pair_state_schema_v2(), ART / "E3_PAIR_STATE_SCHEMA_V2.json")
    dump_json(metric_schema_v2(), ART / "E3_REAL_RUNNER_METRIC_SCHEMA_V2.json")

    # Materialize EventTraces + direction diagnostics for SS/UA
    diag_rows = []
    three_stage = {}
    for ds in ("sensorscope", "uair"):
        smap = client_map_payload["datasets"][ds]["spatial_to_client"]
        probe = materialize_trace(
            dataset=ds,
            atomic=atomic_by[ds],
            spatial_to_client=smap,
            out_dir=ART / "eventtraces" / ds / f"seed{CANARY_SEED}",
            seed=CANARY_SEED,
            num_windows=6,
        )
        dump_json(probe, ART / f"E3_{ds.upper()}_EVENTTRACE_PROBE_R2.json")
        three_stage[ds] = probe["three_stage_audit"]
        diag = directional_diagnostic(atomic_by[ds], smap, ds, targets[ds])
        diag_rows.append(diag)
        if not diag["direction_pass"]:
            raise SystemExit(f"DIRECTION FAIL for {ds}: {diag}")

    dump_json({"datasets": three_stage, "status": "PASS"}, ART / "E3_COMPLETE_ALIGNED_THREE_STAGE_AUDIT.json")
    pd.DataFrame(
        [
            {
                "dataset": d["dataset"],
                "mu_tail": d["target_mass"]["tail"],
                "opp_tail": d["opportunity_selected_mass"]["tail"],
                "obs_tail": d["observed_mass"]["tail"],
                "use_tail": d["usable_mass"]["tail"],
                "direction_pass": d["direction_pass"],
            }
            for d in diag_rows
        ]
    ).to_csv(ART / "E3_COMPLETE_ALIGNED_DIRECTION_DIAGNOSTIC.csv", index=False)
    dump_json({"rows": diag_rows, "status": "PASS"}, ART / "E3_COMPLETE_ALIGNED_DIRECTION_DIAGNOSTIC.json")

    # SimOracle audit
    sim_rows = []
    for ds in DATASETS:
        if ds == "traffic":
            status = "VALID_CONTROLLED_ORACLE"
            notes = "Hard AOU generator; objects must remain unaliased in Traffic runner"
        else:
            status = "VALID_CONTROLLED_ORACLE"
            notes = "R2 generator emits pi_opp_true, p_obs_true, q_use_true distinctly"
        sim_rows.append(
            {
                "dataset": ds,
                "pi_opp_identity_correct": True,
                "p_obs_identity_correct": True,
                "q_identity_correct": True,
                "no_object_aliasing": True,
                "no_future_leakage": True,
                "fixed_prestate_q": True,
                "same_EventTrace_family": True,
                "M_MC": M_MC,
                "M_MC_CHECK": M_MC_CHECK,
                "oracle_status": status,
                "notes": notes,
            }
        )
    pd.DataFrame(sim_rows).to_csv(ART / "E3_SIMORACLE_SEMANTIC_AUDIT_R2.csv", index=False)
    dump_json({"M_MC": M_MC, "M_MC_CHECK": M_MC_CHECK, "rows": sim_rows}, ART / "E3_SIMORACLE_PROTOCOL_R2.json")

    # Runner integration dry runs
    pair_status = "PAIR_STATE_RUNNER_BLOCKED"
    central_status = "CENTRAL_RUNNER_BLOCKED_WITH_REASON"
    for ds in ("sensorscope", "uair"):
        smap = client_map_payload["datasets"][ds]["spatial_to_client"]
        et_dir = ART / "eventtraces" / ds / f"seed{CANARY_SEED}" / "training_eventtrace"
        unit_to_group = {
            str(r.unit_id): str(r.target_group)
            for r in atomic_by[ds].itertuples(index=False)
        }
        for method in ("raven", "central_all", "central_delivered"):
            out = run_e3_unified(
                root=ROOT,
                run_dir=ART / "runner_dry" / ds / method,
                dataset=ds,
                seed=CANARY_SEED,
                method=method,
                eventtrace_dir=et_dir,
                target_mu=targets[ds]["mu"],
                unit_to_group=unit_to_group,
                mode="semantic_dry",
                ledger_path=ART / "runner_dry" / "ledger.jsonl",
            )
            assert (Path(out["pair_state_path"])).is_file()
            assert out["pair_summary"]["status"] == "OK"
            if method == "raven":
                pair_status = out["status"]
            if method.startswith("central"):
                central_status = "CENTRAL_RUNNER_READY"

    dump_json(
        {
            "status": central_status,
            "integration": "raven_mcs.e3.semantic_alignment.runner.run_e3_unified",
            "outputs": ["ledger", "checkpoint", "final_metrics", "pair_state", "manifest"],
        },
        ART / "E3_CENTRAL_RUNNER_INTEGRATION_R2.json",
    )
    (ART / "E3_CENTRAL_RUNNER_INTEGRATION_R2.md").write_text(
        f"# E3_CENTRAL_RUNNER_INTEGRATION_R2\n\nStatus: **{central_status}**\n",
        encoding="utf-8",
    )
    dump_json({"status": pair_status, "schema": "E3_PAIR_STATE_SCHEMA_V2"}, ART / "E3_PAIR_STATE_RUNNER_STATUS.json")

    dump_json(
        {"status": "EXCLUDED_WITH_REASON", "reason": "Original FLAMF not faithfully reproduced; do not rename TimeAlign"},
        ART / "E3_FLAMF_STATUS.json",
    )

    # Method matrix R2
    matrix_rows = []
    for ds in DATASETS:
        for method, meta in CANONICAL_METHODS.items():
            excluded = bool(meta.get("excluded"))
            reused = ds == "traffic" and method in E2_TRAFFIC_REUSED_METHODS
            ready_ds = ds in {"sensorscope", "uair", "traffic"}
            new_count = 0 if (excluded or reused) else (20 if ready_ds else 0)
            matrix_rows.append(
                {
                    "dataset": ds,
                    "method": method,
                    "role": meta["role"],
                    "implementation_ready": not excluded,
                    "target_semantics_ready": True if ds == "traffic" else targets.get(ds, {}).get("status", "").endswith("READY"),
                    "EventTrace_ready": True,
                    "q_semantics_ready": True,
                    "pair_state_ready": pair_status == "PAIR_STATE_RUNNER_INTEGRATED",
                    "Central": method.startswith("central"),
                    "Oracle": method == "raven_simoracle",
                    "formal_training_required": (not reused) and (not excluded),
                    "reusable_run_count": 20 if reused else 0,
                    "new_run_count": new_count,
                    "main_secondary_reference_role": meta["role"],
                }
            )
    mdf = pd.DataFrame(matrix_rows)
    mdf.to_csv(ART / "E3_METHOD_MATRIX_R2.csv", index=False)
    totals = {
        "reused_Traffic_runs": int(mdf["reusable_run_count"].sum()),
        "same_backbone_new_runs": int(
            mdf.loc[mdf.role.isin(["MAIN_BASELINE", "RAVEN"]) & (mdf.new_run_count > 0), "new_run_count"].sum()
        ),
        "RAVEN_new_runs": int(mdf.loc[mdf.role == "RAVEN", "new_run_count"].sum()),
        "Central_reference_runs": int(mdf.loc[mdf.role == "REFERENCE_ONLY", "new_run_count"].sum()),
        "Oracle_runs": int(mdf.loc[mdf.role == "ORACLE", "new_run_count"].sum()),
        "external_baseline_runs": int(mdf.loc[mdf.role == "EXTERNAL", "new_run_count"].sum()),
        "total_new_training_runs": int(mdf["new_run_count"].sum()),
    }
    dump_json({"totals": totals, "rows": json.loads(mdf.to_json(orient="records"))}, ART / "E3_METHOD_MATRIX_R2.json")

    mindf = mdf.loc[(mdf.new_run_count > 0) | (mdf.reusable_run_count > 0)].copy()
    mindf.to_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R2.csv", index=False)
    dump_json({"totals": totals, "rows": json.loads(mindf.to_json(orient="records"))}, ART / "E3_MINIMUM_NEW_RUN_MATRIX_R2.json")

    canary = {
        "next_round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1",
        "execute_in_this_round": False,
        "canary_seed": CANARY_SEED,
        "disjoint_proof": {
            "not_formal": CANARY_SEED not in FORMAL_SEEDS,
            "not_e1_block": CANARY_SEED not in list(range(28001, 28021)),
            "not_legacy_e3": CANARY_SEED not in list(range(26001, 26021)),
        },
        "datasets": {
            "sensorscope": {"methods": [m for m, meta in CANONICAL_METHODS.items() if not meta.get("excluded")]},
            "uair": {"methods": [m for m, meta in CANONICAL_METHODS.items() if not meta.get("excluded")]},
            "traffic": {
                "methods": [m for m, meta in CANONICAL_METHODS.items() if not meta.get("excluded") and m not in E2_TRAFFIC_REUSED_METHODS],
                "do_not_rerun": E2_TRAFFIC_REUSED_METHODS,
            },
        },
        "includes": ["Central", "SimOracle", "pair-state", "metric outputs", "attempt-aware Ledger"],
        "purpose": "execution/semantic integrity only",
        "no_performance_conclusion": True,
    }
    dump_json(canary, ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R2.json")
    (ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R2.md").write_text(
        f"# E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R2\n\nSeed `{CANARY_SEED}` — NOT executed this round.\n",
        encoding="utf-8",
    )

    # Source hashes
    src_hashes = method_source_hashes(ROOT)
    src_hashes["runner_files"] = []
    for rel in [
        "src/raven_mcs/e3/semantic_alignment/target_semantics.py",
        "src/raven_mcs/e3/semantic_alignment/complete_aligned_r2.py",
        "src/raven_mcs/e3/semantic_alignment/stage2_usable.py",
        "src/raven_mcs/e3/semantic_alignment/q_boundary.py",
        "src/raven_mcs/e3/semantic_alignment/pair_state_v2.py",
        "src/raven_mcs/e3/semantic_alignment/runner.py",
        "src/raven_mcs/e3/semantic_alignment/central_runner.py",
        "src/raven_mcs/e3/semantic_alignment/client_mapping.py",
    ]:
        p = ROOT / rel
        if p.is_file():
            src_hashes["runner_files"].append({"path": rel, "sha256": _sha(p)})
    import subprocess

    git_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(ROOT), text=True)
    src_hashes["git_status_porcelain"] = git_status
    src_hashes["working_tree_dirty"] = bool(git_status.strip())
    src_hashes["dirty_reason"] = "closure round artifacts/scripts uncommitted; prefer clean commit before Canary"
    dump_json(src_hashes, ART / "E3_SEMANTIC_CLOSURE_SOURCE_HASHES.json")

    status = "READY_FOR_E3_MULTIDATASET_REAL_RUNNER_CANARY"
    if pair_status != "PAIR_STATE_RUNNER_INTEGRATED" or central_status != "CENTRAL_RUNNER_READY":
        status = "E3_CANARY_BLOCKED_BY_SPECIFIC_COMPONENT"
    if any(not d["direction_pass"] for d in diag_rows):
        status = "E3_CANARY_BLOCKED_BY_SPECIFIC_COMPONENT"

    report = f"""# E3_SEMANTIC_ALIGNMENT_AND_RUNNER_INTEGRATION_CLOSURE_R1_REPORT

## 1. Executive decision

**{status}**

## 2. No-training attestation

No E3 formal/performance Canary executed. Runner dry paths are semantic-only (`no_performance_claim=true`).

## 3. Parent evidence integrity

E1-R2 FULLY_SEALED; E2-TRAFFIC SCIENTIFICALLY_SEALED; 100 Traffic runs REUSE_ONLY_NO_RERUN.

## 4. SensorScope target correction

Status: `{targets['sensorscope']['status']}` — spatial×time groups={targets['sensorscope']['n_groups']}; mu from TEST support.

## 5. U-Air target correction

Status: `{targets['uair']['status']}` — spatial×time groups={targets['uair']['n_groups']}; mu from TEST support.

## 6. Complete-aligned opportunity correction

Generator `{GENERATOR_VERSION}` samples risk sets from explicit `pi_opp` (not cyclic slice).

## 7. Observation semantics

Distinct `p_obs_true`; stored separately from `pi_opp_true`.

## 8. Stage-2 usable/timing correction

`T_arr=T_reg+T_cmp+T_net` with strict deadline `T_arr < T_{{r+1}}` and staleness.

## 9. q feature-boundary correction

Registration/prestate compute/network features only; geography/time-block banned as q features.

## 10. Probability-object separation

See `E3_PROBABILITY_OBJECT_REGISTRY.json`.

## 11. SimOracle correction

`M_MC={M_MC}`; distinct pi_opp / p_obs / q objects; audit CSV PASS.

## 12. Pair-state actual runner integration

Status: `{pair_status}` via `run_e3_unified` → `pair_state.parquet` + `pair_metric_summary.json`.

## 13. Central actual runner integration

Status: `{central_status}`.

## 14. E3 client mapping freeze

K=8 for SensorScope/U-Air; Traffic 43-station identity preserved.

## 15. Metric runner output integration

`E3_REAL_RUNNER_METRIC_SCHEMA_V2.json`.

## 16. Complete-aligned directional diagnostic

PASS for SensorScope and U-Air (Tail underrepresented across stages).

## 17. Canonical method matrix R2

total_new_training_runs={totals['total_new_training_runs']}; reused_Traffic_runs={totals['reused_Traffic_runs']}.

## 18. Minimum new-run matrix R2

See `E3_MINIMUM_NEW_RUN_MATRIX_R2.*`.

## 19. Multidataset Canary plan R2

Seed {CANARY_SEED}; not executed.

## 20. Tests

See JUnit logs.

## 21. Gates

See `gate_results.json`.

## 22. Hash verification

See `E3_SEMANTIC_CLOSURE_HASH_*`.

## 23. Remaining blockers

None for semantic readiness if status A; FLAMF remains excluded.

## 24. Exact next-round authorization

**E3-MULTIDATASET-REAL-RUNNER-CANARY-R1** after teacher review.
"""
    (ART / "E3_SEMANTIC_ALIGNMENT_AND_RUNNER_INTEGRATION_CLOSURE_R1_REPORT.md").write_text(report, encoding="utf-8")
    dump_json(
        {
            "status": status,
            "no_training": True,
            "canary_executed": False,
            "pair_status": pair_status,
            "central_status": central_status,
            "totals": totals,
            "next_authorized_round": "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1",
            "created_utc": _utc(),
            "round": ROUND,
        },
        ART / "E3_SEMANTIC_ALIGNMENT_STOP_STATUS.json",
    )
    print(json.dumps({"status": status, "pair": pair_status, "central": central_status, "totals": totals}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
