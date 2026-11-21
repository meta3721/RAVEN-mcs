"""Summaries, crossing brackets, and routing classification for R1i. Post-oracle only."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from raven_mcs.sag.availability_stress import (
    A_GRID,
    BOUNDARY_NEAR_MARGIN,
    BOUNDARY_RICH_MIN_SAFE,
    BOUNDARY_RICH_MIN_UNSAFE,
    BOUNDARY_RICH_SAFE_HI,
    BOUNDARY_RICH_SAFE_LO,
    MIN_CROSSING_WINDOWS,
    MONO_TOL,
    TINY_CLUSTER_MAX,
)


def _quantile(xs: Sequence[float], q: float) -> float:
    arr = np.asarray([float(x) for x in xs if np.isfinite(float(x))], dtype=np.float64)
    if not len(arr):
        return float("nan")
    return float(np.quantile(arr, q))


def contiguous_runs(ids: Sequence[int]) -> list[list[int]]:
    ordered = sorted({int(i) for i in ids})
    if not ordered:
        return []
    runs = [[ordered[0]]]
    for x in ordered[1:]:
        if x == runs[-1][-1] + 1:
            runs[-1].append(x)
        else:
            runs.append([x])
    return runs


def concentration_flags(
    window_ids: Sequence[int],
    *,
    is_edge: Mapping[int, bool],
    is_complete: Mapping[int, bool],
) -> dict[str, Any]:
    ids = sorted({int(i) for i in window_ids})
    if not ids:
        return {
            "all_split_edge": False,
            "single_tiny_cluster": False,
            "all_partial": False,
            "n_contiguous_runs": 0,
            "concentrated": False,
        }
    all_edge = all(bool(is_edge.get(i, False)) for i in ids)
    runs = contiguous_runs(ids)
    single_tiny = len(runs) == 1 and len(ids) <= TINY_CLUSTER_MAX
    all_partial = all(not bool(is_complete.get(i, True)) for i in ids)
    return {
        "all_split_edge": all_edge,
        "single_tiny_cluster": single_tiny,
        "all_partial": all_partial,
        "n_contiguous_runs": len(runs),
        "concentrated": bool(all_edge or single_tiny or all_partial),
    }


def summarize_levels(stress: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (dataset, a), sub in stress.groupby(["dataset", "availability_level"], sort=True):
        c_real = sub["C_real_support"].astype(float)
        c_ora = sub["C_oracle_safe"].astype(float)
        margin = sub["oracle_margin"].astype(float)
        n_safe = int(sub["oracle_safe"].astype(bool).sum())
        n = int(len(sub))
        n_unsafe = n - n_safe
        rows.append(
            {
                "dataset": dataset,
                "availability_level": float(a),
                "n_windows": n,
                "mean_C_real_support": float(c_real.mean()),
                "median_C_real_support": float(c_real.median()),
                "p10_C_real_support": _quantile(c_real.tolist(), 0.10),
                "p90_C_real_support": _quantile(c_real.tolist(), 0.90),
                "mean_C_oracle_safe": float(c_ora.mean()),
                "median_C_oracle_safe": float(c_ora.median()),
                "p10_C_oracle_safe": _quantile(c_ora.tolist(), 0.10),
                "p90_C_oracle_safe": _quantile(c_ora.tolist(), 0.90),
                "min_C_oracle_safe": float(c_ora.min()),
                "max_C_oracle_safe": float(c_ora.max()),
                "n_safe": n_safe,
                "n_unsafe": n_unsafe,
                "fraction_safe": float(n_safe / n) if n else float("nan"),
                "fraction_unsafe": float(n_unsafe / n) if n else float("nan"),
                "median_oracle_margin": float(margin.median()),
                "p10_oracle_margin": _quantile(margin.tolist(), 0.10),
                "p90_oracle_margin": _quantile(margin.tolist(), 0.90),
            }
        )
    return pd.DataFrame(rows)


def crossing_brackets(stress: pd.DataFrame) -> pd.DataFrame:
    levels = sorted((float(a) for a in A_GRID), reverse=True)
    rows: list[dict[str, Any]] = []
    for (dataset, wid), sub in stress.groupby(["dataset", "window_id"], sort=True):
        by_a = {float(r.availability_level): r for r in sub.itertuples(index=False)}
        natural = by_a.get(1.00)
        natural_safe = bool(natural.oracle_safe) if natural is not None else False
        a_high = a_low = None
        c_high = c_low = m_high = m_low = None
        notes = []
        for hi, lo in zip(levels, levels[1:]):
            if hi not in by_a or lo not in by_a:
                continue
            if bool(by_a[hi].oracle_safe) and (not bool(by_a[lo].oracle_safe)):
                a_high, a_low = hi, lo
                c_high = float(by_a[hi].C_oracle_safe)
                c_low = float(by_a[lo].C_oracle_safe)
                m_high = float(by_a[hi].oracle_margin)
                m_low = float(by_a[lo].oracle_margin)
                break
        if a_high is None:
            if natural is not None and not natural_safe:
                notes.append("already_unsafe_at_a=1.00")
            elif natural is not None and all(bool(by_a[a].oracle_safe) for a in levels if a in by_a):
                notes.append("still_safe_at_a=0.20")
            else:
                notes.append("no_adjacent_safe_to_unsafe_bracket")
        rows.append(
            {
                "dataset": dataset,
                "window_id": int(wid),
                "natural_safe": natural_safe,
                "crossing_exists": a_high is not None,
                "a_safe_high": a_high if a_high is not None else float("nan"),
                "a_unsafe_low": a_low if a_low is not None else float("nan"),
                "C_oracle_safe_at_high": c_high if c_high is not None else float("nan"),
                "C_oracle_safe_at_low": c_low if c_low is not None else float("nan"),
                "margin_high": m_high if m_high is not None else float("nan"),
                "margin_low": m_low if m_low is not None else float("nan"),
                "notes": ";".join(notes),
            }
        )
    return pd.DataFrame(rows)


def classify_boundary_rich(
    summary: pd.DataFrame,
    stress: pd.DataFrame,
    completeness: pd.DataFrame,
) -> pd.DataFrame:
    edge = {}
    complete = {}
    for r in completeness.itertuples(index=False):
        key = (str(r.dataset), int(r.window_id))
        edge[key] = bool(r.is_first_n_window) or bool(r.is_last_n_window)
        complete[key] = bool(r.is_complete_by_rule)
    rows: list[dict[str, Any]] = []
    for r in summary.itertuples(index=False):
        dataset = str(r.dataset)
        a = float(r.availability_level)
        sub = stress.loc[(stress["dataset"] == dataset) & (np.isclose(stress["availability_level"].astype(float), a))]
        safe_ids = [int(w) for w in sub.loc[sub["oracle_safe"].astype(bool), "window_id"].tolist()]
        unsafe_ids = [int(w) for w in sub.loc[~sub["oracle_safe"].astype(bool), "window_id"].tolist()]
        e_map = {i: edge.get((dataset, i), False) for i in safe_ids + unsafe_ids}
        c_map = {i: complete.get((dataset, i), True) for i in safe_ids + unsafe_ids}
        flags_u = concentration_flags(unsafe_ids, is_edge=e_map, is_complete=c_map)
        flags_s = concentration_flags(safe_ids, is_edge=e_map, is_complete=c_map)
        frac = float(r.fraction_safe)
        band = BOUNDARY_RICH_SAFE_LO <= frac <= BOUNDARY_RICH_SAFE_HI
        counts = int(r.n_safe) >= BOUNDARY_RICH_MIN_SAFE and int(r.n_unsafe) >= BOUNDARY_RICH_MIN_UNSAFE
        rich = band and counts and (not flags_u["concentrated"])
        if flags_s["all_partial"] and flags_u["all_partial"]:
            rich = False
        rows.append(
            {
                "dataset": dataset,
                "availability_level": a,
                "fraction_safe": frac,
                "n_safe": int(r.n_safe),
                "n_unsafe": int(r.n_unsafe),
                "in_band": band,
                "unsafe_all_split_edge": flags_u["all_split_edge"],
                "unsafe_tiny_cluster": flags_u["single_tiny_cluster"],
                "unsafe_all_partial": flags_u["all_partial"],
                "BOUNDARY_RICH": bool(rich),
            }
        )
    return pd.DataFrame(rows)


def boundary_near_rows(stress: pd.DataFrame) -> pd.DataFrame:
    sub = stress.loc[stress["oracle_margin"].astype(float).abs() <= BOUNDARY_NEAR_MARGIN].copy()
    return sub


def monotonicity_audit(stress: pd.DataFrame) -> pd.DataFrame:
    levels = sorted(float(a) for a in A_GRID)
    rows: list[dict[str, Any]] = []
    for (dataset, wid), sub in stress.groupby(["dataset", "window_id"], sort=True):
        by_a = {float(r.availability_level): r for r in sub.itertuples(index=False)}
        for lo, hi in zip(levels, levels[1:]):
            if lo not in by_a or hi not in by_a:
                continue
            c_real_lo = float(by_a[lo].C_real_support)
            c_real_hi = float(by_a[hi].C_real_support)
            c_ora_lo = float(by_a[lo].C_oracle_safe)
            c_ora_hi = float(by_a[hi].C_oracle_safe)
            rows.append(
                {
                    "dataset": dataset,
                    "window_id": int(wid),
                    "a_low": lo,
                    "a_high": hi,
                    "C_real_low": c_real_lo,
                    "C_real_high": c_real_hi,
                    "C_oracle_low": c_ora_lo,
                    "C_oracle_high": c_ora_hi,
                    "real_monotone": c_real_lo <= c_real_hi + MONO_TOL,
                    "oracle_monotone": c_ora_lo <= c_ora_hi + MONO_TOL,
                }
            )
    return pd.DataFrame(rows)


def dataset_verdict(
    *,
    dataset: str,
    summary: pd.DataFrame,
    rich: pd.DataFrame,
    crossings: pd.DataFrame,
    n_mono_viol: int,
    baseline_ok: bool,
) -> dict[str, Any]:
    ds = summary.loc[summary["dataset"] == dataset]
    rich_ds = rich.loc[rich["dataset"] == dataset]
    n_rich = int(rich_ds["BOUNDARY_RICH"].astype(bool).sum())
    mild = bool(
        any(
            float(r.fraction_safe) >= 0.80
            for r in ds.itertuples(index=False)
            if abs(float(r.availability_level) - 1.00) < 1e-9 or abs(float(r.availability_level) - 0.80) < 1e-9
        )
    )
    severe = bool(
        any(
            float(r.fraction_safe) <= 0.20
            for r in ds.itertuples(index=False)
            if abs(float(r.availability_level) - 0.40) < 1e-9 or abs(float(r.availability_level) - 0.20) < 1e-9
        )
    )
    n_cross = int(crossings.loc[crossings["dataset"] == dataset, "crossing_exists"].astype(bool).sum())
    frac_by_a = {float(r.availability_level): float(r.fraction_safe) for r in ds.itertuples(index=False)}
    monotone_transition = True
    ordered = sorted(frac_by_a)
    for a_low, a_high in zip(ordered, ordered[1:]):
        if frac_by_a[a_high] + 1e-6 < frac_by_a[a_low]:
            monotone_transition = False
    all_safe = all(float(v) >= 0.99 for v in frac_by_a.values())
    all_unsafe = all(float(v) <= 0.01 for v in frac_by_a.values())
    if (not baseline_ok) or n_mono_viol > 0:
        label = "STRESS_IMPLEMENTATION_FAILURE"
    elif n_rich >= 1 and mild and severe and n_cross >= MIN_CROSSING_WINDOWS and monotone_transition:
        label = "BOUNDARY_USABLE"
    elif monotone_transition and n_cross >= 1 and not all_safe and not all_unsafe:
        label = "BOUNDARY_PARTIALLY_USABLE"
    else:
        label = "NO_BOUNDARY_CROSSING"
    return {
        "dataset": dataset,
        "verdict": label,
        "n_boundary_rich_levels": n_rich,
        "MILD_SAFE_EXISTS": mild,
        "SEVERE_UNSAFE_EXISTS": severe,
        "n_crossing_windows": n_cross,
        "monotone_transition": monotone_transition,
        "all_safe": all_safe,
        "all_unsafe": all_unsafe,
    }


def overall_verdict(by_dataset: Mapping[str, str], *, impl_fail: bool) -> str:
    if impl_fail or any(v == "STRESS_IMPLEMENTATION_FAILURE" for v in by_dataset.values()):
        return "R1I_STRESS_IMPLEMENTATION_FAILURE"
    vals = list(by_dataset.values())
    n_usable = sum(v == "BOUNDARY_USABLE" for v in vals)
    n_partial = sum(v == "BOUNDARY_PARTIALLY_USABLE" for v in vals)
    if n_usable == len(vals) and len(vals) >= 2:
        return "READY_FOR_DYNAMIC_CERTIFICATE_STRESS_AUDIT"
    if n_usable >= 1 and n_partial >= 1:
        return "READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT"
    if n_usable >= 1:
        return "READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT"
    return "R1I_STRESS_BOUNDARY_NOT_USABLE"
