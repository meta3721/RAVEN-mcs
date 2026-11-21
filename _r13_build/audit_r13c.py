#!/usr/bin/env python
# ASCII-only: theta-scored cells and a stored-vs-scored sensitivity for claim A.
import csv, os, statistics as st

ROOT = r"C:\Cursor\raven.mcs"
ES = os.path.join(ROOT, "results_estimand_selection", "round_v1")
p = os.path.join(ES, "tables", "RISK_ROWS.csv")
with open(p, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

th = [r for r in rows if r["theta_scored"] == "True"]
print("theta_scored rows in RISK_ROWS.csv:", len(th))
for r in th:
    print("   %-12s %-26s seed %s stored=%s scored=%s rel_diff=%.4f" % (
        r["dataset"], r["method"], r["seed"], r["stored_RMSE_mu"], r["R_mu"],
        float(r["rel_diff_vs_stored"])))

print()
print("claim-A sensitivity: recompute b from stored_RMSE_mu instead of R_mu")
for ds in ("sensorscope", "uair"):
    ms = sorted({r["method"] for r in rows if r["dataset"] == ds})
    vals = []
    for m in ms:
        sub = [r for r in rows if r["dataset"] == ds and r["method"] == m]
        b2 = st.fmean((float(r["R_arr"]) - float(r["stored_RMSE_mu"])) / float(r["stored_RMSE_mu"])
                      for r in sub)
        vals.append((b2, m))
        print("   %-12s %-26s stored-based mean_b=%+.6f%%  printed-col mean=%+.6f%%" % (
            ds, m, 100 * b2,
            100 * st.fmean(float(r["b"]) for r in sub)))
    lo = min(vals); hi = max(vals)
    print("   -> %s stored-based min %+.4f%% (%s), max %+.4f%% (%s)" % (
        ds, 100 * lo[0], lo[1], 100 * hi[0], hi[1]))

print()
print("R_mu for uair theta-scored cells > or < stored? (sign of rel_diff)")
for r in th:
    print("   %-12s %-26s seed %s rel_diff=%+.6f" % (
        r["dataset"], r["method"], r["seed"], float(r["rel_diff_vs_stored"])))
