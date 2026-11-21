"""S1 caption labelling: make the two exhibits explicitly different comparisons. Line-based, CRLF-safe."""
from __future__ import annotations

import hashlib
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex")
raw = P.read_bytes()
pre = hashlib.sha256(raw).hexdigest()
crlf = raw.count(bytes([13, 10]))
eol = b"\r\n" if crlf == raw.count(bytes([10])) else b"\n"
lines = raw.split(eol)
print("pre :", len(raw), "B  sha256", pre[:16], " lines", len(lines))

# --- Table XVIII caption (tab:app_e3_uair): name the FedAvg identity difference ---
i = next(k for k, l in enumerate(lines) if b"The RAVEN row here uses the Design-on setting.}" in l)
print("  tab XVIII caption end at line", i + 1)
lines[i:i + 1] = [
    b"The RAVEN row here uses the Design-on setting.  The FedAvg row is the",
    b"current-runner re-run that keeps every delivered client, so its active set is",
    b"not the one behind the same-named row of Figs.~\\ref{fig:e3_structural}",
    b"and~\\ref{fig:e3_prediction}; the two exhibits are separate comparisons.}",
]

# --- fig3 caption: rows are the frozen run set, so it carries no same-support claim ---
j = [k for k, l in enumerate(lines) if l.strip() == b"Table~\\ref{tab:main_effectiveness}.}"]
print("  caption-end candidates for the two figures:", [k + 1 for k in j])
assert len(j) == 2, j
lines[j[0]:j[0] + 1] = [
    b"Table~\\ref{tab:main_effectiveness}.  These rows are the frozen run set, and",
    b"some of their active sets differ from the Table~\\ref{tab:app_e3_uair} rows,",
    b"so the figure supports no same-support claim of its own.}",
]
# --- fig4 caption: one line pointing at fig3's identity statement ---
j = [k for k, l in enumerate(lines) if l.strip() == b"Table~\\ref{tab:main_effectiveness}.}"]
assert len(j) == 1, j
lines[j[0]:j[0] + 1] = [
    b"Table~\\ref{tab:main_effectiveness}.  Row identities are those stated in",
    b"Fig.~\\ref{fig:e3_structural}.}",
]

out = eol.join(lines)
post = hashlib.sha256(out).hexdigest()
print("post:", len(out), "B  sha256", post[:16], " lines", len(lines),
      " (was", len(raw.split(eol)), ")")
P.write_bytes(out)
print("written:", P.name)
