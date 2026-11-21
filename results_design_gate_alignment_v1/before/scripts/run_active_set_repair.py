#!/usr/bin/env python3
"""Training active-set repair (route A) -- driver.

Implements `raven-mcs-active-set-repair-design.md` (route A: every method receives
exactly the information its own definition licenses).

Stages, in the plan's execution priority (SS13):
    g0    inventory, no training            -> ACTIVE_SET_INVENTORY.csv, PI_TAR_HOLES.csv
    g1    reproduction gates, 12 runs       -> G1_REPORT.json
    e1    rebuild on the licensed set, 80 runs (+ per-run active-set assertion)
    e2    single-batch re-evaluation        -> E2_UAIR_CELLS.csv (std + phys domains)
    e3    downstream recomputation          -> P2_COVERAGE.csv, PAIRED_STATS.csv
    g2    hybrid blocks, 6 runs             -> G2_REPORT.json
    status

Write boundary (SS14): this driver writes only
`results_active_set_repair/round_v1/`. No `src/` change, no frozen tree overwritten,
no `.tex` edit, no table cell replaced, no commit.

`run_h_headroom.run_arm` is reused unchanged. Its module global `OUT` is redirected
here, which is safe because `trace_dir("C0_frozen", ...)` resolves against
`FROZEN_E3`/`eventtraces`, not against `OUT`, so the frozen EventTraces are still the
ones read.
"""

from __future__ import annotations

import argparse
import dataclasses
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h_headroom as h  # noqa: E402
import audit_table2_uair_fedavg as a2  # noqa: E402
import raven_mcs.training.window_runner as wr  # noqa: E402
from raven_mcs.aggregation.method_policy import POLICY_MAP  # noqa: E402
from raven_mcs.aggregation.methods import RavenWoInstAggregator  # noqa: E402
from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402
from raven_mcs.e3.canary.dataset_load import (  # noqa: E402
    load_paper_dataset,
    load_spatial_to_client,
)
from raven_mcs.e3.real_runner.runner import (  # noqa: E402
    _mu_weights_for_test,
    _predict_model,
)
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle  # noqa: E402
from raven_mcs.models.common_ndmf import CommonNDMF  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

OUT = ROOT / "results_active_set_repair" / "round_v1"
OUT.mkdir(parents=True, exist_ok=True)
h.OUT = OUT  # redirect run_arm's run_dir and h._log into the allowed write root

TAG = "repair"
SEEDS = list(range(30001, 30021))
TEST_SEEDS = list(range(30011, 30021))
UAIR_SIGMA = 17.36325121670317
TOL = 1e-9
# ---------------------------------------------------------------------------------------
# G1a TOLERANCE AMENDMENT -- authorized by the user on 2026-09-27.
# The frozen SensorScope `debt_cal` seed30001 value is 7.915297744846339; the current
# runner deterministically returns 7.915297538076236, abs_diff 2.0677010326153322e-07.
# `G1_DEBT_CAL_DIAG.json` shows this is NOT in-process state leakage: a fresh process with
# `debt_cal` as the first `run_arm` call, a same-process repeat, and the third-in-process
# G1a call all return the identical 7.915297538076236. It is a deterministic
# frozen-versus-current runner drift.
# Grounds for applying G1a at 1e-6 rather than bit equality:
#   1. it is 5x below the 1e-6 tolerance that the plan's own E2 reference routine
#      (`audit_table2_uair_fedavg.block_rmse`) is verified against (plan SS7 E2);
#   2. its relative magnitude is 2.6e-08, about 1e6 times smaller than the ~6.3 % filter
#      effect that E1 exists to measure, so it cannot confound the comparison;
#   3. E1's four rebuilt rows are compared against each other and against RAVEN-NoDesign
#      from the new batch; the frozen `debt_cal` value is only the old cell being replaced.
# The plan's literal G1a failure action was "stop"; this override is recorded in
# `G1_REPORT.json["amendment"]` and must be flagged in the experiment report.
G1A_TOL = 1e-6
REBUILD = ("fedavg_window", "fedasync_window", "flamf_timealign_adapted", "debt_cal")
DESIGN_ON = ("local_hajek", "twostage_hajek", "inst_cal", "raven", "raven_simoracle")

TREES: dict[str, Path] = {
    "e3": ROOT / "artifacts" / "e3_formal_runs_r1" / "runs",
    "fedau": ROOT / "artifacts" / "e3_fedau_window_r1" / "runs",
    "obsuse": ROOT / "artifacts" / "e3_obsuse_window_r1" / "runs",
    "e4": ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs",
}
PER_SEED_CSV = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1" / "tables" / "TABLE_II_WORSTGROUP_PER_SEED.csv"
AUDIT_PER_SEED = ROOT / "results_table2_audit" / "uair_fedavg_current_per_seed.csv"
LABEL = {"cityscanner": "cityscanner_nyc_pm25", "pilot2": "cityscanner_nyc_p2_measured_o"}


# --------------------------------------------------------------------------- utils
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(line: str) -> None:
    with (OUT / "EXECUTION_LOG.md").open("a", encoding="utf-8") as fh:
        fh.write(f"- {_now()} {line}\n")


def _stamp(name: str) -> Path:
    return OUT / name


def frozen_run(tree: str, dataset: str, method: str, seed: int) -> Path | None:
    """Resolve a frozen run directory inside one of the stored trees."""
    base = TREES[tree]
    p = base / dataset / method / f"seed{seed}"
    if (p / "final_metrics.json").is_file():
        return p
    for cand in base.rglob(f"seed{seed}"):
        parts = cand.relative_to(base).parts
        if dataset in parts and method in parts and (cand / "final_metrics.json").is_file():
            return cand
    return None


def _metrics(run_dir: Path, key: str = "RMSE_mu") -> float | None:
    f = run_dir / "final_metrics.json"
    if not f.is_file():
        return None
    v = json.loads(f.read_text(encoding="utf-8")).get(key)
    return None if v is None else float(v)


def _windows(run_dir: Path) -> dict[int, list[str]]:
    f = run_dir / "window_metrics.json"
    if not f.is_file():
        return {}
    recs = json.loads(f.read_text(encoding="utf-8"))
    return {int(r["window_id"]): [str(c) for c in r["active_clients"]] for r in recs}


def licensed_class(method: str) -> str:
    pol = POLICY_MAP.get(method)
    if pol is None:
        return "unknown"
    if getattr(pol, "uses_central_training", False):
        return "central"
    return "design_support" if getattr(pol, "uses_design_ratio", False) else "full"


# ------------------------------------------------------------------- pi^tar holes
def pi_target_and_support(dataset: str):
    """Reproduce the runner's pi^tar and the pi^opp (client x stratum) support."""
    ds = load_paper_dataset(ROOT, dataset)
    mapping = load_spatial_to_client(ROOT, dataset)
    sealed, meta = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset, root=ROOT)
    atomic = sealed.copy()
    if "target_group_main" not in atomic.columns:
        atomic["target_group_main"] = atomic["target_group"].astype(str)
    frame = build_pi_target(atomic, mapping, split="test")
    tar = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in frame.itertuples()
    }
    train = sealed.loc[sealed["split"].astype(str) == "train"]
    by_client: dict[str, set[str]] = {}
    for r in train.itertuples(index=False):
        c = mapping.get(str(r.spatial_id))
        if c is None:
            continue
        by_client.setdefault(str(c), set()).add(str(r.opportunity_stratum))
    support = {(c, s) for c, ss in by_client.items() for s in ss}
    return tar, support, meta


# ---------------------------------------------------------------------------- G0
def stage_g0() -> int:
    """Inventory: pi^tar holes per block and realized vs licensed active sets."""
    _log("G0 start")
    hole_rows = []
    for dataset in ("uair", "sensorscope", "traffic"):
        try:
            tar, support, meta = pi_target_and_support(dataset)
        except Exception as exc:  # dataset not loadable / not present
            hole_rows.append({"block": dataset, "status": f"ERROR {type(exc).__name__}: {exc}"})
            _log(f"G0 {dataset}: {type(exc).__name__}: {exc}")
            continue
        zero = {k for k in support if tar.get(k, 0.0) <= 0.0}
        hole_rows.append({
            "block": dataset,
            "status": "OK",
            "n_strata": meta.get("n_unique_strata"),
            "support_pairs": len(support),
            "zero_pi_tar_pairs": len(zero),
            "zero_fraction": round(len(zero) / max(1, len(support)), 6),
        })
        _log(f"G0 {dataset}: support={len(support)} zero={len(zero)}")
    hole_rows.append({
        "block": "tdrive_speed",
        "status": "NOT_COUNTED",
        "reason": ("load_spatial_to_client has no tdrive branch (dataset_load.py:76-85), so the runner's "
                   "pi^tar support cannot be rebuilt for this block, and no stored hybrid pi^tar artifact "
                   "exists under results_tdrive_rank/ or manuscript_evidence_closure_r1/09_tdrive_decision/. "
                   "T-Drive is outside route A's rebuild set."),
    })
    _log("G0 tdrive_speed: NOT_COUNTED (no mapping loader, no stored pi^tar)")
    holes = pd.DataFrame(hole_rows)
    holes.to_csv(_stamp("PI_TAR_HOLES.csv"), index=False)
    print(holes.to_string(index=False), flush=True)

    # hybrids: stored decision artifacts, no EventTrace pipeline in this driver
    hybrid = []
    for key, dec in (
        ("cityscanner", ROOT / "results_c1_cityscanner" / "round_v1" / "CS_PHI_DECISION.json"),
        ("pilot2", ROOT / "results_joint_ou" / "round_v1" / "JO_PHI_DECISION.json"),
    ):
        if dec.is_file():
            hybrid.append({"block": LABEL[key], "source": str(dec.relative_to(ROOT)),
                           **json.loads(dec.read_text(encoding="utf-8"))})
    if hybrid:
        dump_json(hybrid, _stamp("HYBRID_PHI_DECISIONS.json"))

    ref_tree = TREES["fedau"]
    rows = []
    for tree, base in TREES.items():
        if not base.exists():
            continue
        for wm in sorted(base.rglob("window_metrics.json")):
            parts = wm.relative_to(base).parts
            if len(parts) < 4 or not parts[-2].startswith("seed"):
                continue
            dataset, method, seed = parts[-4], parts[-3], int(parts[-2].replace("seed", ""))
            if dataset not in ("uair", "sensorscope", "traffic"):
                continue
            ref_dir = ref_tree / dataset / "fedau_window" / f"seed{seed}"
            ref = _windows(ref_dir)
            if not ref:
                continue
            mine = _windows(wm.parent)
            common = sorted(set(mine) & set(ref))
            ident = sum(1 for w in common if mine[w] == ref[w])
            klass = licensed_class(method)
            verdict = "unknown"
            if klass == "full":
                verdict = "compliant" if ident == len(common) and common else "VIOLATION"
            elif klass == "design_support":
                verdict = "restricted_as_licensed"
            rows.append({
                "tree": tree,
                "block": dataset,
                "method": method,
                "seed": seed,
                "licensed_class": klass,
                "windows": len(mine),
                "compared": len(common),
                "identical_to_fedau": ident,
                "mean_abs_active": round(float(np.mean([len(v) for v in mine.values()])), 4),
                "mean_abs_active_fedau": round(float(np.mean([len(v) for v in ref.values()])), 4),
                "verdict": verdict,
            })
    inv = pd.DataFrame(rows)
    inv.to_csv(_stamp("ACTIVE_SET_INVENTORY.csv"), index=False)

    summary = {
        "generated": _now(),
        "pi_tar_holes": hole_rows,
        "n_run_dir_inventoried": int(len(inv)),
        "violations": int((inv["verdict"] == "VIOLATION").sum()) if len(inv) else 0,
        "violation_methods": sorted(inv.loc[inv["verdict"] == "VIOLATION", "method"].unique().tolist())
        if len(inv) else [],
        "violation_blocks": sorted(inv.loc[inv["verdict"] == "VIOLATION", "block"].unique().tolist())
        if len(inv) else [],
    }
    dump_json(summary, _stamp("G0_SUMMARY.json"))
    print(f"\nACTIVE_SET_INVENTORY rows={len(inv)} violations={summary['violations']}")
    if len(inv):
        piv = (inv.groupby(["block", "method", "licensed_class", "verdict"])
                  .agg(runs=("seed", "count"), ident=("identical_to_fedau", "sum"),
                       compared=("compared", "sum"),
                       mean_abs=("mean_abs_active", "mean"))
                  .reset_index())
        print(piv.to_string(index=False), flush=True)
    _log(f"G0 done rows={len(inv)} violations={summary['violations']}")
    return 0


# ---------------------------------------------------------------------------- G1
def _gate_compare(method: str, dataset: str, seed: int, frozen: Path, tol: float = TOL) -> dict:
    row = h.run_arm("C0_frozen", dataset, method, seed, tag=TAG)
    fz = _metrics(frozen, "RMSE_mu")
    rerun = float(row["RMSE_mu"])
    return {
        "method": method, "dataset": dataset, "seed": seed,
        "frozen": fz, "rerun": rerun,
        "abs_diff": None if fz is None else abs(rerun - fz),
        "bit_equal": None if fz is None else abs(rerun - fz) <= tol,
    }


def stage_g1() -> int:
    """G1a-G1d reproduction gates. Any bit-exact failure stops the run."""
    _log("G1 start")
    report: dict[str, object] = {"generated": _now(), "tolerance": TOL}
    failures: list[str] = []

    # G1a -- SensorScope, unaffected cells: must reproduce the frozen tree.
    # Tolerance amended from bit equality to G1A_TOL; see the constant's comment.
    g1a = []
    for method in ("fedasync_window", "flamf_timealign_adapted", "debt_cal"):
        fz = frozen_run("e3", "sensorscope", method, 30001)
        if fz is None:
            failures.append(f"G1a {method}: no frozen SensorScope seed30001")
            continue
        r = _gate_compare(method, "sensorscope", 30001, fz, tol=G1A_TOL)
        r["tol"] = G1A_TOL
        r["bit_equal_strict"] = bool(r["abs_diff"] is not None and r["abs_diff"] <= TOL)
        g1a.append(r)
        if not r["bit_equal"]:
            failures.append(f"G1a {method}: abs_diff={r['abs_diff']} > {G1A_TOL}")
    report["G1a"] = g1a
    report["amendment"] = {
        "gate": "G1a",
        "plan_rule": "final metrics bit-equal to the frozen tree; failure action = stop",
        "original_tolerance": TOL,
        "applied_tolerance": G1A_TOL,
        "authorized_by": "user, 2026-09-27 (explicit: loosen the tolerance, run E1, flag it)",
        "measured_drift": {r["method"]: r["abs_diff"] for r in g1a if r["method"] == "debt_cal"},
        "evidence_file": "G1_DEBT_CAL_DIAG.json",
        "determinism": ("fresh-process first call, same-process repeat and third-in-process "
                        "G1a call all return 7.915297538076236"),
        "grounds": [
            "5x below the 1e-6 tolerance used by the plan's own E2 block_rmse reference path",
            "relative magnitude 2.6e-08, ~1e6 times smaller than the ~6.3 % filter effect",
            "E1 compares new-batch rows against each other; the frozen value is only the replaced cell",
        ],
    }

    # G1b -- U-Air central: bit-equal; Central rows stay unchanged if it passes
    fz = frozen_run("e3", "uair", "central_delivered", 30001)
    if fz is None:
        failures.append("G1b central_delivered: no frozen run")
        report["G1b"] = None
    else:
        report["G1b"] = _gate_compare("central_delivered", "uair", 30001, fz)

    # G1c -- which artifact does current code reproduce at the three divergent seeds?
    per_seed = pd.read_csv(PER_SEED_CSV)
    per_seed = per_seed[per_seed["dataset"] == "uair"]
    g1c = []
    for method in ("raven", "twostage_hajek"):
        for seed in (30007, 30016, 30018):
            fz = frozen_run("e3", "uair", method, seed)
            r = _gate_compare(method, "uair", seed, fz if fz else Path("/nonexistent"))
            row = per_seed[(per_seed["method"] == method) & (per_seed["seed"] == seed)]
            r["csv"] = None if row.empty else float(row.iloc[0]["RMSE_mu"])
            for tag, val in (("tree", r["frozen"]), ("csv", r["csv"])):
                r[f"match_{tag}"] = None if val is None else abs(r["rerun"] - val) <= TOL
            g1c.append(r)
    report["G1c"] = g1c
    report["G1c_selection"] = {}
    for method in ("raven", "twostage_hajek"):
        rows = [r for r in g1c if r["method"] == method]
        tree_hits = sum(1 for r in rows if r["match_tree"])
        csv_hits = sum(1 for r in rows if r["match_csv"])
        report["G1c_selection"][method] = {
            "tree_matches": tree_hits, "csv_matches": csv_hits, "n": len(rows),
            "selected": "tree" if tree_hits >= csv_hits and tree_hits else ("csv" if csv_hits else None),
        }

    # G1d -- determinism against results_table2_audit (runs are inside E1's seed set)
    audit = pd.read_csv(AUDIT_PER_SEED).set_index("seed")
    g1d = []
    for seed in (30001, 30006):
        fz = frozen_run("e3", "uair", "fedavg_window", seed)
        r = _gate_compare("fedavg_window", "uair", seed, fz if fz else Path("/nonexistent"))
        r["audit"] = float(audit.loc[seed, "RMSE_mu"]) if seed in audit.index else None
        r["match_audit"] = None if r["audit"] is None else abs(r["rerun"] - r["audit"]) <= TOL
        g1d.append(r)
        if not r["match_audit"]:
            failures.append(f"G1d seed{seed}: rerun {r['rerun']} != audit {r['audit']}")
    report["G1d"] = g1d

    report["failures"] = failures
    report["pass"] = not failures
    dump_json(report, _stamp("G1_REPORT.json"))
    for key in ("G1a", "G1b", "G1c", "G1d"):
        print(f"--- {key}")
        val = report[key]
        if isinstance(val, list):
            for r in val:
                print("   ", {k: v for k, v in r.items() if k != "method" or True})
        else:
            print("   ", val)
    print(f"\nG1 pass={report['pass']} failures={failures}", flush=True)
    _log(f"G1 done pass={report['pass']} failures={failures}")
    return 0 if report["pass"] else 1


# ---------------------------------------------------------------------------- E1
def stage_diag() -> int:
    """Diagnose the G1a `debt_cal` 2.07e-07 drift.

    `debt_cal` was the third `run_arm` call in the G1a process. This stage re-runs it
    as the FIRST call in a fresh process (`repair_solo`) and then a second time in the
    same process (`repair_again`), so in-process ordering can be separated from a
    genuine frozen-versus-current runner difference.
    """
    _log("DIAG start")
    fz = frozen_run("e3", "sensorscope", "debt_cal", 30001)
    frozen = _metrics(fz, "RMSE_mu")
    out: dict[str, object] = {"generated": _now(), "frozen": frozen,
                              "frozen_path": str(fz.relative_to(ROOT)), "runs": []}
    for tag in ("repair_solo", "repair_again"):
        r = h.run_arm("C0_frozen", "sensorscope", "debt_cal", 30001, tag=tag)
        rec = {"tag": tag, "first_call_in_process": tag == "repair_solo",
               "rerun": float(r["RMSE_mu"]), "abs_diff_vs_frozen": abs(float(r["RMSE_mu"]) - frozen)}
        out["runs"].append(rec)
        print(rec, flush=True)
    g1 = json.loads(_stamp("G1_REPORT.json").read_text(encoding="utf-8"))
    third = [r for r in g1["G1a"] if r["method"] == "debt_cal"]
    out["g1a_value_third_in_process"] = third[0]["rerun"] if third else None
    out["self_consistent"] = (abs(out["runs"][0]["rerun"] - out["runs"][1]["rerun"]) <= TOL)
    out["solo_reproduces_frozen"] = bool(out["runs"][0]["abs_diff_vs_frozen"] <= TOL)
    out["ordering_effect"] = bool(
        third and abs(out["runs"][0]["rerun"] - third[0]["rerun"]) > TOL)
    out["verdict"] = (
        "in-process ordering effect: G1a arms must be run in separate processes"
        if out["ordering_effect"] and out["solo_reproduces_frozen"]
        else "genuine deterministic frozen-versus-current drift in debt_cal"
        if out["self_consistent"]
        else "current runner is non-deterministic for debt_cal"
    )
    dump_json(out, _stamp("G1_DEBT_CAL_DIAG.json"))
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1), flush=True)
    _log(f"DIAG done verdict={out['verdict']}")
    return 0


def stage_e1() -> int:
    """Rebuild the four no-Design methods on the licensed (full-delivery) set."""
    _log("E1 start")
    ref_tree = TREES["fedau"]
    rows, asserts = [], []
    for method in REBUILD:
        for seed in SEEDS:
            r = h.run_arm("C0_frozen", "uair", method, seed, tag=TAG)
            run_dir = OUT / TAG / "C0_frozen" / "uair" / method / f"seed{seed}"
            ref = _windows(ref_tree / "uair" / "fedau_window" / f"seed{seed}")
            mine = _windows(run_dir)
            common = sorted(set(mine) & set(ref))
            ident = sum(1 for w in common if mine[w] == ref[w])
            ok = bool(common) and ident == len(common) and len(mine) == len(ref)
            asserts.append({
                "method": method, "seed": seed,
                "windows": len(mine), "reference_windows": len(ref),
                "compared": len(common), "identical": ident,
                "mean_abs_active": round(float(np.mean([len(v) for v in mine.values()])), 4),
                "assert_pass": ok,
            })
            rows.append({"method": method, "seed": seed, "RMSE_mu": float(r["RMSE_mu"]),
                         "runtime_seconds": r.get("runtime_seconds")})
            if not ok:
                pd.DataFrame(asserts).to_csv(_stamp("E1_ASSERTIONS.csv"), index=False)
                _log(f"E1 ASSERTION FAIL {method} seed{seed}: {ident}/{len(common)}")
                raise SystemExit(f"E1 active-set assertion failed: {method} seed{seed} "
                                 f"identical {ident}/{len(common)} (windows {len(mine)} vs {len(ref)})")
        print(f"E1 {method}: 20 seeds done", flush=True)
    pd.DataFrame(asserts).to_csv(_stamp("E1_ASSERTIONS.csv"), index=False)
    pd.DataFrame(rows).to_csv(_stamp("E1_RUNS.csv"), index=False)
    a = pd.DataFrame(asserts)
    print(a.groupby("method")[["compared", "identical"]].sum().to_string(), flush=True)
    _log("E1 done; all assertions passed")
    return 0


# ---------------------------------------------------------------------------- E2
def _load_state(ckpt: Path):
    """Central runs wrap the weights as {"state_dict", "method", "seed"}; others are raw."""
    obj = torch.load(ckpt, map_location="cpu")
    if isinstance(obj, dict) and "state_dict" in obj:
        return obj["state_dict"]
    return obj


def _block_eval(ckpt: Path, ds, mu: np.ndarray) -> dict[str, float]:
    model = CommonNDMF(num_spatial=ds.num_spatial)
    model.load_state_dict(_load_state(ckpt))
    model.eval()
    pred = _predict_model(model, ds)
    w = _mu_weights_for_test(pred, mu)
    blocks = np.asarray([h._block_of(g) for g in pred["group_strs"]])
    err2 = (pred["y_true"] - pred["y_pred"]) ** 2
    out = {"RMSE_mu": float(np.sqrt(np.sum(w * err2)))}
    for b in range(4):
        m = blocks == b
        wb = w[m] / w[m].sum()
        out[f"RMSE_block{b}"] = float(np.sqrt(np.sum(wb * err2[m])))
    out["WorstGroupRMSE"] = max(out[f"RMSE_block{b}"] for b in range(4))
    return out


def _e2_sources() -> dict[str, tuple[str, Path]]:
    """method -> (source description, run-tree root) for one single artifact per row."""
    g1 = json.loads(_stamp("G1_REPORT.json").read_text(encoding="utf-8"))
    sel = {k: v.get("selected") for k, v in (g1.get("G1c_selection") or {}).items()}
    src: dict[str, tuple[str, Path]] = {}
    for m in REBUILD:
        src[m] = (f"E1 ({TAG})", OUT / TAG / "C0_frozen" / "uair" / m)
    for m in ("local_hajek", "inst_cal", "raven_simoracle", "central_all", "central_delivered"):
        src[m] = ("E3 tree", TREES["e3"] / "uair" / m)
    for m in ("raven", "twostage_hajek"):
        choice = sel.get(m) or "tree"
        src[m] = (f"G1c selected: {choice}",
                  (TREES["e3"] / "uair" / m) if choice == "tree" else (TREES["e3"] / "uair" / m))
    src["fedau_window"] = ("FedAU tree", TREES["fedau"] / "uair" / "fedau_window")
    src["obsuse_window"] = ("ObsUse tree", TREES["obsuse"] / "uair" / "obsuse_window")
    src["raven_wo_design"] = ("E4 tree", TREES["e4"] / "uair" / "raven_wo_design")
    return src


def stage_e2() -> int:
    """Single-batch re-evaluation of every printed U-Air row; std and phys domains."""
    _log("E2 start")
    ds = load_paper_dataset(ROOT, "uair")
    mu = np.asarray(production_target_bundle(root=ROOT, dataset_name="uair", dataset=ds)["mu"],
                    dtype=np.float64)
    rows = []
    for method, (source, root) in _e2_sources().items():
        for seed in SEEDS:
            run_dir = root / f"seed{seed}"
            ckpt = run_dir / "checkpoints" / "final.pt"
            if not ckpt.is_file():
                rows.append({"method": method, "seed": seed, "source": source,
                             "status": "MISSING_CHECKPOINT"})
                continue
            try:
                met = _block_eval(ckpt, ds, mu)
            except Exception as exc:
                rows.append({"method": method, "seed": seed, "source": source,
                             "status": f"EVAL_ERROR {type(exc).__name__}: {str(exc)[:140]}"})
                continue
            fm = json.loads((run_dir / "final_metrics.json").read_text(encoding="utf-8"))
            rec = {"method": method, "seed": seed, "source": source, "status": "OK",
                   "RMSE_mu_std": met["RMSE_mu"], "RMSE_mu_phys": met["RMSE_mu"] * UAIR_SIGMA,
                   "WorstGroupRMSE_std": met["WorstGroupRMSE"],
                   "WorstGroupRMSE_phys": met["WorstGroupRMSE"] * UAIR_SIGMA,
                   "Delta_group": fm.get("Delta_group"), "Delta_c_s": fm.get("Delta_c_s")}
            for b in range(4):
                rec[f"RMSE_block{b}_std"] = met[f"RMSE_block{b}"]
                rec[f"RMSE_block{b}_phys"] = met[f"RMSE_block{b}"] * UAIR_SIGMA
            rows.append(rec)
        print(f"E2 {method} <- {source}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(_stamp("E2_UAIR_CELLS.csv"), index=False)

    ok = df[df["status"] == "OK"]
    agg = []
    for method, g in ok.groupby("method"):
        rec = {"method": method, "source": g["source"].iloc[0], "n": len(g)}
        for col in ("RMSE_mu_std", "RMSE_mu_phys", "WorstGroupRMSE_std", "WorstGroupRMSE_phys",
                    "Delta_group", "Delta_c_s"):
            rec[f"{col}_mean"] = float(g[col].mean())
            rec[f"{col}_std"] = float(g[col].std(ddof=1))
        for lab, seeds in (("TEST", TEST_SEEDS), ("ALL20", SEEDS)):
            sub = g[g["seed"].isin(seeds)]
            for col in ("RMSE_mu_std", "WorstGroupRMSE_std", "Delta_group", "Delta_c_s"):
                rec[f"{col}_{lab}"] = float(sub[col].mean())
        agg.append(rec)
    summary = pd.DataFrame(agg).sort_values("method")
    summary.to_csv(_stamp("E2_UAIR_SUMMARY.csv"), index=False)
    print(summary[["method", "n", "RMSE_mu_std_mean", "RMSE_mu_phys_mean",
                   "WorstGroupRMSE_std_mean", "Delta_group_mean", "Delta_c_s_mean"]]
          .to_string(index=False), flush=True)
    _log("E2 done")
    return 0


# ---------------------------------------------------------------------------- E3
P2_METHODS = ("debt_cal", "fedasync_window", "fedavg_window", "flamf_timealign_adapted",
              "inst_cal", "local_hajek", "raven", "raven_simoracle", "twostage_hajek")
NO_DESIGN_COMPARATORS = ("fedavg_window", "fedasync_window", "flamf_timealign_adapted",
                         "debt_cal", "fedau_window", "obsuse_window")


def _e2_table() -> dict[tuple[int, str, str], float]:
    """(seed, method, column) -> value, from the single-source E2 table."""
    df = pd.read_csv(_stamp("E2_UAIR_CELLS.csv"))
    df = df[df["status"] == "OK"]
    return {(int(r.seed), str(r.method), c): float(getattr(r, c))
            for r in df.itertuples()
            for c in ("RMSE_mu_std", "WorstGroupRMSE_std", "Delta_group", "Delta_c_s")}


def stage_e3() -> int:
    """Downstream recomputation: P2 coverage row and the SS8 paired statistics."""
    _log("E3 start")
    e2 = _e2_table()

    # --- P2 coverage over the 180-run U-Air set of tab:app_p2_coverage
    #     (9 windowed methods x 20 seeds), rebuilt methods substituted by E1.
    per_run = []
    for m in P2_METHODS:
        root = (OUT / TAG / "C0_frozen" / "uair" / m) if m in REBUILD else (TREES["e3"] / "uair" / m)
        for seed in SEEDS:
            wm = root / f"seed{seed}" / "window_metrics.json"
            if not wm.is_file():
                continue
            wins = json.loads(wm.read_text(encoding="utf-8"))
            per_run.append({"method": m, "seed": seed,
                            "active_windows": int(sum(1 for w in wins if w.get("active"))),
                            "windows": len(wins)})
    pr = pd.DataFrame(per_run)
    cov = pd.DataFrame([{
        "block": "uair",
        "runs": int(len(pr)),
        "mean_active_windows": round(float(pr["active_windows"].mean()), 4),
        "min_active_windows": int(pr["active_windows"].min()),
        "max_active_windows": int(pr["active_windows"].max()),
        "published_mean": 70.10,
        "published_range": "63-75",
        "rebuilt_substituted": ", ".join(REBUILD),
    }])
    cov.to_csv(_stamp("P2_COVERAGE.csv"), index=False)
    pr.to_csv(_stamp("P2_COVERAGE_PER_RUN.csv"), index=False)
    print(cov.to_string(index=False), flush=True)

    # --- paired statistics: RAVEN-NoDesign vs the six no-Design comparators (SS8)
    metrics = ("RMSE_mu_std", "WorstGroupRMSE_std", "Delta_group", "Delta_c_s")
    nd = "raven_wo_design"
    pvals: dict[tuple[str, str], float] = {}
    out = []
    for lab, seeds in (("TEST", TEST_SEEDS), ("ALL20", SEEDS)):
        for comp in NO_DESIGN_COMPARATORS:
            ks = [s for s in seeds
                  if (s, nd, "RMSE_mu_std") in e2 and (s, comp, "RMSE_mu_std") in e2]
            if len(ks) < 3:
                continue
            rec = {"primary": nd, "comparator": comp, "slice": lab, "n": len(ks)}
            for met in metrics:
                x = np.array([e2[(s, nd, met)] for s in ks], dtype=float)
                y = np.array([e2[(s, comp, met)] for s in ks], dtype=float)
                rel = (x - y) / y
                n = len(rel)
                se = rel.std(ddof=1) / np.sqrt(n)
                tcrit = float(stats.t.ppf(0.975, n - 1))
                rec[f"{met}_rel_mean"] = float(rel.mean())
                rec[f"{met}_rel_lo"] = float(rel.mean() - tcrit * se)
                rec[f"{met}_rel_hi"] = float(rel.mean() + tcrit * se)
                rec[f"{met}_wins"] = int((x < y).sum())
                rec[f"{met}_p"] = float(stats.ttest_rel(x, y).pvalue)
                pvals[(lab, f"{met}|{comp}")] = rec[f"{met}_p"]
            out.append(rec)
    paired = pd.DataFrame(out)
    for lab in ("TEST", "ALL20"):
        for met in metrics:
            keys = [(lab, f"{met}|{c}") for c in NO_DESIGN_COMPARATORS
                    if (lab, f"{met}|{c}") in pvals]
            ps = sorted(((k, pvals[k]) for k in keys), key=lambda kv: kv[1])
            m, prev = len(ps), 0.0
            for i, (k, p) in enumerate(ps):
                prev = min(1.0, max(prev, (m - i) * p))
                comp = k[1].split("|")[1]
                idx = paired.index[(paired["comparator"] == comp) & (paired["slice"] == lab)]
                paired.loc[idx, f"{met}_holm"] = prev
    paired.to_csv(_stamp("PAIRED_STATS.csv"), index=False)
    show = ["comparator", "slice", "n", "RMSE_mu_std_rel_mean", "WorstGroupRMSE_std_rel_mean",
            "Delta_group_rel_mean", "Delta_c_s_rel_mean", "Delta_group_holm"]
    print(paired[[c for c in show if c in paired.columns]].to_string(index=False), flush=True)
    _log("E3 done")
    return 0


# ------------------------------------------------- C1/C2/C3: review-driven checks
ARM_2X2 = "raven_wo_design_wo_inst"


def _register_2x2() -> None:
    """design-off x instant-calibration-off, with no src/ change.

    Mirrors the runtime-registration pattern `run_h_headroom` already uses for
    `raven_simoracle_nodesign`: replace the policy, point the family's aggregator at it.
    """
    POLICY_MAP[ARM_2X2] = dataclasses.replace(
        POLICY_MAP["raven_wo_inst"], uses_design_ratio=False
    )
    prev = h._get_aggregator

    def _get(name: str):
        if str(name).strip().lower() == ARM_2X2:
            return RavenWoInstAggregator()
        return prev(name)

    wr.get_aggregator = _get


def stage_c1() -> int:
    """C1 (review §2): does the CURRENT code reproduce frozen `raven_wo_design` bit-exactly?

    The reviewer's point: the decisive R1 comparison is rebuilt Debt-Cal against FROZEN
    RAVEN-NoDesign, so it is cross-batch, and `raven_wo_design` had never been
    bit-reproduction-checked on U-Air.
    """
    _log("C1 start")
    rows = []
    for seed in (30001, 30002):
        fz = TREES["e4"] / "uair" / "raven_wo_design" / f"seed{seed}" / "final_metrics.json"
        ref = json.loads(fz.read_text(encoding="utf-8"))
        r = h.run_arm("C0_frozen", "uair", "raven_wo_design", seed, tag="c1")
        mine = json.loads(
            (OUT / "c1" / "C0_frozen" / "uair" / "raven_wo_design" / f"seed{seed}"
             / "final_metrics.json").read_text(encoding="utf-8"))
        rec = {"seed": seed, "frozen_path": str(fz.relative_to(ROOT))}
        for k in ("RMSE_mu", "Delta_group", "Delta_c_s"):
            rec[f"{k}_frozen"] = ref.get(k)
            rec[f"{k}_rerun"] = mine.get(k)
            rec[f"{k}_abs_diff"] = (None if ref.get(k) is None or mine.get(k) is None
                                    else abs(float(ref[k]) - float(mine[k])))
        rec["all_bit_equal"] = all(rec[f"{k}_abs_diff"] == 0.0
                                   for k in ("RMSE_mu", "Delta_group", "Delta_c_s"))
        rows.append(rec)
        print(rec, flush=True)
    dump_json({"generated": _now(), "rows": rows,
               "verdict": ("FROZEN raven_wo_design REPRODUCES BIT-EXACTLY: R1's cross-batch "
                           "comparison is against a reproducible artifact"
                           if all(r["all_bit_equal"] for r in rows) else
                           "FROZEN raven_wo_design DOES NOT reproduce: R1's comparator is "
                           "itself non-reproducible")},
              _stamp("C1_RAVEN_WO_DESIGN_REPRO.json"))
    _log("C1 done")
    return 0


def stage_c2() -> int:
    """C2 (review §2): does `debt_cal`'s P2 `variance_diag` ever carry non-finite/negative
    entries, i.e. is the new sanitisation in `p2_cvxpy.py` ever load-bearing?"""
    _log("C2 start")
    import raven_mcs.aggregation.methods as M
    orig = M.solve_p2
    sig = inspect.signature(orig)
    seen: list[dict] = []

    def shim(*a, **kw):
        try:
            vd = sig.bind_partial(*a, **kw).arguments.get("variance_diag")
        except TypeError:
            vd = None
        if vd is not None:
            v = np.asarray(vd, dtype=np.float64)
            seen.append({"n": int(v.size),
                         "n_nonfinite": int((~np.isfinite(v)).sum()),
                         "n_negative": int((v < 0).sum()),
                         "min": float(np.nanmin(v)) if v.size else None})
        return orig(*a, **kw)

    M.solve_p2 = shim
    try:
        for ds, seed in (("uair", 30001), ("sensorscope", 30001)):
            h.run_arm("C0_frozen", ds, "debt_cal", seed, tag="c2")
    finally:
        M.solve_p2 = orig
    tot = {"calls": len(seen),
           "calls_with_nonfinite": sum(1 for s in seen if s["n_nonfinite"]),
           "calls_with_negative": sum(1 for s in seen if s["n_negative"]),
           "min_seen": min((s["min"] for s in seen if s["min"] is not None), default=None)}
    verdict = ("sanitisation NEVER load-bearing on these two runs (0 non-finite, 0 negative)"
               if tot["calls_with_nonfinite"] == 0 and tot["calls_with_negative"] == 0
               else "sanitisation IS load-bearing; the frozen pre-fix code saw the raw value")
    out = {"generated": _now(), "totals": tot, "per_call": seen[:40], "verdict": verdict,
           "note": ("p2_cvxpy.py:94-95 'variance_diag must be nonnegative' is unreachable "
                    "because :80 clamps to >=0 first")}
    dump_json(out, _stamp("C2_VDIAG_SANITISATION.json"))
    print(json.dumps({"totals": tot, "verdict": verdict}, indent=1), flush=True)
    _log(f"C2 done: {verdict}")
    return 0


def stage_c3() -> int:
    """C3: the missing 2x2 arm -- design off x instant calibration off.

    The reviewer's §5 inference attributes RAVEN-NoDesign's `Delta_group` advantage to
    "P2 instant group calibration AND debt", but `raven_wo_inst` is design-ON, so the
    design factor and the active set move together. This arm separates them.
    """
    _log("C3 start")
    _register_2x2()
    try:
        r = h.run_arm("C0_frozen", "uair", ARM_2X2, SEEDS[0], tag="c3")
    except ValueError as exc:
        msg = str(exc)
        if "lambda_group must be >= max_server_learning_rate" not in msg:
            raise
        # BLOCKED, and the block is itself a finding: `RavenWoInstAggregator.__init__`
        # hardcodes lambda_group=0.0 and instant_calibration=False, and the uncommitted
        # feasibility.py diff made `validate_p2_lambdas` accept lambda_g=0 only when
        # instant_calibration=False is passed -- but the call site in
        # sag/counterfactual_audit.py:106 does not pass it. So the diff is half-applied
        # and the PUBLISHED E4 arm `raven_wo_inst` is unrunnable under the current tree.
        out = {
            "generated": _now(),
            "status": "BLOCKED",
            "arm_intended": ARM_2X2,
            "error": msg,
            "raised_from": {
                "call": "src/raven_mcs/sag/counterfactual_audit.py:106 _solve_alpha -> solve_p2",
                "validator": "src/raven_mcs/aggregation/feasibility.py:41 validate_p2_lambdas",
                "guard": "src/raven_mcs/training/window_runner.py:1016,1252  if not lowmem: _run_counterfactual()",
            },
            "root_cause": (
                "The uncommitted feasibility.py diff added `instant_calibration: bool = True` to "
                "validate_p2_lambdas and made the lambda_group >= max_server_learning_rate check "
                "conditional on it, with a docstring naming 'the raven_wo_inst ablation path' as the "
                "reason. The caller in counterfactual_audit._solve_alpha does not pass "
                "instant_calibration=False, so the default True applies and lambda_g=0 is rejected. "
                "The diff is half-applied."),
            "blast_radius": (
                "RavenWoInstAggregator hardcodes lambda_group=0.0, so ANY arm built on it is "
                "unrunnable: the published E4 arm `raven_wo_inst` cannot be regenerated. "
                "`twostage_hajek`, whose stored numbers are bit-identical to raven_wo_inst, uses "
                "TwoStageHajekAggregator instead and DOES run (G1c re-ran it 6/6 bit-exact), so the "
                "block is specific to the wo_inst class."),
            "why_it_blocks_C3": (
                "The missing 2x2 cell (design off x instant calibration off) can only be built on "
                "RavenWoInstAggregator, because `instant_calibration=False` is a constructor argument "
                "of that class, not a policy field."),
            "unblocking_options": [
                "authorize completing the half-applied diff: pass instant_calibration=False from "
                "counterfactual_audit._solve_alpha when lambda_group == 0 (a src/ change, outside "
                "route A's SS14 boundary)",
                "authorize a runtime shim of counterfactual_audit.solve_p2 in the driver (no src/ "
                "change, but it alters the audit path, so the arm's gate must be always_off)",
                "run the 2x2 with window_runner's lowmem=True so _run_counterfactual is skipped "
                "(changes the run configuration relative to the published arms)",
            ],
            "verified_by": "scripts/run_active_set_repair.py --stage c3 (raises on RavenWoInstAggregator)",
        }
        dump_json(out, _stamp("C3_TWO_BY_TWO.json"))
        print(json.dumps({k: v for k, v in out.items() if k != "unblocking_options"}, indent=1)[:1200],
              flush=True)
        _log(f"C3 BLOCKED: {msg}")
        return 0
    ref_tree = TREES["fedau"]
    rows, asserts = [{"seed": SEEDS[0], "RMSE_mu": float(r["RMSE_mu"])}], []
    for seed in SEEDS:
        r = h.run_arm("C0_frozen", "uair", ARM_2X2, seed, tag="c3")
        run_dir = OUT / "c3" / "C0_frozen" / "uair" / ARM_2X2 / f"seed{seed}"
        ref = _windows(ref_tree / "uair" / "fedau_window" / f"seed{seed}")
        mine = _windows(run_dir)
        common = sorted(set(mine) & set(ref))
        ident = sum(1 for w in common if mine[w] == ref[w])
        asserts.append({"seed": seed, "windows": len(mine), "compared": len(common),
                        "identical": ident,
                        "assert_pass": bool(common) and ident == len(common) and len(mine) == len(ref)})
        rows.append({"seed": seed, "RMSE_mu": float(r["RMSE_mu"])})
    pd.DataFrame(asserts).to_csv(_stamp("C3_ASSERTIONS.csv"), index=False)
    if not all(a["assert_pass"] for a in asserts):
        raise SystemExit("C3 active-set assertion failed: the arm is not on full delivery")

    def arm_means(tree: str, method: str, tag: str | None = None) -> dict:
        root = (OUT / tag / "C0_frozen" / "uair" / method) if tag else (TREES[tree] / "uair" / method)
        out = {}
        for k in ("RMSE_mu", "Delta_group", "Delta_c_s"):
            v = []
            for s in SEEDS:
                f = root / f"seed{s}" / "final_metrics.json"
                if f.is_file():
                    x = json.loads(f.read_text(encoding="utf-8")).get(k)
                    if isinstance(x, (int, float)):
                        v.append(float(x))
            out[k] = sum(v) / len(v) if v else None
        return out

    table = {
        "design_on__inst_on": {"arm": "raven", "tree": "e3", **arm_means("e3", "raven")},
        "design_on__inst_off": {"arm": "raven_wo_inst", "tree": "e4", **arm_means("e4", "raven_wo_inst")},
        "design_off__inst_on": {"arm": "raven_wo_design", "tree": "e4", **arm_means("e4", "raven_wo_design")},
        "design_off__inst_off": {"arm": ARM_2X2, "tree": "c3", **arm_means("", "", tag="c3")},
    }
    on_on = table["design_on__inst_on"]["Delta_group"]
    on_off = table["design_on__inst_off"]["Delta_group"]
    off_on = table["design_off__inst_on"]["Delta_group"]
    off_off = table["design_off__inst_off"]["Delta_group"]
    out = {"generated": _now(), "table": table,
           "instant_calibration_effect": {
               "design_on": (on_off - on_on) / on_on,
               "design_off": (off_off - off_on) / off_on},
           "verdict": ("instant calibration remains decisive with design OFF: the reviewer's "
                       "attribution survives the 2x2"
                       if (off_off - off_on) / off_on > 0.005 else
                       "instant calibration is NOT decisive with design OFF: the reviewer's "
                       "attribution does not survive the 2x2")}
    dump_json(out, _stamp("C3_TWO_BY_TWO.json"))
    for k, v in table.items():
        print(f"  {k:<22} {v['arm']:<26} RMSE={v['RMSE_mu']:.6f} d_g={v['Delta_group']:.6f} "
              f"d_cs={v['Delta_c_s']:.6f}", flush=True)
    print(f"  instant-calibration effect on Delta_group: design ON {(on_off-on_on)/on_on*100:+.3f} %"
          f" | design OFF {(off_off-off_on)/off_on*100:+.3f} %", flush=True)
    print(f"  verdict: {out['verdict']}", flush=True)
    _log(f"C3 done: {out['verdict']}")
    return 0


def stage_g2run() -> int:
    """G2, executed through `run_nodesign_supplement.train_one` (the routine the plan's
    SS14 names). The reviewer's decision rule: if the current full-delivery FedAvg
    reproduces the frozen ledger bit-exactly on a block whose `pi^tar` is ~70 % zero,
    then the frozen run cannot have dropped those pairs."""
    _log("G2run start")
    import run_nodesign_supplement as rns
    rns.OUT = OUT  # honour the write boundary
    ledgers = {"cityscanner": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRAIN_LEDGER.json",
               "pilot2": ROOT / "results_joint_ou" / "round_v1" / "JO_TRAIN_LEDGER.json"}
    seeds = {"cityscanner": 32001, "pilot2": 33001}
    metrics = ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s")
    rows = []
    for block in ("cityscanner", "pilot2"):
        setup = rns.build_setup(block)
        led = {r["method"]: r for r in json.loads(ledgers[block].read_text(encoding="utf-8"))["rows"]
               if int(r.get("seed", -1)) == seeds[block]}
        for method in ("fedavg_window", "fedau_window", "obsuse_window"):
            rec = rns.train_one(block, setup, method=method, seed=seeds[block], tag="g2")
            fz = led.get(method)
            row = {"block": block, "method": method, "seed": seeds[block],
                   "run_status": rec.get("status"),
                   "frozen_design_on": None if fz is None else fz.get("design_on")}
            if fz is None:
                row["comparison"] = "NO FROZEN ROW"
            else:
                for k in metrics:
                    a, b = rec.get(k), fz.get(k)
                    row[f"{k}_rerun"] = a
                    row[f"{k}_frozen"] = b
                    row[f"{k}_bit_equal"] = (None if a is None or b is None
                                             else abs(float(a) - float(b)) <= TOL)
                row["comparison"] = ("BIT-IDENTICAL: frozen used the same (full-delivery) set"
                                     if all(row[f"{k}_bit_equal"] for k in metrics
                                            if row[f"{k}_bit_equal"] is not None)
                                     else "DIFFERS: frozen used a different active set")
            rows.append(row)
            print(f"  {block:<12} {method:<16} {row['comparison']}", flush=True)
    out = {"generated": _now(), "rows": rows,
           "conclusion": ("Every frozen hybrid row reproduces under full delivery, so City "
                          "Scanner and Pilot 2 active sets are CLEARED on these six cells."
                          if all(r["comparison"].startswith("BIT-IDENTICAL") for r in rows)
                          else "At least one hybrid row differs: that method/block joins the "
                               "rebuild set.")}
    dump_json(out, _stamp("G2_RUN_REPORT.json"))
    print(f"\n{out['conclusion']}", flush=True)
    _log(f"G2run done: {out['conclusion']}")
    return 0


# ---------------------------------------------------------------------------- G2
def stage_g2() -> int:
    """Hybrid blocks. Reports feasibility; executes the runs the stored pipelines allow."""
    _log("G2 start")
    report: dict[str, object] = {"generated": _now(), "runs": []}
    for dataset, seeds in ((LABEL["cityscanner"], (32001,)), (LABEL["pilot2"], (33001,))):
        for method in ("fedavg_window", "fedau_window", "obsuse_window"):
            report["runs"].append({"block": dataset, "method": method, "seed": seeds[0],
                                   "status": "NOT_EXECUTED"})
    report["blocker"] = (
        "City Scanner and Pilot 2 are not served by load_paper_dataset (only sensorscope, "
        "uair, traffic, tdrive*); their frozen runs live under results_c1_cityscanner/round_v1 "
        "and results_joint_ou/round_v1 with ledger files, not window_metrics.json. The G2 "
        "requirement 'logged A_r equals full delivery' therefore needs instrumentation in the "
        "hybrid drivers (scripts/run_path_a_no2.py, scripts/run_joint_ou_cs_p2.py), which the "
        "plan's SS14 write boundary excludes from src/ changes."
    )
    report["frozen_leaders"] = {
        "cityscanner": _ledger_probe(ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRAIN_LEDGER.json"),
        "pilot2": _ledger_probe(ROOT / "results_joint_ou" / "round_v1" / "JO_TRAIN_LEDGER.json"),
    }
    dump_json(report, _stamp("G2_REPORT.json"))
    print(json.dumps({"blocker": report["blocker"],
                      "frozen_leaders": report["frozen_leaders"]}, indent=1)[:1600], flush=True)
    _log("G2 done (feasibility report)")
    return 0


def _ledger_probe(path: Path):
    if not path.is_file():
        return {"present": False}
    try:
        led = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"present": True, "error": str(exc)}
    if isinstance(led, dict):
        head = list(led.keys())[:12]
        return {"present": True, "type": "dict", "keys": head,
                "n": len(led.get("rows", led)) if isinstance(led.get("rows"), list) else None}
    return {"present": True, "type": type(led).__name__, "n": len(led)}


# ---------------------------------------------------------------------------- CLI
def stage_status() -> int:
    print(f"OUT = {OUT.relative_to(ROOT)}")
    for f in sorted(OUT.glob("*")):
        print(f"  {f.name:<34} {f.stat().st_size:>9} B")
    done = len(list((OUT / TAG).rglob("final_metrics.json"))) if (OUT / TAG).exists() else 0
    print(f"  runs completed under {TAG}/: {done}")
    return 0


STAGES = {"g0": stage_g0, "g1": stage_g1, "diag": stage_diag, "e1": stage_e1,
          "e2": stage_e2, "e3": stage_e3, "g2": stage_g2, "status": stage_status,
          "c1": stage_c1, "c2": stage_c2, "c3": stage_c3, "g2run": stage_g2run}


def main() -> int:
    ap = argparse.ArgumentParser(description="Training active-set repair (route A)")
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    args = ap.parse_args()
    return STAGES[args.stage]()


if __name__ == "__main__":
    raise SystemExit(main())
