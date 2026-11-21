import csv, pathlib, collections
import statistics as st
p = pathlib.Path("RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv")
rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
print("columns:", list(rows[0].keys()))
print("components:", sorted({r["component"] for r in rows}))
print("configurations:", sorted({r["configuration"] for r in rows})[:12])
print()
# published convention: relative change = (config - full)/full ; positive = ablation worsens
for comp in sorted({r["component"] for r in rows}):
    for ds in ("uair", "sensorscope"):
        for met in ("Delta_group", "Delta_c_s", "RMSE_mu"):
            vals = [(float(r["value"]) - float(r["full_RAVEN"])) / float(r["full_RAVEN"]) * 100
                    for r in rows if r["dataset"] == ds and r["component"] == comp and r["metric"] == met]
            if vals:
                print(f"  {ds:<12} {comp:<8} {met:<12} mean={st.mean(vals):+8.3f}%  n={len(vals)}")
    print()
