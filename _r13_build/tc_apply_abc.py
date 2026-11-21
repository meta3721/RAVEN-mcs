"""Apply edits A, B, C of the two-constant disclosure prompt, then run G1 (byte integrity)."""
from __future__ import annotations

import hashlib
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")

A_OLD = (b"to this standardization.  The test-split target means are $7.657$, $-0.807$ and\n"
         b"$0.003$ on SensorScope, U-Air and NSW-Traffic, against training-split means of\n"
         b"$0.301$, $0$, and $0$, and a constant predictor attains $\\mathrm{RMSE}_{\\mu}$ of\n"
         b"$2.088$, $0.678$ and $1.007$ under the same weights.  On SensorScope and U-Air the\n"
         b"training and test target levels differ, so an absolute $\\mathrm{RMSE}_{\\mu}$ on\n"
         b"those two blocks reflects that difference as well as prediction error; the relative\n"
         b"columns are invariant to it.")
A_NEW = (b"to this standardization.  The test-split target means are $7.657$, $-0.807$ and\n"
         b"$0.003$ on SensorScope, U-Air and NSW-Traffic, against training-split means of\n"
         b"$0.301$, $0$, and $0$.  Fitted on the scored test labels, the test-fitted constant\n"
         b"attains $\\mathrm{RMSE}_{\\mu}$ of $2.088$, $0.678$ and $1.007$; the training-mean\n"
         b"predictor, which uses only the training split, attains $7.647$, $1.054$ and $1.007$.\n"
         b"On SensorScope and U-Air the two differ by about $3.7\\times$ and $1.6\\times$, because\n"
         b"their training and test target levels differ, so an absolute $\\mathrm{RMSE}_{\\mu}$\n"
         b"there is read against the training-mean predictor; the relative quantities are\n"
         b"invariant to that difference.")

B_OLD = (b"against $1.007$ for a constant predictor on\n"
         b"the same test weights, so the contrast is between two arms that both leave the\n"
         b"constant.")
B_NEW = (b"against $1.007$ for the test-fitted constant on\n"
         b"the same test weights, where the training-mean predictor takes the same value;\n"
         b"both arms therefore sit below that reference.")

C_OLD = (b"We do not claim a Holm-significant RMSE win.\n"
         b"A supplemental protocol table uses intermittent occupancy.}")
C_NEW = (b"We do not claim a Holm-significant RMSE win.\n"
         b"Fitted on the scored test labels, the test-fitted constant attains\n"
         b"$\\mathrm{RMSE}_{\\mu}$ of $2.088$ on SensorScope and $0.678$ on U-Air, while the\n"
         b"training-mean predictor attains $7.647$ and $1.054$; the absolute column on both\n"
         b"blocks is read against the training-mean predictor.\n"
         b"A supplemental protocol table uses intermittent occupancy.}")

EDITS = [("A", A_OLD, A_NEW), ("B", B_OLD, B_NEW), ("C", C_OLD, C_NEW)]

raw = P.read_bytes()
pre = hashlib.sha256(raw).hexdigest()
print("pre-edit :", len(raw), "B  sha256", pre)
print("CRLF before:", raw.count(b"\r\n"), "| LF:", raw.count(b"\n"))

new = raw
for name, old, rep in EDITS:
    n = new.count(old)
    assert n == 1, f"edit {name}: anchor count {n}"
    new = new.replace(old, rep)
    print(f"  edit {name}: applied ({len(rep) - len(old):+d} B)")

post = hashlib.sha256(new).hexdigest()
print("\npost-edit:", len(new), "B  sha256", post)

# G1: reversing every edit must recover the pre-edit bytes exactly
back = new
for name, old, rep in reversed(EDITS):
    assert back.count(rep) == 1, f"reverse {name}: count {back.count(rep)}"
    back = back.replace(rep, old)
g1 = hashlib.sha256(back).hexdigest() == pre
print("G1 reverse-replacement recovers pre-edit exactly:", g1)
print("G1 CRLF unchanged:", new.count(b"\r\n") == raw.count(b"\r\n"))
assert g1 and new.count(b"\r\n") == raw.count(b"\r\n"), "G1 failed"

P.write_bytes(new)
print("\nwritten:", P.name)
print("PRE_SHA", pre)
print("POST_SHA", post)
