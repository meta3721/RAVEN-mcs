import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\S1P_REPORT.md")
t = p.read_text(encoding="utf-8")

old = ("The first frozen configuration (`fe84a4c6fb1124ed...`) is superseded by "
       "`57b4bcec0cb030cf...`; the selection outcome did not change.")
new = ("`S1P_FROZEN_CONFIG.json` was therefore written three times: `fe84a4c6fb1124ed...` (with the "
       "incomplete cell), `57b4bcec0cb030cf...` (after repairing it), and finally "
       "`d52dbcfc542e7e7b...` (after the 15 empty traffic directories were removed, so the refusal now "
       "records as BLOCKED). **The selection outcome was identical in all three passes** - SensorScope "
       "`eta_s* = 0.01`, U-Air `eta_s* = 0.003` - and no test-derived value was read in any of them.")

n = t.count(old)
assert n == 1, f"anchor count {n}"
p.write_text(t.replace(old, new), encoding="utf-8")
print("corrected provenance chain;", len(t.splitlines()), "lines")
