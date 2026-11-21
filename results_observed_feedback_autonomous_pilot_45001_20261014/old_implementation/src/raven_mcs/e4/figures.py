"""Generate at most two E4 main figures from sealed source CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

MAX_FIGURES = 2


def _load_paired(art: Path) -> list[dict]:
    with (Path(art) / "E4_ABLATION_PAIRED_TESTS.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _plot_metric(art: Path, metric: str, outfile: str) -> Path:
    rows = [r for r in _load_paired(art) if r["metric"] == metric]
    components = ["Design", "Obs", "Use", "Inst", "Debt"]
    datasets = ["sensorscope", "uair"]
    x = np.arange(len(components))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, dataset in enumerate(datasets):
        vals = []
        for comp in components:
            match = next(r for r in rows if r["component"] == comp and r["dataset"] == dataset)
            vals.append(float(match["relative_change"]))
        ax.bar(x + (i - 0.5) * width, vals, width, label="SensorScope" if dataset == "sensorscope" else "U-Air")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(components)
    ax.set_ylabel(f"Paired relative change in {metric}\n(ablation − full RAVEN)/RAVEN")
    ax.set_title(f"E4 paired relative change in {metric}")
    ax.legend()
    fig.tight_layout()
    out = Path(art) / "figures" / outfile
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out.with_suffix(".png"), dpi=160)
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".svg"))
    plt.close(fig)
    return out


def generate_main_figures(art: Path) -> list[str]:
    art = Path(art)
    # Source CSVs for figures
    paired = _load_paired(art)
    src1 = art / "figure_data" / "FIG_E4_1_source.csv"
    src2 = art / "figure_data" / "FIG_E4_2_source.csv"
    src1.parent.mkdir(parents=True, exist_ok=True)
    for path, metric in ((src1, "Delta_c_s"), (src2, "Delta_group")):
        rows = [r for r in paired if r["metric"] == metric]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    _plot_metric(art, "Delta_c_s", "FIG_E4_1")
    _plot_metric(art, "Delta_group", "FIG_E4_2")
    return ["figures/FIG_E4_1.png", "figures/FIG_E4_2.png"]
