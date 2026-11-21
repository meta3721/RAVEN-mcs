"""Single frozen atomic deployment law ϖ^{tar} for paper μ and Gate π^{tar}.

R1c: μ and π^{tar} must come from one train-split public atomic law.
Does not change E3 production_target_bundle or paper h(i) maps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np
import pandas as pd

from raven_mcs.sag.deployment_groups import GROUP_LABELS, N_H_GROUPS
from raven_mcs.utils.hashing import sha256_json

PI_SAFE_RULE_V1 = {
    "rule_id": "PI_SAFE_RULE_V1",
    "quantile": 0.10,
    "data_source": "public_pi_opp_joint_on_target_positive_pairs",
    "fit_scope": "frozen public opportunity law × {pi_tar>0}",
    "excludes": [
        "labels",
        "test_outcomes",
        "test_prediction_residuals",
        "current_window_events",
        "gate_ON_OFF",
    ],
}

COMPAT_ATOL = 1e-10
COMPAT_ATOL_RELAXED = 1e-8


@dataclass
class FrozenAtomicTargetLaw:
    dataset: str
    split: str
    varpi: dict[str, float]
    mu: np.ndarray
    pi_target: dict[tuple[str, str], float]
    share_ks_g: dict[tuple[str, str], np.ndarray]
    n_atoms: int
    n_pos_pairs: int
    construction: str
    uses_labels: bool = False
    uses_test_outcomes: bool = False
    uses_test_split_mass: bool = False
    uses_test_public_metadata: bool = False
    rule_id: str = ""
    compatibility: dict[str, Any] = field(default_factory=dict)
    law_hash: str = ""

    def as_public_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "split": self.split,
            "n_atoms": self.n_atoms,
            "n_pos_pairs": self.n_pos_pairs,
            "construction": self.construction,
            "uses_labels": self.uses_labels,
            "uses_test_outcomes": self.uses_test_outcomes,
            "uses_test_split_mass": self.uses_test_split_mass,
            "uses_test_public_metadata": self.uses_test_public_metadata,
            "rule_id": self.rule_id,
            "mu": [float(x) for x in self.mu.tolist()],
            "law_hash": self.law_hash,
            "compatibility": self.compatibility,
        }


def _supported_train(atomic: pd.DataFrame) -> pd.DataFrame:
    if "unit_id" not in atomic.columns or "split" not in atomic.columns:
        raise ValueError("atomic table must contain unit_id and split")
    if "support_flag" not in atomic.columns:
        raise ValueError("atomic table must contain support_flag")
    selected = atomic.loc[atomic["split"].astype(str) == "train"].copy()
    if selected.empty:
        raise ValueError("no train-split atomic units")
    supported = selected.loc[selected["support_flag"].astype(bool)].copy()
    if supported.empty:
        raise ValueError("no supported train-split atomic units")
    return supported


def build_frozen_atomic_target_law(
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    unit_to_h: Mapping[str, int],
    *,
    dataset: str,
) -> FrozenAtomicTargetLaw:
    """Uniform ϖ on train+supported atoms; derive μ and π_{k,s} from the same law."""
    supported = _supported_train(atomic)
    unit_ids = supported["unit_id"].astype(str).tolist()
    n = len(unit_ids)
    mass = 1.0 / float(n)
    varpi = {uid: mass for uid in unit_ids}

    mapping = {str(k): str(v) for k, v in spatial_to_client.items()}
    h_map = {str(k): int(v) for k, v in unit_to_h.items()}

    mu = np.zeros(N_H_GROUPS, dtype=np.float64)
    pi: dict[tuple[str, str], float] = {}
    pair_h_mass: dict[tuple[str, str], np.ndarray] = {}

    required = ("spatial_id", "opportunity_stratum")
    missing = [c for c in required if c not in supported.columns]
    if missing:
        raise ValueError(f"atomic table missing {missing}")

    for row in supported.itertuples(index=False):
        uid = str(row.unit_id)
        if uid not in h_map:
            raise ValueError(f"train unit {uid} missing from frozen paper h(i) map")
        g = int(h_map[uid])
        if g < 0 or g >= N_H_GROUPS:
            raise ValueError(f"h(i) out of range for unit {uid}: {g}")
        w = float(varpi[uid])
        mu[g] += w
        client = mapping.get(str(row.spatial_id))
        if client is None:
            raise ValueError(f"train spatial_id {row.spatial_id} lacks frozen client map")
        key = (str(client), str(row.opportunity_stratum))
        pi[key] = pi.get(key, 0.0) + w
        if key not in pair_h_mass:
            pair_h_mass[key] = np.zeros(N_H_GROUPS, dtype=np.float64)
        pair_h_mass[key][g] += w

    # Zero-mass support pairs from public deployment metadata (all splits).
    all_units = atomic[["spatial_id", "opportunity_stratum"]].copy()
    all_units["opportunity_stratum"] = all_units["opportunity_stratum"].astype(str)
    all_units["client_id"] = all_units["spatial_id"].astype(str).map(mapping)
    if all_units["client_id"].isna().any():
        raise ValueError("atomic spatial_id lacks frozen client mapping")
    for row in all_units[["client_id", "opportunity_stratum"]].drop_duplicates().itertuples(index=False):
        key = (str(row.client_id), str(row.opportunity_stratum))
        pi.setdefault(key, 0.0)
        pair_h_mass.setdefault(key, np.zeros(N_H_GROUPS, dtype=np.float64))

    share_ks_g: dict[tuple[str, str], np.ndarray] = {}
    for key, hmass in pair_h_mass.items():
        tot = float(hmass.sum())
        share_ks_g[key] = (hmass / tot) if tot > 0 else np.zeros(N_H_GROUPS, dtype=np.float64)

    mu_from_pi = np.zeros(N_H_GROUPS, dtype=np.float64)
    for key, mass_ks in pi.items():
        mu_from_pi += float(mass_ks) * share_ks_g[key]

    sum_varpi = float(sum(varpi.values()))
    sum_pi = float(sum(pi.values()))
    mu_err = float(np.max(np.abs(mu - np.asarray([sum(w for u, w in varpi.items() if h_map[u] == g) for g in range(N_H_GROUPS)]))))
    bridge_err = float(np.max(np.abs(mu - mu_from_pi)))
    max_abs = max(
        abs(sum_varpi - 1.0),
        abs(sum_pi - 1.0),
        abs(float(mu.sum()) - 1.0),
        mu_err,
        bridge_err,
    )
    passed = max_abs <= COMPAT_ATOL
    relaxed = (not passed) and max_abs <= COMPAT_ATOL_RELAXED
    compatibility = {
        "sum_varpi": sum_varpi,
        "sum_pi": sum_pi,
        "sum_mu": float(mu.sum()),
        "mu_marginal_max_abs": mu_err,
        "group_bridge_max_abs": bridge_err,
        "max_abs_error": max_abs,
        "atol": COMPAT_ATOL,
        "passed": bool(passed or relaxed),
        "used_relaxed_atol": bool(relaxed),
        "status": (
            "PASS"
            if passed
            else ("PASS_RELAXED_1e-8" if relaxed else "TARGET_COMPATIBILITY_NOT_CLOSED")
        ),
    }
    law_hash = sha256_json(
        {
            "dataset": str(dataset).lower(),
            "split": "train",
            "varpi": varpi,
            "mu": mu.tolist(),
            "pi": {f"{k}|{s}": v for (k, s), v in sorted(pi.items())},
        }
    )
    return FrozenAtomicTargetLaw(
        dataset=str(dataset).lower(),
        split="train",
        varpi=varpi,
        mu=mu,
        pi_target=pi,
        share_ks_g=share_ks_g,
        n_atoms=n,
        n_pos_pairs=sum(1 for v in pi.values() if v > 0.0),
        construction="train_split_supported_atomic_uniform_then_xi_and_h_marginal",
        compatibility=compatibility,
        law_hash=law_hash,
    )


def compatibility_rows(law: FrozenAtomicTargetLaw) -> list[dict[str, Any]]:
    rows = [
        {
            "check": "sum_varpi",
            "expected": 1.0,
            "observed": law.compatibility["sum_varpi"],
            "abs_error": abs(law.compatibility["sum_varpi"] - 1.0),
        },
        {
            "check": "sum_pi",
            "expected": 1.0,
            "observed": law.compatibility["sum_pi"],
            "abs_error": abs(law.compatibility["sum_pi"] - 1.0),
        },
        {
            "check": "sum_mu",
            "expected": 1.0,
            "observed": law.compatibility["sum_mu"],
            "abs_error": abs(law.compatibility["sum_mu"] - 1.0),
        },
        {
            "check": "mu_marginal",
            "expected": 0.0,
            "observed": law.compatibility["mu_marginal_max_abs"],
            "abs_error": law.compatibility["mu_marginal_max_abs"],
        },
        {
            "check": "group_bridge",
            "expected": 0.0,
            "observed": law.compatibility["group_bridge_max_abs"],
            "abs_error": law.compatibility["group_bridge_max_abs"],
        },
    ]
    for row in rows:
        row["dataset"] = law.dataset
        row["atol"] = COMPAT_ATOL
        row["pass"] = int(float(row["abs_error"]) <= COMPAT_ATOL)
        row["status"] = law.compatibility["status"]
    return rows


def atomic_law_rows(
    law: FrozenAtomicTargetLaw,
    unit_to_h: Mapping[str, int] | None = None,
) -> list[dict[str, Any]]:
    h_map = {str(k): int(v) for k, v in (unit_to_h or {}).items()}
    return [
        {
            "dataset": law.dataset,
            "unit_id": uid,
            "varpi_tar": mass,
            "h": h_map.get(str(uid)),
        }
        for uid, mass in sorted(law.varpi.items())
    ]


def pi_safe_rule_hash() -> str:
    return sha256_json(PI_SAFE_RULE_V1)


def freeze_pi_safe_rule_v1(
    *,
    value_sensorscope: float,
    value_uair: float,
    n_pos_sensorscope: int | None = None,
    n_pos_uair: int | None = None,
) -> dict[str, Any]:
    payload = {
        **PI_SAFE_RULE_V1,
        "value_SensorScope": float(value_sensorscope),
        "value_UAir": float(value_uair),
        "n_positive_target_pairs_SensorScope": n_pos_sensorscope,
        "n_positive_target_pairs_UAir": n_pos_uair,
        "hash": pi_safe_rule_hash(),
        "frozen": True,
        "status": "FROZEN_DEVELOPMENT_PROTOCOL",
        "note": "Rule frozen; environment-specific values follow the same q10 protocol.",
    }
    return payload


TARGET_LAW_RULE_V1 = {
    "rule_id": "TARGET_LAW_RULE_V1",
    "scientific_population": "public_evaluation_deployment_supported_atoms",
    "atomic_support": "test_split AND support_flag, public covariates only",
    "atomic_mass_construction": (
        "mu_g from train-split TOD occupancy; "
        "varpi_i = mu_h(i) / n_{I_dep, h(i)} on I_dep"
    ),
    "group_mass_source": "train_split_supported_atomic_uniform_then_h_marginal",
    "allowed_metadata": [
        "unit_id",
        "split",
        "support_flag",
        "spatial_id",
        "absolute_time",
        "opportunity_stratum",
        "frozen_client_map",
        "frozen_h_map",
    ],
    "forbidden_outcome_information": [
        "labels",
        "test_Y",
        "test_predictions",
        "test_residuals",
        "RMSE",
        "Delta_group",
        "gate_ON_OFF",
        "current_window_R_O_U",
    ],
    "train_val_test_relation": (
        "mu_g frozen on train public support; "
        "I_dep is test public support; val unused"
    ),
}


def target_law_rule_hash() -> str:
    return sha256_json(TARGET_LAW_RULE_V1)


def freeze_target_law_rule_v1() -> dict[str, Any]:
    return {
        **TARGET_LAW_RULE_V1,
        "hash": target_law_rule_hash(),
        "frozen": True,
        "status": "FROZEN",
    }


def _supported_split(atomic: pd.DataFrame, split: str) -> pd.DataFrame:
    if "unit_id" not in atomic.columns or "split" not in atomic.columns:
        raise ValueError("atomic table must contain unit_id and split")
    if "support_flag" not in atomic.columns:
        raise ValueError("atomic table must contain support_flag")
    selected = atomic.loc[atomic["split"].astype(str) == str(split)].copy()
    if selected.empty:
        raise ValueError(f"no {split}-split atomic units")
    supported = selected.loc[selected["support_flag"].astype(bool)].copy()
    if supported.empty:
        raise ValueError(f"no supported {split}-split atomic units")
    return supported


def _assemble_law(
    *,
    atomic: pd.DataFrame,
    mapping: dict[str, str],
    h_map: dict[str, int],
    varpi: dict[str, float],
    mu: np.ndarray,
    dataset: str,
    split: str,
    construction: str,
    uses_test_public_metadata: bool,
    rule_id: str,
) -> FrozenAtomicTargetLaw:
    pi: dict[tuple[str, str], float] = {}
    pair_h_mass: dict[tuple[str, str], np.ndarray] = {}
    atoms = atomic.loc[atomic["unit_id"].astype(str).isin(list(varpi))].copy()
    required = ("spatial_id", "opportunity_stratum")
    missing = [c for c in required if c not in atoms.columns]
    if missing:
        raise ValueError(f"atomic table missing {missing}")
    for row in atoms.itertuples(index=False):
        uid = str(row.unit_id)
        w = float(varpi.get(uid, 0.0))
        if w <= 0.0:
            continue
        if uid not in h_map:
            raise ValueError(f"unit {uid} missing from frozen paper h(i) map")
        g = int(h_map[uid])
        client = mapping.get(str(row.spatial_id))
        if client is None:
            raise ValueError(f"spatial_id {row.spatial_id} lacks frozen client map")
        key = (str(client), str(row.opportunity_stratum))
        pi[key] = pi.get(key, 0.0) + w
        if key not in pair_h_mass:
            pair_h_mass[key] = np.zeros(N_H_GROUPS, dtype=np.float64)
        pair_h_mass[key][g] += w
    all_units = atomic[["spatial_id", "opportunity_stratum"]].copy()
    all_units["opportunity_stratum"] = all_units["opportunity_stratum"].astype(str)
    all_units["client_id"] = all_units["spatial_id"].astype(str).map(mapping)
    if all_units["client_id"].isna().any():
        raise ValueError("atomic spatial_id lacks frozen client mapping")
    for row in all_units[["client_id", "opportunity_stratum"]].drop_duplicates().itertuples(index=False):
        key = (str(row.client_id), str(row.opportunity_stratum))
        pi.setdefault(key, 0.0)
        pair_h_mass.setdefault(key, np.zeros(N_H_GROUPS, dtype=np.float64))
    share_ks_g: dict[tuple[str, str], np.ndarray] = {}
    for key, hmass in pair_h_mass.items():
        tot = float(hmass.sum())
        share_ks_g[key] = (hmass / tot) if tot > 0 else np.zeros(N_H_GROUPS, dtype=np.float64)
    mu_from_varpi = np.zeros(N_H_GROUPS, dtype=np.float64)
    for uid, w in varpi.items():
        mu_from_varpi[int(h_map[str(uid)])] += float(w)
    mu_from_pi = np.zeros(N_H_GROUPS, dtype=np.float64)
    for key, mass_ks in pi.items():
        mu_from_pi += float(mass_ks) * share_ks_g[key]
    sum_varpi = float(sum(varpi.values()))
    sum_pi = float(sum(pi.values()))
    mu_err = float(np.max(np.abs(mu - mu_from_varpi)))
    bridge_err = float(np.max(np.abs(mu - mu_from_pi)))
    max_abs = max(
        abs(sum_varpi - 1.0),
        abs(sum_pi - 1.0),
        abs(float(mu.sum()) - 1.0),
        mu_err,
        bridge_err,
    )
    passed = max_abs <= COMPAT_ATOL
    relaxed = (not passed) and max_abs <= COMPAT_ATOL_RELAXED
    compatibility = {
        "sum_varpi": sum_varpi,
        "sum_pi": sum_pi,
        "sum_mu": float(mu.sum()),
        "mu_marginal_max_abs": mu_err,
        "group_bridge_max_abs": bridge_err,
        "max_abs_error": max_abs,
        "atol": COMPAT_ATOL,
        "passed": bool(passed or relaxed),
        "used_relaxed_atol": bool(relaxed),
        "status": (
            "PASS"
            if passed
            else ("PASS_RELAXED_1e-8" if relaxed else "TARGET_COMPATIBILITY_NOT_CLOSED")
        ),
    }
    law_hash = sha256_json(
        {
            "rule_id": rule_id,
            "dataset": str(dataset).lower(),
            "split": split,
            "varpi": varpi,
            "mu": mu.tolist(),
            "pi": {f"{k}|{s}": v for (k, s), v in sorted(pi.items())},
        }
    )
    return FrozenAtomicTargetLaw(
        dataset=str(dataset).lower(),
        split=split,
        varpi=varpi,
        mu=mu,
        pi_target=pi,
        share_ks_g=share_ks_g,
        n_atoms=sum(1 for w in varpi.values() if w > 0.0),
        n_pos_pairs=sum(1 for v in pi.values() if v > 0.0),
        construction=construction,
        uses_test_public_metadata=uses_test_public_metadata,
        rule_id=rule_id,
        compatibility=compatibility,
        law_hash=law_hash,
    )


def build_target_law_v1(
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    unit_to_h: Mapping[str, int],
    *,
    dataset: str,
) -> FrozenAtomicTargetLaw:
    """TARGET_LAW_RULE_V1: train-frozen μ_g, atomic ϖ on test public support."""
    train = _supported_split(atomic, "train")
    dep = _supported_split(atomic, "test")
    mapping = {str(k): str(v) for k, v in spatial_to_client.items()}
    h_map = {str(k): int(v) for k, v in unit_to_h.items()}
    mu = np.zeros(N_H_GROUPS, dtype=np.float64)
    for uid in train["unit_id"].astype(str).tolist():
        if uid not in h_map:
            raise ValueError(f"train unit {uid} missing from frozen paper h(i) map")
        mu[int(h_map[uid])] += 1.0
    if float(mu.sum()) <= 0:
        raise ValueError("train-split mu sums to 0")
    mu = mu / float(mu.sum())
    n_by_g = np.zeros(N_H_GROUPS, dtype=np.int64)
    dep_h: dict[str, int] = {}
    for uid in dep["unit_id"].astype(str).tolist():
        if uid not in h_map:
            raise ValueError(f"test unit {uid} missing from frozen paper h(i) map")
        g = int(h_map[uid])
        dep_h[uid] = g
        n_by_g[g] += 1
    for g in range(N_H_GROUPS):
        if mu[g] > 0 and int(n_by_g[g]) == 0:
            raise ValueError(f"I_dep has no atoms in group {g} with positive mu")
    varpi = {
        uid: (float(mu[g]) / float(n_by_g[g]) if n_by_g[g] > 0 else 0.0)
        for uid, g in dep_h.items()
    }
    return _assemble_law(
        atomic=atomic,
        mapping=mapping,
        h_map=h_map,
        varpi=varpi,
        mu=mu,
        dataset=dataset,
        split="test",
        construction="train_mu_g_then_group_uniform_on_test_I_dep",
        uses_test_public_metadata=True,
        rule_id="TARGET_LAW_RULE_V1",
    )


def compare_target_laws(
    old: FrozenAtomicTargetLaw,
    new: FrozenAtomicTargetLaw,
    pi_opp_joint: Mapping[tuple[str, str], float] | None = None,
) -> dict[str, Any]:
    """Semantic comparison only. Not a performance selector."""
    units = sorted(set(old.varpi) | set(new.varpi))
    tv_atom = 0.5 * float(
        sum(abs(float(old.varpi.get(u, 0.0)) - float(new.varpi.get(u, 0.0))) for u in units)
    )
    overlap_atom = float(
        sum(min(float(old.varpi.get(u, 0.0)), float(new.varpi.get(u, 0.0))) for u in units)
    )
    pairs = sorted(set(old.pi_target) | set(new.pi_target))
    tv_pi = 0.5 * float(
        sum(abs(float(old.pi_target.get(k, 0.0)) - float(new.pi_target.get(k, 0.0))) for k in pairs)
    )
    overlap_pi = float(
        sum(min(float(old.pi_target.get(k, 0.0)), float(new.pi_target.get(k, 0.0))) for k in pairs)
    )
    old_pos = {k for k, w in old.pi_target.items() if w > 0.0}
    new_pos = {k for k, w in new.pi_target.items() if w > 0.0}
    opp = set(pi_opp_joint or {})
    return {
        "dataset": new.dataset,
        "support_size_r1c": old.n_atoms,
        "support_size_r1d": new.n_atoms,
        "mass_overlap_atom": overlap_atom,
        "tv_atom": tv_atom,
        "target_zero_mass_r1d_on_r1c_support": float(
            sum(old.varpi.get(u, 0.0) for u in old.varpi if new.varpi.get(u, 0.0) <= 0.0)
        ),
        "train_support_overlap_atoms": float(overlap_atom),
        "tv_pi": tv_pi,
        "mass_overlap_pi": overlap_pi,
        "n_pos_pairs_r1c": old.n_pos_pairs,
        "n_pos_pairs_r1d": new.n_pos_pairs,
        "opportunity_support_overlap": (
            float(sum(new.pi_target.get(k, 0.0) for k in new_pos if k in opp))
            if opp
            else float("nan")
        ),
        "pi_pos_jaccard": (
            len(old_pos & new_pos) / len(old_pos | new_pos) if (old_pos | new_pos) else float("nan")
        ),
    }
