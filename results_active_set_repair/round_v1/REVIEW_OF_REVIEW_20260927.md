# Review of the independent review — `raven-mcs-active-set-repair-analysis-20260927.md`

```text
Object under review:  the attached analysis by Claude (2026-09-27), a review of
                      EXPERIMENT_REPORT_FOR_VERIFICATION.md revision 1.
This document:        the executed work's response, written by the agent that ran route A.
Method:               every checkable assertion in the review was re-derived from stored
                      artifacts before being accepted or disputed. Nothing below is accepted
                      on the strength of its wording.
Outcome:              7 of 7 checkable assertions confirmed. 2 of the report's 4 amendment
                      grounds and 1 of its 4 "plan defects" are withdrawn. 3 new findings.
Revision 2 of the report implements all of it; see SS6.
```

---

## 1. The review's checkable assertions — all confirmed

| # | assertion | how it was checked | result |
|--:|:---|:---|:---|
| 1 | `DebtCalAggregator` calls `solve_p2` with `lambda_beta=1e-8`; `raven_simoracle` with `1.0` | `methods.py:447-457` (comment: "keep negligible so Debt-Cal") vs `:619/659` | **confirmed** |
| 2 | the added `instant_calibration` parameter is inert for Debt-Cal | `methods.py:447-457` does not pass it; `p2_cvxpy.py:56` defaults to `True` | **confirmed** |
| 3 | the `v_diag` sanitisation only bites on non-finite/negative input, and nobody had checked whether it fires | instrumented `methods.solve_p2`; `C2_VDIAG_SANITISATION.json`: **171 calls, 0 non-finite, 0 negative**, min `0.011557` | **confirmed, and it never fires** |
| 4 | `train_one` already wraps `runner._process_window` and returns per-window metrics, so G2 needs no `src/` change | `run_nodesign_supplement.py:169`; monkeypatch at `:200/225`; `window_metrics = runner.run()` at `:227`; `_load_cityscanner`/`_load_pilot2` present | **confirmed — the plan named this routine in its SS14 and the report never read it** |
| 5 | the report transposed the manuscript's two percentages | report rev 1: `(−6.17 % and −9.11 %)`; `main.tex:1784`: `(−9.11\% and −6.17\%)` | **confirmed** |
| 6 | `appendix.tex` carries 778 / 85 / 6438 / `2.686e-8` and those sentences are not re-audited after the rebuild | `appendix.tex:1584-1588` prose, `:1607-1610` table | **confirmed** |
| 7 | the new batch has no traceable code version, because `runtime_manifest.json`'s `git_commit` does not reflect the worktree | `runtime_manifest.json` records only hashes; `WORKTREE_DIFF.sha256` now pins **12 modified + 85 untracked** `src/` paths at `git HEAD 2e47464c2c15` | **confirmed** |

The review also states that `verify_report_claims.py` passes 92/92 — reproduced. It is a fair review:
it verified first, then argued, and it separated "the numbers are right" from "the argument is right",
which is the correct split.

## 2. Conceded — corrections to revision 1

| # | revision 1 said | verdict |
|--:|:---|:---|
| 1 | amendment ground 1: "`2.07e-07` is 5x below the `1e-6` used in the plan's E2 path, so the plan is internally inconsistent" | **withdrawn.** These bound different comparisons — E2 checks a recomputation against a stored value, G1a checks whether the code is the same. Citing one as precedent was rhetoric, not a contradiction |
| 2 | amendment ground 3: "SensorScope has no `pi^tar` holes, so the drift is unrelated to the filter" | **narrowed.** True, but it does not bound the drift's *magnitude* on U-Air, which is what the amendment needs. The report implied otherwise |
| 3 | amendment ground 4: "E1's rows are compared within the new batch" | **withdrawn as factually wrong.** RAVEN-NoDesign is the frozen E4 tree; the decisive R1 comparison is cross-batch. This also exposed a missing check, now run |
| 4 | "`p2_cvxpy.py` is the strongest drift lead" | **withdrawn.** The sanitisation never fires (C2) and the parameter is inert (confirmed). The reviewer's `lambda_beta=1e-8` candidate replaces it |
| 5 | plan defect 2: "G2 is not executable as written" | **withdrawn.** The plan named `train_one`; the report looked for a `load_paper_dataset` path, concluded a `src/` change was needed, and never read the named routine. **The most consequential error in revision 1** |
| 6 | "the manuscript sentence is superseded" | **split.** Only the FedAvg half is void; the TwoStage half is a licensed within-Design-family comparison and survives in kind |
| 7 | the percentages quoted from the manuscript | **corrected** to the manuscript's own order |

## 3. Where the review needs refinement

### 3.1 "instant calibration **and debt**" — debt is inert

The review's SS5 attributes RAVEN-NoDesign's `Δ_group` structure to "P2's instant group calibration
**and** debt". The E4 one-factor arms separate them (U-Air, `Δ_group`, 20 seeds):

| arm | `Δ_group` | component removed vs full `raven` |
|:---|:---|:---|
| `raven` | 1.092362 | — |
| `raven_wo_debt` | 1.092409 | debt (**`4.3e-5` — inert**) |
| `raven_wo_obs` | 1.093706 | observation-IPW (`1.1e-3` — inert) |
| `raven_wo_use` | 1.092513 | usable-IPW (`3.2e-3` — inert) |
| `raven_wo_inst` | **1.119606** | instant calibration (**`+2.5 %` — decisive**) |

So the driver is **instant group calibration alone**; debt contributes essentially nothing on U-Air.
The conclusion is directionally right and the composition is wrong. This matters because it is
actionable: "the group-calibration term is the effective machinery" is a cleaner claim than "the P2
package is".

### 3.2 The 2x2 the attribution needs, and why it cannot be run today

The review's inference compares NoDesign (design **off**, full delivery) against
FedAvg/Debt-Cal (design off, full delivery) — that part is licensed-set and sound. But the
`raven_wo_inst` arm it leans on is design **on**, so the design factor and the active set move
together. The controlled cell is `design off x instant calibration off`; it was built at runtime with
no `src/` change and **cannot execute**, because `instant_calibration=False` is a constructor argument
of `RavenWoInstAggregator`, and that class is currently unrunnable (SS4.1). Recorded as
`C3_TWO_BY_TWO.json :: status = BLOCKED` with three unblocking options.

Indirect support stands: on the licensed set, the two no-Design arms carrying P2 calibration
(Debt-Cal 1.017533, NoDesign 1.016515) beat the five without it (1.041296-1.055671). That is
evidence *for* the review's conclusion, but it is not the 2x2.

### 3.3 On the framing of SS5

The review reads SS5 as damage. Half of it is better read as a reframing the manuscript can use: the
result says the effective machinery on U-Air is **P2's group calibration**, while the IPW/Hájek
correction family is numerically inert there. That is the same statement as Tier 2 reached from the
ablation side — and **the manuscript's own E4 family already contains the proof** (SS4.2). It does not
change what R4 must replace; it changes what the paper can claim.

## 4. Findings this exchange produced that were in neither document

### 4.1 A half-applied uncommitted diff makes a published arm unrunnable

The uncommitted `feasibility.py` diff adds `instant_calibration: bool = True` to
`validate_p2_lambdas` and makes the `lambda_group` check conditional on it, with a docstring naming
**"the raven_wo_inst ablation path"** as the reason. The caller at
`src/raven_mcs/sag/counterfactual_audit.py:106` does not pass it, so the default `True` applies.
`RavenWoInstAggregator.__init__` hardcodes `lambda_group=0.0`. With
`window_runner.py:1016/1252` running `_run_counterfactual()` whenever `lowmem` is false:

```text
ValueError: lambda_group must be >= max_server_learning_rate (got 0.0 < 1.0)
```

Verified by direct execution, not inference: `run_arm("C0_frozen", "uair", "raven_wo_inst", 30001)`
raises. **The published E4 arm `raven_wo_inst` cannot be regenerated under the current tree.** Blast
radius is class-specific: `twostage_hajek`, whose stored numbers are bit-identical to `raven_wo_inst`,
uses `TwoStageHajekAggregator` and re-runs fine (G1c, 6/6 bit-exact). This strengthens the review's
SS6(c): the worktree is not merely untraceable, it is partly broken.

### 4.2 The E4 ablation family contains bitwise-duplicate arms

| arm A | arm B | relationship |
|:---|:---|:---|
| `raven_wo_inst` (E4) | `twostage_hajek` (E3) | **bit-identical per seed**, three metrics, `max abs diff = 0.0` |
| `inst_cal` (E3) | `raven_wo_debt` (E4) | **bit-identical per seed** |

Across two different batches, 20 seeds, three metrics. On U-Air, **TwoStage-Hájek is RAVEN without
instant calibration**, and **Inst-Cal is RAVEN without debt**. This sharpens the review's SS6(b): the
`−9.11 %` claim is not merely a within-Design-family comparison, it is a comparison against an
ablation arm of the same method. It also means the appendix's "sealed same-backbone family" presents
duplicates as independent baselines.

### 4.3 G2 executed — the hybrid blocks are cleared (the review's own route)

Run through `run_nodesign_supplement.train_one`, one seed per block, three methods each:

| block | methods | result |
|:---|:---|:---|
| `cityscanner_nyc_pm25` 32001 | fedavg / fedau / obsuse | **BIT-IDENTICAL** to the frozen ledger |
| `cityscanner_nyc_p2_measured_o` 33001 | fedavg / fedau / obsuse | **BIT-IDENTICAL** to the frozen ledger |

The review's decision rule is correct and is the right one: the current `fedavg_window` is `ζ≡1`
(full delivery), so if it reproduces a frozen ledger bit-exactly on a block where ~70 % of `π^opp`
pairs have `π^tar = 0`, the frozen run cannot have dropped those pairs. **City Scanner and Pilot 2
used the licensed set; route A's damage is confined to U-Air.** The frozen ledgers do carry
`design_on: true` on the `fedau_window` rows, which is why the plan flagged these blocks — the
bit-identical reproduction shows that flag did not affect the active set.

### 4.4 The `raven_wo_design` bit-reproduction the review asked for

Requested in its SS2 as the first of two supplementary checks. Run: the current code reproduces
**frozen U-Air `raven_wo_design` bit-exactly** at seeds 30001 and 30002, `abs_diff = 0.0` on
`RMSE_mu`, `Delta_group`, `Delta_c_s` (`C1_RAVEN_WO_DESIGN_REPRO.json`). Together with
`raven_simoracle` (`GATE_uair.json`, 0.0), **every checked U-Air arm except `debt_cal` reproduces
bit-exactly**, so R1's cross-batch comparator is sound.

## 5. Verdict

**The review is correct, and it is the most useful artifact in this exchange.** Seven of seven
checkable assertions confirmed; three of my claims withdrawn; one of them (G2) a genuine
misjudgement that had already been reported to the user as a plan defect.

Two things it does not do, both of which the executed work supplied: it does not separate instant
calibration from debt inside its own SS5 attribution (SS3.1), and it does not name the 2x2 arm its
conclusion requires (SS3.2). One assertion is unverifiable from artifacts — that
`scripts/run_path_a_no2.py` is "a PATH_A NO2 driver this session does not integrate" — and it is
immaterial, because the plan named `train_one`, not that driver.

## 6. Actions taken in revision 2 of the report

1. SS0 amendment grounds rewritten: 3 grounds, 2 superseded ones retained for audit.
2. SS0.1 `p2_cvxpy` lead withdrawn on C2 evidence; `lambda_beta=1e-8` installed as the leading
   candidate with the supporting bit-exactness census.
3. SS0.2 new: the half-applied diff.
4. SS4.3 new: the blocked 2x2 and its three unblocking options.
5. SS4.4 new: the E4 duplicate arms.
6. SS4.5 new: G2 executed, hybrids cleared.
7. SS6.3 corrected: the transposed quotation, and the TwoStage half split out as surviving.
8. SS6.4 new: the `appendix.tex` 778/85/6438 dependency.
9. SS8 defect 2 retracted; defect 4 confirmed as the plan author's, with its provenance in an earlier
   record of mine stated plainly.
10. SS9 falsification targets rebuilt.
11. `WORKTREE_DIFF.sha256` added (SS6(c) of the review): sha256 of every uncommitted `src/` diff plus
    `git HEAD 2e47464c2c15`, 97 entries.
12. `verify_report_claims.py` extended to 137 checks (139 with `--deep`), all passing, covering C1,
    C2, C3, G2 and both SS4.4 identities.

**Not done, and needing authorization:** completing the half-applied diff (a `src/` change, outside
route A's SS14 boundary), replacing any manuscript cell, and committing anything.
