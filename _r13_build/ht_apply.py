"""Honesty text repairs: H0, the section-2 diagnostic, edits 1-4, and H1."""
from __future__ import annotations

import hashlib
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
raw = P.read_bytes()
pre = hashlib.sha256(raw).hexdigest()

print("=== H0 — pre-edit state ===")
print(f"  sha256 {pre}")
crlf = raw.count(b"\r\n")
print(f"  {len(raw)} B, {raw.count(chr(10).encode())} newlines, CRLF {crlf}")

L = raw.decode("utf-8").splitlines()
print("\n=== H0 — the section-2 diagnostic: is contribution 4's object the same as the limitations'? ===")
print("  contribution 4 (L229-239) points at Table~\\ref{tab:e4_ablation} and 'the small Inst entry'.")
t = next(i for i, l in enumerate(L) if l.startswith("\\label{tab:e4_ablation}"))
for i in range(t - 14, t + 3):
    print(f"   {i+1:>5}: {L[i][:104]}")
print("  -> the ablation table reports objective-term ablations on U-Air; the limitations sentence is")
print("     about the paired oracle-margin headroom on NSW-Traffic.  DIFFERENT OBJECTS: no edit.")

EDITS = [
    ("1 conclusion readout order",
     b"of $5.80\\%$, and the same fifteen runs reduce\n"
     b"$\\Delta_{\\mathrm{group}}$ and $\\Delta_{c\\text{-}s}$\n"
     b"(Section~\\ref{subsec:limitations}).",
     b"of $5.80\\%$.  Those runs also reduce\n"
     b"$\\Delta_{\\mathrm{group}}$ and $\\Delta_{c\\text{-}s}$, scored after that prediction contrast\n"
     b"(Section~\\ref{subsec:limitations})."),

    ("2 limitations: what the MDE means for the bar",
     b"The interval contains zero.  Those fifteen runs score $\\mathrm{RMSE}_{\\mu}$ at",
     b"The interval contains zero, and that detectable effect is too coarse to resolve the\n"
     b"$0.5\\%$ bar of Section~\\ref{subsec:ceiling}.  Those fifteen runs score\n"
     b"$\\mathrm{RMSE}_{\\mu}$ at"),

    ("3 availability: name the new sources",
     b"against the manifest.\n\nThe trained server-weight rules of Section~\\ref{subsec:eval_rq3} are rules of",
     b"against the manifest.\n\n"
     b"The Adam step replacement and its structural readout of\n"
     b"Section~\\ref{subsec:limitations} are internal to this study rather than part of\n"
     b"that bundle: \\texttt{results\\_traffic\\_e1/} holds the prediction contrast over\n"
     b"seeds $30006$--$30020$ and \\texttt{results\\_traffic\\_struct/} the structural\n"
     b"readout, with the test-fitted constant and the training-mean predictor tabulated\n"
     b"in \\texttt{TWO\\_CONSTANTS.json}.\n\n"
     b"The trained server-weight rules of Section~\\ref{subsec:eval_rq3} are rules of"),

    ("4 rewrap one over-long source line",
     b"both arms therefore sit below that reference.  Scored on the same runs after that prediction contrast, the oracle-margin weights reduce $\\Delta_{\\mathrm{group}}$ by $0.0079$",
     b"both arms therefore sit below that reference.  Scored on the same runs after that\n"
     b"prediction contrast, the oracle-margin weights reduce $\\Delta_{\\mathrm{group}}$ by\n"
     b"$0.0079$"),
]

new = raw
for name, old, rep in EDITS:
    n = new.count(old)
    print(f"\n  edit {name}: anchor count {n}")
    assert n == 1, f"anchor count {n} for edit {name}"
    new = new.replace(old, rep)

post = hashlib.sha256(new).hexdigest()
print(f"\n=== H1 — byte integrity ===")
print(f"  post-edit sha256 {post}")
print(f"  {len(new)} B ({len(new) - len(raw):+d} B)")
back = new
for name, old, rep in reversed(EDITS):
    assert back.count(rep) == 1, f"reverse {name}: {back.count(rep)}"
    back = back.replace(rep, old)
g1 = hashlib.sha256(back).hexdigest() == pre
print("  reverse-replacement recovers pre-edit exactly:", g1)
print("  CRLF unchanged:", new.count(b"\r\n") == raw.count(b"\r\n"))
assert g1 and new.count(b"\r\n") == raw.count(b"\r\n"), "H1 failed"

P.write_bytes(new)
print("\nwritten:", P.name)
print("PRE_SHA", pre)
print("POST_SHA", post)
