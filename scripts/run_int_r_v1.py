#!/usr/bin/env python3
"""INT-R-E3 executor: calibrate occupancy, generate traces, audit, optional training.

Does not edit the manuscript. Does not invent metrics. Gate_t is not the Design switch.
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
    OccupancySpec,
    RHO_STAR,
    calibrate_markov,
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

OUT = ROOT / "results_int_r" / "round_v1"
TRACE_ROOT = ROOT / "artifacts" / "e3_int_r_eventtraces"
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
    mapping = load_spatial_to_client(ROOT, "sensorscope")
    n_clients = len(sorted(set(mapping.values())))
    n_windows = int(load_horizon(ROOT, "sensorscope")["chosen_E3_formal_windows"])
    spec = calibrate_markov(n_clients=n_clients, n_windows=n_windows)
    from raven_mcs.e3.int_r.occupancy import occupancy_rng, simulate_occupancy

    A = simulate_occupancy(
        n_clients=n_clients,
        n_windows=n_windows,
        spec=spec,
        rng=occupancy_rng("sensorscope", CALIBRATION_SEED),
    )
    met = occupancy_metrics(A)
    payload = {
        **spec.to_dict(),
        "calibration_seed": CALIBRATION_SEED,
        "n_clients_sensorscope": n_clients,
        "n_windows_sensorscope": n_windows,
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
    row = {
        "forced_ones_matches_always_on": True,
        "inactive_have_no_rows": bool(empty_inactive),
        "canary_n_event_rows": int(a2["n_event_rows"]),
        "canary_n_client_windows": int(a2["n_client_windows"]),
        "occupancy_source_label_leak": bool(leak),
        "gate_used": False,
    }
    dump_json(row, OUT / "INT_R_SMOKE.json")
    if leak or not empty_inactive:
        raise RuntimeError(f"INT-R smoke failed: {row}")
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

    ss = next(r for r in rows if r["dataset"] == "sensorscope" and r["seed"] == 30001)
    ua = next(r for r in rows if r["dataset"] == "uair" and r["seed"] == 30001)
    gates["INT-R-OCC-1"] = 0.35 <= ss["mean_active_frac"] <= 0.50 and 0.35 <= ua["mean_active_frac"] <= 0.50
    if spec.family == "bernoulli_iid":
        gates["INT-R-OCC-2"] = True
    else:
        gates["INT-R-OCC-2"] = ss["burstiness_pooled"] > 0 and ua["burstiness_pooled"] > 0
    gates["INT-R-OCC-3"] = ss["tv_opp_mu"] > TV_THRESHOLD and ua["tv_opp_mu"] > TV_THRESHOLD
    occ_src = (ROOT / "src" / "raven_mcs" / "e3" / "int_r" / "occupancy.py").read_text(
        encoding="utf-8"
    ).lower()
    gates["INT-R-OCC-4"] = all(s not in occ_src for s in ("rmse", "y_i", "test_error"))
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


def stage_train(*, max_runs: int | None, datasets: tuple[str, ...]) -> list[dict[str, Any]]:
    from raven_mcs.e3.real_runner.runner import run_e3_real

    spec = load_spec()
    dump_json(
        {
            "occupancy": spec.to_dict(),
            "calibration_seed": CALIBRATION_SEED,
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
    schedule = [
        r for r in e3_schedule() if r["dataset"] in datasets
    ]
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
        }
        dump_json(accepted, marker)
        results.append(accepted)
    dump_json({"n": len(results), "rows": results}, OUT / "INT_R_TRAIN_LEDGER.json")
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=["calibrate", "smoke", "generate", "audit", "train", "all"],
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
        print(json.dumps(stage_calibrate(), indent=2), flush=True)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
