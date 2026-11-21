"""Splice the corrected sections into the round-14 review by slicing on headings, not long literals."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
P = ROOT / "_r13_build/raven-mcs-tmc-review-r14.md"
SEC3 = (ROOT / "_r13_build/r14_sec3_new.md").read_text(encoding="utf-8").replace("ceil ing", "ceiling")
SCORES = (ROOT / "_r13_build/r14_scores_new.md").read_text(encoding="utf-8").rstrip("\n").split("\n")

lines = P.read_text(encoding="utf-8").split("\n")


def find(pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise SystemExit("anchor not found")


# ---- 1. replace section 3 entirely (from '## 3. ' up to '## 4. ') ----
i3 = find(lambda s: s.startswith("## 3. "))
i4 = find(lambda s: s.startswith("## 4. "), i3 + 1)
lines = lines[:i3] + SEC3.rstrip("\n").split("\n") + [""] + lines[i4:]

# ---- 2. replace the Soundness / Evidence / Clarity scorecard rows ----
for prefix, newrow in zip(("| Soundness |", "| Evidence |", "| Clarity |"), SCORES):
    j = find(lambda s, p=prefix: s.startswith(p))
    lines[j] = newrow

# ---- 3. replace the weighted total and the stance paragraph ----
j = find(lambda s: s.startswith("Weighted readiness ="))
k = find(lambda s: s.startswith("## 6."), j + 1)
lines = lines[:j] + [
    "Weighted readiness = 0.10×2 + 0.20×4 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×4 = **3.10**.",
    "",
    "**Overall stance: 4/10, lean reject.** Round 13 was 5/10 borderline at 3.30, and I first wrote "
    "3/10 here on the strength of the finding withdrawn in section 3; that score was not justified and "
    "this correction raises it. What remains is one moderate methodological concern (L2220–L2221 derives "
    "a learner-level cause from an optimizer contrast) plus one reporting gap (the undisclosed "
    "train → test target-level shift). Neither is fatal, no theorem and no printed number is affected, "
    "and the relative comparisons stand. If the level shift is stated as an intended out-of-period "
    "evaluation and the per-split target statistics are reported, this moves to 5/10.",
    "",
] + lines[k:]

# ---- 4. replace the revision-log bullet ----
j = find(lambda s: s.startswith("- **Revision log for this canonical file.**"))
k = find(lambda s: s.startswith("- The 22:57 edit's authorization"), j + 1)
lines = lines[:j] + [
    "- **Revision log for this canonical file.** Three positions, all dated 2026-10-08, kept so the path "
    "is auditable. (1) First version: Soundness 3 / Evidence 3 / overall 2.90, 4/10, asserting that the "
    "S1' round *strengthens* the ceiling argument and that the federated arm \"beats the centralized "
    "reference by 1.4–16.7 %\" — both **withdrawn**. (2) Second version: after two commissioned "
    "independent checks returned, Soundness 2 / Evidence 2 / overall 2.30, 3/10, asserting that on "
    "SensorScope and U-Air every deposited arm is worse than the constant predictor and therefore has no "
    "skill — **the inference withdrawn**; the arithmetic was right but the constant was an oracle over "
    "the test split, and the deciding split statistics are in section 3. (3) This version: Soundness 4 / "
    "Evidence 3 / Clarity 4 / overall **3.10**, 4/10, with the train-to-test target-level shift as the "
    "surviving, narrower finding. The author's rebuttal is what forced position (3).",
] + lines[k:]

P.write_text("\n".join(lines), encoding="utf-8")
txt = P.read_text(encoding="utf-8")
print("spliced. lines:", len(txt.splitlines()), "| chars:", len(txt))
for probe in ("withdrawn", "3.10", "4/10, lean reject", "train target mean (sd)"):
    print(f"  contains {probe!r}: {probe in txt}")
print("  stale 'decisive finding' heading present:", "The decisive finding" in txt)
print("  stale '2.30' present:", "2.30" in txt)
