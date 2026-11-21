"""Current-window opportunity C_cov: rolling predictor + window max-residual conformal.

Uses only F_{r-} completed windows. Current R is never an input.
Calibration unit is a window, not iid events inside a window.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from raven_mcs.sag.certificates import (
    c_cov_from_opportunity_lcb,
    encode_pair,
    opportunity_mass_map,
)


def rolling_pi_hat(
    history_masses: Sequence[Mapping[tuple[str, str], float]],
    pairs: Sequence[tuple[str, str]],
    *,
    lookback: int,
) -> dict[tuple[str, str], float]:
    recent = list(history_masses[-int(lookback):]) if lookback > 0 else []
    if not recent:
        return {key: float("nan") for key in pairs}
    out: dict[tuple[str, str], float] = {}
    for key in pairs:
        xs = [float(row.get(key, 0.0)) for row in recent]
        out[key] = float(np.mean(xs))
    return out


def window_max_residual(
    pi_hat: Mapping[tuple[str, str], float],
    realized: Mapping[tuple[str, str], float],
    pairs: Sequence[tuple[str, str]],
) -> float:
    vals = []
    for key in pairs:
        hat = pi_hat.get(key, float("nan"))
        ref = float(realized.get(key, 0.0))
        if not np.isfinite(float(hat)):
            continue
        vals.append(float(hat) - ref)
    if not vals:
        return float("nan")
    return float(max(vals))


def conformal_upper_residual(residuals: Sequence[float], delta: float) -> float:
    xs = sorted(float(x) for x in residuals if np.isfinite(float(x)))
    if not xs:
        return float("nan")
    n = len(xs)
    k = min(n, max(1, int(np.ceil((n + 1) * (1.0 - float(delta))))))
    return float(xs[k - 1])


def history_mass_list(history: Sequence[Mapping[str, Any]]) -> list[dict[tuple[str, str], float]]:
    return [opportunity_mass_map(row) for row in history]


def dynamic_lower_pi_opp(
    history: Sequence[Mapping[str, Any]],
    pairs: Sequence[tuple[str, str]],
    *,
    lookback: int,
    delta: float,
    min_calib: int,
) -> dict[str, Any]:
    """F_{r-}-measurable rolling predictor + window max-residual conformal LCB."""
    masses = history_mass_list(history)
    n = len(masses)
    fail = {
        "cold_start": True,
        "pi_hat": {key: float("nan") for key in pairs},
        "lowers": {
            key: {
                "pi_hat_opp": float("nan"),
                "lower_pi_opp": float("nan"),
                "n": float(n),
            }
            for key in pairs
        },
        "q": float("nan"),
        "n_calib": 0,
        "n_history": n,
        "method": "rolling_mean_plus_window_max_residual_conformal",
    }
    if n < int(lookback) or int(lookback) <= 0:
        return fail
    pi_hat = rolling_pi_hat(masses, pairs, lookback=int(lookback))
    residuals: list[float] = []
    for t in range(int(lookback), n):
        hat_t = rolling_pi_hat(masses[:t], pairs, lookback=int(lookback))
        r_t = window_max_residual(hat_t, masses[t], pairs)
        if np.isfinite(r_t):
            residuals.append(r_t)
    if len(residuals) < int(min_calib):
        fail["n_calib"] = len(residuals)
        fail["pi_hat"] = pi_hat
        return fail
    q = conformal_upper_residual(residuals, delta)
    lowers = {}
    for key in pairs:
        hat = float(pi_hat[key])
        lower = float(max(0.0, hat - q)) if np.isfinite(hat) and np.isfinite(q) else float("nan")
        lowers[key] = {
            "pi_hat_opp": hat,
            "lower_pi_opp": lower,
            "n": float(n),
            "q_max_residual": q,
            "n_calib": float(len(residuals)),
        }
    return {
        "cold_start": False,
        "pi_hat": pi_hat,
        "lowers": lowers,
        "q": q,
        "n_calib": len(residuals),
        "n_history": n,
        "method": "rolling_mean_plus_window_max_residual_conformal",
    }


def coverage_flags(
    lowers: Mapping[tuple[str, str], Mapping[str, float]],
    realized: Mapping[tuple[str, str], float],
    pi_target: Mapping[tuple[str, str], float],
) -> dict[str, Any]:
    n_pair = 0
    n_cover = 0
    w_cover = 0.0
    w_tot = 0.0
    for key, mass in pi_target.items():
        w = float(mass)
        if w <= 0.0:
            continue
        rec = lowers.get((str(key[0]), str(key[1])), {})
        lower = rec.get("lower_pi_opp", float("nan"))
        ref = float(realized.get((str(key[0]), str(key[1])), 0.0))
        w_tot += w
        n_pair += 1
        ok = np.isfinite(float(lower)) and float(lower) <= ref
        n_cover += int(ok)
        w_cover += w if ok else 0.0
    joint = int(n_pair > 0 and n_cover == n_pair)
    return {
        "pairwise_coverage": (n_cover / n_pair) if n_pair else float("nan"),
        "target_mass_weighted_coverage": (w_cover / w_tot) if w_tot else float("nan"),
        "joint_window_coverage": joint,
        "n_pairs": n_pair,
    }


def same_block_indices(blocks: Sequence[int], current_block: int) -> list[int]:
    return [i for i, block in enumerate(blocks) if int(block) == int(current_block)]


def tod_conditioned_rolling_pi_hat(
    history_masses: Sequence[Mapping[tuple[str, str], float]],
    history_blocks: Sequence[int],
    pairs: Sequence[tuple[str, str]],
    *,
    current_block: int,
    lookback: int,
) -> dict[tuple[str, str], float]:
    """TOD_CONDITIONED_ROLLING_V1: last-L same-block means; else global last-L.

    Zero masses enter the mean. Current-window mass is not an argument.
    Dataset name is not an argument.
    """
    if len(history_masses) != len(history_blocks):
        raise ValueError("history masses and public blocks must align")
    same = [history_masses[i] for i in same_block_indices(history_blocks, current_block)]
    if same:
        return rolling_pi_hat(same, pairs, lookback=int(lookback))
    return rolling_pi_hat(history_masses, pairs, lookback=int(lookback))


def _tod_hats_and_residuals(
    masses: Sequence[Mapping[tuple[str, str], float]],
    blocks: Sequence[int],
    pairs: Sequence[tuple[str, str]],
    *,
    lookback: int,
) -> tuple[list[dict[tuple[str, str], float]], list[float]]:
    hats: list[dict[tuple[str, str], float]] = []
    residuals: list[float] = []
    n = len(masses)
    for t in range(n):
        hat_t = tod_conditioned_rolling_pi_hat(
            masses[:t],
            blocks[:t],
            pairs,
            current_block=int(blocks[t]) if t < len(blocks) else -1,
            lookback=int(lookback),
        )
        hats.append(hat_t)
        if t >= int(lookback):
            residuals.append(window_max_residual(hat_t, masses[t], pairs))
        else:
            residuals.append(float("nan"))
    return hats, residuals


def dynamic_lower_pi_opp_tod(
    history: Sequence[Mapping[str, Any]],
    history_blocks: Sequence[int],
    current_block: int,
    pairs: Sequence[tuple[str, str]],
    *,
    lookback: int,
    delta: float,
    min_calib: int,
    calibration: str = "global",
) -> dict[str, Any]:
    """TOD rolling predictor + window max-residual conformal LCB.

    calibration='global' is Stage 1 (R1d conformal, new predictor).
    calibration='tod_block' is Stage 2 (same-block residual quantile, global fallback).
    """
    masses = history_mass_list(history)
    n = len(masses)
    method = (
        "tod_conditioned_rolling_plus_window_max_residual_conformal"
        if calibration == "global"
        else "tod_conditioned_rolling_plus_tod_block_max_residual_conformal"
    )
    fail = {
        "cold_start": True,
        "pi_hat": {key: float("nan") for key in pairs},
        "lowers": {
            key: {
                "pi_hat_opp": float("nan"),
                "lower_pi_opp": float("nan"),
                "n": float(n),
            }
            for key in pairs
        },
        "q": float("nan"),
        "n_calib": 0,
        "n_history": n,
        "method": method,
        "calibration": calibration,
        "used_same_block_fallback": False,
    }
    if n < int(lookback) or int(lookback) <= 0 or len(history_blocks) != n:
        return fail
    hats, residuals = _tod_hats_and_residuals(
        masses, history_blocks, pairs, lookback=int(lookback),
    )
    valid_idx = [i for i, r in enumerate(residuals) if np.isfinite(r)]
    if calibration == "tod_block":
        same_idx = [
            i for i in valid_idx if int(history_blocks[i]) == int(current_block)
        ]
        if len(same_idx) >= int(min_calib):
            calib_res = [residuals[i] for i in same_idx]
        else:
            calib_res = [residuals[i] for i in valid_idx]
            fail["used_same_block_fallback"] = True
    else:
        calib_res = [residuals[i] for i in valid_idx]
    if len(calib_res) < int(min_calib):
        fail["n_calib"] = len(calib_res)
        fail["pi_hat"] = tod_conditioned_rolling_pi_hat(
            masses, history_blocks, pairs, current_block=int(current_block), lookback=int(lookback),
        )
        return fail
    q = conformal_upper_residual(calib_res, delta)
    pi_hat = tod_conditioned_rolling_pi_hat(
        masses, history_blocks, pairs, current_block=int(current_block), lookback=int(lookback),
    )
    lowers = {}
    for key in pairs:
        hat = float(pi_hat[key])
        lower = float(max(0.0, hat - q)) if np.isfinite(hat) and np.isfinite(q) else float("nan")
        lowers[key] = {
            "pi_hat_opp": hat,
            "lower_pi_opp": lower,
            "n": float(n),
            "q_max_residual": q,
            "n_calib": float(len(calib_res)),
        }
    return {
        "cold_start": False,
        "pi_hat": pi_hat,
        "lowers": lowers,
        "q": q,
        "n_calib": len(calib_res),
        "n_history": n,
        "method": method,
        "calibration": calibration,
        "used_same_block_fallback": bool(fail["used_same_block_fallback"]),
    }


def stage1_stop_status(
    *,
    joint_coverage: float,
    c_cov_zero_fraction: float,
    coverage_slides: bool,
    joint_stop: float = 0.90,
    zero_stop: float = 0.90,
) -> str:
    if (not np.isfinite(float(joint_coverage))) or float(joint_coverage) < float(joint_stop) or bool(coverage_slides):
        return "DYNAMIC_COV_NOT_CALIBRATED"
    if float(c_cov_zero_fraction) < float(zero_stop):
        return "STAGE1_DYNAMIC_COV_CALIBRATED_NONVACUOUS"
    return "DYNAMIC_COV_TOO_CONSERVATIVE"


def stage2_trigger_status(*, point_zero_fraction: float, c_cov_zero_fraction: float, zero_stop: float = 0.90) -> str:
    if float(point_zero_fraction) >= float(zero_stop):
        return "R1E_POINT_PREDICTOR_NONVACUITY_NOT_ACHIEVED"
    if float(c_cov_zero_fraction) >= float(zero_stop):
        return "GLOBAL_CALIBRATION_DOMINATES_NONVACUITY"
    return "NO_STAGE2"


def extract_window_opp_masses(
    *,
    trace_events: Any,
    dataset: Any,
    n_windows: int,
    paper_h_by_unit: Mapping[str, int] | None = None,
) -> list[dict[str, Any]]:
    """Post-hoc realized current-window opportunity masses from EventTrace.

    Does not enter the same-window Gate. Uses risk-set marks only.
    """
    from raven_mcs.data.window_dataset import extract_window_slice
    from raven_mcs.sag.certificates import window_opportunity_event_counts, window_opportunity_masses

    rows: list[dict[str, Any]] = []
    for window_id in range(int(n_windows)):
        slc = extract_window_slice(
            window_id,
            trace_events,
            dataset,
            h_by_unit=paper_h_by_unit,
        )
        pairs = [
            (str(rec.client_id), str(stratum))
            for rec in slc.records
            for stratum in rec.opportunity_strata
        ]
        counts = window_opportunity_event_counts(pairs)
        masses = window_opportunity_masses(pairs)
        rows.append(
            {
                "window_id": int(window_id),
                "opp_mass_by_pair": {encode_pair(k): float(v) for k, v in masses.items()},
                "opp_count_by_pair": {encode_pair(k): float(v) for k, v in counts.items()},
                "opp_event_total": float(sum(counts.values())),
            }
        )
    return rows
