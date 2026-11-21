"""Append IX.8 (items 87-88) to the diagnosis ledger."""
from __future__ import annotations

import hashlib
import pathlib

LG = pathlib.Path(r"C:\Cursor\raven.mcs\ccfa-review-reports\raven-mcs-metric-definition-diagnosis.md")
raw = LG.read_bytes()
print("before:", len(raw), "B  sha256", hashlib.sha256(raw).hexdigest()[:16], " CRLF", raw.count(b"\r\n"))
assert b"| 88 |" not in raw

ADD = """## IX.8 Sixth-pass additions (items 87-88), 2026-10-10: the ceiling-ladder writing round

| # | correction | evidence |
|:--|:---|:---|
| 87 | **The ceiling ladder was written into the manuscript, and the round is blocked by its own page gate rather than by any content problem; the manuscript was never left over budget.** The plan (`ccfa-review-reports/raven-mcs-ceiling-ladder-manuscript-execution-prompt.md`) specified four insertions and a hard 18 pp allowance. Applied in place, they total +1879 B and build to **19 pages**, so W2 failed and section 7's blocked path ran: the file was restored byte-for-byte to `3cc106ca4b6087d9...`, 119922 B, 18 pp, and `CW_BLOCKED.md` was written instead of a workaround. W0, W1, W3, W4 and W5 all pass: all four anchors matched once; reversing the insertions recovers the pre-edit sha256 exactly with the CRLF count unchanged; prose stays at em dashes 0/3 with none of the banned defensive phrases; twelve of twelve printed numbers recompute from the artifacts; and the title, abstract and contribution-list regions are byte-identical, which is what proves the change did not drift into a scope repositioning. Marginal page cost, one build per variant with the same command sequence: pre-edit control 18, ceiling paragraph alone (`+1227` B) **18**, ceiling paragraph plus availability naming (`+1407` B) **18**, all four (`+1879` B) **19**. The substance therefore fits and the overflow is caused by the two cross-reference sentences, about 440 B between them. Three options are recorded unapplied: apply the measured-fit scope (the ceiling paragraph plus the availability naming) and drop the two cross-references; or keep all four and compress the ceiling paragraph by about four lines; or keep all four and have the author name a cut elsewhere. | `results_paper_ceiling/round_v1/{CW_GATES.md,CW_BLOCKED.md,CW_NUMBERS.json}`; `_r13_build/{cw_apply.py,cw_one.py,cw_outputs.py}`; `main.tex` `3cc106ca...` -> `f55e49fd...` (variant, not applied) |
| 88 | **W4 caught a real wrong number before any manuscript write survived, and this round also produced a process defect of its own.** (a) The frozen rung's top-region share had been written as `0.2500`, which is the design-stage analytic value for four equal regions. The measured frozen target gives region0 `0.232558` and regions 1-3 `0.255814`, so the share is **`0.2558`**; the number was wrong in the plan, in the insertion text and in the design file's analytic table, and only the design table was labelled as analytic. It was corrected in both copies of the insertion text and W4 now sources it from `TE2_PHASE0.json`, so no incorrect value reached the canonical file. This is the first time a gate in this project caught an error before publication rather than after. (b) A triage script imported `cw_apply.py` to reuse its constants, which re-executed the whole module and applied edit 1 to an already-edited file before failing on edit 2. No damage occurred, because the assertions precede the write, and the lesson is recorded: scratch scripts that write the manuscript must guard their side effects behind a `__main__` check or expose constants from a side-effect-free module. (c) A separate triage used Python `subprocess` to drive pdflatex with `capture_output=True`; every build returned a sentinel because the failure was swallowed, so the measurement was redone from the shell, where the same builds succeed. | `results_paper_ceiling/round_v1/CW_NUMBERS.json` (`correction_caught_by_this_gate`); `_r13_build/cw_fix_share.py`; `results_traffic_e2/round_v1/TE2_PHASE0.json` |

"""

new = raw.rstrip(b"\n") + b"\n\n" + ADD.encode("utf-8")
LG.write_bytes(new)
print("after :", len(new), "B  sha256", hashlib.sha256(new).hexdigest()[:16], " (+", len(new) - len(raw), "B)")
