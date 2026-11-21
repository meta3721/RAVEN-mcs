#!/usr/bin/env python3
"""P1 deployment-consequence audit: group under-service from existing artifacts.

Does not retrain. Reconstructs per-window mix omega_r on the persisted
Delta_c-s support (client x opportunity_stratum) from delta_cs_state_v6.parquet.

Inventory (do not assume P2):
- Formal E3 has no p2_invocation_states.json.
- Side-path FedAU/ObsUse and drifting dumps p2, but it is empty except RAVEN.
- RAVEN drifting p2 has M (n_groups x n_active), alpha, mu, debt; no omega.
  Formal RAVEN cannot be compared on that 220-D group omega.
- window_metrics.json stores alpha/active_clients only (no omega, no M, no debt).
- ledger.jsonl is START/FINISH only.
- Therefore metric A uses parquet atomic_contribution, which already sums to 1
  per active window and is the realized Pi-hat increment on (k,s).

Under-service definition:
  pair g is under-served in window r iff omega_r(g) < 0.5 * mu_g.
  Rationale: half the public target share is a conservative 'effectively
  represented' cutoff. Because a delivered pair typically receives ~alpha
  (O(0.1)) while 0.5*mu_g is O(10^-3), the rule is essentially a coverage
  indicator. Never-delivered target pairs are omega=0 and count as
  under-served; pairs that never appear in any method add a constant and
  do not change paired method comparisons, so the common universe is the
  union of pairs observed in any of the five methods for that seed.

Metric B (worst-group test RMSE) is NOT computed: no per-group test RMSE is
persisted, and Tail_RMSE is not a worst-group substitute.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from raven_mcs.e3.formal.constants import FORMAL_SEEDS
from raven_mcs.e3.formal.stats import holm, paired_summary, summarize_vector

THRESH_FRAC = 0.5
PERSIST_RATE = 0.5
DATASETS = ("sensorscope", "uair")
SCENARIOS = ("complete_aligned", "drifting")
METHODS = (
    "fedavg_window",
    "fedau_window",
    "obsuse_window",
    "twostage_hajek",
    "raven",
)
DISPLAY = {
    "fedavg_window": "FedAvg-Window",
    "fedau_window": "FedAU-Window",
    "obsuse_window": "ObsUse-Window",
    "twostage_hajek": "TwoStage-Hajek",
    "raven": "RAVEN-MCS",
}
SEED_METRICS = (
    "underservice_events",
    "underservice_mass",
    "n_persist_groups",
    "n_pairs",
    "n_windows",
)
OUT_DIR = _ROOT / "_paper_work" / "deployment_consequence_results"


def run_dir(scenario: str, dataset: str, method: str, seed: int) -> Path:
    if scenario == "drifting":
        root = _ROOT / "artifacts" / "e3_drifting_r1" / "runs"
    elif method == "fedau_window":
        root = _ROOT / "artifacts" / "e3_fedau_window_r1" / "runs"
    elif method == "obsuse_window":
        root = _ROOT / "artifacts" / "e3_obsuse_window_r1" / "runs"
    else:
        root = _ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
    return root / dataset / method / f"seed{seed}"


def parquet_path(scenario: str, dataset: str, method: str, seed: int) -> Path:
    return run_dir(scenario, dataset, method, seed) / "delta_cs_state_v6.parquet"


def inventory() -> dict:
    rows = []
    for scenario in SCENARIOS:
        for dataset in DATASETS:
            for method in METHODS:
                for seed in FORMAL_SEEDS:
                    d = run_dir(scenario, dataset, method, seed)
                    p2 = d / "p2_invocation_states.json"
                    p2_n = None
                    p2_has_m = False
                    if p2.is_file():
                        payload = json.loads(p2.read_text(encoding="utf-8"))
                        p2_n = len(payload) if isinstance(payload, list) else None
                        if payload and isinstance(payload[0], dict):
                            p2_has_m = payload[0].get("M") is not None
                    wm = d / "window_metrics.json"
                    wm_keys = None
                    if wm.is_file():
                        recs = json.loads(wm.read_text(encoding="utf-8"))
                        if recs:
                            wm_keys = sorted(recs[0].keys())
                    rows.append(
                        {
                            "scenario": scenario,
                            "dataset": dataset,
                            "method": method,
                            "seed": int(seed),
                            "run_exists": d.is_dir(),
                            "parquet": (d / "delta_cs_state_v6.parquet").is_file(),
                            "window_metrics": wm.is_file(),
                            "window_metrics_keys": wm_keys,
                            "p2_exists": p2.is_file(),
                            "p2_n": p2_n,
                            "p2_has_M": p2_has_m,
                            "ledger": (d / "ledger.jsonl").is_file(),
                            "checkpoint": (d / "checkpoints" / "final.pt").is_file(),
                        }
                    )
    return pd.DataFrame(rows)


def _pair_id(client_id: str, stratum: str) -> str:
    return f"{client_id}::{stratum}"


def window_omega(frame: pd.DataFrame) -> pd.DataFrame:
    g = (
        frame.groupby(
            ["window", "client_id", "opportunity_stratum_id"],
            sort=False,
        )
        .agg(
            omega=("atomic_contribution", "sum"),
            mu=("target_client_stratum_mass", "max"),
        )
        .reset_index()
    )
    g["group_id"] = [
        _pair_id(c, s)
        for c, s in zip(g["client_id"], g["opportunity_stratum_id"])
    ]
    return g


def cell_under_service(
    scenario: str,
    dataset: str,
    seed: int,
    method_frames: dict[str, pd.DataFrame],
) -> tuple[list[dict], list[dict]]:
    """Return (group-level rows, seed-level rows) for one dataset/scenario/seed."""
    pair_mu: dict[str, float] = {}
    windows: set[int] = set()
    omegas: dict[str, pd.DataFrame] = {}
    for method, frame in method_frames.items():
        wo = window_omega(frame)
        omegas[method] = wo
        windows.update(int(w) for w in wo["window"].unique())
        for gid, mu in zip(wo["group_id"], wo["mu"]):
            prev = pair_mu.get(gid)
            if prev is None:
                pair_mu[gid] = float(mu)
            elif abs(prev - float(mu)) > 1e-9:
                raise ValueError(
                    f"target mass mismatch {dataset} {scenario} seed{seed} "
                    f"{gid}: {prev} vs {mu}"
                )
    n_windows = len(windows)
    n_pairs = len(pair_mu)
    group_rows: list[dict] = []
    seed_rows: list[dict] = []
    window_index = sorted(windows)
    groups = sorted(pair_mu)
    mu_vec = np.asarray([pair_mu[g] for g in groups], dtype=np.float64)
    thresh = THRESH_FRAC * mu_vec
    for method in METHODS:
        wo = omegas[method]
        mat = np.zeros((n_windows, n_pairs), dtype=np.float64)
        w_map = {w: i for i, w in enumerate(window_index)}
        g_map = {g: i for i, g in enumerate(groups)}
        for row in wo.itertuples(index=False):
            mat[w_map[int(row.window)], g_map[row.group_id]] = float(row.omega)
        under = mat < thresh[None, :]
        counts = under.sum(axis=0)
        mass = (under * mu_vec[None, :]).sum(axis=1).sum()
        events = int(under.sum())
        persist = int((counts / max(n_windows, 1) >= PERSIST_RATE).sum())
        shortfall = float(np.maximum(mu_vec[None, :] - mat, 0.0).sum())
        for gid, mu, cnt in zip(groups, mu_vec, counts):
            group_rows.append(
                {
                    "dataset": dataset,
                    "scenario": scenario,
                    "method": method,
                    "seed": int(seed),
                    "group_id": gid,
                    "mu": float(mu),
                    "n_windows": n_windows,
                    "underservice_windows": int(cnt),
                    "underservice_rate": float(cnt / n_windows) if n_windows else None,
                    "threshold_frac": THRESH_FRAC,
                }
            )
        seed_rows.append(
            {
                "dataset": dataset,
                "scenario": scenario,
                "method": method,
                "seed": int(seed),
                "n_windows": n_windows,
                "n_pairs": n_pairs,
                "underservice_events": events,
                "underservice_mass": float(mass),
                "n_persist_groups": persist,
                "shortfall_l1": shortfall,
                "mean_served_pairs": float((mat >= thresh[None, :]).sum(axis=1).mean())
                if n_windows
                else None,
                "threshold_frac": THRESH_FRAC,
                "status": "OK",
            }
        )
    return group_rows, seed_rows


def collect() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    missing: list[str] = []
    group_rows: list[dict] = []
    seed_rows: list[dict] = []
    for scenario in SCENARIOS:
        for dataset in DATASETS:
            for seed in FORMAL_SEEDS:
                frames: dict[str, pd.DataFrame] = {}
                cell_ok = True
                for method in METHODS:
                    path = parquet_path(scenario, dataset, method, seed)
                    if not path.is_file():
                        missing.append(str(path))
                        cell_ok = False
                        continue
                    frames[method] = pd.read_parquet(path)
                if not cell_ok:
                    for method in METHODS:
                        seed_rows.append(
                            {
                                "dataset": dataset,
                                "scenario": scenario,
                                "method": method,
                                "seed": int(seed),
                                "status": "MISSING",
                                "underservice_events": None,
                                "underservice_mass": None,
                                "n_persist_groups": None,
                                "n_pairs": None,
                                "n_windows": None,
                            }
                        )
                    continue
                g_rows, s_rows = cell_under_service(
                    scenario, dataset, seed, frames
                )
                group_rows.extend(g_rows)
                seed_rows.extend(s_rows)
    return pd.DataFrame(group_rows), pd.DataFrame(seed_rows), missing


def _seed_map(frame: pd.DataFrame, dataset: str, scenario: str, method: str, metric: str) -> dict[int, float]:
    sub = frame[
        (frame["dataset"] == dataset)
        & (frame["scenario"] == scenario)
        & (frame["method"] == method)
        & (frame["status"] == "OK")
    ]
    out: dict[int, float] = {}
    for row in sub.itertuples(index=False):
        val = getattr(row, metric)
        if val is None or (isinstance(val, float) and not math.isfinite(val)):
            continue
        out[int(row.seed)] = float(val)
    return out


def stats_tables(seed_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    holm_rows = []
    comparisons = (
        ("raven", "fedau_window", "raven_vs_fedau"),
        ("raven", "obsuse_window", "raven_vs_obsuse"),
        ("raven", "fedavg_window", "raven_vs_fedavg"),
    )
    specified = {"raven_vs_fedau"}
    primary = "underservice_events"
    diagnostic_metrics = ("underservice_mass", "n_persist_groups", "shortfall_l1")
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            for method in METHODS:
                sub = seed_frame[
                    (seed_frame["dataset"] == dataset)
                    & (seed_frame["scenario"] == scenario)
                    & (seed_frame["method"] == method)
                    & (seed_frame["status"] == "OK")
                ]
                for metric in (
                    "underservice_events",
                    "underservice_mass",
                    "n_persist_groups",
                    "shortfall_l1",
                    "mean_served_pairs",
                    "n_pairs",
                    "n_windows",
                ):
                    vals = [float(v) for v in sub[metric].tolist() if pd.notna(v)]
                    stats = summarize_vector(vals)
                    summary_rows.append(
                        {
                            "dataset": dataset,
                            "scenario": scenario,
                            "method": method,
                            "metric": metric,
                            **stats,
                        }
                    )
            for metric, role in (
                (primary, "specified"),
                *[(m, "diagnostic") for m in diagnostic_metrics],
            ):
                packed: dict[str, dict] = {}
                family: dict[str, float] = {}
                for left, right, name in comparisons:
                    a = _seed_map(seed_frame, dataset, scenario, left, metric)
                    b = _seed_map(seed_frame, dataset, scenario, right, metric)
                    if len(set(a) & set(b)) < 2:
                        packed[name] = {"n": len(set(a) & set(b)), "p_raw": None, "test_status": "INSUFFICIENT"}
                        continue
                    summary = paired_summary(a, b)
                    packed[name] = summary
                    family[name] = float(summary["p_raw"])
                adjusted = holm(family) if family else {}
                for name, summary in packed.items():
                    holm_rows.append(
                        {
                            "dataset": dataset,
                            "scenario": scenario,
                            "metric": metric,
                            "comparison": name,
                            "holm_family": f"{dataset}:{scenario}:{metric}:3comparisons",
                            "family_role": "specified"
                            if (role == "specified" and name in specified)
                            else ("specified_family" if role == "specified" else "diagnostic"),
                            "n": summary.get("n"),
                            "mean_diff_left_minus_right": summary.get(
                                "mean_diff_raven_minus_baseline"
                            ),
                            "effect_size": summary.get("effect_size"),
                            "wins": summary.get("wins"),
                            "ties": summary.get("ties"),
                            "losses": summary.get("losses"),
                            "p_raw": summary.get("p_raw"),
                            "p_holm": adjusted.get(name),
                            "test_status": summary.get("test_status"),
                            "significant_holm_0.05": (
                                False
                                if adjusted.get(name) is None
                                else float(adjusted[name]) < 0.05
                                and float(summary.get("mean_diff_raven_minus_baseline", 0.0)) < 0
                            ),
                            "raven_lower_holm": (
                                False
                                if adjusted.get(name) is None
                                else float(adjusted[name]) < 0.05
                                and float(summary.get("mean_diff_raven_minus_baseline", 0.0)) < 0
                            ),
                            "baseline_lower_holm": (
                                False
                                if adjusted.get(name) is None
                                else float(adjusted[name]) < 0.05
                                and float(summary.get("mean_diff_raven_minus_baseline", 0.0)) > 0
                            ),
                        }
                    )
    return pd.DataFrame(summary_rows), pd.DataFrame(holm_rows)


def _fmt_p(p) -> str:
    if p is None or (isinstance(p, float) and not math.isfinite(p)):
        return "NA"
    p = float(p)
    if p < 1e-4:
        return f"{p:.3e}"
    return f"{p:.4f}"


def write_conclusion(holm_frame: pd.DataFrame, summary_frame: pd.DataFrame, missing: list[str], inv: pd.DataFrame) -> str:
    lines = []
    lines.append("Deployment-consequence audit (complete_aligned + drifting, 20 seeds).")
    lines.append("Support: client x opportunity_stratum from delta_cs_state_v6.parquet.")
    lines.append(
        f"Under-service: omega_r(g) < {THRESH_FRAC} * mu_g; "
        "persistently under-served if rate >= 0.5 of active windows."
    )
    lines.append("Metric B worst-group test RMSE: NOT COMPUTED (not persisted; Tail_RMSE not used).")
    lines.append("")
    lines.append("INVENTORY")
    lines.append(
        f"- parquet cells: {int(inv['parquet'].sum())}/{len(inv)}; "
        f"missing parquet paths: {len(missing)}"
    )
    lines.append(
        f"- p2 present: {int(inv['p2_exists'].sum())}/{len(inv)}; "
        f"p2 with M: {int(inv['p2_has_M'].sum())}/{len(inv)} "
        "(RAVEN drifting/side-path only; formal E3 has no p2 file)"
    )
    wm_keys = inv.loc[inv["window_metrics_keys"].notna(), "window_metrics_keys"]
    if len(wm_keys):
        lines.append(f"- window_metrics keys (first non-null): {wm_keys.iloc[0]}")
    lines.append("- ledger: START/FINISH only; no per-window omega/debt.")
    lines.append("")
    lines.append("Group under-service accumulation (underservice_events = sum_g count_g):")
    core = holm_frame[holm_frame["metric"] == "underservice_events"]
    raven_better = 0
    raven_worse = 0
    n_core = 0
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            for cmp_name, label in (
                ("raven_vs_fedau", "FedAU"),
                ("raven_vs_obsuse", "ObsUse"),
                ("raven_vs_fedavg", "FedAvg"),
            ):
                row = core[
                    (core["dataset"] == dataset)
                    & (core["scenario"] == scenario)
                    & (core["comparison"] == cmp_name)
                ]
                if row.empty:
                    lines.append(f"- {dataset} {scenario} vs {label}: MISSING")
                    continue
                r = row.iloc[0]
                n_core += 1
                if bool(r["raven_lower_holm"]):
                    raven_better += 1
                    tag = "Holm-sig RAVEN lower"
                elif bool(r["baseline_lower_holm"]):
                    raven_worse += 1
                    tag = "Holm-sig baseline lower"
                elif float(r["mean_diff_left_minus_right"]) < 0:
                    tag = "RAVEN numerically lower, not Holm-sig"
                else:
                    tag = "RAVEN numerically higher, not Holm-sig"
                lines.append(
                    f"- {dataset} {scenario} vs {label}: {tag}, "
                    f"mean_diff={float(r['mean_diff_left_minus_right']):.4f}, "
                    f"wins={r['wins']}/ties={r['ties']}/losses={r['losses']}, "
                    f"p_holm={_fmt_p(r['p_holm'])}"
                )
    lines.append("")
    lines.append("Means (underservice_events):")
    sub = summary_frame[summary_frame["metric"] == "underservice_events"]
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            bits = []
            for method in METHODS:
                row = sub[
                    (sub["dataset"] == dataset)
                    & (sub["scenario"] == scenario)
                    & (sub["method"] == method)
                ]
                if row.empty or row.iloc[0]["mean"] is None:
                    bits.append(f"{DISPLAY[method]}=NA")
                else:
                    r = row.iloc[0]
                    bits.append(
                        f"{DISPLAY[method]}={float(r['mean']):.2f}+/-{float(r['std']):.2f}"
                    )
            lines.append(f"- {dataset} {scenario}: " + "; ".join(bits))
    lines.append("")
    # drift amplification vs complete_aligned
    lines.append("Drift vs complete_aligned (RAVEN minus FedAU mean underservice_events):")
    for dataset in DATASETS:
        diffs = {}
        for scenario in SCENARIOS:
            row = core[
                (core["dataset"] == dataset)
                & (core["scenario"] == scenario)
                & (core["comparison"] == "raven_vs_fedau")
            ]
            diffs[scenario] = (
                float(row.iloc[0]["mean_diff_left_minus_right"]) if not row.empty else float("nan")
            )
        larger = (
            "YES, |gap| larger under drift"
            if abs(diffs["drifting"]) > abs(diffs["complete_aligned"])
            else "NO, |gap| not larger under drift"
        )
        lines.append(
            f"- {dataset}: complete_aligned {diffs['complete_aligned']:.4f}, "
            f"drifting {diffs['drifting']:.4f} -> {larger}"
        )
    lines.append("")
    lines.append("Author verdict (honest):")
    if raven_better == n_core and n_core > 0:
        lines.append(
            "- YES: RAVEN accumulates fewer under-served client-stratum groups "
            "than FedAU / ObsUse / FedAvg on both datasets and both scenarios "
            "(Holm-significant on the specified underservice_events family)."
        )
        lines.append(
            "- This supports a deployment-consequence reading of the Delta_c-s "
            "advantage: worse stratum alignment corresponds to more windows in "
            "which target pairs receive less than half their public share."
        )
        support = "SUPPORT"
    elif raven_better > 0 and raven_worse == 0:
        lines.append(
            f"- MIXED: RAVEN is Holm-significantly lower on {raven_better}/{n_core} "
            "dataset-scenario-baseline comparisons; none favor the baseline."
        )
        lines.append(
            "- This partially supports a deployment-consequence reading, but not "
            "a blanket claim that structural alignment always yields fewer "
            "under-served groups against every baseline."
        )
        support = "PARTIAL"
    else:
        lines.append(
            f"- NOT SUPPORTED as a uniform deployment gain: Holm RAVEN-lower "
            f"{raven_better}/{n_core}, Holm baseline-lower {raven_worse}/{n_core}."
        )
        lines.append(
            "- Do not claim that the Delta_c-s advantage translates into fewer "
            "persistently under-served deployment groups."
        )
        support = "NOT_SUPPORTED"
    lines.append(f"- VERDICT_CODE={support}")
    lines.append(
        "- Do not claim empirical proof of ||Q_R||_1=o(S_R); this audit is a "
        "coverage-count analogue of under-service, not the debt recursion."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inv = inventory()
    inv.to_csv(OUT_DIR / "inventory.csv", index=False)
    group_df, seed_df, missing = collect()
    group_df.to_csv(OUT_DIR / "under_service.csv", index=False)
    seed_df.to_csv(OUT_DIR / "under_service_seed.csv", index=False)
    summary_df, holm_df = stats_tables(seed_df)
    summary_df.to_csv(OUT_DIR / "summary.csv", index=False)
    holm_df.to_csv(OUT_DIR / "holm.csv", index=False)
    text = write_conclusion(holm_df, summary_df, missing, inv)
    (OUT_DIR / "conclusion.txt").write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {OUT_DIR}")
    print(f"missing parquet: {len(missing)}")
    print(f"group rows: {len(group_df)}; seed rows: {len(seed_df)}")


if __name__ == "__main__":
    main()
