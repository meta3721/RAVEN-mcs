#!/usr/bin/env python3
"""INT-R-E3 round_v2 executor: stability-calibrated occupancy, audit, then train.

Does not edit the manuscript. Does not invent metrics. Gate_t is not the Design switch.
Does not overwrite round_v1 traces or always-on formal EventTraces.
"""

from __future__ import annotations

import argparse
import ast
import csv
import inspect
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import M_MC  # noqa: E402
from raven_mcs.e3.canary.dataset_load import (  # noqa: E402
    load_horizon,
    load_paper_dataset,
    load_spatial_to_client,
)
from raven_mcs.e3.formal.constants import FORMAL_SEEDS  # noqa: E402
from raven_mcs.e3.int_r.occupancy import (  # noqa: E402
    B_STAR,
    CALIBRATION_SEED,
    CALIBRATOR_VERSION_V2,
    OccupancySpec,
    RHO_STAR,
    STABILITY_SEEDS,
    calibrate_markov_v2,
    occupancy_metrics,
)
from raven_mcs.e3.protocol_closure.complete_aligned import freeze_public_target_from_atomic  # noqa: E402
from raven_mcs.e3.real_runner.generator_r3 import (  # noqa: E402
    _block_from_stratum,
    generate_complete_aligned_r3,
    materialize_r3_trace,
)
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

OUT = ROOT / "results_int_r" / "round_v2"
TRACE_ROOT = ROOT / "artifacts" / "e3_int_r_eventtraces_v2"
DATASETS = ("sensorscope", "uair")
AUDIT_SEEDS = (30001, 30010, 30020)
CANARY_SEED = 31001
TV_THRESHOLD = 0.05


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def spec_path() -> Path:
    return OUT / "INT_R_OCCUPANCY_SPEC.json"


def load_spec() -> OccupancySpec:
    raw = json.loads(spec_path().read_text(encoding="utf-8"))
    return OccupancySpec(
        family=str(raw["family"]),
        alpha=float(raw["alpha"]),
        beta=float(raw["beta"]),
        rho0=float(raw["rho0"]),
        burstiness_miss=bool(raw.get("burstiness_miss", False)),
    )


def stage_calibrate() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    mapping = load_spatial_to_client(ROOT, "sensorscope")
    n_clients = len(sorted(set(mapping.values())))
    n_windows_ss = int(load_horizon(ROOT, "sensorscope")["chosen_E3_formal_windows"])
    n_windows_ua = int(load_horizon(ROOT, "uair")["chosen_E3_formal_windows"])
    n_windows_by_dataset = {"sensorscope": n_windows_ss, "uair": n_windows_ua}
    result = calibrate_markov_v2(
        n_clients=n_clients,
        n_windows_cal=n_windows_ss,
        n_windows_by_dataset=n_windows_by_dataset,
    )
    spec = result.spec
    from raven_mcs.e3.int_r.occupancy import occupancy_rng, simulate_occupancy

    A = simulate_occupancy(
        n_clients=n_clients,
        n_windows=n_windows_ss,
        spec=spec,
        rng=occupancy_rng("sensorscope", CALIBRATION_SEED),
    )
    met = occupancy_metrics(A)
    grid_rows = [dict(r) for r in result.grid_rows]
    with (OUT / "INT_R_CALIBRATION_GRID.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(grid_rows[0].keys()))
        w.writeheader()
        w.writerows(grid_rows)
    payload = {
        **spec.to_dict(),
        "calibrator_version": CALIBRATOR_VERSION_V2,
        "stability_level": result.stability_level,
        "stability_hits": result.stability_hits,
        "stability_n_checks": result.stability_n_checks,
        "stability_mean_rho": result.stability_mean_rho,
        "stability_std_rho": result.stability_std_rho,
        "stability_seeds": list(STABILITY_SEEDS),
        "grid_expanded": result.grid_expanded,
        "calibration_seed": CALIBRATION_SEED,
        "n_clients_sensorscope": n_clients,
        "n_windows_sensorscope": n_windows_ss,
        "n_windows_uair": n_windows_ua,
        "rho_star": RHO_STAR,
        "B_star": B_STAR,
        "calibration_replay": met,
        "git_commit": _git_commit(),
        "calibrated_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, spec_path())
    return payload


def _prepare_atomic(dataset: str) -> tuple[pd.DataFrame, dict[str, str], int]:
    ds = load_paper_dataset(ROOT, dataset)
    mapping = load_spatial_to_client(ROOT, dataset)
    atomic, _meta = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset, root=ROOT)
    n_windows = int(load_horizon(ROOT, dataset)["chosen_E3_formal_windows"])
    return atomic, mapping, n_windows


def stage_smoke() -> dict[str, Any]:
    spec = load_spec()
    atomic, mapping, _n = _prepare_atomic("sensorscope")
    kwargs = dict(
        dataset="sensorscope",
        atomic=atomic,
        spatial_to_client=mapping,
        seed=CANARY_SEED,
        num_windows=3,
        m_mc=8,
    )
    forced = OccupancySpec(family="two_state_markov", alpha=1.0, beta=0.0, rho0=1.0)
    t0, _, _, _ = generate_complete_aligned_r3(**kwargs, occupancy_spec=None)
    t1, _, _, a1 = generate_complete_aligned_r3(**kwargs, occupancy_spec=forced)
    t2, _, _, a2 = generate_complete_aligned_r3(**kwargs, occupancy_spec=spec)

    def drop(events: pd.DataFrame) -> pd.DataFrame:
        out = events.copy()
        out["opportunity_features"] = out["opportunity_features"].map(
            lambda f: {k: v for k, v in dict(f).items() if k != "occupancy_A"}
        )
        return out.sort_values(["window_id", "client_id"]).reset_index(drop=True)

    pd.testing.assert_frame_equal(drop(t0.events), drop(t1.events), check_dtype=False)
    A = a2["occupancy_matrix"]
    clients = a2["occupancy_client_ids"]
    present = set(zip(t2.events["client_id"].astype(str), t2.events["window_id"].astype(int)))
    empty_inactive = True
    for t in range(A.shape[0]):
        for j, cid in enumerate(clients):
            if int(A[t, j]) == 0 and (str(cid), int(t)) in present:
                empty_inactive = False
    occ_src = inspect.getsource(
        sys.modules["raven_mcs.e3.int_r.occupancy"]
    ).lower()
    leak = any(s in occ_src for s in ("rmse", "y_i", "test_error"))
    seed_literal = "30001" in (
        ROOT / "src" / "raven_mcs" / "e3" / "int_r" / "occupancy.py"
    ).read_text(encoding="utf-8")
    row = {
        "forced_ones_matches_always_on": True,
        "inactive_have_no_rows": bool(empty_inactive),
        "canary_n_event_rows": int(a2["n_event_rows"]),
        "canary_n_client_windows": int(a2["n_client_windows"]),
        "occupancy_source_label_leak": bool(leak),
        "occupancy_source_has_table_seed_literal": bool(seed_literal),
        "gate_used": False,
        "calibrator_version": CALIBRATOR_VERSION_V2,
    }
    dump_json(row, OUT / "INT_R_SMOKE.json")
    if leak or not empty_inactive or seed_literal:
        raise RuntimeError(f"INT-R v2 smoke failed: {row}")
    return row


def stage_generate(*, datasets: tuple[str, ...], seeds: list[int], force: bool) -> list[dict[str, Any]]:
    spec = load_spec()
    TRACE_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for dataset in datasets:
        atomic, mapping, n_windows = _prepare_atomic(dataset)
        for seed in seeds:
            out = TRACE_ROOT / dataset / f"seed{seed}"
            ident = out / "training_eventtrace" / "trace_identity.json"
            if ident.is_file() and not force:
                identity = json.loads(ident.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "status": "REUSED",
                        "dataset": dataset,
                        "seed": seed,
                        "hash": identity.get("trace_hash"),
                    }
                )
                print(f"REUSED {dataset} seed{seed}", flush=True)
                continue
            print(f"START trace {dataset} seed{seed}", flush=True)
            mat = materialize_r3_trace(
                dataset=dataset,
                atomic=atomic,
                spatial_to_client=mapping,
                out_dir=out,
                seed=int(seed),
                num_windows=n_windows,
                m_mc=M_MC,
                delivery_mode="nominal",
                occupancy_spec=spec,
            )
            dump_json(
                {
                    "scenario": "complete_aligned_int_r",
                    "round": "v2",
                    "num_windows": n_windows,
                    "m_mc": M_MC,
                    "occupancy": spec.to_dict(),
                    "gate_used": False,
                    "scd_rule": {
                        "sensorscope": "Design ON (raven always_on components; not Gate)",
                        "uair": "Design OFF (raven_wo_design; not Gate)",
                    },
                },
                out / "generation_meta.json",
            )
            identity = mat.get("identity") or {}
            row = {
                "status": "CREATED",
                "dataset": dataset,
                "seed": seed,
                "hash": identity.get("trace_hash"),
                "n_event_rows": (mat.get("audit") or {}).get("n_event_rows"),
                "occupancy_mean_active_frac": (mat.get("audit") or {}).get(
                    "occupancy_mean_active_frac"
                ),
            }
            print(f"DONE {row['status']} {dataset} seed{seed}", flush=True)
            rows.append(row)
    dump_json({"rows": rows}, OUT / "INT_R_TRACE_LEDGER.json")
    return rows


def _tv_opp_mu(dataset: str, seed: int) -> float:
    atomic, _mapping, _n = _prepare_atomic(dataset)
    mu = freeze_public_target_from_atomic(atomic, dataset=dataset)["mu"]
    mu_vec = np.asarray([float(mu[str(g)]) for g in (0, 1, 2, 3)], dtype=np.float64)
    et = TRACE_ROOT / dataset / f"seed{seed}" / "training_eventtrace"
    from raven_mcs.simulation.event_trace import load_event_trace

    trace, _identity = load_event_trace(et)
    events = trace.events
    train_units = set(
        atomic.loc[atomic["split"].astype(str) == "train", "unit_id"].astype(str)
    )
    unit_block = {
        str(r.unit_id): _block_from_stratum(str(r.target_group))
        for r in atomic.itertuples(index=False)
        if str(r.unit_id) in train_units
    }
    counts = np.zeros(4, dtype=np.float64)
    for risk in events["risk_set_unit_ids"]:
        if isinstance(risk, str):
            risk = ast.literal_eval(risk)
        for uid in risk:
            if str(uid) not in unit_block:
                continue
            counts[int(unit_block[str(uid)])] += 1.0
    if counts.sum() <= 0:
        return float("nan")
    pi = counts / counts.sum()
    return float(0.5 * np.abs(pi - mu_vec).sum())


def stage_audit() -> dict[str, Any]:
    spec = load_spec()
    rows = []
    gates = {}
    for dataset in DATASETS:
        for seed in AUDIT_SEEDS:
            occ_path = TRACE_ROOT / dataset / f"seed{seed}" / "occupancy_matrix.parquet"
            if not occ_path.is_file():
                raise FileNotFoundError(occ_path)
            frame = pd.read_parquet(occ_path)
            A = frame.drop(columns=["window_id"]).to_numpy(dtype=np.int8)
            met = occupancy_metrics(A)
            tv = _tv_opp_mu(dataset, seed)
            rows.append(
                {
                    "dataset": dataset,
                    "seed": seed,
                    "mean_active_frac": met["mean_active_frac"],
                    "burstiness_pooled": met["burstiness_pooled"],
                    "tv_opp_mu": tv,
                    "n_clients": int(met["n_clients"]),
                    "n_windows": int(met["n_windows"]),
                    "fraction_windows_all_clients_off": met["fraction_windows_all_clients_off"],
                    "mean_active_clients_per_window": met["mean_active_clients_per_window"],
                }
            )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    with (OUT / "tables" / "INT_R_OCC.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    all_rows = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            occ_path = TRACE_ROOT / dataset / f"seed{seed}" / "occupancy_matrix.parquet"
            if not occ_path.is_file():
                continue
            frame = pd.read_parquet(occ_path)
            A = frame.drop(columns=["window_id"]).to_numpy(dtype=np.int8)
            met = occupancy_metrics(A)
            all_rows.append(
                {
                    "dataset": dataset,
                    "seed": int(seed),
                    "mean_active_frac": met["mean_active_frac"],
                    "burstiness_pooled": met["burstiness_pooled"],
                    "n_windows": int(met["n_windows"]),
                    "frac_all_off": met["fraction_windows_all_clients_off"],
                }
            )
    if all_rows:
        with (OUT / "tables" / "INT_R_OCC_ALL_SEEDS.csv").open(
            "w", newline="", encoding="utf-8"
        ) as fh:
            w = csv.DictWriter(fh, fieldnames=list(all_rows[0].keys()))
            w.writeheader()
            w.writerows(all_rows)

    ss = next(r for r in rows if r["dataset"] == "sensorscope" and r["seed"] == 30001)
    ua = next(r for r in rows if r["dataset"] == "uair" and r["seed"] == 30001)
    gates["INT-R-OCC-1"] = (
        0.35 <= ss["mean_active_frac"] <= 0.50 and 0.35 <= ua["mean_active_frac"] <= 0.50
    )
    if spec.family == "bernoulli_iid":
        gates["INT-R-OCC-2"] = True
    else:
        gates["INT-R-OCC-2"] = ss["burstiness_pooled"] > 0 and ua["burstiness_pooled"] > 0
    gates["INT-R-OCC-3"] = ss["tv_opp_mu"] > TV_THRESHOLD and ua["tv_opp_mu"] > TV_THRESHOLD
    occ_src = (ROOT / "src" / "raven_mcs" / "e3" / "int_r" / "occupancy.py").read_text(
        encoding="utf-8"
    )
    occ_lower = occ_src.lower()
    gates["INT-R-OCC-4"] = all(s not in occ_lower for s in ("rmse", "y_i", "test_error"))
    gates["INT-R-OCC-5"] = True
    for dataset in DATASETS:
        seed = 30001
        frame = pd.read_parquet(TRACE_ROOT / dataset / f"seed{seed}" / "occupancy_matrix.parquet")
        from raven_mcs.simulation.event_trace import load_event_trace

        trace, _identity = load_event_trace(
            TRACE_ROOT / dataset / f"seed{seed}" / "training_eventtrace"
        )
        events = trace.events
        present = set(zip(events["client_id"].astype(str), events["window_id"].astype(int)))
        clients = [c for c in frame.columns if c != "window_id"]
        A = frame[clients].to_numpy(dtype=np.int8)
        for t, win in enumerate(frame["window_id"].tolist()):
            for j, cid in enumerate(clients):
                if int(A[t, j]) == 0 and (str(cid), int(win)) in present:
                    gates["INT-R-OCC-5"] = False
    summary = {
        "gates": gates,
        "all_pass": all(gates.values()),
        "occupancy_spec": spec.to_dict(),
        "rows": rows,
    }
    dump_json(summary, OUT / "INT_R_OCC_GATES.json")
    if not summary["all_pass"]:
        raise RuntimeError(f"occupancy gates failed: {gates}")
    return summary


def scd_method(dataset: str) -> str:
    if dataset == "sensorscope":
        return "raven"
    if dataset == "uair":
        return "raven_wo_design"
    raise ValueError(dataset)


def e3_schedule() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    shared = ["fedavg_window", "twostage_hajek", "fedau_window", "obsuse_window"]
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            for method in shared:
                rows.append({"dataset": dataset, "seed": seed, "method": method})
            rows.append({"dataset": dataset, "seed": seed, "method": scd_method(dataset)})
            if dataset == "uair":
                rows.append({"dataset": dataset, "seed": seed, "method": "raven"})
            if dataset == "sensorscope":
                rows.append({"dataset": dataset, "seed": seed, "method": "raven_wo_design"})
    return rows


_WG_PACK: dict[str, dict[str, Any]] = {}


def _g2_eval_pack(dataset_name: str) -> dict[str, Any]:
    """Four UTC-block evaluation pack. Same h(i) construction as G2 / Table II."""
    if dataset_name in _WG_PACK:
        return _WG_PACK[dataset_name]
    from raven_mcs.data.target import RepeatableTimeOfDayMapper
    from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
    from raven_mcs.models.features import extract_features

    ds = load_paper_dataset(ROOT, dataset_name)
    bundle = production_target_bundle(root=ROOT, dataset_name=dataset_name, dataset=ds)
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    test = ds.atomic_df[ds.atomic_df["split"] == "test"].copy()
    g2i = ds._target_group_str_to_int
    fine = np.asarray([int(g2i.get(str(g), 0)) for g in test["target_group"].tolist()], dtype=int)
    blocks = RepeatableTimeOfDayMapper().map(test).to_numpy(dtype=int)
    hours = []
    for ts in test["absolute_time"].tolist():
        hours.append(float(ts.timestamp()) / 3600.0 if hasattr(ts, "timestamp") else float(ts))
    hours = np.asarray(hours, dtype=np.float64)
    spatial_ids = [str(s) for s in test["spatial_id"].tolist()]
    time_indices = [int(t) for t in test["time_index"].tolist()]
    total_slots = int(ds.atomic_df["time_index"].max()) + 1
    feats = extract_features(
        spatial_ids,
        hours.tolist(),
        time_indices,
        {str(k): int(v) for k, v in ds._spatial_to_idx.items()},
        total_slots,
    )
    y_true = test["target_value"].to_numpy(dtype=np.float64)
    counts: dict[int, int] = {}
    for g in fine.tolist():
        counts[int(g)] = counts.get(int(g), 0) + 1
    w = np.zeros(len(fine), dtype=np.float64)
    for i, g in enumerate(fine.tolist()):
        mg = float(mu[g]) if g < len(mu) else 0.0
        w[i] = mg / max(counts[int(g)], 1)
    s = float(w.sum())
    w = w / s if s > 0 else np.full(len(w), 1.0 / max(len(w), 1))
    pack = {
        "num_spatial": int(ds.num_spatial),
        "features": feats,
        "y_true": y_true,
        "blocks": blocks,
        "mu_w": w,
    }
    _WG_PACK[dataset_name] = pack
    return pack


def _wrmse_block(y_true: np.ndarray, y_pred: np.ndarray, mask: np.ndarray, mu_w: np.ndarray) -> float:
    if not np.any(mask):
        return float("nan")
    ww = mu_w[mask].copy()
    s = float(ww.sum())
    ww = ww / s if s > 0 else np.full(int(mask.sum()), 1.0 / int(mask.sum()))
    err = y_true[mask] - y_pred[mask]
    return float(np.sqrt(np.sum(ww * err * err)))


def _worst_group_rmse(run_dir: Path, dataset_name: str) -> float | None:
    import torch
    from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt

    ckpt = run_dir / "checkpoints" / "final.pt"
    if not ckpt.is_file():
        return None
    pack = _g2_eval_pack(dataset_name)
    model = CommonNDMF_from_ckpt(ckpt, pack["num_spatial"])
    sp_idx, hour_t, wday_t, trend_t = pack["features"]
    model.eval()
    with torch.no_grad():
        y_pred = model(sp_idx, hour_t, wday_t, trend_t).cpu().numpy().reshape(-1)
    y_true = pack["y_true"]
    mu_w = pack["mu_w"]
    blocks = pack["blocks"]
    block_vals = []
    for g in range(4):
        rmse_g = _wrmse_block(y_true, y_pred, blocks == g, mu_w)
        if np.isfinite(rmse_g):
            block_vals.append(rmse_g)
    if not block_vals:
        return None
    return float(np.max(block_vals))


def _write_manifest(spec: OccupancySpec) -> None:
    raw = json.loads(spec_path().read_text(encoding="utf-8"))
    dump_json(
        {
            "occupancy": spec.to_dict(),
            "calibrator_version": raw.get("calibrator_version", CALIBRATOR_VERSION_V2),
            "stability_level": raw.get("stability_level"),
            "stability_hits": raw.get("stability_hits"),
            "stability_n_checks": raw.get("stability_n_checks"),
            "calibration_seed": CALIBRATION_SEED,
            "stability_seeds": list(STABILITY_SEEDS),
            "rho_star": RHO_STAR,
            "B_star": B_STAR,
            "rng_scheme": "always_advance_r3_rng_then_drop_A0_rows",
            "scd_rule": {
                "sensorscope": "raven (Design always_on; not Gate)",
                "uair": "raven_wo_design (Design always_off; not Gate)",
            },
            "gate_used": False,
            "generator_version": "e3-complete-aligned-r3-v1 + occupancy_spec",
            "git_commit": _git_commit(),
        },
        OUT / "INT_R_MANIFEST.json",
    )


def _mean_std(vals: list[float]) -> tuple[str, str]:
    arr = np.asarray(vals, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size != 20:
        return "TBD", "TBD"
    return f"{float(arr.mean()):.10g}", f"{float(arr.std(ddof=1)):.10g}"


def _holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = [1.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        raw = float(pvals[int(idx)]) * (m - rank)
        running = max(running, raw)
        adj[int(idx)] = min(1.0, running)
    return adj


def stage_tables() -> dict[str, Any]:
    ledger_path = OUT / "INT_R_TRAIN_LEDGER.json"
    if not ledger_path.is_file():
        raise FileNotFoundError(ledger_path)
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    rows = list(payload.get("rows") or [])
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    e3_methods = {
        "sensorscope": [
            "fedavg_window",
            "twostage_hajek",
            "fedau_window",
            "obsuse_window",
            "raven",
        ],
        "uair": [
            "fedavg_window",
            "twostage_hajek",
            "fedau_window",
            "obsuse_window",
            "raven_wo_design",
            "raven",
        ],
    }
    e3_out = []
    for dataset, methods in e3_methods.items():
        for method in methods:
            sub = [
                r
                for r in rows
                if r.get("dataset") == dataset and r.get("method") == method
            ]
            keys = {
                "RMSE_mu": "rmse_mu",
                "WorstGroupRMSE": "worstgroup",
                "Delta_group": "delta_group",
                "Delta_c_s": "delta_cs",
            }
            rec: dict[str, Any] = {"dataset": dataset, "method": method}
            for src, dst in keys.items():
                vals = [float(r[src]) for r in sub if r.get(src) is not None]
                mean_s, std_s = _mean_std(vals)
                rec[f"{dst}_mean"] = mean_s
                rec[f"{dst}_std"] = std_s
            e3_out.append(rec)
    e3_fields = [
        "dataset",
        "method",
        "rmse_mu_mean",
        "rmse_mu_std",
        "worstgroup_mean",
        "worstgroup_std",
        "delta_group_mean",
        "delta_group_std",
        "delta_cs_mean",
        "delta_cs_std",
    ]
    with (OUT / "tables" / "INT_R_E3.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=e3_fields)
        w.writeheader()
        w.writerows(e3_out)

    e4_row: dict[str, Any] = {
        "dataset": "sensorscope",
        "removed": "Design",
        "delta_group_pct": "TBD",
        "delta_cs_pct": "TBD",
        "rmse_mu_pct": "TBD",
        "tail_rmse_pct": "TBD",
        "holm_star_flags": "TBD",
    }
    scd = {
        int(r["seed"]): r
        for r in rows
        if r.get("dataset") == "sensorscope" and r.get("method") == "raven"
    }
    off = {
        int(r["seed"]): r
        for r in rows
        if r.get("dataset") == "sensorscope" and r.get("method") == "raven_wo_design"
    }
    common = sorted(set(scd) & set(off))
    metric_map = {
        "delta_group_pct": "Delta_group",
        "delta_cs_pct": "Delta_c_s",
        "rmse_mu_pct": "RMSE_mu",
        "tail_rmse_pct": "Tail_RMSE",
    }
    if len(common) == 20:
        rels = {}
        pvals = []
        names = []
        for out_key, src in metric_map.items():
            paired = []
            for seed in common:
                a = scd[seed].get(src)
                b = off[seed].get(src)
                if a is None or b is None or float(a) == 0:
                    paired = []
                    break
                paired.append((float(b) - float(a)) / float(a))
            if len(paired) != 20:
                e4_row[out_key] = "TBD"
                continue
            arr = np.asarray(paired, dtype=np.float64)
            e4_row[out_key] = f"{float(100.0 * arr.mean()):.10g}"
            rels[out_key] = arr
            names.append(out_key)
            se = float(arr.std(ddof=1) / np.sqrt(arr.size))
            if se <= 0:
                pvals.append(1.0)
            else:
                t = float(arr.mean() / se)
                try:
                    from math import erf

                    # two-sided from normal approx if scipy missing
                    p = float(2.0 * (1.0 - 0.5 * (1.0 + erf(abs(t) / np.sqrt(2.0)))))
                    pvals.append(p)
                except Exception:
                    pvals.append(float("nan"))
        if names and len(pvals) == len(names) and all(np.isfinite(pvals)):
            adj = _holm(pvals)
            stars = [n for n, p in zip(names, adj) if p < 0.05]
            e4_row["holm_star_flags"] = ",".join(stars) if stars else "none"
    with (OUT / "tables" / "INT_R_E4_DESIGN.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(e4_row.keys()))
        w.writeheader()
        w.writerow(e4_row)
    return {"e3": e3_out, "e4": e4_row}


def stage_train(*, max_runs: int | None, datasets: tuple[str, ...]) -> list[dict[str, Any]]:
    from raven_mcs.e3.real_runner.runner import run_e3_real

    spec = load_spec()
    _write_manifest(spec)
    schedule = [r for r in e3_schedule() if r["dataset"] in datasets]
    if max_runs is not None:
        schedule = schedule[: int(max_runs)]
    results = []
    art = OUT / "runs"
    for i, job in enumerate(schedule, 1):
        dataset = str(job["dataset"])
        seed = int(job["seed"])
        method = str(job["method"])
        run_dir = art / dataset / method / f"seed{seed}"
        marker = run_dir / "INT_R_ACCEPTED.json"
        print(f"[{i}/{len(schedule)}] TRAIN {dataset} {method} seed{seed}", flush=True)
        if marker.is_file():
            prev = json.loads(marker.read_text(encoding="utf-8"))
            results.append({"status": "REUSED", **prev})
            continue
        ds = load_paper_dataset(ROOT, dataset)
        mapping = load_spatial_to_client(ROOT, dataset)
        et = TRACE_ROOT / dataset / f"seed{seed}" / "training_eventtrace"
        row = run_e3_real(
            root=ROOT,
            run_dir=run_dir,
            dataset=ds,
            method=method,
            seed=seed,
            eventtrace_dir=et,
            spatial_to_client=mapping,
            dataset_name=dataset,
            local_steps=2,
        )
        metrics = row.get("metrics") or {}
        worst = _worst_group_rmse(run_dir, dataset)
        accepted = {
            "dataset": dataset,
            "method": method,
            "seed": seed,
            "status": row.get("status"),
            "RMSE_mu": metrics.get("RMSE_mu"),
            "Delta_group": metrics.get("Delta_group"),
            "Delta_c_s": metrics.get("Delta_c_s"),
            "Head_RMSE": metrics.get("Head_RMSE"),
            "Tail_RMSE": metrics.get("Tail_RMSE"),
            "WorstGroupRMSE": worst,
        }
        dump_json(accepted, marker)
        results.append(accepted)
        dump_json({"n": len(results), "rows": results}, OUT / "INT_R_TRAIN_LEDGER.json")
    dump_json({"n": len(results), "rows": results}, OUT / "INT_R_TRAIN_LEDGER.json")
    stage_tables()
    return results


def stage_recompute_worst() -> dict[str, Any]:
    """Recompute four-UTC WorstGroupRMSE from checkpoints. Does not retrain."""
    ledger_path = OUT / "INT_R_TRAIN_LEDGER.json"
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    rows = list(payload.get("rows") or [])
    n = 0
    for rec in rows:
        dataset = str(rec["dataset"])
        method = str(rec["method"])
        seed = int(rec["seed"])
        run_dir = OUT / "runs" / dataset / method / f"seed{seed}"
        worst = _worst_group_rmse(run_dir, dataset)
        rec["WorstGroupRMSE"] = worst
        marker = run_dir / "INT_R_ACCEPTED.json"
        if marker.is_file():
            accepted = json.loads(marker.read_text(encoding="utf-8"))
            accepted["WorstGroupRMSE"] = worst
            dump_json(accepted, marker)
        n += 1
        if n % 20 == 0:
            print(f"recompute_worst {n}/{len(rows)}", flush=True)
    dump_json({"n": len(rows), "rows": rows}, ledger_path)
    stage_tables()
    return {"n": n}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=["calibrate", "smoke", "generate", "audit", "train", "tables", "recompute_worst", "all"],
        default="all",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-runs", type=int, default=None)
    parser.add_argument("--dataset", choices=["sensorscope", "uair", "all"], default="all")
    parser.add_argument("--start-seed", type=int, default=None)
    parser.add_argument("--end-seed", type=int, default=None)
    args = parser.parse_args()
    datasets = DATASETS if args.dataset == "all" else (args.dataset,)
    if args.start_seed is not None or args.end_seed is not None:
        start = int(args.start_seed or FORMAL_SEEDS[0])
        end = int(args.end_seed or FORMAL_SEEDS[-1])
        seeds = [s for s in FORMAL_SEEDS if start <= s <= end]
    else:
        seeds = list(FORMAL_SEEDS)

    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage in {"calibrate", "all"}:
        print("STAGE calibrate", flush=True)
        print(json.dumps(stage_calibrate(), indent=2, default=str), flush=True)
    if args.stage in {"smoke", "all"}:
        print("STAGE smoke", flush=True)
        print(json.dumps(stage_smoke(), indent=2), flush=True)
    if args.stage in {"generate", "all"}:
        print("STAGE generate", flush=True)
        stage_generate(datasets=datasets, seeds=seeds, force=args.force)
    if args.stage in {"audit", "all"}:
        print("STAGE audit", flush=True)
        print(json.dumps(stage_audit(), indent=2, default=str), flush=True)
    if args.stage in {"train", "all"}:
        print("STAGE train", flush=True)
        stage_train(max_runs=args.max_runs, datasets=datasets)
    if args.stage == "recompute_worst":
        print("STAGE recompute_worst", flush=True)
        print(json.dumps(stage_recompute_worst(), indent=2, default=str), flush=True)
    if args.stage == "tables":
        print("STAGE tables", flush=True)
        print(json.dumps(stage_tables(), indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
