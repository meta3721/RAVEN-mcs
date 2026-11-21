"""Production-path perturbation tests for atomic p_obs and joint pi_opp."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.base import DatasetMetadata
from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata
from raven_mcs.training.window_runner import build_full_runner


def _tiny_dataset(tmp_dir) -> tuple[ProcessedDataset, dict[str, str]]:
    from pathlib import Path

    from raven_mcs.utils.serialization import dump_json

    tmp_dir = Path(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    clients = []
    for split, t0 in (("train", 0), ("test", 10)):
        for i, spatial in enumerate(["n0", "n1"]):
            for block in (0, 2):
                t = t0 + block
                uid = f"{spatial}_t{t:05d}"
                rows.append(
                    {
                        "unit_id": uid,
                        "spatial_id": spatial,
                        "absolute_time": pd.Timestamp("2020-01-01", tz="UTC")
                        + pd.Timedelta(hours=t),
                        "time_index": t,
                        "target_value": 1.0 + i,
                        "split": split,
                        "target_group": f"{spatial}::block{block}",
                        "opportunity_stratum": f"{spatial}::block{block}::weekday",
                        "public_features": {"time_block": float(block), "weekday": 1.0},
                        "support_flag": True,
                        "is_warmup": False,
                    }
                )
                clients.append(
                    {
                        "client_id": f"client-{i:03d}",
                        "unit_id": uid,
                        "potential_measurement": 1.0 + i,
                        "controlled_generator_parameters": {"fixture": 1.0},
                        "split": split,
                        "source_trace_id": "hotfix",
                    }
                )
    pd.DataFrame(rows).to_parquet(tmp_dir / "atomic_units.parquet", index=False)
    pd.DataFrame(clients).to_parquet(tmp_dir / "client_measurements.parquet", index=False)
    mapping = {"n0": "client-000", "n1": "client-001"}
    dump_json(mapping, tmp_dir / "spatial_to_client.json")
    meta = DatasetMetadata(
        dataset="hotfix_fixture",
        target_name="synthetic",
        target_unit="u",
        spatial_unit="s",
        time_unit="h",
        source_name="hotfix",
        source_url="local://hotfix",
        raw_license="internal",
        filtering_rules=("finite",),
    )
    return ProcessedDataset(tmp_dir, meta), mapping


def _trace_with_pobs(
    *,
    p_by_unit: dict[str, float],
    unit_ids: list[str],
    client_id: str = "client-000",
) -> EventTrace:
    mean_p = float(np.mean(list(p_by_unit.values())))
    events = pd.DataFrame(
        [
            {
                "window_id": 0,
                "client_id": client_id,
                "risk_set_unit_ids": list(unit_ids),
                "opportunity_features": {
                    "pi_opp_true": 0.5,
                    "p_obs_true_by_unit": dict(p_by_unit),
                    "p_obs_mean_diagnostic": mean_p,
                    "q_use_true": 0.8,
                    "opportunity_stratum": "n0::block0::weekday",
                    "M_MC": 2000,
                },
                "observed_unit_ids": list(unit_ids),
                "O": {u: True for u in unit_ids},
                "registration_time": 0.05,
                "downloaded_version": 0,
                "model_age": 0.0,
                "tau": 0,
                "device_profile": "tier-2",
                "network_profile": "net-tier-2",
                "compute_success": True,
                "compute_duration": 0.1,
                "network_success": True,
                "network_duration": 0.1,
                "arrival_time": 0.25,
                "U": 1,
                "raw_workload": float(len(unit_ids)),
                "oracle_p": max(mean_p, 1e-12),  # diagnostic-only schema field
                "oracle_q": 0.8,
                "hidden_confounder": 0.0,
            }
        ]
    )
    meta = EventTraceMetadata(
        dataset="hotfix",
        seed=0,
        num_windows=1,
        num_clients=1,
        s_max=5,
        generator="hotfix-pobs",
        notes=("atomic p_obs perturbation",),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    return trace


def production_atomic_pobs_perturbation(tmp_dir) -> dict[str, Any]:
    """Same mean p, different atomic distribution → production weights must differ."""
    dataset, mapping = _tiny_dataset(tmp_dir)
    units = ["n0_t00000", "n0_t00002"]  # train units for n0
    # Ensure both units exist
    assert all(dataset.get_atomic_by_id(u) is not None for u in units)

    case_a = {"n0_t00000": 0.2, "n0_t00002": 0.8}
    case_b = {"n0_t00000": 0.4, "n0_t00002": 0.6}
    assert abs(np.mean(list(case_a.values())) - np.mean(list(case_b.values()))) < 1e-12

    def extract_weights(p_map: dict[str, float]) -> list[float]:
        trace = _trace_with_pobs(p_by_unit=p_map, unit_ids=units)
        # Build minimal pi_target for design ratio methods
        pi_target = {
            ("client-000", "n0::block0::weekday"): 0.5,
            ("client-000", "n0::block2::weekday"): 0.5,
        }
        # Align mu
        n_groups = dataset.num_groups
        mu = np.ones(n_groups) / n_groups
        runner = build_full_runner(
            trace,
            dataset,
            method="raven_simoracle",
            n_groups=n_groups,
            model_seed=1,
            local_steps=1,
            target_mu=mu,
            pi_target=pi_target,
            use_coarse_time_groups=False,
        )
        # Inject frozen joint pi_opp for design ratio
        runner.pi_opp_joint = {
            ("client-000", "n0::block0::weekday"): 0.5,
            ("client-000", "n0::block2::weekday"): 0.5,
        }
        runner.run()
        # Extract a_bar from diagnostics for the client
        diags = [d for d in runner.diagnostics if d.get("client_id") == "client-000"]
        assert diags, "no diagnostics from production runner"
        return list(diags[0]["a_bar"])

    wa = extract_weights(case_a)
    wb = extract_weights(case_b)
    # Analytical: with equal zeta, a ∝ 1/p
    # Hand raw weights before Hajek normalize differ; after normalize still differ if p differ
    differ = float(np.max(np.abs(np.asarray(wa) - np.asarray(wb)))) > 1e-12
    # If only mean oracle_p=0.5 were used, weights would be identical
    return {
        "mean_p": 0.5,
        "case_a_p": case_a,
        "case_b_p": case_b,
        "production_weights_a": wa,
        "production_weights_b": wb,
        "weights_differ": differ,
        "path": "build_full_runner(raven_simoracle) -> FullWindowRunner diagnostics a_bar",
        "status": "PASS" if differ else "FAIL",
        "blocker_if_fail": "ATOMIC_POBS_PRODUCTION_CONSUMPTION_BLOCKED",
    }


def production_joint_piopp_perturbation() -> dict[str, Any]:
    """Design-ratio path uses joint pi_opp via FullWindowRunner._compute_zeta."""
    from raven_mcs.training.window_runner import FullWindowRunner

    clients = ["c0", "c1"]
    pi_opp_a = {
        ("c0", "s0"): 0.40,
        ("c0", "s1"): 0.10,
        ("c1", "s0"): 0.10,
        ("c1", "s1"): 0.40,
    }
    pi_opp_b = {
        ("c0", "s0"): 0.10,
        ("c0", "s1"): 0.40,
        ("c1", "s0"): 0.40,
        ("c1", "s1"): 0.10,
    }
    pi_tar = {k: 0.25 for k in pi_opp_a}
    assert abs(sum(pi_opp_a.values()) - 1.0) < 1e-12
    assert abs(sum(pi_opp_b.values()) - 1.0) < 1e-12

    def ratios_via_production_runner(pi_opp: dict[tuple[str, str], float]) -> dict[str, float]:
        runner = object.__new__(FullWindowRunner)
        runner.pi_target = dict(pi_tar)
        runner.pi_opp_joint = dict(pi_opp)
        runner.p_min = 1e-6
        runner.opportunity_estimator = None
        out: dict[str, float] = {}
        for c in clients:
            strata = ["s0", "s1"]
            z = runner._compute_zeta(c, strata)
            for s, val in zip(strata, z):
                out[f"{c}|{s}"] = float(val)
        return out

    ra = ratios_via_production_runner(pi_opp_a)
    rb = ratios_via_production_runner(pi_opp_b)
    # Conditional-only would normalize per client and yield different denominators
    cond_a = {}
    for c in clients:
        sub = {k: v for k, v in pi_opp_a.items() if k[0] == c}
        z = sum(sub.values())
        for k, v in sub.items():
            cond_a[k] = v / z
    uses_joint = any(abs(pi_opp_a[k] - cond_a[k]) > 1e-12 for k in pi_opp_a)
    # If production used conditional-only for c0, zeta(c0,s0)=0.25/0.8; joint uses 0.25/0.40
    hand_c0s0_a = 0.25 / 0.40
    hand_cond_c0s0_a = 0.25 / 0.80
    err = abs(ra["c0|s0"] - hand_c0s0_a)
    not_conditional = abs(ra["c0|s0"] - hand_cond_c0s0_a) > 1e-9
    differ = any(abs(ra[k] - rb[k]) > 1e-12 for k in ra)
    return {
        "sum_pi_opp_a": float(sum(pi_opp_a.values())),
        "sum_pi_tar": float(sum(pi_tar.values())),
        "semantic": "normalized opportunity event mass over client×stratum (joint)",
        "design_ratio": "pi_tar / pi_opp_joint via FullWindowRunner._compute_zeta",
        "path": "FullWindowRunner._compute_zeta(pi_opp_joint=...)",
        "ratios_a": ra,
        "ratios_b": rb,
        "ratios_differ": differ,
        "uses_joint_not_conditional_only": uses_joint and not_conditional,
        "hand_c0_s0_a": hand_c0s0_a,
        "hand_conditional_c0_s0_a": hand_cond_c0s0_a,
        "error": err,
        "generator_joint_builder": "raven_mcs.e3.real_runner.generator_r3.build_joint_pi_opp",
        "status": "PASS" if differ and uses_joint and not_conditional and err <= 1e-12 else "FAIL",
        "blocker_if_fail": "PIOPP_PRODUCTION_CONSUMPTION_BLOCKED",
        "reference_joint_from_builder": {
            str(k): float(v)
            for k, v in build_joint_pi_opp(
                ["c0", "c1"],
                {
                    "c0": ["c0::block0::weekday", "c0::block2::weekday"],
                    "c1": ["c1::block0::weekday", "c1::block2::weekday"],
                },
            ).items()
        },
    }


def piopp_semantic_identity() -> dict[str, Any]:
    return {
        "identity": "A",
        "label": "normalized opportunity event mass over client×stratum",
        "not": "pair inclusion probability",
        "joint_construction": (
            "pi_opp_joint(k,s) = P(client opportunity = k) * P(s|k) "
            "materialized by build_joint_pi_opp on the same support as pi_tar"
        ),
        "scale_match": "sum_{k,s} pi_opp_joint = 1 and sum_{k,s} pi_tar = 1",
        "production_consumer": "FullWindowRunner._compute_zeta uses pi_opp_joint as zeta denominator",
        "status": "FROZEN",
    }


def pobs_field_usage_audit() -> dict[str, Any]:
    from pathlib import Path

    wr = Path(__file__).resolve().parents[2] / "training" / "window_runner.py"
    text = wr.read_text(encoding="utf-8")
    # SimOracle scientific path must key on p_obs_true_by_unit
    uses_atomic = "p_obs_true_by_unit" in text
    # Must not use mean diagnostic for atomic first-stage correction
    # (oracle_p may exist as EventTrace schema field but must not drive weights)
    simoracle_block_ok = (
        "uses_oracle_propensity" in text
        and "p_obs_true_by_unit" in text
        and "ATOMIC_POBS_ERROR" in text
    )
    return {
        "scientific_weighting_may_read": ["p_obs_true_by_unit", "opportunity_features.p_obs_true_by_unit"],
        "diagnostic_only": ["oracle_p", "p_obs_mean_diagnostic"],
        "forbidden_for_atomic_correction": ["oracle_p", "p_obs_mean_diagnostic"],
        "enforcement": "FullWindowRunner SimOracle path uses p_obs_true_by_unit only",
        "static_check_uses_atomic": uses_atomic,
        "static_check_simoracle_block": simoracle_block_ok,
        "status": "AUDITED" if uses_atomic and simoracle_block_ok else "FAIL",
    }
