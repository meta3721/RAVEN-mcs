# RAVEN-MCS - round 18 independent review

Reviewer: DeepSeek. Skill `ccf-paper-reviewer`, mode `full`, **assessment only: no manuscript file was
modified, no source, figure, or PDF was written.**

## Mode

`full` (scientific + writing + format), single reviewer. No simulated multiple reviewers and no invented
consensus. Where I use the five role lenses of the frozen contract, they are lenses on one reviewer's
evidence, not independent panellists.

## Venue and assumptions

IEEE Transactions on Mobile Computing, journal, method-plus-measurement. Page budget: the project's working
limit of 14 body pages with the supplement not exceeding the body. The current TMC policy statement was not
verifiable this round (see Format/venue concerns), so no format judgement below depends on it.

## Target, and why this is not a delta over round 17

- `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, sha256 `40E9A6A0...`, 89366 B, mtime 2026-10-17 17:01.
- `appendix.tex`, sha256 `6214F734...`, 91297 B, same timestamp.
- `main.pdf` 14 pages, `supplemental.pdf` 14 pages, both 2026-10-17 17:02, i.e. built after the sources.
- Abstract 176 words.

Round 17 scored a different manuscript (`3CC106CA`, 119922 B) and the text between the two was replaced by a
compression rewrite. **This review therefore reports absolute readiness only and deliberately computes no
progress delta**: the skill requires progress and readiness to stay separate, and a delta across a
replacement rewrite that this reviewer did not supervise, with no retained diff base, would be a
manufactured number. Any difference from round 17's 3.55 is a difference between two texts, not a
regression claim.

The tree also changed three times during this session's repair work (16:50, 16:52, 17:01). Every statement
below is bound to the hash above.

## Paper summary

The paper separates two objects that are usually conflated in federated mobile crowdsensing: the
**reference** that sequential selection actually supports (a target mass reconstructed at the sensing-unit
level from opportunity, observation, and usable-update histories) and the **executable allocation** the
current window can realise (client weights under caps, minimum effective support, and group-composition
constraints). RAVEN-MCS builds the reference with layer-specific corrections and Hájek normalisation, then
projects and calibrates it onto the current feasible set, carrying unresolved under-service as a debt. The
theory gives ideal moment recovery under A1-A3 and plug-in stability at a fixed window state. The
measurement programme reports structural gains relative to Uniform, an explicit attribution of how much of
the total structural change Uniform already explains, and a set of nulls and trade-offs on the prediction
side.

## Likely stance and calibrated score

**5/10 borderline negative. Readiness 3.40 of 10 against a 4.0 threshold. Lean reject at this revision.**
The paper is honest and internally consistent; what holds it below the bar is that its own matched-support
table shows the full method losing four of five measured axes to a simpler rule, and the paper supplies no
decision under which that trade is worth the complexity.

## Quantitative scorecard

Dimensions anchored 1-5, weights from frozen contract `TMC-J-R4`; overall weighted 1-10.

| dimension | weight | score | confidence | evidence basis |
|---|---:|---:|---|---|
| Originality | 0.10 | 3 | medium | abstract, Introduction L121-151, the reference-versus-allocation split |
| Soundness | 0.20 | 4 | high | Propositions 2-3 and their assumptions; `tab:trained_rules`; paired-seed protocol |
| Evidence | 0.25 | 3 | high | `tab:trained_rules`, attribution paragraph L1551-1567, abstract, conclusion |
| Clarity | 0.15 | 4 | high | 14-page compressed text, section structure, table captions |
| Reproducibility | 0.10 | 3 | high | Data and Code Availability L1808-1819, submission evidence index |
| Significance | 0.10 | 3 | medium | abstract, L1558-1567, conclusion |
| Related work | 0.05 | 3 | medium | Related Work section; no searched positioning in this round |
| Terminology | 0.05 | 4 | high | matched support, Uniform, reference projection, Design, support rule, coverage Gate |

**Weighted 3.40.** Every dimension scored 3 or below is given its deduction and repair condition below.

### Deductions and repair conditions

- **Originality 3.** Deduction: the conceptual split is real and the nearest neighbours (FedIPW, FedPALS)
  are named and correctly separated as building blocks, but no new machinery is introduced beyond
  projection plus convex calibration, and no searched positioning exists. Repair: one searched paragraph
  that places the reference-versus-allocation distinction against the closest MCS and FL work.
- **Evidence 3.** Deduction: the evidence is adequate for the structural claim and honest about the nulls,
  but it is bounded to two station datasets, constructed `U` on every block, and a prediction endpoint on
  which the method does not win. Repair: none available inside this round's authority; the scoped claim
  must stay structural and the prediction null must stay visible.
- **Reproducibility 3.** Deduction: the availability section now gives a single index with relative paths,
  scoring identities, and a packaged/local-only distinction, which is a genuine improvement, but three
  author fields are still placeholders and the local-only items cannot be inspected by a reviewer.
  Repair: complete the author block; keep local-only material explicitly labelled.
- **Significance 3.** Deduction: the `0.5` pp practical line is cleared stably on SensorScope only, and on
  U-Air the same contrast moves from `.170` on tuning seeds to `.402` on report seeds while the method's
  prediction error is the worst of the six rules. Repair: state what deployment decision the trade
  supports, or narrow the claim to "structural mismatch at a stated prediction cost".
- **Related work 3.** Deduction: nearest neighbours are handled, but coverage of the MCS structural-alignment
  literature was not verified and no search was performed in this round. Repair: a search-backed
  positioning paragraph.

## Top strengths

1. **The abstract, introduction and conclusion all disclose the negative result.** "Structural alignment
   does not consistently improve prediction", "projection can achieve lower group mismatch and runtime than
   the full RAVEN criterion", and "These differences do not establish consistent prediction gains" are in
   the paper's most visible positions. This is not decorative hedging; it matches the tables.
2. **`tab:trained_rules` is the right experiment.** It puts Count, Uniform, reference projection, the
   `kappa=1000` variant, Inst-Cal and full RAVEN on one matched Design-on support with five metrics and
   wall-clock, so "what does the full criterion add" is answered by evidence rather than asserted. Its
   caption also discloses that the U-Air count row uses the restricted RAVEN-Design support and therefore
   differs from the unrestricted FedAvg row elsewhere, which is exactly the disambiguation a careful reader
   needs.
3. **The attribution is quantified rather than asserted.** Uniform accounts for `68.96 %` of the SensorScope
   count-to-RAVEN group reduction and `83.07 %` on U-Air, with the partition given in pp and intervals, and
   the text states that the `.922` pp Design contrast "is not additive with projection - Uniform".
4. **The theory is scoped at the point of statement.** Ideal recovery is attributed to A1-A3 in the
   proposition and in the appendix; stability is "at a fixed window state"; long-run alignment is
   conditional on debt growth; and the text says outright that neither property establishes prediction
   improvement.
5. **The uncomfortable numbers are kept**: Use is not significant, default debt is tiny, the U-Air count row
   is restricted, coverage has a `0.750` failing cell, real `U` is unmeasured, and T-Drive does not pass its
   descriptive tolerance.

## Major concerns

**C1 (decisive). The full method loses to a simple projection on four of five axes, and no decision rule
makes the trade.** In `tab:trained_rules`, SensorScope reference projection is better than full RAVEN on
`Delta_group` (1.01158 vs 1.01394), `RMSE_mu` (7.93725 vs 7.93799), `WorstGroupRMSE` (8.66989 vs 8.67066)
and wall-clock (19.9 s vs 27.1 s); full RAVEN is better only on `Delta_c-s` (1.26438 vs 1.26903). On U-Air
the ordering flips and both are worse than Uniform on prediction. The paper reports this, but never says
which operator, endpoint, or regime would pay 36 % more runtime and a prediction cost for a `Delta_c-s`
gain of `0.0005`. **A TMC method paper has to answer that.** Repair class: a stated decision rule bound to a
named use case, or a narrowed contribution that presents the full criterion as a diagnostic variant rather
than the method.

**C2. On U-Air the method's prediction error is the worst of the six rules.** Reference projection
`RMSE_mu = 1.19691` and `WorstGroupRMSE = 1.26474` against Uniform `1.19349` / `1.26094` and Count
`1.19225` / `1.25956`. The structural gain (`1.09162` vs `1.09734`) is real but the same row set pays for it
in accuracy. Because the paper's own criterion of interest is a deployment-target *risk*, a reviewer will
ask whether a structurally better but less accurate allocation is a gain or a cost. Repair class: state the
criterion explicitly (structure subject to a prediction constraint, or vice versa) instead of leaving the
reader to weigh two columns.

**C3. `0.5` pp is an author-defined practical line and only one block clears it stably.** The text is candid
that SensorScope clears it and U-Air moves from `.170` to `.402` across seed slices. A self-set tolerance
that one block clears, on a metric the authors define, cannot carry practical significance on its own.
Repair class: tie the `0.5` pp line to an external quantity (a target-mass error tolerated by an operator, or
a mismatch threshold implied by a published protocol), or present it as a study-internal reference value.

**C4. Every block uses a constructed `U`, and no deployment test exists.** The paper says so. For a venue
that values measurement, this is the dominant scope limit: the "usable-update" layer is the one that cannot
be validated on public data, and it is also the layer the method's third correction depends on. Repair class:
none within this round's authority; the limitation must stay explicit, and the City Scanner blocks must not
be described as validation of `U`.

**C5. The evidence base is two station datasets plus City Scanner protocols, at 20 seeds, all labelled
development.** Tables VI and VII and the appendix learning/geometry material are declared development-only
by the text, which is honest, but it means the *reported* structural effect rests on SensorScope and U-Air
alone. Repair class: none new; keep the development labels.

**C6. Related work: nearest neighbours are correct, coverage is unverified.** FedIPW and FedPALS are named
with their actual mechanisms and the "building blocks vs new object" separation is the right one. No search
was performed, so I cannot certify that no closer MCS-side structural-alignment work exists. Repair class:
one searched positioning paragraph.

## Writing and presentation concerns

1. The compression is aggressive and the reading load is high. Several paragraphs carry three or four
   distinct claims; the attribution paragraph L1551-1567 in particular packs the partition, the practical
   line, the tuning-versus-report instability, the direct-reference readouts, and the non-additivity warning
   into one block. A reader must work to recover which claim each number supports. **Improvement class:
   paragraph break at the practical-line sentence, not new content.**
2. The paper uses "count weighting", "Uniform", "FedAvg", and "matched support" in close proximity across
   two tables. The captions disambiguate, but the body would benefit from one sentence stating that
   "Count / matched support" is the restricted-support count rule, once, before the first table.
3. The abstract at 176 words is within the venue's 100-200 word range and contains no equations or
   citations, which matches the official requirement.
4. No em-dash, filler-opener, or defensive-phrasing problem was found in the passages read this round.

## Format/venue concerns

1. **Author block is still a placeholder state.** `main.tex` L61 has `**** and Anfeng Liu`; L63 has `***` and
   `****@csu.edu.cn`. Two occurrences of `****` and three of `***` remain overall. This alone prevents the
   file set from being submitted as-is, independent of any scientific question.
2. **Page budget: satisfied.** `main.pdf` 14 pages, `supplemental.pdf` 14 pages, both measured after the
   current sources, both with 0 undefined references and 0 Overfull as of this review's build check.
3. **The current TMC rule set is not verified.** The Computer Society author page was retrieved this round
   and establishes that page limits include abstracts, references and author biographies, that the abstract
   is 100-200 words for a regular journal paper, that supplemental material must be a separate file, and that
   journal author biographies are not required. **It does not establish TMC's own page limit**, which lives
   on a client-rendered TMC page and behind a 403 submission portal. So "14 pages" is the project budget and
   the measured count, **not** a verified TMC limit.
4. Supplemental figures 5 and 6 in the appendix carry an explicit statement that their rows are the frozen
   run set and that some active sets differ from the matched-support table, so they no longer carry a
   same-support claim. The underlying per-arm support records for three baselines are still missing, so the
   two exhibits remain labelled-but-ununified; that is the honest maximum available without a re-run.

## Multi-reviewer panel (single reviewer, five lenses)

```text
Lens: Best-justified
Score tendency: 4-5   Confidence: high
  + every headline claim I checked has a table or a proposition behind it, and the negatives are stated
  - the paper's strongest evidence argues against its own full method
Lens: Critical
Score tendency: 3     Confidence: high
  - the full criterion's value is not established; a simpler rule beats it on 4 of 5 axes
  - U-Air prediction is the worst of six rules
Lens: Method / soundness
Score tendency: 4-5   Confidence: high
  + propositions are scoped correctly and the appendix condition map now matches them
  - no decision rule for the multi-endpoint trade-off
Lens: Reproducibility
Score tendency: 3     Confidence: high
  + single evidence index with scoring identities and a packaged/local-only split
  - author placeholders; local-only items unverifiable by a reviewer
Lens: Writing and presentation
Score tendency: 4     Confidence: medium
  + honest abstract and conclusion; captions disambiguate supports
  - dense compression; one overloaded attribution paragraph
```

```text
Agreement (across lenses): the text is honest and internally consistent, and the tables support the claims
Disagreement: the Method lens would score the paper up on scoping while the Critical lens scores it down on
  the full method's value; that disagreement is substantive and the paper itself does not resolve it
Decisive accept axis: a structural-alignment criterion with a demonstrated decision value
Decisive reject axis: the full method's own table shows a simpler projection is better on most axes
Final calibrated stance: 5/10 borderline negative, lean reject at this revision
```

## Concern-to-action table

| # | concern | severity | affected criterion | fix class | owner skill | score-impact condition |
|---|---|---|---|---|---|---|
| C1 | full method loses to projection on 4/5 axes, no decision rule | **decisive** | Significance, Evidence | state a decision rule or narrow the contribution | `ccf-paper-writer` with author decision | Significance +1 if the trade is bound to a named use case |
| C2 | U-Air prediction is worst of six rules | major | Evidence | state the criterion (structure subject to prediction, or the converse) | `ccf-paper-writer` | Evidence +1 if the criterion is explicit and the claim narrowed accordingly |
| C3 | `0.5` pp line is self-set, one block only | major | Significance | anchor the line to an external quantity, or re-label as internal | author decision | Significance +1 |
| C4 | no measured real `U` anywhere | major | Evidence | keep explicit; do not describe City Scanner as validating `U` | none authorized | no score change; scope limit |
| C5 | reported effect rests on two station datasets | major | Evidence | keep development labels | none authorized | no score change |
| C6 | positioning unsearched | minor | Related work, Originality | one searched paragraph | `ccf-literature-searcher` then `ccf-paper-writer` | Related work +1, Originality +1 |
| F1 | author placeholders | blocking for submission | Reproducibility, format | fill from authoritative identity | author | required before submission |
| F2 | TMC page limit unverified | blocking for compliance | format | read it in the submission portal | author | required before submission |

## Recommended next CCFA owner

`ccf-paper-writer` for the two writing-class items only (the paragraph break at the practical-line sentence,
and one clarifying sentence on "Count / matched support"). **C1-C3 are author decisions, not editing tasks**;
no `ccf-paper-writer` pass can close them. C6 belongs to `ccf-literature-searcher`. F1-F2 belong to the
author.

## Checks run

- Read the abstract, the Introduction's gap and contribution passages, the matched-support subsection and its
  table, the attribution paragraph, the conclusion, and the availability section in the current file.
- Verified the shipped PDFs post-date the sources: sources 17:01, PDFs 17:02, both 14 pages.
- Verified abstract word count 176 against the official 100-200 range.
- Verified the repair markers from the 2026-10-17 repair round are present in this text: the S2 condition
  mapping (`rests on A1--A3`), the S4 terminology (`support rule`), the S1 caption statements
  (`same-support claim`, `current-runner re-run`), and the S3 availability entry.
- **Two of my own probes were wrong and are recorded**: an `-match` on the S3 index string returned false
  because the source splits the path with `\allowbreak` across two lines, and an earlier probe reported the
  S2 closing clause missing for the same line-break reason. In both cases the text was intact; the probes
  are the defect. Neither mistaken report was allowed to stand in a deliverable.

## Unresolved or unverified

- No literature search: Originality and Related work carry medium confidence and are not moved by this
  review.
- No re-derivation of the proofs; no re-implementation of baselines; no re-run of any experiment; no
  re-scoring. The prediction-side numbers are taken from the table as printed.
- The City Scanner tables were not re-read this round, so the abstract's City Scanner sentence is recorded as
  "not re-verified here" rather than as supported.
- The current TMC page and anonymity rules remain unverified.
- The three baselines' frozen-run support records remain missing, so the two appendix figures stay
  labelled-but-ununified.

## Output self-check

- Section order follows the skill's standard contract.
- No score was given without an evidence basis; every score of 3 or below carries a deduction and a repair
  condition.
- Progress and readiness were not fused: this review reports readiness only and explicitly declines to
  compute a delta across a replacement rewrite.
- No acceptance probability, no invented consensus, no invented citation, no invented score change.
- No manuscript file was written, and no recommendation below is phrased as an edit to be applied without an
  author decision where one is required.
