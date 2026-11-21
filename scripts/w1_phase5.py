"""W1 Phase 5: cost table (C1), endpoint semantics (C2), debt certificate (C3), cross-ruler (X).

Protocol: raven-mcs-w1-ladder-frontier-execution-prompt.md (sha256 a26c6388…), Phase 5.
Read-only: writes only results_w1_ladder/round_v2/.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                                   # noqa: E402
import w1_ladder as L                                                                   # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v2"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
DEBT_ARMS = (("e3", "raven"), ("e3", "debt_cal"), ("e4", "raven_wo_design"),
             ("e4", "raven_wo_obs"), ("e4", "raven_wo_use"), ("e4", "raven_wo_inst"))
RETIME_RUNGS = ("L3", "L5", "L6", "L4p")
RETIME_SEEDS = (30001, 30002)
ALIGN_TOL = 1e-12
ALIGN_FRACTION_FLOOR = 0.90
OUR_RULER = "R_on"
OFF_RULER = "R_offp"


def cpu_info() -> dict:
    name = "unknown"
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-ItemProperty 'HKLM:\\HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0')."
                              "ProcessorNameString"],
                             capture_output=True, text=True, timeout=60)
        if out.returncode == 0 and out.stdout.strip():
            name = out.stdout.strip()
    except Exception:
        pass
    return {"cpu_model": name, "logical_cores": None, "platform": platform.platform(),
            "python": platform.python_version()}


def frozen_runtime(ds: str) -> pd.DataFrame:
    rows = []
    for tag, base, arm in [("e4", E4, a) for a in
                           ("raven_wo_debt", "raven_wo_use", "raven_wo_obs", "raven_wo_design",
                            "raven_wo_inst")] + \
                          [("e3", E3, a) for a in ("raven", "inst_cal", "debt_cal",
                                                   "twostage_hajek", "local_hajek")]:
        vals = []
        for seed in W.SEEDS:
            p = base / ds / arm / f"seed{seed}" / "final_metrics.json"
            if p.is_file():
                m = json.loads(p.read_text(encoding="utf-8"))
                if m.get("runtime_seconds") is not None:
                    vals.append(float(m["runtime_seconds"]))
        if vals:
            rows.append({"ds": ds, "arm": arm, "family": tag, "n_seeds": len(vals),
                         "runtime_seconds_mean": float(np.mean(vals)),
                         "runtime_seconds_sd": float(np.std(vals, ddof=1)) if len(vals) > 1 else None})
    return pd.DataFrame(rows)


def retime(pi: dict) -> pd.DataFrame:
    """Clean single-process timing of the ladder rungs (2 seeds per dataset)."""
    sel = pd.read_csv(OUT / "LADDER_SELECTION.csv")
    chosen = {(r.ds, r.rung): r.config for r in sel[sel.split == "chosen"].itertuples()}
    rows = []
    for d in W.DS:
        for seed in RETIME_SEEDS:
            case = W.build_case(d, OUR_RULER, "raven_wo_use", seed, pi[d])
            if case is None:
                continue
            plan = [("L0", None), ("L1", None), ("L3", chosen[(d, "L3")]),
                    ("L4", chosen[(d, "L4")]), ("L5", chosen[(d, "L5")]),
                    ("L6", chosen[(d, "L6")]), ("L4p", chosen[(d, "L4p")])]
            for rung, cfg in plan:
                ts = []
                t0 = time.perf_counter()
                if rung == "L0":
                    a = L.alpha_uniform(case)
                elif rung == "L1":
                    a = L.alpha_count(case)
                elif rung == "L3":
                    a = L.alpha_match(case, eps=float(cfg))
                elif rung == "L4":
                    a = L.alpha_match(case, eps=float(chosen[(d, "L3")]), lam_v=float(cfg))
                elif rung == "L5":
                    a, ts, warns = L.alpha_p2_seq(case, float(cfg), debt_source="zero")
                elif rung == "L6":
                    a, ts, warns = L.alpha_p2_seq(case, float(cfg), debt_source="recorded")
                else:
                    a, ts, warns = L.alpha_p2_seq(case, float(cfg), lam_beta=1e-8, lam_v=0.0,
                                                  lam_s=0.0, debt_source="recorded")
                wall = time.perf_counter() - t0
                if not ts:
                    ts = [wall / max(case["n"], 1)] * case["n"]
                rows.append({"ds": d, "rung": rung, "seed": seed, "config": str(cfg),
                             "n_windows": case["n"],
                             "solve_ms_median": float(np.median(ts) * 1e3),
                             "solve_ms_p95": float(np.percentile(ts, 95) * 1e3),
                             "warnings": int(warns if rung in ("L5", "L6", "L4p") else 0),
                             "source": "phase5_retime_single_process"})
    return pd.DataFrame(rows)


def cost_table(pi: dict, info: dict) -> pd.DataFrame:
    lad = pd.read_csv(OUT / "LADDER.csv")
    lad = lad[lad["split"] == "report"]
    agg = (lad.groupby(["ds", "rung"])
           .agg(n_seeds=("seed", "nunique"),
                solve_ms_median=("solve_ms_median", "median"),
                solve_ms_p95=("solve_ms_p95", "median"),
                warnings=("warnings", "sum"))
           .reset_index())
    agg["source"] = "phase4_ladder_concurrent_2proc"
    rt = retime(pi)
    rt_agg = (rt.groupby(["ds", "rung"])
              .agg(n_seeds=("seed", "nunique"),
                   solve_ms_median=("solve_ms_median", "median"),
                   solve_ms_p95=("solve_ms_p95", "median"),
                   warnings=("warnings", "sum"))
              .reset_index())
    rt_agg["source"] = "phase5_retime_single_process"
    cost = pd.concat([agg, rt_agg], ignore_index=True)
    fr = pd.concat([frozen_runtime(d) for d in W.DS], ignore_index=True)
    fr["source"] = "frozen_run_final_metrics"
    fr = fr.rename(columns={"arm": "rung"})
    out = pd.concat([cost, fr[["ds", "rung", "n_seeds", "source",
                               "runtime_seconds_mean", "runtime_seconds_sd", "family"]]],
                    ignore_index=True)
    for k, v in info.items():
        out[k] = v
    return out


def endpoint_semantics() -> pd.DataFrame:
    lat = pd.read_csv(OUT / "LADDER_REPORT_SEEDS.csv")
    lat = lat[lat["ruler"] == OUR_RULER]
    rows = []
    for (d, rung), g in lat.groupby(["ds", "rung"]):
        dg, du, ds_ = (float(g.d_group.mean()), float(g.d_unif_group.mean()),
                       float(g.d_star_group.mean()))
        rows.append({"ds": d, "object": rung, "kind": "ladder_rung", "d_group": dg,
                     "tv_group": dg / 2, "tv_unavoidable": ds_ / 2,
                     "tv_avoidable_not_avoided": (dg - ds_) / 2})
        if rung == "L0":
            rows.append({"ds": d, "object": "Delta_unif", "kind": "reference", "d_group": du,
                         "tv_group": du / 2, "tv_unavoidable": ds_ / 2,
                         "tv_avoidable_not_avoided": (du - ds_) / 2})
            rows.append({"ds": d, "object": "Delta_star", "kind": "reference", "d_group": ds_,
                         "tv_group": ds_ / 2, "tv_unavoidable": ds_ / 2,
                         "tv_avoidable_not_avoided": 0.0})
    ar = pd.read_csv(OUT / "FRONTIER_ARMS.csv")
    ar = ar[(ar.ruler == OUR_RULER) & (ar.endpoint == "group")]
    for (d, arm), g in ar.groupby(["ds", "arm"]):
        dg, du, ds_ = float(g.d_rule.mean()), float(g.d_unif.mean()), float(g.d_star.mean())
        rows.append({"ds": d, "object": arm, "kind": "frozen_arm", "d_group": dg,
                     "tv_group": dg / 2, "tv_unavoidable": ds_ / 2,
                     "tv_avoidable_not_avoided": (dg - ds_) / 2})
    return pd.DataFrame(rows)


def certificate() -> pd.DataFrame:
    rows = []
    for tag, arm in DEBT_ARMS:
        base = {"e3": E3, "e4": E4}[tag]
        for d in W.DS:
            for seed in W.SEEDS:
                p = base / d / arm / f"seed{seed}" / "final_metrics.json"
                if not p.is_file():
                    continue
                m = json.loads(p.read_text(encoding="utf-8"))
                q = m.get("Q_norm1_over_S")
                dg = m.get("Delta_group")
                row = {"ds": d, "arm": arm, "family": tag, "seed": seed,
                       "Q_norm1_over_S": q, "bound_2Q": None if q is None else 2.0 * float(q),
                       "Delta_group": dg, "applicability": m.get("Q_norm1_over_S_applicability")}
                if q is None or dg is None:
                    row.update({"ratio": None, "pass": None,
                                "status": "not_applicable_uses_debt_false"})
                else:
                    bound = 2.0 * float(q)
                    row.update({"ratio": float(dg) / bound if bound > 0 else None,
                                "pass": bool(float(dg) <= bound + 1e-9),
                                "status": "ok" if float(dg) <= bound + 1e-9 else "CERT_VIOLATION"})
                rows.append(row)
    return pd.DataFrame(rows)


def aligned_pair(case_on: dict, case_off: dict) -> tuple:
    """Window indices aligned between the two rulers.

    Pairing is by window_id first (client-tuple-only pairing mis-pairs when several windows
    share the same active set, e.g. SensorScope), then the protocol's criterion is checked:
    the active_client tuples must be identical.
    """
    off_by_wid = {case_off["wids"][j]: j for j in range(case_off["n"])}
    pairs = []
    for j in range(case_on["n"]):
        k = off_by_wid.get(case_on["wids"][j])
        if k is not None and tuple(case_off["clients"][k]) == tuple(case_on["clients"][j]):
            pairs.append((j, k))
    return pairs


def cross_ruler(pi: dict) -> pd.DataFrame:
    rows = []
    for d in W.DS:
        for seed in W.SEEDS:
            c_on = W.build_case(d, OUR_RULER, "raven_wo_use", seed, pi[d])
            c_off = W.build_case(d, OFF_RULER, "raven_wo_design", seed, pi[d])
            if c_on is None or c_off is None:
                continue
            pairs = aligned_pair(c_on, c_off)
            max_m = max((float(np.abs(c_on["M"][j] - c_off["M"][k]).max()) for j, k in pairs),
                        default=None)
            base = {"ds": d, "seed": seed, "n_on": c_on["n"], "n_off": c_off["n"],
                    "aligned_windows": len(pairs),
                    "aligned_fraction": len(pairs) / max(1, min(c_on["n"], c_off["n"])),
                    "max_abs_M_diff": max_m,
                    "g4_ruler_ok": None if max_m is None else bool(max_m <= ALIGN_TOL)}
            if not pairs:
                rows.append({**base, "direction": "none", "arm": None, "d_group_aligned": None})
                continue
            # (1) Design-on arms' alpha evaluated on R_offp
            for arm in ("raven", "inst_cal"):
                p = E3 / d / arm / f"seed{seed}"
                if not (p / "window_metrics.json").is_file():
                    continue
                act = W.active_windows(json.loads((p / "window_metrics.json").read_text()))
                act_by_wid = {int(x["window_id"]): x for x in act}
                omegas = []
                for j, k in pairs:
                    x = act_by_wid.get(int(c_on["wids"][j]))
                    if x is None:
                        omegas = []
                        break
                    a = np.asarray(x["alpha"], dtype=float)
                    if len(a) != len(c_on["clients"][j]):
                        omegas = []
                        break
                    omegas.append(c_off["M"][k] @ a)
                if not omegas:
                    continue
                dg = float(np.abs(np.mean(omegas, axis=0) - c_off["mu"]).sum())
                rows.append({**base, "direction": f"{arm}_alpha_on_{OFF_RULER}", "arm": arm,
                             "d_group_aligned": dg})
            # (2) Design-off arm's alpha evaluated on R_on
            omegas = []
            for j, k in pairs:
                a = np.asarray(c_off["alpha_arm"], dtype=float)
                blocks, off = [], 0
                for t in range(c_off["n"]):
                    K = len(c_off["clients"][t])
                    blocks.append(a[off:off + K])
                    off += K
                omegas.append(c_on["M"][j] @ blocks[k])
            dg = float(np.abs(np.mean(omegas, axis=0) - c_on["mu"]).sum())
            rows.append({**base, "direction": f"raven_wo_design_alpha_on_{OUR_RULER}",
                         "arm": "raven_wo_design", "d_group_aligned": dg})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v2")
    ap.add_argument("--skip-retime", action="store_true")
    args = ap.parse_args()
    global OUT
    OUT = ROOT / "results_w1_ladder" / args.round
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    info = cpu_info()
    (OUT / "COST_MACHINE.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

    es = endpoint_semantics()
    es.to_csv(OUT / "ENDPOINT_SEMANTICS.csv", index=False)
    print("endpoint semantics rows", len(es))

    xr = cross_ruler(pi)
    xr.to_csv(OUT / "CROSS_RULER.csv", index=False)
    print(xr.groupby("ds")[["n_on", "n_off", "aligned_windows", "aligned_fraction",
                            "max_abs_M_diff"]].mean().to_string())

    cost = cost_table(pi, info) if not args.skip_retime else None
    if cost is not None:
        cost.to_csv(OUT / "COST.csv", index=False)
        print("cost rows", len(cost), "cpu", info["cpu_model"])

    cert = certificate()
    cert.to_csv(OUT / "CERT.csv", index=False)
    bad = cert[cert["status"] == "CERT_VIOLATION"]
    na = cert[cert["status"] == "not_applicable_uses_debt_false"]
    print("cert rows", len(cert), "violations", len(bad), "not_applicable", len(na))
    if len(cert[cert["status"] == "ok"]):
        ok = cert[cert["status"] == "ok"]
        print("cert ratio min %.4f max %.4f ; bound-vs-Delta margin min %.4f"
              % (ok["ratio"].min(), ok["ratio"].max(),
                 (ok["bound_2Q"] - ok["Delta_group"]).min()))
    print("CERT_VIOLATION" if len(bad) else "certificate ok")


if __name__ == "__main__":
    main()
