"""Ceiling ladder into the manuscript: W0, the four insertions, W1, and the W5 scope check."""
from __future__ import annotations

import hashlib
import json
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
raw = P.read_bytes()
pre = hashlib.sha256(raw).hexdigest()
crlf0 = raw.count(b"\r\n")
txt = raw.decode("utf-8")

print("=== W0 - pre-edit state ===")
print(f"  sha256 {pre}")
print(f"  {len(raw)} B, {txt.count(chr(10))} newlines, CRLF {crlf0}")

SIGN_OFF = (
    "authorial sign-off: the user instructed verbatim '按你的方案执行论文编写' (execute the manuscript "
    "writing per your plan) on 2026-10-10, which approves the plan as written: the ceiling paragraph as "
    "scoped, one cross-reference in the limitations, one clause in the conclusion, naming "
    "results_traffic_e2/ and the pre-registration in the availability section, and the title, abstract and "
    "contribution list left unchanged. The plan's open page-budget item is resolved by the plan's own "
    "default: if the build reaches 19 pages, stop and report rather than cut."
)
print("  " + SIGN_OFF[:100] + "...")

ABS_A = txt.index("\\begin{abstract}")
ABS_B = txt.index("\\end{abstract}")
TITLE = next(l for l in txt.splitlines() if l.startswith("\\title"))
CONT_A = txt.index("Our main contributions are as follows.")
CONT_B = txt.index("\\end{itemize}", CONT_A)


def region_hash(s: str, a: int, b: int) -> str:
    return hashlib.sha256(s[a:b].encode("utf-8")).hexdigest()[:16]


PRE_REGIONS = {"abstract": region_hash(txt, ABS_A, ABS_B), "title": hashlib.sha256(
    TITLE.encode()).hexdigest()[:16], "contribution_list": region_hash(txt, CONT_A, CONT_B)}
print("  scope regions (pre):", PRE_REGIONS)

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

EDITS = [("1 ceiling paragraph", CEIL_ANCHOR, CEIL_NEW),
         ("2 limitations cross-reference", LIM_ANCHOR, LIM_NEW),
         ("3 conclusion clause", CONC_ANCHOR, CONC_NEW),
         ("4 availability", AVAIL_ANCHOR, AVAIL_NEW)]

new = txt
for name, old, rep in EDITS:
    n = new.count(old)
    print(f"  edit {name}: anchor count {n}")
    assert n == 1, f"anchor count {n} for {name}"
    new = new.replace(old, rep)

post = hashlib.sha256(new.encode("utf-8")).hexdigest()
print(f"\n=== W1 - byte integrity ===")
print(f"  post sha256 {post}")
print(f"  {len(new.encode())} B ({len(new.encode()) - len(raw):+d} B)")
back = new
for name, old, rep in reversed(EDITS):
    assert back.count(rep) == 1, f"reverse {name}: {back.count(rep)}"
    back = back.replace(rep, old)
ok = hashlib.sha256(back.encode("utf-8")).hexdigest() == pre
print("  reverse recovers pre-edit exactly:", ok)
print("  CRLF unchanged:", new.count("\r\n") == crlf0)
assert ok and new.count("\r\n") == crlf0, "W1 failed"

POST_REGIONS = {"abstract": region_hash(new, new.index("\\begin{abstract}"),
                                       new.index("\\end{abstract}")),
                "title": hashlib.sha256(next(l for l in new.splitlines()
                                             if l.startswith("\\title")).encode()).hexdigest()[:16],
                "contribution_list": region_hash(new, new.index("Our main contributions are as follows."),
                                                 new.index("\\end{itemize}",
                                                           new.index("Our main contributions are as follows.")))}
print("\n=== W5 - scope did not drift ===")
for k in PRE_REGIONS:
    same = PRE_REGIONS[k] == POST_REGIONS[k]
    print(f"  {k:<20} {PRE_REGIONS[k]} -> {POST_REGIONS[k]}  identical: {same}")
    assert same, f"{k} changed"
print("  em dashes in the inserted text:", sum(rep.count("---") for _, _, rep in EDITS))

P.write_text(new, encoding="utf-8", newline="")
assert P.read_bytes().count(b"\r\n") == crlf0
print("\nwritten:", P.name)
json.dump({"pre_sha256": pre, "post_sha256": post, "sign_off": SIGN_OFF,
           "scope_regions_pre": PRE_REGIONS, "scope_regions_post": POST_REGIONS,
           "reverse_recovers_pre": ok},
          open(r"C:\Cursor\raven.mcs\_r13_build\cw_stage1.json", "w", encoding="utf-8"),
          indent=2, sort_keys=True)
