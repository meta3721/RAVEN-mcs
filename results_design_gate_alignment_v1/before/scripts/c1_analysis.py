#!/usr/bin/env python3
"""C1 (Part B) analysis -- B2 endpoints, B3 decision rules, mechanical application.

Reads results_gatekeeping/round_v1/C1_RUNS.csv (written by scripts/c1_deletion_driver.py)
and writes, inside results_gatekeeping/round_v1/:

  C1_PRIMARY.json            primary H_mech + structural guardrail
  C1_SECONDARY.csv           secondary family (Holm within the family)
  C1_A1_CHAINS.csv           confirmatory A1 chains H1 -> H2(delta_CS) -> H3
  C1_SENSITIVITY_NO32005.csv every estimate recomputed without trace 32005
  C1_PER_SEED.csv            per (arm, trace, model seed) rows, trace 32005 marked
  C1_ARM_SUMMARY.csv         per-arm trace-level means incl. WorstGroupRMSE and R0-R3

Estimators, contrasts, margins, bootstrap settings and decision rules are exactly those
registered in results_gatekeeping/round_v1/PREREG.md AMENDMENT 1 (t3).  Nothing here
chooses a contrast, margin, arm or seed after seeing a C1 RMSE.

ASCII-only console output.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import pathlib
import sys

import numpy as np
from scipy import stats

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_gatekeeping" / "round_v1"
RUNS = OUT / "C1_RUNS.csv"
A1_SCRIPT = OUT / "A1_ANALYSIS.py"

B_BOOT = 10000
SEED_BOOT = 20261003
R = 3
DELTA_CS = 0.02
Z95 = 1.6448536269514722
Z80 = 0.8416212335729143
SENS_TRACE = 32005
ARMS = ("fedavg_window", "raven_wo_design", "raven_ctrl", "raven_ctrl_floor",
        "raven_M1mu", "raven_M2mu")
NEW_ARMS = ("raven_ctrl_floor", "raven_M1mu", "raven_M2mu")
LEVEL_ARMS = ("raven_ctrl", "raven_ctrl_floor", "raven_M1mu", "raven_M2mu")  # dose variant
CHAIN_ARMS = ("raven_ctrl_floor", "raven_M1mu", "raven_M2mu")
REF = "fedavg_window"
METRICS = ("RMSE_mu", "WorstGroupRMSE", "WG_R0", "WG_R1", "WG_R2", "WG_R3",
           "Delta_group", "Delta_c_s")
TEMPLATE_PRIMARY = ("hl_rel_diff", "ci95_lo", "ci95_hi", "wilcoxon_p", "n_traces", "r",
                    "reading", "dgroup_gain_retained_share")


# --------------------------------------------------------------------------- io
def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_rows(path: pathlib.Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: pathlib.Path, rows: list[dict], header: list[str] | None = None) -> None:
    if header is None:
        header = []
        for r in rows:
            for k in r:
                if k not in header:
                    header.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=header)
        wr.writeheader()
        for r in rows:
            wr.writerow({c: r.get(c, "") for c in header})


def fmt(x, nd: int = 10) -> str:
    try:
        return ("%." + str(nd) + "g") % float(x)
    except (TypeError, ValueError):
        return ""


# --------------------------------------------------------------------------- data
def load() -> tuple[dict, list[int]]:
    rows = read_rows(RUNS)
    traces = sorted({int(r["trace_seed"]) for r in rows})
    data: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    for arm in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        if not sub:
            continue
        data[arm] = {}
        for t in traces:
            ts = sorted([r for r in sub if int(r["trace_seed"]) == t],
                        key=lambda r: int(r["model_seed"]))
            data[arm][str(t)] = {m: np.array([float(r[m]) for r in ts]) for m in METRICS}
            data[arm][str(t)]["rho"] = np.array([float(r["rho_realized"]) for r in ts])
    return data, traces


def tmean(data: dict, arm: str, metric: str, traces: list[int]) -> np.ndarray:
    return np.array([float(np.mean(data[arm][str(t)][metric])) for t in traces])


def rho_of(data: dict, arm: str, traces: list[int]) -> np.ndarray:
    return np.array([float(np.mean(data[arm][str(t)]["rho"])) for t in traces])


# --------------------------------------------------------------------------- estimators
def walsh_averages(d: np.ndarray) -> np.ndarray:
    n = len(d)
    a = (d[:, None] + d[None, :]) / 2.0
    return np.sort(a[np.triu_indices(n)])


def hl(d: np.ndarray) -> float:
    return float(np.median(walsh_averages(d)))


def signedrank_critical(n: int):
    """(c_lo, c_hi, source) exactly as A1_ANALYSIS.py."""
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
        return (max(int(math.floor(mu - Z95 * sd)), 0),
                min(int(math.floor(mu + Z95 * sd)), m - 1),
                "normal approximation (exact distribution unavailable)")


def wilcoxon_bounds(d: np.ndarray) -> tuple[float, float, dict]:
    w = walsh_averages(d)
    m = len(w)
    c_lo, c_hi, src = signedrank_critical(len(d))
    return (float(w[min(max(c_lo, 0), m - 1)]), float(w[min(max(c_hi, 0), m - 1)]),
            {"n": len(d), "N_walsh": m, "c_lo": c_lo, "c_hi": c_hi,
             "critical_value_distribution": src})


def cluster_boot_hl(a_seeds: list[np.ndarray], b_seeds: list[np.ndarray],
                    rng: np.random.Generator) -> np.ndarray:
    """Preregistered trace-cluster bootstrap of the HL paired relative difference.

    Each resample: draw n traces with replacement; within a drawn trace draw r model
    seeds with replacement from that trace's r runs of each arm; the trace-level means
    of the drawn runs give d*_t = mean_a/mean_b - 1; the draw is HL(d*).
    """
    n = len(a_seeds)
    out = np.empty(B_BOOT)
    for bi in range(B_BOOT):
        t_idx = rng.integers(0, n, n)
        d = np.empty(n)
        for k, t in enumerate(t_idx):
            r = len(a_seeds[t])
            j = rng.integers(0, r, r)
            d[k] = float(a_seeds[t][j].mean()) / float(b_seeds[t][j].mean()) - 1.0
        out[bi] = hl(d)
    return out


def rel_trace_means(a_seeds: list[np.ndarray], b_seeds: list[np.ndarray]) -> np.ndarray:
    return np.array([float(a.mean()) / float(b.mean()) - 1.0 for a, b in zip(a_seeds, b_seeds)])


def rel_seed_paired(a_seeds: list[np.ndarray], b_seeds: list[np.ndarray]) -> np.ndarray:
    return np.array([float(np.mean(a / b - 1.0)) for a, b in zip(a_seeds, b_seeds)])


def read_ci(lo: float, hi: float, delta: float = DELTA_CS) -> str:
    """Mechanical reading of a CI, exactly as registered in AMENDMENT 1 A4."""
    if lo > 0.0:
        return "deletion causes a prediction cost"
    if lo >= -delta and hi <= delta:
        return "no detectable deletion cost (CI inside +-delta_CS)"
    return "inconclusive"


def power_diag(c: dict, delta: float = DELTA_CS) -> dict:
    """A1 SS5 power formulas applied to the observed trace-level SD of this contrast.

    Diagnostic only (B3 requires the inconclusive row to report the CI and the power);
    it selects no margin, arm, seed or contrast.
    """
    se = c["se"]
    return {
        "sd_trace_level": c["rel_sd"], "se": se, "n_traces": c["n_traces"],
        "delta_CS": delta,
        "power_at_theta0_delta_CS": float(stats.norm.cdf((delta - 0.0) / se - Z95)),
        "mde80": delta - (Z80 + Z95) * se,
        "testable_power_ge_0.80": bool(stats.norm.cdf((delta - 0.0) / se - Z95) >= 0.80),
        "ci_width_percentile": c["ci95_hi"] - c["ci95_lo"],
        "ci_half_width_below": -c["ci95_lo"], "ci_half_width_above": c["ci95_hi"],
        "formula": "power(theta) = Phi((delta - theta)/SE - z_0.95), SE = sd(d_t)/sqrt(n); "
                   "MDE_80 = delta - (z_0.80 + z_0.95)*SE (A1 PREREG SS5)",
        "role": "post hoc diagnostic required by B3 for the inconclusive row; not a decision",
    }


def contrast(data: dict, arm: str, ref: str, traces: list[int], metric: str = "RMSE_mu") -> dict:
    a_seeds = [data[arm][str(t)][metric] for t in traces]
    b_seeds = [data[ref][str(t)][metric] for t in traces]
    d = rel_trace_means(a_seeds, b_seeds)
    theta = hl(d)
    lo_w, hi_w, wmeta = wilcoxon_bounds(d)
    se = float(np.std(d, ddof=1) / math.sqrt(len(d)))
    rng = np.random.default_rng(SEED_BOOT)
    boot = cluster_boot_hl(a_seeds, b_seeds, rng)
    p_w = float(stats.wilcoxon(d).pvalue)
    return {
        "arm": arm, "ref": ref, "metric": metric, "n_traces": len(d),
        "d": d, "hl": theta,
        "ci95_lo": float(np.quantile(boot, 0.025)),
        "ci95_hi": float(np.quantile(boot, 0.975)),
        "ci_basic_lo": float(2 * theta - np.quantile(boot, 0.975)),
        "ci_basic_hi": float(2 * theta - np.quantile(boot, 0.025)),
        "wilcoxon_inverted_lo": lo_w, "wilcoxon_inverted_hi": hi_w, "walsh": wmeta,
        "wilcoxon_p": p_w, "rel_mean": float(np.mean(d)), "rel_median": float(np.median(d)),
        "rel_sd": float(np.std(d, ddof=1)), "se": se, "boot": boot,
        "d_seed_paired": rel_seed_paired(a_seeds, b_seeds),
        "n_traces_arm_lower": int(np.sum(d < 0)),
    }


# --------------------------------------------------------------------------- graphical Holm
def graphical_holm(chains: dict, alpha: float = 0.05) -> dict:
    """Verbatim logic of A1_ANALYSIS.graphical_holm (Bretz-Maurer-Brannath-Posch)."""
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


def step_record(ghist: dict, chain: str, step: str) -> dict:
    for h in ghist["history"]:
        if h["chain"] == chain and h["step"] == step:
            return h
    return {"alpha_allocated": None, "rejected": False, "p": None}


def verify_against_a1(chains: dict) -> dict:
    """Cross-check this file's graphical procedure and bounds against A1_ANALYSIS.py."""
    if not A1_SCRIPT.is_file():
        return {"available": False}
    spec = importlib.util.spec_from_file_location("a1_analysis_ref", A1_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                      # type: ignore[union-attr]
    mine = graphical_holm(chains, 0.05)
    theirs = mod.graphical_holm(chains, 0.05)
    d = np.array([0.01, -0.02, 0.03, 0.005, -0.011, 0.02, 0.0, -0.004, 0.017, 0.009])
    my_lo, my_hi, _ = wilcoxon_bounds(d)
    th_lo, th_hi, _ = mod.wilcoxon_bounds(d)
    return {"available": True,
            "graphical_history_identical": mine["history"] == theirs["history"],
            "final_weights_identical": mine["final_weights"] == theirs["final_weights"],
            "wilcoxon_bounds_identical": (my_lo == th_lo and my_hi == th_hi),
            "wilcoxon_bounds_demo": {"lo": my_lo, "hi": my_hi}}


# --------------------------------------------------------------------------- main
def main() -> int:
    if not RUNS.is_file():
        print("C1_RUNS.csv missing -- run the driver first")
        return 2
    data, traces = load()
    per_seed_done = {a: all(int(len(data[a][str(t)]["RMSE_mu"])) == R for t in traces)
                     for a in data}
    prov = {"runs_csv_sha256": sha256_file(RUNS), "n_runs": len(read_rows(RUNS)),
            "traces": traces, "arms": sorted(data), "complete": per_seed_done,
            "bootstrap": {"B": B_BOOT, "seed": SEED_BOOT, "type": "trace-cluster, "
                          "traces resampled with replacement and r model seeds within "
                          "trace resampled with replacement; percentile interval"},
            "registered_in": "PREREG.md AMENDMENT 1 (t3), hashed in MANIFEST.sha256 "
                             "before the first B1 run"}

    # ------------------------------------------------ primary
    prim = contrast(data, "raven_ctrl", "raven_ctrl_floor", traces)
    reading = read_ci(prim["ci95_lo"], prim["ci95_hi"])
    # structural guardrail
    dg = {a: tmean(data, a, "Delta_group", traces) for a in ARMS}
    dcs = {a: tmean(data, a, "Delta_c_s", traces) for a in ARMS}
    gain_fed = float(np.mean(dg[REF]) - np.mean(dg["raven_ctrl"]))
    gain_floor = float(np.mean(dg[REF]) - np.mean(dg["raven_ctrl_floor"]))
    retained = (gain_floor / gain_fed) if gain_fed > 0 else None
    guard = {
        "Delta_group_mean": {a: float(np.mean(dg[a])) for a in ARMS},
        "Delta_c_s_mean": {a: float(np.mean(dcs[a])) for a in ARMS},
        "Delta_group_ctrl_floor_minus_ctrl": float(np.mean(dg["raven_ctrl_floor"])
                                                   - np.mean(dg["raven_ctrl"])),
        "Delta_c_s_ctrl_floor_minus_ctrl": float(np.mean(dcs["raven_ctrl_floor"])
                                                 - np.mean(dcs["raven_ctrl"])),
        "rule": "retained = (mean_t Dg(fedavg) - mean_t Dg(floor)) / "
                "(mean_t Dg(fedavg) - mean_t Dg(ctrl))",
        "dgroup_gain_fedavg_to_ctrl": gain_fed,
        "dgroup_gain_fedavg_to_floor": gain_floor,
        "dgroup_gain_retained_share": retained,
        "per_trace_retained_share": [
            float((dg[REF][i] - dg["raven_ctrl_floor"][i])
                  / (dg[REF][i] - dg["raven_ctrl"][i]))
            if (dg[REF][i] - dg["raven_ctrl"][i]) > 0 else None
            for i in range(len(traces))],
    }
    primary = {
        "hl_rel_diff": prim["hl"], "ci95_lo": prim["ci95_lo"], "ci95_hi": prim["ci95_hi"],
        "wilcoxon_p": prim["wilcoxon_p"], "n_traces": prim["n_traces"], "r": R,
        "reading": reading, "dgroup_gain_retained_share": retained,
        "contrast": "RMSE_mu(raven_ctrl)/RMSE_mu(raven_ctrl_floor) - 1, trace-level means "
                    "over r = 3 model seeds",
        "delta_CS": DELTA_CS,
        "ci_type": "percentile trace-cluster bootstrap",
        "ci_basic_lo": prim["ci_basic_lo"], "ci_basic_hi": prim["ci_basic_hi"],
        "wilcoxon_inverted_lo": prim["wilcoxon_inverted_lo"],
        "wilcoxon_inverted_hi": prim["wilcoxon_inverted_hi"],
        "rel_mean": prim["rel_mean"], "rel_median": prim["rel_median"],
        "rel_sd": prim["rel_sd"], "se": prim["se"],
        "n_traces_arm_lower": prim["n_traces_arm_lower"],
        "reading_robust_to_interval_type": {
            "percentile": reading,
            "basic": read_ci(prim["ci_basic_lo"], prim["ci_basic_hi"]),
            "wilcoxon_inverted": read_ci(prim["wilcoxon_inverted_lo"],
                                         prim["wilcoxon_inverted_hi"]),
            "note": "the preregistered primary interval is the percentile one"},
        "power_diagnostic": power_diag(prim),
        "d_seed_paired_robustness": {
            "hl": hl(prim["d_seed_paired"]),
            "mean": float(np.mean(prim["d_seed_paired"])),
            "note": "declared robustness column; never a decision"},
        "structural_guardrail": guard,
        "walsh": prim["walsh"], "provenance": prov,
    }
    (OUT / "C1_PRIMARY.json").write_text(
        json.dumps(primary, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")

    # ------------------------------------------------ secondary family
    sec = []
    c_m1 = contrast(data, "raven_M1mu", "raven_ctrl", traces)
    c_m2 = contrast(data, "raven_M2mu", "raven_ctrl", traces)
    c_fl = contrast(data, "raven_ctrl_floor", "raven_wo_design", traces)

    def dose(arm_list: tuple) -> dict:
        xs, ys = [], []
        for a in arm_list:
            xa, ya = rho_of(data, a, traces), tmean(data, a, "RMSE_mu", traces)
            xs.append(xa)
            ys.append(ya)
        x = np.concatenate(xs)
        y = np.concatenate(ys)
        slope = float(np.polyfit(x, y, 1)[0])
        rng = np.random.default_rng(SEED_BOOT)
        boot = np.empty(B_BOOT)
        n = len(traces)
        for b in range(B_BOOT):
            t_idx = rng.integers(0, n, n)
            bx, by = [], []
            for t in t_idx:
                j = rng.integers(0, R, R)
                for a in arm_list:
                    bx.append(float(np.mean(data[a][str(traces[t])]["rho"][j])))
                    by.append(float(np.mean(data[a][str(traces[t])]["RMSE_mu"][j])))
            boot[b] = np.polyfit(np.asarray(bx), np.asarray(by), 1)[0]
        p = 2.0 * min(float(np.mean(boot <= 0.0)), float(np.mean(boot >= 0.0)))
        return {"slope": slope, "ci95_lo": float(np.quantile(boot, 0.025)),
                "ci95_hi": float(np.quantile(boot, 0.975)), "p": min(p, 1.0),
                "n_points": len(x), "arms": list(arm_list),
                "rho_values": sorted({round(float(v), 6) for v in x
                                      if abs(v) < 1e-9 or v > 1e-9})}

    d_all = dose(ARMS)
    d_lvl = dose(LEVEL_ARMS)
    members = [
        ("M1mu_minus_ctrl", c_m1, "raven_M1mu - raven_ctrl"),
        ("M2mu_minus_ctrl", c_m2, "raven_M2mu - raven_ctrl"),
        ("ctrl_floor_minus_wo_design", c_fl, "raven_ctrl_floor - raven_wo_design"),
        ("dose_response_slope", None, "OLS slope of RMSE_mu on realized rho"),
    ]
    pvals = [c_m1["wilcoxon_p"], c_m2["wilcoxon_p"], c_fl["wilcoxon_p"], d_all["p"]]
    order = sorted(range(4), key=lambda i: pvals[i])
    holm = {}
    n_family = 4
    for k, i in enumerate(order):
        thr = 0.05 / (n_family - k)
        prev_rejected = all(holm[j]["reject"] for j in order[:k])
        holm[i] = {"rank": k + 1, "threshold": thr,
                   "reject": bool(pvals[i] <= thr and prev_rejected)}
    for i, (name, c, label) in enumerate(members):
        row = {"member": name, "contrast": label, "n_traces": len(traces), "r": R,
               "holm_rank": holm[i]["rank"], "holm_threshold": holm[i]["threshold"],
               "holm_reject": holm[i]["reject"]}
        if c is not None:
            row.update({"hl_rel_diff": fmt(c["hl"]), "ci95_lo": fmt(c["ci95_lo"]),
                        "ci95_hi": fmt(c["ci95_hi"]), "wilcoxon_p": fmt(c["wilcoxon_p"]),
                        "ci_basic_lo": fmt(c["ci_basic_lo"]),
                        "ci_basic_hi": fmt(c["ci_basic_hi"]),
                        "wilcoxon_inverted_lo": fmt(c["wilcoxon_inverted_lo"]),
                        "wilcoxon_inverted_hi": fmt(c["wilcoxon_inverted_hi"]),
                        "rel_mean": fmt(c["rel_mean"]), "rel_sd": fmt(c["rel_sd"]),
                        "n_traces_arm_lower": c["n_traces_arm_lower"],
                        "p_source": "two-sided paired Wilcoxon on trace-level means"})
        else:
            row.update({"hl_rel_diff": "", "ci95_lo": fmt(d_all["ci95_lo"]),
                        "ci95_hi": fmt(d_all["ci95_hi"]), "wilcoxon_p": "",
                        "bootstrap_p": fmt(d_all["p"]),
                        "slope": fmt(d_all["slope"]), "n_points": d_all["n_points"],
                        "p_source": "trace-cluster bootstrap p = 2*min(P(slope*<=0), "
                                    "P(slope*>=0))"})
        sec.append(row)
    sec.append({"member": "dose_response_slope_declared_variant",
                "contrast": "OLS slope of RMSE_mu on realized rho, RAVEN-Design arms only "
                            "(raven_ctrl, raven_ctrl_floor, raven_M1mu, raven_M2mu)",
                "n_traces": len(traces), "r": R, "holm_rank": "", "holm_threshold": "",
                "holm_reject": "not a member of the Holm family (declared robustness)",
                "slope": fmt(d_lvl["slope"]), "ci95_lo": fmt(d_lvl["ci95_lo"]),
                "ci95_hi": fmt(d_lvl["ci95_hi"]), "bootstrap_p": fmt(d_lvl["p"]),
                "n_points": d_lvl["n_points"], "p_source": "trace-cluster bootstrap"})
    write_csv(OUT / "C1_SECONDARY.csv", sec)

    # ------------------------------------------------ confirmatory A1 chains
    chain_contrasts = {}
    chains = {}
    for arm in CHAIN_ARMS:
        c = contrast(data, arm, REF, traces)
        t_grp = tmean(data, arm, "Delta_group", traces) - tmean(data, REF, "Delta_group", traces)
        p_h1 = float(stats.wilcoxon(t_grp, alternative="less").pvalue)
        p_h2_sr = float(stats.wilcoxon(c["d"] - DELTA_CS, alternative="less").pvalue)
        p_h2_norm = float(stats.norm.cdf((c["hl"] - DELTA_CS) / c["se"])) if c["se"] > 0 else 1.0
        p_h3 = float(stats.wilcoxon(c["d"], alternative="greater").pvalue)
        chain_contrasts[arm] = {"c": c, "p_h1": p_h1, "p_h2_sr": p_h2_sr,
                                "p_h2_norm": p_h2_norm, "p_h3": p_h3,
                                "n_T_lower": int(np.sum(t_grp < 0))}
        chains[arm] = [{"name": "H1", "p": p_h1},
                       {"name": "H2", "p": p_h2_sr},
                       {"name": "H3", "p": p_h3}]
    ghist = graphical_holm(chains, 0.05)
    a1_check = verify_against_a1(chains)
    chain_rows = []
    for arm in CHAIN_ARMS:
        cc = chain_contrasts[arm]
        c = cc["c"]
        r1 = step_record(ghist, arm, "H1")
        r2 = step_record(ghist, arm, "H2")
        r3 = step_record(ghist, arm, "H3")
        h1_rej = bool(r1["rejected"])
        h2_rej_rule = bool(h1_rej and c["wilcoxon_inverted_hi"] < DELTA_CS)
        h2_rej_graph = bool(h1_rej and r2["rejected"])
        if h2_rej_rule:
            h3_rej = bool(c["wilcoxon_inverted_lo"] > 0.0)
        else:
            h3_rej = "not tested (H2 not rejected)"
        chain_rows.append({
            "arm": arm, "ref": REF, "n_traces": len(traces), "r": R,
            "H1_p": fmt(cc["p_h1"]), "H1_reject": str(h1_rej),
            "H2_hl": fmt(c["hl"]), "H2_ub95": fmt(c["wilcoxon_inverted_hi"]),
            "delta_CS": DELTA_CS, "H2_reject": str(h2_rej_rule),
            "H3_reject": str(h3_rej), "alpha_allocated": r1["alpha_allocated"],
            "alpha_H1_allocated": r1["alpha_allocated"],
            "alpha_H2_allocated": r2["alpha_allocated"],
            "alpha_H3_allocated": r3["alpha_allocated"],
            "H2_p_signedrank_less": fmt(cc["p_h2_sr"]),
            "H2_p_normal_A1impl": fmt(cc["p_h2_norm"]),
            "H2_reject_graphical_A1impl": str(h2_rej_graph),
            "H2_lb95_wilcoxon_inverted": fmt(c["wilcoxon_inverted_lo"]),
            "H2_ci95_lo": fmt(c["ci95_lo"]), "H2_ci95_hi": fmt(c["ci95_hi"]),
            "H2_p_wilcoxon_two_sided": fmt(c["wilcoxon_p"]),
            "H1_p_wilcoxon_less": fmt(cc["p_h1"]),
            "H3_p_wilcoxon_greater": fmt(cc["p_h3"]),
            "n_traces_arm_lower_delta_group": cc["n_T_lower"],
            "n_traces_arm_lower_rmse": c["n_traces_arm_lower"],
            "consistency_H2_rule_vs_signedrank": str(
                (c["wilcoxon_inverted_hi"] < DELTA_CS) == (cc["p_h2_sr"] < 0.05)),
            "rule_used_for_H2": "U_wilcox < delta_CS, gated by H1",
        })
    write_csv(OUT / "C1_A1_CHAINS.csv", chain_rows)

    # ------------------------------------------------ per-seed + per-arm tables
    per_seed = []
    run_rows = read_rows(RUNS)
    for r in run_rows:
        per_seed.append({
            "arm": r["arm"], "trace_seed": r["trace_seed"], "model_seed": r["model_seed"],
            "model_seed_offset": r["model_seed_offset"],
            "trace_32005_flag": "TRUE" if int(r["trace_seed"]) == SENS_TRACE else "",
            "rho_realized": r["rho_realized"], "RMSE_mu": r["RMSE_mu"],
            "WorstGroupRMSE": r["WorstGroupRMSE"],
            "Delta_group": r["Delta_group"], "Delta_c_s": r["Delta_c_s"],
            "runtime_s": r["runtime_s"], "source": r["source"]})
    write_csv(OUT / "C1_PER_SEED.csv", per_seed)

    arm_summary = []
    for arm in ARMS:
        row = {"arm": arm, "n_traces": len(traces), "r": R,
               "rho_realized_mean": float(np.mean(rho_of(data, arm, traces)))}
        for m in METRICS:
            v = tmean(data, arm, m, traces)
            row[f"{m}_mean"] = float(np.mean(v))
            row[f"{m}_sd"] = float(np.std(v, ddof=1))
        row["RMSE_mu_min"] = float(np.min(tmean(data, arm, "RMSE_mu", traces)))
        row["RMSE_mu_max"] = float(np.max(tmean(data, arm, "RMSE_mu", traces)))
        arm_summary.append(row)
    write_csv(OUT / "C1_ARM_SUMMARY.csv", arm_summary)

    # ------------------------------------------------ sensitivity without trace 32005
    keep = [t for t in traces if t != SENS_TRACE]
    sens_rows = []

    def add_sens(name, full, no05, ctype="", extra=None):
        rec = {"estimate": name, "value_full_set": fmt(full), "value_no32005": fmt(no05),
               "n_traces_full": len(traces), "n_traces_no32005": len(keep),
               "role": "declared sensitivity analysis, never primary",
               "delta_from_full": (fmt(float(no05) - float(full))
                                   if full is not None and no05 is not None else ""),
               "ci_type": ctype}
        if extra:
            rec.update(extra)
        sens_rows.append(rec)

    p05 = contrast(data, "raven_ctrl", "raven_ctrl_floor", keep)
    add_sens("PRIMARY_H_mech_hl(ctrl/floor-1)", prim["hl"], p05["hl"],
             "percentile trace-cluster bootstrap")
    add_sens("PRIMARY_H_mech_ci95_lo", prim["ci95_lo"], p05["ci95_lo"], "percentile")
    add_sens("PRIMARY_H_mech_ci95_hi", prim["ci95_hi"], p05["ci95_hi"], "percentile")
    add_sens("PRIMARY_H_mech_wilcoxon_p", prim["wilcoxon_p"], p05["wilcoxon_p"], "two-sided")
    pd_full, pd_05 = power_diag(prim), power_diag(p05)
    add_sens("PRIMARY_power_at_theta0_delta_CS", pd_full["power_at_theta0_delta_CS"],
             pd_05["power_at_theta0_delta_CS"], "A1 SS5 formula, post hoc diagnostic")
    add_sens("PRIMARY_MDE80_at_delta_CS", pd_full["mde80"], pd_05["mde80"],
             "A1 SS5 formula, post hoc diagnostic")
    add_sens("PRIMARY_sd_trace_level", prim["rel_sd"], p05["rel_sd"])
    add_sens("PRIMARY_ci_width", pd_full["ci_width_percentile"], pd_05["ci_width_percentile"],
             "percentile")
    for name, arm, ref in (("SEC_M1mu_minus_ctrl", "raven_M1mu", "raven_ctrl"),
                           ("SEC_M2mu_minus_ctrl", "raven_M2mu", "raven_ctrl"),
                           ("SEC_ctrl_floor_minus_wo_design", "raven_ctrl_floor",
                            "raven_wo_design")):
        cfull = contrast(data, arm, ref, traces)
        c05 = contrast(data, arm, ref, keep)
        add_sens(f"{name}_hl", cfull["hl"], c05["hl"])
        add_sens(f"{name}_wilcoxon_p", cfull["wilcoxon_p"], c05["wilcoxon_p"])
    for name, armset in (("SEC_dose_slope_all6", ARMS), ("SEC_dose_slope_raven_arms",
                                                         LEVEL_ARMS)):
        d0 = dose(armset)
        # recompute the no-32005 slope on the same arm set (point estimate only)
        xs, ys = [], []
        for a in armset:
            xs.append(rho_of(data, a, keep))
            ys.append(tmean(data, a, "RMSE_mu", keep))
        d1 = float(np.polyfit(np.concatenate(xs), np.concatenate(ys), 1)[0])
        add_sens(f"{name}", d0["slope"], d1)
    for arm in CHAIN_ARMS:
        cfull = chain_contrasts[arm]
        t_g = tmean(data, arm, "Delta_group", keep) - tmean(data, REF, "Delta_group", keep)
        p_h1 = float(stats.wilcoxon(t_g, alternative="less").pvalue)
        c05 = contrast(data, arm, REF, keep)
        add_sens(f"A1CHAIN_{arm}_H1_p", cfull["p_h1"], p_h1)
        add_sens(f"A1CHAIN_{arm}_H2_hl", cfull["c"]["hl"], c05["hl"])
        add_sens(f"A1CHAIN_{arm}_H2_ub95", cfull["c"]["wilcoxon_inverted_hi"],
                 c05["wilcoxon_inverted_hi"])
        add_sens(f"A1CHAIN_{arm}_H3_lb95", cfull["c"]["wilcoxon_inverted_lo"],
                 c05["wilcoxon_inverted_lo"])
    for a in ARMS:
        add_sens(f"ARM_{a}_RMSE_mu_mean", float(np.mean(tmean(data, a, "RMSE_mu", traces))),
                 float(np.mean(tmean(data, a, "RMSE_mu", keep))))
        add_sens(f"ARM_{a}_Delta_group_mean",
                 float(np.mean(tmean(data, a, "Delta_group", traces))),
                 float(np.mean(tmean(data, a, "Delta_group", keep))))
        add_sens(f"ARM_{a}_WorstGroupRMSE_mean",
                 float(np.mean(tmean(data, a, "WorstGroupRMSE", traces))),
                 float(np.mean(tmean(data, a, "WorstGroupRMSE", keep))))
    gain_fed05 = float(np.mean(tmean(data, REF, "Delta_group", keep))
                       - np.mean(tmean(data, "raven_ctrl", "Delta_group", keep)))
    gain_fl05 = float(np.mean(tmean(data, REF, "Delta_group", keep))
                      - np.mean(tmean(data, "raven_ctrl_floor", "Delta_group", keep)))
    add_sens("GUARDRAIL_dgroup_gain_retained_share", retained,
             (gain_fl05 / gain_fed05) if gain_fed05 > 0 else None)
    write_csv(OUT / "C1_SENSITIVITY_NO32005.csv", sens_rows)

    # ------------------------------------------------ console (ASCII)
    print("=== primary H_mech (raven_ctrl / raven_ctrl_floor - 1, trace-level means) ===")
    print("  HL=%+.6f  pctCI=[%+.6f, %+.6f]  wilcoxon_p=%.4g  n=%d r=%d"
          % (prim["hl"], prim["ci95_lo"], prim["ci95_hi"], prim["wilcoxon_p"],
             prim["n_traces"], R))
    print("  reading:", reading)
    print("  guardrail: retained share = %s  (fed gain %.6f, floor gain %.6f)"
          % ("TBD" if retained is None else "%.4f" % retained, gain_fed, gain_floor))
    print("=== secondary family (Holm, m=4) ===")
    for row in sec:
        pv = row.get("wilcoxon_p") or row.get("bootstrap_p", "")
        print("  %-38s hl=%-12s ci=[%s, %s] p=%-12s rank=%s thr=%s rej=%s"
              % (row["member"], row.get("hl_rel_diff", row.get("slope", "")),
                 row.get("ci95_lo", ""), row.get("ci95_hi", ""), pv,
                 row["holm_rank"], row["holm_threshold"], row["holm_reject"]))
    print("=== primary power diagnostic (post hoc, required by B3) ===")
    print(" ", json.dumps(primary["power_diagnostic"], default=str))
    print("=== A1 chains (K=3 graphical alpha) ===")
    for row in chain_rows:
        print("  %-18s H1p=%-12s rej=%-5s HL=%+.5f ub95=%+.5f aH1=%.5f aH2=%.5f dCS=%s "
              "H2rej=%-5s H3=%-28s"
              % (row["arm"], row["H1_p"], row["H1_reject"], float(row["H2_hl"]),
                 float(row["H2_ub95"]), row["alpha_H1_allocated"],
                 row["alpha_H2_allocated"] if row["alpha_H2_allocated"] is not None else float("nan"),
                 row["delta_CS"], row["H2_reject"], row["H3_reject"]))
    print("=== A1 graph check ===")
    print(" ", json.dumps(a1_check, default=str))
    print("=== per-arm trace-level means ===")
    for row in arm_summary:
        print("  %-18s rho=%.4f RMSE=%.4f WG=%.4f Dg=%.4f Dcs=%.4f"
              % (row["arm"], row["rho_realized_mean"], row["RMSE_mu_mean"],
                 row["WorstGroupRMSE_mean"], row["Delta_group_mean"], row["Delta_c_s_mean"]))
    print("=== sensitivity no-32005 (primary rows) ===")
    for r in sens_rows[:4]:
        print("  %-32s full=%-14s no32005=%-14s" % (r["estimate"], r["value_full_set"],
                                                    r["value_no32005"]))

    (OUT / "C1_ANALYSIS_PROVENANCE.json").write_text(
        json.dumps({"provenance": prov, "a1_graph_crosscheck": a1_check,
                    "primary": {k: primary[k] for k in TEMPLATE_PRIMARY},
                    "secondary_family": sec, "a1_chains": chain_rows,
                    "n_sensitivity_rows": len(sens_rows)},
                   indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
