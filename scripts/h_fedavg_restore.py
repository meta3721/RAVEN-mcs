"""h_fedavg_restore.py -- restore U-Air FedAvg to the frozen active set, then recompute H.

Rule R (pre-registered in the round's instruction): for fedavg_window only, a client-window whose
(opportunity_stratum, unit) has pi_tar = 0 is not in A_r. Implemented by copying the EventTrace the
H round used and setting U = 0 on those event rows. src/ is not edited; no trace is regenerated.

    python scripts/h_fedavg_restore.py --stage-b          # seeds 30001 and 30006, then the rest
    python scripts/h_fedavg_restore.py --gate-only        # the first two seeds only
    python scripts/h_fedavg_restore.py --stage-c          # C1-C5 FedAvg
    python scripts/h_fedavg_restore.py --tables           # H summary + H_DECISION.json
"""
from __future__ import annotations

import argparse, json, os, pathlib, shutil, sys, time
import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))

import run_h_headroom as H                                              # noqa: E402
from raven_mcs.correction.pi_target import build_pi_target               # noqa: E402
from raven_mcs.e3.canary.dataset_load import (                          # noqa: E402
    load_paper_dataset, load_spatial_to_client)
from raven_mcs.e3.real_runner import runner as e3runner                 # noqa: E402
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402
from raven_mcs.simulation.event_trace import load_event_trace           # noqa: E402

OUT = ROOT / "results_h_headroom" / "round_v2"
E3T = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces" / "uair"
V1T = ROOT / "results_h_headroom" / "round_v1" / "eventtraces"
U1T = ROOT / "results_h_headroom" / "round_u1" / "eventtraces"
FROZEN = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs" / "uair" / "fedavg_window"
ARMS = ("raven_simoracle", "raven_simoracle_nodesign")
CONDITIONS = {
    "C0_frozen":        dict(theta=1.25, tail=0.55, model="full",           target="test_share"),
    "C1_tilt_strong":   dict(theta=2.5,  tail=0.25, model="full",           target="test_share"),
    "C2_tilt_extreme":  dict(theta=4.0,  tail=0.10, model="full",           target="test_share"),
    "C3_low_capacity":  dict(theta=1.25, tail=0.55, model="diurnal_blind",  target="test_share"),
    "C4_block_uniform": dict(theta=1.25, tail=0.55, model="full",           target="block_uniform"),
    "C5_combined":      dict(theta=4.0,  tail=0.10, model="diurnal_blind",  target="block_uniform"),
}
STAGE_B_FIRST = (30001, 30006)
ALL_SEEDS = list(range(30001, 30021))
TOL = 1e-9
_PI = {}


def pi_target_for(dataset: str = "uair") -> dict:
    """Rule R reads the pi_tar the run actually uses: C0/C3 test split, C4/C5 rescaled."""
    if "tar" not in _PI:
        ds = load_paper_dataset(ROOT, dataset)
        mapping = load_spatial_to_client(ROOT, dataset)
        atomic, _ = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset, root=ROOT)
        frame = atomic.copy()
        frame["target_group_main"] = frame["target_group"].astype(str)
        pi = build_pi_target(frame, mapping, split="test")
        _PI["tar"] = {(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
                      for r in pi.itertuples()}
        _PI["ds"] = ds
        _PI["mapping"] = mapping
    return _PI["tar"]


def target_override(cond: str):
    if CONDITIONS[cond]["target"] != "block_uniform":
        return None
    _, factor = H.block_uniform_target("uair", _PI["ds"], _PI["mapping"])
    pi = pi_target_for()
    out = {k: v * factor[H._block_of(k[1])] for k, v in pi.items()}
    return out


def make_filtered_trace(cond: str, seed: int) -> pathlib.Path:
    """Copy the trace the H round used and zero U where the run's pi_tar is 0."""
    src = (E3T / f"seed{seed}" if cond in ("C0_frozen", "C3_low_capacity", "C4_block_uniform")
           else (V1T if seed <= 30005 else U1T) / cond / "uair" / f"seed{seed}") / "training_eventtrace"
    dst = OUT / "eventtraces" / cond / "uair" / f"seed{seed}" / "training_eventtrace"
    if not src.is_dir():
        raise SystemExit("STOP: source trace missing: %s" % src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_dir():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    pi = target_override(cond) or pi_target_for()
    ev = pd.read_parquet(dst / "events.parquet")
    key = ev["client_id"].astype(str) + "|" + ev["opportunity_features"].map(
        lambda d: str((d if isinstance(d, dict) else json.loads(d)).get("opportunity_stratum")))
    zero = key.map(lambda k: pi.get(tuple(k.split("|")), 0.0) == 0.0).to_numpy()
    n_before = int((ev["U"].astype(float) > 0).sum())
    ev.loc[zero, "U"] = 0.0
    n_after = int((ev["U"].astype(float) > 0).sum())
    ev.to_parquet(dst / "events.parquet", index=False)
    return dst


def train(cond: str, seed: int) -> dict:
    rd = OUT / "runs" / cond / "uair" / "fedavg_window" / f"seed{seed}"
    marker = rd / "final_metrics.json"
    if not marker.is_file():
        trace_dir = make_filtered_trace(cond, seed)
        c = CONDITIONS[cond]
        gc = dict(H.CONDITIONS["C0_frozen"]); gc["theta"] = c["theta"]
        gc["tail_scale"] = c["tail"]; gc["model"] = c["model"]
        ov, _ = (None, None)
        if c["target"] == "block_uniform":
            ov, _ = H.block_uniform_target("uair", _PI["ds"], _PI["mapping"])
        with H.injected(gc, block_factor=None):
            e3runner.run_e3_real(
                root=ROOT, run_dir=rd, dataset=H.load_paper_dataset(ROOT, "uair"),
                method="fedavg_window", seed=int(seed), eventtrace_dir=trace_dir,
                spatial_to_client=_PI["mapping"], dataset_name="uair",
                local_steps=H.LOCAL_STEPS, pi_target_override=ov,
                source_identity={"git_commit": "h_fedavg_restore_r2", "condition": cond,
                                 "rule": "R_pi_tar_zero_excluded"})
    return json.loads(marker.read_text(encoding="utf-8"))


def gate(cond: str, seed: int) -> dict:
    m = train(cond, seed)
    f = json.loads((FROZEN / f"seed{seed}" / "final_metrics.json").read_text(encoding="utf-8"))
    p = OUT / "runs" / cond / "uair" / "fedavg_window" / f"seed{seed}" / "window_metrics.json"
    q = FROZEN / f"seed{seed}" / "window_metrics.json"
    a = json.loads(p.read_text(encoding="utf-8")); b = json.loads(q.read_text(encoding="utf-8"))
    da, db = {}, {}
    for w in a:
        if w.get("active"): da[int(w["window_id"])] = sorted(str(x) for x in w["active_clients"])
    for w in b:
        if w.get("active"): db[int(w["window_id"])] = sorted(str(x) for x in w["active_clients"])
    diff = {k: {"v2": da.get(k), "frozen": db.get(k)} for k in sorted(set(da) | set(db))
            if da.get(k) != db.get(k)}
    warmup = "warmup_force" in json.dumps(a[:3])
    return {"condition": cond, "seed": int(seed),
            "RMSE_mu_v2": float(m["RMSE_mu"]), "RMSE_mu_frozen": float(f["RMSE_mu"]),
            "rmse_abs_diff": abs(float(m["RMSE_mu"]) - float(f["RMSE_mu"])),
            "Delta_group_v2": float(m["Delta_group"]), "Delta_group_frozen": float(f["Delta_group"]),
            "dgroup_abs_diff": abs(float(m["Delta_group"]) - float(f["Delta_group"])),
            "active_set_equal": len(diff) == 0,
            "n_windows_differing": len(diff),
            "differing_windows": list(diff)[:10],
            "pass": bool(len(diff) == 0
                         and abs(float(m["RMSE_mu"]) - float(f["RMSE_mu"])) <= TOL
                         and abs(float(m["Delta_group"]) - float(f["Delta_group"])) <= TOL)}


def stage_b(gate_only: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(exist_ok=True)
    rows = []
    for seed in STAGE_B_FIRST:
        t0 = time.perf_counter()
        r = gate("C0_frozen", seed)
        r["seconds"] = time.perf_counter() - t0
        rows.append(r)
        print("  C0 seed %d  rmse d=%.3e  dgroup d=%.3e  active_equal=%s  pass=%s (%.0fs)"
              % (seed, r["rmse_abs_diff"], r["dgroup_abs_diff"], r["active_set_equal"],
                 r["pass"], r["seconds"]), flush=True)
    if not all(r["pass"] for r in rows):
        json.dump({"pass": False, "stage": "B", "rows": rows,
                   "differing_windows": {str(r["seed"]): r["differing_windows"] for r in rows}},
                  open(OUT / "GATE_C0.json", "w", encoding="utf-8"), indent=2)
        pd.DataFrame(rows).to_csv(OUT / "tables" / "C0_REPRO.csv", index=False)
        print("STOP: Stage B gate failed; no waiver added, rule R unchanged, other seeds not started.")
        return
    if gate_only:
        print("gate-only: two seeds pass; remaining seeds not started")
        pd.DataFrame(rows).to_csv(OUT / "tables" / "C0_REPRO.csv", index=False)
        return
    for seed in [s for s in ALL_SEEDS if s not in STAGE_B_FIRST]:
        r = gate("C0_frozen", seed)
        rows.append(r)
        print("  C0 seed %d  rmse d=%.3e  dgroup d=%.3e  pass=%s"
              % (seed, r["rmse_abs_diff"], r["dgroup_abs_diff"], r["pass"]), flush=True)
        if not r["pass"]:
            json.dump({"pass": False, "stage": "B", "failed_seed": seed, "rows": rows},
                      open(OUT / "GATE_C0.json", "w", encoding="utf-8"), indent=2)
            pd.DataFrame(rows).to_csv(OUT / "tables" / "C0_REPRO.csv", index=False)
            print("STOP: a C0 cell failed; reported, not replaced.")
            return
    json.dump({"pass": True, "stage": "B", "n": len(rows), "rows": rows},
              open(OUT / "GATE_C0.json", "w", encoding="utf-8"), indent=2)
    pd.DataFrame(rows).to_csv(OUT / "tables" / "C0_REPRO.csv", index=False)
    print("Stage B PASS on all %d C0 seeds" % len(rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage-b", action="store_true")
    ap.add_argument("--gate-only", action="store_true")
    a = ap.parse_args()
    if a.stage_b or a.gate_only:
        stage_b(gate_only=a.gate_only)


if __name__ == "__main__":
    main()
