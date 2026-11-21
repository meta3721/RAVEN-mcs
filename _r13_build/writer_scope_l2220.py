"""ccf-paper-writer, mode=polish, bounded edit: scope L2220-L2221 to the class L2110 defines.

In-place edit of the canonical manuscript. Records hashes and the exact replacement for reversal.
"""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
P = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"

OLD = ("by $12\\%$.  The\nfederated learner, not the weighting, therefore limits the prediction endpoint.")
NEW = ("by $12\\%$.  Inside the class the method defines, the\n"
       "federated learner, not the weighting, limits the prediction endpoint.")


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


before = sha(P)
t = P.read_text(encoding="utf-8")
n = t.count(OLD)
assert n == 1, f"anchor count {n}"
t = t.replace(OLD, NEW)
P.write_text(t, encoding="utf-8")
after = sha(P)

print("ccf-paper-writer / polish / in-place edit")
print("  file   :", P.relative_to(ROOT).as_posix())
print("  before :", before)
print("  after  :", after)
print("  bytes  :", len(t.encode()), "(was", P.stat().st_size, ")")
print()
print("  removed: 'The federated learner, not the weighting, therefore limits the prediction endpoint.'")
print("  added  : 'Inside the class the method defines, the federated learner, not the weighting,")
print("            limits the prediction endpoint.'")
print()
i = t.find("Inside the class the method defines")
print("  context after edit:")
for ln in t[max(0, i - 430):i + 130].split("\n"):
    print("   |", ln)
