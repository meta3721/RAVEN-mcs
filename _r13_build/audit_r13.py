#!/usr/bin/env python
# ASCII-only recomputation for the r13 numeric traceability audit.
# READ-ONLY with respect to the workspace except for this script's own output in _r13_build.
import csv, hashlib, json, os, sys, math, statistics as st

ROOT = r"C:\Cursor\raven.mcs"
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def sha256_pref(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def rd_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


ES = os.path.join(ROOT, "results_estimand_selection", "round_v1")
GD = os.path.join(ROOT, "results_gate_dose", "round_v2")

FILES = [
    os.path.join(ES, "SELECTION_DECISION.json"),
    os.path.join(ES, "tables", "RISK_ROWS.csv"),
    os.path.join(ES, "tables", "SELECTION.csv"),
    os.path.join(ES, "tables", "SELECTION_SUMMARY.csv"),
    os.path.join(ES, "PART_I_REPORT.md"),
    os.path.join(ES, "WEIGHTS.csv"),
    os.path.join(GD, "DOSE_DECISION.json"),
    os.path.join(GD, "tables", "DOSE_SUMMARY.csv"),
    os.path.join(GD, "tables", "DOSE_SLOPES.csv"),
    os.path.join(GD, "tables", "DOSE_CELLS.csv"),
    os.path.join(GD, "tables", "DOSE_CELLS_PAIRED.csv"),
    os.path.join(GD, "tables", "GATE_POLICY.csv"),
    os.path.join(GD, "GATE.json"),
    os.path.join(GD, "GATE_AMENDMENT.md"),
    os.path.join(GD, "M0_RUNS.json"),
    os.path.join(GD, "DOSE_RUNS.json"),
    os.path.join(ROOT, "results_gate_dose", "round_v1", "RHO.csv"),
    os.path.join(ROOT, "results_gate_dose", "round_v1", "MASKS.json"),
    os.path.join(ROOT, "results_gate_dose", "round_v1", "TARGET_WIRING.json"),
]
p("== sha256 (first 16 hex) ==")
for fp in FILES:
    if os.path.exists(fp):
        p("  ", sha256_pref(fp), os.path.relpath(fp, ROOT))
    else:
        p("   MISSING", os.path.relpath(fp, ROOT))
p("")

# ---------------- Part A: RISK_ROWS ----------------
p("=" * 70)
p("A. RISK_ROWS.csv / SELECTION_DECISION.json")
p("=" * 70)
rows = rd_csv(os.path.join(ES, "tables", "RISK_ROWS.csv"))
p("RISK_ROWS rows:", len(rows))
datasets = sorted({r["dataset"] for r in rows})
methods = sorted({r["method"] for r in rows})
seeds = sorted({int(r["seed"]) for r in rows})
p("datasets:", datasets)
p("n methods (overall):", len(methods))
for ds in datasets:
    ms = sorted({r["method"] for r in rows if r["dataset"] == ds})
    ss = sorted({int(r["seed"]) for r in rows if r["dataset"] == ds})
    p("  %-12s methods=%d seeds=%d rows=%d" % (ds, len(ms), len(ss),
      sum(1 for r in rows if r["dataset"] == ds)))
p("method names:")
for m in methods:
    p("   -", m)

# recompute b = (R_arr - R_mu)/R_mu and the printed b column
p("")
p("per (dataset, method): mean b over 20 seeds, recomputed from R_mu/R_arr, "
  "and mean of printed 'b' column; also mean of b_R")
p("%-12s %-26s %14s %14s %14s %14s" % ("dataset", "method",
   "mean_b_recomp", "mean_b_printed", "mean_bR_printed", "max|diff|"))
summary = {}
for ds in datasets:
    for m in sorted({r["method"] for r in rows if r["dataset"] == ds}):
        sel = [r for r in rows if r["dataset"] == ds and r["method"] == m]
        rec = []
        prn = []
        br = []
        md = 0.0
        for r in sel:
            Rmu = float(r["R_mu"]); Rarr = float(r["R_arr"])
            rec.append((Rarr - Rmu) / Rmu)
            prn.append(float(r["b"]))
            br.append(float(r["b_R"]))
            md = max(md, abs(rec[-1] - prn[-1]))
        summary[(ds, m)] = dict(n=len(sel), mean_b_recomp=st.fmean(rec),
                                mean_b_printed=st.fmean(prn),
                                mean_bR=st.fmean(br), max_abs_diff=md,
                                min_b=min(prn), max_b=max(prn))
        p("%-12s %-26s %14.10f %14.10f %14.10f %14.2e" % (
            ds, m, st.fmean(rec), st.fmean(prn), st.fmean(br), md))

for ds in datasets:
    vals = [summary[(ds, m)]["mean_b_printed"] for m in sorted(
        {r["method"] for r in rows if r["dataset"] == ds})]
    p("")
    p("%s: min mean_b = %.10f  (%.4f%%)  via %s" % (
        ds, min(vals), 100 * min(vals),
        [m for m in sorted({r["method"] for r in rows if r["dataset"] == ds})
         if summary[(ds, m)]["mean_b_printed"] == min(vals)]))
    p("%s: max mean_b = %.10f  (%.4f%%)  via %s" % (
        ds, max(vals), 100 * max(vals),
        [m for m in sorted({r["method"] for r in rows if r["dataset"] == ds})
         if summary[(ds, m)]["mean_b_printed"] == max(vals)]))

# cross-check against SELECTION_DECISION.json method_b
dec = json.load(open(os.path.join(ES, "SELECTION_DECISION.json"), encoding="utf-8"))
p("")
p("cross-check mean_b vs SELECTION_DECISION.json -> summaries[].method_b[].mean_b")
for s in dec["summaries"]:
    ds = s["dataset"]
    p("  dataset=%s n_methods=%s n_seeds=%s" % (ds, s.get("n_methods"), s.get("n_seeds")))
    for m, d in sorted(s["method_b"].items()):
        mine = summary[(ds, m)]["mean_b_printed"]
        p("    %-26s json=%.10f  my_mean_of_printed_b=%.10f  diff=%.2e" % (
            m, d["mean_b"], mine, abs(d["mean_b"] - mine)))

# ---------------- Part B: SELECTION.csv ----------------
p("")
p("=" * 70)
p("B. SELECTION.csv per-seed agreement")
p("=" * 70)
sel = rd_csv(os.path.join(ES, "tables", "SELECTION.csv"))
p("rows:", len(sel), "datasets:", sorted({r["dataset"] for r in sel}))
for ds in sorted({r["dataset"] for r in sel}):
    sub = [r for r in sel if r["dataset"] == ds]
    agr = [r for r in sub if r["m_arr_arr"] == r["m_mu_arr"]]
    agrR = [r for r in sub if r["m_arr_arrR"] == r["m_mu_arrR"]]
    bad = [r for r in sub if r["m_arr_arr"] != r["m_mu_arr"]]
    p("%s: n_seeds=%d  agreement(m_arr==m_mu)=%d  agreement(arrR)=%d  mismatches=%d" % (
        ds, len(sub), len(agr), len(agrR), len(bad)))
    p("   distinct m_mu values:", sorted({r["m_mu_arr"] for r in sub}))
    p("   distinct m_arr values:", sorted({r["m_arr_arr"] for r in sub}))
    p("   d_arr values:", sorted({r["d_arr"] for r in sub}))
    p("   tau_arr: min=%s max=%s ; seeds with tau<1: %s" % (
        min(float(r["tau_arr"]) for r in sub), max(float(r["tau_arr"]) for r in sub),
        [r["seed"] for r in sub if float(r["tau_arr"]) < 1.0]))
    for r in sub:
        p("     seed %s m_arr=%-24s m_mu=%-24s d=%s reg=%s tau=%s" % (
            r["seed"], r["m_arr_arr"], r["m_mu_arr"], r["d_arr"], r["reg_arr"], r["tau_arr"]))

# ---------------- Part C: DOSE ----------------
p("")
p("=" * 70)
p("C. DOSE_SUMMARY.csv / DOSE_CELLS.csv / DOSE_SLOPES.csv")
p("=" * 70)
dsm = rd_csv(os.path.join(GD, "tables", "DOSE_SUMMARY.csv"))
p("DOSE_SUMMARY rows:", len(dsm), "header:", list(dsm[0].keys()))
p("%-12s %-6s %12s %12s %12s %12s %12s %12s %12s" % (
    "dataset", "level", "rho", "rRMSE_mean%", "rRMSE_lo%", "rRMSE_hi%",
    "rdgroup%", "rdcs%", "rTail%"))
for r in dsm:
    p("%-12s %-6s %12.6f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f" % (
        r["dataset"], r["level"], float(r["rho"]), 100 * float(r["r_RMSE_mean"]),
        100 * float(r["r_RMSE_ci_lo"]), 100 * float(r["r_RMSE_ci_hi"]),
        100 * float(r["r_dgroup_mean"]), 100 * float(r["r_dcs_mean"]),
        100 * float(r["r_Tail_mean"])))

cells = rd_csv(os.path.join(GD, "tables", "DOSE_CELLS.csv"))
p("")
p("DOSE_CELLS rows:", len(cells), "header:", list(cells[0].keys()))
lev = sorted({(r["dataset"], r["level"]) for r in cells},
             key=lambda t: (t[0], float(t[1])))
p("levels actually run (dataset, level, n_rows, n_seeds):")
for ds, lv in lev:
    sub = [r for r in cells if r["dataset"] == ds and r["level"] == lv]
    p("   %-12s m=%-5s rows=%-4d seeds=%d" % (
        ds, lv, len(sub), len({r["seed"] for r in sub})))

# recompute r_RMSE per cell as (raven - raven_wo_design)/raven_wo_design
p("")
p("recompute per-cell r_RMSE = (RMSE_mu[raven] - RMSE_mu[raven_wo_design]) / RMSE_mu[raven_wo_design]")
p("%-12s %-6s %12s %12s %12s %12s" % ("dataset", "level", "mean%", "min%", "max%", "n"))
bykey = {}
for r in cells:
    bykey.setdefault((r["dataset"], r["level"], r["seed"]), {})[r["arm"]] = r
rec_means = []
for ds, lv in lev:
    vals = []
    for (d2, l2, sd), arms in bykey.items():
        if d2 != ds or l2 != lv:
            continue
        if "raven" in arms and "raven_wo_design" in arms:
            a = float(arms["raven"]["RMSE_mu"]); b = float(arms["raven_wo_design"]["RMSE_mu"])
            vals.append((a - b) / b)
    if vals:
        rec_means.append((ds, lv, st.fmean(vals), min(vals), max(vals), len(vals)))
        p("%-12s %-6s %12.4f %12.4f %12.4f %12d" % (
            ds, lv, 100 * st.fmean(vals), 100 * min(vals), 100 * max(vals), len(vals)))

p("")
p("compare recomputed per-level mean r_RMSE with DOSE_SUMMARY r_RMSE_mean")
for (ds, lv, mm, mn, mx, n) in rec_means:
    tgt = [r for r in dsm if r["dataset"] == ds and r["level"] == lv]
    if tgt:
        p("  %-12s %-6s recomputed=%+.10f  summary=%+.10f  diff=%.2e" % (
            ds, lv, mm, float(tgt[0]["r_RMSE_mean"]),
            abs(mm - float(tgt[0]["r_RMSE_mean"]))))

# alternative definition check
p("")
p("alternative r_RMSE via (raven_wo_design - raven)/raven, per level (to test sign convention)")
for ds, lv in lev:
    vals = []
    for (d2, l2, sd), arms in bykey.items():
        if d2 != ds or l2 != lv:
            continue
        a = float(arms["raven"]["RMSE_mu"]); b = float(arms["raven_wo_design"]["RMSE_mu"])
        vals.append((b - a) / a)
    if vals:
        p("  %-12s %-6s mean=%+.4f%%" % (ds, lv, 100 * st.fmean(vals)))

# max over ALL sensorscope cells of r_RMSE
allv = []
for (ds, lv, sd), arms in bykey.items():
    if ds != "sensorscope":
        continue
    a = float(arms["raven"]["RMSE_mu"]); b = float(arms["raven_wo_design"]["RMSE_mu"])
    allv.append(((a - b) / b, lv, sd))
allv.sort()
p("")
p("SensorScope per-CELL r_RMSE: min=%+.4f%% (m=%s,seed=%s)  max=%+.4f%% (m=%s,seed=%s)  n=%d" % (
    100 * allv[0][0], allv[0][1], allv[0][2], 100 * allv[-1][0], allv[-1][1], allv[-1][2], len(allv)))
uav = []
for (ds, lv, sd), arms in bykey.items():
    if ds != "uair":
        continue
    a = float(arms["raven"]["RMSE_mu"]); b = float(arms["raven_wo_design"]["RMSE_mu"])
    uav.append(((a - b) / b, lv, sd))
uav.sort()
p("U-Air   per-CELL r_RMSE: min=%+.4f%% (m=%s,seed=%s)  max=%+.4f%% (m=%s,seed=%s)  n=%d" % (
    100 * uav[0][0], uav[0][1], uav[0][2], 100 * uav[-1][0], uav[-1][1], uav[-1][2], len(uav)))

# max |r_RMSE| per level
p("")
p("SensorScope per-level MAX positive cell r_RMSE (is 0.17% a cell bound or a level-mean bound?)")
for ds, lv in lev:
    v = [x for x in allv if x[1] == lv] if ds == "sensorscope" else [x for x in uav if x[1] == lv]
    if v:
        p("  %-12s m=%-5s mean=%+.4f%%  max_cell=%+.4f%%  p95_cell=%+.4f%%" % (
            ds, lv, 100 * st.fmean([x[0] for x in v]), 100 * max(x[0] for x in v),
            100 * sorted(x[0] for x in v)[int(0.95 * (len(v) - 1))]))

# ---------------- Part F: slopes ----------------
p("")
p("=" * 70)
p("F. DOSE_SLOPES.csv")
p("=" * 70)
sl = rd_csv(os.path.join(GD, "tables", "DOSE_SLOPES.csv"))
p("%-12s %-26s %6s %14s %14s %14s   %-8s" % (
    "dataset", "endpoint", "ncells", "slope", "ci_lo", "ci_hi", "label"))
for r in sl:
    p("%-12s %-26s %6s %14.6f %14.6f %14.6f   %-6s  rho*=%s [%s, %s]" % (
        r["dataset"], r["endpoint"], r["n_cells"], float(r["slope"]),
        float(r["slope_ci_lo"]), float(r["slope_ci_hi"]), r["label"],
        r["rho_star"], r["rho_star_ci_lo"], r["rho_star_ci_hi"]))

dd = json.load(open(os.path.join(GD, "DOSE_DECISION.json"), encoding="utf-8"))
p("")
p("DOSE_DECISION.json verbatim key readouts:")
p("  gate_law =", json.dumps(dd["gate_law"]))
p("  h1_labels =", json.dumps(dd["h1_labels"]))
p("  h2 =", json.dumps(dd["h2"]))
p("  gate.G1/G2/G3_amended =", dd["gate"]["G1"], dd["gate"]["G2"], dd["gate"]["G3_amended"])
p("  gate.G3_original_pass =", dd["gate"]["G3_original_pass"],
  " G3_original_tol_rel =", dd["gate"]["G3_original_tol_rel"],
  " G3_tol_rel =", dd["gate"]["G3_tol_rel"])
p("  gate.amended =", dd["gate"]["amended"], " amendment =", dd["gate"]["amendment"])
p("  gate.pass =", dd["gate"]["pass"])
p("  rho_star =", json.dumps(dd["rho_star"]))
p("  h3.label_w_eq =", dd["h3"]["label_w_eq"], " label_w_pred =",
  dd["h3"]["primary_w_pred"]["label"])
p("  h3.secondary_w_eq.label =", dd["h3"]["secondary_w_eq"]["label"])
p("  h3.uair_descriptive =", json.dumps(dd["h3"]["uair_descriptive"]))

p("")
p("GATE.json verbatim keys:")
gj = json.load(open(os.path.join(GD, "GATE.json"), encoding="utf-8"))
for k in sorted(gj):
    v = gj[k]
    if isinstance(v, (str, int, float, bool)) or v is None:
        p("   %s = %s" % (k, json.dumps(v)))

# ---------------- Part G: masks / target wiring ----------------
p("")
p("=" * 70)
p("G. MASKS.json levels, TARGET_WIRING.json, RHO.csv")
p("=" * 70)
mk = json.load(open(os.path.join(ROOT, "results_gate_dose", "round_v1", "MASKS.json"),
                    encoding="utf-8"))
for ds, d in mk["datasets"].items():
    ncand = len(d["candidates"])
    p("%s: n_candidates(pi_tar>0 keys)=%d rule=%s" % (ds, ncand, d["candidate_rule"]))
    for lv, ld in sorted(d["levels"].items(), key=lambda t: float(t[0])):
        nm = ld["n_masked"]
        p("   level %-5s m=%-5s n_masked=%-4d  n_masked/n_candidates=%.4f" % (
            lv, ld["m"], nm, nm / ncand))

rho_p = os.path.join(ROOT, "results_gate_dose", "round_v1", "RHO.csv")
if os.path.exists(rho_p):
    rho = rd_csv(rho_p)
    p("RHO.csv rows=%d header=%s" % (len(rho), list(rho[0].keys())))
    for r in rho:
        p("   ", json.dumps(r))

tw = json.load(open(os.path.join(ROOT, "results_gate_dose", "round_v1", "TARGET_WIRING.json"),
                    encoding="utf-8"))
p("TARGET_WIRING.json top-level keys:", list(tw.keys())[:20])
p(json.dumps(tw)[:3000])

with open(os.path.join(ROOT, "_r13_build", "audit_r13_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
print("\n[written] _r13_build/audit_r13_out.txt")
