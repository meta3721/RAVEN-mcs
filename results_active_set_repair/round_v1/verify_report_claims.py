#!/usr/bin/env python3
"""Independent re-derivation of every numeric claim in EXPERIMENT_REPORT_FOR_VERIFICATION.md.

Run:  .venv_new/Scripts/python.exe results_active_set_repair/round_v1/verify_report_claims.py
      ... --deep     also rebuild pi^tar from the runner path and recount the holes (~2 min)

Exit code 0 = every check passed. Any FAIL prints the claim, the expected value, the
re-derived value and the artifact it came from.

This script only READS stored artifacts. It trains nothing and writes nothing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results_active_set_repair" / "round_v1"
FROZEN_E3 = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
FEDAU = ROOT / "artifacts" / "e3_fedau_window_r1" / "runs"
OBSUSE = ROOT / "artifacts" / "e3_obsuse_window_r1" / "runs"
E4 = ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs"
SEALED = ROOT / "manuscript_evidence_closure_r1" / "01_table_sources" / "TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv"
PER_SEED_REPRO = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1" / "tables" / "TABLE_II_WORSTGROUP_PER_SEED.csv"
AUDIT_PER_SEED = ROOT / "results_table2_audit" / "uair_fedavg_current_per_seed.csv"
REPORT = OUT / "EXPERIMENT_REPORT_FOR_VERIFICATION.md"
SIGMA = 17.36325121670317
SEEDS = list(range(30001, 30021))

_results: list[tuple[bool, str, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    _results.append((bool(ok), name, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""), flush=True)
    return bool(ok)


def close(a, b, tol) -> bool:
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


def rd_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def rd_csv(p: Path) -> list[dict]:
    with p.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def mean_rmse(d: Path) -> float | None:
    vals = []
    for s in SEEDS:
        f = d / f"seed{s}" / "final_metrics.json"
        if not f.is_file():
            return None
        vals.append(float(rd_json(f)["RMSE_mu"]))
    return sum(vals) / len(vals)


# --------------------------------------------------------------------------- sections
def s0_amendment():
    print("\n== S0  G1a tolerance amendment ==")
    g1 = rd_json(OUT / "G1_REPORT.json")
    am = g1.get("amendment") or {}
    check("G1_REPORT.json carries the amendment block", bool(am))
    check("plan tolerance recorded as 1e-9", close(am.get("original_tolerance"), 1e-9, 0),
          f"got {am.get('original_tolerance')}")
    check("applied tolerance recorded as 1e-6", close(am.get("applied_tolerance"), 1e-6, 0),
          f"got {am.get('applied_tolerance')}")
    rows = [r for r in g1["G1a"] if r["method"] == "debt_cal"]
    check("debt_cal G1a arm is explicitly not bit-exact",
          bool(rows) and rows[0].get("bit_equal_strict") is False,
          f"abs_diff={rows[0]['abs_diff'] if rows else None}")
    diag = rd_json(OUT / "G1_DEBT_CAL_DIAG.json")
    check("drift is deterministic (three measurements identical)",
          diag.get("self_consistent") is True and diag.get("ordering_effect") is False,
          f"verdict={diag.get('verdict')}")
    vals = {r["rerun"] for r in diag["runs"]} | {diag.get("g1a_value_third_in_process")}
    check("all measurements equal 7.915297538076236", vals == {7.915297538076236}, f"{vals}")
    check("frozen reference is 7.915297744846339",
          close(diag.get("frozen"), 7.915297744846339, 0), f"{diag.get('frozen')}")
    check("amendment appears in the report text",
          "TOLERANCE AMENDMENT" in REPORT.read_text(encoding="utf-8"))


def s0b_boundary_and_env():
    print("\n== S0b  Environment fingerprint ==")
    import numpy
    import pandas
    import scipy
    import torch
    exp = {"python": "3.11.9", "pandas": "3.0.5", "numpy": "2.4.6",
           "torch": "2.13.0+cu130", "scipy": "1.17.1"}
    got = {"python": sys.version.split()[0], "pandas": pandas.__version__,
           "numpy": numpy.__version__, "torch": torch.__version__,
           "scipy": scipy.__version__}
    for k, v in exp.items():
        check(f"env {k} == {v}", got.get(k) == v, f"got {got.get(k)}")
    try:
        import cvxpy
        check("env cvxpy == 1.9.2", cvxpy.__version__ == "1.9.2", f"got {cvxpy.__version__}")
    except Exception as exc:
        check("env cvxpy == 1.9.2", False, str(exc))


def s1_g0():
    print("\n== S1  G0 inventory ==")
    holes = {r["block"]: r for r in rd_csv(OUT / "PI_TAR_HOLES.csv")}
    for block, pairs, zero in (("uair", 288, 72), ("sensorscope", 440, 0), ("traffic", 344, 0)):
        r = holes.get(block, {})
        try:
            got = (int(float(r["support_pairs"])), int(float(r["zero_pi_tar_pairs"])))
        except (KeyError, TypeError, ValueError):
            got = None
        check(f"{block}: support={pairs}, zero_pi_tar={zero}", got == (pairs, zero), f"got {got}")
    check("tdrive_speed is reported NOT_COUNTED, not a number",
          holes.get("tdrive_speed", {}).get("status") == "NOT_COUNTED")

    inv = rd_csv(OUT / "ACTIVE_SET_INVENTORY.csv")
    check("ACTIVE_SET_INVENTORY has 640 rows", len(inv) == 640, f"got {len(inv)}")
    vio = [r for r in inv if r["verdict"] == "VIOLATION"]
    check("80 violations", len(vio) == 80, f"got {len(vio)}")
    check("violations are exactly the four no-Design methods",
          sorted({r["method"] for r in vio}) == sorted(
              ["fedavg_window", "fedasync_window", "flamf_timealign_adapted", "debt_cal"]),
          f"got {sorted({r['method'] for r in vio})}")
    check("all violations are on uair", {r["block"] for r in vio} == {"uair"},
          f"got {sorted({r['block'] for r in vio})}")
    by = {}
    for r in inv:
        by.setdefault((r["block"], r["method"]), []).append(r)
    def agg(block, method):
        rs = by[(block, method)]
        return (sum(int(r["identical_to_fedau"]) for r in rs),
                sum(int(r["compared"]) for r in rs),
                sum(float(r["mean_abs_active"]) for r in rs) / len(rs))
    a = agg("uair", "fedavg_window")
    check("uair contaminated batch = 826/1600, mean 1.8269",
          a[0] == 826 and a[1] == 1600 and close(a[2], 1.826875, 5e-6), f"{a}")
    a = agg("uair", "fedau_window")
    check("uair clean batch = 1600/1600, mean 2.4500",
          a[0] == 1600 and a[1] == 1600 and close(a[2], 2.45, 5e-9), f"{a}")
    a = agg("sensorscope", "fedavg_window")
    check("sensorscope = 2000/2000, mean 2.4245",
          a[0] == 2000 and a[1] == 2000 and close(a[2], 2.4245, 5e-9), f"{a}")


def s2_g1():
    print("\n== S2  G1 gates ==")
    g1 = rd_json(OUT / "G1_REPORT.json")
    check("G1 pass=True under the amendment", g1.get("pass") is True)
    a = {r["method"]: r for r in g1["G1a"]}
    check("G1a fedasync_window bit-exact 0.0", close(a["fedasync_window"]["abs_diff"], 0.0, 0))
    check("G1a flamf_timealign_adapted bit-exact 0.0",
          close(a["flamf_timealign_adapted"]["abs_diff"], 0.0, 0))
    check("G1a debt_cal abs_diff == 2.0677010326153322e-07",
          close(a["debt_cal"]["abs_diff"], 2.0677010326153322e-07, 1e-20),
          f"{a['debt_cal']['abs_diff']}")
    check("G1b central_delivered bit-exact 0.0",
          close((g1.get("G1b") or {}).get("abs_diff"), 0.0, 0))
    sel = g1.get("G1c_selection") or {}
    check("G1c selects the E3 tree for both Design-on methods",
          all(sel.get(m, {}).get("selected") == "tree" for m in ("raven", "twostage_hajek")),
          json.dumps(sel))
    check("G1c 6/6 match the tree, 0/6 match the repro CSV",
          all(r["match_tree"] for r in g1["G1c"]) and not any(r["match_csv"] for r in g1["G1c"]))


def s2b_drift_lead():
    print("\n== S2b  debt_cal drift: checkpoint_hash is the discriminator ==")
    base = OUT / "repair" / "C0_frozen" / "sensorscope"
    for m, same_expected in (("fedasync_window", True), ("flamf_timealign_adapted", True),
                             ("debt_cal", False)):
        f = FROZEN_E3 / "sensorscope" / m / "seed30001" / "runtime_manifest.json"
        n = base / m / "seed30001" / "runtime_manifest.json"
        if not (f.is_file() and n.is_file()):
            check(f"{m}: manifests present", False)
            continue
        a, b = rd_json(f), rd_json(n)
        check(f"{m}: EventTrace_hash identical", a["EventTrace_hash"] == b["EventTrace_hash"])
        check(f"{m}: checkpoint_hash {'identical' if same_expected else 'DIFFERS'}",
              (a["checkpoint_hash"] == b["checkpoint_hash"]) is same_expected,
              "same" if a["checkpoint_hash"] == b["checkpoint_hash"] else "diff")
        check(f"{m}: config_hash and metric_hash differ (non-diagnostic)",
              a["config_hash"] != b["config_hash"] and a["metric_hash"] != b["metric_hash"])
    p = ROOT / "src" / "raven_mcs" / "aggregation" / "p2_cvxpy.py"
    check("p2_cvxpy.py exists and postdates the frozen batch",
          p.is_file() and p.stat().st_mtime > (FROZEN_E3 / "sensorscope" / "debt_cal" /
                                               "seed30001" / "final_metrics.json").stat().st_mtime,
          f"p2_cvxpy={p.stat().st_mtime:.0f} > frozen="
          f"{(FROZEN_E3 / 'sensorscope' / 'debt_cal' / 'seed30001' / 'final_metrics.json').stat().st_mtime:.0f}")


def s3_e1():
    print("\n== S3  E1 rebuild ==")
    asrt = rd_csv(OUT / "E1_ASSERTIONS.csv")
    check("E1 assertions: 80 runs x 80 windows", len(asrt) == 80, f"got {len(asrt)}")
    bad = [r for r in asrt if r["assert_pass"] not in ("True", "true", "1")]
    check("every E1 assertion passed", not bad, f"{len(bad)} failed")
    for m in ("fedavg_window", "fedasync_window", "flamf_timealign_adapted", "debt_cal"):
        rs = [r for r in asrt if r["method"] == m]
        check(f"{m}: 1600/1600 windows identical",
              sum(int(r["identical"]) for r in rs) == 1600
              and sum(int(r["compared"]) for r in rs) == 1600, f"n={len(rs)}")

    expect = {"fedavg_window": (1.188238, 1.111932, -6.4217),
              "fedasync_window": (1.188279, 1.111924, -6.4257),
              "flamf_timealign_adapted": (1.188435, 1.112002, -6.4314),
              "debt_cal": (1.189318, 1.114378, -6.3011)}
    for m, (old_e, new_e, rel_e) in expect.items():
        old = mean_rmse(FROZEN_E3 / "uair" / m)
        new = mean_rmse(OUT / "repair" / "C0_frozen" / "uair" / m)
        rel = (new - old) / old * 100
        check(f"{m}: old {old_e} -> new {new_e} ({rel_e} %)",
              close(old, old_e, 5e-7) and close(new, new_e, 5e-7) and close(rel, rel_e, 5e-4),
              f"old={old:.6f} new={new:.6f} rel={rel:.4f}%")
    moves = []
    for m in expect:
        old = mean_rmse(FROZEN_E3 / "uair" / m)
        new = mean_rmse(OUT / "repair" / "C0_frozen" / "uair" / m)
        moves.append((new - old) / old * 100)
    check("all four moves lie in [-6.44, -6.29] % (method-independent shift)",
          all(-6.44 <= x <= -6.29 for x in moves), f"{[round(x,4) for x in moves]}")
    audit = {int(r["seed"]): float(r["RMSE_mu"]) for r in rd_csv(AUDIT_PER_SEED)}
    got = mean_rmse(OUT / "repair" / "C0_frozen" / "uair" / "fedavg_window")
    aud = sum(audit[s] for s in SEEDS) / len(SEEDS)
    check("E1 FedAvg reproduces results_table2_audit mean 1.1119 to 4 dp",
          close(round(got, 4), round(aud, 4), 0), f"E1={got:.6f} audit={aud:.6f}")


def s4_e2_r1():
    print("\n== S4  E2 / R1 ==")
    e2 = {r["method"]: r for r in rd_csv(OUT / "E2_UAIR_SUMMARY.csv")}
    r1 = {"fedavg_window": 1.111932, "fedasync_window": 1.111924,
          "flamf_timealign_adapted": 1.112002, "debt_cal": 1.114378,
          "fedau_window": 1.112813, "obsuse_window": 1.112034, "raven_wo_design": 1.113059}
    for m, v in r1.items():
        check(f"R1 {m} RMSE_mu_std = {v}",
              close(float(e2[m]["RMSE_mu_std_mean"]), v, 5e-7),
              f"got {float(e2[m]['RMSE_mu_std_mean']):.6f}")
    t = {"fedavg_window": (1.169045, 1.044620, 1.313777),
         "raven_wo_design": (1.170275, 1.016515, 1.294934),
         "debt_cal": (1.171764, 1.017533, 1.294779)}
    for m, (wg, dg, dc) in t.items():
        check(f"R1 {m} WG/Delta_group/Delta_c_s",
              close(float(e2[m]["WorstGroupRMSE_std_mean"]), wg, 5e-7)
              and close(float(e2[m]["Delta_group_mean"]), dg, 5e-7)
              and close(float(e2[m]["Delta_c_s_mean"]), dc, 5e-7))
    found = [m for m in r1 if m not in ("debt_cal", "raven_wo_design")
             and abs(float(e2[m]["RMSE_mu_std_mean"]) - 1.113059) < 0.0012]
    check("prediction is a tie: the other 5 comparators are within 0.11 % of RAVEN-NoDesign",
          len(found) == 5, f"within-band comparators = {len(found)}")

    sealed = {r["method"]: r for r in rd_csv(SEALED) if r["dataset"] == "U-Air"}
    for m, key in (("central_all", "Central-All"), ("central_delivered", "Central-Delivered")):
        got = float(e2[m]["RMSE_mu_phys_mean"])
        want = float(sealed[key]["RMSE_mu_mean"])
        check(f"N7 arithmetic: {m} physical == sealed {key} ({want})",
              close(got, want, 5e-6), f"got {got:.6f}")
    for m in ("central_all", "central_delivered"):
        check(f"{m}: phys == std x sigma",
              close(float(e2[m]["RMSE_mu_phys_mean"]),
                    float(e2[m]["RMSE_mu_std_mean"]) * SIGMA, 1e-6))


def s5_e3_r2():
    print("\n== S5  E3 / R2 ==")
    cov = rd_csv(OUT / "P2_COVERAGE.csv")[0]
    check("P2 coverage U-Air: 180 / 72.6111 / 63-79",
          int(cov["runs"]) == 180 and close(float(cov["mean_active_windows"]), 72.6111, 5e-5)
          and int(cov["min_active_windows"]) == 63 and int(cov["max_active_windows"]) == 79,
          json.dumps(cov))
    # the definition itself: reproduce BOTH published rows from the untouched trees
    def pub(ds, nwin):
        vals = []
        for d in sorted((FROZEN_E3 / ds).iterdir()):
            for sd in sorted(d.glob("seed*")):
                f = sd / "window_metrics.json"
                if f.is_file():
                    vals.append(sum(1 for w in rd_json(f) if w.get("active")))
        return len(vals), sum(vals) / len(vals), min(vals), max(vals)
    n, m, lo, hi = pub("uair", 80)
    check("guard: published U-Air row reproduces as 180 / 70.1000 / 63-75",
          n == 180 and close(m, 70.10, 5e-5) and (lo, hi) == (63, 75), f"{n}/{m}/{lo}-{hi}")
    n, m, lo, hi = pub("sensorscope", 100)
    check("guard: published SensorScope row reproduces as 180 / 93.8500 / 88-98",
          n == 180 and close(m, 93.85, 5e-5) and (lo, hi) == (88, 98), f"{n}/{m}/{lo}-{hi}")

    pa = {(r["comparator"], r["slice"]): r for r in rd_csv(OUT / "PAIRED_STATS.csv")}
    exp = {("fedavg_window", "TEST", "Delta_group_rel_mean"): -3.078,
           ("fedavg_window", "ALL20", "Delta_group_rel_mean"): -2.711,
           ("debt_cal", "TEST", "Delta_group_rel_mean"): -0.052,
           ("debt_cal", "ALL20", "Delta_group_rel_mean"): -0.089,
           ("debt_cal", "TEST", "Delta_c_s_rel_mean"): -0.055,
           ("debt_cal", "ALL20", "Delta_c_s_rel_mean"): 0.015,
           ("fedau_window", "ALL20", "Delta_group_rel_mean"): -3.733,
           ("obsuse_window", "ALL20", "Delta_c_s_rel_mean"): -2.143,
           ("fedavg_window", "TEST", "RMSE_mu_std_rel_mean"): 0.545,
           ("obsuse_window", "TEST", "WorstGroupRMSE_std_rel_mean"): 0.443}
    for (c, sl, met), v in exp.items():
        check(f"R2 {c} {sl} {met} = {v} %",
              close(float(pa[(c, sl)][met]) * 100, v, 2e-3),
              f"got {float(pa[(c,sl)][met])*100:.3f}")
    sig = {c for (c, sl) in pa if sl == "TEST"
           and float(pa[(c, sl)]["Delta_group_holm"]) < 0.05}
    check("Delta_group significant against exactly 5 of 6 comparators, Debt-Cal excluded",
          sig == {"fedavg_window", "fedasync_window", "flamf_timealign_adapted",
                  "fedau_window", "obsuse_window"}, f"significant set={sorted(sig)}")
    check("Delta_group NOT significant vs Debt-Cal (Holm p 0.41 ALL20)",
          close(float(pa[("debt_cal", "ALL20")]["Delta_group_holm"]), 0.411533, 1e-5),
          f"got {pa[('debt_cal','ALL20')]['Delta_group_holm']}")
    ns = [c for (c, sl) in pa if sl == "TEST" and float(pa[(c, sl)]["RMSE_mu_std_holm"]) < 0.05]
    check("RMSE_mu significant against nothing", not ns, f"{sorted(ns)}")


def s6_deviations():
    print("\n== S6  Declared deviations ==")
    g2 = rd_json(OUT / "G2_REPORT.json")
    check("G2 recorded 0 executed runs", all(r["status"] == "NOT_EXECUTED" for r in g2["runs"]),
          f"{len(g2['runs'])} rows")
    check("G2 blocker mentions the missing dataset loader",
          "load_paper_dataset" in g2.get("blocker", ""))
    txt = " ".join(REPORT.read_text(encoding="utf-8").split())  # normalize line wrapping
    for key in ("NOT_COUNTED", "store_fields", "no run currently honours", "no `src/` change"):
        check(f"report documents: {key}", key in txt)


def s7_manifest():
    print("\n== S7  Artifact manifest ==")
    man = OUT / "MANIFEST.sha256"
    if not man.is_file():
        check("MANIFEST.sha256 present", False, "generate it before handing over")
        return
    bad = 0
    n = 0
    for line in man.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        h, name = line.split(None, 1)
        name = name.strip().lstrip("*")
        p = OUT / name if not name.startswith("scripts/") else ROOT / name
        if not p.is_file():
            bad += 1
            print(f"   missing {name}")
            continue
        n += 1
        if hashlib.sha256(p.read_bytes()).hexdigest()[:16] != h[:16]:
            bad += 1
            print(f"   hash drift {name}")
    check(f"manifest verifies ({n} files)", bad == 0, f"{bad} bad")


def s8_deep_holes():
    print("\n== S8  --deep: rebuild pi^tar from the runner path ==")
    sys.path.insert(0, str(ROOT / "src"))
    from raven_mcs.correction.pi_target import build_pi_target
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
    for name, pairs, zero in (("uair", 288, 72), ("sensorscope", 440, 0)):
        ds = load_paper_dataset(ROOT, name)
        mp = load_spatial_to_client(ROOT, name)
        sealed, _ = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=name, root=ROOT)
        a = sealed.copy()
        if "target_group_main" not in a.columns:
            a["target_group_main"] = a["target_group"].astype(str)
        fr = build_pi_target(a, mp, split="test")
        tar = {(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
               for r in fr.itertuples()}
        train = sealed.loc[sealed["split"].astype(str) == "train"]
        sbc: dict[str, set[str]] = {}
        for r in train.itertuples(index=False):
            c = mp.get(str(r.spatial_id))
            if c:
                sbc.setdefault(c, set()).add(str(r.opportunity_stratum))
        support = {(c, s) for c, ss in sbc.items() for s in ss}
        got_zero = sum(1 for k in support if tar.get(k, 0.0) <= 0.0)
        check(f"{name}: runner path gives {pairs} pairs / {zero} holes",
              len(support) == pairs and got_zero == zero, f"{len(support)}/{got_zero}")


def s9_review_checks():
    """C1/C2/C3/G2 checks added after independent review."""
    print("\n== S9  Review-driven checks ==")
    c1 = rd_json(OUT / "C1_RAVEN_WO_DESIGN_REPRO.json")
    check("C1: frozen U-Air raven_wo_design reproduces bit-exactly",
          len(c1["rows"]) == 2 and all(r["all_bit_equal"] for r in c1["rows"]),
          f"{[r['all_bit_equal'] for r in c1['rows']]}")
    for r in c1["rows"]:
        for k in ("RMSE_mu", "Delta_group", "Delta_c_s"):
            check(f"C1 seed{r['seed']} {k} abs_diff == 0.0", r[f"{k}_abs_diff"] == 0.0,
                  f"{r[f'{k}_abs_diff']}")

    c2 = rd_json(OUT / "C2_VDIAG_SANITISATION.json")
    t = c2["totals"]
    check("C2: 171 solve_p2 calls instrumented", t["calls"] == 171, f"{t['calls']}")
    check("C2: zero calls with non-finite variance_diag", t["calls_with_nonfinite"] == 0)
    check("C2: zero calls with negative variance_diag", t["calls_with_negative"] == 0)
    check("C2: smallest variance_diag seen is 0.0116",
          close(t["min_seen"], 0.011557369275859935, 1e-12), f"{t['min_seen']}")

    c3 = rd_json(OUT / "C3_TWO_BY_TWO.json")
    check("C3: 2x2 arm recorded BLOCKED", c3.get("status") == "BLOCKED")
    check("C3: blocker names the half-applied diff",
          "half-applied" in c3.get("root_cause", "")
          and "counterfactual_audit" in json.dumps(c3.get("raised_from", {})))
    feas = ROOT / "src" / "raven_mcs" / "aggregation" / "feasibility.py"
    src = feas.read_text(encoding="utf-8")
    check("C3 claim: validate_p2_lambdas gates on instant_calibration",
          "instant_calibration" in src and "when instant_calibration=False" in src)

    g2 = rd_json(OUT / "G2_RUN_REPORT.json")
    check("G2run: 6 hybrid cells executed", len(g2["rows"]) == 6, f"{len(g2['rows'])}")
    check("G2run: every hybrid cell BIT-IDENTICAL",
          all(r["comparison"].startswith("BIT-IDENTICAL") for r in g2["rows"]),
          json.dumps([r["comparison"][:14] for r in g2["rows"]]))
    for r in g2["rows"]:
        for k in ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s"):
            check(f"G2run {r['block']}/{r['method']} {k} bit-equal",
                  r.get(f"{k}_bit_equal") is True, f"{r.get(f'{k}_bit_equal')}")

    # SS4.4 identities, and the SS0.3 erratum that reinterprets the first one
    trees_ = {"e3": FROZEN_E3, "e4": E4, "fedau": FEDAU, "obsuse": OBSUSE}

    def series(tree: str, method: str, key: str):
        d = trees_[tree] / "uair" / method
        out = []
        for s in SEEDS:
            f = d / f"seed{s}" / "final_metrics.json"
            if not f.is_file():
                return None
            out.append(float(rd_json(f)[key]))
        return out

    for a, ta, b, tb in (("raven_wo_inst", "e4", "twostage_hajek", "e3"),
                         ("inst_cal", "e3", "raven_wo_debt", "e4")):
        for key in ("RMSE_mu", "Delta_group"):
            va, vb = series(ta, a, key), series(tb, b, key)
            ok = va is not None and vb is not None and max(abs(x - y) for x, y in zip(va, vb)) == 0.0
            check(f"SS4.4 identity {a} == {b} on {key}", ok)

    # --- SS0.3 erratum: the wo_inst arm is the superseded one, and Table IV is right
    rep = REPORT.read_text(encoding="utf-8")
    for k in ("Revision 3 is an erratum", "### 0.3 Erratum", "Table IV is correct",
              "is the superseded artifact", "instant calibration is\nnot a lever"):
        check(f"report carries erratum marker {k!r}", k in rep)

    dec = ROOT / "artifacts" / "e4_ablation_semantic_integrity_repair_r1" / "E4_WO_INST_FINAL_DECISION.json"
    d = rd_json(dec)
    check("E4_WO_INST_FINAL_DECISION records proven_invalid",
          d.get("proven_invalid") is True, f"{d.get('proven_invalid')}")
    check("E4_WO_INST_FINAL_DECISION authorises 40 corrective reruns",
          d.get("authorized_corrective_reruns") == 40, f"{d.get('authorized_corrective_reruns')}")

    inval = E4 / "uair" / "raven_wo_inst" / "seed30001" / "p2_invocation_states.json"
    sib = E4 / "uair" / "raven_wo_obs" / "seed30001" / "p2_invocation_states.json"
    check("invalidated wo_inst arm logged ZERO P2 invocations",
          inval.is_file() and inval.stat().st_size < 10,
          f"{inval.stat().st_size if inval.is_file() else 'absent'} B")
    check("a sibling E4 arm logged a large P2 invocation record",
          sib.is_file() and sib.stat().st_size > 100_000,
          f"{sib.stat().st_size if sib.is_file() else 'absent'} B")

    claim = ROOT / "artifacts" / "e4_wo_inst_reference_penalty_final_correction_r1" / "E4_WO_INST_FINAL_CLAIM.json"
    if claim.is_file():
        cells = rd_json(claim)["cells"]
        base = {"UAir_Delta_group": 1.092362, "SensorScope_Delta_group": 1.013943}
        printed = {"UAir_Delta_group": -0.089, "SensorScope_Delta_group": -0.260}
        for k, b in base.items():
            pct = cells[k]["mean_paired_diff"] / b * 100
            check(f"corrective rerun reproduces Table IV ({k} {printed[k]})",
                  abs(pct - printed[k]) < 2e-3, f"implied {pct:+.4f}%")
    else:
        check("corrective-rerun claim file present", False, "generate it before handing over")


def s10_worktree():
    print("\n== S10  Working-tree provenance ==")
    p = OUT / "WORKTREE_DIFF.sha256"
    check("WORKTREE_DIFF.sha256 present", p.is_file(),
          "records the hash of each uncommitted src/ diff at hand-over time")


def s11_manuscript():
    """SS12: every replaced cell must match the artifacts, and the old values must be gone."""
    print("\n== S11  Manuscript cells vs artifacts ==")
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean" / "main.tex").read_text(encoding="utf-8")
    app = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean" / "appendix.tex").read_text(encoding="utf-8")
    flat_m = " ".join(main.split())
    flat_a = " ".join(app.split())

    e2 = {r["method"]: r for r in rd_csv(OUT / "E2_UAIR_SUMMARY.csv")}

    def v(m, c, p=4):
        return f"{float(e2[m][c]):.{p}f}"

    # main.tex Table III, U-Air FedAvg-Window row
    for cell in (v("fedavg_window", "RMSE_mu_std_mean"), v("fedavg_window", "WorstGroupRMSE_std_mean"),
                 v("fedavg_window", "Delta_group_mean"), v("fedavg_window", "Delta_c_s_mean")):
        check(f"main.tex carries U-Air FedAvg cell {cell}", cell in flat_m)
    for old in ("1.1882", "1.2596", "1.1218", "1.2621"):
        check(f"main.tex no longer carries the old U-Air FedAvg cell {old}",
              f"${old}$" not in flat_m)

    # appendix tab:app_e3_uair rows
    for m in ("fedavg_window", "fedasync_window", "flamf_timealign_adapted", "debt_cal"):
        cells = [v(m, c) for c in ("RMSE_mu_std_mean", "Delta_group_mean", "Delta_c_s_mean")]
        check(f"appendix carries {m} row {cells}", all(c in flat_a for c in cells))
    for old in ("$1.1883", "$1.1884", "$1.1893", "$1.0976"):
        check(f"appendix no longer carries the old row value {old}", old not in flat_a)

    # tab:app_block_rmse, UA FedAvg row
    blk = [f"{float(x):.4f}" for x in (
        sum(float(r[f"RMSE_block{b}_std"]) for r in
            rd_csv(OUT / "E2_UAIR_CELLS.csv")
            if r["status"] == "OK" and r["method"] == "fedavg_window") / 20 for b in range(4))]
    check(f"appendix carries the rebuilt UA block row {blk}", all(c in flat_a for c in blk))
    check("appendix no longer carries the old UA block row ($1.2596{\\pm}0.0709$)",
          "$1.2596{\\pm}0.0709$" not in flat_a.replace(" ", ""))

    # tab:app_p2_coverage
    check("appendix p2_coverage U-Air row is 72.61 / 63--79",
          "72.61 & 63--79" in flat_a)
    check("appendix p2_coverage no longer says 70.10 / 63--75",
          "70.10 & 63--75" not in flat_a)

    # prose
    check("the voided '-6.17%' claim is gone from main.tex", "6.17\\%" not in flat_m)
    check("the '-9.11%' sentence is restated within the Design family",
          "family-internal comparison" in flat_m)
    check("the Design-support restriction is stated for Local-Hajek",
          "both restrict the active set to the Design support" in flat_m)
    check("N7 scale disclosure present in main.tex",
          "17.363" in flat_m and "575.776" in flat_m)
    check("the six-comparator qualification is present",
          "ties Debt-Cal on both" in flat_m)
    check("the three feasibility-audit counts were left untouched",
          "778" in flat_a and "6438" in flat_a)

    # SS12 / review M2-M5: the recoverable-gain ceiling subsection
    for k in ("Recoverable-Gain Ceiling", "H\\ge0.5\\%", "It did\nnot fire",
              "0.217\\%", "270", "0.104\\%", "0.251\\%", "15$--$21", "0.17$--$0.36",
              "0.70$--$0.80"):
        check(f"main.tex ceiling passage carries {k!r}", k in main)
    check("the ceiling subsection sits before Limitations",
          main.index("Recoverable-Gain Ceiling") < main.index("\\subsection{Limitations}"))
    for rd, fn, key in (("round_v1", "H_DECISION.json", None), ("round_u1", "U1_DECISION.json", None)):
        d = json.loads((ROOT / "results_h_headroom" / rd / fn).read_text(encoding="utf-8"))
        check(f"{rd}: decision STOP, no GO cell, bar 0.5%",
              d["decision"] == "STOP" and d["go_cells"] == [] and d["go_bar"] == 0.005)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep", action="store_true")
    args = ap.parse_args()
    print(f"verifying {REPORT.name}")
    s0_amendment()
    s0b_boundary_and_env()
    s1_g0()
    s2_g1()
    s2b_drift_lead()
    s3_e1()
    s4_e2_r1()
    s5_e3_r2()
    s6_deviations()
    s7_manifest()
    s9_review_checks()
    s10_worktree()
    s11_manuscript()
    if args.deep:
        s8_deep_holes()
    fails = [n for ok, n, _ in _results if not ok]
    print(f"\n==== {len(_results) - len(fails)}/{len(_results)} checks passed ====")
    if fails:
        print("FAILED:")
        for n in fails:
            print("  -", n)
        return 1
    print("ALL CLAIMS RE-DERIVED FROM STORED ARTIFACTS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
