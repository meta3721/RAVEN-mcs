#!/usr/bin/env python3
"""Gate-dose round, round_v1 -- driver.

Instruction (read-only copy):
  raven-mcs-gate-dose-execution-prompt.md, sha256 56607091...
  "Executable instruction: dose-response of the Design gate (does rho predict the
   prediction cost of Design?)"

This module is the only writer for results_gate_dose/round_v1/.  It never edits
src/, the manuscript, artifacts/ or any existing results_* directory.  Every
deviation from the instruction is recorded in the report, not silently absorbed.

Frozen protocol elements (section 1 and section 4 of the instruction)
--------------------------------------------------------------------
  mask order   : candidates = production test-split keys with pi_tar > 0, sorted
                 lexicographically; ONE permutation per dataset from
                 numpy.random.default_rng(20261007); level m masks the first
                 round(m * n_positive) keys of that order; nested.
  levels       : SensorScope 0, 0.10, 0.25, 0.40 ; U-Air 0, 0.10, 0.20
  arms         : raven (Design on), raven_wo_design (Design off)
  seeds        : 30001-30020, frozen EventTraces, no regeneration
  estimand     : r_e = (M_e(raven) - M_e(raven_wo_design)) / M_e(raven_wo_design)
  H1           : OLS of r_RMSE on realized rho across (level, seed) cells;
                 seed-cluster bootstrap, 10000 draws, numpy seed 20261007,
                 percentile 95 %.
  H2           : SensorScope m = 0 non-inferiority, upper 95 % t bound < +0.5 %.

Stages (section 7 of the instruction)
------------------------------------
  p0  masks, target wiring, realized rho, manifest            -- no training
  p1  gate at m = 0, seeds 30001-30002, both arms, both datasets -- 8 trains
  p2  the dose cells                                           -- 200 trains
  p3  tables, H1, H2 if licensed, DOSE_DECISION.json

Training (p1/p2) starts only after the user writes "授权门控剂量".
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import pathlib
import shutil
import sys
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "results_gate_dose" / "round_v1"
SCRATCH = ROOT / ".rb_work" / "gate_dose_scratch"
REPLAY_ROOT = OUT / "theta_rescore"

E3_RUNS = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4_RUNS = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
TRACES = ROOT / "artifacts/e3_formal_runs_r1/eventtraces"
TARGET_ARTIFACT = {
    "sensorscope": ROOT / (
        "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/"
        "E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json"
    ),
    "uair": ROOT / (
        "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/"
        "E3_UAIR_TARGET_SEMANTICS_R2.json"
    ),
}
SCD_PHI = ROOT / "post_review/C2_scd_phi/tables/SCD_PHI.csv"

SEEDS = list(range(30001, 30021))
GATE_SEEDS = [30001, 30002]
LEVELS = {"sensorscope": [0.0, 0.10, 0.25, 0.40], "uair": [0.0, 0.10, 0.20]}
ARMS = ["raven", "raven_wo_design"]
METHOD_RAVEN, METHOD_NODESIGN = "raven", "raven_wo_design"
LOCAL_STEPS = 2
MASK_RNG_SEED = 20261007
BOOTSTRAP_SEED = 20261007
BOOTSTRAP_DRAWS = 10000
TOL = 1e-12
RHO_TOL = 1e-6
GATE_TOL = 1e-9
RESCORE_TOL = 1e-8
TAIL = ["RMSE_mu", "Delta_group", "Delta_c_s", "Tail_RMSE"]
R = {"RMSE_mu": "r_RMSE", "Delta_group": "r_dgroup", "Delta_c_s": "r_dcs", "Tail_RMSE": "r_Tail"}

# Frozen m = 0 anchors the instruction names (section 3 / section 0).
# SensorScope 0 exactly; U-Air "mean ~= 0.354" -- the printed 35.4 % and the
# unrounded stored value differ, which is reported rather than hidden.
RHO_M0_ANCHOR = {"sensorscope": 0.0, "uair": 0.35443037974683544}
RHO_M0_PRINTED = {"sensorscope": 0.0, "uair": 0.354}

# ------------------------------------------------------- user-confirmed interpretations
# Confirmed 2026-10-06, before any training run in this round.  These are decisions about
# how to read the instruction, not changes to it; each is recorded in P0_REPORT.md §7.
CONFIRMED = {
    # 1. The primary rho frame is the train-atom frame, because it is the only frame that
    #    reproduces the instruction's pinned m = 0 anchors (0 / 0.35443037974683544).
    "rho_frame": "train_atoms",
    # 2. The instruction's 1e-6 rho tolerance is read against the unrounded 0.35443037...
    #    (the printed 0.354 is 4.3e-4 away and cannot satisfy it).
    "rho_m0_tolerance_reference": "unrounded",
    # 3. The stored-vs-theta-rescore check applies to the two endpoints that are functions
    #    of the final theta (both reproduce at 0.0); the structural endpoints are
    #    trajectory functionals and their replay movement is disclosed, not gated.
    "theta_check_endpoints": ["RMSE_mu", "Tail_RMSE"],
    "theta_rescore_endpoints": TAIL,
    # 4. If the m = 0 gate misses, write pass: false and stop.  No tolerance amendment, no
    #    waiver list, no continuation into P2 on a failed gate.
    "gate_failure_action": "stop_round",
}


# --------------------------------------------------------------------- utilities
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: pathlib.Path) -> str:
    return sha256_bytes(p.read_bytes())


def sha256_json(obj: Any) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def pi_hash(pi: dict[tuple[str, str], float]) -> str:
    """Canonical hash of a (client, stratum) -> mass map."""
    return sha256_json({f"{c}::{s}": float(v) for (c, s), v in pi.items()})


def dump_json(obj: Any, p: pathlib.Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")


def rel(p: pathlib.Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------- target consumers
def load_atomic(dataset: str) -> tuple[pd.DataFrame, dict[str, str]]:
    """Sealed atomic frame + frozen spatial -> client map (production construction)."""
    from raven_mcs.e3.canary.dataset_load import load_spatial_to_client
    from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum

    atomic = pd.read_parquet(ROOT / "data" / "processed" / dataset / "atomic_units.parquet")
    sealed, _meta = apply_sealed_opportunity_stratum(atomic, dataset=dataset, root=ROOT)
    mapping = load_spatial_to_client(ROOT, dataset)
    return sealed, mapping


def production_pi_target(dataset: str, sealed: pd.DataFrame, mapping: dict[str, str]) -> dict[tuple[str, str], float]:
    """Consumer T1 at m = 0: exactly what run_e3_real builds for pi_target_mode='test'."""
    from raven_mcs.correction.pi_target import build_pi_target

    frame = sealed.copy()
    if "target_group_main" not in frame.columns:
        frame["target_group_main"] = frame["target_group"].astype(str)
    pi = build_pi_target(frame, mapping, split="test")
    return {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in pi.itertuples(index=False)
    }


def production_mu(dataset: str) -> tuple[np.ndarray, list[str], dict[str, Any]]:
    """Consumer T2 at m = 0: the frozen artifact mu and its group order."""
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset
    from raven_mcs.e3.target_pair.target_wiring import production_target_bundle

    ds = load_paper_dataset(ROOT, dataset)
    bundle = production_target_bundle(root=ROOT, dataset_name=dataset, dataset=ds)
    return (
        np.asarray(bundle["mu"], dtype=np.float64),
        list(bundle["group_id_by_index"]),
        {
            "artifact_path": str(bundle["artifact_path"]).replace("\\", "/"),
            "artifact_sha256": bundle["artifact_sha256"],
            "n_groups_runtime": int(bundle["n_groups_runtime"]),
            "n_groups_frozen": int(bundle["n_groups_frozen"]),
        },
    )


def group_share_from_test(sealed: pd.DataFrame, mapping: dict[str, str], gids: list[str]) -> np.ndarray:
    """Consumer T2 construction: group share of the (masked) test split."""
    test = sealed.loc[sealed["split"].astype(str) == "test"]
    unit_client = {}
    for r in sealed.itertuples(index=False):
        sid = str(r.spatial_id)
        if sid in mapping:
            unit_client[str(r.unit_id)] = str(mapping[sid])
    share = np.zeros(len(gids), dtype=np.float64)
    for r in test.itertuples(index=False):
        uid = str(r.unit_id)
        c = unit_client.get(uid)
        if c is None:
            continue
        share[gids.index(str(r.target_group))] += 1.0
    return share


# --------------------------------------------------------------------------- masks
def mask_permutation(dataset: str, pi0: dict[tuple[str, str], float]) -> dict[str, Any]:
    """Section 1 mask construction, fixed before any run."""
    candidates = sorted(k for k, v in pi0.items() if v > 0.0)
    rng = np.random.default_rng(MASK_RNG_SEED)
    perm = rng.permutation(len(candidates))
    order = [candidates[int(i)] for i in perm]
    levels = LEVELS[dataset]
    per_level = {}
    for m in levels:
        n = int(round(m * len(candidates)))
        if m == 0.0:
            n = 0
        per_level[fmt_m(m)] = {
            "m": m,
            "n_masked": n,
            "masked_keys": [[k[0], k[1]] for k in order[:n]],
        }
    return {
        "dataset": dataset,
        "rng": "numpy.random.default_rng(%d)" % MASK_RNG_SEED,
        "draws": 1,
        "candidate_rule": "production test-split keys with pi_tar > 0, lexicographic",
        "n_positive": len(candidates),
        "n_keys_total": len(pi0),
        "candidates": [[k[0], k[1]] for k in candidates],
        "permutation": [int(i) for i in perm],
        "order": [[k[0], k[1]] for k in order],
        "levels": per_level,
        "nested": all(
            set(tuple(x) for x in per_level[fmt_m(levels[i])]["masked_keys"])
            <= set(tuple(x) for x in per_level[fmt_m(levels[i + 1])]["masked_keys"])
            for i in range(len(levels) - 1)
        ),
    }


def fmt_m(m: float) -> str:
    return ("%.2f" % m).rstrip("0").rstrip(".") if m else "0"


def masked_targets(
    pi0: dict[tuple[str, str], float],
    masked_keys: list[list[str]],
    sealed: pd.DataFrame,
    mapping: dict[str, str],
    gids: list[str],
) -> dict[str, Any]:
    """The three consumers, all read off the same masked test split."""
    masked = {tuple(k) for k in masked_keys}
    raw = {k: (0.0 if k in masked else float(v)) for k, v in pi0.items()}
    total = float(sum(raw.values()))
    if total <= 0.0:
        raise RuntimeError("masked target has zero mass")
    pi_masked = {k: v / total for k, v in raw.items()}

    # mu: group share of the masked test units.
    unit_client = {}
    for r in sealed.itertuples(index=False):
        sid = str(r.spatial_id)
        if sid in mapping:
            unit_client[str(r.unit_id)] = str(mapping[sid])
    test = sealed.loc[sealed["split"].astype(str) == "test"]
    share = np.zeros(len(gids), dtype=np.float64)
    n_units = 0
    key_of_unit_stratum = {}
    for r in sealed.itertuples(index=False):
        key_of_unit_stratum[str(r.unit_id)] = str(r.opportunity_stratum)
    for r in test.itertuples(index=False):
        uid = str(r.unit_id)
        c = unit_client.get(uid)
        if c is None:
            continue
        s = key_of_unit_stratum[uid]
        if (c, s) in masked:
            continue
        n_units += 1
        share[gids.index(str(r.target_group))] += 1.0
    if n_units == 0:
        raise RuntimeError("every test unit belongs to a masked key")
    mu = share / share.sum()
    return {"pi_target": pi_masked, "mu": mu, "n_test_units_kept": n_units,
            "n_masked_keys": len(masked), "mass_removed": 1.0 - total}


# ----------------------------------------------------------------------- rho (T3)
def unit_frame(sealed: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """(unit_id, split, client_id, stratum) for every atomic unit."""
    rows = []
    for r in sealed.itertuples(index=False):
        uid = str(r.unit_id)
        sid = str(r.spatial_id)
        rows.append({"unit_id": uid, "split": str(r.split),
                     "client_id": str(mapping.get(sid, "")),
                     "stratum": str(r.opportunity_stratum)})
    return pd.DataFrame(rows)


def delivered_risk_records(dataset: str, frame: pd.DataFrame, seeds: list[int]) -> pd.DataFrame:
    """U = 1 delivered risk units, non-test splits, per frozen trace.

    Semantics of scripts/c1_deletion_driver.py::risk_records (its `json.loads` of the
    list columns included), re-pointed at the E3 frozen traces because the C1 copy is
    bound to City Scanner paths.
    """
    split_of = dict(zip(frame["unit_id"], frame["split"]))
    stratum_of = dict(zip(frame["unit_id"], frame["stratum"]))
    recs = []
    for seed in seeds:
        ev = pd.read_parquet(TRACES / dataset / ("seed%d" % seed) / "training_eventtrace/events.parquet")
        for row in ev.itertuples(index=False):
            if int(row.U) != 1:
                continue
            cid = str(row.client_id)
            raw = row.risk_set_unit_ids
            ids = json.loads(raw) if isinstance(raw, str) else list(raw)
            for uid_raw in ids:
                uid = str(uid_raw)
                if split_of.get(uid) == "test":
                    continue
                recs.append({"trace_seed": int(seed), "window_id": int(row.window_id),
                             "client_id": cid, "unit_id": uid,
                             "stratum": stratum_of.get(uid, "unknown")})
    return pd.DataFrame(recs)


def train_atom_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Every train atom with its (client, stratum) key.

    This is the frame that reproduces the instruction's pinned m = 0 anchors
    (SensorScope 0, U-Air 0.35443037974683544 = SCD_PHI phi_train_unit) and the
    frame SCD_PHI calls `phi_train_unit`.  It carries no model output and no seed
    dependence, which is what section 3 of the instruction asks for.
    """
    train = frame.loc[frame["split"].astype(str) == "train"]
    train = train.loc[train["client_id"].astype(str) != ""]
    return pd.DataFrame({"client_id": train["client_id"].astype(str).tolist(),
                         "stratum": train["stratum"].astype(str).tolist()})


def rho_for(values: dict[tuple[str, str], float], frame: pd.DataFrame) -> dict[str, Any]:
    """Verbatim semantics of c1_deletion_driver.rho_for (lines 334-342)."""
    vals = np.asarray([values.get((c, s), np.nan)
                       for c, s in zip(frame["client_id"], frame["stratum"])],
                      dtype=np.float64)
    n = int(np.isfinite(vals).sum())
    n_zero = int(np.nansum(vals <= 0.0))
    return {"n_delivered": n, "n_zero": n_zero,
            "rho_delivered": (n_zero / n) if n else None}


# ------------------------------------------------------------- monkeypatch helpers
@contextlib.contextmanager
def patched_bundle(mu: np.ndarray):
    """Patch production_target_bundle so mu is the masked group target.

    Same technique as scripts/run_h_headroom.py::injected.  Head/tail ids and the
    artifact hashes stay those of the frozen artifact; only mu is replaced.
    """
    import raven_mcs.e3.real_runner.runner as rr

    orig = rr.production_target_bundle

    def _bundle(**kw):
        b = dict(orig(**kw))
        b["mu"] = np.asarray(mu, dtype=np.float64)
        b["mu_source"] = "GATE_DOSE_MASKED_TEST_SPLIT"
        return b

    rr.production_target_bundle = _bundle
    try:
        yield
    finally:
        rr.production_target_bundle = orig


@contextlib.contextmanager
def patched_pi_tar(pi_masked: dict[tuple[str, str], float]):
    """Patch the Delta_c-s denominator builder so consumer T3 sees the masked target.

    accumulate_delta_cs_v6 calls build_pi_tar_client_stratum(...) directly; the
    function asserts sum(pi_tar) == 1, which the renormalized map satisfies.
    """
    import raven_mcs.e3.delta_cs_rho.delta_cs_v6 as v6

    orig = v6.build_pi_tar_client_stratum
    flat = {f"{c}::{s}": float(v) for (c, s), v in pi_masked.items()}

    def _build(atomic, spatial_to_client, *, split="test"):
        return dict(flat)

    v6.build_pi_tar_client_stratum = _build
    try:
        yield
    finally:
        v6.build_pi_tar_client_stratum = orig


@contextlib.contextmanager
def frozen_theta(state: dict[str, Any]):
    """Run the production entry point with theta pinned and no local step.

    `_frozen_train_step` keeps the checkpoint parameters and returns an empty
    update, so the server aggregation is a no-op on theta while every downstream
    quantity is recomputed by the production code path.
    """
    import raven_mcs.training.window_runner as wr
    import raven_mcs.e3.real_runner.runner as rr

    orig_build = rr.build_full_runner
    orig_step = wr.ClientTrainer.train_step

    def _build(*a, **kw):
        runner = orig_build(*a, **kw)
        runner.theta = {k: v.clone().detach() for k, v in state.items()}
        runner.model.load_state_dict(runner.theta)
        runner.model_versions = {0: {k: v.clone() for k, v in runner.theta.items()}}
        return runner

    def _step(self, *, model_state, observed_records, a_bar_weights, local_steps):
        self.model.load_state_dict({k: v.clone() for k, v in model_state.items()})
        self.model.eval()
        return np.array([], dtype=np.float64), 0.0

    rr.build_full_runner = _build
    wr.ClientTrainer.train_step = _step
    try:
        yield
    finally:
        rr.build_full_runner = orig_build
        wr.ClientTrainer.train_step = orig_step


# --------------------------------------------------------------------- run one cell
def run_cell(dataset: str, arm: str, seed: int, level: float, pi_masked, mu_masked,
             *, out_dir: pathlib.Path, frozen_state=None) -> dict[str, Any]:
    """One training run (or frozen-theta replay when frozen_state is given)."""
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.real_runner.runner import run_e3_real

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    ctx = [patched_bundle(mu_masked), patched_pi_tar(pi_masked)]
    if frozen_state is not None:
        ctx.append(frozen_theta(frozen_state))
    with contextlib.ExitStack() as stack:
        for c in ctx:
            stack.enter_context(c)
        run_e3_real(
            root=ROOT,
            run_dir=out_dir,
            dataset=load_paper_dataset(ROOT, dataset),
            method=arm,
            seed=int(seed),
            eventtrace_dir=TRACES / dataset / ("seed%d" % seed) / "training_eventtrace",
            spatial_to_client=load_spatial_to_client(ROOT, dataset),
            dataset_name=dataset,
            local_steps=LOCAL_STEPS,
            pi_target_override={k: float(v) for k, v in pi_masked.items()},
        )
    metrics = json.loads((out_dir / "final_metrics.json").read_text(encoding="utf-8"))
    wm = json.loads((out_dir / "window_metrics.json").read_text(encoding="utf-8"))
    return {"metrics": metrics, "window_metrics": wm, "run_dir": out_dir}


def load_theta(run_dir: pathlib.Path) -> dict[str, Any]:
    import torch

    obj = torch.load(run_dir / "checkpoints/final.pt", map_location="cpu", weights_only=False)
    return obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj


def stored_run_dir(dataset: str, arm: str, seed: int) -> pathlib.Path:
    base = E3_RUNS if arm == METHOD_RAVEN else E4_RUNS
    return base / dataset / arm / ("seed%d" % seed)


# ---------------------------------------------------------------------------- P0
def stage_p0(force: bool = False) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    masks_path = OUT / "MASKS.json"
    wiring_path = OUT / "TARGET_WIRING.json"
    rho_path = OUT / "RHO.csv"
    if masks_path.exists() and not force:
        raise SystemExit("P0 artifacts already exist; pass --force to rewrite them")

    wiring: dict[str, Any] = {"created_utc": now(), "datasets": {}}
    masks: dict[str, Any] = {"created_utc": now(), "rng_seed": MASK_RNG_SEED, "datasets": {}}
    rho_rows: list[dict[str, Any]] = []

    for dataset in ("sensorscope", "uair"):
        sealed, mapping = load_atomic(dataset)
        pi0 = production_pi_target(dataset, sealed, mapping)
        mu0, gids, art = production_mu(dataset)
        share0 = group_share_from_test(sealed, mapping, gids)
        mask = mask_permutation(dataset, pi0)
        masks["datasets"][dataset] = mask

        ds_wiring: dict[str, Any] = {
            "target_artifact": art,
            "n_groups": len(gids),
            "consumers": {
                "T1_pi_target_override": "run_e3_real(pi_target_override=...) -> WorkerSetup.pi_target",
                "T2_mu_bundle": "production_target_bundle(...)['mu'] (patched), used by Delta_group and the RMSE_mu test weights",
                "T3_delta_cs_denominator": "raven_mcs.e3.delta_cs_rho.delta_cs_v6.build_pi_tar_client_stratum (patched)",
            },
            "levels": {},
        }

        # ---- m = 0 identities against the production objects
        m0 = masked_targets(pi0, [], sealed, mapping, gids)
        pi0_prod_hash = pi_hash(pi0)
        pi0_new_hash = pi_hash(m0["pi_target"])
        keys = sorted(set(pi0) | set(m0["pi_target"]))
        pi0_max_diff = float(max(abs(pi0.get(k, 0.0) - m0["pi_target"].get(k, 0.0)) for k in keys))
        ds_wiring["m0_identity"] = {
            # The masked map is renormalized by its own total, so at m = 0 it differs
            # from the production map only by renormalization noise (~1e-15).  The
            # check is therefore a value check, not a hash check.
            "T1_pi_target_hash_production": pi0_prod_hash,
            "T1_pi_target_hash_rebuilt": pi0_new_hash,
            "T1_pi_target_max_abs_diff_vs_production": pi0_max_diff,
            "T1_pi_target_hash_equal": pi0_prod_hash == pi0_new_hash,
            "T1_pi_target_values_equal_1e-12": pi0_max_diff <= TOL,
            "T2_mu_max_abs_diff_vs_production": float(np.abs(m0["mu"] - mu0).max()),
            "T2_mu_max_abs_diff_share_vs_mu": float(np.abs(share0 / share0.sum() - mu0).max()),
            "T3_pi_tar_rebuilt_max_abs_diff_vs_production": pi0_max_diff,
            "T3_pi_tar_hash_equal": pi0_new_hash == pi0_prod_hash,
            "sum_pi_target": float(sum(m0["pi_target"].values())),
            "sum_mu": float(m0["mu"].sum()),
            "renormalization_noise_note": "1 - sum(pi_tar) before renormalization at m = 0",
            "pi0_sum_before_renorm": float(sum(pi0.values())),
        }
        ds_wiring["m0_identity"]["pass"] = bool(
            ds_wiring["m0_identity"]["T1_pi_target_values_equal_1e-12"]
            and ds_wiring["m0_identity"]["T2_mu_max_abs_diff_vs_production"] <= TOL
            and ds_wiring["m0_identity"]["T3_pi_tar_rebuilt_max_abs_diff_vs_production"] <= TOL
            and abs(ds_wiring["m0_identity"]["sum_pi_target"] - 1.0) <= TOL
            and abs(ds_wiring["m0_identity"]["sum_mu"] - 1.0) <= TOL
        )

        # ---- rho frames, computed once (no model output, no training)
        frame_units = unit_frame(sealed, mapping)
        train_atoms = train_atom_frame(frame_units)
        delivered = delivered_risk_records(dataset, frame_units, SEEDS)
        ds_wiring["rho_frame"] = {
            "primary": "train atoms (sealed split == 'train'), keyed by (client, stratum)",
            "primary_rule": "SCD_PHI phi_train_unit; reproduces the pinned m = 0 anchors",
            "n_train_atoms": int(len(train_atoms)),
            "cross_check_frames": {
                "delivered_U1_non_test": {
                    "n_records": int(len(delivered)),
                    "n_traces": len(SEEDS),
                    "source": rel(TRACES / dataset),
                    "frame_rho_at_m0": rho_for(pi0, delivered)["rho_delivered"],
                    "note": "c1_deletion_driver-style event-trace frame; for the E3 traces it "
                            "gives 0 / 0.2543 and is reported as a cross-check only, because "
                            "the instruction pins m = 0 to 0 / 0.35443 (SCD_PHI phi_train_unit)",
                },
            },
        }

        for m in LEVELS[dataset]:
            level = mask["levels"][fmt_m(m)]
            tgt = masked_targets(pi0, level["masked_keys"], sealed, mapping, gids)
            share = group_share_from_test_masked(sealed, mapping, gids, level["masked_keys"])
            mu_share_diff = float(np.abs(share / share.sum() - tgt["mu"]).max())
            entry = {
                "m": m,
                "n_masked_keys": level["n_masked"],
                "mass_removed": tgt["mass_removed"],
                "sum_pi_target": float(sum(tgt["pi_target"].values())),
                "sum_mu": float(tgt["mu"].sum()),
                "mu_vs_masked_test_share_max_abs": mu_share_diff,
                "pi_target_hash": sha256_json({f"{c}::{s}": v for (c, s), v in tgt["pi_target"].items()}),
                "mu_hash": sha256_json(tgt["mu"].tolist()),
                "n_test_units_kept": tgt["n_test_units_kept"],
                "pass": bool(abs(sum(tgt["pi_target"].values()) - 1.0) <= TOL
                             and abs(tgt["mu"].sum() - 1.0) <= TOL
                             and mu_share_diff <= TOL),
            }
            ds_wiring["levels"][fmt_m(m)] = entry

            # realized rho on the primary frame; it carries no seed dimension.
            primary = rho_for(tgt["pi_target"], train_atoms)
            alt_delivered = rho_for(tgt["pi_target"], delivered)
            per_seed = {}
            for seed in SEEDS:
                sub = delivered[delivered["trace_seed"] == seed]
                per_seed[str(seed)] = rho_for(tgt["pi_target"], sub)["rho_delivered"]
            finite = [v for v in per_seed.values() if v is not None]
            rho_rows.append({
                "dataset": dataset, "m": m, "level": fmt_m(m),
                "n_masked_keys": level["n_masked"],
                "rho": primary["rho_delivered"],
                "n_train_atoms": primary["n_delivered"],
                "n_train_atoms_zero": primary["n_zero"],
                "rho_alt_delivered_traces": alt_delivered["rho_delivered"],
                "rho_alt_n_records": alt_delivered["n_delivered"],
                "rho_alt_per_seed_mean": float(np.mean(finite)) if finite else None,
                "rho_alt_per_seed_min": float(np.min(finite)) if finite else None,
                "rho_alt_per_seed_max": float(np.max(finite)) if finite else None,
                "rho_alt_per_seed": json.dumps(per_seed, sort_keys=True),
                "seed_dimension": "none (static frame, no model output)",
            })

        wiring["datasets"][dataset] = ds_wiring

    # ---- m = 0 rho check against the published anchors
    phi = pd.read_csv(SCD_PHI).set_index("dataset")
    rho_check = {}
    for dataset in ("sensorscope", "uair"):
        row = next(r for r in rho_rows if r["dataset"] == dataset and r["m"] == 0.0)
        anchor = RHO_M0_ANCHOR[dataset]
        printed = RHO_M0_PRINTED[dataset]
        rho_check[dataset] = {
            "rho_m0_measured": row["rho"],
            "anchor_unrounded": anchor,
            "anchor_printed": printed,
            "diff_vs_unrounded": abs(row["rho"] - anchor),
            "diff_vs_printed": abs(row["rho"] - printed),
            "pass_vs_unrounded_1e-6": abs(row["rho"] - anchor) <= RHO_TOL,
            "pass_vs_printed_1e-6": abs(row["rho"] - printed) <= RHO_TOL,
            "scd_phi_train_unit": float(phi.loc[dataset, "phi_train_unit"]),
            "scd_phi_train_pair": float(phi.loc[dataset, "phi_train_pair"]),
            "scd_phi_et_occ": float(phi.loc[dataset, "phi_et_occ"]),
        }
    wiring["m0_rho_check"] = rho_check

    dump_json(masks, masks_path)
    dump_json(wiring, wiring_path)

    rho_df = pd.DataFrame(rho_rows)
    rho_df.to_csv(rho_path, index=False)

    manifest = write_manifest(masks, wiring, rho_rows)

    print("P0 written to %s" % rel(OUT))
    print("content hashes: %s" % json.dumps(manifest["content_sha256"]))
    print(json.dumps({"m0_identity": {d: wiring["datasets"][d]["m0_identity"]["pass"]
                                      for d in wiring["datasets"]},
                      "m0_rho": {d: {"measured": rho_check[d]["rho_m0_measured"],
                                     "anchor": rho_check[d]["anchor_unrounded"],
                                     "diff": rho_check[d]["diff_vs_unrounded"],
                                     "pass": rho_check[d]["pass_vs_unrounded_1e-6"]}
                                 for d in rho_check},
                      "levels": {d: wiring["datasets"][d]["levels"] for d in wiring["datasets"]}},
                     indent=2, default=float))
    return wiring


def group_share_from_test_masked(sealed, mapping, gids, masked_keys) -> np.ndarray:
    masked = {tuple(k) for k in masked_keys}
    unit_client = {}
    for r in sealed.itertuples(index=False):
        sid = str(r.spatial_id)
        if sid in mapping:
            unit_client[str(r.unit_id)] = str(mapping[sid])
    stratum = dict(zip(sealed["unit_id"].astype(str), sealed["opportunity_stratum"].astype(str)))
    test = sealed.loc[sealed["split"].astype(str) == "test"]
    share = np.zeros(len(gids), dtype=np.float64)
    for r in test.itertuples(index=False):
        uid = str(r.unit_id)
        c = unit_client.get(uid)
        if c is None or (c, stratum[uid]) in masked:
            continue
        share[gids.index(str(r.target_group))] += 1.0
    return share


def write_manifest(masks: dict[str, Any], wiring: dict[str, Any],
                   rho_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """(Re)write MANIFEST.sha256 from the current artifacts.

    Called at the end of p0 and again after the P0 report is written, so the report's
    hash is recorded too.  The content hashes are timestamp-free and are the
    pre-registration proof: at m = 0 they were written before any training run.
    """
    masks_path, wiring_path, rho_path = OUT / "MASKS.json", OUT / "TARGET_WIRING.json", OUT / "RHO.csv"
    manifest = {
        "round": "results_gate_dose/round_v1",
        "created_utc": now(),
        "instruction": {
            "path": "raven-mcs-gate-dose-execution-prompt.md",
            "sha256": "56607091831dbaff735061019b6c82cb5a89d2b09c465083cac70c967ee2b59b",
            "bytes": 11275,
        },
        "files": {},
        "content_sha256": {
            # Timestamp-free hashes of the frozen-content objects.  `RHO.csv` is covered
            # by its own file hash (it is content-deterministic, unlike the JSON dumps).
            "masks": sha256_json(masks["datasets"]),
            "wiring": sha256_json({k: v for k, v in wiring.items() if k != "created_utc"}),
        },
        "training_authorized": (OUT / "GATE.json").is_file(),
    }
    for p in (masks_path, wiring_path, rho_path):
        if p.is_file():
            manifest["files"][rel(p)] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    # `P0_REPORT.md` is deliberately NOT hashed here: this manifest is regenerated as
    # the round progresses, and hashing a narrative file that cites the manifest is a
    # circular dependency.
    dump_json(manifest, OUT / "MANIFEST.sha256")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["p0", "p0-manifest", "p1", "p2", "p3", "rho-probe"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if args.stage == "p0":
        stage_p0(force=args.force)
    elif args.stage == "p0-manifest":
        masks = json.loads((OUT / "MASKS.json").read_text(encoding="utf-8"))
        wiring = json.loads((OUT / "TARGET_WIRING.json").read_text(encoding="utf-8"))
        rho_rows = pd.read_csv(OUT / "RHO.csv").to_dict(orient="records")
        m = write_manifest(masks, wiring, rho_rows)
        print("manifest refreshed")
        print(json.dumps({"content_sha256": m["content_sha256"],
                          "files": {k: v["sha256"][:16] for k, v in m["files"].items()}}, indent=2))
    else:
        raise SystemExit("stage %s not enabled in this build" % args.stage)


if __name__ == "__main__":
    main()
