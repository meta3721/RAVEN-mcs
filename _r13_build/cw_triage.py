"""W2 triage, self-contained: measure each insertion's page cost, then restore the pre-edit file.

The canonical main.tex is restored in a finally block and asserted against the pre-edit hash.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
SRC = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean"
P = SRC / "main.tex"
OUT = ROOT / "_r13_build/build_cwtest"
PRE = "3cc106ca4b6087d9d6a47d69936abf0cd95914b0285e1a86d3c938acb5ad161c"

CEIL_ANCHOR = (
    "SensorScope and $0.251\\%$ on U-Air, both inside the same bound.  The bound is\n"
    "this weight class at the server step of the grid.  NSW-Traffic, where that step\n"
    "is replaced, is reported in Section~\\ref{subsec:limitations}.\n")
CEIL_NEW = CEIL_ANCHOR + """
A third measurement bounds the same class from the side the stress grid holds
fixed, namely how the deployment target is distributed over groups.
Re-weighting the frozen spatial$\\times$time target so that one region carries
progressively more of the target mass, across top-region shares of $0.2500$,
$0.6322$, $0.7746$ and $1.0000$, moves the gap from the uncorrected member to the
oracle-margin member from $+0.001\\%$ at the frozen target, interval
$[-0.010\\%,+0.015\\%]$, to $+0.022\\%$, $+0.045\\%$ and $+0.097\\%$ with interval
$[+0.067\\%,+0.130\\%]$ at the single-region limit, on twenty seeds at the frozen
server step.  The gap rises with concentration and its interval excludes zero at
the three most concentrated levels, while no interval's upper end reaches the
$0.5\\%$ bar set above; the single-region level is the most concentrated target
that exists, so concentration cannot be traded further and the value bounds the
class rather than one choice of target.  The uncorrected member here is
H\\'ajek aggregation rather than window FedAvg, so the ladder extends this
section's bound to NSW-Traffic rather than reproducing the grid's $H$ on it.  The
endpoint and the four concentration levels were fixed before the runs.
"""
LIM_ANCHOR = (
    "Inside this weight class the oracle-margin weights supply no detectable\n"
    "$\\mathrm{RMSE}_{\\mu}$ headroom, on the original server step and after the Adam\n"
    "replacement.\n")
LIM_NEW = (
    "Inside this weight class the oracle-margin weights supply no detectable\n"
    "$\\mathrm{RMSE}_{\\mu}$ headroom, on the original server step and after the Adam\n"
    "replacement.  The concentration ladder of Section~\\ref{subsec:ceiling} bounds,\n"
    "at the original server step, what re-weighting inside this class could buy on\n"
    "this block across the full range of target concentration, so the null above is\n"
    "not an artefact of a nearly uniform target.\n")
CONC_ANCHOR = (
    "after the server step is replaced by Adam, at an $80\\%$ minimum detectable effect\n"
    "of $5.80\\%$.  Those runs also reduce\n")
CONC_NEW = (
    "after the server step is replaced by Adam, at an $80\\%$ minimum detectable effect\n"
    "of $5.80\\%$, while at the frozen server step the class's recoverable gain stays\n"
    "at $+0.097\\%$, below the $0.5\\%$ bar, even when the whole deployment target is\n"
    "concentrated on one region (Section~\\ref{subsec:ceiling}).  Those runs also reduce\n")
AVAIL_ANCHOR = (
    "readout, with the test-fitted constant and the training-mean predictor tabulated\n"
    "in \\texttt{TWO\\_CONSTANTS.json}.\n")
AVAIL_NEW = (
    "readout, with the test-fitted constant and the training-mean predictor tabulated\n"
    "in \\texttt{TWO\\_CONSTANTS.json}, and \\texttt{results\\_traffic\\_e2/} the\n"
    "concentration ladder of Section~\\ref{subsec:ceiling} with the re-weighted target\n"
    "artifact and the pre-registration frozen before those runs.\n")
EDITS = [("1", CEIL_ANCHOR, CEIL_NEW), ("2", LIM_ANCHOR, LIM_NEW),
         ("3", CONC_ANCHOR, CONC_NEW), ("4", AVAIL_ANCHOR, AVAIL_NEW)]

cur = P.read_text(encoding="utf-8")
back = cur
for name, old, rep in reversed(EDITS):
    assert back.count(rep) == 1, f"reverse {name}: count {back.count(rep)}"
    back = back.replace(rep, old)
pre_txt = back
assert hashlib.sha256(pre_txt.encode()).hexdigest() == PRE, "reverse does not reproduce the pre-edit hash"
print("reverted text reproduces the pre-edit sha256 exactly\n")


def build(label: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for tex in ("supplemental.tex", "main.tex", "main.tex"):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                        f"-output-directory={OUT}", tex],
                       cwd=str(SRC), capture_output=True, text=True)
    log = (OUT / "main.log").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Output written on .*main\.pdf \((\d+) pages", log)
    n = int(m.group(1)) if m else -1
    print(f"  {label:<46} main.pdf = {n} pages", flush=True)
    return n


results = {}
try:
    for label, text in (("pre-edit (control)", pre_txt),
                        ("ceiling paragraph only", pre_txt.replace(CEIL_ANCHOR, CEIL_NEW, 1)),
                        ("all four insertions (as executed)", cur)):
        P.write_text(text, encoding="utf-8", newline="")
        results[label] = build(label)
finally:
    P.write_text(pre_txt, encoding="utf-8", newline="")
    now = hashlib.sha256(P.read_bytes()).hexdigest()
    print(f"\nrestored main.tex sha256 {now}")
    print("pre-edit restored exactly:", now == PRE)
    assert now == PRE, "RESTORE FAILED"

print("\nmarginal page cost over the pre-edit control:")
for k in results:
    if k != "pre-edit (control)":
        print(f"  {k:<40} {results[k] - results['pre-edit (control)']:+d} page(s)")
json.dump({"results": results, "restored_sha256": now}, open(ROOT / "_r13_build/cw_pages.json", "w"), indent=2)
