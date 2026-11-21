"""h_response_shift.py — scheme 2 Stage B: response-shift headroom H.

Runs ONLY with the phrase "授权 H 测量" in hand (see PREREG.md of
results_h_response_shift/round_v1). Trains the headroom pair only:
fedavg_window and raven_simoracle, five seeds, the frozen C0 traces, a fixed c grid.
Writes only under results_h_response_shift/round_v1/. No manuscript, no src/ edit.

    python scripts/h_response_shift.py --driver-check      # §4.1, one seed, production model
    python scripts/h_response_shift.py --run               # §4 Stage B grid, feature_blind
    python scripts/h_response_shift.py --tables            # §4.2/§4.3 H and the decision
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h_headroom as H                                                # noqa: E402
from raven_mcs.e3.canary.dataset_load import (                            # noqa: E402
    apply_train_zscore_standardization,
    load_paper_dataset,
    load_spatial_to_client,
)
from raven_mcs.e3.real_runner import runner as e3runner                   # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF                       # noqa: E402

OUT = ROOT / "results_h_response_shift" / "round_v1"
C_GRID = (0.0, 0.5, 1.0, 2.0)
SEEDS = [30001, 30002, 30003, 30004, 30005]
ARMS = ("fedavg_window", "raven_simoracle")
DATASETS = ("sensorscope", "uair")
LOCAL_STEPS = H.LOCAL_STEPS
REF = ROOT / "results_h_headroom" / "round_v1" / "gate" / "C0_frozen"


# ----------------------------------------------------------------- the backbone (§3)
class FeatureBlindNDMF(H.DiurnalBlindNDMF):
    """DiurnalBlindNDMF plus a hard-zeroed spatial index: one embedding row for all stations."""

    def forward(self, spatial_index, hour, weekday, trend):        # noqa: D102
        spatial_index = torch.zeros_like(spatial_index)
        return super().forward(spatial_index, hour, weekday, trend)


def feature_blind_factory(num_spatial: int, *, seed: int = 26001) -> CommonNDMF:
    torch.manual_seed(int(seed))
    return FeatureBlindNDMF(num_spatial=num_spatial)


# ----------------------------------------------------------------- the label shift (§2)
def shift_dataset(ds, c: float, dataset_name: str) -> dict:
    """Apply delta(unit) = c*s(g) - delta_bar to every split, in the units of stored RMSE_mu.

    Must run AFTER apply_train_zscore_standardization, which load_paper_dataset already does
    for U-Air and which is a no-op for SensorScope.
    """
    atomic = ds._atomic_df.copy()
    groups = sorted(str(g) for g in atomic["target_group"].astype(str).unique())
    s_of = {g: (1.0 if i % 2 == 0 else -1.0) for i, g in enumerate(groups)}
    gstr = atomic["target_group"].astype(str)
    raw = np.array([c * s_of[g] for g in gstr], dtype=np.float64)
    is_train = (atomic["split"].astype(str) == "train").to_numpy()
    dbar = float(raw[is_train].mean()) if is_train.any() else 0.0
    delta = raw - dbar
    atomic["target_value"] = atomic["target_value"].astype(float).to_numpy() + delta
    ds._atomic_df = atomic
    # mirror onto the client measurement index
    d_of_unit = {str(u): float(d) for u, d in zip(atomic["unit_id"].astype(str), delta)}
    ds._measurement_index = {k: float(v) + d_of_unit.get(str(k[1]), 0.0)
                             for k, v in ds._measurement_index.items()}
    if "potential_measurement" in ds._client_df.columns:
        cdf = ds._client_df.copy()
        cdf["potential_measurement"] = (
            cdf["potential_measurement"].astype(float).to_numpy()
            + [d_of_unit.get(str(u), 0.0) for u in cdf["unit_id"].astype(str)])
        ds._client_df = cdf
    return {"c": c, "n_groups": len(groups), "delta_bar": dbar,
            "min_delta": float(delta.min()), "max_delta": float(delta.max()),
            "zero_exactly": bool(c == 0.0 and abs(delta).max() == 0.0)}


def run_one(dataset_name: str, method: str, seed: int, c: float, *, tag: str) -> dict:
    run_dir = OUT / "runs" / f"c{c:g}" / dataset_name / method / f"seed{seed}"
    marker = run_dir / "final_metrics.json"
    info = {}
    if not marker.is_file():
        ds = load_paper_dataset(ROOT, dataset_name)
        mapping = load_spatial_to_client(ROOT, dataset_name)
        info = shift_dataset(ds, c, dataset_name)
        cond = dict(H.CONDITIONS["C0_frozen"])
        cond["model"] = "feature_blind"          # our factory, installed below
        orig_model = H.wr.deterministic_common_ndmf
        H.wr.deterministic_common_ndmf = feature_blind_factory
        try:
            with H.injected(cond, block_factor=None):
                e3runner.run_e3_real(
                    root=ROOT, run_dir=run_dir, dataset=ds, method=method, seed=int(seed),
                    eventtrace_dir=H.trace_dir("C0_frozen", dataset_name, seed),
                    spatial_to_client=mapping, dataset_name=dataset_name,
                    local_steps=LOCAL_STEPS, pi_target_override=None,
                    source_identity={"git_commit": "h_response_shift_r1",
                                     "condition": "C0_frozen", "c": c,
                                     "backbone": "feature_blind"},
                )
        finally:
            H.wr.deterministic_common_ndmf = orig_model
    m = json.loads(marker.read_text(encoding="utf-8"))
    return {"dataset": dataset_name, "method": method, "seed": int(seed), "c": float(c),
            "tag": tag, "RMSE_mu": float(m["RMSE_mu"]), "Delta_group": float(m["Delta_group"]),
            "Head_RMSE": m.get("Head_RMSE"), "Tail_RMSE": m.get("Tail_RMSE"),
            "zero_exactly": info.get("zero_exactly"), "delta_bar": info.get("delta_bar")}


# ----------------------------------------------------------------- §4.1 driver check
def driver_check() -> bool:
    """c = 0, production full model, both datasets, seed 30001, both arms."""
    rows, ok = [], True
    for dataset_name in DATASETS:
        for method in ARMS:
            rd = OUT / "driver_check" / "C0_frozen" / dataset_name / method / "seed30001"
            marker = rd / "final_metrics.json"
            if not marker.is_file():
                ds = load_paper_dataset(ROOT, dataset_name)
                mapping = load_spatial_to_client(ROOT, dataset_name)
                with H.injected(dict(H.CONDITIONS["C0_frozen"]), block_factor=None):
                    e3runner.run_e3_real(
                        root=ROOT, run_dir=rd, dataset=ds, method=method, seed=30001,
                        eventtrace_dir=H.trace_dir("C0_frozen", dataset_name, 30001),
                        spatial_to_client=mapping, dataset_name=dataset_name,
                        local_steps=LOCAL_STEPS, pi_target_override=None,
                        source_identity={"git_commit": "h_response_shift_r1",
                                         "condition": "C0_frozen", "stage": "driver_check"})
            got = float(json.loads(marker.read_text(encoding="utf-8"))["RMSE_mu"])
            ref_p = REF / dataset_name / method / "seed30001" / "final_metrics.json"
            if not ref_p.is_file():
                rows.append({"dataset": dataset_name, "method": method, "rerun": got,
                             "reference": None, "abs_diff": None,
                             "status": "REFERENCE_MISSING"})
                ok = False
                continue
            want = float(json.loads(ref_p.read_text(encoding="utf-8"))["RMSE_mu"])
            d = abs(got - want)
            rows.append({"dataset": dataset_name, "method": method, "rerun": got,
                         "reference": want, "abs_diff": d,
                         "status": "PASS" if d <= 1e-6 else "FAIL"})
            ok &= (d <= 1e-6)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "DRIVER_CHECK.csv", index=False)
    print(df.to_string(index=False))
    (OUT / "DRIVER_CHECK.json").write_text(
        json.dumps({"pass": bool(ok), "tolerance": 1e-6, "rows": rows}, indent=2), encoding="utf-8")
    print("driver check pass = %s" % ok)
    return bool(ok)


# ----------------------------------------------------------------- §4 Stage B grid
def stage_b() -> None:
    print("Stage B: %d runs" % (len(DATASETS) * len(ARMS) * len(SEEDS) * len(C_GRID)))
    rows = []
    for dataset_name in DATASETS:
        for method in ARMS:
            for seed in SEEDS:
                for c in C_GRID:
                    t0 = time.perf_counter()
                    r = run_one(dataset_name, method, seed, c, tag="grid")
                    r["seconds"] = time.perf_counter() - t0
                    rows.append(r)
                    print("  %-12s %-16s %d c=%-4g RMSE_mu=%.10f (%.1fs)"
                          % (dataset_name, method, seed, c, r["RMSE_mu"], r["seconds"]), flush=True)
    pd.DataFrame(rows).to_csv(OUT / "H_SEED_ROWS.csv", index=False)
    print("wrote H_SEED_ROWS.csv (%d rows)" % len(rows))


# ----------------------------------------------------------------- §4.2 / §4.3 tables
def tables() -> None:
    from scipy import stats
    df = pd.read_csv(OUT / "H_SEED_ROWS.csv")
    rows = []
    for dataset_name in DATASETS:
        for c in C_GRID:
            sub = df[(df.dataset == dataset_name) & (df.c == c)]
            piv = {a: g.set_index("seed") for a, g in sub.groupby("method")}
            common = sorted(set(piv["fedavg_window"].index) & set(piv["raven_simoracle"].index))
            f = piv["fedavg_window"].loc[common, "RMSE_mu"].to_numpy(float)
            o = piv["raven_simoracle"].loc[common, "RMSE_mu"].to_numpy(float)
            hh = (f - o) / f
            n = len(hh)
            mean = float(hh.mean())
            sd = float(hh.std(ddof=1)) if n > 1 else float("nan")
            se = sd / np.sqrt(n) if n > 1 else float("nan")
            tcrit = float(stats.t.ppf(0.975, n - 1)) if n > 1 else float("nan")
            lo, hi = mean - tcrit * se, mean + tcrit * se
            backbone = "feature_blind"
            if c == 0.0:
                go = False
                note = "c=0 baseline, never GO"
                if lo > 0 and mean >= 0.01:
                    note = "STOP: the blind model itself produces headroom"
            else:
                go = bool(mean >= 0.01 and lo > 0)
                note = ""
            rows.append({"ds": dataset_name, "c": c, "backbone": backbone, "n": n,
                         "H": mean, "ci_lo": lo, "ci_hi": hi,
                         "fedavg_RMSE_mu": float(f.mean()), "oracle_RMSE_mu": float(o.mean()),
                         "go": go, "note": note})
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "H_SUMMARY.csv", index=False)
    print(out.round(6).to_string(index=False))

    winners = out[(out.c > 0) & (out.go)].to_dict("records")
    # §4.3 c=0 stop rule
    stop0 = out[(out.c == 0.0) & (out.ci_lo > 0) & (out.H >= 0.01)]
    decision = "GO" if winners else "STOP"
    if len(stop0):
        decision = "STOP"
    dec = {"stage_A": json.loads((OUT / "H_DECISION.json").read_text(encoding="utf-8"))["stage_A"]
           if (OUT / "H_DECISION.json").is_file() else None,
           "stage_B_ran": True, "decision": decision,
           "winning_cells": [{"ds": w["ds"], "c": w["c"], "H": w["H"], "ci_lo": w["ci_lo"]}
                             for w in winners],
           "c0_stop_triggered": bool(len(stop0)),
           "grid": {"c": list(C_GRID), "seeds": SEEDS, "arms": list(ARMS),
                    "datasets": list(DATASETS), "backbone": "feature_blind",
                    "traces": "frozen C0 (theta=1.25, tail_scale=0.55)"},
           "cost": "%d training runs" % len(df)}
    (OUT / "H_DECISION.json").write_text(json.dumps(dec, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    print()
    print(json.dumps(dec, indent=2, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--driver-check", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--tables", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.driver_check:
        if not driver_check():
            raise SystemExit("STOP: §4.1 driver check failed; Stage B not started")
    if a.run:
        if not (OUT / "DRIVER_CHECK.json").is_file() or \
                not json.loads((OUT / "DRIVER_CHECK.json").read_text(encoding="utf-8"))["pass"]:
            raise SystemExit("STOP: §4.1 driver check has not passed")
        stage_b()
    if a.tables:
        tables()


if __name__ == "__main__":
    main()
