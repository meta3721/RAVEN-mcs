"""Fix every feasibility() call site: the third argument is e_bar, not the target."""
import pathlib
import re

p = pathlib.Path("scripts/w1_v51_oracle.py")
t = p.read_text(encoding="utf-8")

repl = [
    # helper: make the projection's own checks use e_bar
    ("    if feasibility(uni, hi, target) <= 1e-13:\n"
     "        cands.append((float(((uni - v) ** 2).sum()), uni, \"uniform\",\n"
     "                      {\"nu\": 0.0, \"mu_sum\": 0.0}))",
     "    if feasibility(uni, hi, e_bar) <= 1e-13:\n"
     "        cands.append((float(((uni - v) ** 2).sum()), uni, \"uniform\",\n"
     "                      {\"nu\": 0.0, \"mu_sum\": 0.0}))"),
    ("                if feasibility(x, hi, target) > 1e-10:\n                    continue",
     "                if feasibility(x, hi, e_bar) > 1e-10:\n                    continue"),
    ("        if feasibility(uni, hi, target) <= 1e-13:\n"
     "            return uni, \"degenerate_uniform\", {\"nu\": 0.0, \"mu_sum\": None}",
     "        if feasibility(uni, hi, e_bar) <= 1e-13:\n"
     "            return uni, \"degenerate_uniform\", {\"nu\": 0.0, \"mu_sum\": None}"),
    # the SLSQP helper receives target; it must convert back to e_bar
    ("        if feasibility(x, hi, target) <= 1e-12:",
     "        if feasibility(x, hi, 1.0 / target) <= 1e-12:"),
    # the KKT verification helper receives target
    ("    if feasibility(x, hi, target) > 1e-9:\n        return float(\"inf\")",
     "    if feasibility(x, hi, 1.0 / target) > 1e-9:\n        return float(\"inf\")"),
    # gate/battery call sites in main()
    ("    if feasibility(x, hi, target) > 1e-12:\n        kind = \"residual\"",
     "    if feasibility(x, hi, 1.0 / target) > 1e-12:\n        kind = \"residual\""),
]
for old, new in repl:
    if old in t:
        t = t.replace(old, new)
    else:
        print("skip (not found):", old.splitlines()[0][:70])
p.write_text(t, encoding="utf-8")

# report remaining call sites for manual review
for i, line in enumerate(t.splitlines(), 1):
    if "feasibility(" in line and "def feasibility" not in line:
        print("%4d %s" % (i, line.strip()))
