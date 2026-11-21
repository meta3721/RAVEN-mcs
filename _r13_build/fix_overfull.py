"""Fix the one Overfull: allow a break inside the long texttt path."""
from __future__ import annotations

import hashlib
import pathlib

M = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
raw = M.read_bytes()
eol = b"\r\n" if raw.count(bytes([13, 10])) == raw.count(bytes([10])) else b"\n"
old = (b"\\texttt{submission\\_evidence/SUBMISSION\\_EVIDENCE\\_INDEX.md} beside the bundle.")
new = (b"\\texttt{submission\\_evidence/}\\allowbreak"
       b"\\texttt{SUBMISSION\\_EVIDENCE\\_INDEX.md} beside the bundle.")
print("anchor count:", raw.count(old))
assert raw.count(old) == 1
out = raw.replace(old, new, 1)
M.write_bytes(out)
print("main.tex:", len(out), "B  sha256", hashlib.sha256(out).hexdigest()[:16])
