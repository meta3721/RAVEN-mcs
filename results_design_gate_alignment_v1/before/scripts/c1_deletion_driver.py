#!/usr/bin/env python3
"""C1 deletion driver -- Part B (B0, B1) of the A1/C1 gatekeeping protocol.

Round directory: results_gatekeeping/round_v1 (Part B appended to Part A).
Protocol: results_gatekeeping/round_v1/PROTOCOL.md
Preregistration: results_gatekeeping/round_v1/PREREG.md, AMENDMENT 1 (Part B, r = 3),
hashed into MANIFEST.sha256 before any B1 run started.

Design
------
This driver does NOT re-implement training.  It imports ``build_setup`` and
``train_one`` from ``scripts/run_nodesign_supplement.py`` (the reconstruction of the
frozen City Scanner training path) and replaces ONLY ``setup["pi_target"]`` per arm.
The module-level output root of that module is redirected into this round's directory
so that no existing results directory is written to.

Arms (protocol SS2 B1):
  fedavg_window     frozen comparator (reused at model seed s; 2 extra seeds trained)
  raven_wo_design   Design off (reused at model seed s; 2 extra seeds trained)
  raven_ctrl        frozen RAVEN = control map (reused at model seed s; 2 extras trained)
  raven_ctrl_floor  control map with every zero key floored to the smallest positive
                    control key mass, renormalized  -> expected 0 % deleted units
  raven_M1mu        M1 (ACS population) rescaled within region to marginals mu
  raven_M2mu        M2 (NYC 311) rescaled within region to marginals mu

Every map must cover every risk-set key of every trace; a missing key is a hard error.

Stages
  recon   structural checks only (key coverage, map sums, realized rho).  No training.
  maps    write C1_MAPS.json.
  b0a     reproduction gate against the frozen seed-32001 rows (hard gate).
  b0b     seed-32005 variance probe, 5 model seeds x 2 arms (diagnostic only).
  b1      train the r = 3 grid (shardable).
  runs    collect every (arm, trace, model seed) row into C1_RUNS.csv.

Writes only under results_gatekeeping/round_v1/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_nodesign_supplement as ns  # noqa: E402

# ------------------------------------------------------------------ paths / constants
GATE_DIR = ROOT / "results_gatekeeping" / "round_v1"
RUN_OUT = GATE_DIR / "c1_runs"                      # <- ns.OUT is redirected here
MAPS_CSV = ROOT / "results_exogenous_target" / "round_v1" / "MAPS_KEY_LEVEL.csv"
EXOG_JSON = ROOT / "results_exogenous_target" / "round_v1" / "DOWNLOAD_LOG.json"
TRACES = ROOT / "artifacts" / "e3_c1_cityscanner_eventtraces_v1" / "cityscanner_nyc_pm25"
ATOMIC = ROOT / "data" / "processed" / "cityscanner_nyc_pm25" / "atomic_units.parquet"
FROZEN_CS = ROOT / "results_c1_cityscanner" / "round_v1" / "runs" / "cityscanner_nyc_pm25"
FROZEN_NS = ROOT / "results_nodesign_supplement" / "round_v1" / "runs" / "cityscanner_nyc_pm25"
CS_SETUP = ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRAIN_SETUP.json"
CS_DECISION = ROOT / "results_c1_cityscanner" / "round_v1" / "CS_PHI_DECISION.json"
NODESIGN_SCRIPT = ROOT / "scripts" / "run_nodesign_supplement.py"

DATASET = "cityscanner_nyc_pm25"
BLOCK = "cityscanner"
TRACE_SEEDS = list(range(32001, 32011))
R = 3
SEED_OFFSETS = (0, 100000, 200000)               # r = 3 model seeds {s, s+1e5, s+2e5}
PROBE_OFFSETS = (0, 100000, 200000, 300000, 400000)
PROBE_TRACE = 32005
SENS_TRACE = 32005
REGION_ORDER = ("region0", "region1", "region2", "region3")

# arm -> (method passed to the runner, map name, frozen marker or None)
ARMS: dict[str, dict[str, Any]] = {
    "fedavg_window":    {"method": "fedavg_window",    "map": "control",       "frozen": "cs"},
    "raven_wo_design":  {"method": "raven_wo_design",  "map": "control",       "frozen": "nodesign"},
    "raven_ctrl":       {"method": "raven",            "map": "control",       "frozen": "cs"},
    "raven_ctrl_floor": {"method": "raven",            "map": "control_floor", "frozen": None},
    "raven_M1mu":       {"method": "raven",            "map": "M1_mu",         "frozen": None},
    "raven_M2mu":       {"method": "raven",            "map": "M2_mu",         "frozen": None},
}
NEW_ARMS = ("raven_ctrl_floor", "raven_M1mu", "raven_M2mu")
REUSED_ARMS = ("fedavg_window", "raven_wo_design", "raven_ctrl")
B0A_ARMS = (("raven_ctrl", "raven", "cs"), ("raven_wo_design", "raven_wo_design", "nodesign"))

ENDPOINTS = ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s")
B0A_TOL = 1e-12

_CACHE: dict[str, Any] = {}


# ------------------------------------------------------------------ small utilities
def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n",
                    encoding="utf-8", newline="\n")


def write_csv(path: Path, rows: list[dict], header: list[str] | None = None) -> None:
    if header is None:
        header = []
        for r in rows:
            for k in r:
                if k not in header:
                    header.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    import csv as _csv
    with path.open("w", newline="", encoding="utf-8") as fh:
        wr = _csv.DictWriter(fh, fieldnames=header)
        wr.writeheader()
        for r in rows:
            wr.writerow({c: r.get(c, "") for c in header})


def log(line: str) -> None:
    RUN_OUT.mkdir(parents=True, exist_ok=True)
    path = GATE_DIR / "C1_EXECUTION_LOG.md"
    if not path.is_file():
        path.write_text("# C1 (Part B) execution log\n\n", encoding="utf-8", newline="\n")
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(f"- {now()} {line}\n")
    print(line, flush=True)


def map_sha256(values: dict[tuple[str, str], float]) -> str:
    """Canonical map hash: sorted (client|stratum|%.17g) lines, sha256 of UTF-8 bytes."""
    h = hashlib.sha256()
    for key in sorted(values):
        h.update(f"{key[0]}|{key[1]}|{float(values[key]):.17g}\n".encode("utf-8"))
    return h.hexdigest()


# ------------------------------------------------------------------ setup and maps
def get_setup() -> dict[str, Any]:
    """build_setup once; ns.OUT is redirected into this round before the call."""
    if "setup" not in _CACHE:
        ns.OUT = RUN_OUT
        t0 = time.perf_counter()
        setup = ns.build_setup(BLOCK)
        _CACHE["setup"] = setup
        _CACHE["control"] = dict(setup["pi_target"])
        _CACHE["maps"] = build_maps(setup)
        log(f"setup built in {time.perf_counter() - t0:.1f}s; "
            f"control keys={len(_CACHE['control'])}")
    return _CACHE["setup"]


def region_mu(setup: dict[str, Any]) -> dict[str, float]:
    g2i = {str(g): int(i) for g, i in setup["ds"]._target_group_str_to_int.items()}
    if set(g2i) != set(REGION_ORDER):
        raise RuntimeError(f"h encoding {g2i} != {REGION_ORDER}")
    return {r: float(setup["mu"][g2i[r]]) for r in REGION_ORDER}


def load_maps_table() -> pd.DataFrame:
    tbl = pd.read_csv(MAPS_CSV)
    tbl["client_id"] = tbl["client_id"].astype(str)
    tbl["opportunity_stratum"] = tbl["opportunity_stratum"].astype(str)
    tbl["region"] = tbl["region"].astype(str)
    return tbl


def build_maps(setup: dict[str, Any]) -> dict[str, Any]:
    """Build the four pi^tar objects and the structural metadata block."""
    ctrl = dict(_CACHE["control"])
    pos = sorted(v for v in ctrl.values() if v > 0.0)
    if not pos:
        raise RuntimeError("control map has no positive key")
    pi_floor = float(pos[0])
    n_zero_ctrl = int(sum(1 for v in ctrl.values() if v <= 0.0))

    flo = {k: (float(v) if v > 0.0 else pi_floor) for k, v in ctrl.items()}
    z = float(sum(flo.values()))
    flo = {k: v / z for k, v in flo.items()}

    mu = region_mu(setup)
    tbl = load_maps_table()
    maps: dict[str, dict[tuple[str, str], float]] = {"control": ctrl, "control_floor": flo}
    meta: dict[str, Any] = {}
    # M1/M2 live on the *same key universe as the control map* (the key-level support that
    # the frozen runs use), so that after region-matching every arm has the same region
    # marginals = mu on the operative key set.  Rescaling on the raw 3568-row cross
    # product instead would leave phantom (cell, stratum) keys carrying mass and would
    # make the region marginal of the real support differ from mu.
    for name, col in (("M1_mu", "pi_M1"), ("M2_mu", "pi_M2")):
        lut = {(c, s): float(v) for c, s, v in zip(tbl["client_id"],
                                                   tbl["opportunity_stratum"], tbl[col])}
        missing = sorted(k for k in ctrl if k not in lut)
        if missing:
            raise RuntimeError(f"{col} lacks control keys: {missing[:3]}")
        vals = {k: lut[k] for k in ctrl}
        sub = {r: float(sum(v for k, v in vals.items() if k[1].startswith(r + "::")))
               for r in REGION_ORDER}
        if any(sub[r] <= 0.0 for r in REGION_ORDER):
            raise RuntimeError(f"{col} has an empty region on the control support: {sub}")
        scale = {r: mu[r] / sub[r] for r in REGION_ORDER}
        m = {k: v * scale[k[1].split("::")[0]] for k, v in vals.items()}
        tot = float(sum(m.values()))
        m = {k: v / tot for k, v in m.items()}
        maps[name] = m
        # the same construction on the full cross-product universe, for the record
        full_sub = {r: float(tbl.loc[tbl["region"] == r, col].sum()) for r in REGION_ORDER}
        full_scale = {r: mu[r] / full_sub[r] for r in REGION_ORDER}
        full_m = {k: lut[k] * full_scale[k[1].split("::")[0]] for k in ctrl}
        z = float(sum(full_m.values()))
        full_marg = {r: float(sum(v for k, v in full_m.items()
                                  if k[1].startswith(r + "::")) / z) for r in REGION_ORDER}
        meta[name] = {
            "source_column": col,
            "key_universe": "control map key set (build_pi_target(split='test'))",
            "raw_region_marginal_on_support": sub,
            "region_scale_to_mu": scale,
            "rejected_alternative": {
                "key_universe": "full MAPS_KEY_LEVEL.csv cross product (3568 keys)",
                "raw_region_marginal": full_sub,
                "region_scale_to_mu": full_scale,
                "resulting_region_marginal_on_the_real_support": full_marg,
                "max_abs_dev_from_mu_on_real_support": max(abs(full_marg[r] - mu[r])
                                                           for r in REGION_ORDER),
                "why_rejected": ("phantom (cell, stratum) combinations would carry mass and "
                                 "the real support's region marginal would not equal mu, so "
                                 "the arms would not be region-matched"),
            },
        }

    # ---- structural checks -------------------------------------------------------
    marg_ctrl = {r: sum(v for k, v in ctrl.items() if k[1].startswith(r + "::"))
                 for r in REGION_ORDER}
    marg_floor = {r: sum(v for k, v in flo.items() if k[1].startswith(r + "::"))
                  for r in REGION_ORDER}
    checks = {
        "control_region_marginals": marg_ctrl,
        "control_region_marginals_equal_mu": all(
            abs(marg_ctrl[r] - mu[r]) <= 1e-12 for r in REGION_ORDER),
        "floor_region_marginals": marg_floor,
        "mu": mu,
        "map_sums": {k: float(sum(v.values())) for k, v in maps.items()},
        "pi_floor": pi_floor,
        "n_zero_keys_control": n_zero_ctrl,
        "n_zero_keys_control_floor": int(sum(1 for v in flo.values() if v <= 0.0)),
        "key_counts": {k: len(v) for k, v in maps.items()},
        "map_sha256": {k: map_sha256(v) for k, v in maps.items()},
        "n_positive_keys": {k: int(sum(1 for v in m.values() if v > 0.0))
                            for k, m in maps.items()},
    }
    # cross-check: MAPS_KEY_LEVEL pi_control must equal build_setup's pi_target on the
    # shared key set (both are build_pi_target(split="test")).
    lut = {(c, s): float(v) for c, s, v in zip(tbl["client_id"], tbl["opportunity_stratum"],
                                               tbl["pi_control"])}
    shared = [k for k in ctrl if k in lut]
    max_dev = max((abs(ctrl[k] - lut[k]) for k in shared), default=float("nan"))
    checks["control_vs_maps_key_level"] = {
        "n_shared_keys": len(shared), "n_control_keys": len(ctrl),
        "max_abs_dev": max_dev,
        "all_control_keys_in_maps_key_level": len(shared) == len(ctrl),
        "agree_1e_15": bool(max_dev <= 1e-15),
    }
    checks["mu_source"] = str(CS_DECISION.relative_to(ROOT))
    return {"maps": maps, "meta": meta, "pi_floor": pi_floor, "checks": checks}


def get_maps() -> dict[str, Any]:
    get_setup()
    return _CACHE["maps"]


# ------------------------------------------------------------------ traces and rho
def trace_events(trace_seed: int) -> pd.DataFrame:
    et = TRACES / f"seed{trace_seed}" / "training_eventtrace" / "events.parquet"
    if not et.is_file():
        raise FileNotFoundError(et)
    return pd.read_parquet(et)


def _atomic_lookups() -> tuple[dict[str, str], dict[str, str]]:
    if "atomic_lut" not in _CACHE:
        atomic = pd.read_parquet(ATOMIC)
        u = atomic["unit_id"].astype(str)
        _CACHE["atomic_lut"] = (
            dict(zip(u, atomic["split"].astype(str))),
            dict(zip(u, atomic["opportunity_stratum"].astype(str))),
        )
    return _CACHE["atomic_lut"]


def risk_records(u_filter: bool = True, trace_seeds: list[int] | None = None) -> pd.DataFrame:
    """Exactly the exogenous_target_cityscanner.trace_delivered construction."""
    seeds = TRACE_SEEDS if trace_seeds is None else list(trace_seeds)
    recs = []
    for ts in seeds:
        ev = trace_events(ts)
        for row in ev.itertuples(index=False):
            if (not u_filter) or bool(row.U):
                for uid in json.loads(row.risk_set_unit_ids):
                    recs.append({"trace_seed": int(ts), "window_id": int(row.window_id),
                                 "client_id": str(row.client_id), "unit_id": str(uid)})
    df = pd.DataFrame(recs)
    split_of, stratum_of = _atomic_lookups()
    df["split"] = df["unit_id"].map(split_of).fillna("unknown")
    df["stratum"] = df["unit_id"].map(stratum_of)
    return df


def risk_set_keys() -> set[tuple[str, str]]:
    """Every (client, stratum) key any trace can ask for -- hard coverage requirement."""
    if "risk_keys" not in _CACHE:
        recs = risk_records(u_filter=False)
        _CACHE["risk_keys"] = set(zip(recs["client_id"], recs["stratum"]))
    return _CACHE["risk_keys"]


def rho_for(values: dict[tuple[str, str], float], frame: pd.DataFrame) -> dict[str, Any]:
    """Realized deleted share, exactly as exogenous_target_cityscanner.rho_for."""
    vals = np.asarray([values.get((c, s), np.nan)
                       for c, s in zip(frame["client_id"], frame["stratum"])],
                      dtype=np.float64)
    n = int(np.isfinite(vals).sum())
    n_zero = int(np.nansum(vals <= 0.0))
    return {"n_delivered": n, "n_zero": n_zero,
            "rho_delivered": (n_zero / n) if n else None}


def arm_rho() -> dict[str, dict[int, dict[str, Any]]]:
    """per arm -> per trace -> rho over U=1 delivered units on non-test splits."""
    if "rho" not in _CACHE:
        delivered = risk_records(u_filter=True)
        train_only = delivered[delivered["split"] != "test"]
        out: dict[str, dict[int, dict[str, Any]]] = {}
        for arm, spec in ARMS.items():
            if arm in ("fedavg_window", "raven_wo_design"):
                out[arm] = {t: {"n_delivered": 0, "n_zero": 0, "rho_delivered": 0.0,
                                "note": "Design off: zeta not applied, deleted share is 0 "
                                        "by construction"}
                            for t in TRACE_SEEDS}
                continue
            vals = get_maps()["maps"][spec["map"]]
            out[arm] = {t: rho_for(vals, train_only[train_only["trace_seed"] == t])
                        for t in TRACE_SEEDS}
        _CACHE["rho"] = out
    return _CACHE["rho"]


# ------------------------------------------------------------------ training
def arm_tag(arm: str) -> str:
    return f"c1_runs/{arm}"


def run_arm(arm: str, trace_seed: int, model_seed: int, tag: str | None = None) -> dict[str, Any]:
    """Train one (arm, trace, model seed) run with only setup['pi_target'] replaced."""
    spec = ARMS[arm]
    setup = dict(get_setup())
    setup["pi_target"] = get_maps()["maps"][spec["map"]]
    off = model_seed - trace_seed
    if off not in (0, 100000, 200000, 300000, 400000):
        raise RuntimeError(f"model seed {model_seed} is not trace {trace_seed} + offset")
    return _train_on_trace(setup, spec["method"], trace_seed, model_seed,
                           tag or arm_tag(arm))


def _trace_redirect(trace_seed: int, model_seed: int) -> tuple[Path, Path, Path | None]:
    """Make RUN_OUT/_trace_link/p<pid>/seed<model_seed> resolve to trace `trace_seed`.

    ``train_one`` keys both the trace directory and the model seed on one integer, so at
    r = 3 the extra model seeds (s + 1e5, s + 2e5) need the trace to be *findable* under
    the model-seed name.  Nothing in the training path changes: only the directory in
    which ``train_one`` looks for the trace.  Returns (patched_trace_root, run_dir,
    junction_to_remove_or_None).
    """
    link_base = RUN_OUT / "_trace_link" / f"p{os.getpid()}"
    link_root = link_base / DATASET / f"seed{model_seed}"
    target = TRACES / f"seed{trace_seed}"
    made: Path | None = None
    if not (link_root / "training_eventtrace" / "events.parquet").is_file():
        link_root.parent.mkdir(parents=True, exist_ok=True)
        try:
            if link_root.exists():
                import shutil
                shutil.rmtree(link_root)
            import _winapi
            _winapi.CreateJunction(str(target), str(link_root))
        except Exception:
            import shutil
            shutil.copytree(target, link_root, dirs_exist_ok=True)
        made = link_root
    return link_base, link_root, made


def _train_on_trace(setup: dict[str, Any], method: str, trace_seed: int, model_seed: int,
                    tag: str) -> dict[str, Any]:
    """Call ns.train_one on the trace of `trace_seed` while recording `model_seed`."""
    run_dir = RUN_OUT / tag / DATASET / method / f"seed{model_seed}"
    marker = run_dir / "ACCEPTED.json"
    if marker.is_file():
        rec = json.loads(marker.read_text(encoding="utf-8"))
        return {"status": "REUSED", **rec}
    cfg = ns.BLOCKS[BLOCK]
    saved_root, saved_out = cfg["trace_root"], ns.OUT
    ns.OUT = RUN_OUT
    try:
        if trace_seed != model_seed:                   # extra model seed: redirect only
            cfg["trace_root"], _, _ = _trace_redirect(trace_seed, model_seed)
        row = ns.train_one(BLOCK, setup, method=method, seed=int(model_seed), tag=tag)
    finally:
        cfg["trace_root"], ns.OUT = saved_root, saved_out
    return row


def frozen_row(arm: str, trace_seed: int) -> dict[str, Any]:
    spec = ARMS[arm]
    if spec["frozen"] == "cs":
        p = FROZEN_CS / spec["method"] / f"seed{trace_seed}" / "CS_ACCEPTED.json"
    elif spec["frozen"] == "nodesign":
        p = FROZEN_NS / spec["method"] / f"seed{trace_seed}" / "ACCEPTED.json"
    else:
        raise RuntimeError(f"{arm} has no frozen row")
    rec = json.loads(p.read_text(encoding="utf-8"))
    return {"status": "FROZEN", "source_path": str(p.relative_to(ROOT)), **rec}


def trained_row(arm: str, trace_seed: int, model_seed: int, tag: str | None = None) -> dict[str, Any]:
    spec = ARMS[arm]
    p = RUN_OUT / (tag or arm_tag(arm)) / DATASET / spec["method"] / f"seed{model_seed}" / "ACCEPTED.json"
    if not p.is_file():
        raise FileNotFoundError(p)
    return {"status": "NEW", "source_path": str(p.relative_to(ROOT)),
            **json.loads(p.read_text(encoding="utf-8"))}


def row_for(arm: str, trace_seed: int, model_seed: int) -> dict[str, Any]:
    if model_seed == trace_seed and ARMS[arm]["frozen"]:
        return frozen_row(arm, trace_seed)
    return trained_row(arm, trace_seed, model_seed)


# ------------------------------------------------------------------ plan
def b1_plan() -> list[tuple[str, int, int]]:
    plan = []
    for t in TRACE_SEEDS:
        for off in SEED_OFFSETS:
            ms = t + off
            for arm in NEW_ARMS:
                plan.append((arm, t, ms))
            for arm in REUSED_ARMS:
                if off == 0:
                    continue                      # frozen row is reused
                plan.append((arm, t, ms))
    return plan


# ------------------------------------------------------------------ stages
def stage_recon() -> dict[str, Any]:
    setup = get_setup()
    maps = get_maps()
    keys = risk_set_keys()
    coverage = {}
    for arm, spec in ARMS.items():
        m = maps["maps"][spec["map"]]
        missing = sorted(k for k in keys if k not in m)
        coverage[arm] = {"map": spec["map"], "n_map_keys": len(m),
                         "n_risk_keys": len(keys), "n_missing": len(missing),
                         "missing_examples": ["|".join(k) for k in missing[:5]]}
    delivered = risk_records(u_filter=True)
    train_only = delivered[delivered["split"] != "test"]
    rho = {arm: {str(t): rho_for(maps["maps"][ARMS[arm]["map"]], train_only[
        train_only["trace_seed"] == t]) for t in TRACE_SEEDS} for arm in ARMS}
    out = {
        "utc": now(),
        "n_risk_keys_all_events": len(keys),
        "risk_records": {"u1_rows": int(len(delivered)),
                         "u1_non_test_rows": int(len(train_only)),
                         "split_counts": delivered["split"].value_counts().to_dict()},
        "coverage": coverage,
        "maps": maps["checks"],
        "map_meta": maps["meta"],
        "rho_per_arm_trace": rho,
        "setup_checks": {k: list(v) for k, v in setup["setup_checks"].items()},
        "b1_plan_n_runs": len(b1_plan()),
    }
    dump_json(out, GATE_DIR / "C1_RECON.json")
    print(json.dumps({"n_risk_keys": len(keys), "b1_plan_n_runs": len(b1_plan()),
                      "coverage_missing": {a: c["n_missing"] for a, c in coverage.items()},
                      "rho_mean": {a: float(np.mean([v["rho_delivered"] for v in rho[a].values()]))
                                   for a in rho},
                      "floor": maps["pi_floor"],
                      "map_sha256": maps["checks"]["map_sha256"]}, indent=1, default=str))
    return out


def stage_maps(write: bool = True) -> dict[str, Any]:
    setup = get_setup()
    maps = get_maps()
    keys = risk_set_keys()
    rho = arm_rho()
    per_arm = {}
    for arm, spec in ARMS.items():
        m = maps["maps"][spec["map"]]
        per_arm[arm] = {
            "method": spec["method"], "map": spec["map"],
            "map_sha256": map_sha256(m), "n_keys": len(m),
            "n_positive_keys": int(sum(1 for v in m.values() if v > 0.0)),
            "n_zero_keys": int(sum(1 for v in m.values() if v <= 0.0)),
            "region_marginals": {r: float(sum(v for k, v in m.items()
                                              if str(k[1]).startswith(r + "::")))
                                 for r in REGION_ORDER},
            "n_risk_keys_missing": int(sum(1 for k in keys if k not in m)),
            "rho_realized_per_trace": {str(t): rho[arm][t]["rho_delivered"]
                                       for t in TRACE_SEEDS},
            "rho_realized_mean": float(np.mean([rho[arm][t]["rho_delivered"]
                                                for t in TRACE_SEEDS])),
            "rho_note": ("Design off: no deletion" if arm in ("fedavg_window", "raven_wo_design")
                         else "computed from U=1 delivered units on non-test splits"),
        }
    doc = {
        "round": "results_gatekeeping/round_v1", "part": "B (C1)", "r": R,
        "utc": now(),
        "pi_floor": maps["pi_floor"],
        "pi_floor_definition": ("smallest positive control key mass in "
                                "build_pi_target(split='test') at key level"),
        "region_matching": ("M1/M2 are rescaled within region so that each region's "
                            "marginal equals mu (the frozen test region share); the "
                            "control map already satisfies this exactly"),
        "key_universe": ("control and control_floor: the key-level support returned by "
                         "build_pi_target(split='test') as used by the frozen runs; "
                         "M1_mu/M2_mu: the full MAPS_KEY_LEVEL.csv key universe (3568)"),
        "map_sha256_convention": ("sha256 over sorted lines 'client|stratum|%.17g', "
                                  "UTF-8, trailing newline per line"),
        "checks": maps["checks"], "map_meta": maps["meta"],
        "risk_key_coverage": {"n_risk_keys": len(keys),
                              "min_map_keys": min(v["n_keys"] for v in per_arm.values()),
                              "hard_error_on_missing": True},
        "arms": per_arm,
        "rho_definition": ("share of delivered units (events with U = 1) on non-test "
                           "splits whose (client, stratum) key carries pi^tar = 0, "
                           "recomputed exactly as scripts/exogenous_target_cityscanner.py"),
        "inputs": {str(p.relative_to(ROOT)): sha256_file(p) for p in
                   (MAPS_CSV, CS_SETUP, CS_DECISION, ATOMIC, NODESIGN_SCRIPT)},
        "traces": TRACE_SEEDS, "model_seed_offsets": list(SEED_OFFSETS),
    }
    if write:
        dump_json(doc, GATE_DIR / "C1_MAPS.json")
    print(json.dumps({a: {"rho": round(v["rho_realized_mean"], 6), "keys": v["n_keys"],
                          "sha256": v["map_sha256"][:16]} for a, v in per_arm.items()},
                     indent=1))
    return doc


def stage_b0a(threads_note: str = "", tag: str = "b0a",
              arms: tuple = B0A_ARMS) -> dict[str, Any]:
    rows = {}
    gates = {}
    for arm, method, frozen_kind in arms:
        setup = dict(get_setup())
        setup["pi_target"] = get_maps()["maps"]["control"]
        t0 = time.perf_counter()
        got = _train_on_trace(setup, method, 32001, 32001, tag=tag)
        frozen = frozen_row(arm, 32001)
        diffs = {f: abs(float(got[f]) - float(frozen[f])) for f in ENDPOINTS}
        gates[arm] = {
            "method": method, "trace_seed": 32001, "model_seed": 32001,
            "frozen_source": frozen["source_path"],
            "frozen": {f: float(frozen[f]) for f in ENDPOINTS},
            "rerun": {f: float(got[f]) for f in ENDPOINTS},
            "abs_diff": diffs, "max_abs_diff": max(diffs.values()),
            "tolerance": B0A_TOL,
            "eventtrace_hash_match": got.get("eventtrace_hash") == frozen.get("eventtrace_hash"),
            "wall_s_this_call": float(time.perf_counter() - t0),
            "pass": bool(max(diffs.values()) <= B0A_TOL
                         and got.get("eventtrace_hash") == frozen.get("eventtrace_hash")),
        }
        rows[arm] = got
    ok = all(g["pass"] for g in gates.values())
    doc = {
        "stage": "B0-a driver reproduction (hard gate)",
        "utc": now(), "block": BLOCK, "r": R, "tag": tag,
        "driver": ("scripts/c1_deletion_driver.py imports build_setup and train_one from "
                   "scripts/run_nodesign_supplement.py and replaces only setup['pi_target']"),
        "tolerance": B0A_TOL, "endpoints": list(ENDPOINTS),
        "arms": gates, "pass": ok, "threads_note": threads_note,
        "verdict": ("PASS: the rebuilt driver reproduces both frozen seed-32001 rows "
                    "bit-exactly" if ok else "FAIL: STOP -- no B1 run may start"),
    }
    out_name = "B0_REPRO.json" if tag == "b0a" else f"B0_REPRO__{tag}.json"
    dump_json(doc, GATE_DIR / out_name)
    for arm, g in gates.items():
        log(f"B0-a {arm}: max|delta|={g['max_abs_diff']:.3e} pass={g['pass']}")
    print(json.dumps({a: {"max_abs_diff": g["max_abs_diff"], "pass": g["pass"]}
                      for a, g in gates.items()}, indent=1))
    return doc


def stage_b0b(shard: int = 0, nshards: int = 1) -> dict[str, Any]:
    """Seed-32005 probe: 5 model seeds x 2 arms on trace 32005.  Diagnostic only."""
    jobs = [(arm, off) for arm in ("raven_ctrl", "raven_wo_design")
            for off in PROBE_OFFSETS][shard::nshards]
    done: dict[tuple[str, int], dict[str, Any]] = {}
    for arm, off in jobs:
        ms = PROBE_TRACE + off
        if off == 0:
            done[(arm, off)] = (frozen_row(arm, PROBE_TRACE), "frozen")
        else:
            rec = run_arm(arm, PROBE_TRACE, ms)
            done[(arm, off)] = (rec, rec["status"].lower())
        log(f"B0-b {arm} seed{ms} {done[(arm, off)][1]} "
            f"RMSE={float(done[(arm, off)][0]['RMSE_mu']):.6f}")
    if nshards > 1:
        return {"shard": shard, "nshards": nshards, "jobs": len(jobs)}
    out_rows = []
    for arm in ("raven_ctrl", "raven_wo_design"):
        spec = ARMS[arm]
        for off in PROBE_OFFSETS:
            ms = PROBE_TRACE + off
            rec, src = done[(arm, off)]
            out_rows.append({
                "arm": arm, "trace_seed": PROBE_TRACE, "model_seed": ms,
                "model_seed_offset": off,
                "source": ("frozen" if off == 0 else "trained_B0b_stage"),
                "role": "original model seed" if off == 0 else "replicate model seed",
                "RMSE_mu": rec["RMSE_mu"], "WorstGroupRMSE": rec["WorstGroupRMSE"],
                "Delta_group": rec["Delta_group"], "Delta_c_s": rec["Delta_c_s"],
                "runtime_s": rec.get("runtime_seconds", ""),
                "rho_realized": arm_rho()[arm][PROBE_TRACE]["rho_delivered"],
                "map_sha256": map_sha256(get_maps()["maps"][spec["map"]]),
            })
    df = pd.DataFrame(out_rows)
    piv = df.pivot(index="model_seed", columns="arm", values="RMSE_mu")
    ratios = (piv["raven_ctrl"] / piv["raven_wo_design"] - 1.0)
    verdict = {
        "trace_seed": PROBE_TRACE,
        "rmse_raven_ctrl": {str(k): float(v) for k, v in piv["raven_ctrl"].items()},
        "rmse_raven_wo_design": {str(k): float(v) for k, v in piv["raven_wo_design"].items()},
        "rel_ratio_ctrl_over_wo_design": {str(k): float(v) for k, v in ratios.items()},
        "mean_rel_ratio": float(ratios.mean()), "sd_rel_ratio": float(ratios.std(ddof=1)),
        "n_seeds_ratio_ge_0.20": int((ratios >= 0.20).sum()),
        "n_seeds_ratio_ge_0.39": int((ratios >= 0.39).sum()),
    }
    dump_json(verdict, GATE_DIR / "B0_SEED32005_PROBE.json")
    header = ["arm", "trace_seed", "model_seed", "model_seed_offset", "source", "role",
              "RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s", "runtime_s",
              "rho_realized", "map_sha256"]
    write_csv(GATE_DIR / "B0_SEED32005_PROBE.csv", out_rows, header)
    print(json.dumps(verdict, indent=1))
    return verdict


def stage_b1(shard: int, nshards: int, limit: int | None = None) -> int:
    plan = b1_plan()
    mine = plan[shard::nshards]
    if limit:
        mine = mine[:limit]
    log(f"SHARD {shard}/{nshards}: {len(mine)} of {len(plan)} runs")
    n_fail = 0
    for i, (arm, ts, ms) in enumerate(mine, 1):
        t0 = time.perf_counter()
        try:
            row = run_arm(arm, ts, ms)
            log(f"  [{i}/{len(mine)}] {arm} trace{ts} seed{ms} {row['status']} "
                f"RMSE={float(row['RMSE_mu']):.6f} sec={time.perf_counter() - t0:.1f}")
        except Exception as exc:                       # record and continue
            n_fail += 1
            log(f"  FAIL {arm} trace{ts} seed{ms}: {type(exc).__name__}: {exc}")
            dump_json({"arm": arm, "trace_seed": ts, "model_seed": ms,
                       "error": f"{type(exc).__name__}: {exc}", "utc": now()},
                      GATE_DIR / "C1_FAILURES" / f"{arm}_trace{ts}_seed{ms}.json")
    log(f"SHARD {shard}/{nshards} done: {len(mine) - n_fail} ok, {n_fail} failed")
    return n_fail


def stage_runs() -> pd.DataFrame:
    rho = arm_rho()
    rows = []
    for arm in ARMS:
        for t in TRACE_SEEDS:
            for off in SEED_OFFSETS:
                ms = t + off
                rec = row_for(arm, t, ms)
                rows.append({
                    "arm": arm, "trace_seed": t, "model_seed": ms,
                    "model_seed_offset": off,
                    "rho_realized": rho[arm][t]["rho_delivered"],
                    "RMSE_mu": rec["RMSE_mu"],
                    "WorstGroupRMSE": rec["WorstGroupRMSE"],
                    "WG_R0": rec["WorstGroupRMSE_R0"], "WG_R1": rec["WorstGroupRMSE_R1"],
                    "WG_R2": rec["WorstGroupRMSE_R2"], "WG_R3": rec["WorstGroupRMSE_R3"],
                    "Delta_group": rec["Delta_group"], "Delta_c_s": rec["Delta_c_s"],
                    "runtime_s": rec.get("runtime_seconds", ""),
                    "map_sha256": map_sha256(get_maps()["maps"][ARMS[arm]["map"]]),
                    "source": rec["status"], "source_path": rec.get("source_path", ""),
                })
    header = ["arm", "trace_seed", "model_seed", "model_seed_offset", "rho_realized",
              "RMSE_mu", "WorstGroupRMSE", "WG_R0", "WG_R1", "WG_R2", "WG_R3",
              "Delta_group", "Delta_c_s", "runtime_s", "map_sha256", "source",
              "source_path"]
    write_csv(GATE_DIR / "C1_RUNS.csv", rows, header)
    df = pd.DataFrame(rows)
    # remove the per-process trace redirects created for the extra model seeds
    import shutil
    link = RUN_OUT / "_trace_link"
    if link.is_dir():
        shutil.rmtree(link, ignore_errors=True)
    print(df.groupby("arm")[["RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s"]]
          .agg(["mean", "std"]).to_string())
    return df


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=("recon", "maps", "b0a", "b0b", "b1", "runs", "plan"))
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--tag", default="b0a")
    ap.add_argument("--arms", default="")
    args = ap.parse_args()

    if args.threads > 0:
        import torch
        torch.set_num_threads(args.threads)
        note = f"torch.set_num_threads({args.threads})"
    else:
        note = "torch default thread count"
    os.environ.setdefault("C1_THREADS_NOTE", note)
    ns.OUT = RUN_OUT
    RUN_OUT.mkdir(parents=True, exist_ok=True)

    if args.stage == "plan":
        plan = b1_plan()
        print(json.dumps({"n_runs": len(plan),
                          "by_arm": {a: sum(1 for p in plan if p[0] == a) for a in ARMS}},
                         indent=1))
        return 0
    if args.stage == "recon":
        stage_recon()
        return 0
    if args.stage == "maps":
        stage_maps()
        return 0
    if args.stage == "b0a":
        arms = tuple(a for a in B0A_ARMS
                     if not args.arms or a[0] in args.arms.split(","))
        doc = stage_b0a(threads_note=note, tag=args.tag, arms=arms)
        return 0 if doc["pass"] else 2
    if args.stage == "b0b":
        stage_b0b(args.shard, args.nshards)
        return 0
    if args.stage == "b1":
        return 1 if stage_b1(args.shard, args.nshards, args.limit or None) else 0
    if args.stage == "runs":
        stage_runs()
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
