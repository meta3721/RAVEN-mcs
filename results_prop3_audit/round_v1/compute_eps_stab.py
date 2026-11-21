#!/usr/bin/env python
"""eps_stab audit on the frozen E3 (SensorScope / U-Air) artifacts.

Read-only numerical audit.  This script NEVER writes outside
``results_prop3_audit/round_v1/`` and never runs training or a solver.

It implements, exactly as specified in the task:

  zeta_T = pi_tar / max(pi_opp_true, pi_min)      [Design ON]  or 1  [Design OFF]
  a_T    = min(a_max, zeta_T / max(p_obs_true, p_min))
  d_T    = min(d_max, 1 / max(q_use_true, q_min))
  m_T    = n_obs * a_T          b_T = m_T * d_T
  zeta_star = pi_tar / pi_opp_true                [Design ON]  or 1  [Design OFF]
  a_star = zeta_star / p_obs_true               d_star = 1 / q_use_true
  b_star = n_obs * a_star * d_star
  beta   = b / sum_j b_j   (Hajek, over the ACTIVE clients j of the window)
  eps_stab(r) = || beta_T(r) - beta_star(r) ||_1

Active client of a window = client-window with at least one observed unit
(n_obs > 0, equivalently O true).

Run:  .venv_new\\Scripts\\python.exe results_prop3_audit\\round_v1\\compute_eps_stab.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent

AUDIT_CSV = ROOT / "artifacts" / "a5_a6_audit" / "audit_records.csv"
TRACE_ROOT = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces"
RUNS_ROOT = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
SS_CLIENT_YAML = ROOT / "configs" / "frozen" / "e1_sensorscope_clients.yaml"

DATASETS = ("sensorscope", "uair")
SEEDS = tuple("seed30%03d" % i for i in range(1, 21))

# --------------------------------------------------------------------------
# constants  (verified: src/raven_mcs/training/window_runner.py:1433-1437 of the
# frozen run revision f7bff5e3..., and build_full_runner *defaults* at the same
# revision lines 824-828; src/raven_mcs/e3/real_runner/runner.py:471-484 calls
# build_full_runner without overriding any of a_max/p_min/pi_min/d_max/q_min)
# --------------------------------------------------------------------------
A_MAX = 20.0
P_MIN = 0.05
PI_MIN = 1e-6
D_MAX = 10.0
Q_MIN = 0.05

# build_joint_pi_opp defaults (src/raven_mcs/e3/real_runner/generator_r3.py:17-44)
THETA_ALIGN = 1.25
TAIL_BLOCKS = {2, 3}

# pi_target resolution -- see EPS_STAB.md "pi_tar resolution"
PI_TARGET_MODE = "test"

EPS_TOL = 1e-12  # "numerically zero" threshold for the >0 fraction

# Active-set variants.  "O_n_obs_gt_0" is the definition given in the task;
# "A_r_frozen" is the realized design-ON active set logged by the runs;
# "O_and_U" is the realized design-OFF active set.
ACTIVE_SET_VARIANTS = {
    "O_n_obs_gt_0": lambda g: g[g["O"]],
    "A_r_frozen": lambda g: g[g["O"] & g["in_A_r"]],
    "O_and_U": lambda g: g[g["O"] & g["U"]],
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# pi_opp / pi_tar reconstruction  (pandas + numpy only, no repo imports)
# --------------------------------------------------------------------------
def spatial_to_client(root: Path, dataset: str, atomic: pd.DataFrame) -> dict[str, str]:
    """Mirror raven_mcs.e3.canary.dataset_load.load_spatial_to_client."""
    if dataset == "sensorscope":
        payload = yaml.safe_load(SS_CLIENT_YAML.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in payload["station_to_client"].items()}
    if dataset == "uair":
        spatials = sorted(atomic["spatial_id"].astype(str).unique().tolist())
        return {sid: "client-%03d" % (i % 8) for i, sid in enumerate(spatials)}
    raise ValueError(dataset)


def block_from_stratum(stratum: str) -> int:
    for part in str(stratum).split("::"):
        if part.startswith("block"):
            return int(part.replace("block", ""))
    return 0


def build_joint_pi_opp(
    client_ids: list[str],
    strata_by_client: dict[str, list[str]],
) -> dict[tuple[str, str], float]:
    """Mirror raven_mcs.e3.real_runner.generator_r3.build_joint_pi_opp."""
    p_client = 1.0 / max(len(client_ids), 1)
    raw: dict[tuple[str, str], float] = {}
    for client in client_ids:
        strata = strata_by_client.get(client, [])
        if not strata:
            continue
        scores = np.asarray(
            [np.exp(-THETA_ALIGN if block_from_stratum(s) in TAIL_BLOCKS else 0.0)
             for s in strata],
            dtype=np.float64,
        )
        cond = scores / scores.sum()
        for s, c in zip(strata, cond):
            raw[(client, s)] = float(p_client * c)
    total = sum(raw.values())
    if total <= 0:
        raise RuntimeError("empty joint pi_opp")
    return {k: v / total for k, v in raw.items()}


def build_pi_tar(
    atomic: pd.DataFrame,
    mapping: dict[str, str],
    split: str = "test",
) -> dict[tuple[str, str], float]:
    """Mirror raven_mcs.correction.pi_target.build_pi_target (mode 'test').

    TargetBuilder gives uniform atom mass over SUPPORTED units of ``split``;
    pi_tar(k,s) = Lambda_s * lambda_{k|s} with the lambda_{k|s} share taken on
    the same frozen split.  Every (client, stratum) pair appearing anywhere in
    the atomic table is present in the support (value 0 when it carries no
    split mass) -- exactly as the runner's pi_target dict is built.
    """
    frame = atomic.copy()
    frame["opportunity_stratum"] = frame["opportunity_stratum"].astype(str)
    frame["spatial_id"] = frame["spatial_id"].astype(str)
    frame["unit_id"] = frame["unit_id"].astype(str)

    selected = frame.loc[frame["split"].astype(str) == str(split)].copy()
    supported = selected.loc[selected["support_flag"].astype(bool)].copy()
    if supported.empty:
        raise RuntimeError("no supported atomic units in split=%s" % split)

    n_sup = len(supported)
    supported["target_mass"] = 1.0 / n_sup
    supported["client_id"] = supported["spatial_id"].map(mapping)
    if supported["client_id"].isna().any():
        raise RuntimeError("positive target station lacks frozen client mapping")

    lambda_s = supported.groupby("opportunity_stratum")["target_mass"].sum()
    mass_ks = (
        supported.groupby(["client_id", "opportunity_stratum"])["target_mass"]
        .sum()
        .rename("mass_ks")
    )

    all_units = frame[["spatial_id", "opportunity_stratum"]].copy()
    all_units["client_id"] = all_units["spatial_id"].map(mapping)
    if all_units["client_id"].isna().any():
        raise RuntimeError("atomic station lacks frozen client mapping")
    support = all_units[["client_id", "opportunity_stratum"]].drop_duplicates()
    support = support.merge(
        mass_ks.reset_index(), on=["client_id", "opportunity_stratum"], how="left",
    )
    support["mass_ks"] = support["mass_ks"].fillna(0.0)
    support["Lambda_s_tar"] = support["opportunity_stratum"].map(lambda_s).fillna(0.0)
    support["lambda_k_given_s_tar"] = 0.0
    pos = support["Lambda_s_tar"] > 0
    support.loc[pos, "lambda_k_given_s_tar"] = (
        support.loc[pos, "mass_ks"] / support.loc[pos, "Lambda_s_tar"]
    )
    support["pi_k_s_tar"] = support["Lambda_s_tar"] * support["lambda_k_given_s_tar"]

    total = float(support["pi_k_s_tar"].sum())
    if abs(total - 1.0) > 1e-12:
        raise RuntimeError("pi target does not sum to one (sum=%r)" % total)
    return {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in support.itertuples(index=False)
    }


def dataset_targets(dataset: str) -> dict:
    atomic = pd.read_parquet(ROOT / "data" / "processed" / dataset / "atomic_units.parquet")
    mapping = spatial_to_client(ROOT, dataset, atomic)

    train = atomic.loc[atomic["split"].astype(str) == "train"]
    strata_by_client: dict[str, list[str]] = {}
    for r in train.itertuples(index=False):
        c = mapping.get(str(r.spatial_id))
        if c is None:
            continue
        strata_by_client.setdefault(c, []).append(str(r.opportunity_stratum))
    for c in strata_by_client:
        strata_by_client[c] = sorted(set(strata_by_client[c]))

    pi_opp = build_joint_pi_opp(sorted(strata_by_client), strata_by_client)
    pi_tar = build_pi_tar(atomic, mapping, split="test")
    return {
        "atomic": atomic,
        "mapping": mapping,
        "strata_by_client": strata_by_client,
        "pi_opp_joint": pi_opp,
        "pi_tar": pi_tar,
    }


# --------------------------------------------------------------------------
# frozen trace harvest
# --------------------------------------------------------------------------
def harvest(dataset: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (margin rows re-harvested from parquet, stratum per client-window).

    Column semantics mirror tools/a5_a6_support_audit.py exactly.
    """
    rows = []
    strata = []
    for seed in SEEDS:
        path = TRACE_ROOT / dataset / seed / "training_eventtrace" / "events.parquet"
        if not path.is_file():
            continue
        df = pd.read_parquet(
            path,
            columns=["window_id", "client_id", "opportunity_features",
                     "observed_unit_ids", "O", "U", "oracle_p", "oracle_q"],
        )
        for r in df.itertuples(index=False):
            of = r.opportunity_features
            j = json.loads(of) if isinstance(of, str) else dict(of)
            obs = r.observed_unit_ids
            if isinstance(obs, str):
                try:
                    n_obs = len(json.loads(obs))
                except Exception:
                    n_obs = 0
            elif obs is None:
                n_obs = 0
            else:
                n_obs = len(obs)
            o_flag = r.O
            if isinstance(o_flag, str):
                o_flag = o_flag.strip().lower() in ("true", "1")
            rows.append(dict(
                dataset=dataset, seed=seed, window=int(r.window_id),
                client=str(r.client_id),
                pi_opp_true=j.get("pi_opp_true"),
                p_obs_true=j.get("p_obs_true"),
                q_use_true=j.get("q_use_true"),
                q_mc_se=j.get("q_mc_se"),
                n_obs=n_obs, O=bool(o_flag) or n_obs > 0,
                U=str(r.U).strip().lower() in ("true", "1"),
                oracle_p=r.oracle_p, oracle_q=r.oracle_q))
            strata.append(dict(
                dataset=dataset, seed=seed, window=int(r.window_id),
                client=str(r.client_id),
                opportunity_stratum=str(j.get("opportunity_stratum")),
                risk_set_size=len(json.loads(r.risk_set_unit_ids))
                if isinstance(getattr(r, "risk_set_unit_ids", None), str) else np.nan,
            ))
    return pd.DataFrame(rows), pd.DataFrame(strata)


# --------------------------------------------------------------------------
# eps_stab core
# --------------------------------------------------------------------------
def window_eps(pi_tar, pi_opp, p_obs, q_use, n_obs, design_on: bool,
               force_a_ideal: bool = False, force_d_ideal: bool = False) -> dict:
    """eps_stab for one window, plus the per-client factors that drive it.

    ``force_a_ideal`` / ``force_d_ideal`` are decomposition switches used only
    by the Design-OFF attribution check; both default to False, i.e. the exact
    definition under audit.
    """
    pi_tar = np.asarray(pi_tar, dtype=np.float64)
    pi_opp = np.asarray(pi_opp, dtype=np.float64)
    p_obs = np.asarray(p_obs, dtype=np.float64)
    q_use = np.asarray(q_use, dtype=np.float64)
    n_obs = np.asarray(n_obs, dtype=np.float64)

    with np.errstate(divide="ignore", invalid="ignore"):
        if design_on:
            zeta_T = pi_tar / np.maximum(pi_opp, PI_MIN)
            zeta_s = pi_tar / pi_opp
        else:
            zeta_T = np.ones_like(pi_tar)
            zeta_s = np.ones_like(pi_tar)

        a_T = np.minimum(A_MAX, zeta_T / np.maximum(p_obs, P_MIN))
        a_s = zeta_s / p_obs
        d_T = np.minimum(D_MAX, 1.0 / np.maximum(q_use, Q_MIN))
        d_s = 1.0 / q_use

    if force_a_ideal:
        a_T = a_s
    if force_d_ideal:
        d_T = d_s

    b_T = n_obs * a_T * d_T
    b_s = n_obs * a_s * d_s

    if not np.all(np.isfinite(b_s)):
        return {"status": "UNDEFINED", "reason": "b_star not finite"}
    if not np.all(np.isfinite(b_T)):
        return {"status": "UNDEFINED", "reason": "b_T not finite"}

    sum_T = float(b_T.sum())
    sum_s = float(b_s.sum())
    if sum_T <= 0.0 or sum_s <= 0.0:
        return {
            "status": "UNDEFINED",
            "reason": "Hajek denominator is zero (sum b_T=%r, sum b_star=%r)"
                      % (sum_T, sum_s),
            "sum_b_T": sum_T, "sum_b_star": sum_s,
        }

    beta_T = b_T / sum_T
    beta_s = b_s / sum_s
    return {
        "status": "OK",
        "eps_stab": float(np.abs(beta_T - beta_s).sum()),
        "sum_b_T": sum_T, "sum_b_star": sum_s,
        "a_T": a_T, "a_star": a_s, "d_T": d_T, "d_star": d_s,
    }


def pct(x: float) -> float:
    return float(100.0 * x)


def load_active_set(reference_arm: str = "raven") -> dict:
    """Realized A_r per (dataset, seed, window) from window_metrics.json.

    ``active_clients`` is written by FullWindowRunner for every aggregation
    window and equals {k : U_k = 1 and m_k > 0}.  It is verified to be
    identical across all arms that write window_metrics.json (central_* use a
    different code path and write none), so the choice of arm is immaterial;
    ``reference_arm`` only names the file actually read.
    """
    rows = []
    arms_seen = set()
    disagreements = 0
    arm_sizes = {}
    frozen_activity = {}
    for ds in DATASETS:
        ds_dir = RUNS_ROOT / ds
        arms = sorted(p.name for p in ds_dir.iterdir() if p.is_dir()) if ds_dir.is_dir() else []
        n_nonempty = 0
        n_active_flag = 0
        n_activity_mismatch = 0
        for seed in SEEDS:
            ref = None
            ref_arm = None
            for arm in arms:
                path = ds_dir / arm / seed / "window_metrics.json"
                if not path.is_file():
                    continue
                with open(path, encoding="utf-8") as fh:
                    payload = json.load(fh)
                cur = {int(r["window_id"]): tuple(sorted(r["active_clients"]))
                       for r in payload}
                arm_sizes.setdefault(arm, []).append(sum(len(v) for v in cur.values()))
                arms_seen.add(arm)
                if ref is None:
                    ref, ref_arm = cur, arm
                elif cur != ref:
                    disagreements += 1
            if ref is None:
                continue
            for window, clients in sorted(ref.items()):
                for client in clients:
                    rows.append({"dataset": ds, "seed": seed, "window": window,
                                 "client": client})
            flag_path = ds_dir / reference_arm / seed / "window_metrics.json"
            if flag_path.is_file():
                with open(flag_path, encoding="utf-8") as fh:
                    flagged = {int(r["window_id"]): bool(r["active"])
                               for r in json.load(fh)}
                for window in flagged:
                    empty = len(ref.get(window, ())) == 0
                    n_nonempty += int(not empty)
                    n_active_flag += int(flagged[window])
                    if empty == flagged[window]:
                        n_activity_mismatch += 1
        frozen_activity[ds] = {
            "n_windows_nonempty_A_r": n_nonempty,
            "n_windows_active_true_in_logs": n_active_flag,
            "n_windows_where_they_disagree": n_activity_mismatch,
            "verdict": "PASS" if n_activity_mismatch == 0 else "FAIL",
        }
    frame = pd.DataFrame(rows)
    meta = {
        "source": ("artifacts/e3_formal_runs_r1/runs/<dataset>/<arm>/<seed>/"
                   "window_metrics.json : active_clients"),
        "definition": "A_r = {k : U_k = 1 and m_k > 0} (window_runner.py:466-469 of the run revision)",
        "reference_arm": reference_arm,
        "arms_seen": sorted(arms_seen),
        "n_arms": len(arms_seen),
        "cross_arm_disagreements_within_seed": disagreements,
        "arm_row_totals": {a: int(sum(v)) for a, v in sorted(arm_sizes.items())},
        "n_A_r_rows": int(len(frame)),
        "frozen_activity_check": frozen_activity,
        "note": ("identical across every arm that writes window_metrics.json "
                 "(verified per seed), so the arm choice does not affect any number"),
    }
    return {"frame": frame, "meta": meta}


def describe(values: np.ndarray) -> dict:
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        return {"n": 0}
    return {
        "n": int(v.size),
        "median": float(np.median(v)),
        "p95": float(np.percentile(v, 95)),
        "max": float(v.max()),
        "mean": float(v.mean()),
        "p99": float(np.percentile(v, 99)),
        "n_gt_0": int((v > 0).sum()),
        "frac_gt_0": float((v > 0).mean()),
        "n_gt_tol": int((v > EPS_TOL).sum()),
        "frac_gt_tol": float((v > EPS_TOL).mean()),
    }


# --------------------------------------------------------------------------
# sanity check 3: synthetic
# --------------------------------------------------------------------------
def synthetic_cases() -> dict:
    """Tiny windows exercising the inactive-bounds and failure-mode cases."""
    cases = {}

    def run(name, clients, design_on):
        df = pd.DataFrame(clients)
        out = window_eps(
            df["pi_tar"], df["pi_opp_true"], df["p_obs_true"],
            df["q_use_true"], df["n_obs"], design_on=design_on,
        )
        cases[name] = {
            "clients": clients,
            "design_on": design_on,
            "status": out["status"],
            "eps_stab": out.get("eps_stab"),
            "reason": out.get("reason"),
            "a_T": None if out["status"] != "OK" else [float(x) for x in out["a_T"]],
            "a_star": None if out["status"] != "OK" else [float(x) for x in out["a_star"]],
            "d_T": None if out["status"] != "OK" else [float(x) for x in out["d_T"]],
            "d_star": None if out["status"] != "OK" else [float(x) for x in out["d_star"]],
        }
        return cases[name]

    # --- all bounds inactive: p in [p_min, 1/a_max), q in (1/d_max, 1],
    #     zeta = pi_tar/pi_opp small enough that a never reaches a_max.
    benign = [
        dict(pi_tar=0.020, pi_opp_true=0.020, p_obs_true=0.50, q_use_true=0.80, n_obs=7),
        dict(pi_tar=0.005, pi_opp_true=0.010, p_obs_true=0.40, q_use_true=0.60, n_obs=3),
        dict(pi_tar=0.015, pi_opp_true=0.030, p_obs_true=0.25, q_use_true=0.20, n_obs=5),
    ]
    run("benign_design_on", benign, True)
    run("benign_design_off", benign, False)

    # --- failure mode 1: p_obs_true below p_min
    run("fail_p_below_p_min", [
        dict(pi_tar=0.020, pi_opp_true=0.020, p_obs_true=0.02, q_use_true=0.80, n_obs=7),
        dict(pi_tar=0.005, pi_opp_true=0.010, p_obs_true=0.40, q_use_true=0.60, n_obs=3),
    ], True)

    # --- failure mode 2: q_use_true below q_min
    run("fail_q_below_q_min", [
        dict(pi_tar=0.020, pi_opp_true=0.020, p_obs_true=0.50, q_use_true=0.02, n_obs=7),
        dict(pi_tar=0.005, pi_opp_true=0.010, p_obs_true=0.40, q_use_true=0.60, n_obs=3),
    ], True)

    # --- failure mode 3a: a_max ceiling hit, floors inactive
    #     (p=0.30 >= p_min, pi_tar/pi_opp = 10 -> a_star = 33.33 > a_max = 20)
    run("fail_a_max_ceiling", [
        dict(pi_tar=0.300, pi_opp_true=0.030, p_obs_true=0.30, q_use_true=0.80, n_obs=7),
        dict(pi_tar=0.005, pi_opp_true=0.010, p_obs_true=0.40, q_use_true=0.60, n_obs=3),
    ], True)

    # --- failure mode 3b: d_max ceiling hit, floors inactive
    #     (q=0.08 >= q_min, 1/q = 12.5 > d_max = 10)
    run("fail_d_max_ceiling", [
        dict(pi_tar=0.020, pi_opp_true=0.020, p_obs_true=0.50, q_use_true=0.08, n_obs=7),
        dict(pi_tar=0.005, pi_opp_true=0.010, p_obs_true=0.40, q_use_true=0.60, n_obs=3),
    ], True)

    return cases


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "audit": "eps_stab",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
    }

    # ---- inputs ---------------------------------------------------------
    inputs = {}
    for label, path in (
        ("audit_records_csv", AUDIT_CSV),
        ("sensorscope_client_mapping_yaml", SS_CLIENT_YAML),
    ):
        inputs[label] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    for ds in DATASETS:
        p = ROOT / "data" / "processed" / ds / "atomic_units.parquet"
        inputs["atomic_units_%s" % ds] = {
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(p), "bytes": p.stat().st_size,
        }
    trace_files = []
    for ds in DATASETS:
        for seed in SEEDS:
            f = TRACE_ROOT / ds / seed / "training_eventtrace" / "events.parquet"
            trace_files.append((ds, seed, f))
    inputs["eventtrace_files"] = {
        "pattern": "artifacts/e3_formal_runs_r1/eventtraces/<dataset>/<seed>/training_eventtrace/events.parquet",
        "n_files": len(trace_files),
        "n_present": sum(1 for _, _, f in trace_files if f.is_file()),
    }
    inputs["run_revision_window_runner"] = {
        "note": ("run-time revision of src/raven_mcs/training/window_runner.py "
                 "(sha256 f7bff5e3...) recovered verbatim at this path; it is the "
                 "file recorded as method_source_hash in the frozen run ledgers"),
        "path": ("artifacts/e4_wo_inst_reference_penalty_final_correction_r1/"
                 "recovered_source/window_runner.py"),
        "sha256": sha256_file(
            ROOT / "artifacts" / "e4_wo_inst_reference_penalty_final_correction_r1"
            / "recovered_source" / "window_runner.py"
        ),
    }
    report["inputs"] = inputs
    report["constants"] = {
        "a_max": A_MAX, "p_min": P_MIN, "pi_min": PI_MIN,
        "d_max": D_MAX, "q_min": Q_MIN,
        "theta_align": THETA_ALIGN, "tail_blocks": sorted(TAIL_BLOCKS),
        "pi_target_mode": PI_TARGET_MODE,
        "n_obs_definition": "len(observed_unit_ids) from the frozen EventTrace",
        "active_client_definition": "client-window with n_obs > 0 (O true)",
    }

    # ---- targets --------------------------------------------------------
    targets = {ds: dataset_targets(ds) for ds in DATASETS}
    for ds in DATASETS:
        report.setdefault("pi_target_resolution", {})[ds] = {
            "mode": PI_TARGET_MODE,
            "n_client_stratum_pairs": len(targets[ds]["pi_tar"]),
            "n_zero_pairs": int(sum(1 for v in targets[ds]["pi_tar"].values() if v == 0.0)),
            "sum_pi_tar": float(sum(targets[ds]["pi_tar"].values())),
            "n_pi_opp_pairs": len(targets[ds]["pi_opp_joint"]),
            "n_clients": len(targets[ds]["strata_by_client"]),
        }

    # ---- verification of reconstruction against frozen artifacts --------
    verification: dict = {}
    for ds in DATASETS:
        pi_opp = targets[ds]["pi_opp_joint"]
        pi_tar = targets[ds]["pi_tar"]
        n_ev = n_opp_mismatch = n_opp_missing = 0
        max_opp_diff = 0.0
        n_tar_zero = 0
        n_tar_missing = 0
        for seed in SEEDS:
            f = TRACE_ROOT / ds / seed / "training_eventtrace" / "events.parquet"
            df = pd.read_parquet(f, columns=["client_id", "opportunity_features"])
            for r in df.itertuples(index=False):
                of = r.opportunity_features
                j = json.loads(of) if isinstance(of, str) else dict(of)
                key = (str(r.client_id), str(j.get("opportunity_stratum")))
                n_ev += 1
                exp = pi_opp.get(key)
                if exp is None:
                    n_opp_missing += 1
                else:
                    d = abs(exp - float(j["pi_opp_true"]))
                    max_opp_diff = max(max_opp_diff, d)
                    if d > 1e-15:
                        n_opp_mismatch += 1
                if key in pi_tar:
                    if pi_tar[key] == 0.0:
                        n_tar_zero += 1
                else:
                    n_tar_missing += 1

        # independent cross-check of pi_tar against the frozen per-run state
        n_rows = n_unresolved = n_state_files = n_state_files_skipped = 0
        max_tar_diff = 0.0
        need_cols = ("client_id", "opportunity_stratum_id", "target_client_stratum_mass")
        for method_dir in sorted((RUNS_ROOT / ds).iterdir()) if (RUNS_ROOT / ds).is_dir() else []:
            if not method_dir.is_dir():
                continue
            for seed_dir in sorted(method_dir.glob("seed*")):
                state = seed_dir / "delta_cs_state_v6.parquet"
                if not state.is_file():
                    continue
                import pyarrow.parquet as pq
                names = set(pq.read_schema(state).names)
                if not set(need_cols).issubset(names):
                    n_state_files_skipped += 1
                    continue
                n_state_files += 1
                d = pd.read_parquet(
                    state,
                    columns=["client_id", "opportunity_stratum_id",
                             "target_client_stratum_mass"],
                ).drop_duplicates()
                for r in d.itertuples(index=False):
                    key = (str(r.client_id), str(r.opportunity_stratum_id))
                    val = pi_tar.get(key)
                    n_rows += 1
                    if val is None:
                        n_unresolved += 1
                    else:
                        max_tar_diff = max(max_tar_diff,
                                           abs(val - float(r.target_client_stratum_mass)))
        verification[ds] = {
            "pi_opp_vs_frozen_trace": {
                "n_events": n_ev, "n_missing_key": n_opp_missing,
                "n_mismatch_gt_1e-15": n_opp_mismatch,
                "max_abs_diff": max_opp_diff,
                "verdict": "PASS" if (n_opp_mismatch == 0 and n_opp_missing == 0) else "FAIL",
            },
            "pi_tar_vs_frozen_delta_cs_state": {
                "n_rows_checked": n_rows, "n_unresolved": n_unresolved,
                "n_state_files_used": n_state_files,
                "n_state_files_skipped_no_column": n_state_files_skipped,
                "max_abs_diff": max_tar_diff,
                "verdict": "PASS" if (n_unresolved == 0 and max_tar_diff == 0.0) else "FAIL",
            },
            "events_with_zero_pi_tar": {
                "n": n_tar_zero, "n_events": n_ev,
                "share_pct": pct(n_tar_zero / n_ev) if n_ev else None,
                "n_key_missing_from_pi_tar_support": n_tar_missing,
            },
        }
    report["verification"] = verification

    # ---- audit CSV + re-harvest ----------------------------------------
    csv = pd.read_csv(AUDIT_CSV)
    csv["O"] = csv["O"].astype(bool)
    csv["U"] = csv["U"].astype(bool)
    csv["client"] = csv["client"].astype(str)
    csv["dataset"] = csv["dataset"].astype(str)
    csv["seed"] = csv["seed"].astype(str)

    reharvest_frames = []
    strata_frames = []
    for ds in DATASETS:
        r, s = harvest(ds)
        reharvest_frames.append(r)
        strata_frames.append(s)
    reharvest = pd.concat(reharvest_frames, ignore_index=True)
    strata = pd.concat(strata_frames, ignore_index=True)

    key = ["dataset", "seed", "window", "client"]
    merged = reharvest.merge(
        csv[key + ["pi_opp_true", "p_obs_true", "q_use_true", "n_obs", "O", "U"]],
        on=key, how="outer", suffixes=("_re", "_csv"), indicator=True,
    )
    margins = ["pi_opp_true", "p_obs_true", "q_use_true"]
    only_re = int((merged["_merge"] == "left_only").sum())
    only_csv = int((merged["_merge"] == "right_only").sum())
    margin_mismatch = {}
    for m in margins:
        a = merged["%s_re" % m].to_numpy(dtype=float)
        b = merged["%s_csv" % m].to_numpy(dtype=float)
        both = np.isfinite(a) & np.isfinite(b)
        margin_mismatch[m] = {
            "n_compared": int(both.sum()),
            "n_diff_gt_1e-12": int((np.abs(a[both] - b[both]) > 1e-12).sum()),
            "max_abs_diff": float(np.abs(a[both] - b[both]).max()) if both.any() else None,
        }
    nobs_diff = int((merged["n_obs_re"].fillna(-1) != merged["n_obs_csv"].fillna(-1)).sum())
    o_diff = int((merged["O_re"].fillna(False) != merged["O_csv"].fillna(False)).sum())
    report["reharvest_verification"] = {
        "csv_rows": int(len(csv)),
        "reharvest_rows": int(len(reharvest)),
        "rows_only_in_reharvest": only_re,
        "rows_only_in_csv": only_csv,
        "margin_mismatches": margin_mismatch,
        "n_obs_mismatches": nobs_diff,
        "O_mismatches": o_diff,
        "verdict": "PASS" if (
            only_re == 0 and only_csv == 0 and nobs_diff == 0 and o_diff == 0
            and all(v["n_diff_gt_1e-12"] == 0 for v in margin_mismatch.values())
        ) else "FAIL",
    }

    # ---- attach stratum + pi_tar to the audit rows ----------------------
    audit = csv.merge(strata, on=["dataset", "seed", "window", "client"], how="left")
    assert len(audit) == len(csv), "stratum join changed the row count"
    n_missing_stratum = int(audit["opportunity_stratum"].isna().sum())
    audit["pi_tar"] = [
        targets[ds]["pi_tar"].get((c, s), np.nan)
        for ds, c, s in zip(audit["dataset"], audit["client"], audit["opportunity_stratum"])
    ]
    n_missing_tar = int(audit["pi_tar"].isna().sum())

    # ---- realized active set A_r from the frozen run logs ----------------
    ar = load_active_set()
    report["active_set_Ar"] = ar["meta"]
    ar_keys = set(map(tuple, ar["frame"][["dataset", "seed", "window", "client"]].values))
    audit["in_A_r"] = pd.Series(
        [(d, s, int(w), c) in ar_keys
         for d, s, w, c in zip(audit["dataset"], audit["seed"],
                               audit["window"], audit["client"])],
        index=audit.index, dtype=bool,
    )

    # ---- sanity check 1: reproduce known audit readings -----------------
    # The three quoted readings come from two different normalisations of the
    # same q_use_true distribution; both are reproduced here and labelled.
    #   * q_min floor        -> among OBSERVED client-windows (O true)
    #   * q < 1/d_max        -> the task's figure 24.22/23.75 is the OBSERVED
    #                           (O true) share; the shipped
    #                           artifacts/a5_a6_audit/audit_summary.csv P5b row
    #                           reports the ALL-records share (41.52/41.86),
    #                           which counts the structurally-zero q of
    #                           inactive client-windows.
    known = {"sensorscope": {"q_floor_pct": 5.22, "q_below_dmax_pct": 24.22, "min_p": 0.1925},
             "uair": {"q_floor_pct": 5.18, "q_below_dmax_pct": 23.75, "min_p": 0.1925}}
    sc1 = {}
    for ds in DATASETS:
        t = audit[audit["dataset"] == ds]
        obs = t[t["O"]]
        qu = t["q_use_true"].dropna()
        q_floor = pct(float((obs["q_use_true"] < Q_MIN).mean()))
        q_below_obs = pct(float((obs["q_use_true"] < 1.0 / D_MAX).mean()))
        q_below_all = pct(float((qu < 1.0 / D_MAX).mean()))
        q_below_pos = pct(float((qu[qu > 0] < 1.0 / D_MAX).mean()))
        min_p = float(t["p_obs_true"].dropna().min())
        sc1[ds] = {
            "q_min_floor_active_pct_observed": q_floor,
            "q_min_floor_active_pct_claimed": known[ds]["q_floor_pct"],
            "q_min_floor_active_pass": abs(q_floor - known[ds]["q_floor_pct"]) <= 0.005,
            "q_below_inv_d_max_pct_observed": q_below_obs,
            "q_below_inv_d_max_pct_claimed": known[ds]["q_below_dmax_pct"],
            "q_below_inv_d_max_pass": abs(q_below_obs - known[ds]["q_below_dmax_pct"]) <= 0.005,
            "q_below_inv_d_max_pct_all_records": q_below_all,
            "q_below_inv_d_max_pct_records_with_q_positive": q_below_pos,
            "audit_summary_csv_P5b_reading_pct": 41.52 if ds == "sensorscope" else 41.86,
            "min_p_obs_true": min_p,
            "min_p_obs_true_claimed": known[ds]["min_p"],
            "min_p_obs_true_pass": abs(min_p - known[ds]["min_p"]) < 1e-12,
            "note": ("q<1/d_max is reported both among OBSERVED client-windows "
                     "(matches the quoted 24.22/23.75) and over ALL harvested "
                     "records (matches audit_summary.csv P5b = 41.52/41.86). "
                     "The two differ because inactive client-windows carry the "
                     "structural q_use_true = 0."),
        }
        sc1[ds]["verdict"] = "PASS" if (
            sc1[ds]["q_min_floor_active_pass"] and sc1[ds]["q_below_inv_d_max_pass"]
            and sc1[ds]["min_p_obs_true_pass"]
        ) else "FAIL"
    report["sanity_check_1_known_readings"] = sc1

    # ---- sanity check 2: Design OFF a-side can never clip ---------------
    sc2 = {}
    for ds in DATASETS:
        t = audit[audit["dataset"] == ds]
        inv_p = (1.0 / t["p_obs_true"].to_numpy(dtype=float))
        act = t[t["O"]]
        act_inv_p = (1.0 / act["p_obs_true"].to_numpy(dtype=float))
        sc2[ds] = {
            "a_max": A_MAX,
            "max_over_all_client_windows_of_1_over_p_obs_true": float(inv_p.max()),
            "max_over_active_client_windows_of_1_over_p_obs_true": float(act_inv_p.max()),
            "clause_is_below_a_max": bool(inv_p.max() < A_MAX),
            "n_client_windows_with_1_over_p_gt_a_max": int((inv_p > A_MAX).sum()),
            "a_side_clips_in_design_off": bool((inv_p > A_MAX).any()),
        }
    report["sanity_check_2_design_off_a_side"] = sc2

    # ---- sanity check 3: synthetic --------------------------------------
    report["sanity_check_3_synthetic"] = synthetic_cases()

    # ---- main results ---------------------------------------------------
    results: dict = {}
    window_rows = []
    for ds in DATASETS:
        t = audit[audit["dataset"] == ds]
        results[ds] = {}
        for vname, vmask in ACTIVE_SET_VARIANTS.items():
            results[ds][vname] = {}
            for design_on in (True, False):
                label = "design_on" if design_on else "design_off"
                eps_vals = []
                a_only, d_only, full = [], [], []
                n_windows_total = 0
                n_windows_active = 0
                undefined = []
                for (seed, window), g in t.groupby(["seed", "window"], sort=True):
                    n_windows_total += 1
                    act = vmask(g)
                    if act.empty:
                        continue
                    n_windows_active += 1
                    args = (
                        act["pi_tar"].to_numpy(float),
                        act["pi_opp_true"].to_numpy(float),
                        act["p_obs_true"].to_numpy(float),
                        act["q_use_true"].to_numpy(float),
                        act["n_obs"].to_numpy(float),
                    )
                    out = window_eps(*args, design_on=design_on)
                    if out["status"] != "OK":
                        undefined.append({"seed": seed, "window": int(window),
                                          "reason": out["reason"]})
                        continue
                    eps_vals.append(out["eps_stab"])
                    decomposition = False
                    if vname == "O_n_obs_gt_0" and not design_on:
                        # attribution switches, diagnostics only
                        oa = window_eps(*args, design_on=design_on, force_d_ideal=True)
                        od = window_eps(*args, design_on=design_on, force_a_ideal=True)
                        if oa["status"] == "OK" and od["status"] == "OK":
                            a_only.append(oa["eps_stab"])
                            d_only.append(od["eps_stab"])
                            full.append(out["eps_stab"])
                            decomposition = True
                    window_rows.append({
                        "dataset": ds, "seed": seed, "window": int(window),
                        "variant": vname, "design": label,
                        "n_active": int(len(act)),
                        "eps_stab": out["eps_stab"],
                    })
                vals = np.asarray(eps_vals, dtype=np.float64)
                entry = {
                    "n_windows_in_trace": n_windows_total,
                    "n_windows_with_active_clients": n_windows_active,
                    "n_windows_used": int(vals.size),
                    "n_windows_undefined": len(undefined),
                    "undefined_reasons": sorted({u["reason"] for u in undefined}),
                    "eps_stab": describe(vals),
                    "median": float(np.median(vals)) if vals.size else None,
                    "p95": float(np.percentile(vals, 95)) if vals.size else None,
                    "max": float(vals.max()) if vals.size else None,
                    "frac_windows_eps_gt_0": float((vals > 0).mean()) if vals.size else None,
                    "frac_windows_eps_gt_1e-12": float((vals > EPS_TOL).mean()) if vals.size else None,
                }
                if decomposition and full:
                    entry["design_off_attribution"] = {
                        "note": ("a-side-only eps (d forced ideal) isolates the "
                                 "numerator term; d-side-only eps (a forced ideal) "
                                 "isolates the q term"),
                        "max_eps_with_a_side_only": float(np.max(a_only)),
                        "max_eps_with_d_side_only": float(np.max(d_only)),
                        "max_abs_diff_d_side_only_vs_full": float(
                            np.max(np.abs(np.asarray(d_only) - np.asarray(full)))),
                        "n_windows": int(len(full)),
                    }
                results[ds][vname][label] = entry

        # a-side clause maxima (Design ON and Design OFF clauses)
        t_act = t[t["O"]]
        clause_on = (t["pi_tar"] / (t["pi_opp_true"] * t["p_obs_true"])).to_numpy(float)
        clause_off = (1.0 / t["p_obs_true"]).to_numpy(float)
        clause_on_act = (t_act["pi_tar"] / (t_act["pi_opp_true"] * t_act["p_obs_true"])).to_numpy(float)
        clause_off_act = (1.0 / t_act["p_obs_true"]).to_numpy(float)
        # exact floored quantity that actually decides clipping (Design ON):
        #   a_T = min(a_max, zeta_T / max(p_obs, p_min)),
        #   zeta_T = pi_tar / max(pi_opp, pi_min)
        zeta_T = t["pi_tar"].to_numpy(float) / np.maximum(t["pi_opp_true"].to_numpy(float), PI_MIN)
        a_raw_on = zeta_T / np.maximum(t["p_obs_true"].to_numpy(float), P_MIN)
        t_ar = t[t["O"] & t["in_A_r"]]
        clause_on_ar = (t_ar["pi_tar"] / (t_ar["pi_opp_true"] * t_ar["p_obs_true"])).to_numpy(float)
        clause_off_ar = (1.0 / t_ar["p_obs_true"]).to_numpy(float)
        results[ds]["a_side_clauses"] = {
            "a_max": A_MAX,
            "design_on_clause_pi_tar_over_pi_opp_p_obs_max": float(clause_on.max()),
            "design_on_clause_max_active_only": float(clause_on_act.max()),
            "design_on_clause_max_A_r_only": float(clause_on_ar.max()),
            "design_on_clause_n_clipping_against_a_max": int((clause_on > A_MAX).sum()),
            "design_on_clause_n_clipping_active_only": int((clause_on_act > A_MAX).sum()),
            "design_on_clause_n_clipping_A_r_only": int((clause_on_ar > A_MAX).sum()),
            "design_on_clause_share_clipping_A_r_only": float((clause_on_ar > A_MAX).mean()),
            "design_on_clause_below_a_max": bool(clause_on.max() < A_MAX),
            "design_off_clause_1_over_p_obs_max": float(clause_off.max()),
            "design_off_clause_max_active_only": float(clause_off_act.max()),
            "design_off_clause_max_A_r_only": float(clause_off_ar.max()),
            "design_off_clause_n_clipping_against_a_max": int((clause_off > A_MAX).sum()),
            "design_off_clause_n_clipping_A_r_only": int((clause_off_ar > A_MAX).sum()),
            "design_off_clause_below_a_max": bool(clause_off.max() < A_MAX),
            "diagnostic_design_on_floored_a_T_max": float(a_raw_on.max()),
            "diagnostic_design_on_n_floored_a_T_clipped": int((a_raw_on > A_MAX).sum()),
        }

    report["results"] = results

    # ---- internal consistency of the definition --------------------------
    # eps_stab compares NORMALISED shares, so it is invariant to any clipping
    # that is proportional across the window's active clients.  In particular
    # a window with a single active client always has beta_T = beta_star = [1]
    # and therefore eps_stab = 0 whatever the bounds do.  The claims below are
    # the falsifiable part of that structure.
    consistency = {}
    for ds in DATASETS:
        t = audit[audit["dataset"] == ds]
        rows_ds = [r for r in window_rows
                   if r["dataset"] == ds and r["variant"] == "A_r_frozen"]
        for label in ("design_on", "design_off"):
            flagged = {(r["seed"], r["window"]) for r in rows_ds if r["design"] == label
                       and r["eps_stab"] > 0}
            biting_pos, biting_any, single, single_flagged = set(), set(), set(), set()
            for (seed, window), g in t.groupby(["seed", "window"], sort=True):
                act = g[g["O"] & g["in_A_r"]]
                if act.empty:
                    continue
                key = (seed, window)
                if len(act) == 1:
                    single.add(key)
                    if key in flagged:
                        single_flagged.add(key)
                if label == "design_on":
                    z = act["pi_tar"] / np.maximum(act["pi_opp_true"], PI_MIN)
                    a_clip = (z / np.maximum(act["p_obs_true"], P_MIN) > A_MAX)
                else:
                    a_clip = pd.Series(False, index=act.index)
                q_clip = act["q_use_true"] < 1.0 / D_MAX
                bites = (a_clip | q_clip).to_numpy(dtype=bool)
                if bites.any():
                    biting_any.add(key)
                if (bites & (act["pi_tar"].to_numpy(float) > 0.0)).any():
                    biting_pos.add(key)
            only_bite = biting_any - flagged
            consistency.setdefault(ds, {})[label] = {
                "n_windows_used": len(rows_ds),
                "n_windows_eps_gt_0": len(flagged),
                "C1_single_active_client_has_eps_0": {
                    "n_single_client_windows": len(single),
                    "n_of_those_with_eps_gt_0": len(single_flagged),
                    "verdict": "PASS" if not single_flagged else "FAIL",
                },
                "C2_eps_gt_0_implies_a_bound_bites": {
                    "n_eps_gt_0_without_any_biting_bound": len(flagged - biting_any),
                    "verdict": "PASS" if not (flagged - biting_any) else "FAIL",
                },
                "C3_bound_bites_but_eps_is_0": {
                    "n_windows": len(only_bite),
                    "n_of_those_single_client": len(only_bite & single),
                    "n_of_those_biting_only_through_pi_tar_0_clients":
                        len(only_bite - single - biting_pos),
                    "note": ("expected: proportional clipping cancels in the "
                             "Hajek normalisation; a biting client with "
                             "pi_tar = 0 has b = 0 on BOTH sides (U-Air only)"),
                },
            }
    report["internal_consistency_of_definition"] = consistency

    # Design-OFF q-side-only decomposition check
    off_check = {}
    for ds in DATASETS:
        sub = [r for r in window_rows
               if r["dataset"] == ds and r["design"] == "design_off"
               and r["variant"] == "O_n_obs_gt_0"]
        vals = np.asarray([r["eps_stab"] for r in sub], dtype=np.float64)
        off_check[ds] = {
            "n_windows": int(vals.size),
            "max_eps_stab": float(vals.max()) if vals.size else None,
            "median_eps_stab": float(np.median(vals)) if vals.size else None,
            "frac_gt_0": float((vals > 0).mean()) if vals.size else None,
            "a_side_never_clips": results[ds]["a_side_clauses"]["design_off_clause_below_a_max"],
        }
    report["design_off_q_side_only"] = off_check

    # supplementary counts / caveats
    report["supporting_counts"] = {}
    for ds in DATASETS:
        t = audit[audit["dataset"] == ds]
        act = t[t["O"]]
        report["supporting_counts"][ds] = {
            "n_client_windows": int(len(t)),
            "n_active_client_windows": int(len(act)),
            "n_active_and_U_true": int((act["U"]).sum()),
            "n_active_and_U_false": int((~act["U"]).sum()),
            "n_active_with_pi_tar_zero": int((act["pi_tar"] == 0.0).sum()),
            "n_active_with_zero_b_T": int((
                act["pi_tar"] == 0.0).sum()),
            "n_active_with_q_use_true_below_q_min": int((act["q_use_true"] < Q_MIN).sum()),
            "n_active_with_1_over_q_above_d_max": int((1.0 / act["q_use_true"] > D_MAX).sum()),
            "n_active_with_p_below_p_min": int((act["p_obs_true"] < P_MIN).sum()),
            "min_pi_opp_true_all": float(t["pi_opp_true"].min()),
            "n_events_with_stratum_key_missing_from_pi_tar": n_missing_tar,
            "n_rows_with_missing_stratum": n_missing_stratum,
            "n_obs_min_active": int(act["n_obs"].min()),
            "n_obs_median_active": float(act["n_obs"].median()),
        }

    # per-window long table
    pd.DataFrame(window_rows).to_csv(OUT_DIR / "eps_stab_windows.csv", index=False)
    report["per_window_table"] = "results_prop3_audit/round_v1/eps_stab_windows.csv"

    with open(OUT_DIR / "EPS_STAB.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=False, default=str)

    # ---- console summary ------------------------------------------------
    print("=" * 78)
    print("eps_stab audit -- finished", report["generated_utc"])
    print("=" * 78)
    print("audit CSV sha256:", inputs["audit_records_csv"]["sha256"])
    print()
    print("reharvest verification:",
          report["reharvest_verification"]["verdict"],
          {k: v["n_diff_gt_1e-12"] for k, v in margin_mismatch.items()},
          "n_obs mismatches:", nobs_diff)
    for ds in DATASETS:
        print("  %-12s pi_opp %s (max|d|=%.3g, %d events), pi_tar vs state %s (max|d|=%.3g)"
              % (ds,
                 verification[ds]["pi_opp_vs_frozen_trace"]["verdict"],
                 verification[ds]["pi_opp_vs_frozen_trace"]["max_abs_diff"],
                 verification[ds]["pi_opp_vs_frozen_trace"]["n_events"],
                 verification[ds]["pi_tar_vs_frozen_delta_cs_state"]["verdict"],
                 verification[ds]["pi_tar_vs_frozen_delta_cs_state"]["max_abs_diff"]))
    print()
    print("sanity check 1 (known readings):")
    for ds in DATASETS:
        s = sc1[ds]
        print("  %-12s q_floor %.2f%% (claim %.2f) %s | q<1/d_max observed %.2f%% "
              "(claim %.2f) %s | min p %.6g %s -> %s"
              % (ds, s["q_min_floor_active_pct_observed"], s["q_min_floor_active_pct_claimed"],
                 "OK" if s["q_min_floor_active_pass"] else "MISMATCH",
                 s["q_below_inv_d_max_pct_observed"], s["q_below_inv_d_max_pct_claimed"],
                 "OK" if s["q_below_inv_d_max_pass"] else "MISMATCH",
                 s["min_p_obs_true"], "OK" if s["min_p_obs_true_pass"] else "MISMATCH",
                 s["verdict"]))
        print("               (all-records reading = %.2f%%; audit_summary.csv P5b = %.2f%%)"
              % (s["q_below_inv_d_max_pct_all_records"],
                 s["audit_summary_csv_P5b_reading_pct"]))
    print()
    print("sanity check 2 (Design OFF a-side):")
    for ds in DATASETS:
        s = sc2[ds]
        print("  %-12s max 1/p = %.6f < a_max = %.1f : %s (n clipping = %d)"
              % (ds, s["max_over_active_client_windows_of_1_over_p_obs_true"], A_MAX,
                 s["clause_is_below_a_max"], s["n_client_windows_with_1_over_p_gt_a_max"]))
    print()
    print("sanity check 3 (synthetic):")
    for name, c in report["sanity_check_3_synthetic"].items():
        print("  %-24s eps = %s  (%s)" % (name, c["eps_stab"], c["status"]))
    print()
    print("A_r source:", report["active_set_Ar"]["reference_arm"],
          "arms:", report["active_set_Ar"]["n_arms"],
          "rows:", report["active_set_Ar"]["n_A_r_rows"],
          "cross-arm disagreements:", report["active_set_Ar"]["cross_arm_disagreements_within_seed"])
    for ds in DATASETS:
        fa = report["active_set_Ar"]["frozen_activity_check"][ds]
        print("  %-12s A_r non-empty %d windows vs frozen active=true %d -> %s"
              % (ds, fa["n_windows_nonempty_A_r"], fa["n_windows_active_true_in_logs"],
                 fa["verdict"]))
    for ds in DATASETS:
        for label, c in consistency[ds].items():
            print("  %-12s %-11s eps>0 %4d | C1 single-client eps=0: %s (%d single, %d bad)"
                  " | C2: %s | C3 cancelled-but-biting: %d (single %d, pi_tar=0 %d)"
                  % (ds, label, c["n_windows_eps_gt_0"],
                     c["C1_single_active_client_has_eps_0"]["verdict"],
                     c["C1_single_active_client_has_eps_0"]["n_single_client_windows"],
                     c["C1_single_active_client_has_eps_0"]["n_of_those_with_eps_gt_0"],
                     c["C2_eps_gt_0_implies_a_bound_bites"]["verdict"],
                     c["C3_bound_bites_but_eps_is_0"]["n_windows"],
                     c["C3_bound_bites_but_eps_is_0"]["n_of_those_single_client"],
                     c["C3_bound_bites_but_eps_is_0"][
                         "n_of_those_biting_only_through_pi_tar_0_clients"]))
    print()
    print("RESULTS  (rows = active-set variant x Design setting)")
    for ds in DATASETS:
        for vname in ACTIVE_SET_VARIANTS:
            for label in ("design_on", "design_off"):
                e = results[ds][vname][label]
                print("  %-12s %-14s %-11s win used %5d / active %5d  median %.6g  p95 %.6g"
                      "  max %.6g  frac>0 %.4f  frac>1e-12 %.4f  undef %d"
                      % (ds, vname, label, e["n_windows_used"],
                         e["n_windows_with_active_clients"], e["median"], e["p95"],
                         e["max"], e["frac_windows_eps_gt_0"],
                         e["frac_windows_eps_gt_1e-12"], e["n_windows_undefined"]))
        a = results[ds]["a_side_clauses"]
        print("     a-side  ON max(pi_tar/(pi_opp*p)) = %.6g  (a_max=%.1f, n clip %d, active-only %d)"
              % (a["design_on_clause_pi_tar_over_pi_opp_p_obs_max"], A_MAX,
                 a["design_on_clause_n_clipping_against_a_max"],
                 a["design_on_clause_n_clipping_active_only"]))
        print("     a-side OFF max(1/p)               = %.6g  (a_max=%.1f, n clip %d)"
              % (a["design_off_clause_1_over_p_obs_max"], A_MAX,
                 a["design_off_clause_n_clipping_against_a_max"]))
    print()
    dcheck = report["results"]["sensorscope"]["O_n_obs_gt_0"]["design_off"].get(
        "design_off_attribution")
    if dcheck:
        print("Design OFF attribution (SensorScope):",
              json.dumps(dcheck, indent=1))
    print()
    print("wrote:", OUT_DIR / "EPS_STAB.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
