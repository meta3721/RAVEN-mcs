"""Auditable SAG certificates from completed-window history only (F_{r-}).

Formal coverage Gate object (R1l): aggregate realized C_t with the
WARMUP/CERTIFIED/RESET conformal LCB. Pairwise simultaneous positive LCBs
remain diagnostic-only (event_count_cp / dynamic_max_residual).
B_tot uses the Theorem-3/4 decomposition.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.stats import beta as beta_dist

Z_ONE_SIDED_95 = 1.6448536269514722
EB_DELTA = 0.05


@dataclass(frozen=True)
class FrozenSagThresholds:
    tau_cov: float = 0.05
    tau_ret: float = 0.05
    tau_ESS: float = 1.0
    tau_clip: float = 0.95
    tau_A: float = 0.35
    tau_safe: float = 4.0
    delta_cal: float = 0.05
    lookback_min: int = 8
    n_min_conformal: int = 19
    lookback_max: int = 32
    quantile_level: float = 0.95
    lambda_group: float = 1.0
    lambda_beta: float = 1.0
    lambda_variance: float = 0.1
    n_groups: int = 4

    def as_dict(self) -> dict[str, float]:
        return asdict(self)

    def gate_thresholds(self) -> dict[str, float]:
        return {
            "tau_cov": float(self.tau_cov),
            "tau_ret": float(self.tau_ret),
            "tau_ESS": float(self.tau_ESS),
            "tau_clip": float(self.tau_clip),
            "tau_A": float(self.tau_A),
            "tau_safe": float(self.tau_safe),
        }


@dataclass
class CertificateContext:
    """F_{r-}/public context. Must not contain current-window R/O/U/A/M."""

    pi_target: dict[tuple[str, str], float] = field(default_factory=dict)
    pi_safe: float | None = None
    b_q: float = 0.0
    n_clients: int | None = None
    n_groups: int | None = None
    source: str = ""
    cov_mode: str = "event_count_cp"
    rolling_L: int | None = None
    regime_certified: bool = True
    had_active_certified_regime: bool = True
    c_hat: float | None = None


@dataclass
class CertificateBundle:
    C_cov_LCB: float
    C_ret_LCB: float
    C_ESS_LCB: float
    C_clip_UCB: float
    delta_A_UCB: float
    Delta_beta_UCB: float
    Delta_M_UCB: float
    Delta_V_UCB: float
    B_M: float
    B_srv_UCB: float
    delta_cal: float
    B_tot_UCB: float
    n_completed: int
    lookback: int
    cold_start: bool
    missing_certificate: bool
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def as_gate_inputs(self) -> dict[str, Any]:
        return {
            "C_cov_LCB": self.C_cov_LCB,
            "C_ret_LCB": self.C_ret_LCB,
            "C_ESS_LCB": self.C_ESS_LCB,
            "C_clip_UCB": self.C_clip_UCB,
            "delta_A_UCB": self.delta_A_UCB,
            "Delta_beta_UCB": self.Delta_beta_UCB,
            "Delta_M_UCB": self.Delta_M_UCB,
            "Delta_V_UCB": self.Delta_V_UCB,
            "B_srv_UCB": self.B_srv_UCB,
            "delta_cal": self.delta_cal,
            "B_tot_UCB": self.B_tot_UCB,
            "n_completed": self.n_completed,
            "lookback": self.lookback,
            "cold_start": self.cold_start,
            "missing_certificate": self.missing_certificate,
        }


def _finite_list(values: Sequence[Any]) -> list[float]:
    out: list[float] = []
    for item in values:
        try:
            x = float(item)
        except (TypeError, ValueError):
            continue
        if np.isfinite(x):
            out.append(x)
    return out


def mean_lcb(values: Sequence[Any], z: float = Z_ONE_SIDED_95) -> float:
    xs = _finite_list(values)
    if not xs:
        return float("nan")
    arr = np.asarray(xs, dtype=np.float64)
    mean = float(arr.mean())
    if arr.size == 1:
        return mean
    se = float(arr.std(ddof=1) / np.sqrt(arr.size))
    return float(mean - z * se)


def mean_ucb(values: Sequence[Any], z: float = Z_ONE_SIDED_95) -> float:
    xs = _finite_list(values)
    if not xs:
        return float("nan")
    arr = np.asarray(xs, dtype=np.float64)
    mean = float(arr.mean())
    if arr.size == 1:
        return mean
    se = float(arr.std(ddof=1) / np.sqrt(arr.size))
    return float(mean + z * se)


def conformal_upper_quantile(values: Sequence[Any], level: float) -> float:
    """Finite-sample order-statistic UCB: k = ceil((n+1) q)."""
    xs = sorted(_finite_list(values))
    if not xs:
        return float("nan")
    n = len(xs)
    k = min(n, max(1, int(np.ceil((n + 1) * float(level)))))
    return float(xs[k - 1])


def rolling_quantile(values: Sequence[Any], level: float) -> float:
    return conformal_upper_quantile(values, level)


def binary_ucb(values: Sequence[Any], z: float = Z_ONE_SIDED_95) -> float:
    xs = _finite_list(values)
    if not xs:
        return float("nan")
    arr = np.asarray(xs, dtype=np.float64)
    p = float(np.clip(arr.mean(), 0.0, 1.0))
    n = float(arr.size)
    se = float(np.sqrt(p * (1.0 - p) / n))
    return float(min(1.0, p + z * se + 1.0 / n))


def empirical_bernstein_lcb(
    values: Sequence[Any],
    *,
    delta: float = EB_DELTA,
    radius: float = 1.0,
) -> float:
    """One-sided empirical-Bernstein LCB on [0, radius] completed-window masses."""
    xs = _finite_list(values)
    if not xs:
        return float("nan")
    arr = np.asarray(xs, dtype=np.float64)
    n = float(arr.size)
    mean = float(arr.mean())
    if arr.size == 1:
        return float(max(0.0, mean))
    var = float(arr.var(ddof=1))
    logt = float(np.log(1.0 / float(delta)))
    return float(
        max(
            0.0,
            mean
            - np.sqrt(max(2.0 * var * logt / n, 0.0))
            - 3.0 * float(radius) * logt / n,
        )
    )


def b_tot_from_parts(
    b_srv: float,
    delta_a: float,
    delta_cal: float,
) -> float:
    """B_tot = B_srv + 2 δ_A + 2 δ_cal (Spec v1.2)."""
    return float(b_srv) + 2.0 * float(delta_a) + 2.0 * float(delta_cal)


def pair_key(item: Any) -> tuple[str, str]:
    if isinstance(item, (tuple, list)) and len(item) >= 2:
        return str(item[0]), str(item[1])
    if isinstance(item, str) and "|" in item:
        left, right = item.split("|", 1)
        return left, right
    raise TypeError(f"cannot parse pair key: {item!r}")


def encode_pair(key: tuple[str, str]) -> str:
    return f"{key[0]}|{key[1]}"


def opportunity_mass_map(row: Mapping[str, Any]) -> dict[tuple[str, str], float]:
    raw = row.get("opp_mass_by_pair") or {}
    out: dict[tuple[str, str], float] = {}
    if not isinstance(raw, Mapping):
        return out
    for key, value in raw.items():
        try:
            out[pair_key(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def opportunity_count_map(row: Mapping[str, Any]) -> dict[tuple[str, str], float]:
    raw = row.get("opp_count_by_pair") or {}
    out: dict[tuple[str, str], float] = {}
    if not isinstance(raw, Mapping):
        return out
    for key, value in raw.items():
        try:
            out[pair_key(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def clopper_pearson_lcb(x: float, n: float, delta: float) -> float:
    """One-sided Clopper–Pearson lower bound for a binomial proportion.

    LCB = 0 if x<=0; otherwise the δ-quantile of Beta(x, n-x+1).
    """
    try:
        xx = float(x)
        nn = float(n)
        dd = float(delta)
    except (TypeError, ValueError):
        return float("nan")
    if not (np.isfinite(xx) and np.isfinite(nn) and np.isfinite(dd)):
        return float("nan")
    if nn <= 0.0 or xx < 0.0 or xx > nn or dd <= 0.0 or dd >= 1.0:
        return 0.0 if nn > 0.0 and xx <= 0.0 and 0.0 < dd < 1.0 else float("nan")
    if xx <= 0.0:
        return 0.0
    return float(max(0.0, min(1.0, beta_dist.ppf(dd, xx, nn - xx + 1.0))))


def lower_pi_opp_event_count_by_pair(
    history: Sequence[Mapping[str, Any]],
    pairs: Sequence[tuple[str, str]],
    *,
    delta: float,
    bonferroni: bool = True,
) -> dict[tuple[str, str], dict[str, float]]:
    """F_{r-}-measurable CP LCB from completed-window event counts (all t<r)."""
    counts: dict[tuple[str, str], float] = {key: 0.0 for key in pairs}
    total = 0.0
    n_windows = 0
    for row in history:
        cmap = opportunity_count_map(row)
        win_total = row.get("opp_event_total")
        try:
            win_n = float(win_total) if win_total is not None else float(sum(cmap.values()))
        except (TypeError, ValueError):
            win_n = float(sum(cmap.values()))
        if win_n < 0 or not np.isfinite(win_n):
            continue
        total += win_n
        n_windows += 1
        for key in pairs:
            counts[key] += float(cmap.get(key, 0.0))
    m = max(1, len(pairs))
    delta_pair = (float(delta) / float(m)) if bonferroni else float(delta)
    out: dict[tuple[str, str], dict[str, float]] = {}
    for key in pairs:
        x = float(counts[key])
        hat = (x / total) if total > 0.0 else float("nan")
        lcb = clopper_pearson_lcb(x, total, delta_pair)
        out[key] = {
            "pi_hat_opp": hat,
            "lower_pi_opp": lcb,
            "n": float(total),
            "count": x,
            "n_windows": float(n_windows),
            "delta_pair": float(delta_pair),
            "m_target_positive": float(m),
        }
    return out


def pair_presence_distribution(
    pairs: Sequence[tuple[str, str]],
) -> dict[tuple[str, str], float]:
    """DIAGNOSTIC ONLY: unique-pair uniform. Must not enter SAG C_cov."""
    uniq = sorted({(str(k), str(s)) for k, s in pairs})
    if not uniq:
        return {}
    mass = 1.0 / float(len(uniq))
    return {key: mass for key in uniq}


def window_opportunity_event_counts(
    pairs: Sequence[tuple[str, str]],
    weights: Sequence[float] | None = None,
) -> dict[tuple[str, str], float]:
    """Completed-window opportunity-event counts/mass N^{opp}_{k,s}."""
    counts: dict[tuple[str, str], float] = {}
    if weights is None:
        for client, stratum in pairs:
            key = (str(client), str(stratum))
            counts[key] = counts.get(key, 0.0) + 1.0
        return counts
    if len(weights) != len(pairs):
        raise ValueError("opportunity-event weights must align with events")
    for (client, stratum), weight in zip(pairs, weights):
        key = (str(client), str(stratum))
        counts[key] = counts.get(key, 0.0) + float(weight)
    return counts


def window_opportunity_masses(
    pairs: Sequence[tuple[str, str]],
    weights: Sequence[float] | None = None,
) -> dict[tuple[str, str], float]:
    """Completed-window π^{opp}_{k,s} from event counts/mass, not unique-pair presence."""
    counts = window_opportunity_event_counts(pairs, weights)
    total = float(sum(counts.values()))
    if total <= 0.0:
        return {}
    return {key: float(val) / total for key, val in counts.items()}


def lower_pi_opp_by_pair(
    history: Sequence[Mapping[str, Any]],
    pairs: Sequence[tuple[str, str]],
) -> dict[tuple[str, str], dict[str, float]]:
    """F_{r-}-measurable EB LCB on completed-window opportunity masses."""
    out: dict[tuple[str, str], dict[str, float]] = {}
    series: dict[tuple[str, str], list[float]] = {key: [] for key in pairs}
    for row in history:
        masses = opportunity_mass_map(row)
        for key in pairs:
            series[key].append(float(masses.get(key, 0.0)))
    for key, values in series.items():
        hat = float(np.mean(values)) if values else float("nan")
        lcb = empirical_bernstein_lcb(values)
        out[key] = {"pi_hat_opp": hat, "lower_pi_opp": lcb, "n": float(len(values))}
    return out


def c_cov_from_opportunity_lcb(
    pi_target: Mapping[tuple[str, str], float],
    lowers: Mapping[tuple[str, str], Mapping[str, float]],
    pi_safe: float,
) -> dict[str, Any]:
    certified = 0.0
    total = 0.0
    failures: list[dict[str, Any]] = []
    n_pos = 0
    for key, mass in pi_target.items():
        w = float(mass)
        if w <= 0.0:
            continue
        n_pos += 1
        total += w
        rec = lowers.get((str(key[0]), str(key[1])), {})
        lower = rec.get("lower_pi_opp", float("nan"))
        try:
            ok = float(lower) >= float(pi_safe)
        except (TypeError, ValueError):
            ok = False
        if ok:
            certified += w
        else:
            failures.append(
                {
                    "client": str(key[0]),
                    "stratum": str(key[1]),
                    "pi_tar": w,
                    "pi_hat_opp": rec.get("pi_hat_opp"),
                    "lower_pi_opp": lower,
                }
            )
    c_cov = float(certified / total) if total > 0 else float("nan")
    failures.sort(key=lambda row: float(row.get("pi_tar") or 0.0), reverse=True)
    return {
        "C_cov_LCB": c_cov,
        "target_mass_certified": certified,
        "target_mass_total": total,
        "number_target_positive_pairs": n_pos,
        "pi_safe": float(pi_safe),
        "top_failures": failures[:8],
    }


def provisional_pi_safe_from_public_opp(
    pi_target: Mapping[tuple[str, str], float],
    pi_opp_joint: Mapping[tuple[str, str], float],
    *,
    quantile: float = 0.10,
) -> dict[str, Any]:
    masses = [
        float(pi_opp_joint.get(key, 0.0))
        for key, w in pi_target.items()
        if float(w) > 0.0
    ]
    masses = [x for x in masses if np.isfinite(x) and x > 0.0]
    candidates: dict[str, float] = {}
    for name, q in (("q05", 0.05), ("q10", 0.10), ("q25", 0.25)):
        candidates[name] = float(np.quantile(masses, q)) if masses else float("nan")
    chosen = candidates.get(
        {0.05: "q05", 0.10: "q10", 0.25: "q25"}.get(float(quantile), "q10"),
        float("nan"),
    )
    return {
        "pi_safe": chosen,
        "quantile": float(quantile),
        "n_positive_target_pairs": len(masses),
        "candidates": candidates,
        "source": "public_pi_opp_joint_quantile_on_target_positive_pairs",
        "status": "PI_SAFE_REQUIRES_FREEZE_DECISION",
        "frozen": False,
    }


def b_tot_decomposition(
    *,
    delta_beta_ucb: float,
    delta_m_ucb: float,
    delta_v_ucb: float,
    b_m_pre: float,
    b_q: float,
    delta_a_ucb: float,
    delta_cal: float,
    n_groups: int,
    lambda_group: float,
    lambda_beta: float,
    lambda_variance: float,
) -> dict[str, float]:
    term_beta = float(delta_beta_ucb)
    term_m = (
        (float(b_q) + float(lambda_group) * (2.0 * float(b_m_pre) + 1.0))
        / float(lambda_beta)
        * float(delta_m_ucb)
    )
    term_v = float(lambda_variance) / float(lambda_beta) * float(delta_v_ucb)
    d_alpha = term_beta + term_m + term_v
    service_direct = float(delta_m_ucb)
    service_alpha = float(b_m_pre) * d_alpha
    b_srv = float(np.sqrt(max(int(n_groups), 1))) * (service_direct + service_alpha)
    active = 2.0 * float(delta_a_ucb)
    cal = 2.0 * float(delta_cal)
    return {
        "B_M_pre": float(b_m_pre),
        "B_Q": float(b_q),
        "Delta_beta_UCB": float(delta_beta_ucb),
        "Delta_M_UCB": float(delta_m_ucb),
        "Delta_V_UCB": float(delta_v_ucb),
        "term_beta": float(term_beta),
        "term_M": float(term_m),
        "term_V": float(term_v),
        "D_alpha_UCB": float(d_alpha),
        "service_direct_M_term": float(service_direct),
        "service_alpha_term": float(service_alpha),
        "B_srv_UCB": float(b_srv),
        "active_set_term": float(active),
        "cal_failure_term": float(cal),
        "B_tot_UCB": float(b_tot_from_parts(b_srv, delta_a_ucb, delta_cal)),
    }


def compute_certificates(
    history: Sequence[Mapping[str, Any]],
    thresholds: FrozenSagThresholds,
    context: CertificateContext | None = None,
) -> CertificateBundle:
    """Build F_{r-}-measurable certificates from completed windows only."""
    ctx = context or CertificateContext()
    n = len(history)
    lookback = min(int(thresholds.lookback_max), n)
    recent = list(history[-lookback:]) if lookback else []
    cold = n < int(thresholds.lookback_min)
    delta_cal = float(thresholds.delta_cal)

    target_pairs = [
        (str(k[0]), str(k[1]))
        for k, w in ctx.pi_target.items()
        if float(w) > 0.0
    ]
    has_counts = any(opportunity_count_map(row) or row.get("opp_event_total") for row in history)
    if str(ctx.cov_mode) == "aggregate_stable_regime":
        from raven_mcs.sag.aggregate_certificate import formal_aggregate_coverage

        agg = formal_aggregate_coverage(
            history,
            pi_target=ctx.pi_target,
            pi_safe=ctx.pi_safe,
            regime_certified=bool(ctx.regime_certified),
            had_active_certified_regime=bool(ctx.had_active_certified_regime),
            c_hat=ctx.c_hat,
            alpha=delta_cal,
            tau_cov=float(thresholds.tau_cov),
        )
        cov_info = dict(agg)
        cov_lcb = float(agg["C_LCB"])
        lowers = {}
        if target_pairs and ctx.pi_safe is not None and has_counts:
            diag_lowers = lower_pi_opp_event_count_by_pair(
                history, target_pairs, delta=delta_cal, bonferroni=True,
            )
            pairwise_diag = c_cov_from_opportunity_lcb(ctx.pi_target, diag_lowers, float(ctx.pi_safe))
            cov_info["pairwise_diagnostic_C_cov_LCB"] = pairwise_diag.get("C_cov_LCB")
            cov_info["pairwise_formal_core"] = False
    elif str(ctx.cov_mode) == "dynamic_max_residual" and target_pairs and ctx.pi_safe is not None:
        from raven_mcs.sag.dynamic_cov import dynamic_lower_pi_opp

        dyn = dynamic_lower_pi_opp(
            history,
            target_pairs,
            lookback=int(ctx.rolling_L or thresholds.lookback_min),
            delta=delta_cal,
            min_calib=int(thresholds.lookback_min),
        )
        lowers = dyn["lowers"]
        if dyn["cold_start"]:
            cov_info = {
                "C_cov_LCB": float("nan"),
                "target_mass_certified": float("nan"),
                "number_target_positive_pairs": len(target_pairs),
                "pi_safe": ctx.pi_safe,
                "top_failures": [],
                "lower_pi_opp_method": dyn["method"],
                "C_cov_history_policy": "rolling_plus_prior_window_max_residual",
                "q_max_residual": dyn.get("q"),
                "n_calib": dyn.get("n_calib"),
            }
            cov_lcb = float("nan")
        else:
            cov_info = c_cov_from_opportunity_lcb(ctx.pi_target, lowers, float(ctx.pi_safe))
            cov_lcb = float(cov_info["C_cov_LCB"])
            cov_info["lower_pi_opp_method"] = dyn["method"]
            cov_info["C_cov_history_policy"] = "rolling_plus_prior_window_max_residual"
            cov_info["q_max_residual"] = dyn.get("q")
            cov_info["n_calib"] = dyn.get("n_calib")
    elif target_pairs and ctx.pi_safe is not None and has_counts:
        lowers = lower_pi_opp_event_count_by_pair(
            history, target_pairs, delta=delta_cal, bonferroni=True,
        )
        cov_info = c_cov_from_opportunity_lcb(ctx.pi_target, lowers, float(ctx.pi_safe))
        cov_lcb = float(cov_info["C_cov_LCB"])
        old_lowers = lower_pi_opp_by_pair(recent, target_pairs)
        old_cov = c_cov_from_opportunity_lcb(ctx.pi_target, old_lowers, float(ctx.pi_safe))
        cov_info["C_cov_LCB_old_eb"] = old_cov["C_cov_LCB"]
        cov_info["lower_pi_opp_method"] = "clopper_pearson_event_count_bonferroni"
        cov_info["C_cov_history_policy"] = "all_completed_windows_t_lt_r"
        cov_info["delta_family"] = delta_cal
        if lowers:
            sample = next(iter(lowers.values()))
            cov_info["delta_pair"] = sample.get("delta_pair")
            cov_info["completed_event_total"] = sample.get("n")
            cov_info["n_count_windows"] = sample.get("n_windows")
    elif target_pairs and ctx.pi_safe is not None:
        # Fail-closed: do not use the degenerate window-mass EB as the main certifier.
        lowers = {}
        cov_info = {
            "C_cov_LCB": float("nan"),
            "target_mass_certified": float("nan"),
            "number_target_positive_pairs": len(target_pairs),
            "pi_safe": ctx.pi_safe,
            "top_failures": [],
            "lower_pi_opp_method": "missing_event_counts_fail_closed",
        }
        cov_lcb = float("nan")
    else:
        lowers = {}
        cov_info = {
            "C_cov_LCB": float("nan"),
            "target_mass_certified": float("nan"),
            "number_target_positive_pairs": 0,
            "pi_safe": ctx.pi_safe,
            "top_failures": [],
        }
        cov_lcb = float("nan")

    ret_lcb = mean_lcb([row.get("realized_C_ret") for row in recent])
    ess_lcb = mean_lcb([row.get("realized_C_ESS") for row in recent])
    clip_ucb = mean_ucb([row.get("realized_C_clip") for row in recent])
    delta_a_ucb = binary_ucb([row.get("active_set_mismatch") for row in recent])
    d_beta = conformal_upper_quantile(
        [row.get("Delta_beta") for row in recent], thresholds.quantile_level,
    )
    d_m = conformal_upper_quantile(
        [row.get("Delta_M") for row in recent], thresholds.quantile_level,
    )
    d_v = conformal_upper_quantile(
        [row.get("Delta_V") for row in recent], thresholds.quantile_level,
    )
    n_clients = ctx.n_clients
    if n_clients is None or int(n_clients) <= 0:
        b_m = float("nan")
        bm_note = "NO_LEGAL_TIGHTER_BM_BOUND_FOUND"
    else:
        b_m = float(np.sqrt(float(n_clients)))
        bm_note = "sqrt_K_prewindow_client_roster"
    n_g = int(ctx.n_groups or thresholds.n_groups or 1)
    parts = (
        b_tot_decomposition(
            delta_beta_ucb=d_beta,
            delta_m_ucb=d_m,
            delta_v_ucb=d_v,
            b_m_pre=b_m,
            b_q=float(ctx.b_q),
            delta_a_ucb=delta_a_ucb,
            delta_cal=delta_cal,
            n_groups=n_g,
            lambda_group=float(thresholds.lambda_group),
            lambda_beta=float(thresholds.lambda_beta),
            lambda_variance=float(thresholds.lambda_variance),
        )
        if np.isfinite(d_beta) and np.isfinite(d_m) and np.isfinite(d_v)
        and np.isfinite(b_m) and np.isfinite(delta_a_ucb)
        else None
    )
    b_srv = float(parts["B_srv_UCB"]) if parts else float("nan")
    b_tot = float(parts["B_tot_UCB"]) if parts else float("nan")
    missing = cold or any(
        not np.isfinite(x)
        for x in (cov_lcb, ret_lcb, ess_lcb, clip_ucb, delta_a_ucb, b_tot)
    )
    diagnostics = {
        **cov_info,
        "lower_pi_opp_method": cov_info.get(
            "lower_pi_opp_method", "clopper_pearson_event_count_bonferroni"
        ),
        "B_M_bound_rule": bm_note,
        "n_clients_prewindow": n_clients,
        "pair_lcb_sample": {
            encode_pair(k): v for k, v in list(lowers.items())[:6]
        },
    }
    if parts:
        diagnostics.update(parts)
    return CertificateBundle(
        C_cov_LCB=float(cov_lcb),
        C_ret_LCB=float(ret_lcb),
        C_ESS_LCB=float(ess_lcb),
        C_clip_UCB=float(clip_ucb),
        delta_A_UCB=float(delta_a_ucb),
        Delta_beta_UCB=float(d_beta),
        Delta_M_UCB=float(d_m),
        Delta_V_UCB=float(d_v),
        B_M=float(b_m),
        B_srv_UCB=float(b_srv),
        delta_cal=delta_cal,
        B_tot_UCB=float(b_tot),
        n_completed=n,
        lookback=lookback,
        cold_start=cold,
        missing_certificate=bool(missing),
        diagnostics=diagnostics,
    )
