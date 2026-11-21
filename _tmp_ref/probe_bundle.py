import csv, pathlib
R = pathlib.Path("RAVEN_MCS_PUBLIC_REPRO_R1/tables")
print("=== bundle tables ===")
for p in sorted(R.glob("*.csv")):
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    print(f"  {p.name:<44} rows={len(rows):<5} cols={list(rows[0].keys())[:6] if rows else []}")
print()
for name in ("TABLE_II_MAIN_EFFECTIVENESS.csv",):
    p = R/name
    if not p.is_file(): print(name, "MISSING"); continue
    rows = [r for r in csv.DictReader(open(p, newline="", encoding="utf-8")) if r.get("dataset","").lower() in ("u-air","uair")]
    print(f"=== {name}: U-Air rows ===")
    for r in rows:
        keep = {k: v for k, v in r.items() if k.lower() in ("method","rmse_mu","rmse_mu_mean","rmse_mu_display","worstgroup")}
        print("  ", keep)
print()
print("=== does the bundle carry ANY rebuilt-method value? ===")
import re
for p in sorted(R.glob("*.csv")):
    t = p.read_text(encoding="utf-8", errors="replace")
    hits = [v for v in ("1.1119","1.111932","1.1144","1.114378","1.1690","1.0446","72.61") if v in t]
    print(f"  {p.name:<44} new-value hits: {hits if hits else 'NONE'}")
