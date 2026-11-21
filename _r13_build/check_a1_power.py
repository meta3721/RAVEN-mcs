import csv
import math
import pathlib

src = pathlib.Path(r"C:\Cursor\raven.mcs\results_gatekeeping\round_v1\A1_POWER.csv")
rows = list(csv.DictReader(src.open(encoding="utf-8")))
print("rows:", len(rows))
print()

hdr = f"{'ds':<12}{'arm':<12}{'theta_case':<20}{'paired_sd':>14}{'se_used':>14}{'mde80':>16}{'2.802sd/sqrt(n)':>18}{'ratio':>10}"
print(hdr)
print("-" * len(hdr))

neg = []
per_ds = {}
for r in rows:
    ds = r["ds"]
    arm = r["arm"]
    tc = r["theta_case"]
    try:
        sd = float(r["paired_sd"])
    except (TypeError, ValueError):
        sd = float("nan")
    try:
        se = float(r["se_used"])
    except (TypeError, ValueError):
        se = float("nan")
    try:
        n = float(r["n_effective"])
    except (TypeError, ValueError):
        n = float("nan")
    try:
        mde = float(r["mde80"])
    except (TypeError, ValueError):
        mde = float("nan")
    rec = 2.802 * sd / math.sqrt(n) if n and n > 0 else float("nan")
    ratio = mde / rec if rec and not math.isnan(rec) and rec != 0 else float("nan")
    print(f"{ds:<12}{arm:<12}{tc:<20}{sd:>14.8g}{se:>14.8g}{mde:>16.8g}{rec:>18.8g}{ratio:>10.4g}")
    per_ds.setdefault(ds, []).append(mde)
    if mde < 0:
        neg.append((ds, arm, tc, mde))

print()
print("=== mde80 range per dataset (all rows) ===")
for ds, vals in per_ds.items():
    good = [v for v in vals if not math.isnan(v)]
    print(f"  {ds:<12} n={len(good):<4} min={min(good):.8g}  max={max(good):.8g}")
print()
print("=== negative mde80 rows ===")
for t in neg:
    print("  ", t)
print()
print("=== distinct mde80 values ===")
uniq = sorted({round(v, 12) for vals in per_ds.values() for v in vals if not math.isnan(v)})
for v in uniq:
    print("  ", v)
print()
print("=== mde80 / se_used ratio (is mde80 = k * se_used?) ===")
for r in rows:
    try:
        se = float(r["se_used"])
        mde = float(r["mde80"])
    except (TypeError, ValueError):
        continue
    if se:
        print(f"  {r['ds']:<12}{r['arm']:<12}{r['theta_case']:<20} mde80/se_used = {mde/se:>10.6g}")
