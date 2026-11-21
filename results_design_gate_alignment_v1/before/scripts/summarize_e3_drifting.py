#!/usr/bin/env python3
"""Summarize drifting E3 family: per-seed, mean±std, Wilcoxon+Holm, honest conclusion."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from raven_mcs.e3.formal.constants import FORMAL_SEEDS
from raven_mcs.e3.formal.stats import holm, paired_summary, summarize_vector

ART = _ROOT / "artifacts" / "e3_drifting_r1"
OUT_DIR = _ROOT / "_paper_work" / "drifting_window_results"
DATASETS = ("sensorscope", "uair")
METHODS = (
    "fedavg_window",
    "fedau_window",
    "obsuse_window",
    "twostage_hajek",
    "raven",
)
METRICS = ("RMSE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s")
DISPLAY = {
    "fedavg_window": "FedAvg-Window",
    "fedau_window": "FedAU-Window",
    "obsuse_window": "ObsUse-Window",
    "twostage_hajek": "TwoStage-Hajek",
    "raven": "RAVEN-MCS",
}


def _metrics_path(dataset: str, method: str, seed: int) -> Path:
    return ART / "runs" / dataset / method / f"seed{seed}" / "final_metrics.json"


def collect_rows() -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        for method in METHODS:
            for seed in FORMAL_SEEDS:
                path = _metrics_path(dataset, method, seed)
                rec = {"dataset": dataset, "method": method, "seed": int(seed)}
                if not path.is_file():
                    rec["status"] = "MISSING"
                    for m in METRICS:
                        rec[m] = None
                    rec["Q_norm1_over_S"] = None
                    rows.append(rec)
                    continue
                payload = json.loads(path.read_text(encoding="utf-8"))
                rec["status"] = "OK"
                for m in METRICS:
                    rec[m] = payload.get(m)
                rec["Q_norm1_over_S"] = payload.get("Q_norm1_over_S")
                rows.append(rec)
    return pd.DataFrame(rows)


def _seed_map(frame: pd.DataFrame, dataset: str, method: str, metric: str) -> dict[int, float]:
    sub = frame[(frame["dataset"] == dataset) & (frame["method"] == method)]
    out: dict[int, float] = {}
    for row in sub.itertuples(index=False):
        val = getattr(row, metric)
        if val is None or (isinstance(val, float) and not math.isfinite(val)):
            continue
        out[int(row.seed)] = float(val)
    return out


def stats_table(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    holm_rows = []
    comparisons = (
        ("raven", "fedau_window", "raven_vs_fedau"),
        ("raven", "fedavg_window", "raven_vs_fedavg"),
        ("raven", "obsuse_window", "raven_vs_obsuse"),
        ("raven", "twostage_hajek", "raven_vs_twostage"),
    )
    specified = {"raven_vs_fedau", "raven_vs_fedavg"}
    for dataset in DATASETS:
        packed: dict[tuple[str, str], dict] = {}
        families: dict[str, dict[str, float]] = {name: {} for _, _, name in comparisons}
        for metric in METRICS:
            for left, right, name in comparisons:
                a = _seed_map(frame, dataset, left, metric)
                b = _seed_map(frame, dataset, right, metric)
                if len(set(a) & set(b)) < 2:
                    packed[(name, metric)] = {
                        "n": len(set(a) & set(b)),
                        "p_raw": None,
                        "test_status": "INSUFFICIENT",
                    }
                    continue
                summary = paired_summary(a, b)
                packed[(name, metric)] = summary
                families[name][metric] = float(summary["p_raw"])
        adjusted = {name: holm(family) for name, family in families.items() if family}
        for (name, metric), summary in packed.items():
            p_holm = (adjusted.get(name) or {}).get(metric)
            holm_rows.append(
                {
                    "dataset": dataset,
                    "metric": metric,
                    "comparison": name,
                    "holm_family": f"{dataset}:{name}:4metrics",
                    "family_role": "specified" if name in specified else "diagnostic",
                    "n": summary.get("n"),
                    "mean_diff_left_minus_right": summary.get(
                        "mean_diff_raven_minus_baseline"
                    ),
                    "effect_size": summary.get("effect_size"),
                    "wins": summary.get("wins"),
                    "ties": summary.get("ties"),
                    "losses": summary.get("losses"),
                    "p_raw": summary.get("p_raw"),
                    "p_holm": p_holm,
                    "test_status": summary.get("test_status"),
                    "significant_holm_0.05": (
                        p_holm is not None and float(p_holm) < 0.05
                    ),
                }
            )
        for method in METHODS:
            sub = frame[(frame["dataset"] == dataset) & (frame["method"] == method)]
            for metric in METRICS:
                vals = [
                    float(v)
                    for v in sub[metric].tolist()
                    if v is not None and math.isfinite(float(v))
                ]
                packed_sum = summarize_vector(vals)
                summary_rows.append(
                    {
                        "dataset": dataset,
                        "method": method,
                        "metric": metric,
                        **packed_sum,
                    }
                )
            qvals = [
                float(v)
                for v in sub["Q_norm1_over_S"].tolist()
                if v is not None and math.isfinite(float(v))
            ]
            if qvals:
                packed_q = summarize_vector(qvals)
                summary_rows.append(
                    {
                        "dataset": dataset,
                        "method": method,
                        "metric": "Q_norm1_over_S",
                        **packed_q,
                    }
                )
    return pd.DataFrame(summary_rows), pd.DataFrame(holm_rows)


def _hit(holm_frame: pd.DataFrame, dataset: str, comparison: str, metric: str):
    sub = holm_frame[
        (holm_frame["dataset"] == dataset)
        & (holm_frame["comparison"] == comparison)
        & (holm_frame["metric"] == metric)
    ]
    return None if sub.empty else sub.iloc[0]


def _fmt_cmp(row) -> str:
    if row is None or row.get("p_holm") is None:
        return "TBD"
    sig = bool(row["significant_holm_0.05"])
    lower = float(row["mean_diff_left_minus_right"]) < 0
    return (
        f"{'significant' if sig else 'not significant'}, "
        f"RAVEN_lower={lower}, mean_diff={float(row['mean_diff_left_minus_right']):.4f}, "
        f"p_holm={float(row['p_holm']):.4g}, wins={row.get('wins')}/20"
    )


def conclusion(summary: pd.DataFrame, holm_frame: pd.DataFrame, frame: pd.DataFrame) -> str:
    bits = [
        "Drifting scenario (drift_period=50, drift_magnitude=0.1), 20 paired seeds 30001-30020.",
        "Traces: R3 complete_aligned protocol + opportunity drift; no sealed drifting traces existed.",
        "Holm families (specified): raven_vs_fedau and raven_vs_fedavg, 4 metrics each per dataset.",
        "Diagnostic families: raven_vs_obsuse, raven_vs_twostage (same Holm protocol, labeled diagnostic).",
        "",
    ]
    raven_struct_wins = []
    raven_pred_losses = []
    for dataset in DATASETS:
        bits.append(f"{dataset}:")
        for metric in METRICS:
            bits.append(f"  RAVEN vs FedAU ({metric}): {_fmt_cmp(_hit(holm_frame, dataset, 'raven_vs_fedau', metric))}")
        bits.append(f"  RAVEN vs FedAvg (Delta_c_s): {_fmt_cmp(_hit(holm_frame, dataset, 'raven_vs_fedavg', 'Delta_c_s'))}")
        bits.append(f"  RAVEN vs ObsUse (Delta_c_s): {_fmt_cmp(_hit(holm_frame, dataset, 'raven_vs_obsuse', 'Delta_c_s'))}")
        bits.append(f"  RAVEN vs TwoStage (Delta_c_s): {_fmt_cmp(_hit(holm_frame, dataset, 'raven_vs_twostage', 'Delta_c_s'))}")
        for metric in ("Delta_c_s", "Delta_group"):
            row = _hit(holm_frame, dataset, "raven_vs_fedau", metric)
            if row is not None and row.get("p_holm") is not None:
                raven_struct_wins.append(
                    bool(row["significant_holm_0.05"])
                    and float(row["mean_diff_left_minus_right"]) < 0
                )
        for metric in ("RMSE_mu", "Tail_RMSE"):
            row = _hit(holm_frame, dataset, "raven_vs_fedau", metric)
            if row is not None and row.get("p_holm") is not None:
                raven_pred_losses.append(
                    bool(row["significant_holm_0.05"])
                    and float(row["mean_diff_left_minus_right"]) > 0
                )
        qsub = summary[
            (summary["dataset"] == dataset)
            & (summary["method"] == "raven")
            & (summary["metric"] == "Q_norm1_over_S")
        ]
        if qsub.empty:
            bits.append("  Debt Q_norm1_over_S: TBD (RAVEN only)")
        else:
            bits.append(
                f"  Debt Q_norm1_over_S (RAVEN): mean={float(qsub.iloc[0]['mean']):.4g}, "
                f"std={float(qsub.iloc[0]['std']):.4g}, n={int(qsub.iloc[0]['n'])}"
            )
        bits.append("")
    struct_ok = all(raven_struct_wins) and len(raven_struct_wins) == 4
    pred_loss = any(raven_pred_losses)
    if struct_ok:
        verdict_struct = (
            "RAVEN maintains a Holm-significant structural advantage vs FedAU "
            "on both Delta_c_s and Delta_group on both datasets under drift."
        )
        supports = "This experiment supports RAVEN's time-varying deployment value on structural alignment."
    else:
        n_ok = sum(1 for x in raven_struct_wins if x)
        verdict_struct = (
            f"RAVEN does not uniformly win the structural endpoints vs FedAU under drift "
            f"({n_ok}/4 dataset×metric Holm-significant RAVEN-lower comparisons)."
        )
        supports = "This experiment does not support a blanket claim that drift is where RAVEN most clearly wins."
    if pred_loss:
        verdict_pred = "FedAU still beats or matches RAVEN on prediction on at least one drifting block."
    else:
        verdict_pred = "RAVEN is not Holm-significantly worse than FedAU on drifting prediction endpoints."
    bits.append("Author verdict (honest):")
    bits.append(f"- {verdict_struct}")
    bits.append(f"- {verdict_pred}")
    bits.append(f"- {supports}")
    missing = int((frame["status"] != "OK").sum())
    bits.append(f"- missing_cells={missing}")
    return "\n".join(bits)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = collect_rows()
    frame.to_csv(OUT_DIR / "per_seed.csv", index=False)
    summary, holm_frame = stats_table(frame)
    summary.to_csv(OUT_DIR / "summary.csv", index=False)
    holm_frame.to_csv(OUT_DIR / "holm.csv", index=False)
    text = conclusion(summary, holm_frame, frame)
    (OUT_DIR / "conclusion.txt").write_text(text + "\n", encoding="utf-8")
    print(text)
    missing = int((frame["status"] != "OK").sum())
    print(f"wrote {OUT_DIR} missing_cells={missing}")
    return 0 if missing == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
