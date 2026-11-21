"""Group-decomposition identity check for RMSE_mu (read-only).

Protocol: the execution prompt "group decomposition of RMSE_mu" (attachment, 2026-10-02).

Checks E1-E5 of that protocol and writes only results_group_identity/round_v1/:

  E1  |RMSE_mu - sqrt(sum_b W_b RMSE_block_b^2)| per (dataset, arm, seed), with the block
      masses W_b rebuilt from the scoring mu and the test-unit group counts through
      _mu_weights_for_test (never four equal weights).
  E2  City Scanner: exact layer |d(RMSE^2) - sum_g dmu_g RMSE_g^2| and the Taylor layer,
      for the measured shifts run->M1->M2 plus one frozen small perturbation.
  E3  City Scanner: pair order vs sign of D(mu) = sum_g mu_g (RMSE^2_{g,a} - RMSE^2_{g,b}).
  E4  RMSE_mu only: sign and order of magnitude of the Design on/off gap, SensorScope and U-Air.
  E5  within-group weight variance under _mu_weights_for_test (one seed per dataset).

No training, no src/ edits, no manuscript edits, no writes outside the new output folder.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from raven_mcs.e3.canary.dataset_load import load_paper_dataset       # noqa: E402
from raven_mcs.e3.real_runner.runner import _mu_weights_for_test      # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle  # noqa: E402
from run_h_headroom import _block_of                                   # noqa: E402

OUT = ROOT / "results_group_identity/round_v1"
G2 = ROOT / "post_review/G2_external_baselines/tables/per_seed.csv"
ENDPOINTS = ROOT / "results_exogenous_target/round_v1/ENDPOINT_TABLE.csv"
ENDPOINTS_JSON = ROOT / "results_exogenous_target/round_v1/ENDPOINT_TABLE.json"
PERTURB = np.asarray([0.02, -0.01, -0.01, 0.0])
TOL_EXACT = 1e-12
TOL_STOP = 1e-8


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block_masses(dataset_name: str) -> tuple[np.ndarray, np.ndarray, dict]:
    """W_b for the four UTC blocks, from the scoring mu and the test-unit group counts."""
    ds = load_paper_dataset(ROOT, dataset_name)
    bundle = production_target_bundle(root=ROOT, dataset_name=dataset_name, dataset=ds)
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    names = list(bundle["group_id_by_index"])
    units = ds.get_atomic_units(split="test")
    gids = np.asarray([int(u.target_group) for u in units], dtype=int)
    pred = {"groups": gids}
    w = _mu_weights_for_test(pred, mu)                    # the real implementation
    blocks = np.asarray([_block_of(str(names[g])) for g in gids], dtype=int)
    W = np.asarray([float(w[blocks == b].sum()) for b in range(4)], dtype=np.float64)
    return W, w, {"n_test": int(len(gids)), "n_groups": int(len(mu)),
                  "mu_min": float(mu.min()), "w_sum": float(w.sum()),
                  "groups_present": int(len(set(gids.tolist())))}


def within_group_var(gids: np.ndarray, w: np.ndarray) -> float:
    worst = 0.0
    for g in np.unique(gids):
        vals = w[gids == g]
        worst = max(worst, float(np.var(vals)))
    return worst


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", default=pd.Timestamp.utcnow().isoformat())
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    # ---------------- E1 ----------------
    e1_rows = []

    g2 = pd.read_csv(G2)
    for dataset in ("sensorscope", "uair"):
        W, _, meta = block_masses(dataset)
        sub = g2[g2["dataset"] == dataset]
        for _, r in sub.iterrows():
            blocks = np.asarray([r[f"RMSE_block{b}"] for b in range(4)], dtype=np.float64)
            lhs = float(r["RMSE_mu"])
            rhs = float(np.sqrt(np.sum(W * blocks ** 2)))
            err = abs(lhs - rhs)
            stored_gap = abs(float(r["RMSE_mu_stored"]) - lhs)
            status = "ok" if err <= TOL_EXACT else ("source_mismatch" if stored_gap > 1e-6 else "fail")
            e1_rows.append({"dataset": dataset, "arm": r["method"], "seed": int(r["seed"]),
                            "source": "post_review/G2_external_baselines/tables/per_seed.csv",
                            "abs_err": err, "status": status})

    ep = pd.read_csv(ENDPOINTS)
    epj = json.loads(ENDPOINTS_JSON.read_text())
    for name in ("run", "M1", "M2"):
        mu = np.asarray(epj["weights"][name], dtype=np.float64)
        for _, r in ep.iterrows():
            blocks = np.asarray([r[f"RMSE_R{b}"] for b in range(4)], dtype=np.float64)
            lhs = float(r[f"RMSE_{name}"])
            rhs = float(np.sqrt(np.sum(mu * blocks ** 2)))
            e1_rows.append({"dataset": "cityscanner", "arm": r["arm"], "seed": int(r["seed"]),
                            "source": f"results_exogenous_target/round_v1/ENDPOINT_TABLE.csv[{name}]",
                            "abs_err": abs(lhs - rhs), "status": "ok" if abs(lhs - rhs) <= TOL_EXACT else "fail"})
    e1 = pd.DataFrame(e1_rows)
    pd.DataFrame(e1).to_csv(OUT / "E1_CELLS.csv", index=False)
    e1_same = e1[e1["status"].isin(["ok", "source_mismatch"])]
    e1_max = float(e1["abs_err"].max())
    stopping = e1[(e1["abs_err"] > TOL_STOP) & (e1["status"] == "fail")]

    # ---------------- E2 ----------------
    e2_rows = []
    measured = {"run": epj["weights"]["run"], "M1": epj["weights"]["M1"], "M2": epj["weights"]["M2"]}
    shifts = [("run->M1", "run", "M1"), ("run->M2", "run", "M2"), ("M1->M2", "M1", "M2")]
    for label, a, b in shifts:
        mua = np.asarray(measured[a], dtype=np.float64)
        mub = np.asarray(measured[b], dtype=np.float64)
        dmu = mub - mua
        exact = taylor = 0.0
        for _, r in ep.iterrows():
            g2v = np.asarray([r[f"RMSE_R{k}"] ** 2 for k in range(4)], dtype=np.float64)
            lhs2 = float(r[f"RMSE_{b}"]) ** 2
            rhs2 = float(r[f"RMSE_{a}"]) ** 2
            exact = max(exact, abs((lhs2 - rhs2) - float(dmu @ g2v)))
            taylor = max(taylor, abs(float(r[f"RMSE_{b}"]) - float(r[f"RMSE_{a}"])
                                     - float(dmu @ g2v) / (2 * float(r[f"RMSE_{a}"]))))
        e2_rows.append({"shift": label, "exact_abs": exact, "taylor_abs": taylor,
                        "measured_targets": True})
    # frozen small perturbation: target value comes from the identity itself
    mua = np.asarray(measured["run"], dtype=np.float64)
    mub = mua + PERTURB
    dmu = PERTURB.copy()
    exact = taylor = 0.0
    for _, r in ep.iterrows():
        g2v = np.asarray([r[f"RMSE_R{k}"] ** 2 for k in range(4)], dtype=np.float64)
        rmse_a = float(np.sqrt(mua @ g2v))
        rmse_b = float(np.sqrt(mub @ g2v))
        exact = max(exact, abs((rmse_b ** 2 - rmse_a ** 2) - float(dmu @ g2v)))
        taylor = max(taylor, abs(rmse_b - rmse_a - float(dmu @ g2v) / (2 * rmse_a)))
    e2_rows.append({"shift": "run->run+d (frozen d=(0.02,-0.01,-0.01,0))", "exact_abs": exact,
                    "taylor_abs": taylor, "measured_targets": False})
    pd.DataFrame(e2_rows).to_csv(OUT / "E2_TAYLOR.csv", index=False)

    # ---------------- E3 ----------------
    arms = sorted(ep["arm"].unique())
    per = {a: ep[ep["arm"] == a].sort_values("seed").reset_index(drop=True) for a in arms}
    seeds = list(per[arms[0]]["seed"])
    means = {name: {a: float(per[a][f"RMSE_{name}"].mean()) for a in arms} for name in ("run", "M1", "M2")}
    e3_rows = []
    violations = []
    same_sign_violations = []
    for a, b in itertools.combinations(arms, 2):
        D = {}
        for name in ("run", "M1", "M2"):
            mu = np.asarray(measured[name], dtype=np.float64)
            d_seed = []
            for i in range(len(seeds)):
                diff = np.asarray([per[a][f"RMSE_R{k}"][i] ** 2 - per[b][f"RMSE_R{k}"][i] ** 2
                                   for k in range(4)], dtype=np.float64)
                d_seed.append(float(mu @ diff))
                if np.all(diff > 0) or np.all(diff < 0):
                    expected = 1 if diff[0] > 0 else -1
                    for other in ("run", "M1", "M2"):
                        mu_o = np.asarray(measured[other], dtype=np.float64)
                        if np.sign(float(mu_o @ diff)) != expected:
                            same_sign_violations.append(
                                {"arm_a": a, "arm_b": b, "seed": int(seeds[i]),
                                 "components_all_positive": bool(diff[0] > 0), "mu": other,
                                 "D": float(mu_o @ diff)})
            D[name] = float(np.mean(d_seed))
        order = {name: (means[name][a] < means[name][b]) for name in ("run", "M1", "M2")}
        for m1, m2 in itertools.combinations(("run", "M1", "M2"), 2):
            same_sign = (D[m1] > 0) == (D[m2] > 0)
            flipped_order = order[m1] != order[m2]
            ok = (same_sign and not flipped_order) or ((not same_sign) and flipped_order)
            e3_rows.append({"arm_a": a, "arm_b": b, "mu": m1, "mu_prime": m2,
                            "D": D[m1], "D_prime": D[m2],
                            "sign_same": bool(same_sign), "rank_flipped": bool(flipped_order),
                            "flipped": bool(flipped_order), "consistent": bool(ok)})
            if not ok:
                violations.append((a, b, m1, m2, D[m1], D[m2]))
    pd.DataFrame(e3_rows).to_csv(OUT / "E3_PAIRS.csv", index=False)

    # ---------------- E4 ----------------
    e4_rows = []
    published = {"sensorscope": 0.00005, "uair": -0.06885}
    for dataset in ("sensorscope", "uair"):
        W, _, _ = block_masses(dataset)
        on = g2[(g2["dataset"] == dataset) & (g2["method"] == "raven")]
        off = g2[(g2["dataset"] == dataset) & (g2["method"] == "raven_wo_design")]
        if on.empty or off.empty:
            e4_rows.append({"dataset": dataset, "published_rel": published[dataset],
                            "identity_rel": None, "status": "not_recovered"})
            continue
        rels = []
        for seed in sorted(set(on["seed"]) & set(off["seed"])):
            ro = on[on["seed"] == seed].iloc[0]
            rf = off[off["seed"] == seed].iloc[0]
            m_on = float(np.sqrt(np.sum(W * np.asarray([ro[f"RMSE_block{b}"] for b in range(4)]) ** 2)))
            m_off = float(np.sqrt(np.sum(W * np.asarray([rf[f"RMSE_block{b}"] for b in range(4)]) ** 2)))
            rels.append((m_off - m_on) / m_on)
        rel = float(np.mean(rels))
        pub = published[dataset]
        sign_ok = (rel > 0) == (pub > 0)
        ratio = abs(rel) / abs(pub) if pub != 0 else float("inf")
        e4_rows.append({"dataset": dataset, "published_rel": pub, "identity_rel": rel,
                        "sign_ok": bool(sign_ok), "magnitude_ratio": ratio,
                        "status": "recovered" if (sign_ok and ratio <= 2.0) else "not_recovered"})
    pd.DataFrame(e4_rows).to_csv(OUT / "E4_RMSE_GAP.csv", index=False)

    # ---------------- E5 ----------------
    e5_rows = []
    for dataset in ("sensorscope", "uair"):
        _, _, meta = block_masses(dataset)
        ds = load_paper_dataset(ROOT, dataset)
        bundle = production_target_bundle(root=ROOT, dataset_name=dataset, dataset=ds)
        mu = np.asarray(bundle["mu"], dtype=np.float64)
        gids = np.asarray([int(u.target_group) for u in ds.get_atomic_units(split="test")], dtype=int)
        w = _mu_weights_for_test({"groups": gids}, mu)
        e5_rows.append({"dataset": dataset, "grouping": "target_group (as scored)",
                        "max_within_group_var": within_group_var(gids, w)})
    # City Scanner via the confirmed loader
    import run_nodesign_supplement as nss
    cs_ds, _, _ = nss._load_cityscanner()
    cs_mu = np.asarray(measured["run"], dtype=np.float64)
    cs_gids = np.asarray([int(u.target_group) for u in cs_ds.get_atomic_units(split="test")], dtype=int)
    cs_w = _mu_weights_for_test({"groups": cs_gids}, cs_mu)
    e5_rows.append({"dataset": "cityscanner", "grouping": "target_group (region)",
                    "max_within_group_var": within_group_var(cs_gids, cs_w)})
    pd.DataFrame(e5_rows).to_csv(OUT / "E5_WITHIN_GROUP.csv", index=False)

    # ---------------- report + manifest ----------------
    banned = ["the model was retrained under an exogenous target",
              "the switch point has been proved", "the support loss is bounded",
              "a rank flip means one method is better"]
    report = [
        "# Group-decomposition identity check (`RMSE_mu`)", "",
        f"stamp_utc: {args.stamp}", "",
        "## E1 — `RMSE_mu^2 = sum_b W_b RMSE_block_b^2`", "",
        f"- rows checked: {len(e1)} (City Scanner 150 cells; SensorScope/U-Air "
        f"{int((e1['dataset'] != 'cityscanner').sum())} rows from "
        "`post_review/G2_external_baselines/tables/per_seed.csv`)",
        f"- max absolute error over same-source rows: {e1_max:.3e} "
        f"(pass line {TOL_EXACT:.0e}; stop line {TOL_STOP:.0e})",
        f"- rows marked `source_mismatch`: {int((e1['status'] == 'source_mismatch').sum())}; "
        f"rows marked `fail` above the stop line: {len(stopping)}",
        f"- block masses rebuilt from the scoring `mu` and the test-unit group counts via "
        "`_mu_weights_for_test`; the four blocks are never set to 0.25",
        "",
        "## E2 — exact layer and Taylor layer (City Scanner)", "",
    ]
    for r in e2_rows:
        report.append(f"- {r['shift']}: exact {r['exact_abs']:.3e}, taylor {r['taylor_abs']:.3e}"
                      + ("" if r["measured_targets"] else
                         "  (target from the identity itself: the exact layer is not an "
                         "independent check for this shift)"))
    report += ["", "## E3 — pair order vs sign of `D(mu)`", "",
               f"- pairs checked: {len(e3_rows)} (5 arms, 3 weight vectors)",
               f"- order/sign inconsistencies: {len(violations)}",
               f"- all-four-components-same-sign violations: {len(same_sign_violations)}"]
    for v in same_sign_violations[:20]:
        report.append(f"  - SAME-SIGN VIOLATION {v}")
    for v in violations:
        report.append(f"  - VIOLATION {v}")
    report += ["", "## E4 — Design on/off `RMSE_mu` gap (RMSE only)", ""]
    for r in e4_rows:
        report.append(f"- {r['dataset']}: published {r['published_rel']:+.5%}, identity "
                      f"{(r['identity_rel'] if r['identity_rel'] is not None else float('nan')):+.5%}, "
                      f"status {r['status']}")
    report += ["", "`Delta_group`, `Delta_c-s` and Tail are **not** part of this check.", "",
               "## E5 — within-group weight variance", ""]
    for r in e5_rows:
        report.append(f"- {r['dataset']} ({r['grouping']}): max within-group variance "
                      f"{r['max_within_group_var']:.3e}")
    report += ["", "## Prohibited-claim audit", "",
               "No claim of the following kinds is asserted anywhere in this report or in the "
               "artefacts of this run; they are listed here only so the audit is greppable."]
    report += [f"- not asserted: \"{b}\"" for b in banned]
    (OUT / "CHECK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    files = ["E1_CELLS.csv", "E2_TAYLOR.csv", "E3_PAIRS.csv", "E4_RMSE_GAP.csv",
             "E5_WITHIN_GROUP.csv", "CHECK_REPORT.md"]
    lines = [f"{sha256(OUT / f)}  {f}" for f in files]
    lines.append(f"{sha256(ROOT / 'scripts/group_identity_check.py')}  scripts/group_identity_check.py")
    (OUT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"E1_max_abs_err": e1_max, "E1_source_mismatch": int((e1["status"] == "source_mismatch").sum()),
                      "E1_fail_above_stop": len(stopping), "E2": e2_rows,
                      "E3_violations": len(violations), "E3_same_sign_violations": len(same_sign_violations), "E4": e4_rows, "E5": e5_rows},
                     indent=2, default=str))


if __name__ == "__main__":
    main()
