import csv, pathlib, statistics as st, collections
f = pathlib.Path("artifacts/e2_traffic_formal_runs_r1/formal_results.csv")
rows = list(csv.DictReader(open(f, newline="", encoding="utf-8")))
print("cells:", len(rows), "| status:", collections.Counter(r["status"] for r in rows))
scen = ["balanced","opportunity_only","observation_only","usable_only","complete_aligned","complete_counteracting"]
print()
print("%-24s %8s %8s %9s | %s" % ("scenario","RMSE_mu","RMSE_rho","Gap_mis","per-method Gap_mis (raven vs fedavg)"))
for s in scen:
    rs = [r for r in rows if r["scenario"] == s]
    mu = st.mean(float(r["RMSE_mu"]) for r in rs)
    rho = st.mean(float(r["RMSE_rho"]) for r in rs)
    gap = st.mean(float(r["Gap_mis"]) for r in rs)
    per = {m: st.mean(float(r["Gap_mis"]) for r in rs if r["method"] == m) for m in {r["method"] for r in rs}}
    print("%-24s %8.4f %8.4f %9.5f | raven %+.5f  fedavg %+.5f  twostage %+.5f" % (
        s, mu, rho, gap, per.get("raven",float('nan')), per.get("fedavg_window",float('nan')), per.get("twostage_hajek",float('nan'))))
print()
print("=== per-scenario, within-method spread of Gap_mis (is the scenario discriminating?) ===")
for s in scen:
    rs = [r for r in rows if r["scenario"] == s]
    per = [st.mean(float(r["Gap_mis"]) for r in rs if r["method"] == m) for m in {r["method"] for r in rs}]
    print("  %-24s min %+.5f  max %+.5f  spread %.5f" % (s, min(per), max(per), max(per)-min(per)))
