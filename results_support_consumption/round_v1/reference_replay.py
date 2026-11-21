"""Reconstruct frozen Stage-1 support without training or test labels."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
ROUND_DIR = Path(__file__).resolve().parent
for entry in (str(ROUND_DIR), str(SRC)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from raven_mcs.correction.design_ratio import zeta_hat_stratum
from raven_mcs.correction.pi_target import build_pi_target
from raven_mcs.correction.stage1 import reconstruct_stage1
from raven_mcs.propensity.observation import ObservationPropensity
from raven_mcs.simulation.event_trace import load_event_trace

from protocol import (
    A_MAX,
    NUM_GROUPS,
    NUM_WINDOWS,
    P_MIN,
    PI_MIN,
    PROPENSITY_L2,
    PROPENSITY_MIN_SAMPLES,
    PROPENSITY_PRIOR,
    REGION_ORDER,
    S_MAX,
)


class GateStop(Exception):
    def __init__(self, status: str, detail: str, evidence: dict | None = None):
        super().__init__(f"{status}: {detail}")
        self.status = status
        self.detail = detail
        self.evidence = evidence or {}


@dataclass(frozen=True)
class FrozenAttempt:
    attempt_id: str
    client_id: str
    registration_window: int
    registration_time: float
    arrival_time: float
    arrival_close: int
    retry: int
    m: float
    composition: tuple[float, ...]
    group_mass: tuple[float, ...]
    raw_workload: float | None
    positive: bool


@dataclass
class BlockContext:
    name: str
    dataset: str
    mu: np.ndarray
    pi_target: dict[tuple[str, str], float]
    pi_opp: dict[tuple[str, str], float]
    units: dict[str, dict[str, str]]
    encoding: dict[str, int]
    setup_checks: dict
    confirmation: dict
    trace_root: Path


@dataclass
class ReplayResult:
    seed: int
    trace_hash: str
    attempts: list[FrozenAttempt]
    audit: dict = field(default_factory=dict)


BLOCKS = {
    "measured-O": {
        "dataset": "cityscanner_nyc_p2_measured_o",
        "setup": ROOT / "results_joint_ou" / "round_v1" / "JO_TRAIN_SETUP.json",
        "phi": ROOT / "results_joint_ou" / "round_v1" / "JO_PHI_DECISION.json",
        "atomic": ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "atomic_units.parquet",
        "occupancy": ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "occupancy_units.parquet",
        "pi_source": "occupancy",
        "trace_root": ROOT / "artifacts" / "e3_joint_ou_cs_p2_eventtraces_v1" / "cityscanner_nyc_p2_measured_o",
    },
    "visit": {
        "dataset": "cityscanner_nyc_pm25",
        "setup": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRAIN_SETUP.json",
        "phi": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_PHI_DECISION.json",
        "atomic": ROOT / "data" / "processed" / "cityscanner_nyc_pm25" / "atomic_units.parquet",
        "occupancy": ROOT / "data" / "processed" / "cityscanner_nyc_pm25" / "atomic_units.parquet",
        "pi_source": "atomic",
        "trace_root": ROOT / "artifacts" / "e3_c1_cityscanner_eventtraces_v1" / "cityscanner_nyc_pm25",
    },
}

UNIT_COLUMNS = [
    "unit_id",
    "split",
    "target_group",
    "opportunity_stratum",
    "spatial_id",
    "absolute_time",
]


def hour_block(stratum_id: str) -> float:
    for token in str(stratum_id).split("::"):
        if token.startswith("block") and token[5:].isdigit():
            return float(token[5:])
    return 0.0


def build_occupancy_pi_opp(atomic: pd.DataFrame) -> dict[tuple[str, str], float]:
    """Same definition as scripts/run_joint_ou_cs_p2.py: train client-stratum share."""
    train = atomic.loc[atomic["split"].astype(str) == "train"].copy()
    train["client_id"] = train["spatial_id"].astype(str)
    train["opportunity_stratum"] = train["opportunity_stratum"].astype(str)
    counts = train.groupby(["client_id", "opportunity_stratum"]).size()
    total = float(counts.sum())
    if total <= 0:
        raise GateStop("BLOCKED_REFERENCE", "occupancy pi_opp is empty")
    return {
        (str(key[0]), str(key[1])): float(value) / total
        for key, value in counts.items()
        if float(value) > 0.0
    }


def _read_units(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise GateStop("BLOCKED_ASSET", f"missing unit table {path}")
    frame = pd.read_parquet(path, columns=UNIT_COLUMNS)
    frame["unit_id"] = frame["unit_id"].astype(str)
    frame["split"] = frame["split"].astype(str)
    frame["target_group"] = frame["target_group"].astype(str)
    frame["opportunity_stratum"] = frame["opportunity_stratum"].astype(str)
    frame["spatial_id"] = frame["spatial_id"].astype(str)
    return frame


def _unit_map(frame: pd.DataFrame) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for row in frame.itertuples(index=False):
        mapping[str(row.unit_id)] = {
            "split": str(row.split),
            "target_group": str(row.target_group),
            "opportunity_stratum": str(row.opportunity_stratum),
            "spatial_id": str(row.spatial_id),
        }
    return mapping


def _confirmation(atomic: pd.DataFrame, encoding: dict[str, int]) -> dict:
    dates = {}
    for split, sub in atomic.groupby("split", sort=True):
        dates[str(split)] = {
            "n": int(len(sub)),
            "min_absolute_time": str(sub["absolute_time"].min()),
            "max_absolute_time": str(sub["absolute_time"].max()),
            "regions": sorted(sub["target_group"].astype(str).unique()),
        }
    known = {"train", "validation", "test"}
    present = set(dates)
    return {
        "splits": dates,
        "regions": sorted(encoding),
        "split_names": sorted(present),
        "unused_confirmation_batch": False,
        "unresolved_extra_split": sorted(present - known),
        "reason": (
            "Train is the fitting range. Validation was used for the frozen mu and for "
            "the City Scanner hotspot screen. Test has already been scored. "
            "An independent confirmation claim needs a split outside this set."
        ),
    }


def _aligned_mu(decision: dict, encoding: dict[str, int]) -> np.ndarray:
    mu = np.zeros(NUM_GROUPS, dtype=np.float64)
    source = decision.get("mu")
    if not isinstance(source, dict):
        raise GateStop("BLOCKED_ASSET", "phi decision mu is not a region map")
    for region in REGION_ORDER:
        if region not in source or region not in encoding:
            raise GateStop("BLOCKED_ASSET", f"mu or encoding lacks {region}")
        mu[int(encoding[region])] = float(source[region])
    total = float(mu.sum())
    if total <= 0 or np.any(mu < 0):
        raise GateStop("BLOCKED_ASSET", "phi mu is not a positive mass")
    return mu / total


def load_block(name: str) -> BlockContext:
    if name not in BLOCKS:
        raise GateStop("BLOCKED_ASSET", f"unknown block {name}")
    spec = BLOCKS[name]
    for key in ("setup", "phi", "atomic", "occupancy"):
        if not Path(spec[key]).is_file():
            raise GateStop("BLOCKED_ASSET", f"missing {key} for {name}: {spec[key]}")
    setup = json.loads(Path(spec["setup"]).read_text(encoding="utf-8"))
    decision = json.loads(Path(spec["phi"]).read_text(encoding="utf-8"))
    atomic = _read_units(Path(spec["atomic"]))
    occupancy = atomic if spec["pi_source"] == "atomic" else _read_units(Path(spec["occupancy"]))
    observed_encoding = {
        str(group): index
        for index, group in enumerate(sorted(atomic["target_group"].unique()))
    }
    setup_encoding = {str(key): int(value) for key, value in setup.get("h_encoding", {}).items()}
    if observed_encoding != setup_encoding:
        raise GateStop(
            "BLOCKED_METHOD_IDENTITY",
            "atomic target-group encoding does not match the frozen setup",
            {"atomic": observed_encoding, "setup": setup_encoding},
        )
    if set(observed_encoding) != set(REGION_ORDER):
        raise GateStop("BLOCKED_METHOD_IDENTITY", f"regions are {sorted(observed_encoding)}")
    extra_regions = set(occupancy["target_group"]) - set(observed_encoding)
    if extra_regions:
        raise GateStop("BLOCKED_METHOD_IDENTITY", f"occupancy has unknown regions {sorted(extra_regions)}")
    mu = _aligned_mu(decision, observed_encoding)
    setup_mu = np.asarray(setup.get("mu"), dtype=np.float64)
    if setup_mu.shape != mu.shape or float(np.max(np.abs(setup_mu - mu))) > 1e-12:
        raise GateStop("BLOCKED_ASSET", "setup mu and phi mu disagree")
    pi_frame = occupancy if spec["pi_source"] == "occupancy" else atomic
    pi_input = pi_frame.copy()
    pi_input["target_group_main"] = pi_input["target_group"]
    pi_input["support_flag"] = True
    spatial_to_client = {str(value): str(value) for value in pi_input["spatial_id"].unique()}
    built = build_pi_target(pi_input, spatial_to_client, split="test")
    pi_target = {
        (str(row.client_id), str(row.opportunity_stratum)): float(row.pi_k_s_tar)
        for row in built.itertuples()
    }
    pi_opp = build_occupancy_pi_opp(pi_input)
    checks = {
        "n_pi_target_keys": [len(pi_target), int(setup["n_pi_target_keys"])],
        "n_pi_opp_keys": [len(pi_opp), int(setup["n_pi_opp_keys"])],
        "mu_max_abs_diff": float(np.max(np.abs(setup_mu - mu))),
    }
    if checks["n_pi_target_keys"][0] != checks["n_pi_target_keys"][1]:
        raise GateStop("BLOCKED_REFERENCE", f"pi_target key count {checks['n_pi_target_keys']}")
    if checks["n_pi_opp_keys"][0] != checks["n_pi_opp_keys"][1]:
        raise GateStop("BLOCKED_REFERENCE", f"pi_opp key count {checks['n_pi_opp_keys']}")
    units = _unit_map(atomic)
    if spec["pi_source"] == "occupancy":
        for unit_id, meta in _unit_map(occupancy).items():
            current = units.get(unit_id)
            if current is None:
                units[unit_id] = meta
                continue
            for column in ("split", "target_group", "opportunity_stratum", "spatial_id"):
                if current[column] != meta[column]:
                    raise GateStop(
                        "BLOCKED_METHOD_IDENTITY",
                        f"atomic and occupancy disagree on {unit_id} {column}",
                    )
    return BlockContext(
        name=name,
        dataset=str(spec["dataset"]),
        mu=mu,
        pi_target=pi_target,
        pi_opp=pi_opp,
        units=units,
        encoding=observed_encoding,
        setup_checks=checks,
        confirmation=_confirmation(atomic, observed_encoding),
        trace_root=Path(spec["trace_root"]),
    )


def _as_dict(value) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        loaded = json.loads(value)
        if isinstance(loaded, dict):
            return loaded
    raise GateStop("BLOCKED_ASSET", "opportunity_features is not an object")


def _as_list(value) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise GateStop("BLOCKED_ASSET", "an event list field is not a list")


def _lookup_unit(context: BlockContext, unit_id: str, client_id: str, features: dict) -> tuple[int, str]:
    meta = context.units.get(str(unit_id))
    if meta is None:
        raise GateStop("BLOCKED_ASSET", f"unit {unit_id} is absent from atomic and occupancy tables")
    if meta["split"] != "train":
        raise GateStop("BLOCKED_ASSET", f"unit {unit_id} is in split {meta['split']}, not train")
    if meta["spatial_id"] != str(client_id):
        raise GateStop(
            "BLOCKED_METHOD_IDENTITY",
            f"unit {unit_id} belongs to spatial {meta['spatial_id']} but the event client is {client_id}",
        )
    encoded = context.encoding.get(meta["target_group"])
    if encoded is None:
        raise GateStop("BLOCKED_METHOD_IDENTITY", f"unit {unit_id} has unknown region {meta['target_group']}")
    trace_groups = features.get("target_group_by_unit")
    if isinstance(trace_groups, dict) and str(unit_id) in trace_groups:
        if int(trace_groups[str(unit_id)]) != int(encoded):
            raise GateStop("BLOCKED_METHOD_IDENTITY", f"trace group disagrees for unit {unit_id}")
    trace_strata = features.get("opportunity_stratum_by_unit")
    stratum = meta["opportunity_stratum"]
    if isinstance(trace_strata, dict) and str(unit_id) in trace_strata:
        if str(trace_strata[str(unit_id)]) != stratum:
            raise GateStop("BLOCKED_METHOD_IDENTITY", f"trace stratum disagrees for unit {unit_id}")
    return int(encoded), stratum


def _check_observation(risk: list[str], observed: list[str], raw_o) -> np.ndarray:
    if len(risk) != len(set(risk)):
        raise GateStop("BLOCKED_METHOD_IDENTITY", "a risk set repeats a unit")
    if not set(observed).issubset(set(risk)):
        raise GateStop("BLOCKED_METHOD_IDENTITY", "observed units are outside the risk set")
    mask = np.asarray([1.0 if unit in set(observed) else 0.0 for unit in risk], dtype=np.float64)
    if isinstance(raw_o, dict):
        flagged = {str(unit) for unit, flag in raw_o.items() if bool(flag)}
        if flagged != set(observed):
            raise GateStop("BLOCKED_METHOD_IDENTITY", "O dict disagrees with observed_unit_ids")
    elif isinstance(raw_o, list) and len(raw_o) == len(risk):
        listed = np.asarray([1.0 if bool(flag) else 0.0 for flag in raw_o], dtype=np.float64)
        if not np.array_equal(listed, mask):
            raise GateStop("BLOCKED_METHOD_IDENTITY", "O list disagrees with observed_unit_ids")
    return mask


def replay_seed(context: BlockContext, seed: int) -> ReplayResult:
    trace_dir = context.trace_root / f"seed{int(seed)}" / "training_eventtrace"
    if not (trace_dir / "events.parquet").is_file():
        raise GateStop("BLOCKED_ASSET", f"missing event trace {trace_dir}")
    trace, identity = load_event_trace(trace_dir)
    if int(trace.metadata.num_windows) != NUM_WINDOWS:
        raise GateStop("BLOCKED_ASSET", f"trace windows {trace.metadata.num_windows}")
    propensity = ObservationPropensity()
    if (
        propensity.prior_rate != PROPENSITY_PRIOR
        or propensity.min_samples != PROPENSITY_MIN_SAMPLES
        or propensity.l2 != PROPENSITY_L2
    ):
        raise GateStop("BLOCKED_METHOD_IDENTITY", "observation propensity defaults differ from the freeze")
    if not identity.get("trace_hash"):
        raise GateStop("BLOCKED_ASSET", f"seed {seed} has no trace hash")
    if int(trace.metadata.s_max) != S_MAX:
        raise GateStop("BLOCKED_ASSET", f"seed {seed} metadata s_max is {trace.metadata.s_max}")
    frame = trace.events
    usable = frame.loc[frame["U"].astype(int) == 1]
    arrivals = usable["arrival_time"].astype(float).to_numpy()
    if not np.isfinite(arrivals).all():
        raise GateStop("BLOCKED_ASSET", f"seed {seed} has a non-finite arrival time")
    arrival_close = np.floor(arrivals).astype(int)
    audit = {
        "seed": int(seed),
        "trace_hash": str(identity.get("trace_hash")),
        "n_rows": int(len(frame)),
        "n_u1": int(len(usable)),
        "n_u0": int(len(frame) - len(usable)),
        "n_u1_tau_above_smax": int((usable["tau"].astype(int) > S_MAX).sum()),
        "n_u0_tau_above_smax": int(
            ((frame["U"].astype(int) == 0) & (frame["tau"].astype(int) > S_MAX)).sum()
        ),
        "n_u1_arrival_close_ne_window": int((arrival_close != usable["window_id"].astype(int).to_numpy()).sum()),
        "q_use_used": False,
        "oracle_probability_used": False,
        "target_value_read": False,
        "columns": [str(column) for column in frame.columns],
    }
    if "target_value" in frame.columns:
        raise GateStop("BLOCKED_ASSET", "event table contains target_value")
    if audit["n_u1_tau_above_smax"] > 0:
        raise GateStop(
            "BLOCKED_METHOD_IDENTITY",
            "U=1 contains tau above S_max, contradicting the staleness rule",
            audit,
        )
    attempts: list[FrozenAttempt] = []
    retries: dict[tuple[str, int], int] = {}
    composition_error = 0.0
    min_positive = None
    n_one_hot = 0
    n_mixed = 0
    n_zero = 0
    first_sample = None
    missing_reference = None
    for window in range(NUM_WINDOWS):
        if window % 20 == 0:
            print(f"replay block={context.name} seed={seed} window={window}", flush=True)
        rows = frame.loc[frame["window_id"].astype(int) == window]
        built_rows = []
        for row in rows.itertuples(index=False):
            if int(row.U) != 1:
                continue
            features = _as_dict(row.opportunity_features)
            risk = [str(unit) for unit in _as_list(row.risk_set_unit_ids)]
            observed = [str(unit) for unit in _as_list(row.observed_unit_ids)]
            groups = []
            strata = []
            for unit in risk:
                group, stratum = _lookup_unit(context, unit, str(row.client_id), features)
                groups.append(group)
                strata.append(stratum)
            observation = _check_observation(risk, observed, row.O)
            planned = float(len(risk))
            key = (str(row.client_id), int(window))
            retry = retries.get(key, 0)
            retries[key] = retry + 1
            arrival = float(row.arrival_time)
            if not np.isfinite(arrival):
                raise GateStop("BLOCKED_ASSET", f"non-finite arrival for {row.client_id}")
            built_rows.append((row, risk, groups, strata, observation, planned, retry, arrival))
        for row, risk, groups, strata, observation, planned, retry, arrival in built_rows:
            if not risk or float(observation.sum()) <= 0.0:
                composition = tuple(0.0 for _ in range(NUM_GROUPS))
                mass = 0.0
                group_mass = composition
            else:
                pi_tar = []
                pi_opp = []
                p_hat = []
                for stratum in strata:
                    key = (str(row.client_id), stratum)
                    if key not in context.pi_target or key not in context.pi_opp:
                        missing_reference = key
                        raise GateStop(
                            "BLOCKED_REFERENCE",
                            f"missing frozen design support for client {key[0]} stratum {key[1]}",
                            {"seed": int(seed), "window": int(window)},
                        )
                    pi_tar.append(context.pi_target[key])
                    pi_opp.append(context.pi_opp[key])
                    p_hat.append(
                        float(
                            propensity.predict(
                                np.asarray(
                                    [1.0, hour_block(stratum), float(np.log1p(planned))],
                                    dtype=np.float64,
                                )
                            )
                        )
                    )
                zeta = zeta_hat_stratum(
                    np.asarray(pi_tar, dtype=np.float64),
                    np.asarray(pi_opp, dtype=np.float64),
                    pi_min=PI_MIN,
                )
                try:
                    stage1 = reconstruct_stage1(
                        zeta,
                        np.asarray(p_hat, dtype=np.float64),
                        observation,
                        np.asarray(groups, dtype=np.int64),
                        num_groups=NUM_GROUPS,
                        a_max=A_MAX,
                        p_min=P_MIN,
                    )
                except ValueError as exc:
                    raise GateStop("BLOCKED_METHOD_IDENTITY", str(exc)) from exc
                composition_vector = np.asarray(stage1.composition, dtype=np.float64)
                group_vector = np.asarray(stage1.groups, dtype=np.float64)
                mass = float(stage1.total)
                if mass > 0.0:
                    error = abs(float(composition_vector.sum()) - 1.0)
                    composition_error = max(composition_error, error)
                    if error > 1e-6 or float(composition_vector.min()) < -1e-8:
                        raise GateStop(
                            "BLOCKED_METHOD_IDENTITY",
                            f"composition failed the simplex check at seed {seed} window {window}",
                        )
                    if abs(float(group_vector.sum()) - mass) > 1e-6:
                        raise GateStop("BLOCKED_METHOD_IDENTITY", "group mass does not equal total mass")
                composition = tuple(float(value) for value in composition_vector)
                group_mass = tuple(float(value) for value in group_vector)
            positive = mass > 0.0
            if positive:
                min_positive = mass if min_positive is None else min(min_positive, mass)
                counts = np.zeros(NUM_GROUPS, dtype=int)
                for group, flag in zip(groups, observation):
                    if flag > 0.0:
                        counts[int(group)] += 1
                one_hot = bool(np.max(composition) >= 1.0 - 1e-8)
                if one_hot:
                    n_one_hot += 1
                    if int(np.count_nonzero(counts)) != 1:
                        raise GateStop(
                            "BLOCKED_METHOD_IDENTITY",
                            "one-hot composition is not explained by a single observed group",
                        )
                else:
                    n_mixed += 1
            else:
                n_zero += 1
                counts = np.zeros(NUM_GROUPS, dtype=int)
                one_hot = False
            attempt = FrozenAttempt(
                attempt_id=f"{row.client_id}|{window}|{retry}",
                client_id=str(row.client_id),
                registration_window=int(window),
                registration_time=float(row.registration_time),
                arrival_time=arrival,
                arrival_close=int(np.floor(arrival)),
                retry=int(retry),
                m=mass,
                composition=composition,
                group_mass=group_mass,
                raw_workload=float(row.raw_workload) if "raw_workload" in frame.columns else None,
                positive=positive,
            )
            attempts.append(attempt)
            if first_sample is None and positive:
                first_sample = {
                    "window_id": int(window),
                    "history_rows_before_window": int(len(propensity.history_y)),
                    "p_hat_source": (
                        "prior_rate"
                        if len(propensity.history_y) < propensity.min_samples
                        else "lagged_logistic"
                    ),
                    "attempt_id": attempt.attempt_id,
                    "m": mass,
                    "composition": list(composition),
                    "observed_group_counts": counts.tolist(),
                    "one_hot_explained_by_single_group": one_hot,
                }
        update_x = []
        update_y = []
        for row in rows.itertuples(index=False):
            features = _as_dict(row.opportunity_features)
            risk = [str(unit) for unit in _as_list(row.risk_set_unit_ids)]
            observed = [str(unit) for unit in _as_list(row.observed_unit_ids)]
            if not risk:
                continue
            strata = []
            for unit in risk:
                _group, stratum = _lookup_unit(context, unit, str(row.client_id), features)
                strata.append(stratum)
            observation = _check_observation(risk, observed, row.O)
            planned = float(np.log1p(len(risk)))
            for stratum, flag in zip(strata, observation):
                update_x.append([1.0, hour_block(stratum), planned])
                update_y.append(float(flag))
        if update_x:
            propensity.update_records_after_completion(
                np.asarray(update_x, dtype=np.float64),
                np.asarray(update_y, dtype=np.float64),
            )
    if missing_reference is not None:
        raise GateStop("BLOCKED_REFERENCE", f"missing design key {missing_reference}")
    if first_sample is None:
        raise GateStop("BLOCKED_ASSET", f"seed {seed} has no positive-mass delivery")
    audit.update(
        {
            "n_attempts": len(attempts),
            "n_positive": int(sum(attempt.positive for attempt in attempts)),
            "n_zero_mass": n_zero,
            "n_one_hot": n_one_hot,
            "n_mixed": n_mixed,
            "max_abs_composition_error": composition_error,
            "min_positive_mass": min_positive,
            "first_positive": first_sample,
            "propensity_history_rows": int(len(propensity.history_y)),
        }
    )
    return ReplayResult(seed=int(seed), trace_hash=str(identity.get("trace_hash")), attempts=attempts, audit=audit)
