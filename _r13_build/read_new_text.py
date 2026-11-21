"""Read the new abstract and contribution list, and test whether the CW anchors survive."""
from __future__ import annotations

import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
t = P.read_text(encoding="utf-8")
L = t.splitlines()

print("=== the new abstract ===")
a, b = next(i for i, l in enumerate(L) if l.startswith("\\begin{abstract}")), \
       next(i for i, l in enumerate(L) if l.startswith("\\end{abstract}"))
for i in range(a, b + 1):
    print(f"{i+1:>5}: {L[i]}")

print("\n=== the new contribution list ===")
c = next(i for i, l in enumerate(L) if "Our main contributions" in l)
d = next(i for i, l in enumerate(L) if i > c and l.startswith("\\end{itemize}"))
for i in range(c, d + 1):
    print(f"{i+1:>5}: {L[i]}")

print("\n=== do the CW insertion anchors survive? ===")
ANCH = {
    "1 ceiling": "SensorScope and $0.251\\%$ on U-Air, both inside the same bound.",
    "2 limitations": "$\\mathrm{RMSE}_{\\mu}$ headroom, on the original server step and after the Adam",
    "3 conclusion": "after the server step is replaced by Adam, at an $80\\%$ minimum detectable effect",
    "4 availability": "readout, with the test-fitted constant and the training-mean predictor tabulated",
}
for k, s in ANCH.items():
    print(f"  {k:<16} occurrences={t.count(s)}")

print("\n=== what else moved: section-level line census ===")
import re
for m in re.finditer(r"(?m)^\\(?:sub)?section\*?\{([^}]*)\}", t):
    print(f"  {t[:m.start()].count(chr(10)) + 1:>5}  {m.group(1)}")
