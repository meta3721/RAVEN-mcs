"""T1 (round v3): window-by-window debt-recursion diagnostics.

Q~_{r+1} = max(Q_r^rec + 0.01 * (mu - M_r alpha_r^rec), 0),  e_r = ||Q~_{r+1} - Q_{r+1}^rec||_inf

Uses only recorded quantities (states M/mu/debt + window_metrics alpha).  No replay alpha.
Read-only: writes only results_w1_ladder/round_v3/.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                       # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v3"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
ARMS = ("raven_wo_use", "raven_wo_obs")
ETA = 0.01
TOL = 1e-12


def run_case(d: str, arm: str, seed: int) -> dict:
    p = E4 / d / arm / f"seed{seed}"
    states = json.loads((p / "p2_invocation_states.json").read_text(encoding="utf-8"))
    act = W.active_windows(json.loads((p / "window_metrics.json").read_text(encoding="utf-8")))
    by_wid = {int(x["window_id"]): x for x in act}
    errs, rows = [], []
    Q_prev = None
    qchanges = 0
    for j, st in enumerate(states):
        M = np.asarray(st["M"], dtype=float)
        mu = np.asarray(st["mu"], dtype=float)
        Q = np.asarray(st["debt"], dtype=float)
        wid = int(st.get("window_id", j)) if "window_id" in st else None
        x = by_wid.get(wid) if wid is not None else (act[j] if j < len(act) else None)
        a = np.asarray(x["alpha"], dtype=float) if x is not None else None
        if Q_prev is not None and float(np.abs(Q - Q_prev).max()) > 0:
            qchanges += 1
        Q_prev = Q.copy()
        rows.append({"j": j, "wid": wid, "K_states": M.shape[1],
                     "K_wm": None if x is None else len(x["active_clients"]),
                     "status": st.get("status"), "fallback_used": bool(st.get("fallback_used")),
                     "repair_used": bool(st.get("feasibility_repair_used")),
                     "alpha_sum": None if a is None else float(a.sum()),
                     "Q_l1": float(np.abs(Q).sum())})
        if a is None or len(a) != M.shape[1] or j + 1 >= len(states):
            errs.append(np.nan)
            continue
        Qn = np.asarray(states[j + 1]["debt"], dtype=float)
        Qt = np.maximum(Q + ETA * (mu - M @ a), 0.0)
        errs.append(float(np.abs(Qt - Qn).max()))
        rows[-1]["e_r"] = errs[-1]
        rows[-1]["e_r_renorm"] = float(np.abs(
            np.maximum(Q + ETA * (mu - M @ (a / max(a.sum(), 1e-300))), 0.0) - Qn).max())
    return {"states": states, "act": act, "rows": rows, "errs": errs, "qchanges": qchanges,
            "path": p}


def h4_eta_search(p: pathlib.Path) -> dict:
    hits = []
    for name in ("config_snapshot.json", "runtime_manifest.json", "method_smoke_audit.json"):
        f = p / name
        if not f.is_file():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for k, v in (d.items() if isinstance(d, dict) else []):
            if "eta" in str(k).lower():
                hits.append({"file": name, "key": k, "value": v})
    return {"hits": hits, "found": bool(hits)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v3")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, detail = [], []
    for d in W.DS:
        for arm in ARMS:
            for seed in W.SEEDS:
                c = run_case(d, arm, seed)
                errs = np.array([e for e in c["errs"] if not np.isnan(e)], dtype=float)
                first = next((i for i, e in enumerate(c["errs"])
                              if not np.isnan(e) and e > TOL), None)
                n_states, n_act = len(c["states"]), len(c["act"])
                r0 = c["rows"][first] if first is not None else {}
                rec = {"ds": d, "arm": arm, "seed": seed, "n_states": n_states, "n_active": n_act,
                       "n_pairs": int(errs.size), "max_e": float(errs.max()) if errs.size else None,
                       "median_e": float(np.median(errs)) if errs.size else None,
                       "first_bad_window": first,
                       "q_change_count": c["qchanges"],
                       "status_bad_window": r0.get("status"),
                       "fallback_bad_window": r0.get("fallback_used"),
                       "repair_bad_window": r0.get("repair_used"),
                       "K_states_bad": r0.get("K_states"), "K_wm_bad": r0.get("K_wm"),
                       "alpha_sum_bad": r0.get("alpha_sum"),
                       "e_bad": r0.get("e_r"),
                       "e_bad_after_renorm": r0.get("e_r_renorm")}
                rows.append(rec)
                if first is not None:
                    w = c["rows"][first]
                    h1 = (w.get("K_states") != w.get("K_wm")) or any(
                        (r.get("K_states") != r.get("K_wm")) for r in c["rows"][:first + 1]
                        if r.get("K_wm") is not None)
                    h2 = bool(w.get("e_r_renorm") is not None and w["e_r_renorm"] <= TOL < (w.get("e_r") or 0))
                    h3 = (n_states != n_act) or (c["qchanges"] < n_states - 1)
                    h4 = h4_eta_search(c["path"])
                    detail.append({"ds": d, "arm": arm, "seed": seed, "first_bad": first,
                                   "H1_index_misalignment": bool(h1),
                                   "H2_alpha_renormalized": bool(h2),
                                   "H3_missing_debt_update": bool(h3),
                                   "H4_eta_not_0.01_found_keys": json.dumps(h4["hits"]),
                                   "H4_eta_key_present": bool(h4["found"]),
                                   "Q_l1_at_bad": w.get("Q_l1"),
                                   "Q_l1_max": max((r.get("Q_l1") or 0.0) for r in c["rows"])})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "DEBT_RECURSION.csv", index=False)
    det = pd.DataFrame(detail)
    if len(det):
        det.to_csv(OUT / "DEBT_RECURSION_HYPOTHESES.csv", index=False)
    summ = {
        "eta": ETA, "tol": TOL, "n_runs": int(len(df)),
        "runs_all_within_tol": int((df["max_e"] <= TOL).sum()),
        "max_e_overall": float(df["max_e"].max()) if len(df) else None,
        "median_of_max_e": float(df["max_e"].median()) if len(df) else None,
        "per_ds_arm": (df.groupby(["ds", "arm"])
                       .agg(n=("max_e", "size"), within_tol=("max_e", lambda s: int((s <= TOL).sum())),
                            max_e=("max_e", "max"), median_max_e=("max_e", "median"),
                            first_bad_mean=("first_bad_window", "mean"))
                       .round(6).reset_index().to_dict("records")),
    }
    if len(det):
        for col in ("H1_index_misalignment", "H2_alpha_renormalized", "H3_missing_debt_update",
                    "H4_eta_key_present"):
            summ[f"{col}_count"] = int(det[col].sum())
        summ["H4_examples"] = det[det["H4_eta_key_present"]].head(3).to_dict("records")
        summ["detail_rows"] = int(len(det))
    (OUT / "DEBT_RECURSION.json").write_text(json.dumps(summ, indent=2, default=str),
                                            encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))


if __name__ == "__main__":
    main()
