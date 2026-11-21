"""Revise the round-15 review after an independent review: Soundness +1 was too generous, because the
2026-10-09 revision removed the only statement that the centralized comparator uses Adam."""
from __future__ import annotations

import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\raven-mcs-tmc-review-r15.md")
lines = P.read_text(encoding="utf-8").split("\n")


def find(pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise SystemExit("anchor not found")


def show(s, n=110):
    print("   " + s.encode("ascii", "replace").decode("ascii")[:n])


# ---- section 2: Soundness no longer moves; weighted delta becomes +0.10 ----
i = find(lambda s: s.startswith("| Soundness | 4 | **5** |"))
show(lines[i])
lines[i] = ("| Soundness | 4 | 4 | 0 | 0.20 | net zero: the contradicted attribution sentence and the "
            "unscoped ceiling bound are both repaired (hunks 3 and 1), but hunk 3 also **removed** the "
            "only statement that the centralized comparator is a short Adam run, while keeping the "
            "2.8 %-3.0 % gap against that comparator, so the disclosure regression offsets the repairs |")

i = find(lambda s: s.startswith("**Weighted progress delta = +0.30"))
show(lines[i])
lines[i] = ("**Weighted progress delta = +0.10 -> classification `improved`.** The single increase passes the "
            "provenance rule: +1 Significance rests on results that were not available to round 14 "
            "(`newly_revealed_by_evidence`). Soundness is unchanged overall, for the reason in its row.")

# ---- section 3: Soundness 5 -> 4, weighted 3.40 -> 3.20, stance 5/10 -> 4/10 ----
i = find(lambda s: s.startswith("| Soundness | **5** |"))
show(lines[i])
lines[i] = ("| Soundness | **4** | 0.20 | high | The two round-14 defects are repaired: the ceiling bound "
            "is scoped to the weight class at the grid's server step, and the learner-versus-weighting "
            "inference is gone. One defect replaces them. L2219-L2220 still reports that window FedAvg "
            "sits 2.8 %-3.0 % above \"a centralized model trained on the same delivered data\" without "
            "stating that the reference is a short Adam minibatch run while the federated step is one "
            "normalized SGD update per window. The 2026-10-07 revision had disclosed exactly that "
            "(\"the centralized reference, trained with Adam, moves its first layer by 12 %\"); the "
            "2026-10-09 hunk deleted the disclosure and kept the comparison, so the current version "
            "discloses less about its comparator than the version it replaced. | Restore the comparator's "
            "update rule and step budget beside the gap, or delete the gap | +1 |")

i = find(lambda s: s.startswith("Weighted readiness ="))
show(lines[i])
lines[i] = ("Weighted readiness = 0.10×2 + 0.20×4 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×3 + 0.05×3 + 0.05×4 "
            "= **3.20**.")

i = find(lambda s: s.startswith("**Overall stance: 5/10"))
show(lines[i])
lines[i] = ("**Overall stance: 4/10, lean reject.** Revised down from 5/10 in this same round after an "
            "independent review of the identical manuscript (sha256 `6FC9BE0B…`) identified the comparator "
            "disclosure regression above; the arithmetic of that review and of mine is identical "
            "everywhere they overlap, and the change is a correction on one cited sentence, not a "
            "response to its lower overall score. Readiness is 3.20, below the 4.0 acceptance threshold, "
            "and no axis carries acceptance on its own: the quantity the introduction sets up "
            "(deployment-target prediction) does not move by a detectable amount, the paper's one "
            "positive measurement is a structural margin whose intervals exclude zero but whose effect "
            "is about 2 % relative, and the released bundle still cannot rebuild the printed numbers.")

# ---- new section 11 ----
assert not any(s.startswith("## 11.") for s in lines)
lines += [
    "",
    "## 11. Correction after an independent review, and what the two reviews differ on",
    "",
    "An independent review of the identical file (`6fc9be0b…`) exists at "
    "`snapshots/2026-10-09-grok-raven-mcs-tmc-review.md`. Its numbers and mine agree everywhere they "
    "overlap, including the twelve values this review recomputed. It found two things this review did "
    "not, and both are accepted here:",
    "",
    "1. **The comparator disclosure regression** (its Soundness deduction, L2218-L2221). This is the "
    "reason Soundness is 4 rather than 5 above. My first pass in this round credited the two repairs "
    "and did not notice that the same hunk had deleted the Adam disclosure the gap depends on.",
    "2. **The limitations paragraph is overloaded.** L2198-L2232 carries arrival bias, masking, the "
    "original server step, the Adam replacement and the later mismatch readout in one paragraph, so "
    "the paper's one positive measurement shares a paragraph with four other topics. That is a real "
    "presentation defect and it is added at R15-7 below.",
    "",
    "The two reviews differ on three dimensions, and the differences are attributable rather than "
    "mysterious:",
    "",
    "| Dimension | This review | The independent review | Basis of the difference |",
    "|---|---:|---:|---|",
    "| Originality | 2 | 3 | Neither review ran a literature search, so neither has evidence for its "
    "number; the difference is a prior about whether the feasible-set projection is a real object, not "
    "a measurement. Both numbers are under-evidenced. |",
    "| Reproducibility | **2** | 3 | This review audited the release: 3 of 9 figure-data files and five "
    "tables disagree with the paper, three drivers are 2-byte stubs, `w1/PAPER_NUMBERS.csv` has no row "
    "for any value added since 2026-10-07, and the shipped PDF is three revisions stale. The "
    "independent review deducts only that the availability section does not name the fifteen-seed "
    "directory, and its own checks list states that it did not re-run the compile or the prose script. "
    "The lower score here is the better-evidenced one. |",
    "| Clarity | 4 | 3 | It charges the undisclosed split means to Clarity as well as to Evidence; this "
    "review charges it once, to Evidence, and keeps Clarity for the two internal-consistency defects "
    "(L2162 against L1834, and the `0.17 %` bound). |",
    "",
    "Two further differences are presentational rather than substantive. The independent review states "
    "its weighted dimension mean as 3.05 / 5 and keeps it explicitly separate from its 1-10 stance; "
    "that is clearer than this review's inherited contract, which reports a weighted sum without "
    "labelling its scale, and its weights differ as well (seven dimensions with Significance at 0.15, "
    "against eight here with Terminology at 0.05 and Significance at 0.10), so the two weighted means "
    "are not comparable. And it declines to do a version comparison at all, calling its reading "
    "absolute; this review reports both a progress card and a readiness card, which is what the frozen "
    "contract asks for but which leaves the scale-labelling ambiguity above to be fixed.",
    "",
    "Both reviews agree on the substantive reading: the structural projection is the defensible part, "
    "the prediction null is real and coarse (its MDE is 5.80 %, so it cannot police a 0.5 % bar in "
    "either direction), the mismatch reductions were scored after the prediction contrast and must not "
    "be promoted, the split means and a constant predictor are absent beside `RMSE_μ`, no fatal "
    "invalidity of a printed result was established, and related work was not searched so novelty "
    "cannot be raised or lowered on this pass.",
]

# add R15-7 to the concern table
i = find(lambda s: s.startswith("| R15-6 |"))
show(lines[i])
lines.insert(i + 1,
             "| R15-7 | Minor | L2198-L2232 carries five topics, including the paper's one positive "
             "measurement; give the Adam result its own paragraph. | `ccf-paper-writer` | Clarity |")

P.write_text("\n".join(lines), encoding="utf-8")
t = P.read_text(encoding="utf-8")
print("\nrevised:", len(t.splitlines()), "lines,", len(t.encode()), "B")
for probe in ("**4** | 0.20 | high", "= **3.20**", "4/10, lean reject", "## 11. Correction"):
    print("  contains", probe, ":", probe in t)
