"""Repair the line-ending damage from the previous write, then prove the only content change is the
intended sentence (by reverting it and recovering the exact pre-edit hash)."""
from __future__ import annotations

import hashlib
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
PRE = "d4fb164df90f59484bfe901b117399536cd727f4cb01fca6a3e09cb902486e60"

raw = P.read_bytes()
print("on disk now:", len(raw), "B | CRLF count:", raw.count(b"\r\n"), "| bare LF:", raw.count(b"\n") - raw.count(b"\r\n"))

fixed = raw.replace(b"\r\n", b"\n")
P.write_bytes(fixed)
print("after LF repair:", len(fixed), "B | CRLF:", fixed.count(b"\r\n"), "| sha256:",
      hashlib.sha256(fixed).hexdigest())

OLD = b"federated learner, not the weighting, therefore limits the prediction endpoint."
NEW = b"federated learner, not the weighting, limits the prediction endpoint."
assert fixed.count(NEW) == 1, "new sentence not found exactly once"
reverted = fixed.replace(NEW, OLD)
print()
print("reversal check (revert only the sentence):")
print("  recovered sha256:", hashlib.sha256(reverted).hexdigest())
print("  pre-edit  sha256:", PRE)
print("  match           :", hashlib.sha256(reverted).hexdigest() == PRE)
print()
print("=> the file differs from the pre-edit state by exactly one sentence and nothing else"
      if hashlib.sha256(reverted).hexdigest() == PRE else
      "=> UNEXPECTED: content changed beyond the intended sentence")
