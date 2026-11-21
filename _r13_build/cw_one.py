"""Apply or restore CW variants in place. Usage: cw_one.py ceiling|ceiling_avail|restore"""
from __future__ import annotations

import hashlib
import pathlib
import sys

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
PRE = "3cc106ca4b6087d9d6a47d69936abf0cd95914b0285e1a86d3c938acb5ad161c"

CEIL_ANCHOR = (
    "SensorScope and $0.251\\%$ on U-Air, both inside the same bound.  The bound is\n"
    "this weight class at the server step of the grid.  NSW-Traffic, where that step\n"
    "is replaced, is reported in Section~\\ref{subsec:limitations}.\n")
CEIL_NEW = CEIL_ANCHOR + """
A third measurement bounds the same class from the side the stress grid holds
fixed, namely how the deployment target is distributed over groups.
Re-weighting the frozen spatial$\\times$time target so that one region carries
progressively more of the target mass, across top-region shares of $0.2558$,
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
AVAIL_ANCHOR = (
    "readout, with the test-fitted constant and the training-mean predictor tabulated\n"
    "in \\texttt{TWO\\_CONSTANTS.json}.\n")
AVAIL_NEW = (
    "readout, with the test-fitted constant and the training-mean predictor tabulated\n"
    "in \\texttt{TWO\\_CONSTANTS.json}, and \\texttt{results\\_traffic\\_e2/} the\n"
    "concentration ladder of Section~\\ref{subsec:ceiling} with the re-weighted target\n"
    "artifact and the pre-registration frozen before those runs.\n")

mode = sys.argv[1]
cur = P.read_text(encoding="utf-8")
if mode in {"ceiling", "ceiling_avail"}:
    assert cur.count(CEIL_ANCHOR) == 1, f"ceiling anchor {cur.count(CEIL_ANCHOR)}"
    cur = cur.replace(CEIL_ANCHOR, CEIL_NEW, 1)
    if mode == "ceiling_avail":
        assert cur.count(AVAIL_ANCHOR) == 1, f"avail anchor {cur.count(AVAIL_ANCHOR)}"
        cur = cur.replace(AVAIL_ANCHOR, AVAIL_NEW, 1)
elif mode == "restore":
    if cur.count(AVAIL_NEW) == 1:
        cur = cur.replace(AVAIL_NEW, AVAIL_ANCHOR, 1)
    if cur.count(CEIL_NEW) == 1:
        cur = cur.replace(CEIL_NEW, CEIL_ANCHOR, 1)
else:
    raise SystemExit("usage: cw_one.py ceiling|ceiling_avail|restore")

P.write_text(cur, encoding="utf-8", newline="")
now = hashlib.sha256(P.read_bytes()).hexdigest()
print(f"  cw_one {mode}: {len(P.read_bytes())} B  sha256 {now[:16]}  "
      f"{'PRE-EDIT OK' if now == PRE else 'variant'}")
if mode == "restore":
    assert now == PRE, "restore failed"
