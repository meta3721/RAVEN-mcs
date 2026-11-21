"""S2 + S4 repairs, line-based so the file's own line ending is preserved."""
from __future__ import annotations

import hashlib
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex")
raw = P.read_bytes()
pre = hashlib.sha256(raw).hexdigest()
crlf = raw.count(bytes([13, 10]))
nl = raw.count(bytes([10]))
eol = b"\r\n" if crlf == nl else b"\n"
print("pre :", len(raw), "B  sha256", pre[:16], " CRLF", crlf, " LF", nl, " -> using", eol)
lines = raw.split(eol)
print("  lines:", len(lines))

# ---- S2: replace the seven-line opening paragraph of appendix H ----
i = next(k for k, l in enumerate(lines) if b"A5, A6a, and A6b are separate hypotheses" in l)
old7 = lines[i:i + 7]
print("  S2 old block:")
for l in old7:
    print("    |", l.decode("utf-8"))
assert b"follow from A5 alone" in old7[1], "unexpected S2 block"
assert old7[6].strip() == b"\\texttt{EventTraces}.", "unexpected S2 block end"
new8 = [
    b"A5, A6a, and A6b are separate hypotheses.  The ideal reconstruction of",
    b"Proposition~\\ref{prop:reconstruction} rests on A1--A3.  The perturbation form",
    b"of Proposition~\\ref{prop:practical_plugin} assumes A1, A4, A5, and A6b",
    b"together with the shared-state and positive-mass conditions stated there, and",
    b"the sharp form with $\\varepsilon_{\\mathrm{stab},r}=0$ additionally needs A6a.",
    b"This section reports which of A5, A6a, and A6b hold on the released protocol",
    b"traces, using their recorded margins and \\texttt{EventTraces}; it does not",
    b"establish the clauses it does not check.",
]
lines[i:i + 7] = new8

# ---- S4: the residual "The gate" -> "The support rule" ----
OLD4 = b"The gate sets Design on exactly when this statistic is zero"
NEW4 = b"The support rule sets Design on exactly when this statistic is zero"
hits = [k for k, l in enumerate(lines) if OLD4 in l]
print("  S4 anchor lines:", hits)
assert len(hits) == 1, f"S4 anchor count {len(hits)}"
lines[hits[0]] = lines[hits[0]].replace(OLD4, NEW4)

out = eol.join(lines)
post = hashlib.sha256(out).hexdigest()
print("post:", len(out), "B  sha256", post[:16], " CRLF", out.count(bytes([13, 10])),
      " lines", len(lines), " (was 1949)")
P.write_bytes(out)
print("written:", P.name)
