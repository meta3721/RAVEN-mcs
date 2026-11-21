"""Correct the addendum row for S2 (the clause survived; the earlier probe was line-break sensitive)."""
from __future__ import annotations

import pathlib

R = pathlib.Path(r"C:\Cursor\raven.mcs\ccf-review-report/PAPER_SUBMISSION_REPAIR_REPORT.md")
t = R.read_text(encoding="utf-8")
old = "| S2 closing clause | `does not establish the clauses it does not check` | **no**, rewritten by the external edit |"
new = ("| S2 closing clause | `does not establish the clauses it does not check` | **yes**, intact at "
       "`appendix.tex` L1467-1468; the first probe reported `no` only because the sentence is split across "
       "those two lines, which is a defect of the probe, not of the text |")
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

anchor = "Rebuild of the new source:"
note = ("All seven repair markers therefore survive the external edit. What the external edit changed outside "
        "those markers was **not** characterised here: it grew `main.tex` by 3025 B and shrank "
        "`appendix.tex` by 747 B, and no copy of the 86379 B version is retained, so a line-level diff "
        "against it is not possible from this workspace.\n\n")
assert t.count(anchor) == 1
t = t.replace(anchor, note + anchor, 1)
R.write_text(t, encoding="utf-8")
print("corrected:", R.stat().st_size, "B")
for line in t.splitlines():
    if "S2 closing clause" in line or "All seven repair markers" in line:
        print("  |", line[:150])
