"""Atomic arrival-risk rho_i^arr for scientific RMSE_rho (not group-marginal)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from raven_mcs.e3.target_pair.errors import RhoWeightError
from raven_mcs.metrics.accuracy import atomic_arrival_weights, rmse_mu, rmse_rho
from raven_mcs.utils.hashing import sha256_json


class AtomicRhoError(RuntimeError):
    CODE = "ATOMIC_RHO_ERROR"


def atomic_rho_schema_v2() -> dict[str, Any]:
    return {
        "schema_version": "E3_ATOMIC_RHO_SCHEMA_V2",
        "formula": {
            "r_hat_i": "sum_k pi_opp_hat(k,s(i)) * nu_hat_k[i|s(i)] * p_obs_hat(k,i) * q_use_hat(k,s(i))",
            "rho_i_arr": "r_hat_i / sum_j r_hat_j",
            "RMSE_rho": "sqrt(sum_i rho_i_arr (y_hat_i - y_i)^2)",
        },
        "forbidden": [
            "delivered group counts only",
            "arrival group counts only",
            "target-group marginals",
            "uniform-within-group redistribution (rho_g/n_g)",
        ],
        "required_fields": [
            "atomic_unit_id",
            "spatial_unit",
            "timestamp",
            "opportunity_stratum_id",
            "raw_arrival_score",
            "rho_atomic",
            "contributing_client_count",
            "pi_opp_component_summary",
            "nu_component_summary",
            "p_obs_component_summary",
            "q_component_summary",
            "support_mask",
            "normalization_denominator",
            "source_hashes",
        ],
    }


def factor_registry() -> dict[str, Any]:
    return {
        "schema_version": "E3_ATOMIC_RHO_FACTOR_REGISTRY",
        "factors": {
            "pi_opp_hat_k_s": {
                "meaning": "joint opportunity event mass over client×stratum",
                "production_source": "pi_opp_joint from build_joint_pi_opp / runner.pi_opp_joint",
                "scale": "sum_{k,s}=1",
            },
            "nu_hat_k_i_given_s": {
                "meaning": "within-stratum atomic allocation of target mass",
                "production_source": "atom_mass_i / Lambda_s on TEST support (uniform atoms → 1/n_s)",
                "frozen_ref": "e1_entry._arrival_weights nu construction",
            },
            "p_obs_hat_k_i": {
                "meaning": "atomic observation probability",
                "simoracle": "EventTrace opportunity_features.p_obs_true_by_unit / atomic_p_obs_true",
                "non_oracle": "obs_propensity.predict when runner available; else EventTrace controlled truth for Complete-aligned eval",
                "forbidden": "mean oracle_p substitution for atomic correction",
            },
            "q_use_hat_k_s": {
                "meaning": "usable probability at client×stratum",
                "simoracle": "EventTrace opportunity_features.q_use_true",
                "non_oracle": "usable_propensity.predict when runner available; else EventTrace controlled truth",
            },
        },
        "status": "FROZEN",
    }


def _extract_p_obs_map(events: pd.DataFrame) -> dict[str, float]:
    """Collect atomic p_obs from EventTrace opportunity_features."""
    out: dict[str, list[float]] = {}
    for _, row in events.iterrows():
        feats = row.get("opportunity_features") or {}
        if isinstance(feats, str):
            import json

            feats = json.loads(feats)
        by_unit = feats.get("p_obs_true_by_unit") or {}
        for uid, p in by_unit.items():
            out.setdefault(str(uid), []).append(float(p))
    return {u: float(np.mean(vs)) for u, vs in out.items()}


def _extract_q_by_client_stratum(events: pd.DataFrame) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], list[float]] = {}
    for _, row in events.iterrows():
        feats = row.get("opportunity_features") or {}
        if isinstance(feats, str):
            import json

            feats = json.loads(feats)
        cid = str(row["client_id"])
        s = str(feats.get("opportunity_stratum") or "")
        q = feats.get("q_use_true")
        if q is None:
            q = row.get("oracle_q")
        if q is None or not s:
            continue
        out.setdefault((cid, s), []).append(float(q))
    return {k: float(np.mean(vs)) for k, vs in out.items()}


def build_atomic_arrival_rho(
    *,
    test_unit_ids: list[str],
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    pi_opp_joint: Mapping[tuple[str, str], float],
    events: pd.DataFrame,
    p_obs_by_unit: Mapping[str, float] | None = None,
    q_by_client_stratum: Mapping[tuple[str, str], float] | None = None,
    support_flags: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Canonical atomic rho_i^arr builder for E3 scientific RMSE_rho."""
    if not test_unit_ids:
        raise AtomicRhoError("ATOMIC_RHO_ERROR: empty test units")
    meta = atomic.set_index("unit_id")
    clients = sorted(set(str(c) for c in spatial_to_client.values()))
    n_u = len(test_unit_ids)
    n_c = len(clients)
    if n_c == 0:
        raise AtomicRhoError("ATOMIC_RHO_ERROR: no clients")

    # Target atom masses (uniform on TEST support) for nu
    test_mask = atomic["split"].astype(str) == "test"
    test_atoms = atomic.loc[test_mask & atomic["support_flag"].astype(bool)]
    if test_atoms.empty:
        raise AtomicRhoError("ATOMIC_RHO_ERROR: empty test support")
    atom_mass = 1.0 / float(len(test_atoms))
    strata = [str(meta.loc[u, "opportunity_stratum"]) for u in test_unit_ids]
    lambda_s: dict[str, float] = {}
    for _, row in test_atoms.iterrows():
        s = str(row["opportunity_stratum"])
        lambda_s[s] = lambda_s.get(s, 0.0) + atom_mass
    nu = np.zeros(n_u, dtype=np.float64)
    for i, s in enumerate(strata):
        lam = lambda_s.get(s, 0.0)
        nu[i] = (atom_mass / lam) if lam > 0 else 0.0

    p_map = dict(p_obs_by_unit) if p_obs_by_unit is not None else _extract_p_obs_map(events)
    q_map = (
        dict(q_by_client_stratum)
        if q_by_client_stratum is not None
        else _extract_q_by_client_stratum(events)
    )
    # Default missing p/q to small positive to keep support diagnosable
    default_p = float(np.mean(list(p_map.values()))) if p_map else 0.5
    default_q = float(np.mean(list(q_map.values()))) if q_map else 0.5

    pi = np.zeros((n_c, n_u), dtype=np.float64)
    p = np.zeros_like(pi)
    q = np.zeros_like(pi)
    for ci, client in enumerate(clients):
        for ui, (uid, s) in enumerate(zip(test_unit_ids, strata)):
            # Only the owning client of the unit's spatial id contributes meaningfully;
            # other clients get 0 pi on unsupported (k,s) under unique station-client map.
            owner = spatial_to_client.get(str(meta.loc[uid, "spatial_id"]))
            if owner != client:
                pi[ci, ui] = 0.0
                p[ci, ui] = 0.0
                q[ci, ui] = 0.0
                continue
            pi[ci, ui] = float(pi_opp_joint.get((client, s), 0.0))
            p[ci, ui] = float(p_map.get(uid, default_p))
            q[ci, ui] = float(q_map.get((client, s), default_q))

    intensity, rho = atomic_arrival_weights(pi, nu, p, q)
    if support_flags is not None:
        mask = np.asarray([bool(support_flags.get(u, True)) for u in test_unit_ids])
        intensity = np.where(mask, intensity, 0.0)
        total = float(intensity.sum())
        if total <= 0:
            raise AtomicRhoError("ATOMIC_RHO_ERROR: zero intensity after support mask")
        rho = intensity / total

    if abs(float(rho.sum()) - 1.0) > 1e-12:
        raise AtomicRhoError(f"ATOMIC_RHO_ERROR: rho sum={rho.sum()}")
    if np.any(~np.isfinite(rho)) or np.any(rho < 0):
        raise AtomicRhoError("ATOMIC_RHO_ERROR: non-finite or negative rho")

    rows = []
    for i, uid in enumerate(test_unit_ids):
        row = meta.loc[uid]
        contrib_clients = int(np.sum(pi[:, i] * p[:, i] * q[:, i] > 0))
        rows.append(
            {
                "atomic_unit_id": uid,
                "spatial_unit": str(row["spatial_id"]),
                "timestamp": str(row["absolute_time"]) if "absolute_time" in row.index else None,
                "opportunity_stratum_id": strata[i],
                "target_group_h": str(row["target_group"]) if "target_group" in row.index else None,
                "raw_arrival_score": float(intensity[i]),
                "rho_atomic": float(rho[i]),
                "contributing_client_count": contrib_clients,
                "pi_opp_component_summary": float(pi[:, i].sum()),
                "nu_component_summary": float(nu[i]),
                "p_obs_component_summary": float(p[:, i].max()),
                "q_component_summary": float(q[:, i].max()),
                "support_mask": True if support_flags is None else bool(support_flags.get(uid, True)),
                "normalization_denominator": float(intensity.sum()),
            }
        )
    frame = pd.DataFrame(rows)
    return {
        "rho": rho,
        "intensity": intensity,
        "frame": frame,
        "sum_rho": float(rho.sum()),
        "n_units": n_u,
        "status": "OK",
        "builder": "build_atomic_arrival_rho",
        "scientific_path": True,
        "group_marginal_used": False,
    }


def within_group_heterogeneity_test() -> dict[str, Any]:
    """Same h(i)=h(j), different atomic factors → rho_i != rho_j."""
    rows = []
    # Two test units same target_group, different p_obs (and same stratum for simplicity)
    for uid, p, t in (("i0", 0.2, 10), ("i1", 0.8, 11)):
        rows.append(
            {
                "unit_id": uid,
                "spatial_id": "n0",
                "absolute_time": pd.Timestamp("2020-01-01", tz="UTC") + pd.Timedelta(hours=t),
                "target_group": "n0::block1",
                "opportunity_stratum": "n0::block1::weekday",
                "split": "test",
                "support_flag": True,
                "time_index": t,
            }
        )
    # need some train for completeness
    rows.append(
        {
            "unit_id": "tr0",
            "spatial_id": "n0",
            "absolute_time": pd.Timestamp("2020-01-01", tz="UTC"),
            "target_group": "n0::block0",
            "opportunity_stratum": "n0::block0::weekday",
            "split": "train",
            "support_flag": True,
            "time_index": 0,
        }
    )
    atomic = pd.DataFrame(rows)
    mapping = {"n0": "c0"}
    pi_opp = {("c0", "n0::block1::weekday"): 1.0}
    events = pd.DataFrame(
        [
            {
                "client_id": "c0",
                "opportunity_features": {
                    "opportunity_stratum": "n0::block1::weekday",
                    "p_obs_true_by_unit": {"i0": 0.2, "i1": 0.8},
                    "q_use_true": 1.0,
                },
                "oracle_q": 1.0,
            }
        ]
    )
    out = build_atomic_arrival_rho(
        test_unit_ids=["i0", "i1"],
        atomic=atomic,
        spatial_to_client=mapping,
        pi_opp_joint=pi_opp,
        events=events,
    )
    rho = out["rho"]
    # Hand: same nu (both in same stratum, 2 test units → nu=0.5 each),
    # pi=1, q=1, p=[0.2,0.8] → intensity ∝ [0.1, 0.4] → rho=[0.2, 0.8]
    hand = np.array([0.2, 0.8])
    err = float(np.max(np.abs(rho - hand)))
    return {
        "h_i": "n0::block1",
        "h_j": "n0::block1",
        "s_i": "n0::block1::weekday",
        "s_j": "n0::block1::weekday",
        "p_obs": {"i0": 0.2, "i1": 0.8},
        "nu": 0.5,
        "q": 1.0,
        "pi_opp": 1.0,
        "hand_rho": hand.tolist(),
        "production_rho": rho.tolist(),
        "error": err,
        "rho_differ": abs(float(rho[0]) - float(rho[1])) > 1e-12,
        "status": "PASS" if err <= 1e-12 and abs(float(rho[0]) - float(rho[1])) > 1e-12 else "FAIL",
    }


def analytical_atomic_rmse_rho_test() -> dict[str, Any]:
    """3 atomic units, non-uniform rho, hand RMSE_mu vs RMSE_rho."""
    rows = []
    specs = [
        ("u0", "n0", "n0::block0", "n0::block0::weekday", 0.1),
        ("u1", "n0", "n0::block0", "n0::block0::weekday", 0.2),
        ("u2", "n1", "n1::block1", "n1::block1::weekend", 0.9),
    ]
    # Build via explicit factors rather than reusing builder path for hand check
    for uid, spatial, group, stratum, _p in specs:
        rows.append(
            {
                "unit_id": uid,
                "spatial_id": spatial,
                "absolute_time": pd.Timestamp("2020-01-06", tz="UTC"),  # weekday
                "target_group": group,
                "opportunity_stratum": stratum,
                "split": "test",
                "support_flag": True,
                "time_index": 0,
            }
        )
    # fix times for weekday/weekend labels in strata — strata already set explicitly
    atomic = pd.DataFrame(rows)
    mapping = {"n0": "c0", "n1": "c1"}
    pi_opp = {
        ("c0", "n0::block0::weekday"): 0.5,
        ("c1", "n1::block1::weekend"): 0.5,
    }
    p_map = {"u0": 0.1, "u1": 0.2, "u2": 0.9}
    events = pd.DataFrame(
        [
            {
                "client_id": "c0",
                "opportunity_features": {
                    "opportunity_stratum": "n0::block0::weekday",
                    "p_obs_true_by_unit": {"u0": 0.1, "u1": 0.2},
                    "q_use_true": 1.0,
                },
            },
            {
                "client_id": "c1",
                "opportunity_features": {
                    "opportunity_stratum": "n1::block1::weekend",
                    "p_obs_true_by_unit": {"u2": 0.9},
                    "q_use_true": 1.0,
                },
            },
        ]
    )
    out = build_atomic_arrival_rho(
        test_unit_ids=["u0", "u1", "u2"],
        atomic=atomic,
        spatial_to_client=mapping,
        pi_opp_joint=pi_opp,
        events=events,
        p_obs_by_unit=p_map,
    )
    rho = out["rho"]
    # Hand intensities:
    # nu: stratum s0 has 2 units → nu=0.5; s1 has 1 → nu=1.0
    # r0 = 0.5 * 0.5 * 0.1 * 1 = 0.025
    # r1 = 0.5 * 0.5 * 0.2 * 1 = 0.05
    # r2 = 0.5 * 1.0 * 0.9 * 1 = 0.45
    # sum=0.525 → rho=[0.025,0.05,0.45]/0.525
    hand_r = np.array([0.025, 0.05, 0.45])
    hand_rho = hand_r / hand_r.sum()
    y_true = np.zeros(3)
    y_pred = np.array([1.0, 0.0, 0.0])
    mu = np.array([1 / 3, 1 / 3, 1 / 3])
    hand_rmse_rho = float(np.sqrt(np.sum(hand_rho * y_pred**2)))
    hand_rmse_mu = float(np.sqrt(np.sum(mu * y_pred**2)))
    prod_rho = float(rmse_rho(y_pred, y_true, rho))
    prod_mu = float(rmse_mu(y_pred, y_true, mu))
    w_err = float(np.max(np.abs(rho - hand_rho)))
    return {
        "hand_rho": hand_rho.tolist(),
        "production_rho": rho.tolist(),
        "weight_error": w_err,
        "hand_RMSE_rho": hand_rmse_rho,
        "production_RMSE_rho": prod_rho,
        "hand_RMSE_mu": hand_rmse_mu,
        "production_RMSE_mu": prod_mu,
        "error_rho": abs(prod_rho - hand_rmse_rho),
        "differ": abs(prod_mu - prod_rho) > 1e-12,
        "status": "PASS"
        if w_err <= 1e-12 and abs(prod_rho - hand_rmse_rho) <= 1e-12 and abs(prod_mu - prod_rho) > 1e-12
        else "FAIL",
    }


def rho_field_usage_audit() -> dict[str, Any]:
    return {
        "scientific_RMSE_rho_must_consume": "rho_atomic from build_atomic_arrival_rho",
        "diagnostic_only": [
            "group_arrival_mass_diagnostic_only",
            "build_rho_weights (rho_g/n_g)",
            "delivered_group_counts_from_events",
        ],
        "failure_if_group_marginal": "E3_RHO_USES_GROUP_MARGINAL_ERROR",
        "status": "AUDITED",
    }


# Backward-compat diagnostic rename wrappers
def group_arrival_mass_diagnostic_only(
    *,
    test_groups: list[str],
    delivered_group_counts: Mapping[str, float],
) -> np.ndarray:
    """DIAGNOSTIC ONLY — must not feed E3 scientific RMSE_rho."""
    from raven_mcs.e3.target_pair.rho_weights import build_rho_weights

    return build_rho_weights(
        test_groups=test_groups, delivered_group_counts=delivered_group_counts
    )
