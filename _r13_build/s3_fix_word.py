"""Repair the word dropped by the S3 patch: restore 'comparisons.  ' before 'Later corrected'."""
from __future__ import annotations

import hashlib
import pathlib

M = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
raw = M.read_bytes()
eol = b"\r\n" if raw.count(bytes([13, 10])) == raw.count(bytes([10])) else b"\n"
lines = raw.split(eol)

i = next(k for k, l in enumerate(lines) if l.startswith(b"Later corrected W1 scores"))
print("prev:", lines[i - 1].decode())
print("curr:", lines[i].decode())
assert lines[i - 1].rstrip().endswith(b"for its indexed"), lines[i - 1]
assert not lines[i].startswith(b"comparisons."), "already repaired"
lines[i] = b"comparisons.  " + lines[i]
out = eol.join(lines)
M.write_bytes(out)
print("\nrepaired:", len(out), "B  sha256", hashlib.sha256(out).hexdigest()[:16], " (pre-S3 was 86353)")
print("\n=== the paragraph now reads ===")
for k in range(i - 3, i + 4):
    print(f"  {k+1:>5}: {lines[k].decode()}")
