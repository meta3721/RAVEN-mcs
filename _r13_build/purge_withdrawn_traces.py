"""Remove the remaining traces of the withdrawn reading from sections 4, 6, 7 and 10.
Console-safe: all echoed text is ASCII-encoded before printing (the console is GBK)."""
from __future__ import annotations

import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\raven-mcs-tmc-review-r14.md")
lines = P.read_text(encoding="utf-8").split("\n")


def show(s: str, n: int = 130) -> None:
    print("   " + s.encode("ascii", "replace").decode("ascii")[:n])


def find(pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise SystemExit("anchor not found")


i = find(lambda s: "measures which degenerate model is marginally less bad" in s)
show(lines[i])
lines[i] = ("  (0.986505 / 0.832921 / 0.857589) compares the FedAdam federated arm against the frozen "
            "`central_delivered` reference; on SensorScope and U-Air that comparison sits inside the same "
            "train-to-test level shift as the rest of those blocks (section 3), so it inherits that "
            "caveat rather than establishing federated superiority over a fair centralized counterpart.")

i = find(lambda s: "The gap is a property of these endpoints" in s and s.startswith("| "))
show(lines[i])
lines[i] = ("| \"The gap is a property of these endpoints rather than of an over-easy regime\" | "
            "L2125-L2128 | Propensity hardening (-15-21x) | **not testable on SS/UA with the current "
            "evidence** | The level shift and the shared windowed server step both sit between the arms "
            "and the endpoint, so `H` near 0 there cannot separate \"no recoverable gain\" from \"the "
            "members do not differ\". The degenerate-predictor rationale I first gave is withdrawn "
            "(section 3); on NSW-Traffic, the one clean block, `H` is one outlier away from being "
            "positive | Report the split statistics; test the ceiling on the block without a level "
            "shift |")

i = find(lambda s: s.startswith("## 7. Multi-reviewer panel"))
lines.insert(i + 2, "> **Read this panel with section 3.** The best-justified, critical and adversarial "
                    "entries below were written before the withdrawal, and their \"worse than a "
                    "constant / no skill\" premises are superseded by it. Their remaining content - the "
                    "structural contribution is untouched, the new numbers at L2214-L2221 are correct, "
                    "the comparator is not like-for-like, the round's arithmetic reproduces - is "
                    "unaffected and still stands.")
lines.insert(i + 1, "")
print("panel note inserted")

i = find(lambda s: s.startswith("- **Constant-predictor audit"))
show(lines[i])
lines[i] = ("- **Constant-predictor audit (run, then withdrawn as evidence - kept for audit).** All 11 "
            "SensorScope arms, all 11 U-Air arms and all 6 NSW-Traffic arms in the frozen E3 tree were "
            "scored at seed 30001 through `runner._predict` + `_mu_weights_for_test` + `metrics.rmse_mu`, "
            "each recomputation matching the stored `RMSE_mu` exactly, and 90 further checkpoints were "
            "scored across the six other trees holding SensorScope/U-Air evidence. The arithmetic stands "
            "(`DO_THE_ARMS_LEARN.json`, `ALL_ARMS_VS_CONSTANT.json`, `PAPER_TREES_VS_CONSTANT.json`), but "
            "the skill inference drawn from it is withdrawn in section 3.")

P.write_text("\n".join(lines), encoding="utf-8")
txt = P.read_text(encoding="utf-8")
print("final: lines", len(txt.splitlines()), "chars", len(txt))
for probe in ("measures which degenerate model", "not supported on SS"):
    print("  stale", repr(probe), ":", probe in txt)
