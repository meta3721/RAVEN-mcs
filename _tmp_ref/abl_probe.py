import csv
rows = list(csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv", newline="", encoding="utf-8")))
print("n rows:", len(rows))
print("metrics:", sorted({r["metric"] for r in rows}))
print("datasets:", sorted({r["dataset"] for r in rows}))
print("status:", sorted({r["status"] for r in rows}))
print()
for r in rows[:4]:
    print({k: r[k] for k in ("dataset","seed","configuration","component","metric","full_RAVEN","ablation","relative_change_percent","status")})
