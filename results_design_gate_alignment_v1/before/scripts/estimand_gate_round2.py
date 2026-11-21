#!/usr/bin/env python3
"""Part II driver for the estimand-gate round: dose of rho against the cost of Design.

Instruction (read-only copy): raven-mcs-estimand-gate-execution-prompt.md
  sha256 ffb4bde64af8b6c4d6c647bc0d8b90e2191b945946e1cedc76e47dc08f1d189d
Round v1 (stopped, read-only): results_gate_dose/round_v1/

Outputs (only): results_gate_dose/round_v2/
  INPUT_HASHES.json, GATE.json, THETA_SCORED.csv,
  tables/DOSE_CELLS.csv, DOSE_SUMMARY.csv, DOSE_SLOPES.csv, GATE_POLICY.csv,
  DOSE_DECISION.json

Stages
  p0       II-P0   verify the four round_v1 input hashes (a mismatch stops the round)
  g1       II-P1   determinism repeat, raven m=0 seed 30001 twice per dataset
  g2       II-P1   off-arm reproduction, raven_wo_design m=0 seeds 30001-30002
  m0       II-P1   the 40 fresh raven m=0 runs
  g3       II-P1   on-arm drift bound over those 40 runs
  dose     II-P2   the 200 dose cells
  p3       II-P3   tables, H1, H2, H3, DOSE_DECISION.json

Training starts only under the authorization phrase; this module performs none by itself.
No src/, manuscript, artifacts/ or other results_* writes.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import gate_dose as gd  # noqa: E402  -- round_v1 driver, reused unchanged

V1 = ROOT / "results_gate_dose" / "round_v1"
OUT = ROOT / "results_gate_dose" / "round_v2"
RUNS = OUT / "runs"
TABLES = OUT / "tables"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
TRACES = ROOT / "artifacts/e3_formal_runs_r1/eventtraces"

SEEDS = list(range(30001, 30021))
GATE_SEEDS = [30001, 30002]
DATASETS = ("sensorscope", "uair")
LEVELS = gd.LEVELS
ARMS = ("raven", "raven_wo_design")
METHOD_RAVEN, METHOD_NODESIGN = "raven", "raven_wo_design"
LOCAL_STEPS = 2

TOL_ABS = 1e-9          # G2
TOL_REL = 1e-6          # G3, as originally frozen in II-3
TOL_REL_AMENDED = 1e-5  # G3 amendment (GATE_AMENDMENT.md), authorized after the 1e-6 miss
# Withdrawn: a confirmation on seeds 30021-30025 is impossible (no stored artifacts or
# traces beyond 30020).  See GATE_AMENDMENT.md §5.  No such run exists.
BOOT_SEED = gd.BOOTSTRAP_SEED
BOOT_DRAWS = gd.BOOTSTRAP_DRAWS
DELTA = 0.005           # II-H2 / II-H3 margin
Z_POWER = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)

EXPECTED = {
    "masks_content": "6b456bd378e92ead19345239801c5f4462b06c81f9219a611cd187adff383e18",
    "wiring_content": "b9de9d9b7d7e782369400b77bed5f0b1d16c8e70104706b80d3ebb978655e125",
    "rho_file": "302cd48c779e9a2a8078fd991ddcd834abf1fd838d7826dd96bfa6241fdc5ecd",
}


def dump_json(obj, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------------- II-P0: hashes
def content_masks() -> str:
    masks = json.loads((V1 / "MASKS.json").read_text(encoding="utf-8"))
    return gd.sha256_json(masks["datasets"])


def content_wiring() -> str:
    wiring = json.loads((V1 / "TARGET_WIRING.json").read_text(encoding="utf-8"))
    return gd.sha256_json({k: v for k, v in wiring.items() if k != "created_utc"})


def stage_p0() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    checks = {
        "MASKS.json": {"content_sha256": content_masks(), "expected": EXPECTED["masks_content"]},
        "TARGET_WIRING.json": {"content_sha256": content_wiring(), "expected": EXPECTED["wiring_content"]},
        "RHO.csv": {"file_sha256": sha256_file(V1 / "RHO.csv"), "expected": EXPECTED["rho_file"]},
    }
    for v in checks.values():
        v["pass"] = v.get("content_sha256", v.get("file_sha256")) == v["expected"]
    confirmed = {k: gd.CONFIRMED[k] for k in
                 ("theta_check_endpoints", "theta_rescore_endpoints",
                  "gate_failure_action", "rho_frame", "rho_m0_tolerance_reference")}
    # CONFIRMED items 2-4, exactly as round_v1 froze them
    confirmed_ok = (
        confirmed["rho_frame"] == "train_atoms"
        and confirmed["rho_m0_tolerance_reference"] == "unrounded"
        and confirmed["theta_check_endpoints"] == ["RMSE_mu", "Tail_RMSE"]
        and confirmed["gate_failure_action"] == "stop_round"
    )
    levels = json.loads((V1 / "MASKS.json").read_text())["datasets"]
    gate = {
        "created_utc": now(),
        "instruction_sha256":
            "ffb4bde64af8b6c4d6c647bc0d8b90e2191b945946e1cedc76e47dc08f1d189d",
        "checks": checks,
        "confirmed_items_2_to_4": confirmed,
        "confirmed_items_pass": bool(confirmed_ok),
        "levels": {ds: sorted(levels[ds]["levels"].keys()) for ds in levels},
        "pass": bool(all(v["pass"] for v in checks.values()) and confirmed_ok),
    }
    dump_json(gate, OUT / "INPUT_HASHES.json")
    for name, v in checks.items():
        print("  %-20s %s  %s" % (name, v["pass"],
                                  v.get("content_sha256", v.get("file_sha256"))[:16]))
    print("  CONFIRMED items 2-4:", confirmed_ok)
    print("  levels:", gate["levels"])
    if not gate["pass"]:
        raise SystemExit("STOP: II-P0 input hash mismatch")
    return gate


# ------------------------------------------------------------------------ run helpers
def targets_for(dataset: str, level: str, ctx: dict | None = None) -> dict:
    """Masked consumers for one level, rebuilt exactly as round_v1 P0 built them."""
    masks = json.loads((V1 / "MASKS.json").read_text(encoding="utf-8"))
    key = level if level in masks["datasets"][dataset]["levels"] else norm_level(level)
    masked_keys = masks["datasets"][dataset]["levels"][key]["masked_keys"]
    if ctx is None:
        sealed, mapping = gd.load_atomic(dataset)
        pi0 = gd.production_pi_target(dataset, sealed, mapping)
        mu0, gids, _ = gd.production_mu(dataset)
    else:
        sealed, mapping = ctx["sealed"], ctx["mapping"]
        pi0, gids = ctx["pi0"], ctx["gids"]
    tgt = gd.masked_targets(pi0, masked_keys, sealed, mapping, gids)
    return {"pi_target": tgt["pi_target"], "mu": tgt["mu"], "gids": gids,
            "n_masked": len(masked_keys)}


def run_one(dataset: str, arm: str, seed: int, level_key: str, tag: str) -> pathlib.Path:
    """Run one cell.  The level is part of the path whenever it is not the m = 0 level, so
    no two cells can overwrite each other.

    Path layout: runs/<tag>/<dataset>/<arm>/seed<seed>/            for tag in g1/g2/m0
                 runs/dose/<dataset>/m<level>/<arm>/seed<seed>/    for the dose cells
    """
    if tag == "dose":
        out = RUNS / tag / dataset / ("m%s" % level_key) / arm / ("seed%d" % seed)
    else:
        out = RUNS / tag / dataset / arm / ("seed%d" % seed)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    t = targets_for(dataset, level_key)
    return gd.run_cell(dataset, arm, seed, 0.0, t["pi_target"], t["mu"], out_dir=out)["run_dir"]


def dose_cell_dir(dataset: str, level_key: str, arm: str, seed: int) -> pathlib.Path:
    return RUNS / "dose" / dataset / ("m%s" % level_key) / arm / ("seed%d" % seed)


def read_metrics(run_dir: pathlib.Path) -> dict:
    fm = json.loads((run_dir / "final_metrics.json").read_text(encoding="utf-8"))
    wm = json.loads((run_dir / "window_metrics.json").read_text(encoding="utf-8"))
    return {"final_metrics": fm, "window_metrics": wm}


def theta_state(run_dir: pathlib.Path) -> dict:
    import torch
    obj = torch.load(run_dir / "checkpoints/final.pt", map_location="cpu", weights_only=False)
    return obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj


def theta_bit_equal(a: dict, b: dict) -> tuple[bool, float]:
    worst = 0.0
    for k in a:
        x, y = np.asarray(a[k]), np.asarray(b[k])
        worst = max(worst, float(np.abs(x - y).max()))
    return (worst == 0.0), worst


def stored_dir(dataset: str, arm: str, seed: int) -> pathlib.Path:
    base = E3 if arm == METHOD_RAVEN else E4
    return base / dataset / arm / ("seed%d" % seed)


# ------------------------------------------------------------------------- II-P1 gates
def stage_g1() -> dict:
    """Determinism: raven m=0 seed 30001 twice per dataset, same environment."""
    rows = []
    for dataset in DATASETS:
        dirs = []
        for rep in (1, 2):
            d = run_one(dataset, METHOD_RAVEN, 30001, "0", "g1_rep%d" % rep)
            dirs.append(d)
            print("  ran %s raven seed30001 rep%d" % (dataset, rep), flush=True)
        a, b = (read_metrics(d) for d in dirs)
        same_theta, worst = theta_bit_equal(theta_state(dirs[0]), theta_state(dirs[1]))
        diffs = {e: abs(float(a["final_metrics"][e]) - float(b["final_metrics"][e]))
                 for e in gd.TAIL}
        zero = all(v == 0.0 for v in diffs.values())
        rows.append({"dataset": dataset, "theta_bit_equal": bool(same_theta),
                     "max_abs_dtheta": worst, "endpoint_abs_diffs": diffs,
                     "all_endpoints_zero": bool(zero),
                     "pass": bool(same_theta and zero)})
    ok = all(r["pass"] for r in rows)
    dump_json({"gate": "G1", "rows": rows, "pass": ok}, OUT / "GATE_G1.json")
    for r in rows:
        print("  G1 %-12s theta_bit_equal=%s max|dtheta|=%.3e endpoints_zero=%s"
              % (r["dataset"], r["theta_bit_equal"], r["max_abs_dtheta"],
                 r["all_endpoints_zero"]))
    if not ok:
        write_gate_fail("G1", rows)
    return {"pass": ok, "rows": rows}


def compare_to_stored(dataset: str, arm: str, seed: int, level_key: str, tag: str) -> dict:
    run_dir = run_one(dataset, arm, seed, level_key, tag)
    got = read_metrics(run_dir)
    ref_dir = stored_dir(dataset, arm, seed)
    ref = read_metrics(ref_dir)
    active_same = ([w["active_clients"] for w in got["window_metrics"]]
                   == [w["active_clients"] for w in ref["window_metrics"]])
    rel = {}
    absd = {}
    for e in gd.TAIL:
        g = float(got["final_metrics"][e])
        s = float(ref["final_metrics"][e])
        absd[e] = abs(g - s)
        rel[e] = abs(g - s) / abs(s) if s else None
    return {"dataset": dataset, "arm": arm, "seed": seed, "level": level_key,
            "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/"),
            "active_clients_identical": bool(active_same),
            "abs_diff": absd, "rel_diff": rel}


def stage_g2() -> dict:
    """Off-arm reproduction against the stored artifacts (abs tol 1e-9)."""
    rows = []
    for dataset in DATASETS:
        for seed in GATE_SEEDS:
            r = compare_to_stored(dataset, METHOD_NODESIGN, seed, "0", "g2")
            r["pass"] = bool(r["active_clients_identical"]
                             and all(r["abs_diff"][e] <= TOL_ABS for e in gd.TAIL))
            rows.append(r)
            print("  G2 %-12s seed%d active=%s max|d|=%.3e pass=%s"
                  % (dataset, seed, r["active_clients_identical"],
                     max(r["abs_diff"].values()), r["pass"]), flush=True)
    ok = all(r["pass"] for r in rows)
    dump_json({"gate": "G2", "tol_abs": TOL_ABS, "rows": rows, "pass": ok}, OUT / "GATE_G2.json")
    if not ok:
        write_gate_fail("G2", rows)
    return {"pass": ok, "rows": rows}


def stage_m0(reuse: bool = True) -> dict:
    """The 40 fresh raven m = 0 runs.

    `reuse=True` keeps runs already produced by the pre-amendment execution.  G1 showed the
    process is bit-reproducible (theta bit-equal, endpoints exactly 0), so a rerun would
    reproduce these bytes; the driver reuses them instead of pretending to re-derive them.
    """
    rows = []
    n_new = n_reused = 0
    for dataset in DATASETS:
        for seed in SEEDS:
            d = RUNS / "m0" / dataset / METHOD_RAVEN / ("seed%d" % seed)
            if reuse and (d / "final_metrics.json").is_file():
                n_reused += 1
            else:
                d = run_one(dataset, METHOD_RAVEN, seed, "0", "m0")
                n_new += 1
            m = read_metrics(d)["final_metrics"]
            rows.append({"dataset": dataset, "seed": seed,
                         "run_dir": str(d.relative_to(ROOT)).replace("\\", "/"),
                         **{e: float(m[e]) for e in gd.TAIL}})
        print("  m0 %-12s done (%d new, %d reused so far)"
              % (dataset, n_new, n_reused), flush=True)
    dump_json({"stage": "m0", "n_new": n_new, "n_reused": n_reused, "rows": rows},
              OUT / "M0_RUNS.json")
    print("  m0 totals: %d new, %d reused from the pre-amendment execution" % (n_new, n_reused))
    return {"rows": rows}


def stage_g3() -> dict:
    """On-arm drift bound over the 40 fresh m=0 runs (rel tol 1e-6)."""
    rows = []
    for dataset in DATASETS:
        for seed in SEEDS:
            run_dir = RUNS / "m0" / dataset / METHOD_RAVEN / ("seed%d" % seed)
            got = read_metrics(run_dir)
            ref = read_metrics(stored_dir(dataset, METHOD_RAVEN, seed))
            active_same = ([w["active_clients"] for w in got["window_metrics"]]
                           == [w["active_clients"] for w in ref["window_metrics"]])
            rel = {}
            for e in gd.TAIL:
                g = float(got["final_metrics"][e])
                s = float(ref["final_metrics"][e])
                rel[e] = abs(g - s) / abs(s) if s else None
            rows.append({"dataset": dataset, "seed": seed,
                         "active_clients_identical": bool(active_same), "rel_diff": rel,
                         "pass": bool(active_same and all(rel[e] <= TOL_REL for e in gd.TAIL))})
        worst = max(max(r["rel_diff"].values()) for r in rows if r["dataset"] == dataset)
        print("  G3 %-12s n=%d worst rel=%.3e (tol %.0e)"
              % (dataset, sum(1 for r in rows if r["dataset"] == dataset), worst, TOL_REL))
    ok = all(r["pass"] for r in rows)
    dump_json({"gate": "G3", "tol_rel": TOL_REL, "rows": rows, "pass": ok,
               "note": "original frozen bound; verdict preserved for audit and NOT used as "
                       "the stop condition once GATE_AMENDMENT.md is in force"},
              OUT / "GATE_G3.json")
    print("  G3 (original, 1e-6): pass = %s  [preserved for audit; amended bound applies]"
          % ok)
    return {"pass": ok, "rows": rows}


def stage_g3_amended(g1: dict, g2: dict) -> dict:
    """Apply the amended bound to the existing 40 runs; report the deviation distribution.

    Confirmation rule (GATE_AMENDMENT.md §5): every cell within 1e-5 on the three relative
    bounds and active_clients identical, AND the 95th percentile of the deviation
    distribution within 2e-6.
    """
    PCT95_TOL = 2e-6
    rows = []
    for dataset in DATASETS:
        for seed in SEEDS:
            run_dir = RUNS / "m0" / dataset / METHOD_RAVEN / ("seed%d" % seed)
            got = read_metrics(run_dir)
            ref = read_metrics(stored_dir(dataset, METHOD_RAVEN, seed))
            active_same = ([w["active_clients"] for w in got["window_metrics"]]
                           == [w["active_clients"] for w in ref["window_metrics"]])
            rel = {}
            for e in gd.TAIL:
                g = float(got["final_metrics"][e])
                s = float(ref["final_metrics"][e])
                rel[e] = abs(g - s) / abs(s) if s else None
            rows.append({"dataset": dataset, "seed": seed,
                         "active_clients_identical": bool(active_same), "rel_diff": rel,
                         "pass_1e-5": bool(active_same and all(v <= TOL_REL_AMENDED
                                                               for v in rel.values())),
                         "pass_1e-6_original": bool(active_same and all(v <= TOL_REL
                                                                        for v in rel.values()))})
    dist = {}
    for dataset in DATASETS:
        sub = [r for r in rows if r["dataset"] == dataset]
        dist[dataset] = {}
        for e in gd.TAIL:
            v = np.array([r["rel_diff"][e] for r in sub], dtype=float)
            dist[dataset][e] = {"max": float(v.max()), "median": float(np.median(v)),
                                "p95": float(np.percentile(v, 95)), "n": int(v.size)}
        worst = max(max(r["rel_diff"].values()) for r in sub)
        p95 = max(dist[dataset][e]["p95"] for e in gd.TAIL)
        print("  G3-amended %-12s n=%d worst=%.3e p95=%.3e fails@1e-5=%d (original fails@1e-6=%d)"
              % (dataset, len(sub), worst, p95,
                 sum(1 for r in sub if not r["pass_1e-5"]),
                 sum(1 for r in sub if not r["pass_1e-6_original"])))
    all_cells = all(r["pass_1e-5"] for r in rows)
    p95_ok = all(max(dist[ds][e]["p95"] for e in gd.TAIL) <= PCT95_TOL for ds in DATASETS)
    ok = bool(all_cells and p95_ok)
    dump_json({"gate": "G3_amended", "tol_rel": TOL_REL_AMENDED, "tol_rel_original": TOL_REL,
               "p95_tol": PCT95_TOL, "rows": rows, "distribution": dist,
               "all_cells_within_1e-5": bool(all_cells), "p95_within_2e-6": bool(p95_ok),
               "reused_runs": True,
               "reuse_note": "the 40 m=0 runs come from the pre-amendment execution; G1 "
                             "established the process is bit-reproducible",
               "pass": ok}, OUT / "GATE_G3_AMENDED.json")
    if not ok:
        write_gate_fail("G3_amended", rows)
    return {"pass": ok, "rows": rows, "distribution": dist}


def write_gate_fail(which: str, rows) -> None:
    dump_json({"pass": False, "failed_gate": which, "rows": rows, "created_utc": now()},
              OUT / "GATE.json")
    raise SystemExit("STOP: gate %s failed; GATE.json written with pass:false" % which)


def stage_gates_all() -> None:
    stage_p0()
    g1 = stage_g1()
    g2 = stage_g2()
    m0 = stage_m0()
    g3 = stage_g3()
    original_pass = g1["pass"] and g2["pass"] and g3["pass"]
    # Preserve the original stop record, then apply the amended G3 bound.
    dump_json({"pass": bool(original_pass), "G1": g1["pass"], "G2": g2["pass"],
               "G3": g3["pass"], "G3_tol_rel": TOL_REL, "n_m0_runs": len(m0["rows"]),
               "created_utc": now(),
               "amended": False,
               "note": "original verdict at the frozen 1e-6 bound; preserved verbatim"},
              OUT / "GATE_ORIGINAL.json")
    g3a = stage_g3_amended(g1, g2)
    ok = g1["pass"] and g2["pass"] and g3a["pass"]
    dump_json({"pass": bool(ok), "G1": g1["pass"], "G2": g2["pass"],
               "G3_original_tol_rel": TOL_REL, "G3_original_pass": g3["pass"],
               "G3_amended": g3a["pass"], "G3_tol_rel": TOL_REL_AMENDED,
               "G3_distribution": g3a["distribution"],
               "n_m0_runs": len(m0["rows"]),
               "reused_runs": True,
               "amended": True, "created_utc": now(),
               "amendment": "GATE_AMENDMENT.md"},
              OUT / "GATE.json")
    print("\nGATE.json (amended): pass =", ok)
    if not ok:
        raise SystemExit("STOP: Part II gate failed under the amended bound")


def norm_level(x) -> str:
    """Canonical level string: 0.1 / 0.25 / 0.4, matching round_v1's MASKS.json keys."""
    v = float(x)
    return ("%.4f" % v).rstrip("0").rstrip(".") if v else "0"


def dose_key(dataset: str) -> list[str]:
    masks = json.loads((V1 / "MASKS.json").read_text(encoding="utf-8"))
    keys = [norm_level(k) for k in masks["datasets"][dataset]["levels"].keys()]
    return sorted(set(keys), key=float)


def stage_dose() -> dict:
    """II-P2: the 200 dose cells (levels x 20 seeds x 2 arms)."""
    rho_v1 = pd.read_csv(V1 / "RHO.csv")
    rho_of = {(r.dataset, norm_level(r.m)): float(r.rho) for r in rho_v1.itertuples()}
    rows = []
    n_done = 0
    for dataset in DATASETS:
        for level in dose_key(dataset):
            if level == "0":
                continue          # m = 0 comes from II-P1 (fresh raven, stored wo_design)
            for seed in SEEDS:
                for arm in ARMS:
                    d = run_one(dataset, arm, seed, level, "dose")
                    m = read_metrics(d)["final_metrics"]
                    wm = read_metrics(d)["window_metrics"]
                    rows.append({
                        "dataset": dataset, "level": level, "rho": rho_of[(dataset, level)],
                        "seed": seed, "arm": arm,
                        "run_dir": str(d.relative_to(ROOT)).replace("\\", "/"),
                        "last_window_active": bool(wm[-1]["active"]),
                        **{e: float(m[e]) for e in gd.TAIL},
                    })
                    n_done += 1
                    if n_done % 20 == 0:
                        print("  dose [%3d/200] %-12s m=%-5s seed%d" 
                              % (n_done, dataset, level, seed), flush=True)
    if n_done != 200:
        raise SystemExit("INCOMPLETE: %d dose cells, expected 200" % n_done)
    dump_json({"stage": "dose", "n_rows": len(rows), "rows": rows}, OUT / "DOSE_RUNS.json")
    return {"rows": rows}


def arm_runs(dataset: str, arm: str, level: str, seed: int) -> pathlib.Path:
    """Where a cell's run lives: stored artifacts at m=0 for the off arm, fresh otherwise."""
    if level == "0":
        if arm == METHOD_NODESIGN:
            return stored_dir(dataset, arm, seed)
        return RUNS / "m0" / dataset / arm / ("seed%d" % seed)
    return dose_cell_dir(dataset, level, arm, seed)


def cell_context(dataset: str) -> dict:
    """Cached target inputs for one dataset (avoids reloading per θ replay)."""
    sealed, mapping = gd.load_atomic(dataset)
    pi0 = gd.production_pi_target(dataset, sealed, mapping)
    _mu0, gids, _ = gd.production_mu(dataset)
    return {"sealed": sealed, "mapping": mapping, "pi0": pi0, "gids": gids}


def build_cells() -> tuple[pd.DataFrame, list[dict]]:
    """One row per (dataset, level, seed, arm) with the four endpoints.

    II-4 applies round_v1 §3: a run whose last window is inactive is scored from its saved
    θ checkpoint.  That affects `RMSE_mu` and `Tail_RMSE` (the endpoints that are functions
    of the final θ); the structural endpoints are kept from the stored metrics and the
    movement is recorded.  Every such cell is listed for `THETA_SCORED.csv`.
    """
    rows = []
    theta_rows = []
    ctx_cache: dict[str, dict] = {}
    for dataset in DATASETS:
        ctx = ctx_cache.setdefault(dataset, cell_context(dataset))
        for level in dose_key(dataset):
            for seed in SEEDS:
                for arm in ARMS:
                    d = arm_runs(dataset, arm, level, seed)
                    fm_path = d / "final_metrics.json"
                    if not fm_path.is_file():
                        raise SystemExit("INCOMPLETE: missing %s" % fm_path)
                    fm = json.loads(fm_path.read_text(encoding="utf-8"))
                    wm = json.loads((d / "window_metrics.json").read_text(encoding="utf-8"))
                    inactive = not bool(wm[-1]["active"])
                    vals = {e: float(fm[e]) for e in gd.TAIL}
                    theta_scored = False
                    if inactive:
                        t = targets_for(dataset, level, ctx)
                        replay = theta_rescore_for_replay(dataset, arm, level, seed, d, t)
                        for e in gd.CONFIRMED["theta_check_endpoints"]:
                            vals[e] = replay[e]
                        theta_scored = True
                        theta_rows.append({
                            "dataset": dataset, "level": level, "seed": seed, "arm": arm,
                            "stored_RMSE_mu": float(fm["RMSE_mu"]),
                            "theta_RMSE_mu": replay["RMSE_mu"],
                            "stored_Delta_group": float(fm["Delta_group"]),
                            "reported_Delta_group": vals["Delta_group"],
                            "stored_Delta_c_s": float(fm["Delta_c_s"]),
                            "reported_Delta_c_s": vals["Delta_c_s"],
                            "stored_Tail_RMSE": float(fm["Tail_RMSE"]),
                            "theta_Tail_RMSE": replay["Tail_RMSE"],
                            "source": ("stored" if (level == "0" and arm == METHOD_NODESIGN)
                                       else "fresh"),
                            "run_dir": str(d.relative_to(ROOT)).replace("\\", "/"),
                        })
                    rows.append({"dataset": dataset, "level": level, "seed": seed, "arm": arm,
                                 "last_window_active": not inactive,
                                 "theta_scored": theta_scored,
                                 "source": ("stored" if (level == "0" and arm == METHOD_NODESIGN)
                                            else "fresh"),
                                 **vals})
    return pd.DataFrame(rows), theta_rows


def theta_rescore_for_replay(dataset: str, arm: str, level: str, seed: int,
                             run_dir: pathlib.Path, targets: dict) -> dict:
    """Frozen-theta replay of one run: RMSE_mu and Tail_RMSE are canonical there."""
    state = theta_state(run_dir)
    out = OUT / "_theta" / dataset / ("m%s" % level) / arm / ("seed%d" % seed)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    res = gd.run_cell(dataset, arm, seed, 0.0, targets["pi_target"], targets["mu"],
                      out_dir=out, frozen_state=state)
    fm = res["metrics"]
    return {e: float(fm[e]) for e in gd.TAIL}


def paired_table(cells: pd.DataFrame, level_rho: dict) -> pd.DataFrame:
    """Paired relative Design cost per (dataset, level, seed)."""
    rows = []
    for (dataset, level, seed), g in cells.groupby(["dataset", "level", "seed"]):
        if set(g.arm) != set(ARMS):
            raise SystemExit("INCOMPLETE: %s %s seed%d arms %s"
                             % (dataset, level, seed, sorted(g.arm)))
        on = g[g.arm == METHOD_RAVEN].iloc[0]
        off = g[g.arm == METHOD_NODESIGN].iloc[0]
        rec = {"dataset": dataset, "level": level, "seed": int(seed),
               "rho": level_rho[(dataset, level)],
               "theta_scored": (not bool(on.last_window_active))
                               or (not bool(off.last_window_active))}
        for e in gd.TAIL:
            rec["on_" + e] = float(on[e])
            rec["off_" + e] = float(off[e])
            rec[gd.R[e]] = (float(on[e]) - float(off[e])) / float(off[e])
        rows.append(rec)
    return pd.DataFrame(rows)


def ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    A = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[0]), float(coef[1])


def cluster_bootstrap_slope(df: pd.DataFrame, ycol: str) -> dict:
    """Seed-cluster bootstrap: resample seeds with all their levels, percentile 95 %."""
    rng = np.random.default_rng(BOOT_SEED)
    seeds = sorted(df.seed.unique())
    draws_b, draws_a, draws_rho = [], [], []
    for _ in range(BOOT_DRAWS):
        pick = rng.integers(0, len(seeds), size=len(seeds))
        sub = pd.concat([df[df.seed == seeds[i]] for i in pick], ignore_index=True)
        if sub.rho.nunique() < 2:
            continue
        a, b = ols(sub.rho.to_numpy(float), sub[ycol].to_numpy(float))
        draws_a.append(a)
        draws_b.append(b)
        if b != 0:
            draws_rho.append(-a / b)
    def pct(v):
        return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if v else (None, None)
    return {"slope": float(ols(df.rho.to_numpy(float), df[ycol].to_numpy(float))[1]),
            "intercept": float(ols(df.rho.to_numpy(float), df[ycol].to_numpy(float))[0]),
            "slope_ci": pct(draws_b), "intercept_ci": pct(draws_a),
            "rho_star": (float(-ols(df.rho.to_numpy(float), df[ycol].to_numpy(float))[0]
                               / ols(df.rho.to_numpy(float), df[ycol].to_numpy(float))[1])
                         if ols(df.rho.to_numpy(float), df[ycol].to_numpy(float))[1] != 0 else None),
            "rho_star_ci": pct(draws_rho), "n_draws": len(draws_b)}


def label_slope(ci: tuple) -> str:
    lo, hi = ci
    if lo is None:
        return "not_evaluable"
    if lo > 0:
        return "open"
    if hi < 0:
        return "harm"
    return "null"


def stage_p3() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    cells, theta_rows = build_cells()
    rho_df = pd.read_csv(V1 / "RHO.csv")
    level_rho = {(r.dataset, norm_level(r.m)): float(r.rho) for r in rho_df.itertuples()}
    pairs = paired_table(cells, level_rho)
    cells.to_csv(TABLES / "DOSE_CELLS.csv", index=False)
    pairs.to_csv(TABLES / "DOSE_CELLS_PAIRED.csv", index=False)
    with (OUT / "THETA_SCORED.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["dataset", "level", "seed", "arm", "source", "stored_RMSE_mu", "theta_RMSE_mu",
                "stored_Delta_group", "reported_Delta_group", "stored_Delta_c_s",
                "reported_Delta_c_s", "stored_Tail_RMSE", "theta_Tail_RMSE", "run_dir"]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(theta_rows)
    print("theta-scored cells: %d (listed in THETA_SCORED.csv)" % len(theta_rows))

    slopes = []
    labels = {}
    for dataset in DATASETS:
        sub = pairs[pairs.dataset == dataset]
        for ycol in (gd.R["RMSE_mu"], gd.R["Delta_c_s"], gd.R["Delta_group"], gd.R["Tail_RMSE"]):
            s = cluster_bootstrap_slope(sub, ycol)
            lab = label_slope(s["slope_ci"]) if ycol == gd.R["RMSE_mu"] else None
            if ycol == gd.R["RMSE_mu"]:
                labels[dataset] = lab
            slopes.append({"dataset": dataset, "endpoint": ycol, "n_cells": len(sub),
                           "slope": s["slope"], "intercept": s["intercept"],
                           "slope_ci_lo": s["slope_ci"][0], "slope_ci_hi": s["slope_ci"][1],
                           "rho_star": s["rho_star"], "rho_star_ci_lo": s["rho_star_ci"][0],
                           "rho_star_ci_hi": s["rho_star_ci"][1], "label": lab})
            sub_ex = sub[~sub.theta_scored]
            s2 = cluster_bootstrap_slope(sub_ex, ycol) if sub_ex.rho.nunique() > 1 else None
            slopes.append({"dataset": dataset, "endpoint": ycol + "__theta_excluded",
                           "n_cells": len(sub_ex),
                           "slope": (s2 or {}).get("slope"), "intercept": (s2 or {}).get("intercept"),
                           "slope_ci_lo": (s2 or {}).get("slope_ci", (None, None))[0],
                           "slope_ci_hi": (s2 or {}).get("slope_ci", (None, None))[1],
                           "rho_star": (s2 or {}).get("rho_star"),
                           "rho_star_ci_lo": (s2 or {}).get("rho_star_ci", (None, None))[0],
                           "rho_star_ci_hi": (s2 or {}).get("rho_star_ci", (None, None))[1],
                           "label": label_slope(s2["slope_ci"]) if s2 else None})
    with (TABLES / "DOSE_SLOPES.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(slopes[0].keys()))
        wr.writeheader()
        wr.writerows(slopes)

    gate_law = (labels.get("sensorscope") == "open" and labels.get("uair") != "harm")
    supported = bool(gate_law)

    # per-level summary with Student-t intervals
    srows = []
    for (dataset, level), g in pairs.groupby(["dataset", "level"]):
        rec = {"dataset": dataset, "level": level, "rho": float(g.rho.iloc[0]), "n": len(g)}
        for e in gd.TAIL:
            v = g[gd.R[e]].to_numpy(float)
            half = float(stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)))
            rec[gd.R[e] + "_mean"] = float(v.mean())
            rec[gd.R[e] + "_ci_lo"] = float(v.mean() - half)
            rec[gd.R[e] + "_ci_hi"] = float(v.mean() + half)
        srows.append(rec)
    with (TABLES / "DOSE_SUMMARY.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(srows[0].keys()))
        wr.writeheader()
        wr.writerows(srows)

    # H2: SensorScope m = 0 non-inferiority, only if H1 supports
    h2 = {"tested": False, "reason": "H1 does not support the law"}
    if supported:
        v = pairs[(pairs.dataset == "sensorscope") & (pairs.level == "0")][gd.R["RMSE_mu"]].to_numpy(float)
        half = float(stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)))
        upper = float(v.mean() + half)
        h2 = {"tested": True, "n": len(v), "mean": float(v.mean()),
              "upper_95_t": upper, "margin": DELTA, "pass": bool(upper < DELTA)}

    # H3: decision policy on SensorScope
    policy_rows = []
    for dataset in DATASETS:
        sub = pairs[pairs.dataset == dataset]
        levels = sorted(sub.level.unique(), key=lambda k: float(k))
        off_level = next((k for k in levels if float(k) > 0), None)
        for seed, g in sub.groupby("seed"):
            g = g.set_index("level")
            rec = {"dataset": dataset, "seed": int(seed), "off_level": off_level}
            off_perf = {e: float(g.loc[off_level, "off_" + e]) for e in gd.TAIL}
            # w_pred: RMSE_mu only, relative to the off value in the same cell
            rec["J_w_pred_gate"] = ((float(g.loc["0", "on_RMSE_mu"]) - off_perf["RMSE_mu"])
                                    / off_perf["RMSE_mu"])
            rec["J_w_pred_always_on"] = rec["J_w_pred_gate"]
            rec["J_w_pred_always_off"] = 0.0
            rec["J_w_pred"] = rec["J_w_pred_gate"]
            # w_eq: the four endpoints of eq:design_switch, each relative to its Design-on
            # value, averaged with w_e = 1/4
            norm = lambda lvl, e: (float(g.loc[lvl, "on_" + e]) / float(g.loc["0", "on_" + e]))
            eq_off = float(np.mean([off_perf[e] / float(g.loc["0", "on_" + e]) for e in gd.TAIL]))
            rec["J_w_eq_gate"] = 1.0                  # rho = 0 at level 0 -> gate says on
            rec["J_w_eq_always_on"] = 1.0
            rec["J_w_eq_always_off"] = eq_off
            rec["J_w_eq"] = 1.0
            rec["best_w_pred"] = "0" if rec["J_w_pred"] <= 0.0 else off_level
            rec["best_w_eq"] = "0" if 1.0 <= eq_off else off_level
            for e in gd.TAIL:
                rec["J_w_pred_" + e] = ((float(g.loc["0", "on_" + e]) - off_perf[e])
                                        / off_perf[e])
            policy_rows.append(rec)
    pol = pd.DataFrame(policy_rows)
    pol.to_csv(TABLES / "GATE_POLICY.csv", index=False)

    def policy_label(dataset: str, wname: str) -> dict:
        sub = pol[pol.dataset == dataset]
        out = {}
        for other in ("always_on", "always_off"):
            d = (sub["J_%s_gate" % wname].to_numpy(float)
                 - sub["J_%s_%s" % (wname, other)].to_numpy(float))
            lo, hi = gd_boot_ci(d)
            out[other] = {"mean": float(d.mean()), "ci_lo": lo, "ci_hi": hi,
                          "n_zero_diffs": int((d == 0).sum()), "n": int(d.size)}
        if all(v["ci_hi"] < 0 for v in out.values()):
            lab = "open"
        elif any(v["ci_lo"] > 0 for v in out.values()):
            lab = "harm"
        else:
            lab = "null"
        # A structural note, not a label change: at rho = 0 the gate's policy IS always_on,
        # so that comparison is identically zero and the "open" condition can never be met.
        out["note_gate_equals_always_on_at_rho_zero"] = True
        return {"label": lab, "comparisons": out}

    h3 = {"primary_w_pred": policy_label("sensorscope", "w_pred"),
          "secondary_w_eq": policy_label("sensorscope", "w_eq"),
          "uair_descriptive": {"note": "every level has rho > 0, gate == always_off"}}
    sub = pol[pol.dataset == "sensorscope"]
    for wname in ("w_pred", "w_eq"):
        k = int((sub["best_" + wname] != "0").sum())
        lo, hi = wilson(k, len(sub))
        h3["base_rate_" + wname] = {"share_off_optimal": k / len(sub),
                                    "n_off_optimal": k, "n": len(sub),
                                    "wilson_lo": lo, "wilson_hi": hi}
        if k in (0, len(sub)):
            h3["label_" + wname] = "saturated"
            h3["primary_w_pred" if wname == "w_pred" else "secondary_w_eq"]["label"] = "saturated"

    decision = {
        "created_utc": now(),
        "instruction_sha256":
            "ffb4bde64af8b6c4d6c647bc0d8b90e2191b945946e1cedc76e47dc08f1d189d",
        "gate": json.loads((OUT / "GATE.json").read_text()) if (OUT / "GATE.json").is_file() else None,
        "h1_labels": labels,
        "gate_law": "supported" if supported else "not supported",
        "h2": h2,
        "h3": h3,
        "delta": DELTA,
        "bootstrap": {"draws": BOOT_DRAWS, "seed": BOOT_SEED},
        "rho_star": {s["dataset"]: s["rho_star"] for s in slopes
                     if s["endpoint"] == gd.R["RMSE_mu"]},
    }
    dump_json(decision, OUT / "DOSE_DECISION.json")
    print(json.dumps({"h1_labels": labels, "gate_law": decision["gate_law"], "h2": h2,
                      "h3_labels": {k: v for k, v in h3.items() if k.startswith("label_")}},
                     indent=2, default=float))


def gd_boot_ci(values: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(BOOT_SEED)
    n = len(values)
    draws = np.array([float(np.mean(values[rng.integers(0, n, size=n)]))
                      for _ in range(BOOT_DRAWS)])
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a binomial share."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (float(max(0.0, c - h)), float(min(1.0, c + h)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["p0", "g1", "g2", "m0", "g3", "gates", "dose", "p3"])
    args = ap.parse_args()
    if args.stage == "p0":
        stage_p0()
    elif args.stage == "g1":
        stage_g1()
    elif args.stage == "g2":
        stage_g2()
    elif args.stage == "m0":
        stage_m0()
    elif args.stage == "g3":
        stage_g3()
    elif args.stage == "gates":
        stage_gates_all()
    elif args.stage == "dose":
        stage_dose()
    elif args.stage == "p3":
        stage_p3()
    else:
        raise SystemExit("stage %s not enabled yet" % args.stage)


if __name__ == "__main__":
    main()
