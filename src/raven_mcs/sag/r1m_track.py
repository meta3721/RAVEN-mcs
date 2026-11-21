"""Sequential (dataset, a) certificate track. Independent buffers; one ridge snapshot per block."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from raven_mcs.sag.r1l_conformal import c_lcb, finite_sample_conformal_quantile, gate_on
from raven_mcs.sag.r1l_design import design_from_gate
from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, NUM_TOL, TAU_COV
from raven_mcs.sag.r1m_predictor import RidgeSnapshot, fit_ridge_snapshot
from raven_mcs.sag.r1m_reset import miscoverage_reset_trigger
from raven_mcs.sag.r1m_spec import PREDICTOR_ID, RESET_RULE_ID, RIDGE_ALPHA


@dataclass
class TrackState:
    dataset: str
    availability_level: float
    pretest_mean: float
    completed_c: list[float]
    hours: list[int]
    weekends: list[int]
    fit_labels: list[str]
    snapshot: RidgeSnapshot
    cal_scores: list[float] = field(default_factory=list)
    cal_windows: list[str] = field(default_factory=list)
    block_id: int = 0
    pending_reset: bool = False
    last_snapshot_hash: str = ""


def open_track(
    *,
    dataset: str,
    availability_level: float,
    pretest_c: list[float],
    pretest_hours: list[int],
    pretest_weekends: list[bool],
    pretest_labels: list[str],
) -> TrackState:
    if not pretest_c:
        raise ValueError("R1M_INSUFFICIENT_PRETEST_HISTORY")
    mean = float(sum(pretest_c) / len(pretest_c))
    snap = fit_ridge_snapshot(
        availability_level=availability_level,
        completed_c=pretest_c,
        hours=pretest_hours,
        weekends=pretest_weekends,
        pretest_mean=mean,
        fit_end_window=str(pretest_labels[-1]),
        block_id=0,
    )
    return TrackState(
        dataset=str(dataset),
        availability_level=float(availability_level),
        pretest_mean=mean,
        completed_c=list(pretest_c),
        hours=[int(h) for h in pretest_hours],
        weekends=[int(bool(w)) for w in pretest_weekends],
        fit_labels=list(pretest_labels),
        snapshot=snap,
        last_snapshot_hash=snap.snapshot_hash,
    )


def decide_window(
    state: TrackState,
    *,
    window_id: int,
    hour: int,
    weekend: bool,
) -> dict[str, Any]:
    q, n_cal, warmup = finite_sample_conformal_quantile(state.cal_scores, alpha=ALPHA)
    if state.pending_reset:
        phase = "RESET"
    elif warmup or n_cal < N_MIN:
        phase = "WARMUP"
    else:
        phase = "CERTIFIED"

    c_hat = state.snapshot.predict(
        availability_level=state.availability_level,
        history_c=state.completed_c,
        hour=hour,
        weekend=weekend,
    )
    if phase != "CERTIFIED":
        c_lcb_v = 0.0
        gate = 0
        q_out = float("nan")
    else:
        c_lcb_v = float(c_lcb(c_hat, q))
        gate = 1 if gate_on(c_lcb_v, TAU_COV) else 0
        q_out = float(q)

    design = design_from_gate(gate)
    if phase == "RESET" and int(design) != 0:
        raise RuntimeError("RESET cannot have Design ON")
    if phase != "CERTIFIED" and int(gate) != 0:
        raise RuntimeError("non-CERTIFIED Gate must be OFF")

    return {
        "dataset": state.dataset,
        "window_id": int(window_id),
        "availability_level": float(state.availability_level),
        "block_id": int(state.block_id),
        "state_before_decision": phase,
        "C_hat": float(c_hat),
        "q_t": q_out,
        "n_cal": int(n_cal),
        "n_cal_before_decision": int(n_cal),
        "cal_window_ids": list(state.cal_windows),
        "C_LCB": float(c_lcb_v),
        "Gate": int(gate),
        "Design": int(design),
        "predictor_id": PREDICTOR_ID,
        "ridge_alpha": RIDGE_ALPHA,
        "predictor_snapshot_id": f"{state.dataset}|a={state.availability_level:.2f}|b{state.block_id}",
        "snapshot_hash": state.snapshot.snapshot_hash,
        "feature_spec_hash": state.snapshot.feature_spec_hash,
        "reset_rule_id": RESET_RULE_ID,
        "pretest_mean": float(state.pretest_mean),
        "n_history": int(len(state.completed_c)),
        "k_n_clipped": False,
    }


def complete_window(
    state: TrackState,
    rec: dict[str, Any],
    *,
    c_t: float,
    hour: int,
    weekend: bool,
    window_label: str,
) -> dict[str, Any]:
    c_hat = float(rec["C_hat"])
    score = float(c_hat - float(c_t))
    state.completed_c.append(float(c_t))
    state.hours.append(int(hour))
    state.weekends.append(int(bool(weekend)))
    state.fit_labels.append(str(window_label))

    reset = miscoverage_reset_trigger(
        state=str(rec["state_before_decision"]),
        c_lcb=float(rec["C_LCB"]),
        c_t=float(c_t),
        tol=NUM_TOL,
    )
    if rec["state_before_decision"] == "RESET":
        state.pending_reset = False
        state.cal_scores.append(score)
        state.cal_windows.append(str(window_label))
        rec["reset_trigger_after_window"] = 0
        rec["state_next_window"] = "WARMUP"
        rec["S_t"] = score
        rec["current_window_in_buffer"] = False
        return rec

    if reset:
        rec["reset_trigger_after_window"] = 1
        rec["state_next_window"] = "RESET"
        state.block_id += 1
        state.snapshot = fit_ridge_snapshot(
            availability_level=state.availability_level,
            completed_c=state.completed_c,
            hours=state.hours,
            weekends=[bool(w) for w in state.weekends],
            pretest_mean=state.pretest_mean,
            fit_end_window=str(window_label),
            block_id=state.block_id,
        )
        state.cal_scores = []
        state.cal_windows = []
        state.pending_reset = True
        rec["S_t"] = score
        rec["current_window_in_buffer"] = False
        rec["new_snapshot_hash"] = state.snapshot.snapshot_hash
        return rec

    state.cal_scores.append(score)
    state.cal_windows.append(str(window_label))
    rec["reset_trigger_after_window"] = 0
    rec["S_t"] = score
    rec["current_window_in_buffer"] = False
    n_after = len(state.cal_scores)
    _, n_after_q, warm = finite_sample_conformal_quantile(state.cal_scores, alpha=ALPHA)
    rec["state_next_window"] = "WARMUP" if (n_after < N_MIN or warm) else "CERTIFIED"
    rec["n_cal_after"] = int(n_after_q)
    return rec
