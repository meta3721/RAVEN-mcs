#!/usr/bin/env python3
"""H headroom experiment (stage 1): how much can oracle reweighting move RMSE_mu?

Pre-registration: ccfa-review-reports/raven-mcs-h-headroom-preregistration.md.
H_{c,b,s} = (RMSE_mu(FedAvg-Window) - RMSE_mu(RAVEN-SimOracle)) / RMSE_mu(FedAvg-Window)
under six frozen conditions on SensorScope and U-Air.  Runs the production E3
runner (run_e3_real) with four injection points: EventTrace directory,
opportunity tilt theta, target mu / pi_tar, and backbone.  Writes only to
results_h_headroom/round_v1/.
"""

from __future__ import annotations

import argparse
import dataclasses
import functools
import inspect
import json
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import raven_mcs.e3.real_runner.generator_r3 as gen  # noqa: E402
import raven_mcs.e3.real_runner.runner as e3runner  # noqa: E402
import raven_mcs.training.window_runner as wr  # noqa: E402
from raven_mcs.aggregation.method_policy import POLICY_MAP  # noqa: E402
from raven_mcs.aggregation.methods import RavenSimOracleAggregator  # noqa: E402
from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402
from raven_mcs.e3.canary.constants import M_MC  # noqa: E402
from raven_mcs.e3.canary.dataset_load import (  # noqa: E402
    load_horizon,
    load_paper_dataset,
    load_spatial_to_client,
)
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

OUT = ROOT / "results_h_headroom" / "round_v1"
# Overridden by CLI flags; defaults reproduce the round_v1 behaviour exactly.
REUSE_FROM: str | None = None
FREEZE_ARM_DATASET: str | None = None
FULL_SEED_DATASET: str | None = None
BASE_SEEDS: list[int] = list(range(30001, 30006))
DECISION_NAME = "H_DECISION.json"
FROZEN_E3 = ROOT / "artifacts" / "e3_formal_runs_r1"
DATASETS = ("sensorscope", "uair")
ORACLE_NODESIGN = "raven_simoracle_nodesign"
ARMS = ("fedavg_window", "raven_simoracle", ORACLE_NODESIGN)
GATE_ARMS = ("fedavg_window", "raven_simoracle")
# Frozen U-Air FedAvg-Window (2026-08-11) dropped clients whose (client, stratum)
# has pi_tar = 0; the current runner keeps them, so that one cell cannot match.
KNOWN_NONREPRO = {("uair", "fedavg_window")}
# Keys added to opportunity_features by later generator versions; events are otherwise identical.
TRACE_META_KEYS = {"drift_magnitude", "drift_period", "occupancy_A"}
SEEDS = list(range(30001, 30006))
LOCAL_STEPS = 2
GO_BAR = 0.005
REPRO_TOL = 1e-9
FROZEN_THETA = 1.25
FROZEN_TAIL_SCALE = 0.55

CONDITIONS: dict[str, dict[str, Any]] = {
    "C0_frozen": {"theta": 1.25, "tail_scale": 0.55, "model": "full", "target": "test_share"},
    "C1_tilt_strong": {"theta": 2.5, "tail_scale": 0.25, "model": "full", "target": "test_share"},
    "C2_tilt_extreme": {"theta": 4.0, "tail_scale": 0.10, "model": "full", "target": "test_share"},
    "C3_low_capacity": {"theta": 1.25, "tail_scale": 0.55, "model": "diurnal_blind", "target": "test_share"},
    "C4_block_uniform": {"theta": 1.25, "tail_scale": 0.55, "model": "full", "target": "block_uniform"},
    "C5_combined": {"theta": 4.0, "tail_scale": 0.10, "model": "diurnal_blind", "target": "block_uniform"},
}

_TAIL_LINE = "scale = 0.55 if block in {2, 3} else 1.0"
_src = inspect.getsource(gen.generate_complete_aligned_r3)
if _src.count(_TAIL_LINE) != 1:
    raise RuntimeError("generator p_obs tail line changed; refuse to inject")
exec(  # noqa: S102
    compile(_src.replace(_TAIL_LINE, "scale = _H_TAIL_SCALE if block in {2, 3} else 1.0"), gen.__file__, "exec"),
    gen.__dict__,
)
gen._H_TAIL_SCALE = FROZEN_TAIL_SCALE
_ORIG_BUILD_JOINT = gen.build_joint_pi_opp

POLICY_MAP[ORACLE_NODESIGN] = dataclasses.replace(POLICY_MAP["raven_simoracle"], uses_design_ratio=False)
_ORIG_GET_AGGREGATOR = wr.get_aggregator


def _get_aggregator(name: str):
    if str(name).strip().lower() == ORACLE_NODESIGN:
        return RavenSimOracleAggregator()
    return _ORIG_GET_AGGREGATOR(name)


wr.get_aggregator = _get_aggregator


class DiurnalBlindNDMF(CommonNDMF):
    """CommonNDMF with the three hour-of-day features zeroed (weekday, trend kept)."""

    _MASK = torch.tensor([0.0, 0.0, 1.0, 1.0, 0.0])

    @staticmethod
    def time_features(hour: torch.Tensor, weekday: torch.Tensor, trend: torch.Tensor) -> torch.Tensor:
        return CommonNDMF.time_features(hour, weekday, trend) * DiurnalBlindNDMF._MASK


def _diurnal_blind_factory(num_spatial: int, *, seed: int = 26001) -> CommonNDMF:
    torch.manual_seed(int(seed))
    return DiurnalBlindNDMF(num_spatial=num_spatial)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(line: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "EXECUTION_LOG.md").open("a", encoding="utf-8") as fh:
        fh.write(f"- {_now()} {line}\n")
    print(line, flush=True)


def _block_of(label: str) -> int:
    for part in str(label).split("::"):
        if part.startswith("block"):
            return int(part[5:])
    raise ValueError(f"no block in {label!r}")


def block_uniform_target(dataset: str, ds, mapping: dict[str, str]) -> tuple[dict, dict[int, float]]:
    atomic, _ = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset, root=ROOT)
    frame = atomic.copy()
    frame["target_group_main"] = frame["target_group"].astype(str)
    pi = build_pi_target(frame, mapping, split="test")
    mass_b: dict[int, float] = {}
    for r in pi.itertuples():
        b = _block_of(r.opportunity_stratum)
        mass_b[b] = mass_b.get(b, 0.0) + float(r.pi_k_s_tar)
    if sorted(mass_b) != [0, 1, 2, 3]:
        raise RuntimeError(f"expected 4 time blocks, got {sorted(mass_b)}")
    factor = {b: 0.25 / m for b, m in mass_b.items()}
    override = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar) * factor[_block_of(r.opportunity_stratum)]
        for r in pi.itertuples()
    }
    total = sum(override.values())
    if abs(total - 1.0) > 1e-9:
        raise RuntimeError(f"block-uniform pi_tar sums to {total}")
    return override, factor


@contextmanager
def injected(cond: dict[str, Any], *, block_factor: dict[int, float] | None):
    theta = float(cond["theta"])
    orig_runner_bjp = e3runner.build_joint_pi_opp
    orig_gen_bjp = gen.build_joint_pi_opp
    orig_bundle = e3runner.production_target_bundle
    orig_model = wr.deterministic_common_ndmf
    orig_scale = gen._H_TAIL_SCALE
    patched_bjp = functools.partial(_ORIG_BUILD_JOINT, theta_align=theta)
    try:
        e3runner.build_joint_pi_opp = patched_bjp
        gen.build_joint_pi_opp = patched_bjp
        gen._H_TAIL_SCALE = float(cond["tail_scale"])
        if cond["model"] == "diurnal_blind":
            wr.deterministic_common_ndmf = _diurnal_blind_factory
        if cond["target"] == "block_uniform":
            if block_factor is None:
                raise RuntimeError("block_uniform target needs block factors")

            def _bundle(**kw):
                b = orig_bundle(**kw)
                names = list(b["group_id_by_index"])
                mu = np.asarray(b["mu"], dtype=np.float64).copy()
                for i, name in enumerate(names):
                    mu[i] *= block_factor[_block_of(name)]
                b = dict(b)
                b["mu"] = mu / float(mu.sum())
                return b

            e3runner.production_target_bundle = _bundle
        yield
    finally:
        e3runner.build_joint_pi_opp = orig_runner_bjp
        gen.build_joint_pi_opp = orig_gen_bjp
        e3runner.production_target_bundle = orig_bundle
        wr.deterministic_common_ndmf = orig_model
        gen._H_TAIL_SCALE = orig_scale


def _needs_new_trace(cond: dict[str, Any]) -> bool:
    return float(cond["theta"]) != FROZEN_THETA or float(cond["tail_scale"]) != FROZEN_TAIL_SCALE


def trace_dir(cond_name: str, dataset: str, seed: int) -> Path:
    if not _needs_new_trace(CONDITIONS[cond_name]):
        return FROZEN_E3 / "eventtraces" / dataset / f"seed{seed}" / "training_eventtrace"
    return OUT / "eventtraces" / cond_name / dataset / f"seed{seed}" / "training_eventtrace"


def generate_trace(cond_name: str, dataset: str, seed: int, *, out_dir: Path | None = None) -> str:
    cond = CONDITIONS[cond_name]
    out = out_dir or trace_dir(cond_name, dataset, seed).parent
    ident = out / "training_eventtrace" / "trace_identity.json"
    if ident.is_file():
        return json.loads(ident.read_text(encoding="utf-8"))["trace_hash"]
    ds = load_paper_dataset(ROOT, dataset)
    mapping = load_spatial_to_client(ROOT, dataset)
    atomic, _ = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset, root=ROOT)
    n_windows = int(load_horizon(ROOT, dataset)["chosen_E3_formal_windows"])
    with injected({**cond, "target": "test_share"}, block_factor=None):
        mat = gen.materialize_r3_trace(
            dataset=dataset,
            atomic=atomic,
            spatial_to_client=mapping,
            out_dir=out,
            seed=int(seed),
            num_windows=n_windows,
            m_mc=M_MC,
            delivery_mode="nominal",
        )
    audit = dict(mat.get("audit") or {})
    dump_json({"condition": cond_name, **cond, "num_windows": n_windows, "m_mc": M_MC, "audit": audit},
              out / "generation_meta.json")
    return str(mat["identity"]["trace_hash"])


def run_arm(cond_name: str, dataset: str, method: str, seed: int, *, tag: str = "runs") -> dict[str, Any]:
    cond = CONDITIONS[cond_name]
    run_dir = OUT / tag / cond_name / dataset / method / f"seed{seed}"
    marker = run_dir / "final_metrics.json"
    if not marker.is_file():
        ds = load_paper_dataset(ROOT, dataset)
        mapping = load_spatial_to_client(ROOT, dataset)
        override, factor = (None, None)
        if cond["target"] == "block_uniform":
            override, factor = block_uniform_target(dataset, load_paper_dataset(ROOT, dataset), mapping)
        with injected(cond, block_factor=factor):
            e3runner.run_e3_real(
                root=ROOT,
                run_dir=run_dir,
                dataset=ds,
                method=method,
                seed=int(seed),
                eventtrace_dir=trace_dir(cond_name, dataset, seed),
                spatial_to_client=mapping,
                dataset_name=dataset,
                local_steps=LOCAL_STEPS,
                pi_target_override=override,
                source_identity={"git_commit": "h_headroom_r1", "condition": cond_name},
            )
    m = json.loads(marker.read_text(encoding="utf-8"))
    return {
        "condition": cond_name,
        "dataset": dataset,
        "method": method,
        "seed": int(seed),
        **{k: m.get(k) for k in ("RMSE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho", "runtime_seconds")},
    }


def _events_equal_ignoring_meta(a_dir: Path, b_dir: Path) -> bool:
    a = pd.read_parquet(a_dir / "events.parquet")
    b = pd.read_parquet(b_dir / "events.parquet")
    if list(a.columns) != list(b.columns) or len(a) != len(b):
        return False
    for col in a.columns:
        if col == "opportunity_features":
            continue
        if not a[col].astype(str).equals(b[col].astype(str)):
            return False

    def _strip(v):
        d = json.loads(v) if isinstance(v, str) else dict(v)
        return json.dumps({k: d[k] for k in sorted(d) if k not in TRACE_META_KEYS}, sort_keys=True, default=str)

    return a["opportunity_features"].map(_strip).equals(b["opportunity_features"].map(_strip))


def stage_gate(dataset: str) -> bool:
    seed = SEEDS[0]
    regen_root = OUT / "gate_regen" / dataset / f"seed{seed}"
    generate_trace("C0_frozen", dataset, seed, out_dir=regen_root)
    trace_ok = _events_equal_ignoring_meta(regen_root / "training_eventtrace", trace_dir("C0_frozen", dataset, seed))
    rows = {}
    for method in GATE_ARMS:
        row = run_arm("C0_frozen", dataset, method, seed, tag="gate")
        frozen = json.loads(
            (FROZEN_E3 / "runs" / dataset / method / f"seed{seed}" / "final_metrics.json").read_text(encoding="utf-8")
        )
        d = abs(float(row["RMSE_mu"]) - float(frozen["RMSE_mu"]))
        rows[method] = {"rerun": row["RMSE_mu"], "frozen": frozen["RMSE_mu"], "abs_diff": d,
                        "known_nonrepro": (dataset, method) in KNOWN_NONREPRO}
    smoke = run_arm("C0_frozen", dataset, ORACLE_NODESIGN, seed, tag="gate")
    arms_ok = all(r["abs_diff"] <= REPRO_TOL or r["known_nonrepro"] for r in rows.values())
    ok = trace_ok and arms_ok and np.isfinite(float(smoke["RMSE_mu"]))
    dump_json({"dataset": dataset, "seed": seed, "trace_events_equal_ignoring_meta": trace_ok,
               "trace_meta_keys_ignored": sorted(TRACE_META_KEYS), "arms": rows,
               "oracle_nodesign_smoke_RMSE_mu": smoke["RMSE_mu"], "tolerance": REPRO_TOL,
               "pass": ok, "utc": _now()}, OUT / f"GATE_{dataset}.json")
    _log(f"GATE {dataset} pass={ok} trace_ok={trace_ok} "
         + " ".join(f"{m}:d={r['abs_diff']:.2e}" for m, r in rows.items())
         + f" nodesign_oracle={smoke['RMSE_mu']:.6f}")
    return ok


def stage_runs(dataset: str, conditions: list[str]) -> None:
    gate = OUT / f"GATE_{dataset}.json"
    if not gate.is_file() or not json.loads(gate.read_text(encoding="utf-8"))["pass"]:
        raise SystemExit(f"gate for {dataset} has not passed")
    for cond_name in conditions:
        for seed in SEEDS:
            if _needs_new_trace(CONDITIONS[cond_name]):
                h = generate_trace(cond_name, dataset, seed)
                _log(f"TRACE {cond_name} {dataset} seed{seed} hash={h[:12]}")
            for method in ARMS:
                row = run_arm(cond_name, dataset, method, seed)
                _log(f"RUN {cond_name} {dataset} {method} seed{seed} RMSE_mu={row['RMSE_mu']:.6f}")


def stage_tables() -> None:
    reuse_root = (ROOT / "results_h_headroom" / REUSE_FROM) if REUSE_FROM else None
    rows = []
    for cond_name in CONDITIONS:
        for dataset in DATASETS:
            for method in ARMS:
                for seed in SEEDS:
                    source = "new"
                    marker = OUT / "runs" / cond_name / dataset / method / f"seed{seed}" / "final_metrics.json"
                    if not marker.is_file() and reuse_root is not None:
                        marker = (reuse_root / "runs" / cond_name / dataset / method
                                  / f"seed{seed}" / "final_metrics.json")
                        source = "reuse"
                    if marker.is_file():
                        m = json.loads(marker.read_text(encoding="utf-8"))
                        rows.append({"condition": cond_name, "dataset": dataset, "method": method,
                                     "seed": seed, "source": source,
                                     **{k: m.get(k) for k in ("RMSE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho")}})
    df = pd.DataFrame(rows)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "tables" / "H_seed_rows.csv", index=False)
    from scipy import stats

    summary = []
    for (cond_name, dataset), sub in df.groupby(["condition", "dataset"]):
        u = sub[sub["method"] == "fedavg_window"].set_index("seed")
        od = sub[sub["method"] == "raven_simoracle"].set_index("seed")
        ond = sub[sub["method"] == ORACLE_NODESIGN].set_index("seed")
        common = sorted(set(u.index) & set(od.index) & set(ond.index))
        if len(common) < 2:
            continue
        rec: dict[str, Any] = {"condition": cond_name, "dataset": dataset, "n": len(common)}

        def _ci(x: np.ndarray, name: str) -> None:
            half = float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))
            rec[name] = float(x.mean())
            rec[f"{name}_ci_lo"] = float(x.mean() - half)
            rec[f"{name}_ci_hi"] = float(x.mean() + half)

        for metric in ("RMSE_mu", "Tail_RMSE", "RMSE_rho"):
            uu = u.loc[common, metric].to_numpy(float)
            dd = od.loc[common, metric].to_numpy(float)
            nn = ond.loc[common, metric].to_numpy(float)
            # Revision 2: the frozen dataset's oracle arm is pinned to the NoDesign arm, so the
            # better-arm choice is not re-made on the extended sample.
            if dataset == FREEZE_ARM_DATASET:
                best = nn
            else:
                best = dd if float(od.loc[common, "RMSE_mu"].mean()) <= float(ond.loc[common, "RMSE_mu"].mean()) else nn
            _ci((uu - best) / uu, f"H_{metric}")
            _ci((uu - dd) / uu, f"H_design_{metric}")
            _ci((uu - nn) / uu, f"H_nodesign_{metric}")
            _ci((dd - nn) / nn, f"design_support_cost_{metric}")
        if dataset == FREEZE_ARM_DATASET:
            rec["best_oracle"] = ORACLE_NODESIGN
        else:
            rec["best_oracle"] = (
                "raven_simoracle"
                if float(od.loc[common, "RMSE_mu"].mean()) <= float(ond.loc[common, "RMSE_mu"].mean())
                else ORACLE_NODESIGN
            )
        rec["arm_frozen"] = bool(dataset == FREEZE_ARM_DATASET)
        rec["n_reused"] = int((sub["source"] == "reuse").sum() // len(ARMS))
        rec["fedavg_RMSE_mu_mean"] = float(u.loc[common, "RMSE_mu"].mean())
        rec["simoracle_RMSE_mu_mean"] = float(od.loc[common, "RMSE_mu"].mean())
        rec["simoracle_nodesign_RMSE_mu_mean"] = float(ond.loc[common, "RMSE_mu"].mean())
        rec["go"] = bool(cond_name != "C0_frozen" and rec["H_RMSE_mu"] >= GO_BAR and rec["H_RMSE_mu_ci_lo"] > 0)
        summary.append(rec)
    sm = pd.DataFrame(summary)
    sm.to_csv(OUT / "tables" / "H_summary.csv", index=False)
    expected_n = len(SEEDS)
    if FULL_SEED_DATASET is not None:
        base_n = len(BASE_SEEDS)
        complete = len(sm) == len(CONDITIONS) * len(DATASETS)
        per_ds_expected: dict[str, int] = {}
        for ds in DATASETS:
            want = expected_n if ds == FULL_SEED_DATASET else base_n
            per_ds_expected[ds] = want
            complete = complete and bool((sm.loc[sm["dataset"] == ds, "n"] == want).all())
    else:
        per_ds_expected = {ds: expected_n for ds in DATASETS}
        complete = len(sm) == len(CONDITIONS) * len(DATASETS) and bool((sm["n"] == expected_n).all())
    go_cells = sm.loc[sm["go"], ["condition", "dataset"]].to_dict("records")
    dump_json({"complete": complete, "go_bar": GO_BAR,
               "decision": ("GO" if go_cells else "STOP") if complete else "INCOMPLETE",
               "go_cells": go_cells, "n_seeds": expected_n, "n_seeds_base": len(BASE_SEEDS),
               "expected_n_per_dataset": per_ds_expected,
               "full_seed_dataset": FULL_SEED_DATASET,
               "round": OUT.name, "reuse_from": REUSE_FROM,
               "arm_frozen_dataset": FREEZE_ARM_DATASET, "utc": _now()}, OUT / DECISION_NAME)
    _log(f"TABLES complete={complete} go_cells={go_cells} n={expected_n} -> {DECISION_NAME}")


def _parse_seeds(spec: str) -> list[int]:
    spec = str(spec).strip()
    if "-" in spec and "," not in spec:
        lo, hi = spec.split("-", 1)
        return list(range(int(lo), int(hi) + 1))
    return [int(x) for x in spec.split(",") if x.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("gate", "runs", "tables"), required=True)
    ap.add_argument("--dataset", choices=DATASETS)
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--round", default="round_v1",
                    help="output round directory under results_h_headroom/")
    ap.add_argument("--seeds", default="30001-30005",
                    help="inclusive range A-B, or a comma list")
    ap.add_argument("--reuse-from", default=None,
                    help="prior round directory whose runs supply reused seeds (tables stage)")
    ap.add_argument("--freeze-arm-dataset", default=None,
                    help="dataset whose oracle arm is pinned to the NoDesign arm (revision 2)")
    ap.add_argument("--decision-name", default="H_DECISION.json")
    ap.add_argument("--full-seed-dataset", default=None,
                    help="dataset that must reach every seed in --seeds; others may be partial")
    ap.add_argument("--base-seeds", default="30001-30005",
                    help="seed set expected of the non-extended datasets (tables completeness)")
    args = ap.parse_args()

    global OUT, SEEDS, REUSE_FROM, FREEZE_ARM_DATASET, DECISION_NAME, FULL_SEED_DATASET, BASE_SEEDS
    OUT = ROOT / "results_h_headroom" / args.round
    SEEDS = _parse_seeds(args.seeds)
    REUSE_FROM = args.reuse_from
    FREEZE_ARM_DATASET = args.freeze_arm_dataset
    DECISION_NAME = args.decision_name
    FULL_SEED_DATASET = args.full_seed_dataset
    BASE_SEEDS = _parse_seeds(args.base_seeds)

    if args.stage == "tables":
        stage_tables()
        return 0
    if args.dataset is None:
        raise SystemExit("--dataset required")
    if args.stage == "gate":
        return 0 if stage_gate(args.dataset) else 2
    stage_runs(args.dataset, [c for c in args.conditions.split(",") if c])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
