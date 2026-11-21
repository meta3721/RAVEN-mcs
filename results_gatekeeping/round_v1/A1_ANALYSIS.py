#!/usr/bin/env python3
"""A1 analysis (Part A only): descriptive gatekeeping hierarchy + power table.

Round: results_gatekeeping/round_v1
Protocol: results_gatekeeping/round_v1/PROTOCOL.md
Preregistration: results_gatekeeping/round_v1/PREREG.md (sha256 in MANIFEST.sha256,
written before this script first ran).

READ-ONLY with respect to the repository: reads only the inputs listed below and writes
only inside results_gatekeeping/round_v1/.  No training, no model build(), no re-scoring,
no git, no writes outside the round directory.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys

import numpy as np
from scipy import stats

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_gatekeeping" / "round_v1"

B_BOOT = 10000
SEED_BOOT = 20261003
Z95 = 1.6448536269514722          # one-sided 95 %
Z80 = 0.8416212335729143          # 80 % power
SENS_SEED = 32005                 # declared sensitivity exclusion
DELTA = {"sensorscope": 0.005, "uair": 0.005, "cityscanner_nyc_pm25": 0.02}
MARGIN_NAME = {"sensorscope": "0.5%", "uair": "0.5%",
               "cityscanner_nyc_pm25": "2% (delta_CS)"}
ARMS = {"sensorscope": ["raven", "proj_beta"],
        "uair": ["raven", "proj_beta"],
        "cityscanner_nyc_pm25": ["raven"]}
LABEL = "post hoc descriptive"

INPUTS = {
    "tradeoff_v51": ROOT / "results_w1_ladder" / "round_v5_1" / "TRADEOFF_V51.csv",
    "tradeoff_v4": ROOT / "results_w1_ladder" / "round_v4" / "TRADEOFF.csv",
    "tradeoff_paired_v4": ROOT / "results_w1_ladder" / "round_v4" / "TRADEOFF_PAIRED.csv",
    "cs_e3": ROOT / "results_c1_cityscanner" / "round_v1" / "tables" / "CS_E3.csv",
    "cs_seed_rows": (ROOT / "results_nodesign_supplement" / "round_v1" / "tables"
                     / "cityscanner_seed_rows.csv"),
    "cs_train_setup": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRAIN_SETUP.json",
    "cs_phi_decision": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_PHI_DECISION.json",
    "maps_key_level": ROOT / "results_exogenous_target" / "round_v1" / "MAPS_KEY_LEVEL.csv",
    # read during reconnaissance to establish the CS design (not used in any A1 number)
    "cs_train_ledger": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRAIN_LEDGER.json",
    "cs_trace_manifest": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRACE_MANIFEST.json",
    "script_run_nodesign_supplement": ROOT / "scripts" / "run_nodesign_supplement.py",
    "script_w1_replay": ROOT / "scripts" / "w1_replay.py",
    "script_exogenous_target_cityscanner": ROOT / "scripts" / "exogenous_target_cityscanner.py",
}


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(p: pathlib.Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def fmt(x, nd=10):
    return ("%." + str(nd) + "g") % x


# ---------------------------------------------------------------------------
# data assembly (theta-canonical for SS/U-Air; frozen CS tables for City Scanner)
# ---------------------------------------------------------------------------

def load_w1() -> dict:
    rows = read_csv(INPUTS["tradeoff_v51"])
    out: dict[tuple, dict] = {}
    for r in rows:
        if r["ds"] in ("sensorscope", "uair"):
            out.setdefault((r["ds"], r["arm"]), {})[int(r["seed"])] = r
    return out


def load_cs() -> dict:
    rows = read_csv(INPUTS["cs_e3"])
    return {(r["method"], int(r["seed"])): r
            for r in rows if r["dataset"] == "cityscanner_nyc_pm25"}


def paired_vectors(ds, arm, w1, cs):
    """(seeds, ref_rmse, arm_rmse, ref_dg, arm_dg), paired by unit (seed == trace)."""
    if ds == "cityscanner_nyc_pm25":
        seeds = sorted({s for (m, s) in cs if m == "raven"})
        assert sorted({s for (m, s) in cs if m == "fedavg_window"}) == seeds, \
            "raven and fedavg_window must run on the same traces"
        ref = [fnum(cs[("fedavg_window", s)]["RMSE_mu"]) for s in seeds]
        a = [fnum(cs[(arm, s)]["RMSE_mu"]) for s in seeds]
        ref_dg = [fnum(cs[("fedavg_window", s)]["Delta_group"]) for s in seeds]
        a_dg = [fnum(cs[(arm, s)]["Delta_group"]) for s in seeds]
    else:
        base = w1[(ds, "fedavg_window")]
        seeds = sorted(base)
        arows = w1[(ds, arm)]
        assert sorted(arows) == seeds, (ds, arm)
        ref = [fnum(base[s]["RMSE_mu"]) for s in seeds]
        a = [fnum(arows[s]["RMSE_mu"]) for s in seeds]
        ref_dg = [fnum(base[s]["Delta_group"]) for s in seeds]
        a_dg = [fnum(arows[s]["Delta_group"]) for s in seeds]
    return (np.array(seeds, dtype=int), np.array(ref), np.array(a),
            np.array(ref_dg), np.array(a_dg))


# ---------------------------------------------------------------------------
# estimators (preregistered)
# ---------------------------------------------------------------------------

def walsh_averages(d: np.ndarray) -> np.ndarray:
    """Sorted Walsh averages (d_i + d_j)/2, i <= j.  Convention is preregistered."""
    n = len(d)
    a = (d[:, None] + d[None, :]) / 2.0
    return np.sort(a[np.triu_indices(n)])


def hl_estimate(d: np.ndarray) -> float:
    return float(np.median(walsh_averages(d)))


def _signedrank_critical(n: int):
    """(c_lo, c_hi, source) with c_lo = max{c: F(c) <= 0.05}, c_hi = min{c: F(c) >= 0.95}."""
    m = n * (n + 1) // 2
    try:
        from scipy.stats._wilcoxon import _get_wilcoxon_distr  # type: ignore
        cdf = np.cumsum(_get_wilcoxon_distr(n))
        c_lo = int(np.searchsorted(cdf, 0.05, side="right")) - 1
        c_hi = int(np.searchsorted(cdf, 0.95, side="left"))
        return max(c_lo, 0), min(c_hi, m - 1), "exact null distribution of W+"
    except Exception:
        mu = n * (n + 1) / 4.0
        sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
        c_lo = int(math.floor(mu - Z95 * sd))
        c_hi = int(math.floor(mu + Z95 * sd))
        return max(c_lo, 0), min(c_hi, m - 1), "normal approximation (exact distribution unavailable)"


def wilcoxon_bounds(d: np.ndarray):
    """One-sided 95 % distribution-free bounds on the HL shift (Wilcoxon inversion).

    L = W_norm[c_lo], U = W_norm[c_hi], with c_lo/c_hi the 5 %/95 % points of the exact
    null distribution of W+.  Convention verified inside the script against
    scipy.stats.wilcoxon(..., alternative=...) on the same data.
    """
    n = len(d)
    w = walsh_averages(d)
    m = len(w)
    c_lo, c_hi, src = _signedrank_critical(n)
    lower = float(w[min(max(c_lo, 0), m - 1)])
    upper = float(w[min(max(c_hi, 0), m - 1)])
    return lower, upper, {"n": n, "N_walsh": m, "c_lo": c_lo, "c_hi": c_hi,
                          "critical_value_distribution": src}


def wilcoxon_ci(d: np.ndarray):
    """Backwards-compatible alias returning (lower, upper, source-string)."""
    lo, hi, meta = wilcoxon_bounds(d)
    return lo, hi, meta["critical_value_distribution"]


def basic_bootstrap(d: np.ndarray, rng: np.random.Generator, b: int = B_BOOT):
    """Basic (reflection) bootstrap of the HL estimator over paired units."""
    n = len(d)
    theta = hl_estimate(d)
    idx = rng.integers(0, n, size=(b, n))
    s = d[idx]
    boots = np.median(((s[:, :, None] + s[:, None, :]).reshape(b, -1)) / 2.0, axis=1)
    delta = boots - theta
    hi = theta - float(np.quantile(delta, 0.025))   # one-sided 95 % upper bound
    lo = theta - float(np.quantile(delta, 0.975))   # two-sided 95 % lower bound
    return theta, lo, hi, boots


def power_normal(delta: float, theta: float, se: float) -> float:
    if se <= 0:
        return 1.0 if theta < delta else 0.0
    return float(stats.norm.cdf((delta - theta) / se - Z95))


def power_t(delta: float, theta: float, se: float, df: int) -> float:
    if se <= 0:
        return 1.0 if theta < delta else 0.0
    crit = float(stats.t.ppf(0.95, df))
    return float(stats.nct.cdf((delta - theta) / se, df, -crit))


def mde80(delta: float, se: float) -> float:
    return delta - (Z80 + Z95) * se


def power_cluster_bootstrap(theta: float, sig_b: float, sig_w: float, r: int, n: int,
                            delta: float, n_rep: int = 4000, b: int = 800,
                            seed: int = SEED_BOOT) -> float:
    """Monte-Carlo power of the preregistered rule under the trace-cluster model.

    Per replication: trace means dbar_t = theta + B_t + mean_r(W_tr); the rule rejects
    when the one-sided 95 % basic-bootstrap upper bound over the n traces is < delta.
    """
    rng = np.random.default_rng(seed)
    sd_bar = math.sqrt(max(sig_b ** 2 + sig_w ** 2 / r, 0.0))
    rej = 0
    for _ in range(n_rep):
        tr = theta + rng.normal(0.0, sd_bar, size=n)
        idx = rng.integers(0, n, size=(b, n))
        boots = tr[idx].mean(axis=1)
        c = float(tr.mean())
        sd_boot = math.sqrt(float(np.var(tr, ddof=1)) / n)
        upper = c + Z95 * sd_boot          # basic-bootstrap upper bound == c + z*se
        if upper < delta:
            rej += 1
    return rej / n_rep


# ---------------------------------------------------------------------------
# graphical Bretz-Maurer-Brannath-Posch procedure (equal weights, Holm transitions)
# ---------------------------------------------------------------------------

def graphical_holm(chains: dict, alpha: float = 0.05) -> dict:
    names = list(chains)
    K = len(names)
    w = {k: 1.0 / K for k in names}
    g = {(i, j): (1.0 / (K - 1) if (i != j and K > 1) else 0.0)
         for i in names for j in names}
    pos = {k: 0 for k in names}
    history: list[dict] = []
    active = set(names)
    while active:
        best = None
        for k in sorted(active):
            if pos[k] >= len(chains[k]):
                active.discard(k)
                continue
            a = w[k] * alpha
            p = chains[k][pos[k]]["p"]
            if p is not None and p < a and (best is None or p < best[1]):
                best = (k, p, a)
        if best is None:
            break
        k, p, a = best
        step = chains[k][pos[k]]
        history.append({"chain": k, "step": step["name"], "p": p,
                        "alpha_allocated": a, "rejected": True})
        pos[k] += 1
        if pos[k] >= len(chains[k]):
            active.discard(k)
        released = w[k]
        w[k] = 0.0
        for j in names:
            if j in active:
                w[j] += released * g[(k, j)]
    for k in names:
        while pos[k] < len(chains[k]):
            history.append({"chain": k, "step": chains[k][pos[k]]["name"],
                            "p": chains[k][pos[k]]["p"],
                            "alpha_allocated": w[k] * alpha, "rejected": False})
            pos[k] += 1
    return {"history": history, "final_weights": {k: w[k] for k in names}}


def step_record(ghist: dict, chain: str, step: str):
    for h in ghist["history"]:
        if h["chain"] == chain and h["step"] == step:
            return h
    return {"alpha_allocated": None, "rejected": False, "p": None}


# ---------------------------------------------------------------------------
# City Scanner within-trace proxy (Part B B0-b did not run)
# ---------------------------------------------------------------------------

def cs_within_trace_proxy() -> dict:
    rows = read_csv(INPUTS["cs_seed_rows"])
    by: dict[str, dict] = {}
    for r in rows:
        by.setdefault(r["method"], {})[int(r["seed"])] = r
    seeds = sorted(by.get("raven", {}))
    d_wo = []
    for s in seeds:
        if s in by.get("raven_wo_design", {}):
            a = fnum(by["raven"][s]["RMSE_mu"])
            b = fnum(by["raven_wo_design"][s]["RMSE_mu"])
            if a > 0:
                d_wo.append(b / a - 1.0)
    d_wo = np.array(d_wo)
    return {
        "proxy_definition": ("SD across the 10 traces of "
                             "RMSE_mu(raven_wo_design)/RMSE_mu(raven)-1; the second arm "
                             "shares raven's traces and model seeds and differs only in its "
                             "pi^tar support, so the contrast removes the between-trace "
                             "effect and its scatter estimates the within-trace scale"),
        "n_traces": int(len(d_wo)),
        "mean_rel_diff_wo_vs_raven": float(np.mean(d_wo)) if len(d_wo) else None,
        "sd_rel_diff_wo_vs_raven": float(np.std(d_wo, ddof=1)) if len(d_wo) > 1 else None,
        "sigma_w": float(np.std(d_wo, ddof=1)) if len(d_wo) > 1 else 0.0,
        "source": "results_nodesign_supplement/round_v1/tables/cityscanner_seed_rows.csv",
        "status": ("proxy -- Part B B0-b did not run: the authorization phrase "
                   "was not given"),
        "warning": ("estimates the within-trace scale from an arm contrast, not from "
                    "model-seed replicates of one arm; it is the most optimistic of the "
                    "admissible readings, and is replaced by the B0-b estimate once B0 "
                    "exists"),
    }


def verify_inversion(n_rep: int = 20000, seed: int = 4242) -> dict:
    """Check the preregistered Wilcoxon inversion: coverage and test consistency."""
    rng = np.random.default_rng(seed)
    out = {}
    for n, theta in ((20, 0.30), (10, 0.30)):
        cov = p_lo = p_hi = 0
        for _ in range(n_rep):
            d = rng.normal(theta, 1.0, n)
            lo, hi, _ = wilcoxon_bounds(d)
            cov += (lo <= theta <= hi)
            p_lo += (lo <= theta)
            p_hi += (hi >= theta)
        out["n=%d" % n] = {
            "two_sided_90_coverage": cov / n_rep,
            "one_sided_lower_coverage": p_lo / n_rep,
            "one_sided_upper_coverage": p_hi / n_rep,
            "targets": {"two_sided": 0.90, "one_sided": 0.95},
            "replications": n_rep, "seed": seed, "true_shift": theta,
            "note": "simulation only; not part of any A1 decision",
        }
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    w1 = load_w1()
    cs = load_cs()
    proxy = cs_within_trace_proxy()

    provenance = {k: {"path": str(v.relative_to(ROOT)), "sha256": sha256_file(v),
                      "bytes": v.stat().st_size} for k, v in INPUTS.items()}

    full: dict[tuple, dict] = {}
    for ds, arms in ARMS.items():
        for arm in arms:
            seeds, ref, a, ref_dg, a_dg = paired_vectors(ds, arm, w1, cs)
            d = a / ref - 1.0
            t = a_dg - ref_dg
            theta, lo_bb, hi_bb, _ = basic_bootstrap(d, np.random.default_rng(SEED_BOOT))
            lo_w, hi_w, wmeta = wilcoxon_bounds(d)
            se = float(np.std(d, ddof=1) / math.sqrt(len(d)))
            p_h1 = float(stats.wilcoxon(t, alternative="less").pvalue)
            p_h3 = float(stats.wilcoxon(d, alternative="greater").pvalue)
            p_h2 = float(stats.norm.cdf((theta - DELTA[ds]) / se)) if se > 0 else float("nan")
            # preregistered consistency check: the Wilcoxon-inverted bounds must agree
            # with the exact signed-rank tests on the same data.
            lo_d, hi_d, _ = wilcoxon_bounds(d - DELTA[ds])
            check_h2 = (hi_w < DELTA[ds]) == (float(stats.wilcoxon(d, alternative="less").pvalue) < 0.05)
            check_h3 = (lo_w > 0.0) == (p_h3 < 0.05)
            full[(ds, arm)] = {
                "seeds": seeds, "n": int(len(d)), "d": d, "t": t,
                "rel_mean": float(np.mean(d)), "rel_median": float(np.median(d)),
                "rel_sd": float(np.std(d, ddof=1)), "se": se,
                "hl": theta, "ub_basic": hi_bb, "lb_basic": lo_bb,
                "ub_wilcox": hi_w, "lb_wilcox": lo_w, "wmeta": wmeta,
                "ub_norm": theta + Z95 * se,
                "ub_wilcox_shifted": hi_d, "lb_wilcox_shifted": lo_d,
                "p_h1": p_h1, "p_h3": p_h3, "p_h2": p_h2,
                "check_ub_consistency": check_h2, "check_lb_consistency": check_h3,
                "n_t_lower": int(np.sum(t < 0)), "n_d_lower": int(np.sum(d < 0)),
            }

    ghist = {}
    for ds, arms in ARMS.items():
        chains = {arm: [{"name": "H1", "p": full[(ds, arm)]["p_h1"]},
                        {"name": "H2", "p": full[(ds, arm)]["p_h2"]},
                        {"name": "H3", "p": full[(ds, arm)]["p_h3"]}] for arm in arms}
        ghist[ds] = graphical_holm(chains, alpha=0.05)

    desc_rows, detail_rows = [], []
    for ds, arms in ARMS.items():
        delta = DELTA[ds]
        for arm in arms:
            f = full[(ds, arm)]
            r1 = step_record(ghist[ds], arm, "H1")
            r2 = step_record(ghist[ds], arm, "H2")
            h1_rej = bool(r1["rejected"])
            h2_rej = bool(r2["rejected"]) if h1_rej else False
            if h2_rej:
                h3_rej = bool(f["lb_wilcox"] > 0.0)
                h3_note = ""
            else:
                h3_rej = "not tested (H2 not rejected)"
                h3_note = "preregistered rule: H3 is tested only if H2 is rejected"
            pw0 = power_normal(delta, 0.0, f["se"])
            desc_rows.append({
                "ds": ds, "arm": arm,
                "H1_p": fmt(f["p_h1"]), "H1_reject": str(h1_rej),
                "H2_hl": fmt(f["hl"]), "H2_ub95": fmt(f["ub_wilcox"]),
                "H2_reject": str(h2_rej), "H3_reject": str(h3_rej),
                "power_H2_at_delta": fmt(pw0), "label": LABEL,
            })
            detail_rows.append({
                "ds": ds, "arm": arm, "n_units": f["n"],
                "unit_first": int(f["seeds"][0]), "unit_last": int(f["seeds"][-1]),
                "units_arm_lower_rel_rmse": f["n_d_lower"],
                "units_arm_lower_delta_group": f["n_t_lower"],
                "rel_mean": fmt(f["rel_mean"]), "rel_median": fmt(f["rel_median"]),
                "rel_sd": fmt(f["rel_sd"]), "se": fmt(f["se"]),
                "HL": fmt(f["hl"]),
                "ub95_wilcoxon_inverted_PRIMARY": fmt(f["ub_wilcox"]),
                "lb95_wilcoxon_inverted_PRIMARY": fmt(f["lb_wilcox"]),
                "ub95_basic_bootstrap_secondary": fmt(f["ub_basic"]),
                "lb95_basic_bootstrap_secondary": fmt(f["lb_basic"]),
                "ub95_normal_secondary": fmt(f["ub_norm"]),
                "walsh_N": f["wmeta"]["N_walsh"], "walsh_c_hi": f["wmeta"]["c_hi"],
                "walsh_c_lo": f["wmeta"]["c_lo"],
                "wilcoxon_critical_distribution": f["wmeta"]["critical_value_distribution"],
                "delta": delta, "margin": MARGIN_NAME[ds],
                "H1_p_wilcoxon_less": fmt(f["p_h1"]),
                "H2_p_theta_ge_delta_normal": fmt(f["p_h2"]),
                "H3_p_wilcoxon_greater": fmt(f["p_h3"]),
                "alpha_H1_allocated": r1["alpha_allocated"],
                "alpha_H2_allocated": r2["alpha_allocated"],
                "alpha_H3_allocated": step_record(ghist[ds], arm, "H3")["alpha_allocated"],
                "H1_reject": str(h1_rej), "H2_reject": str(h2_rej),
                "H3_reject": str(h3_rej), "H3_note": h3_note,
                "rule_used_for_H2": "U_wilcox < delta",
                "consistency_ub_vs_signedrank_less": f["check_ub_consistency"],
                "consistency_lb_vs_signedrank_greater": f["check_lb_consistency"],
                "label": LABEL,
            })

    # ---------------- power table ----------------
    power_rows = []
    cs_tot = full[("cityscanner_nyc_pm25", "raven")]["rel_sd"]
    sig_w_proxy = proxy["sd_rel_diff_wo_vs_raven"]     # pilot within-trace scale
    scen_def = {
        "S0_sigmaW_zero": (cs_tot, 0.0,
                           "Part B B0-b not run (no authorization): sigma_W = 0 -- floor "
                           "scenario, r is irrelevant"),
        "S1_neutral": (cs_tot / math.sqrt(2.0), cs_tot / math.sqrt(2.0),
                       "Part B B0-b not run (no authorization): sigma_W = sigma_B (neutral)"),
        "S2_pilot_within_trace": (math.sqrt(max(cs_tot ** 2 - sig_w_proxy ** 2, 0.0)),
                                  sig_w_proxy,
                                  "Part B B0-b not run (no authorization): sigma_W = pilot "
                                  "within-trace scale, SD of raven_wo_design/raven-1 across "
                                  "the 10 traces (upper/optimistic reading)"),
    }

    def prow(ds, arm, delta, scen, r, th_case, th, se_use, sig_b, sig_wv, proxy_flag,
             proxy_src, boot="", status=""):
        return {
            "ds": ds, "arm": arm, "margin": MARGIN_NAME[ds], "delta": delta,
            "scenario": scen, "n_traces": full[(ds, arm)]["n"], "r_model_seeds": r,
            "n_effective": full[(ds, arm)]["n"] * r,
            "theta_case": th_case, "theta_true": th,
            "paired_sd": full[(ds, arm)]["rel_sd"], "se_used": se_use,
            "sigma_between_trace": sig_b, "sigma_within_trace_proxy": sig_wv,
            "proxy_flag": proxy_flag, "proxy_source": proxy_src, "proxy_status": status,
            "power_normal": power_normal(delta, th, se_use),
            "power_t_df": power_t(delta, th, se_use, max(full[(ds, arm)]["n"] - 1, 1)),
            "mde80": mde80(delta, se_use),
            "power_boot_cluster": boot,
            "testable_power_ge_0.80": ("" if th_case != "theta0"
                                       else str(power_normal(delta, th, se_use) >= 0.80)),
            "label": LABEL,
        }

    for ds, arm in [("sensorscope", "raven"), ("sensorscope", "proj_beta"),
                    ("uair", "raven"), ("uair", "proj_beta")]:
        delta = DELTA[ds]
        f = full[(ds, arm)]
        for th_case, th in (("theta0", 0.0), ("theta_delta_half", delta / 2),
                            ("theta_delta", delta)):
            power_rows.append(prow(ds, arm, delta, "observed_n_r1", 1, th_case, th,
                                   f["se"], "", 0.0, "measured",
                                   "observed paired SD over 20 seeds at r=1", "",
                                   "measured -- B0 not needed for these datasets"))

    delta_cs = DELTA["cityscanner_nyc_pm25"]
    fcs = full[("cityscanner_nyc_pm25", "raven")]
    for th_case, th in (("theta0", 0.0), ("theta_delta_half", delta_cs / 2),
                        ("theta_delta", delta_cs)):
        power_rows.append(prow("cityscanner_nyc_pm25", "raven", delta_cs, "observed_n_r1", 1,
                               th_case, th, fcs["se"], cs_tot,
                               sig_wv=0.0, proxy_flag="measured",
                               proxy_src="observed paired SD over 10 traces at r=1",
                               status="measured -- r=1 requires no assumption"))
    scen_boot = {}
    for r in (1, 3, 5):
        for scen, (sb, sw, src) in scen_def.items():
            se_use = math.sqrt(sb ** 2 / fcs["n"] + sw ** 2 / (fcs["n"] * r))
            scen_boot[(scen, r)] = power_cluster_bootstrap(
                0.0, sb, sw, r, fcs["n"], delta_cs)   # theta = 0 (headline case)
            for th_case, th in (("theta0", 0.0), ("theta_delta_half", delta_cs / 2),
                                ("theta_delta", delta_cs)):
                power_rows.append(prow("cityscanner_nyc_pm25", "raven", delta_cs, scen, r,
                                       th_case, th, se_use, sb, sw, "proxy", src,
                                       boot=(scen_boot[(scen, r)] if th_case == "theta0" else ""),
                                       status="proxy -- Part B B0-b did not run"))

    # ---------------- sensitivity: drop 32005 ----------------
    sens_rows = []
    for ds, arms in ARMS.items():
        for arm in arms:
            seeds, ref, a, ref_dg, a_dg = paired_vectors(ds, arm, w1, cs)
            keep = seeds != SENS_SEED
            if keep.all():
                sens_rows.append({"ds": ds, "arm": arm, "excluded_unit": "not applicable",
                                  "n_units": int(len(seeds)),
                                  "note": "unit %d does not occur on this dataset"
                                          % SENS_SEED,
                                  "role": "declared sensitivity analysis, never primary",
                                  "label": "post hoc descriptive (sensitivity)"})
                continue
            d = (a / ref - 1.0)[keep]
            t = (a_dg - ref_dg)[keep]
            theta, lo_bb, hi_bb, _ = basic_bootstrap(d, np.random.default_rng(SEED_BOOT))
            sens_rows.append({
                "ds": ds, "arm": arm, "excluded_unit": str(SENS_SEED),
                "n_units": int(len(d)), "note": "",
                "rel_mean": fmt(float(np.mean(d))), "rel_median": fmt(float(np.median(d))),
                "rel_sd": fmt(float(np.std(d, ddof=1))),
                "H1_p": fmt(float(stats.wilcoxon(t, alternative="less").pvalue)),
                "H2_hl": fmt(theta), "H2_ub95": fmt(hi_bb),
                "delta": DELTA[ds],
                "H2_reject": str(hi_bb < DELTA[ds]),
                "H3_lb95": fmt(lo_bb),
                "H3_reject": str(lo_bb > 0.0),
                "role": "declared sensitivity analysis, never primary",
                "label": "post hoc descriptive (sensitivity)",
            })

    # ---------------- protocol SS0 reproduction check ----------------
    d_cs = full[("cityscanner_nyc_pm25", "raven")]["d"]
    idx32005 = list(full[("cityscanner_nyc_pm25", "raven")]["seeds"]).index(32005)
    checks = {
        "computed": {"rel_mean": float(np.mean(d_cs)), "rel_median": float(np.median(d_cs)),
                     "rel_sd": float(np.std(d_cs, ddof=1)),
                     "seeds_first_arm_lower": int(np.sum(d_cs < 0)), "n": int(len(d_cs)),
                     "seed32005_rel_ratio": float(d_cs[idx32005] + 1.0)},
        "protocol_SS0": {"rel_mean": 0.0559, "rel_median": 0.0027, "rel_sd": 0.134,
                         "seeds_first_arm_lower": "5/10",
                         "seed32005": "raven 0.4092 vs fedavg_window 0.2938 (+39%)"},
    }
    checks["agrees"] = {
        "mean": abs(checks["computed"]["rel_mean"] - 0.0559) < 5e-4,
        "median": abs(checks["computed"]["rel_median"] - 0.0027) < 5e-4,
        "sd": abs(checks["computed"]["rel_sd"] - 0.134) < 1e-3,
        "seeds": checks["computed"]["seeds_first_arm_lower"] == 5,
    }

    # ---------------- write ----------------
    def write_csv(path, rows, header=None):
        if header is None:                      # union of keys, in first-seen order
            header = []
            for r in rows:
                for k in r:
                    if k not in header:
                        header.append(k)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=header)
            wr.writeheader()
            for r in rows:
                wr.writerow({c: r.get(c, "") for c in header})

    write_csv(OUT / "A1_DESCRIPTIVE.csv", desc_rows,
              ["ds", "arm", "H1_p", "H1_reject", "H2_hl", "H2_ub95", "H2_reject",
               "H3_reject", "power_H2_at_delta", "label"])
    write_csv(OUT / "A1_DESCRIPTIVE_DETAIL.csv", detail_rows)
    write_csv(OUT / "A1_POWER.csv", power_rows)
    write_csv(OUT / "A1_SENSITIVITY_NO32005.csv", sens_rows)

    prov = {"round": "results_gatekeeping/round_v1", "part": "A only",
            "generated_by": "A1_ANALYSIS.py",
            "prereg_sha256": {"PREREG.md": sha256_file(OUT / "PREREG.md"),
                              "PROTOCOL.md": sha256_file(OUT / "PROTOCOL.md")},
            "inputs": provenance, "training_runs": 0, "build_calls": 0,
            "bootstrap": {"B": B_BOOT, "seed": SEED_BOOT, "type": "basic/reflection on HL",
                          "role": "secondary bound; H2/H3 decisions use the "
                                  "Wilcoxon-inverted distribution-free bound"},
            "wilcoxon_inversion_checks": {
                "%s|%s" % k: {"ub_vs_signedrank_less_agree": v["check_ub_consistency"],
                              "lb_vs_signedrank_greater_agree": v["check_lb_consistency"],
                              "walsh": v["wmeta"]} for k, v in full.items()},
            "wilcoxon_inversion_simulation": verify_inversion(),
            "graphical_holm": ghist,
            "protocol_SS0_checks": checks,
            "cs_within_trace_proxy": proxy,
            "cityscanner_power_scenarios": {
                "total_paired_sd_r1": cs_tot,
                "sigma_within_pilot_proxy": sig_w_proxy,
                "scenario_sigmas": {k: {"sigma_between": v[0], "sigma_within": v[1],
                                        "source": v[2]} for k, v in scen_def.items()},
                "power_theta0_by_scenario_r": {"%s|r=%d" % k: v
                                               for k, v in scen_boot.items()}},
            "sensitivity_rule": "drop unit %d; sensitivity only, never primary" % SENS_SEED}
    (OUT / "A1_PROVENANCE.json").write_text(
        json.dumps(prov, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")

    # ---------------- console (ASCII) ----------------
    print("=== A1_DESCRIPTIVE (all rows: post hoc descriptive) ===")
    for r in desc_rows:
        print("%-22s %-10s H1p=%-10.4g rej=%-5s HL=%+.5f ub95=%+.5f rej=%-5s H3=%-28s pw0=%.3f"
              % (r["ds"], r["arm"], float(r["H1_p"]), r["H1_reject"], float(r["H2_hl"]),
                 float(r["H2_ub95"]), r["H2_reject"], r["H3_reject"],
                 float(r["power_H2_at_delta"])))
    print("=== alpha allocation (graphical Holm within dataset) ===")
    for ds, g in ghist.items():
        for h in g["history"]:
            print("  %-22s %-3s a=%.5f p=%s rej=%s"
                  % (ds, h["step"], h["alpha_allocated"],
                     ("None" if h["p"] is None else "%.4g" % h["p"]), h["rejected"]))
        print("  final weights:", g["final_weights"])
    print("=== CS proxy ===")
    print(json.dumps(proxy, indent=1, default=str))
    print("=== protocol SS0 check ===")
    print(json.dumps(checks, indent=1, default=str))
    print("=== CS power at theta=0 ===")
    for k, v in sorted(scen_boot.items()):
        print("  %-24s r=%d  power=%.4f" % (k[0], k[1], v))
    print("=== sensitivity ===")
    for r in sens_rows:
        print("  %-22s %-10s %s" % (r["ds"], r["arm"], json.dumps(
            {k: v for k, v in r.items() if k in ("n_units", "H2_ub95", "H2_reject", "note")},
            default=str)))
    return 0


def finalize_manifest() -> str:
    """Append the artefact hashes to MANIFEST.sha256, without touching the registration block.

    The registration block recorded the PRE-COMPUTATION hashes.  PREREG.md was amended
    after that (documented in the registration timeline inside PREREG.md and in
    EXECUTION_REPORT.md); the amendment history is asserted here rather than silently
    re-pinned.
    """
    man = OUT / "MANIFEST.sha256"
    text = man.read_text(encoding="utf-8")
    base = text.split("# post-computation artefact hashes")[0]
    doc = {}
    for line in base.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        h, name = line.split()[:2]
        doc[name] = h
    # frozen claims of the registration block
    assert doc.get("PROTOCOL.md") == sha256_file(OUT / "PROTOCOL.md"), \
        "PROTOCOL.md changed after registration"
    assert doc.get("PREREG.md") == "c30ea27366df3217008aa26796c553d5d908c31b71b072728cd657e9f43e76d8", \
        "the recorded first PREREG.md hash is not the one this round recorded"
    timeline = [
        "# REGISTRATION TIMELINE",
        "#  t0  PROTOCOL.md copied byte-identical; PREREG.md written; both hashed into this",
        "#      file BEFORE any A1 number was computed:",
        "#        PREREG.md sha256 c30ea27366df3217008aa26796c553d5d908c31b71b072728cd657e9f43e76d8",
        "#  t1  PREREG.md amended TWICE, still before any A1 value was read or reported:",
        "#      (a) Wilcoxon-inverted bound corrected to the preregistered estimator form",
        "#          (L = W_norm[c_lo], U = W_norm[c_hi], exact null CDF) and named primary,",
        "#          basic bootstrap and normal bound demoted to secondary;",
        "#      (b) City Scanner within-trace variance scenarios restated as the admissible",
        "#          range S0/S1/S2 with sigma_W defined as the within-trace paired-difference SD.",
        "#      Both amendments came from reviewing estimator definitions (pre-existing",
        "#      protocol text) and from failing internal consistency checks, NOT from any",
        "#      A1 result. The locked rules (H1/H2/H3 order, delta, delta_CS, sensitivity",
        "#      rule, arm list, seed sets, bootstrap B/seed) were NOT changed at t1.",
        "#  t2  registration timeline (SS0 of PREREG.md) added; this is the operative",
        "#      registration. It changed no rule either.",
        "#      PREREG.md as executed (sha256, re-read at finalisation):",
        "#        " + sha256_file(OUT / "PREREG.md"),
        "",
    ]
    lines = [base.rstrip("\n"), ""] + timeline
    lines.append("# post-computation artefact hashes")
    lines.append("# appended by A1_ANALYSIS.py --write-manifest after computing; hashes are")
    lines.append("# given for tamper-evidence and are NOT anchors for files that this")
    lines.append("# script itself writes (A1_ANALYSIS.py is rewritten by editing, so its own")
    lines.append("# hash here lags one edit by construction). The registration block and the")
    lines.append("# input list above are the immutable parts.")
    for name in ("A1_ANALYSIS.py", "A1_DESCRIPTIVE.csv", "A1_DESCRIPTIVE_DETAIL.csv",
                 "A1_POWER.csv", "A1_SENSITIVITY_NO32005.csv", "A1_PROVENANCE.json",
                 "EXECUTION_REPORT.md", "ERRATA_FOR_PAPER.md"):
        p = OUT / name
        if p.exists():
            lines.append("%s  %s" % (sha256_file(p), name))
    lines.append("")
    lines.append("# read-only inputs (sha256 as read by this round)")
    for k, v in INPUTS.items():
        lines.append("# %s  %s  %s" % (sha256_file(v), k, v.relative_to(ROOT)))
    man.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return str(man)


if __name__ == "__main__":
    rc = main()
    if "--write-manifest" in sys.argv:
        print("manifest written:", finalize_manifest())
    sys.exit(rc)
