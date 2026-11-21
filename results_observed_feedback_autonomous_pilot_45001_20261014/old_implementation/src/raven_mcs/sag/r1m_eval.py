"""R1m metrics, routing criteria, and artifact-derived verdicts. No theorem claims."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.stats import beta

from raven_mcs.sag.availability_stress import BOUNDARY_NEAR_MARGIN
from raven_mcs.sag.r1j_eval import classify, confusion_metrics
from raven_mcs.sag.r1l_spec import NUM_TOL, TAU_COV
from raven_mcs.sag.r1m_spec import ALLOWED_OVERALL, ALLOWED_TRACK, PRIMARY, SECONDARY

VALIDITY_MIN = 0.95
FSR_MAX = 0.05
BALANCED_ACC_MIN = 0.65
DUTY_MIN = 0.25
PRIMARY_CERT_MIN = 15
SECONDARY_CERT_MIN = 10
ZERO_FRAC_MAX = 0.80


def clopper_pearson_upper(errors: int, n: int, conf: float = 0.95) -> float:
    k = int(errors)
    n = int(n)
    if n <= 0:
        return float("nan")
    if k >= n:
        return 1.0
    if k < 0:
        return float("nan")
    return float(beta.ppf(conf, k + 1, n - k))


def _bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(("1", "true", "yes"))


def certified(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[frame["state_before_decision"].astype(str) == "CERTIFIED"].copy()


def annotate_window(row: Mapping[str, Any]) -> dict[str, Any]:
    c_t = float(row["C_t"])
    c_lcb = float(row["C_LCB"])
    gate = int(row["Gate_t"])
    y_oracle = bool(c_t + NUM_TOL >= TAU_COV)
    valid = bool(c_lcb <= c_t + NUM_TOL)
    fs = bool(gate == 1 and c_t + NUM_TOL < TAU_COV)
    fu = bool(gate == 0 and c_t + NUM_TOL >= TAU_COV)
    y_cert = bool(gate == 1)
    return {
        "Y_oracle": y_oracle,
        "Y_cert": y_cert,
        "certificate_valid": valid,
        "false_safe": fs,
        "false_unsafe": fu,
        "classification": classify(y_oracle, y_cert),
        "boundary_near": bool(abs(c_t - TAU_COV) <= BOUNDARY_NEAR_MARGIN + NUM_TOL),
        "C_LCB_zero": bool(abs(c_lcb) <= NUM_TOL),
    }


def summarize_scope(frame: pd.DataFrame) -> dict[str, Any]:
    n_total = int(len(frame))
    n_warmup = int((frame["state_before_decision"].astype(str) == "WARMUP").sum()) if n_total else 0
    n_reset = int((frame["state_before_decision"].astype(str) == "RESET").sum()) if n_total else 0
    cert = certified(frame)
    n_cert = int(len(cert))
    n_blocks = int(frame["block_id"].nunique()) if n_total else 0
    reset_count = int(frame["reset_trigger_after_window"].astype(int).sum()) if n_total else 0
    lengths = (
        frame.groupby("block_id").size().astype(float).tolist() if n_total else []
    )
    duty = float(n_cert / n_total) if n_total else float("nan")
    design_all = float(frame["Design_t"].astype(int).mean()) if n_total else float("nan")
    design_cert = float(cert["Design_t"].astype(int).mean()) if n_cert else float("nan")
    design_on = int(cert["Design_t"].astype(int).sum()) if n_cert else 0
    if n_cert:
        validity = float(cert["certificate_valid"].astype(bool).mean())
        mis = 1.0 - validity
        n_unsafe = int((~cert["Y_oracle"].astype(bool)).sum())
        n_safe = int(cert["Y_oracle"].astype(bool).sum())
        fs_count = int(cert["false_safe"].astype(bool).sum())
        fu_count = int(cert["false_unsafe"].astype(bool).sum())
        fsr_unsafe = float(fs_count / n_unsafe) if n_unsafe else 0.0
        fsr_all = float(fs_count / n_cert)
        cm = confusion_metrics(cert)
        zero_frac = float(cert["C_LCB_zero"].astype(bool).mean())
        lcb = cert["C_LCB"].astype(float)
        med = float(lcb.median())
        p10 = float(lcb.quantile(0.10))
        p90 = float(lcb.quantile(0.90))
        bn = cert.loc[cert["boundary_near"].astype(bool)]
        n_bn = int(len(bn))
        bn_both = bool(
            n_bn
            and int(bn["Y_oracle"].astype(bool).sum()) > 0
            and int((~bn["Y_oracle"].astype(bool)).sum()) > 0
        )
        bn_zero = bool(n_bn and bool(bn["C_LCB_zero"].astype(bool).all()))
        mis_count = int((~cert["certificate_valid"].astype(bool)).sum())
    else:
        validity = mis = fsr_unsafe = fsr_all = zero_frac = float("nan")
        n_unsafe = n_safe = fs_count = fu_count = mis_count = 0
        cm = confusion_metrics(pd.DataFrame(columns=["Y_oracle", "Y_cert"]))
        med = p10 = p90 = float("nan")
        n_bn = 0
        bn_both = False
        bn_zero = True
    abstention = float((n_warmup + n_reset) / n_total) if n_total else float("nan")
    return {
        "n_total_windows": n_total,
        "n_warmup": n_warmup,
        "n_reset": n_reset,
        "n_certified": n_cert,
        "certified_duty_cycle": duty,
        "design_on_fraction_all": design_all,
        "design_on_fraction_certified": design_cert,
        "design_on_count": design_on,
        "reset_count": reset_count,
        "number_of_blocks": n_blocks,
        "mean_block_length": float(np.mean(lengths)) if lengths else float("nan"),
        "median_block_length": float(np.median(lengths)) if lengths else float("nan"),
        "n_oracle_safe_certified": n_safe,
        "n_oracle_unsafe_certified": n_unsafe,
        "validity_rate": validity,
        "miscoverage_rate": mis,
        "miscoverage_count": mis_count,
        "false_safe_count": fs_count,
        "false_unsafe_count": fu_count,
        "FSR_unsafe": fsr_unsafe,
        "FSR_all": fsr_all,
        "fraction_C_LCB_zero": zero_frac,
        "median_C_LCB": med,
        "p10_C_LCB": p10,
        "p90_C_LCB": p90,
        "abstention_fraction": abstention,
        "n_boundary_near_certified": n_bn,
        "boundary_has_both": bn_both,
        "all_lcb_zero_on_boundary": bn_zero,
        **cm,
        "false_unsafe_rate": cm.get("false_unsafe_rate", float("nan")),
        "balanced_accuracy": cm.get("balanced_accuracy", float("nan")),
    }


def leakage_ok(buf: pd.DataFrame) -> bool:
    if buf.empty:
        return False
    return bool(
        (not bool(buf["current_window_in_buffer"].astype(bool).any()))
        and int(buf["cross_block_score_count"].astype(int).sum()) == 0
        and int(buf["cross_a_score_count"].astype(int).sum()) == 0
        and int(buf["future_score_count"].astype(int).sum()) == 0
        and bool(buf["pass"].astype(bool).all())
    )


def _num(m: Mapping[str, Any], key: str, default: float) -> float:
    v = m.get(key)
    if v is None or (isinstance(v, (float, np.floating)) and not np.isfinite(v)):
        return float(default)
    return float(v)


def primary_usable(m: Mapping[str, Any], *, leak_ok: bool, impl_ok: bool) -> bool:
    return bool(
        impl_ok
        and leak_ok
        and int(_num(m, "n_certified", 0)) >= PRIMARY_CERT_MIN
        and _num(m, "certified_duty_cycle", 0) + NUM_TOL >= DUTY_MIN
        and _num(m, "validity_rate", 0) + NUM_TOL >= VALIDITY_MIN
        and _num(m, "FSR_unsafe", 1) <= FSR_MAX + NUM_TOL
        and _num(m, "balanced_accuracy", 0) + NUM_TOL >= BALANCED_ACC_MIN
        and _num(m, "fraction_C_LCB_zero", 1) < ZERO_FRAC_MAX
        and int(_num(m, "design_on_count", 0)) > 0
    )


def secondary_safe(m: Mapping[str, Any], *, leak_ok: bool) -> bool:
    val = m.get("validity_rate")
    fsr = m.get("FSR_unsafe")
    return bool(
        leak_ok
        and int(m.get("n_certified") or 0) >= SECONDARY_CERT_MIN
        and np.isfinite(val)
        and float(val) + NUM_TOL >= VALIDITY_MIN
        and np.isfinite(fsr)
        and float(fsr) <= FSR_MAX + NUM_TOL
    )


def track_verdict(m: Mapping[str, Any], *, leak_ok: bool, impl_ok: bool) -> str:
    if (not impl_ok) or (not leak_ok):
        return "IMPLEMENTATION_FAILURE"
    n_cert = int(_num(m, "n_certified", 0))
    val = m.get("validity_rate")
    fsr = m.get("FSR_unsafe")
    if n_cert <= 0:
        return "INSUFFICIENT_CERTIFIED_DUTY"
    if (not np.isfinite(val)) or float(val) + NUM_TOL < VALIDITY_MIN:
        return "SAFETY_NOT_ESTABLISHED"
    if np.isfinite(fsr) and float(fsr) > FSR_MAX + NUM_TOL:
        return "SAFETY_NOT_ESTABLISHED"
    ba = m.get("balanced_accuracy")
    zero = _num(m, "fraction_C_LCB_zero", 1)
    duty = _num(m, "certified_duty_cycle", 0)
    design_on = int(_num(m, "design_on_count", 0))
    if zero >= 0.99 or (design_on == 0 and zero >= ZERO_FRAC_MAX):
        return "NO_DISCRIMINATION"
    usable = bool(
        n_cert >= PRIMARY_CERT_MIN
        and duty + NUM_TOL >= DUTY_MIN
        and np.isfinite(ba)
        and float(ba) + NUM_TOL >= BALANCED_ACC_MIN
        and zero < ZERO_FRAC_MAX
        and design_on > 0
    )
    if usable:
        return "FORMAL_CERTIFICATE_USABLE"
    if n_cert < PRIMARY_CERT_MIN or duty + NUM_TOL < DUTY_MIN:
        return "INSUFFICIENT_CERTIFIED_DUTY"
    if design_on == 0 or (np.isfinite(ba) and float(ba) + NUM_TOL < BALANCED_ACC_MIN):
        return "SAFE_BUT_CONSERVATIVE"
    return "SAFE_BUT_CONSERVATIVE"


def uair_false_safe_failure(m: Mapping[str, Any]) -> bool:
    fsr = m.get("FSR_unsafe")
    val = m.get("validity_rate")
    if int(m.get("n_certified") or 0) <= 0:
        return False
    if np.isfinite(fsr) and float(fsr) > FSR_MAX + NUM_TOL:
        return True
    if np.isfinite(val) and float(val) + NUM_TOL < VALIDITY_MIN:
        return True
    return False


def overall_verdict(
    *,
    primary_ok: bool,
    secondary_ok: bool,
    primary_m: Mapping[str, Any],
    secondary_m: Mapping[str, Any],
    impl_ok: bool,
    leak_ok: bool,
    pretest_ok: bool,
) -> str:
    if not pretest_ok:
        return "R1M_INSUFFICIENT_PRETEST_HISTORY"
    if (not impl_ok) or (not leak_ok):
        return "R1M_IMPLEMENTATION_FAILURE"
    p_val = primary_m.get("validity_rate")
    p_fsr = primary_m.get("FSR_unsafe")
    if (
        (np.isfinite(p_val) and float(p_val) + NUM_TOL < VALIDITY_MIN)
        or (np.isfinite(p_fsr) and float(p_fsr) > FSR_MAX + NUM_TOL)
        or uair_false_safe_failure(secondary_m)
    ):
        return "R1M_SAFETY_NOT_ESTABLISHED"
    if primary_ok and secondary_ok:
        return "READY_FOR_SAG_1SEED_FUNCTIONAL_VALIDATION"
    if primary_ok and (not uair_false_safe_failure(secondary_m)):
        return "READY_FOR_LIMITED_SAG_1SEED_VALIDATION"
    p_track = track_verdict(primary_m, leak_ok=leak_ok, impl_ok=impl_ok)
    if p_track in {"SAFE_BUT_CONSERVATIVE", "INSUFFICIENT_CERTIFIED_DUTY", "NO_DISCRIMINATION"}:
        return "R1M_CERTIFICATE_TOO_CONSERVATIVE"
    if p_track == "SAFETY_NOT_ESTABLISHED":
        return "R1M_SAFETY_NOT_ESTABLISHED"
    return "R1M_CERTIFICATE_TOO_CONSERVATIVE"


assert PRIMARY["dataset"] == "sensorscope"
assert SECONDARY["dataset"] == "uair"
assert set(ALLOWED_TRACK)
assert set(ALLOWED_OVERALL)
