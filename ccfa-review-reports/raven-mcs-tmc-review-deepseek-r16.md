# RAVEN-MCS — round 16 manuscript review

Reviewer: DeepSeek. Skill `ccf-paper-reviewer`, mode `scientific/full`, with new-evidence intake and a
version-comparison card. Contract `TMC-J-R4`, frozen and inherited unchanged.

## 1. Target, contract, comparability

- **Current text**: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, sha256 `3CC106CA4B6087D9...`, 119922 B,
  18 pp on a clean rebuild, LF only, mtime 2026-10-10 20:59. Read directly.
- **Historical text**: `6fc9be0b...`, 117864 B — the target round 15 scored. Both versions are on the same
  frozen contract, so the delta is like-for-like.
- **Contract**: `TMC-J-R4`, eight dimensions, weights 0.10/0.20/0.25/0.15/0.10/0.10/0.05/0.05, dimensions
  anchored 1-5, overall 1-10, acceptance 4, `|delta| < 0.05` counts as unchanged.
- **Confidence**: high on the three axes this round touched (Soundness, Clarity, Reproducibility — every
  charged site was read and, where text moved, byte-verified); medium on Originality and Related work,
  because **no round of this session has performed a literature search**, including this one. The
  round-16 submission presents Originality as the binding constraint on the stance, so that gap is
  material and is recorded as a limitation of the review rather than of the paper.

## 2. Axis scores

| axis | weight | historical | current | delta | basis |
|---|---:|---:|---:|---:|---|
| Originality | 0.10 | 2 | 2 | 0 | framing reframing without new machinery; unsearched, so held rather than moved |
| Soundness | 0.20 | 4 | **5** | **+1** | the comparator-disclosure regression is repaired; no unsupported claim added |
| Evidence | 0.25 | 3 | 3 | 0 | the axis is limited by the manuscript's scope, not by the science (S5.3) |
| Clarity | 0.15 | 4 | **5** | **+1** | both remaining charged defects repaired; the two-constant disclosure is in place |
| Reproducibility | 0.10 | 2 | 2 | 0 | narrowed, still binding (S5.4) |
| Significance | 0.10 | 3 | 3 | 0 | the structural half stays defensible, the prediction half stays a null |
| Related work | 0.05 | 3 | 3 | 0 | unsearched in every round |
| Terminology | 0.05 | 4 | 4 | 0 | the new naming added distinctions rather than collisions |

**Weighted readiness 3.55** (historical 3.20, weighted delta **+0.35**, classification `improved`).
**Stance 5/10 borderline negative.** Below the 4.0 acceptance threshold; no axis carries acceptance alone.

## 3. Version-comparison card

Machine-checked against `scripts/validate_version_comparison.py`; the contract file is
`_r13_build/r16_contract.json`. Seven issues, none carrying a negative current effect, so no decrease is
unexplained.

| id | axis | origin | status | effect (hist -> cur) |
|---|---|---|---|---|
| R16-1 | Soundness | inherited | resolved | 0 -> **+1** |
| R16-2 | Clarity | inherited | resolved | 0 -> **+1** |
| R16-3 | Evidence | newly_revealed_by_evidence | unresolved | 0 -> 0 |
| R16-4 | Reproducibility | inherited | partially_resolved | 0 -> 0 |
| R16-5 | Reproducibility | inherited | unresolved | 0 -> 0 |
| R16-6 | Related work | inherited | unresolved | 0 -> 0 |
| R16-7 | Evidence, Significance | inherited | partially_resolved | 0 -> 0 |

## 4. New evidence intake

Seven items entered this round's assessment. All are repository artifacts at stated hashes; none is an
author promise.

| # | item | what the review did with it |
|---|---|---|
| E1 | **TE1** — the Adam server-step replacement confirmed on NSW-Traffic: 15 paired confirm seeds, `mean_H = -0.014921178351331239`, CI `[-0.0542302207818337, +0.0175677080705695]`, `MDE80 = 0.05802695298194278`, verdict `NO-GO-H` (`TE1_VERDICT.json`) | corroborates the manuscript's limitation paragraph; its detectable effect is 3.9x the point estimate, so it cannot police the 0.5 pp bar — which the manuscript now says |
| E2 | **TS1** — structural readout of the same runs: `Delta_group` `0.007875461474741708` `[0.005050083024358629, 0.011032292876163016]`, `Delta_c-s` `0.009939661215117069` `[0.006724524039012507, 0.013241532821026799]`, both `SEPARATED-ORACLE` | already reflected in the round-15 Significance score; the review re-confirms it is **post-hoc** and keeps it off Evidence |
| E3 | **Two-constant disclosure** — the metric definition now names the test-fitted constant `2.088`/`0.678`/`1.007` and the training-mean predictor `7.647`/`1.054`/`1.007` with ratios 3.7x/1.6x | retires the largest clarity hole; verified at L1606-L1614, L1885-L1888, L2249-L2252 |
| E4 | **Honesty text repairs (HT)** — conclusion readout order, the MDE-versus-0.5 %-bar clause, availability naming the two run trees and the seed range, one rewrap (`HT_GATES.md`, `HT_EDITS.md`) | Soundness and Clarity gains; the byte-level reverse-replacement proof establishes that nothing else moved |
| E5 | **Block screen (BS)** — all four project datasets screened for target concentration and feasible-set slack (`BLOCK_SCREEN.json`) | grounds the new negative; shows the failure directions are complementary |
| E6 | **Dataset search** — 12 public queries, no candidate met the inclusion bar (`literature-search-20261009-concentrated-target/`) | outcome is "not found", explicitly not "does not exist"; recorded as a search result |
| E7 | **TE2** — Phase 0 power gate (`CONTINUE`), step 3 primary cell at `kappa = 5`, and the alternate step 4 **ceiling ladder** (`TE2_VERDICT.json`, `TE2_STEP4_VERDICT.json`) | the strongest scientific result the project now holds, and the reason S5.3 exists |

## 5. Findings

### 5.1 The comparator-disclosure regression is repaired (Soundness 4 -> 5)

Round 15's only current-version deduction was R15-8: the 2026-10-09 revision deleted the sentence naming
the centralized comparator's optimizer while keeping the "2.8 %-3.0 % above a centralized model" claim, so
the paper compared one normalized SGD update per window against a short Adam minibatch run without saying
so. The current text states the rule and its scale: `lr=1e-3`, Adam, minibatch `min(32, n)`, and the
federated side as one step-normalized update per window. That is a disclosure, not a hedge, and it removes
the only unsupported comparison in the paper. Nothing in this round added a claim the evidence does not
support, and the one place where a caveat could have been misused — the null's resolution limit — is now
stated as a limit of the measurement rather than as a bound on the effect.

### 5.2 Both remaining clarity defects are repaired (Clarity 4 -> 5)

The two defects round 13 charged and round 15 re-confirmed are gone. The contradiction between
"the small margin" and "above the 0.5 pp practical line" is removed (`small margin` now occurs zero
times), and the `0.17 %` bound that its own source crossed is now `0.175 %`, above the largest observed
level mean of `0.1747 %`. The paragraph overload round 15 charged separately is split. Verified in the
current text: L2224 carries `0.175 %`, L2251-L2252 reads the `1.007` cell against the named test-fitted
constant and notes the training-mean predictor takes the same value, and the table caption at
L1885-L1888 names both references. The round's own attempt to find a further defect — contribution 4's
"the corpus is not a null" against the limitations' "no detectable headroom" — resolved to two different
objects (a U-Air component-removal ablation versus the paired oracle-margin headroom on NSW-Traffic), so
no edit was made. Confidence: the charged sites were verified; the whole prose surface was not re-read.

### 5.3 The strongest measurement in the project is not in the paper (Evidence stays 3)

This is the central finding of round 16, and it is a scope decision rather than a defect in the text.

The paper's own criterion for this axis, applied consistently since round 9, is: a **pre-registered**
endpoint whose **headroom exceeds its own detectable effect**. As of this round the project holds one.
TE2 step 3 froze its target artifact, priority rule, ladder, endpoint and decision rule in
`TE2_FROZEN_PREREG.json` before any run, then ran 80 cells at `kappa = 5` with the frozen server step and
the target injected through the runner's own `target_artifact` parameter. The pre-registered claim failed
— no arm separated against the 2 % bar of `0.020288`, with `inst_cal` at `+0.000149` (+0.015 %) and
`debt_cal` at `+0.000388` (+0.038 %) — but the reason is decisive and is not the projection: the
**oracle ceiling** on that same cell is only `+0.000228` (+0.0225 %), so the projection arms already
reached the order of the entire class's available room.

The alternate step 4 then measured the ceiling as a function of concentration, two arms, 20 seeds, 80
cells, with the exact single-region target (top-1 share `1.0000`):

| rung | target top-1 share | oracle gap | as % of control | bootstrap 95 % | separated |
|---|---:|---:|---:|---|---|
| `kappa = 1` (frozen runs) | 0.2500 | +0.000013 | +0.0013 % | [-0.00010, +0.00015] | no |
| `kappa = 5` | 0.6322 | +0.000228 | +0.0225 % | [+0.00006, +0.00042] | yes |
| `kappa = 10` | 0.7746 | +0.000462 | +0.0454 % | [+0.00024, +0.00071] | yes |
| **single region** | **1.0000** | **+0.000994** | **+0.0970 %** | [+0.00068, +0.00134] | yes |

The gap is monotone in concentration, about 75x from the uniform target to the extreme, and separated at
`kappa >= 5`. So concentration **does** create statistically detectable room, exactly as the design
hypothesised. But at the physical extreme the whole weight class buys **0.097 %** of the
deployment-weighted error — **20x below the paper's own 2 % bar** — and concentration cannot exceed the
single-region limit, so the ladder has no further rung. The lever is exhausted.

Three consequences for this review:

1. **The paper's central negative is now far better founded than the paper says.** The manuscript's
   limitation paragraph reports a null on the prediction endpoint; TE2 shows *why* the null is structural,
   by bounding the recoverable gain from above at every concentration level, on the only block in the
   project that has feasible-set slack, with the bound separated from zero.
2. **That measurement is not in the manuscript**, so it cannot lift the text's Evidence axis. The axis is
   therefore limited by an authorial scope decision. Reporting the ladder — even in three sentences, with
   the frozen pre-registration cited — would raise Evidence to 4 and is the single largest available
   readiness gain in this review.
3. **It also settles the route the last three rounds were chasing.** The block screen found no dataset in
   the project satisfying both conditions (traffic has the slack but a uniform target; SensorScope and
   U-Air are non-uniform only in the four-block view and their feasible set is locked at 75-80 % of
   windows; T-Drive is natively concentrated but has no run tree and its client mapping raises), and the
   dataset search returned no verified alternative. TE2 then showed that even the route the screen
   recommended — define a concentrated target on the block that has the slack — terminates below the bar.

### 5.4 The release gap is narrowed but still binding (Reproducibility stays 2)

The availability section now names the two run trees behind the Adam replacement and its structural
readout, states that they are internal to this study rather than part of the released bundle, and gives
the confirm seed range `30006-30020` and the constant file. That is the "name it" half of round 15's
charge and it is done. Not done, and all four still charged: the trees are not **in** the bundle;
`w1/PAPER_NUMBERS.csv` does not index any value added since 2026-10-07; the shipped PDF remains the
2026-10-06 artifact; and the `+75 B` change between `7b874f28` and `1d6515ff` on 2026-10-09 is still
unattributed — it does not name a new tree, a seed range or a `round_v1`, and it did not touch any of the
sites this session edited. A reader who takes the bundle cannot reproduce the Adam half of the paper, and
one revision in the chain has no provenance record. This axis is now the second binding constraint.

### 5.5 Standing charges carried forward

- **R16-6 Related work (3).** Neither this review nor the independent review searched the literature, so
  the novelty band is asserted. The round's own dataset search is not a novelty search and cannot stand in
  for one. Recorded as a limitation of the review; if a searched positioning paragraph is added, the axis
  moves to 4.
- **R16-7 Evidence and Significance (3, 3).** The structural contrast is separated but was scored after
  the prediction contrast, so it is exploratory; no deployment decision changes; and the mismatch
  reduction is about 2 % relative. Round 16 adds a measured ceiling to this picture rather than a positive
  result. The honest significance of this work is a **design guideline** — that under two-stage
  non-random selection the aggregation weights cannot move the deployment-level error, and a corrective
  reference buys mismatch, not accuracy — and that is a real contribution to a measurement paper even
  though it will not look like a win.
- **R14-2 target-level shift** is now `partially_resolved`: the manuscript prints the test-split target
  means (`7.657`, `-0.807`, `0.301`) and the two comparators beside them, so the absolute column is
  self-interpreting; the train-side levels that constitute the shift itself are still not printed.

## 6. The three questions the round's experiments were run to answer

1. **Does a deployment target concentrated at the aggregation level give the corrected reference room to
   move an error-type quantity?** No. The whole class buys `0.097 %` of the deployment-weighted error at
   the most extreme concentration that exists, against the paper's own `2 %` bar.
2. **Is the bottleneck the projection or the weight class?** The class. At `kappa = 5` the projection arms
   reached `+0.015 %`/`+0.038 %` against a ceiling of `+0.0225 %`.
3. **Can any of this project's four blocks supply such a target natively?** No, and the failure directions
   are complementary: the one block with slack has a uniform target, the two with mildly non-uniform
   targets have locked feasible sets, and the only natively concentrated one is not runnable. The external
   search produced no verified alternative.

## 7. What would move the stance, and the arithmetic of the ceiling

| repair | axis | weighted gain | readiness |
|---|---|---:|---:|
| (today) | — | — | **3.55** |
| deposit the two trees, index the new numbers, refresh the shipped PDF, attribute or revert the `+75 B` change | Reproducibility 2 -> 3 | +0.10 | 3.65 |
| report the TE2 ceiling ladder and its pre-registration | Evidence 3 -> 4 | +0.25 | 3.90 |
| add one searched positioning paragraph | Related work 3 -> 4 | +0.05 | **3.95** |

All three repairs land at about **3.95**, still a hair below the 4.0 threshold. Crossing it therefore
requires an authorial judgement that this review cannot make for the authors: whether a bounded,
well-measured negative — "the aggregation weights cannot move the deployment-level error, and here is the
ceiling that proves it" — is the contribution this venue should reward. If it is, the remaining gap is
presentation and release discipline, and the paper is close. If it is not, no amount of text repair closes
it, which is why this review has declined across four rounds to raise Significance on wording alone.

## 8. Provenance and audit trail

- Current text `3CC106CA4B6087D9...`, 119922 B; historical `6fc9be0b...`, 117864 B.
- The version chain is byte-verifiable at every step this session touched: `73fa475e` -> `3cc106ca` for the
  four HT edits, proven by exact reverse replacement.
- Evidence artifacts at stated hashes: `TE1_VERDICT.json` `66D10176C0D9C6C7`, `TS1_SUMMARY.json`
  `8A2466BEB9D91DD1`, `TE2_PHASE0.json` `CCB03AE5F8DDA26F`, `TE2_VERDICT.json` `B11D201AA67AD9BC`,
  `TE2_STEP4_VERDICT.json` `2B4F606BB17E33A8`, `TC_TWO_CONSTANTS.json` `319225267112BAC6`, `HT_GATES.md`
  `33FD9503E748DCA2`, `BLOCK_SCREEN.json` `C58C0822C919EA48`.
- Diagnosis ledger now carries items 75-86 recording all of the above, including the round's own five
  defects and deviations.
- Provenance caveat, no dimension charged: the 2026-10-09 revision still has no authorization record, and
  the `+75 B` change within that date is unattributed.

## 9. Verdict

**Readiness 3.55, stance 5/10 borderline negative, lean reject at this revision.** The manuscript's own
text is in the best state this review has seen: the one unsupported comparison is repaired and both
reader-facing contradictions are gone. What holds it below 4.0 is not the prose. It is that the strongest
measurement the project owns — a pre-registered, adequately powered, separated ceiling of `0.097 %` at the
concentration extreme — is not in the paper, and that a reader cannot reproduce its newest half. Both are
fixable without a single new experiment.

## 10. What this review did not do

- No literature search, so Originality and Related work carry medium confidence and are held, not moved.
- No re-derivation of the proofs, no re-implementation of the baselines, no re-run of any experiment.
- No manuscript edit. The one text-level change this review would recommend (reporting the ceiling ladder)
  is an authorial scope decision and is put as a recommendation, not applied.
- The review does not treat the round-16 experiments as manuscript evidence; that is the whole point of
  S5.3.

## 11. Comparison with the independent review

The independent review at `snapshots/2026-10-09-grok-raven-mcs-tmc-review.md` scored the **pre-repair**
text (4/10 lean reject, Significance 2) and its central charge — that the paper's Significance rests on
wording rather than on a usable result — is one this review accepts and has now tested by measurement
rather than by argument. Its two structural asks were: do not promote the post-hoc structural readout, and
make every number locatable. The first is honoured here; the second is half done. The divergence that
remains is comparability: that review used a 7-dimension contract with Significance at 0.15 and no
Terminology term, so its weighted means cannot be placed beside these. Its Soundness reasoning and this
one's now agree, because the defect it found has been repaired.
