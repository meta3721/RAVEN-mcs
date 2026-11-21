"""Protect acronyms from IEEEtran's sentence-casing, then verify the three rendered entries."""
from __future__ import annotations

import hashlib
import pathlib

BIB = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/reference.bib")
raw = BIB.read_bytes()
pre = hashlib.sha256(raw).hexdigest()
text = raw.decode("utf-8")

FIXES = [
    ("DQN-Based offloading", "{DQN}-Based offloading"),
    ("With Non-IID Data", "With Non-{IID} Data"),
]
for old, new in FIXES:
    n = text.count(old)
    print(f"  {old!r}: {n}")
    if n:
        text = text.replace(old, new)

out = text.encode("utf-8")
if out != raw:
    BIB.write_bytes(out)
    print("bib updated:", len(raw), "->", len(out), "B  sha256",
          hashlib.sha256(out).hexdigest()[:16], " (was", pre[:16] + ")")
else:
    print("bib unchanged")
