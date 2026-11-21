# RAVEN-MCS - round 17 review

Reviewer: DeepSeek. Skill `ccf-paper-reviewer`, mode `full` (scientific + writing + format), delivered
assessment-only. **No manuscript file was touched.**

Why this report is at `-deepseek-r17.md` rather than at the canonical
`ccfa-review-reports/raven-mcs-tmc-review.md`: the skill's step 8 says to write or overwrite the canonical
report, but that path currently holds an independent reviewer's report, and overwriting it once already in
this session is a recorded process defect (diagnosis ledger item 78). The project convention that follows
from that incident is that the canonical path belongs to the independent reviewer and this reviewer's
rounds are suffixed. That is a deliberate deviation from step 8, recorded here rather than left implicit.

## Mode

`full`, assessment-only, under the frozen contract `TMC-J-R4`. Target: the single title/abstract/conclusion
pass plus a second pass over the argument and evidence, and a third pass stress-testing the central
contribution; the whole file was read for the earlier rounds of this contract, and this round re-read the
claim-bearing regions.

## Venue and assumptions

IEEE TMC, journal revision, method-plus-measurement paper. Page budget: TMC regular 12 pp with a project
allowance up to a hard 18 pp. Nothing in this review depends on unpublished author intent.

## Paper summary

RAVEN-MCS attacks completion under two-stage non-random selection in asynchronous federated mobile
crowdsensing. Its central claim is negative and structural: the arrival law of usable updates and the
public deployment target are different laws, the risk functionals they induce are not interchangeable, and
a selection-corrected reference calibrated inside the current feasible window buys **mismatch**, not
accuracy. The paper proves the non-interchangeability, defines the corrected reference, and reports a
measurement programme whose prediction-endpoint results are nulls while its structural results separate.
It refuses, in its own abstract, both the optimisation claim and the RMSE win.

## Likely stance and calibrated score

**5/10 borderline negative. Readiness 3.55 of 10, below the 4.0 acceptance threshold. Lean reject at this
revision.** The prose is not what holds it there.

## Quantitative scorecard

Dimensions anchored 1-5; overall weighted 1-10; contract `TMC-J-R4`, weights 0.10/0.20/0.25/0.15/0.10/0.10/0.05/0.05.

| dimension | weight | score | confidence | evidence basis | deduction | repair condition |
|---|---:|---:|---|---|---|---|
| Originality | 0.10 | 2 | medium | title, abstract, intro, contributions | reframing without new machinery; the paper's own contribution 4 concedes the prediction half is not a null | a searched positioning result that separates this framing from closest prior art |
| Soundness | 0.20 | 5 | high | main.tex L2236-L2238, L2242-L2246 | none charged; the comparator's rule and scale are stated, so the one unsupported comparison is gone | n/a |
| Evidence | 0.25 | 3 | high | abstract, `subsec:ceiling`, `subsec:limitations`, TE1/TS1/TE2 artifacts | no endpoint whose headroom exceeds its detectable effect **in the manuscript**; the project's strongest measurement is unreported | report the concentration ladder; verified to fit 18 pp in a two-site scope (S4) |
| Clarity | 0.15 | 5 | medium | L2224, L2249-L2252, L1885-L1888 | none charged; the two reader-facing contradictions are repaired and both comparators are named | n/a |
| Reproducibility | 0.10 | 2 | high | Data and Code Availability; bundle and PDF state | the two new trees are named but not deposited, `w1/PAPER_NUMBERS.csv` indexes nothing added since 2026-10-07, the shipped PDF is the 2026-10-06 artifact, and one revision in the chain is unattributed | deposit the trees, extend the index, refresh the PDF, attribute or revert the `+75 B` change |
| Significance | 0.10 | 3 | medium | abstract, `subsec:eval_rq2`, `subsec:ceiling` | the structural half is defensible and the prediction half is a null; no deployment decision changes and the mismatch reduction is about 2 % relative | a bounded ceiling statement turns the negative into a reusable design guideline |
| Related work | 0.05 | 3 | medium | reference list; no search performed in any round | the novelty band is asserted rather than sourced | one searched positioning paragraph |
| Terminology | 0.05 | 4 | high | metric definition, table captions | none charged; the two-constant naming added distinctions | n/a |

**Weighted 3.55.** Every score of 3 or below above carries its deduction and its repair condition.

## Top strengths

1. **The negative result is honestly scoped.** The abstract refuses both the optimisation claim and the RMSE
   win, and contribution 4 refuses the attribution the data does not support.
2. **The comparator is now fully specified**, so the "2.8 %-3.0 % above a centralized model" statement is
   interpretable rather than misleading.
3. **The metric's two reference constants are named with their values**, which retires the largest clarity
   hole: a reader can no longer compare arms against an unnamed oracle.
4. **The null is reported with its resolution limit** rather than as a bound the measurement cannot support.

## Major concerns

**Concern 1 - the paper's strongest measurement is not in the paper (Evidence, blocking for the stance).**
The project holds a pre-registered ladder over deployment-target concentration, measured on the only block
with feasible-set slack: the oracle gap rises monotonically and detectably with concentration, and at the
single-region limit, which is the most concentrated target that exists, the whole weight class buys
`+0.097 %` of the deployment-weighted error with interval `[+0.067 %, +0.130 %]`. The manuscript reports
none of it.

Claim-evidence audit, in the rubric's format:

```text
Claim: the recoverable gain of the corrected-reference weight class is bounded, not merely unobserved
Where stated: subsec:ceiling, argued from partition structure and the stress grid
Evidence provided: the grid's H over four stress axes, and the cost of estimating the margins
Evidence type: measured, but for the target-distribution axis only up to near-uniform targets
Strength: adequate for the claim as scoped; weak for a reader who asks whether concentration changes it
Reviewer deduction: -1 on Evidence (held at 3, not lower, because the repair is one paragraph away)
Required fix: report the concentration ladder in subsec:ceiling
```

**Concern 2 - the repair is a page-budget decision, not a writing task, and my round-16 cost estimate was
wrong.** Round 16 presented the repair as "three sentences". The measured cost is different: the four
insertions the plan specifies total `+1879 B` and build to **19 pages** against a hard 18 pp allowance,
while the ceiling paragraph alone (`+1227 B`) and the ceiling paragraph plus the availability naming
(`+1407 B`) both build to **18 pages**. Correcting my own estimate is part of this review: the repair is
cheap in prose and expensive in layout, and the right response is to choose which insertions earn their
space, not to shorten the measurement.

**Concern 3 - Reproducibility is the second binding constraint and is fixable without new work.**
The availability section names the two run trees and the confirm seed range, which is half of round 15's
charge. A reader who takes the bundle still cannot reproduce the Adam half, cannot locate any number added
since 2026-10-07 in the index, and receives a PDF older than the source. One revision in the chain
(`7b874f28` -> `1d6515ff`, `+75 B` on 2026-10-09) has no provenance record.

**Concern 4 - Related work is asserted (this is a limitation of every round of this review, including this
one).** No literature search has been performed in any round of this session, so Originality and Related
work carry medium confidence. The round's own dataset search was a benchmark search with no verified
candidate and cannot stand in for a novelty search.

## Writing and presentation concerns

- The ceiling subsection now carries three measurements in one paragraph block; adding the ladder makes it
  four. It remains readable, but the ladder is the one that could be given its own paragraph break.
- The inserted sentence must compare against **the subsection's own `0.5 %` bar** (L2131-L2132). The `2 %`
  figure used as the decision threshold in the TE2 experiment design is an internal planning choice and
  must not appear in the manuscript; the round that drafted the insertion caught exactly this.
- No em-dash, filler-opener, or defensive-phrasing issue arises in the drafted insertions (em dashes 0/3
  paper-wide).
- The abstract, title and contribution list remained byte-identical through the drafting round, which is
  the desired scope: this is a measurement disclosure, not a repositioning.

## Format/venue concerns

- 18 pp is the allowance and the current source sits exactly at it. Any further insertion needs a named
  trade, and no insertion may push the build to 19 pages.
- No table is proposed for the ladder. A four-row table would read better but costs more page budget than
  the prose it replaces; if the author wants it, it is a `ccf-visual-composer` request with its own budget
  decision.
- No compliance issue found at this pass; final template/page/anonymity checks belong to
  `ccf-submission-checker`.

## Multi-reviewer panel

```text
Reviewer: Best-justified
Lens: is the paper's own claim the strongest one its evidence can carry?
Score tendency: 5-6
Confidence: high
Main positive signal: the abstract refuses the optimisation claim and the RMSE win; contribution 4 refuses
  an unsupported attribution
Main negative signal: the ceiling section argues a bound it could measure, and the measurement exists
Evidence basis: main.tex L2121-L2143, L2242-L2259; TE2_STEP4_VERDICT.json
Score-change condition: report the ladder
```

```text
Reviewer: Critical
Lens: what would a hostile reviewer attack first?
Score tendency: 3-4
Confidence: high
Main positive signal: the comparator-disclosure defect raised in round 15 is repaired
Main negative signal: the structural result that carries Significance is about 2 % relative on mismatch
  metrics, changes no deployment decision, and was scored after the prediction contrast
Evidence basis: TS1_SUMMARY.json; main.tex L2253-L2259
Score-change condition: a pre-registered endpoint that changes a stated decision, or a bounded ceiling that
  makes the negative reusable
```

```text
Reviewer: Method / soundness
Lens: can the numbers be trusted and are the assumptions discharged?
Score tendency: 5
Confidence: high
Main positive signal: the two-constant disclosure and the named optimizer rule remove the two places where
  a number could be misread
Main negative signal: none found at this pass; the residual is the unreported ceiling
Evidence basis: L1606-L1614, L1885-L1888, L2249-L2252, L2236-L2238
Score-change condition: n/a
```

```text
Reviewer: Reproducibility auditor
Lens: can a third party recompute what the paper prints?
Score tendency: 2-3
Confidence: high
Main positive signal: the trees behind the newest results are now named, with the confirm seed range
Main negative signal: they are not in the bundle, the number index is stale, the shipped PDF is older than
  the source, and one revision is unattributed
Evidence basis: Data and Code Availability; bundle and PDF state
Score-change condition: deposit, index, refresh, attribute
```

```text
Reviewer: Writing and presentation
Lens: can the contribution, mechanism, evidence and limitations be recovered in one pass?
Score tendency: 5
Confidence: medium
Main positive signal: both reader-facing contradictions are repaired and both constants are named
Main negative signal: the ceiling subsection is accumulating measurements in one block
Evidence basis: L2121-L2143, L2224, L2249-L2252
Score-change condition: n/a
```

```text
Agreement: the manuscript's text is the cleanest this contract has scored, and the binding constraints are
  outside the prose: one unreported measurement and one release gap
Disagreement: none material; the Critical reviewer weighs Significance lower than the Best-justified
  reviewer does, which is the same disagreement round 15 recorded and is not resolvable by argument
Decisive accept axis: a bounded, well-measured negative that a systems reader can reuse as a design rule
Decisive reject axis: the strongest evidence for that negative is not in the paper and the newest half
  cannot be reproduced from the released bundle
Unresolved evidence: no literature search in any round, so novelty and positioning are unverified
Final calibrated stance: 5/10 borderline negative, lean reject at this revision
```

## Concern-to-action table

| # | concern | severity | affected criterion | fix class | owner skill | score-impact condition |
|---|---|---|---|---|---|---|
| 1 | the concentration ladder is unreported | major | Evidence | report the measurement | `ccf-paper-writer`, two-site scope | Evidence 3 -> 4, readiness +0.25 |
| 2 | the repair is page-budget constrained | major | Evidence, format | choose which insertions earn space | `ccf-paper-writer` | necessary for concern 1 |
| 3 | the newest half is not reproducible from the bundle | major | Reproducibility | release discipline | `ccf-submission-checker` | Reproducibility 2 -> 3, readiness +0.10 |
| 4 | positioning is asserted | minor | Related work, Originality | searched positioning paragraph | `ccf-literature-searcher` then `ccf-paper-writer` | Related work 3 -> 4, readiness +0.05 |
| 5 | the ceiling subsection is accumulating | minor | Clarity | paragraph break | `ccf-paper-writer` | no score change expected |

## Reviewer recommendation on the blocked decision

Of the three options on the table:

- **Option A, the two-site scope, is the recommendation**, and it is not a compromise. The dropped
  limitations cross-reference is **redundant**: L2248 already sends the reader to
  `Section~\ref{subsec:ceiling}` from inside the limitations paragraph, so the insertion would have said
  what the paragraph already says. The only real loss is the conclusion clause, which repeats a number that
  lives in the ceiling subsection.
- **Option B is worse than it looks.** Compressing the ceiling paragraph by four lines would mean dropping
  the monotonicity statement, the single-region-as-upper-bound argument, or the control's identity. Those
  are exactly what make the `+0.097 %` a bound rather than a number, and a bare number invites the
  objection that concentration was never varied. The measurement is worth more than the two cross-references
  it would displace.
- **Option C is unnecessary** for the same reason A is sufficient, unless the author also wants the
  conclusion to carry the ceiling.

**The reviewer does not treat the blocked round as a failure.** A gate that stops a change which would have
put the manuscript one page over its allowance, and a number check that caught a design-stage analytic value
(`0.2500`) standing in for the measured one (`0.2558`) before it reached the file, are both the process
working.

## Recommended next CCFA owner

`ccf-paper-writer`, to apply Option A under the existing execution prompt and re-run its gates; then
`ccf-integrity-auditor` for number and claim consistency; then `ccf-paper-reviewer` for a round-18 read of
Evidence. Release work on concern 3 runs in parallel and belongs to `ccf-submission-checker`.

## Checks run

- Manuscript sha256 verified as `3CC106CA4B6087D9D6A47D69936ABF0CD95914B0285E1A86D3C938ACB5AD161C`,
  119922 B, unchanged since the blocked writing round.
- Cross-reference audit: `\ref{subsec:ceiling}` occurs at L2119 and L2248, which is what makes Option A
  redundant-lossless.
- Build evidence reused from the writing round's own measurements (pre-edit 18 pp; ceiling alone 18 pp;
  ceiling + availability 18 pp; all four 19 pp), each taken with the same command sequence and restored in a
  `finally` block whose assertion on the pre-edit hash passed.
- Number traceability: twelve of twelve drafted numbers recompute from the TE2 artifacts; the frozen rung's
  share is `0.2558` from `TE2_PHASE0.json`, not the design-stage `0.2500`.
- Version-comparison card validated by `scripts/validate_version_comparison.py`; because the target text is
  byte-identical to round 16's target, the card must classify progress as `unchanged`, which is a check on
  the review itself rather than on the paper.

## Unresolved or unverified

- No literature search, so Originality and Related work remain asserted rather than verified.
- No re-derivation of the proofs and no re-implementation of the baselines in this round.
- The `+75 B` revision remains unattributed; this review cannot determine its content or intent.
- The bundle's internal state (which figure-data files and tables differ from the paper) was audited in
  round 13 and is carried forward rather than re-audited here.

## Output self-check

- Section order follows the skill's standard contract, with the version-comparison content kept separate
  from the readiness scorecard as the shared standard requires.
- Every score of 3 or below carries a deduction and a repair condition.
- The two scorecards are not combined: relative progress is `unchanged` at 0.00 while absolute readiness is
  3.55, and they answer different questions.
- Confidence is reported per dimension and is not folded into either score.
- No placeholder, no acceptance probability, and no recommendation of rhetorical strengthening for an
  unsupported claim.
- The single deviation from the skill's workflow, writing to a suffixed path instead of the canonical one,
  is stated with its reason.
