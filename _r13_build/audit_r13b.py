#!/usr/bin/env python
# ASCII-only: per-seed ranges, amendment/gate evidence, paired-cells header.
import csv, json, os, statistics as st

ROOT = r"C:\Cursor\raven.mcs"
ES = os.path.join(ROOT, "results_estimand_selection", "round_v1")
GD = os.path.join(ROOT, "results_gate_dose", "round_v2")


def rd(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


rows = rd(os.path.join(ES, "tables", "RISK_ROWS.csv"))
print("per-method per-seed b ranges (min over seeds, max over seeds):")
for ds in ("sensorscope", "uair"):
    for m in sorted({r["method"] for r in rows if r["dataset"] == ds}):
        v = [float(r["b"]) for r in rows if r["dataset"] == ds and r["method"] == m]
        print("  %-12s %-26s n=%2d min=%+.6f%% max=%+.6f%% mean=%+.6f%%" % (
            ds, m, len(v), 100 * min(v), 100 * max(v), 100 * st.fmean(v)))

print()
print("pooled per-seed b range across the 9 configs:")
for ds in ("sensorscope", "uair"):
    v = [float(r["b"]) for r in rows if r["dataset"] == ds]
    print("  %-12s n=%d min=%+.6f%% max=%+.6f%%" % (ds, len(v), 100 * min(v), 100 * max(v)))

print()
print("DOSE_SUMMARY level-mean r_RMSE ceilings:")
dsm = rd(os.path.join(GD, "tables", "DOSE_SUMMARY.csv"))
for ds in ("sensorscope", "uair"):
    sub = [r for r in dsm if r["dataset"] == ds]
    mx = max(float(r["r_RMSE_mean"]) for r in sub)
    print("  %-12s max_level_mean=%.6f%%  (at level %s) ; max ci_hi=%.6f%%" % (
        ds, 100 * mx,
        [r["level"] for r in sub if float(r["r_RMSE_mean"]) == mx],
        100 * max(float(r["r_RMSE_ci_hi"]) for r in sub)))
    for r in sub:
        print("      level %-5s rho=%.6f  mean=%+.6f%%  ci=[%+.6f%%, %+.6f%%]" % (
            r["level"], float(r["rho"]), 100 * float(r["r_RMSE_mean"]),
            100 * float(r["r_RMSE_ci_lo"]), 100 * float(r["r_RMSE_ci_hi"])))

print()
print("DOSE_CELLS_PAIRED.csv header + 3 rows:")
pc = rd(os.path.join(GD, "tables", "DOSE_CELLS_PAIRED.csv"))
print("  rows=%d header=%s" % (len(pc), list(pc[0].keys())))
for r in pc[:3]:
    print("   ", json.dumps(r))

print()
for name in ("GATE_G3.json", "GATE_ORIGINAL.json", "GATE_G3_AMENDED.json", "M0_RUNS.json",
             "GATE_G1.json", "GATE_G2.json"):
    p = os.path.join(GD, name)
    if not os.path.exists(p):
        print(name, "MISSING")
        continue
    j = json.load(open(p, encoding="utf-8"))
    print("==", name, "top-level:", list(j.keys())[:12])
    for k in ("pass", "pass_1e-6_original", "tol_rel", "tol_rel_original",
              "failed_gate", "n_new", "n_reused", "amended", "n_cells",
              "amendment", "authorized_by", "reason"):
        if k in j:
            print("    %s = %s" % (k, json.dumps(j[k])[:300]))
