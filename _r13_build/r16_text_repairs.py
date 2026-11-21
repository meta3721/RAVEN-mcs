"""ccf-paper-writer, mode=polish: repair the text defects both reviews identified.

Byte-level edits (no newline translation). Verifies afterwards that reversing all seven edits recovers
the pre-edit sha256 exactly, i.e. nothing else changed.
"""
from __future__ import annotations

import hashlib
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex")
PRE = "6fc9be0b8689b6c8849b2a07f55a84e25b2d8360bbffcfb54f11a0c93c1c2b95"

EDITS = [
    # E1 - R15-8 / review item 2: name the comparator's update rule and step budget
    (b"step at any local budget, and raising the budget from $2$ to $20$ leaves window\n"
     b"FedAvg $2.8\\%$--$3.0\\%$ above a centralized model trained on the same delivered\n"
     b"data.  The federated parameters move $0.26\\%$--$0.40\\%$ of their initial norm over\n"
     b"those runs.",
     b"step at any local budget, and raising the budget from $2$ to $20$ leaves window\n"
     b"FedAvg $2.8\\%$--$3.0\\%$ above a centralized reference that is itself Adam at\n"
     b"$10^{-3}$ over the pooled training units for $20$ minibatch steps of $32$, so the\n"
     b"gap compares two update rules and step budgets rather than two aggregators alone.\n"
     b"The federated parameters move $0.26\\%$--$0.40\\%$ of their initial norm over those\n"
     b"runs."),

    # E2 - review item 3: the two arms' RMSE_mu levels beside the Adam headroom
    (b"interval $[-5.42\\%,+1.76\\%]$ and an $80\\%$ minimum detectable effect of $5.80\\%$.\n"
     b"The interval contains zero.  Scored on the same runs after that prediction\n"
     b"contrast,",
     b"interval $[-5.42\\%,+1.76\\%]$ and an $80\\%$ minimum detectable effect of $5.80\\%$.\n"
     b"The interval contains zero.  Those fifteen runs score $\\mathrm{RMSE}_{\\mu}$ at\n"
     b"$0.967$ for window FedAvg and $0.973$ for the oracle-margin arm on average, in\n"
     b"$[0.659,1.572]$ and $[0.795,1.459]$, against $1.007$ for a constant predictor on\n"
     b"the same test weights, so the contrast is between two arms that both leave the\n"
     b"constant.  Scored on the same runs after that prediction contrast,"),

    # E3 - review item 1: split target levels and a constant predictor beside the metric
    (b"runs, such as $\\Delta_{\\mathrm{group}}$ and $\\Delta_{c\\text{-}s}$, are invariant\n"
     b"to this standardization.",
     b"runs, such as $\\Delta_{\\mathrm{group}}$ and $\\Delta_{c\\text{-}s}$, are invariant\n"
     b"to this standardization.  The test-split target means are $7.657$, $-0.807$ and\n"
     b"$0.003$ on SensorScope, U-Air and NSW-Traffic, against training-split means of\n"
     b"$0.301$, $0$, and $0$, and a constant predictor attains $\\mathrm{RMSE}_{\\mu}$ of\n"
     b"$2.088$, $0.678$ and $1.007$ under the same weights.  On SensorScope and U-Air the\n"
     b"training and test target levels differ, so an absolute $\\mathrm{RMSE}_{\\mu}$ on\n"
     b"those two blocks reflects that difference as well as prediction error; the relative\n"
     b"columns are invariant to it."),

    # E4 - R15-5: drop the "small margin" characterisation that contradicts L1834
    (b"(P2) returns uniform weights whatever its objective,\n"
     b"which is consistent with the small margin of the projection over uniform server\n"
     b"weights on the group endpoint ($+0.768$ and $+0.286$~pp above).",
     b"(P2) returns uniform weights whatever its objective.  The\n"
     b"projection over uniform server weights is worth $+0.768$ and $+0.286$~pp at the\n"
     b"group endpoint."),

    # E5 - R15-4: the printed bound the source crosses (max level mean 0.174653 %)
    (b"$0.388$ without a prediction cost of Design above $0.17\\%$, while on U-Air the",
     b"$0.388$ without a prediction cost of Design above $0.175\\%$, while on U-Air the"),

    # E6 - R15-7: give the Adam result its own paragraph
    (b"size of its cost.  On NSW-Traffic a window carries $12.1$ active clients on\n"
     b"average.  In the fifteen-seed comparison below,",
     b"size of its cost.\n\nOn NSW-Traffic a window carries $12.1$ active clients on\n"
     b"average.  In the fifteen-seed comparison below,"),
    (b"runs.  Replacing only this server step by Adam",
     b"runs.\n\nReplacing only this server step by Adam"),

    # E7 - review item 4: the conclusion restates how coarse the null is
    (b"On NSW-Traffic the oracle-margin headroom on $\\mathrm{RMSE}_{\\mu}$ contains zero\n"
     b"after the server step is replaced by Adam, and the same fifteen runs reduce",
     b"On NSW-Traffic the oracle-margin headroom on $\\mathrm{RMSE}_{\\mu}$ contains zero\n"
     b"after the server step is replaced by Adam, at an $80\\%$ minimum detectable effect\n"
     b"of $5.80\\%$, and the same fifteen runs reduce"),
]

raw = P.read_bytes()
print("pre-edit :", len(raw), "B  sha256", hashlib.sha256(raw).hexdigest())
print("expected :           sha256", PRE)
assert hashlib.sha256(raw).hexdigest() == PRE, "pre-edit hash mismatch"

new = raw
for i, (old, rep) in enumerate(EDITS, 1):
    n = new.count(old)
    assert n == 1, f"edit {i}: anchor count {n}"
    new = new.replace(old, rep)
    print(f"  edit {i}: applied (+{len(rep) - len(old)} B)")

print("\npost-edit:", len(new), "B  sha256", hashlib.sha256(new).hexdigest())

# reverse every edit and require the exact pre-edit bytes
back = new
for i, (old, rep) in reversed(list(enumerate(EDITS, 1))):
    assert back.count(rep) == 1, f"reverse {i}: count {back.count(rep)}"
    back = back.replace(rep, old)
ok = hashlib.sha256(back).hexdigest() == PRE
print("reverse recovers pre-edit exactly:", ok)
assert ok, "content changed beyond the intended edits"
assert new.count(b"\r\n") == raw.count(b"\r\n"), "line endings changed"

P.write_bytes(new)
print("\nwritten:", P.name)
