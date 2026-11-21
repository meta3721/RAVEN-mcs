"""Frozen client-stratum target mass for the first-stage design ratio."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from raven_mcs.data.target import GroupMapper, TargetBuilder
from raven_mcs.utils.hashing import sha256_file


def build_pi_target(
    atomic: pd.DataFrame,
    station_to_client: dict[str, str],
    *,
    split: str = "test",
) -> pd.DataFrame:
    """Build pi_tar(k,s) = Lambda_s^tar · lambda_{k|s}^tar.

    When each stratum maps to a unique client (SensorScope/U-Air station-level s),
    lambda_{k|s}=1 and pi_tar(k,s)=Lambda_s.

    When multiple clients share a stratum (Traffic 4-region s), lambda_{k|s} is the
    within-stratum client mass share on the frozen TEST support.
    """
    target = TargetBuilder(
        group_mapper=GroupMapper("target_group_main"),
    ).build(atomic, split=split)
    selected = atomic.loc[
        atomic["unit_id"].astype(str).isin(target.atom_mass.index),
        ["unit_id", "spatial_id", "opportunity_stratum"],
    ].copy()
    selected["unit_id"] = selected["unit_id"].astype(str)
    selected["opportunity_stratum"] = selected["opportunity_stratum"].astype(str)
    selected["target_mass"] = selected["unit_id"].map(target.atom_mass)

    mapping = {str(station): str(client) for station, client in station_to_client.items()}
    selected["client_id"] = selected["spatial_id"].astype(str).map(mapping)
    if selected["client_id"].isna().any():
        raise ValueError("positive target station lacks frozen client mapping")

    lambda_s = selected.groupby("opportunity_stratum")["target_mass"].sum()
    mass_ks = (
        selected.groupby(["client_id", "opportunity_stratum"])["target_mass"].sum().reset_index()
    )
    mass_ks = mass_ks.rename(columns={"target_mass": "mass_ks"})

    all_units = atomic[["spatial_id", "opportunity_stratum"]].copy()
    all_units["opportunity_stratum"] = all_units["opportunity_stratum"].astype(str)
    all_units["client_id"] = all_units["spatial_id"].astype(str).map(mapping)
    if all_units["client_id"].isna().any():
        raise ValueError("atomic station lacks frozen client mapping")
    support = all_units[["client_id", "opportunity_stratum"]].drop_duplicates()
    support = support.merge(mass_ks, on=["client_id", "opportunity_stratum"], how="left")
    support["mass_ks"] = support["mass_ks"].fillna(0.0)
    support["Lambda_s_tar"] = support["opportunity_stratum"].map(lambda_s).fillna(0.0)
    # lambda_{k|s} = mass_ks / Lambda_s when Lambda_s>0; else 0
    support["lambda_k_given_s_tar"] = 0.0
    pos = support["Lambda_s_tar"] > 0
    support.loc[pos, "lambda_k_given_s_tar"] = (
        support.loc[pos, "mass_ks"] / support.loc[pos, "Lambda_s_tar"]
    )
    support["pi_k_s_tar"] = support["Lambda_s_tar"] * support["lambda_k_given_s_tar"]
    support["support_flag"] = True
    support = support.drop(columns=["mass_ks"])
    support = support.sort_values(["client_id", "opportunity_stratum"]).reset_index(drop=True)

    # Unique-client strata still get lambda=1 when that client owns all mass
    if abs(float(support["pi_k_s_tar"].sum()) - 1.0) > 1e-12:
        raise ValueError(
            f"pi target does not sum to one (sum={float(support['pi_k_s_tar'].sum())})"
        )
    if bool((support["pi_k_s_tar"] < 0).any()):
        raise ValueError("pi target must be nonnegative")
    return support


def build_pi_target_support_compatible(
    atomic: pd.DataFrame,
    station_to_client: dict[str, str],
    *,
    split: str = "test",
    pi_opp_joint: dict[tuple[str, str], float],
) -> pd.DataFrame:
    """Equal mixture of the support-projected test target and frozen π^opp.

    Pre-registered G1 Path A construction (not tuned):

        π^{test,feas} = Π_{S_feas}(π^{test}),
        π^{sc} = (π^{test,feas} + π^{opp}) / 2,

    where S_feas is the frozen TRAIN client×stratum support.  Every feasible
    pair with π^opp>0 receives strictly positive mass, so train-only strata
    cannot zero a client out of E_r.  Evaluation μ stays the public test
    artifact; only the Design-ratio numerator changes.
    """
    if not pi_opp_joint:
        raise ValueError("support-compatible target requires frozen joint pi_opp")
    test = build_pi_target(atomic, station_to_client, split=split)
    out = test.copy()
    feas = set(pi_opp_joint)
    test_on_feas = []
    opp_aligned = []
    for row in out.itertuples(index=False):
        key = (str(row.client_id), str(row.opportunity_stratum))
        test_mass = float(row.pi_k_s_tar) if key in feas else 0.0
        test_on_feas.append(test_mass)
        opp_aligned.append(float(pi_opp_joint.get(key, 0.0)))
    test_on_feas_arr = pd.Series(test_on_feas, index=out.index, dtype="float64")
    opp_arr = pd.Series(opp_aligned, index=out.index, dtype="float64")
    z_test = float(test_on_feas_arr.sum())
    z_opp = float(opp_arr.sum())
    if z_test <= 0.0 or z_opp <= 0.0:
        raise ValueError("support-compatible target requires positive test-on-feas and opp mass")
    test_feas = test_on_feas_arr / z_test
    opp_norm = opp_arr / z_opp
    out["pi_k_s_tar_test"] = out["pi_k_s_tar"]
    out["pi_k_s_tar"] = 0.5 * test_feas + 0.5 * opp_norm
    out["Lambda_s_tar"] = out.groupby("opportunity_stratum")["pi_k_s_tar"].transform("sum")
    pos = out["Lambda_s_tar"] > 0
    out["lambda_k_given_s_tar"] = 0.0
    out.loc[pos, "lambda_k_given_s_tar"] = (
        out.loc[pos, "pi_k_s_tar"] / out.loc[pos, "Lambda_s_tar"]
    )
    if abs(float(out["pi_k_s_tar"].sum()) - 1.0) > 1e-12:
        raise ValueError(
            f"support-compatible pi target does not sum to one (sum={float(out['pi_k_s_tar'].sum())})"
        )
    if bool((out["pi_k_s_tar"] < 0).any()):
        raise ValueError("support-compatible pi target must be nonnegative")
    return out


def load_pi_target(path: Path) -> tuple[dict[tuple[str, str], float], str]:
    frame = pd.read_parquet(path)
    required = {"client_id", "opportunity_stratum", "pi_k_s_tar", "support_flag"}
    if not required.issubset(frame.columns):
        raise ValueError(f"pi target missing columns: {sorted(required - set(frame))}")
    if abs(float(frame["pi_k_s_tar"].sum()) - 1.0) > 1e-12:
        raise ValueError("frozen pi target does not sum to one")
    values = {
        (str(row.client_id), str(row.opportunity_stratum)): float(row.pi_k_s_tar)
        for row in frame.itertuples()
    }
    return values, sha256_file(path)
