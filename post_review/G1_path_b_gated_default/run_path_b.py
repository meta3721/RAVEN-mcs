"""Path B: dataset-gated default from sealed E3/E4. No new training."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TAB = OUT / "tables"
E3 = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
E4 = ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs"

VAL_SEEDS = list(range(30001, 30011))
TEST_SEEDS = list(range(30011, 30021))
METRICS = ("Delta_group", "RMSE_mu", "Tail_RMSE", "Delta_c_s")
PRIMARY = ("Delta_group", "RMSE_mu", "Tail_RMSE")
METHODS = ("raven", "raven_wo_design", "raven_simoracle")
GATED = {"sensorscope": "raven", "uair": "raven_wo_design"}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run_dir(dataset: str, method: str, seed: int) -> Path:
    if method == "raven_wo_design":
        return E4 / dataset / method / f"seed{seed}"
    return E3 / dataset / method / f"seed{seed}"


def _pct(new: float, ref: float) -> float:
    if ref is None or not np.isfinite(ref) or abs(float(ref)) < 1e-15:
        return float("nan")
    return 100.0 * (float(new) - float(ref)) / float(ref)


def collect(seeds: list[int]) -> pd.DataFrame:
    rows = []
    for dataset, default in GATED.items():
        for seed in seeds:
            mets = {}
            for method in METHODS:
                path = _run_dir(dataset, method, seed) / "final_metrics.json"
                if not path.is_file():
                    raise FileNotFoundError(path)
                raw = _load_json(path)
                mets[method] = {k: raw.get(k) for k in METRICS}
            gated = mets[default]
            row = {
                "dataset": dataset,
                "seed": seed,
                "gated_method": default,
            }
            for key in METRICS:
                row[f"gated_{key}"] = gated[key]
                for method in METHODS:
                    row[f"{method}_{key}"] = mets[method][key]
                row[f"gated_vs_raven_{key}_pct"] = _pct(gated[key], mets["raven"][key])
                row[f"gated_vs_off_{key}_pct"] = _pct(
                    gated[key], mets["raven_wo_design"][key]
                )
                row[f"raven_vs_off_{key}_pct"] = _pct(
                    mets["raven"][key], mets["raven_wo_design"][key]
                )
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame, split: str) -> pd.DataFrame:
    rows = []
    for dataset, sub in df.groupby("dataset"):
        row = {
            "split": split,
            "dataset": dataset,
            "n": int(len(sub)),
            "gated_method": GATED[dataset],
        }
        for key in METRICS:
            row[f"gated_{key}_mean"] = float(sub[f"gated_{key}"].mean())
            row[f"raven_{key}_mean"] = float(sub[f"raven_{key}"].mean())
            row[f"off_{key}_mean"] = float(sub[f"raven_wo_design_{key}"].mean())
            row[f"simoracle_{key}_mean"] = float(sub[f"raven_simoracle_{key}"].mean())
            row[f"raven_vs_off_{key}_pct_mean"] = float(
                sub[f"raven_vs_off_{key}_pct"].mean()
            )
            row[f"gated_vs_raven_{key}_pct_mean"] = float(
                sub[f"gated_vs_raven_{key}_pct"].mean()
            )
        rows.append(row)
    return pd.DataFrame(rows)


def val_confirm(val: pd.DataFrame) -> dict:
    u = val[val.dataset == "uair"]
    s = val[val.dataset == "sensorscope"]
    checks = []
    for key in PRIMARY:
        worse = float(u[f"raven_{key}"].mean()) > float(u[f"raven_wo_design_{key}"].mean())
        checks.append(
            {
                "rule": f"uair_raven_worse_than_off_{key}",
                "raven_mean": float(u[f"raven_{key}"].mean()),
                "off_mean": float(u[f"raven_wo_design_{key}"].mean()),
                "pass": worse,
            }
        )
    ss_dg = float(s["raven_vs_off_Delta_group_pct"].mean())
    checks.append(
        {
            "rule": "sensorscope_raven_not_worse_than_off_Delta_group",
            "raven_vs_off_pct": ss_dg,
            "pass": ss_dg <= 0.5,
        }
    )
    checks.append(
        {
            "rule": "sensorscope_raven_delta_cs_le_off",
            "raven_mean": float(s["raven_Delta_c_s"].mean()),
            "off_mean": float(s["raven_wo_design_Delta_c_s"].mean()),
            "pass": float(s["raven_Delta_c_s"].mean())
            <= float(s["raven_wo_design_Delta_c_s"].mean()),
        }
    )
    return {
        "verdict": "PATH_B_VAL_CONFIRMED" if all(c["pass"] for c in checks) else "PATH_B_VAL_FAILS",
        "n_uair": int(len(u)),
        "n_sensorscope": int(len(s)),
        "checks": checks,
    }


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    val = collect(VAL_SEEDS)
    test = collect(TEST_SEEDS)
    val.to_csv(TAB / "val_seed.csv", index=False)
    test.to_csv(TAB / "test_seed.csv", index=False)
    summ = pd.concat(
        [summarize(val, "val"), summarize(test, "test")],
        ignore_index=True,
    )
    summ.to_csv(TAB / "split_summary.csv", index=False)
    gate = val_confirm(val)
    (OUT / "VAL_CONFIRM.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    print(json.dumps(gate, indent=2))
    print(summ.to_string(index=False))
    (OUT / "test_opened.json").write_text(
        json.dumps(
            {
                "opened": gate["verdict"] == "PATH_B_VAL_CONFIRMED",
                "reason": gate["verdict"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
