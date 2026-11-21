#!/usr/bin/env python3
"""Collect FedAU-Window vs sealed E3 baselines; paired Wilcoxon + Holm; LaTeX table."""

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

FORMAL_ART = _ROOT / "artifacts" / "e3_formal_runs_r1"
FEDAU_ART = _ROOT / "artifacts" / "e3_fedau_window_r1"
OUT_DIR = _ROOT / "_paper_work" / "fedau_window_results"
DATASETS = ("sensorscope", "uair")
METHODS = ("fedavg_window", "fedau_window", "twostage_hajek", "raven")
METRICS = ("RMSE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s")
DISPLAY = {
    "fedavg_window": "FedAvg-Window",
    "fedau_window": "FedAU-Window",
    "twostage_hajek": "TwoStage-Hajek",
    "raven": "RAVEN-MCS",
}


def _metrics_path(dataset: str, method: str, seed: int) -> Path:
    if method == "fedau_window":
        return FEDAU_ART / "runs" / dataset / method / f"seed{seed}" / "final_metrics.json"
    return FORMAL_ART / "runs" / dataset / method / f"seed{seed}" / "final_metrics.json"


def collect_rows() -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        for method in METHODS:
            for seed in FORMAL_SEEDS:
                path = _metrics_path(dataset, method, seed)
                rec = {
                    "dataset": dataset,
                    "method": method,
                    "seed": int(seed),
                }
                if not path.is_file():
                    rec["status"] = "MISSING"
                    for m in METRICS:
                        rec[m] = None
                    rows.append(rec)
                    continue
                payload = json.loads(path.read_text(encoding="utf-8"))
                rec["status"] = "OK"
                for m in METRICS:
                    rec[m] = payload.get(m)
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
        ("fedau_window", "fedavg_window", "fedau_vs_fedavg"),
    )
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
                    "n": summary.get("n"),
                    "mean_diff_left_minus_right": summary.get("mean_diff_raven_minus_baseline"),
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
                vals = [float(v) for v in sub[metric].tolist() if v is not None and math.isfinite(float(v))]
                packed = summarize_vector(vals)
                summary_rows.append(
                    {
                        "dataset": dataset,
                        "method": method,
                        "metric": metric,
                        **packed,
                    }
                )
    return pd.DataFrame(summary_rows), pd.DataFrame(holm_rows)


def _fmt(mean: float | None, std: float | None) -> str:
    if mean is None or std is None:
        return "TBD"
    return f"{mean:.4f} $\\pm$ {std:.4f}"


def latex_table(summary: pd.DataFrame) -> str:
    lookup = {}
    for row in summary.itertuples(index=False):
        lookup[(row.dataset, row.method, row.metric)] = (row.mean, row.std)

    def cell(ds: str, method: str, metric: str) -> str:
        return _fmt(*lookup.get((ds, method, metric), (None, None)))

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{E3 with participation-reweighting baseline (mean $\pm$ std over 20",
        r"paired seeds). Lower is better. FedAU-Window is a windowed adaptation of",
        r"FedAU~\cite{wang2024lightweight}, not an official reproduction; it applies",
        r"inverse-participation client weights only. Holm-corrected families:",
        r"RAVEN-vs-FedAU, FedAU-vs-FedAvg.}",
        r"\label{tab:e3_fedau}",
        r"\setlength{\tabcolsep}{4.5pt}",
        r"\begin{tabular}{llcccc}",
        r"\toprule",
        r"Dataset & Method & $\mathrm{RMSE}_{\mu}$ & Tail RMSE &",
        r"$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\",
        r"\midrule",
    ]
    for ds, ds_name, first in (
        ("sensorscope", "SensorScope", True),
        ("uair", "U-Air", False),
    ):
        if not first:
            lines.append(r"\midrule")
        for i, method in enumerate(METHODS):
            prefix = rf"\multirow{{4}}{{*}}{{{ds_name}}}" if i == 0 else ""
            amp = "&" if i == 0 else "&"
            if i == 0:
                row = (
                    f"{prefix}\n& {DISPLAY[method]:<16} & "
                    f"{cell(ds, method, 'RMSE_mu')} & {cell(ds, method, 'Tail_RMSE')} & "
                    f"{cell(ds, method, 'Delta_group')} & {cell(ds, method, 'Delta_c_s')}\\\\"
                )
            else:
                row = (
                    f"& {DISPLAY[method]:<16} & "
                    f"{cell(ds, method, 'RMSE_mu')} & {cell(ds, method, 'Tail_RMSE')} & "
                    f"{cell(ds, method, 'Delta_group')} & {cell(ds, method, 'Delta_c_s')}\\\\"
                )
            lines.append(row)
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def conclusion(holm_frame: pd.DataFrame) -> str:
    bits = []
    for dataset in DATASETS:
        def hit(comparison: str, metric: str) -> pd.Series | None:
            sub = holm_frame[
                (holm_frame["dataset"] == dataset)
                & (holm_frame["comparison"] == comparison)
                & (holm_frame["metric"] == metric)
            ]
            return None if sub.empty else sub.iloc[0]

        fedau_cs = hit("fedau_vs_fedavg", "Delta_c_s")
        raven_g = hit("raven_vs_fedau", "Delta_group")
        raven_cs = hit("raven_vs_fedau", "Delta_c_s")
        bits.append(f"{dataset}:")
        if fedau_cs is None or fedau_cs.get("p_holm") is None:
            bits.append("  FedAU vs FedAvg Delta_c_s: TBD (insufficient runs).")
        else:
            better = float(fedau_cs["mean_diff_left_minus_right"]) < 0
            sig = bool(fedau_cs["significant_holm_0.05"])
            bits.append(
                f"  FedAU vs FedAvg Delta_c_s: mean_diff={fedau_cs['mean_diff_left_minus_right']:.4f} "
                f"(FedAU lower={better}), p_holm={float(fedau_cs['p_holm']):.4g}, "
                f"Holm-significant={sig}."
            )
        for label, row in (("Delta_group", raven_g), ("Delta_c_s", raven_cs)):
            if row is None or row.get("p_holm") is None:
                bits.append(f"  RAVEN vs FedAU {label}: TBD.")
            else:
                better = float(row["mean_diff_left_minus_right"]) < 0
                sig = bool(row["significant_holm_0.05"])
                bits.append(
                    f"  RAVEN vs FedAU {label}: mean_diff={row['mean_diff_left_minus_right']:.4f} "
                    f"(RAVEN lower={better}), p_holm={float(row['p_holm']):.4g}, "
                    f"Holm-significant={sig}."
                )
    return "\n".join(bits)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = collect_rows()
    frame.to_csv(OUT_DIR / "e3_fedau_window_per_seed.csv", index=False)
    summary, holm_frame = stats_table(frame)
    summary.to_csv(OUT_DIR / "e3_fedau_window_summary.csv", index=False)
    holm_frame.to_csv(OUT_DIR / "e3_fedau_window_holm.csv", index=False)
    latex = latex_table(summary)
    (OUT_DIR / "e3_fedau_window_table.tex").write_text(latex, encoding="utf-8")
    text = conclusion(holm_frame)
    (OUT_DIR / "e3_fedau_window_conclusion.txt").write_text(text + "\n", encoding="utf-8")
    missing = int((frame["status"] != "OK").sum())
    print(latex)
    print(text)
    print(f"wrote {OUT_DIR} missing_cells={missing}")
    return 0 if missing == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
