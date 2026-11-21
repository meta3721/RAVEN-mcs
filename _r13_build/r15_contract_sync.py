"""Sync the round-15 contract with the revised review (Soundness 4, no delta) and record the regression."""
from __future__ import annotations

import json
import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\r15_contract.json")
d = json.loads(P.read_text(encoding="utf-8"))

prog = d["relative_progress_scorecard"]
prog["current"]["Soundness"] = 4
prog["deltas"]["Soundness"] = 0
prog["weighted_delta"] = 0.1
prog["classification"] = "improved"

read = d["absolute_readiness_scorecard"]
read["current_dimension_scores"]["Soundness"] = 4
read["overall_score"] = 3.2
read["stance"] = ("4/10 lean reject, revised down from 5/10 within the same round after an independent "
                  "review of the identical manuscript identified a comparator-disclosure regression; "
                  "readiness is 3.20, below the 4.0 acceptance threshold, and no axis carries acceptance "
                  "on its own")

d["confidence_and_comparability"] += (
    " This contract was corrected after the fact: an independent review of the same file "
    "(snapshots/2026-10-09-grok-raven-mcs-tmc-review.md) showed that the 2026-10-09 hunk deleted the only "
    "statement that the centralized comparator is a short Adam run while keeping the 2.8 %-3.0 % gap "
    "against it. Soundness is therefore 4 on both sides rather than 4 -> 5, the weighted delta is +0.10 "
    "rather than +0.30, and the stance moved to 4/10. The independent review's arithmetic and this "
    "review's agree everywhere they overlap, including all twelve recomputed values.")

# the +1 for the two repairs is offset by a revision-introduced disclosure regression
for issue in d["issues"]:
    if issue["id"] == "R15-1":
        issue["note"] = ("Recorded as a negative historical effect: the two repaired defects depressed "
                         "the historical score by one point and do not depress the current one. The "
                         "current version introduces a different Soundness defect, charged separately "
                         "at R15-8, so the net delta for this dimension is zero.")

d["issues"].append({
    "id": "R15-8",
    "first_seen_version": "round 15 (this comparison)",
    "status": "unresolved",
    "origin": "revision_regression",
    "applies_to": "current",
    "affected_dimensions": ["Soundness"],
    "evidence": "Hunk 3 of the 2026-10-09 revision deleted the sentence 'while on SensorScope the "
                "centralized reference, trained with Adam, moves its first layer by 12 %', which was the "
                "only place the manuscript stated the centralized comparator's optimizer. The same "
                "paragraph retains 'leaves window FedAvg 2.8 %-3.0 % above a centralized model trained on "
                "the same delivered data' at L2219-L2220, so the current version compares a federated "
                "step of one normalized SGD update per window against a short Adam minibatch run without "
                "saying so. 'Adam' now occurs only in reference to replacing the federated server step "
                "(L2222, L2231, L2259). Found by the independent review at snapshots/2026-10-09-grok-"
                "raven-mcs-tmc-review.md and verified here against the round-14 text.",
    "score_effect": {"historical": 0, "current": -1},
})

d["issues"].append({
    "id": "R15-7",
    "first_seen_version": "round 15 (this comparison)",
    "status": "unresolved",
    "origin": "inherited",
    "applies_to": "both",
    "affected_dimensions": ["Clarity"],
    "evidence": "L2198-L2232 carries arrival bias, masking, the original server step, the Adam "
                "replacement and the later mismatch readout in a single paragraph, so the paper's one "
                "positive measurement shares a paragraph with four other topics. Also found by the "
                "independent review; a presentation defect that neither version fixes.",
    "score_effect": {"historical": 0, "current": 0},
})

P.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("contract synced: Soundness 4/4, weighted_delta 0.1, overall 3.2, issues", len(d["issues"]))
for issue in d["issues"]:
    print(f"  {issue['id']:<8} {issue['origin']:<26} {issue['status']:<19} "
          f"effect={issue['score_effect']} dims={issue['affected_dimensions']}")
