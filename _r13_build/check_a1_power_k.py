import csv
import math
import pathlib
from fractions import Fraction

src = pathlib.Path(r"C:\Cursor\raven.mcs\results_gatekeeping\round_v1\A1_POWER.csv")
rows = list(csv.DictReader(src.open(encoding="utf-8")))

print("=== hypothesis: mde80 = delta - k * se_used ===")
ks = []
for r in rows:
    try:
        d = float(r["delta"])
        se = float(r["se_used"])
        m = float(r["mde80"])
    except (TypeError, ValueError):
        continue
    if se == 0:
        continue
    k = (d - m) / se
    ks.append((r["ds"], r["arm"], r["margin"], d, se, m, k))
for t in ks:
    print(f"  {t[0]:<22}{t[1]:<10}margin={t[2]:<6}delta={t[3]:<8.6g}se={t[4]:<12.8g}mde80={t[5]:<14.10g}k={t[6]:.10f}")
kv = [t[6] for t in ks]
print()
print(f"  k: n={len(kv)} min={min(kv):.10f} max={max(kv):.10f} spread={max(kv)-min(kv):.3e}")

print()
print("=== distinct delta and margin values ===")
print("  margins:", sorted({r["margin"] for r in rows}))
print("  deltas :", sorted({r["delta"] for r in rows}))
print("  n_effective values:", sorted({r["n_effective"] for r in rows}))
print("  theta_case values:", sorted({r["theta_case"] for r in rows}))
print("  scenario values:", sorted({r["scenario"] for r in rows}))
print("  testable_power_ge_0.80 values:", sorted({r["testable_power_ge_0.80"] for r in rows}))
print("  power_normal values:", sorted({r["power_normal"] for r in rows}))
print("  power_t_df values:", sorted({r["power_t_df"] for r in rows}))

print()
print("=== does mde80 depend on theta_case? (same ds/arm, varying theta_case) ===")
groups = {}
for r in rows:
    groups.setdefault((r["ds"], r["arm"], r["scenario"], r["margin"]), []).append((r["theta_case"], r["mde80"]))
for key, vals in groups.items():
    distinct = {v[1] for v in vals}
    print(f"  {key}: mde80 distinct={len(distinct)} -> {sorted(distinct)[:4]}")

print()
print("=== is 2.4865 a familiar constant? ===")
for name, val in [("t_.975,19 + t_.80,19", None)]:
    pass
try:
    from scipy import stats  # type: ignore
    t975 = stats.t.ppf(0.975, 19)
    t80 = stats.t.ppf(0.80, 19)
    zn = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)
    print(f"  t_.975,19={t975:.6f}  t_.80,19={t80:.6f}  sum={t975+t80:.6f}")
    print(f"  z_.975+z_.80={zn:.6f}")
except Exception as exc:  # noqa: BLE001
    print("  scipy unavailable:", exc)
print("  observed k ~ ", sum(kv) / len(kv))
