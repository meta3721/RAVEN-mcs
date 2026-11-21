# RAVEN-MCS — IEEE TMC Independent Re-Review, Round 6 (version-comparison)

```text
Review date: 2026-10-03
Target venue/year/track: IEEE Transactions on Mobile Computing, journal revision; method + measurement long paper
Paper title: RAVEN-MCS: Target-Mass-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex (2230 lines, 17 pp, 0 errors / 0 undefined / 0 overfull)
  TO_OVERLEAF_paper_tmc_r1_clean/main.aux (20460 bytes, mtime 10:04:26 > main.tex 10:04:21; 96 \newlabel, 0 "??")
  TO_OVERLEAF_paper_tmc_r1_clean/main.log (17 pages, 886581 bytes; 0 Overfull, 21 Underfull hbox/vbox)
  snapshots/2026-10-03-pre-register-fix/main.tex (2235 lines) — the exact state reviewed in round 5
  snapshots/2026-10-03-pre-v4-contribution/main.tex (2294 lines) — structural-count reference
  results_w1_ladder/round_v3/{EXECUTION_REPORT,MYOPIC_DIAG.json,ERRATA_v2}.md
  results_w1_ladder/round_v4/{PART_A_REPORT,PART_B_REPORT}.md
  ccfa-review-reports/raven-mcs-tmc-review-round5.md (immediate predecessor; frozen dimensions + R5-x ledger)
  ccfa-review-reports/raven-mcs-tmc-review.md (round-4 report; frozen contract + historical baseline)
Search basis: no new external search this round (see §4)
Report file: ccfa-review-reports/raven-mcs-tmc-review-round6.md
Reviewer mode: version-comparison, centrepiece = verification of the register/tone fix (E1–E9 + Table I caption)
Manuscript version / comparison range: round-5 manuscript (snapshot 2026-10-03-pre-register-fix, 2235 lines) -> current 17-pp revision (2230 lines)
Frozen comparison contract ID: TMC-J-R4 (inherited verbatim from the round-4 report §1 via round 5; see §1)
```

**Naming-convention note (skill rule 8).** `ccf-paper-reviewer` rule 8 asks for one canonical `ccfa-review-reports/` report rather than a dated copy per iteration. The requesting agent explicitly asked for a separate round-6 file, with the round-4 and round-5 files preserved as historical artifacts. This file is therefore the round-6 canonical report; `raven-mcs-tmc-review.md` and `raven-mcs-tmc-review-round5.md` are deliberately left untouched.

---

## 1. Frozen Comparison Contract (inherited; not modified)

| Item | Value |
|---|---|
| Target venue / type | IEEE TMC journal revision; method + measurement long paper |
| Dimensions and weights | 8 dimensions: `0.10 / 0.20 / 0.25 / 0.15 / 0.10 / 0.10 / 0.05 / 0.05` |
| Anchors | 1 = unacceptable, 5 = strong |
| Overall mapping | weighted sum -> calibrated 1-10 stance |
| Decision threshold | 4/10 = weak reject |
| Comparison threshold | absolute weighted delta < 0.05 = `unchanged`, otherwise `improved` / `regressed` |
| Evidence standard | manuscript + repository artifacts only |
| Reviewer roles | method/soundness, evidence/experiment, novelty/positioning, writing/clarity, reproducibility, AC |

**Rubric deviation, stated explicitly (inherited from round 5).** The project-frozen 8-dimension rubric uses *Originality/novelty, Soundness/technical quality, Evidence/experiments, Clarity/presentation, Reproducibility, Significance/impact, Related work/positioning, Terminology/notation*, which is **not** the skill's default 8-dimension set (which ends in *Ethics/limitations*). Per instruction this round keeps the round-4/round-5 names and weights unchanged.

**Materials asymmetry disclosed.** Round-5 scores are inherited verbatim from `raven-mcs-tmc-review-round5.md` §11/§13 and were not recomputed. Only the current version was rescored. The round-5 report was written against a 2235-line file; the line numbers quoted in its ledger therefore index that snapshot. All line numbers in this report index the **current 2230-line file**, and where a round-5 line number is cited for comparison it is labelled as such.

---

## 2. Verification Of The Claimed Fix (E1–E9 + Table I caption)

The diff between `snapshots/2026-10-03-pre-register-fix/main.tex` and the current file is `102 insertions / 107 deletions` over 209 changed lines. Nine claimed edits (E1–E9) plus one Table I caption deduplication are present. **Six further text changes are present in the diff that were not declared in the E1–E9 list**; each was inspected for a new defect and none was found (see §7, column "undeclared edit").

| ID | Claimed fix | Verified at | Verdict |
|---|---|---|---|
| `E1` | registered-interval wording, no null-equivalence claim | L246-247 | **Present.** "statistically equivalent to zero inside a pre-registered ±0.10 band of the closable gap" -> "their paired intervals lie inside a pre-registered $\pm0.10$ equivalence band in the same units". Full-text search for `statistically equivalent` in `main.tex`: **0 hits**. |
| `E2` | band denominator now "same-support hindsight optimum" | L607-608 | **Present.** "...between uniform weighting and the same-support hindsight optimum, at the same active set, the same $M_r$, the same $\mathcal{C}_r$..." The mislabelling is gone. The **value** of the denominator is still not printed (see `R5-3`). |
| `E3` | projection-with-debt rule at κ=1000 labelled as a new rule and exploratory; frozen-strength +0.0073 pp stated separately | L2082-2086 | **Present.** "The projection-with-debt rule, a new rule of this study that sets the debt weight to $\kappa=1000$ rather than the frozen value, adds $+1.347$ pp and $+0.580$ pp (Holm $\approx10^{-5}$ on both) on a rule reported as exploratory; at the frozen debt strength the same contrast is $+0.0073$ pp ($[0.0064,0.0083]$) on SensorScope, inside the band." |
| `E4` | projection tolerance 1e-10; replay residuals reported as a residual, not an identity; exploratory status next to the numbers | L2216-2225 | **Present.** "The projection is solved at tolerance $10^{-10}$; ... miss the replay tolerance of $10^{-9}$ ... by $2\times10^{-6}$ to $3.7\times10^{-5}$ ..., so their closed-loop agreement is reported as a residual rather than an identity" and "The projection-with-debt results use a debt weight chosen on the tuning seeds and are reported as exploratory." |
| `E5` | flatness mechanism: over 3279 windows the range of ‖M_r α − μ‖₁ over C_r has median 1e-13, minimizer non-unique | L961-964 | **Present, with two residual problems.** "Over the $3279$ active windows the range of $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ over $\mathcal{C}_r$ has median $10^{-13}$, so the per-window minimizer is not unique and the group term selects among equivalent solutions." Numbers verified against `MYOPIC_DIAG.json` (`n_windows: 3279`, `range_median: -1.1302070390684094e-13`). Residual: **F1** (uniqueness tension + unestablished "selects") and **R5-5** (mechanism still not stated at the point of consequence). |
| `E6` | broken duplicated sentence restored | L1547-1551 | **Present.** "...and the compounding direction is therefore part of the construction rather than a measured property of these traces, and the structural-alignment results of Table~\ref{tab:main_effectiveness} are conditional on it." The round-5 duplicated fragment ("...conditional on it. / the construction rather than a measured property of these traces, and the...") is gone. New issue **F4**: the restored sentence is ungrammatical. |
| `E7` | unsupported "their oracle values" deleted | L1839-1841 | **Present.** The clause now reads "...the observation and usable-update factors, and the debt recursion ($+0.0073$ pp, ...)". The unsupported attribution is gone. |
| `E8` | (27) re-scoped to "one-sided residual bound, not a benefit term" | L1843-1845 | **Present.** "...rather than a structural contributor; \eqref{eq:debt_bound} carries debt as a one-sided residual bound, not as a benefit term." The "which is the role (27) assigns to it" clause — the round-5 conflation — is deleted. |
| `E9` | "does not amplify in α, per (eq:g4_alpha)" | L229-231 | **Present.** "...the calibration program does not amplify in $\boldsymbol\alpha$, per \eqref{eq:g4_alpha}." |
| Table I caption | deduplication of the interleaved rank strings | L1499-1504 | **Present and correct.** Old: "NSW four-region (the NSW-Traffic four-region ranking table in the supplemental material), City Scanner {PM}$_{2.5}$ the City Scanner visit-occupancy ranking table in the supplemental material, and City Scanner Pilot~2 measured $O$ the City Scanner Pilot~2 measured-$O$ ranking table in the supplemental material are not mixed into..." New: "The three supplemental rankings (NSW four-region, City Scanner {PM}$_{2.5}$ visit-occupancy, and City Scanner Pilot~2 measured $O$) are not mixed into Table~\ref{tab:main_effectiveness}." This was a real defect. |

**Undeclared edits found in the diff (all inspected; no new defect):** (i) L284 `are orthogonal; they do not formulate` -> `are orthogonal and do not formulate`; (ii) L316-323 FedIPW/FLOSS/FedPALS sentence split into three sentences; (iii) L1486 removal of "FedAU-Window and ObsUse-Window remain strongest on that hybrid ranking."; (iv) L1713-1714 addition of a cross-reference to `Section~\ref{subsec:eval_rq2}`; (v) L2001 removal of "The non-Design components are magnified in the U-Air ablation figure of the supplemental material."; (vi) L2177-2192 conclusion compression. Items (iii) and (v) remove content; neither removes a claim that any other sentence still depends on, and the conclusion compression preserves all four scoping statements (protocol-constructed $O$/$U$, no isolated usable-update effect, debt as internal accounting, no joint ranking).

---

## 3. Structural Integrity Re-Check (no new defect introduced)

| Check | Pre-v4 snapshot | Round-5 snapshot | **Current** | Verdict |
|---|---|---|---|---|
| `\label` | 96 | 96 | **96** | identical |
| `\begin{table` | 4 | 4 | **4** | identical |
| `\begin{figure` | 4 | 4 | **4** | identical |
| `\begin{equation` | 37 | 37 | **37** | identical |
| `\cite{` | 42 | 42 | **42** | identical |
| `\section{` | 8 | 8 | **8** | identical |
| `\subsection{` | 29 | 29 | **29** | identical |
| `\begin{proposition` | 4 | 4 | **4** | identical |
| `\begin{theorem` | 2 | 2 | **2** | identical |
| em dashes (U+2014) | 0 | 0 | **0** | ≤ 3 required |
| pages | 17 pp | 17 pp | **17 pp** (`Output written on main.pdf (17 pages, 886581 bytes)`) | identical |
| errors / undefined / overfull | 0 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** (0 `Overfull`, 0 `??`, `main.aux` 96 `\newlabel` matching the 96 `\label`) | identical |
| line count | 2294 | 2235 | **2230** | −5 vs round 5 |

No numbering drift: equation count is unchanged at 37, propositions at 4, theorems at 2, and `main.aux` was rebuilt after `main.tex` (10:04:26 vs 10:04:21) with zero unresolved references. The 21 `Underfull` boxes are pre-existing typesetting warnings, not `Overfull`, and do not affect the 0-overfull claim.

---

## 4. Search And Related-Work Basis

```text
Queries used: none this round
Sources searched: repository artifacts only (manuscript, snapshot diff, main.aux/log, round_v3 and round_v4 evidence files, rounds 4-5 review reports)
Closest works found: not re-searched; round 4 carried FedIPW (morishita2026who), FedPALS (listozec2024overcoming), FLOSS (goetze2025floss), FedAU (wang2024lightweight) as the nearest neighbours, cited at main.tex L316-326
Unverified related-work risks: W4 (novelty boundary vs FedIPW/FedPALS) remains unresolved and was NOT re-verified in this round
Source-quality screening status: not performed; no new citation was checked against its source
```

Honest statement: this round spent its budget on verifying the nine claimed fixes and re-scoring, not on positioning. Any novelty statement below is a carry-over, not a fresh judgement.

---

## 5. Expected Review Outcome

```text
Expected outcome: weak reject, upper edge (5/10); stance held, weighted readiness sum 2.90 -> 2.90
Main accept signal: the round-5 register/tone defects were fixed precisely and without collateral damage - the null-equivalence claim is gone, the oracle clause is deleted, (27) is rescoped, "does not amplify" is qualified, and the debt contrast is now split into two named magnitudes; structure counts, page count and compile cleanliness are all unchanged
Main reject signal: the central unresolved decision-relevant weakness is untouched - no prediction endpoint survives Holm anywhere, and the paper's own new evidence shows the full calibration program is unnecessary for the structural gain it is credited with - and the fix stopped one step short on three items, leaving the band without a decision rule, the ruler without a value, and the debt claim unscoped
Confidence: 4/5 (full main text + exact snapshot diff + targeted evidence files; supplemental not re-read; the L1-vs-L2 flatness question of F1 not resolvable from the files read)
```

---

## 6. Relative-Progress Scorecard (round 5 -> current)

Historical scores are the round-5 scores, inherited verbatim from `raven-mcs-tmc-review-round5.md` §11/§13.

| # | Dimension | Historical | Current | Delta | Weight | Weighted delta | Explanation (issue IDs) |
|---|---|---|---|---|---|---|---|
| 1 | Originality / novelty | 2 | 2 | 0 | 0.10 | 0.00 | `W4` unresolved; the revision adds no novelty axis (text-tightening only) |
| 2 | Soundness / technical quality | 4 | 4 | 0 | 0.20 | 0.00 | `R5-9` closed (oracle clause deleted, L1839-1841); `R5-6` closed ((27) rescoped, L1843-1845); `R5-7` closed ("does not amplify in $\boldsymbol\alpha$", L229-231); `R5-4` closed (κ=1000 exploratory at L2082-2086 and L2224-2225). **But** `R5-1` is only partially closed (the claim "debt is ... rather than a structural contributor" at L1842-1843 and L232-235 is still unscoped while L2074-2086 shows the debt-weighted rule lowest on the group endpoint), `R5-2` only partially closed (no decision rule at L606-610), and **F1** is a new text-level tension introduced at L961-964 |
| 3 | Evidence / experiments | 3 | 3 | 0 | 0.25 | 0.00 | No new experimental evidence of any kind this round; no endpoint contrast was added or re-tested. `R5-5` improved in precision (now a number, L961-964) but its mechanism ask is only half met |
| 4 | Clarity / presentation | 3 | 3 | 0 | 0.15 | 0.00 | `R5-12` closed (fragment restored, L1547-1551, verified against the snapshot); `R5-11` partially closed (body now carries `1.237%` at L1576 but the abstract's `1.24%` at L86 still has no ruler, and no body text prints `6.55%`). **But** `R5-3` partially closed (label fixed, value still absent), `R5-15` still open (no decision rule at L606-610), `R5-8` still open (`Proj_{C_r}` never defined), `N1` carried over, and **F1/F4** are new clarity defects |
| 5 | Reproducibility | 2 | 2 | 0 | 0.10 | 0.00 | `M7` unresolved (bundle inventory L2203-2213 still does not list the round-v3/v4 ladder, band-decision or trained-rule artifacts); `R5-17` partially closed (residuals now framed as a residual at L2217-2220, but the `M_r`-drift caveat is still not cross-referenced into the ruler clause L606-608 or into Proposition 3) |
| 6 | Significance / impact | 2 | 2 | 0 | 0.10 | 0.00 | Unchanged reachable-effect axis: the structural headroom is unchanged, no prediction endpoint is significant, and the paper's own evidence still shows the full (P2) is unnecessary for the structural gain. `R5-1`'s partial closure does not change this |
| 7 | Related work / positioning | 3 | 3 | 0 | 0.05 | 0.00 | `W4` unresolved; the FedIPW/FLOSS/FedPALS sentence split at L316-326 is editorial and not new positioning evidence |
| 8 | Terminology / notation | 3 | 3 | 0 | 0.05 | 0.00 | `R5-1` partially closed (L2082-2086 now distinguishes the two contrasts) but the term collision persists: L1839-1841 calls the frozen $+0.0073$ pp quantity "the debt recursion" while L2081-2083 calls the κ=1000 quantity a "rule", and the κ=1000 quantity is still a *recursion* used as a *rule*. `R5-3` label fixed, value absent. `R5-14` partially closed. **F2** is a new collision on "interchangeable" |

**Weighted progress delta = 0.00 ⇒ `unchanged`** under the frozen rule (|weighted Δ| < 0.05).

**Traceable score increases this round: none.** The six closed issues (`R5-4`, `R5-6`, `R5-7`, `R5-9`, `R5-12`, and the Table I caption defect) were all scored as *contributors to a deduction already taken*, not as standalone point deductions, in the round-5 scorecard. Closing them removes part of an existing deduction without reversing it, because the round-5 deduction for each affected dimension was carried by at least one issue that remains open:

| Dimension | Round-5 deduction was carried by | Status after round 6 |
|---|---|---|
| Soundness | `R5-1`, `R5-2`, `R5-4`, `R5-6`, `R5-7` | `R5-1` partial, `R5-2` partial ⇒ deduction stands |
| Clarity | `R5-3`, `R5-11`, `R5-12`, `R5-15`, `N1` | `R5-12` closed, but `R5-3` partial, `R5-15` open, `R5-11` partial, `N1` open ⇒ deduction stands |
| Terminology | `R5-1`, `R5-16`, `R5-3` | `R5-1` partial and `R5-16`/`R5-3` open ⇒ deduction stands |

Per the frozen continuity rule ("if an inherited issue is resolved and the revision introduces no corresponding defect or contradictory evidence, the affected dimension must not decrease"), no dimension decreased. The symmetric rule does not force an increase when sibling issues under the same deduction remain open.

**Traceable score decreases this round: none.**

**Issues excluded from the delta as applying to both versions** (consistent-application rule, as round 5 did for the abstract's `6.55 %` vs `6.885 %`):

| Issue | Why excluded |
|---|---|
| `R5-13` (`6.55 %` at L87 vs `6.885 %` at L1578) | pre-existing and present in the pre-v4 snapshot; not a penalty on the revised version alone |
| `R5-10` ((43) coefficients unlabelled, L2035-2037) | pre-existing at the round-5 snapshot; untouched by this revision |
| `R5-16` ("recoverable" at L1823/L1920/L2184 vs `H` at L2100-2104) | pre-existing; untouched |
| `N1` (key-level vs region-level `ρ_r`) | carried unchanged from round 4 |
| `W4`, `W6`, `M7`, `N2` | inherited, untouched by this revision |

**Inherited issue reconciliation:** `W2`, `W5`, `W7`, `N3` stay `resolved`. `W3` stays `resolved` for its core ask. `M8` stays `resolved`. `W1` stays `unresolved`. `W4`, `W6`, `M7`, `N1`, `N2` unchanged.

---

## 7. Closure Table — R5-1 … R5-17, C1, C2

Status vocabulary: `closed` / `partially closed` / `open`. Every line number indexes the current 2230-line `main.tex`.

| ID | Status | Deciding line | Deciding quote | Note |
|---|---|---|---|---|
| `R5-1` debt magnitudes / non-contributor claim | **partially closed** | L2082-2086 (fixed) vs L1842-1843 and L232-235 (not fixed) | L2082-2086: "The projection-with-debt rule, a new rule of this study that sets the debt weight to $\kappa=1000$ rather than the frozen value, adds $+1.347$ pp and $+0.580$ pp (Holm $\approx10^{-5}$ on both) on a rule reported as exploratory; at the frozen debt strength the same contrast is $+0.0073$ pp ($[0.0064,0.0083]$) on SensorScope, inside the band." **Still unscoped**, L1842-1843: "stay inside that band, so debt is an auditable accounting recursion for residual under-service rather than a structural contributor"; L232-235: "instantaneous calibration and debt are neither prediction drivers nor structural contributors." | The two-contrast renaming is done well and the frozen-strength number is now stated in the same paragraph. But the *claim* the issue was about is unchanged: the paper still asserts debt is "not a structural contributor" in the contributions and in §VII-C, while L2074-2077 prints the projection-with-debt rule as **lowest** on the group endpoint on both datasets. The frozen `λ_g`=1, `η`=0.01 scope is still not named. |
| `R5-2` "statistically equivalent to zero" with no test | **partially closed** | L246-247 (fixed); L606-610 (not fixed) | L246-247: "their paired intervals lie inside a pre-registered $\pm0.10$ equivalence band in the same units." L608-610: "...and with all windows known in advance; the pre-registered equivalence band is $\pm0.10$ in those units." | The over-claim is gone (0 hits for `statistically equivalent`). The required second half — "state the band's decision rule and its status as a practical-equivalence band rather than a test" — is **not done**: the definition has no `\label`, no statement of whether the band is read on the point estimate or the interval, and no disclaimer. The sibling `+0.5 %` tolerance at L1632-1633 still carries exactly the disclaimer this band lacks. Calling it an "equivalence band" keeps the statistical register without the procedure. |
| `R5-3` band denominator mislabelled and unvalued | **partially closed** | L607-608 (label fixed); value absent (grep for `3.44` / `1.32` in `main.tex`: no semantic hit) | L607-608: "in units of the closable gap between uniform weighting and the same-support hindsight optimum, at the same active set, the same $M_r$, the same $\mathcal{C}_r$, and with all windows known in advance". | The mislabelling is fixed — the denominator now names the object that the printed `−0.268` (L1837) implies. The **value is still never printed**, so a reader still cannot convert `+0.0073 pp` or `−0.268` into a common unit or check the band verdict. `PHASE3_REPORT.md:77` gives `(Δ_unif − Δ*)/2 = 3.44 pp` for SensorScope; the U-Air counterpart is likewise absent. |
| `R5-4` failed pre-registered gates undisclosed at the point of use | **closed** | L2082-2086; L2216-2225 | L2084: "on a rule reported as exploratory"; L2224-2225: "The projection-with-debt results use a debt weight chosen on the tuning seeds and are reported as exploratory." Plus L2217-2220: "...miss the replay tolerance of $10^{-9}$ used for the frozen arms, by $2\times10^{-6}$ to $3.7\times10^{-5}$ ..., so their closed-loop agreement is reported as a residual rather than an identity". | Verified against `PART_A_REPORT.md:59,77` ("按协议字面 A2 的门未通过 ... 故 A2 的 κ 数值只作探索性读数") and `PART_B_REPORT.md:17,18,21` (`proj_beta` 0/40 at 2.0e-6/3.0e-6; `proj_beta_debt` max 2.9e-5/3.7e-5). The κ=1000 arm is now labelled a new exploratory rule at both the point of use and in the availability section. **Minor residual:** the B-G2 gate's *partial* status (`uniform_window` 20/20 at 0.0) is not stated, and the A2 gate's reason (a `3.34e-08` α L∞ mismatch between two projection code paths vs a `1e-8` threshold) is still absent — but the exploratory flag neutralises the over-read the issue was about. |
| `R5-5` exact flatness / inertness of the (P2) group term absent | **partially closed** | L961-964 (fact added); L2133-2134 and L1823-1825 (consequence places, no mechanism) | L961-964: "Over the $3279$ active windows the range of $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ over $\mathcal{C}_r$ has median $10^{-13}$, so the per-window minimizer is not unique and the group term selects among equivalent solutions." | Verified against `MYOPIC_DIAG.json` (`n_windows: 3279`, `range_median: -1.1302070390684094e-13`) and `EXECUTION_REPORT.md:132-133`. This is a real precision gain and it now sits next to the `(λ_g/2)‖M_rα − μ‖₂²` term. **Two asks remain:** (a) the *mechanism* (`ERRATA_v2.md:35`: each window covers only a few of the 220 groups, so the covered target coordinates are empty) is still absent, so the reader is told the surface is flat but not why; (b) the conclusion the issue asked for — that the surviving lever is the `β̂` anchor — is not stated, and neither is the tie-break result (`d_myo_tb` = 1.05140 beating uniform 1.06213 in `EXECUTION_REPORT.md:134`) that would substantiate it. |
| `R5-6` (27) cited as assigning a non-contributor role | **closed** | L1843-1845 | "rather than a structural contributor; \eqref{eq:debt_bound} carries debt as a one-sided residual bound, not as a benefit term." | The conflating clause "which is the role \eqref{eq:debt_bound} assigns to it" is deleted. The ground of the citation is now correct: a one-sided inequality is described as a one-sided bound. |
| `R5-7` "does not amplify" beyond its metric | **closed** | L229-231 | "the implemented RAVEN-Design clipped plug-in is a Lipschitz perturbation of the same-window ideal reference that the calibration program does not amplify in $\boldsymbol\alpha$, per \eqref{eq:g4_alpha}." | Now qualified to the `α`-metric with an explicit equation cross-reference. The composition metric is independently handled at L2134-2136, which cites `\eqref{eq:g4_comp}` for the aggregate difference. |
| `R5-8` `Proj_{C_r}(β̂)` never defined; new-rule status late | **open** | L245 (first use), L1832, L2088 | L245: "the part carried by the projected reference $\mathrm{Proj}_{\mathcal{C}_r}(\widehat{\boldsymbol\beta}_r)$ and". Full-text grep for `Proj_`: 11 hits, none a definition. | Unchanged this round. `\mathrm{Proj}_{\mathcal{C}_r}(\cdot)` still appears first inside the contributions with no definition; the nearest thing to a definition is the feasible-set equation `\eqref{eq:Cr}` far later. The status sentence at L2088-2089 ("These projection rules are new rules of this study, not the frozen RAVEN configuration") is 1,840 lines after first use, exactly the delay the issue named. |
| `R5-9` "their oracle values" claimed band-inside, unsupported | **closed** | L1839-1841 | "The group-matching, variance, and staleness terms, the observation and usable-update factors, and the debt recursion ($+0.0073$ pp, ...) stay inside that band". | The clause is deleted rather than supported, which is the honest resolution. Verified that no oracle contrast exists in the v4 package (`PART_A_REPORT.md:26-30` uses `raven_wo_obs`/`raven_wo_use` as p and q) and that the only oracle-adjacent row (`EXECUTION_REPORT.md:119`, `B1(simoracle)−B1(raven)` = `+0.0639` `[−0.0020,+0.1214]`) has its own verdict cell reading "带外但跨 0". Round-5 question 2 is thereby answered by deletion. |
| `R5-10` (43) coefficients printed unlabelled | **open** | L2035-2037 | "the two settings are indifferent when $w_c\,4.990=w_g\,6.943+w_\mu\,6.885+w_t\,7.221$, so a deployment that reads structure only keeps Design on if and only if $w_c/w_g>1.39$" | Untouched. The four coefficients are the U-Air ablation percentages (`$4.990$` is U-Air `Δ_c-s`, per Table~\ref{tab:e4_ablation}) but the sentence still does not say so. Excluded from the progress delta as pre-existing. |
| `R5-11` abstract `1.24 %` vs contributions `+0.922 pp` | **partially closed** | L86-87 (abstract); L1576-1577 (body) | L86-87: "Design is worth $1.24\%$ of group mismatch on SensorScope at unchanged prediction, and on U-Air it costs $6.55\%$ of RMSE while improving cross-sensor mismatch by $4.99\%$." L1576-1577: "Design is worth $1.237\%$ of $\Delta_{\mathrm{group}}$ ... on SensorScope at unchanged prediction". | The body now carries the `1.237 %` figure with its object named, so the abstract sentence is numerically traceable. Two gaps remain: the abstract's sentence still has no ruler and no baseline (the reporting rule at L243-244 requires structural numbers to be quoted relative to uniform weights and decomposed), and the abstract's `6.55 %` U-Air RMSE cost is still not printed anywhere in the body — L1578 states `6.885 %`, which is the SensorScope cost. |
| `R5-12` dangling duplicated clause in §VI-A | **closed** | L1547-1551 | "The reported predictive gains describe this construction rather than the range attainable when selection varies at the unit level, and the compounding direction is therefore part of the construction rather than a measured property of these traces, and the structural-alignment results of Table~\ref{tab:main_effectiveness} are conditional on it." | Verified against the snapshot: the duplicated "conditional on it. / the construction rather than a measured property of these traces, and the" block is gone. New issue **F4**: the restored sentence now contains a doubled "rather than" and a doubled "and". |
| `R5-13` `6.55 %` vs `6.885 %` | **open** (excluded from delta) | L87 vs L1578 | L87: "on U-Air it costs $6.55\%$ of RMSE"; L1578: "costs $6.885\%$ of $\mathrm{RMSE}_{\mu}$, $6.943\%$ of $\Delta_{\mathrm{group}}$" | Unchanged. Pre-existing in the pre-v4 snapshot, so it applies to both versions and carries no progress delta. Note the two figures are in fact different contrasts/objects (U-Air cost vs SensorScope cost), but the paper never prints the U-Air RMSE cost in the body, so the abstract figure has no in-text companion. |
| `R5-14` band verdicts quoted in mixed units | **partially closed** | L1837 vs L1840-1842 | L1837: "outside the equivalence band in the same units ($-0.268$, $[-0.320,-0.214]$)" (G-units); L1840-1842: "the debt recursion ($+0.0073$ pp, $[0.0064,0.0083]$ ...) stay inside that band" (pp) | The G-unit value is now printed for the design-factor row, which is exactly the "print G-units and pp together" ask — but only for that one row. The debt row still gives pp only and then says "inside that band", whose unit is the closable gap, so the reader still cannot verify the verdict for that row. |
| `R5-15` band placement, no label, no disclaimer | **open** | L606-610 vs L1632-1633 | L606-610: "Structural contrasts are reported relative to uniform server weights ... in units of the closable gap between uniform weighting and the same-support hindsight optimum, ...; the pre-registered equivalence band is $\pm0.10$ in those units." L1632-1633: "The tolerance is descriptive rather than a formal non-inferiority test". | The band is still defined inside §III-F "Structural Alignment Objective" (a modelling subsection), still carries no `\label` and no cross-reference to the preregistration, and still lacks the "descriptive rather than a test" disclaimer that its weaker `+0.5 %` sibling carries. All three asks open. |
| `R5-16` "recoverable" names two headroom objects | **open** (excluded from delta) | L1823, L1920, L2184 vs L2100-2104 | L1920: "is already recoverable by uniform server weights"; L2100: "The recoverable gain is bounded inside the class the method defines" | Untouched. Pre-existing; excluded from the progress delta. |
| `R5-17` `M_r`-drift caveat only in the availability section | **partially closed** | L2216-2223 (improved); L606-608 and Prop. 3 (still silent) | L2217-2220: "...so their closed-loop agreement is reported as a residual rather than an identity; the reconstructed reference is bit-identical and the uniform-weight rule reproduces exactly; the residual tracks composition and mass inputs of the run itself, which vary weakly with the model trajectory". | The framing improved materially — a `2e-6…3.7e-5` mismatch is now explicitly a residual, not an identity, and the cause is named. The cross-reference the issue asked for (into the ruler clause at L606-608 and into Proposition 3's A5 premise) is still absent, so a reader of §III-F or §VI still meets the "same $M_r$" premise with no pointer to the disclosure. |
| `C1` Proposition 4's unused directional-derivative clause | **open** | L1349-1351 | "along a feasible direction $d$ of the simplex, $\sum_g d_g=0$, the directional derivative is $\sum_g d_g\,\mathrm{RMSE}_g^2/(2\,\mathrm{RMSE}_{\mu})$" | Still present, still referenced nowhere. Zero space recovered. |
| `C2` Coverage-Gate apparatus supports an instrument that never acts | **open** | L483-499, L986-1007, L1367-1413 (unchanged) | Not touched by this revision. | Zero space recovered. The `C1`/`C2` savings were the round-5 budget for the P0 text; the P0 text was instead inserted into a 17-pp paper that stayed at 17 pp (line count fell 2235 -> 2230, so the edits were net-negative in lines). |

**Closure summary: 6 closed (`R5-4`, `R5-6`, `R5-7`, `R5-9`, `R5-12`, plus the Table I caption defect), 7 partially closed (`R5-1`, `R5-2`, `R5-3`, `R5-5`, `R5-11`, `R5-14`, `R5-17`), 6 open (`R5-8`, `R5-10`, `R5-13`, `R5-15`, `R5-16`, `C1`, `C2` — counted as seven rows since `C1`/`C2` are compression items).**

---

## 8. New Findings Introduced By This Revision

Severity-ranked. Provenance uses the frozen vocabulary. `Fix class` uses the skill's values.

| ID | Severity | Finding | Evidence | Provenance | Affected dimensions | Fix class | Owner skill |
|---|---|---|---|---|---|---|---|
| `F1` | moderate | The new flatness sentence states that "the per-window minimizer is not unique" (L963), which reads against Theorem 1's unconditional "has a unique global minimizer $\boldsymbol\alpha_r^\star$" (L1253-1254), and it attributes to the group term a job the cited measurement does not establish | L961-964 vs L1249-1254; `MYOPIC_DIAG.json` (`range_median: -1.13e-13` on the **`ℓ_1`** surface only); `EXECUTION_REPORT.md:132-134` (conclusion stated in terms of the `ℓ_1` argmin) | `revision_regression` (new text) with `newly_revealed_by_evidence` (the v3 diagnostic) | Soundness, Clarity | writing | `ccf-paper-writer` |
| `F2` | minor | "Interchangeable" now names three different relations in one paper, and the new §V sentence sharpens rather than resolves the collision | L1679-1680: "the arrival law need not be an interchangeable proxy for the deployment target" (risk functionals); L1782 and L1928: "worst-group RMSE is interchangeable with FedAU-Window" / "target RMSE is interchangeable rather than a Holm-significant win" (tolerance); L1439: "are interchangeable" (rankings) | `previously_undetected` (the §V wording pre-dates the revision; the revision's E-adjacent reflow at L1679-1681 brought the two uses into adjacent prominence) | Terminology | writing | `ccf-paper-writer` |
| `F3` | minor | The abstract's `1.24 %` structural claim still carries no ruler and its neighbouring `6.55 %` U-Air RMSE cost is not printed anywhere in the body, so the abstract is not verifiable from the body text | L86-87 abstract; L1576-1578 body (SensorScope `1.237 %` and `6.885 %` only); Table~\ref{tab:main_effectiveness} L1875 (SS `1.0139`, U-Air `1.1954`) | `previously_undetected` (abstract unchanged; the body side improved this round, which exposes the residual abstract gap) | Clarity, Terminology | writing | `ccf-paper-writer` |
| `F4` | minor | The restored sentence at L1547-1551 contains two doubled connectives and reads as two clauses fused without a subject change | L1547-1551: "describe this construction rather than the range attainable when selection varies at the unit level, **and** the compounding direction is therefore part of the construction **rather than** a measured property of these traces, **and** the structural-alignment results ..." | `revision_regression` (the rewritten sentence) | Clarity | writing | `ccf-paper-writer` |

**Not a new finding, recorded for completeness:** the nine undeclared edits listed in §2 were each checked for a defect and none was found. The E5 insertion also shifted every line after L961 by +4 relative to the round-5 snapshot; all 96 labels still resolve, so no cross-reference was broken.

`F1` is the only new finding with a dimension consequence, and it is deliberately not charged as a Soundness decrease: the mathematics of the program is not shown to be wrong, and `main.tex` already contains the self-limiting sentence at L1260-1261 ("The theorem concerns the program, not post-hoc exact optimality of every logged solve"). A one-sentence scoping edit (F1's recommended fix below) would remove the tension entirely.

---

## 9. Absolute-Readiness Scorecard (current version only)

| # | Dimension | Current /5 | Confidence | Deduction basis and raise condition |
|---|---|---|---|---|
| 1 | Originality | 2 | high | Combination-and-scenario novelty; the nearest two-stage IPW work already contains the key structure (`W4`, unchanged). Raise: complete the FedIPW/FedPALS variable-constraint-information mapping and prove an irreducible difference |
| 2 | Soundness | 4 | high | Deduction: `R5-1` the "not a structural contributor" claim (L1842-1843, L232-235) is still unscoped against the κ=1000 rule that L2074-2077 prints lowest on the group endpoint; `R5-2` the equivalence band still has no decision rule (L606-610); `F1` the L963 uniqueness phrasing reads against Theorem 1. Credit: `R5-4`/`R5-6`/`R5-7`/`R5-9` are all closed, no proof error found, `W2`/`W5` repairs intact. Raise: scope the debt claim to the frozen `λ_g`=1, `η`=0.01 configuration and add the band's decision rule — both text-only |
| 3 | Evidence | 3 | high | Deduction: still no prediction-endpoint contrast that survives Holm on any block (L2090-2093), and the paper's own evidence shows the full (P2) captures only a minority share of a small recoverable headroom. Credit: `R5-4`'s disclosure makes the new rule evidence auditable, and the mechanism contrast (`M8`/`W3`) remains in-manuscript. Raise: one endpoint with an externally meaningful win, or a task where structure converts to prediction |
| 4 | Clarity | 3 | high | Deduction: `R5-3` the band denominator is now correctly labelled but its value is still never printed, so the band remains unconvertible; `R5-15` the band still has no label, no decision rule and no disclaimer; `R5-8` `Proj_{C_r}(β̂)` still undefined at first use; `R5-10` the (43) coefficients still unlabelled; `F1`, `F3`, `F4`. Credit: `R5-12` closed — the §VI-A fragment is genuinely repaired. Raise: print the denominator value once per dataset and add one band sentence |
| 5 | Reproducibility | 2 | medium | `M7` unresolved: `RAVEN_MCS_PUBLIC_REPRO_R1` (L2203-2213) still does not list the round-v3/v4 ladder, band-decision or trained-rule artifacts, so the band and ladder claims are not independently checkable from the stated bundle; `R5-17` partially closed; `W6` unchanged. Raise: refresh the bundle and extend its inventory |
| 6 | Significance | 2 | medium | Unchanged. The reachable large effect is still the single Design ablation; the structural headroom is unchanged and the paper's own decomposition still shows the bulk of it is closed by uniform weights. Raise: a task where target-mass alignment changes a decision, not a diagnostic |
| 7 | Related work | 3 | medium | Reasonable positioning; `W4` unresolved and not re-searched this round. Raise: the irreducibility mapping |
| 8 | Terminology | 3 | high | Deduction: the frozen `+0.0073` pp quantity is still called "the debt recursion" (L1840-1841) while the κ=1000 quantity is a "rule" (L2082) although both are the same recursion at different weights; "closable gap" is correctly named but unvalued; "recoverable" still names two headroom objects; `F2` adds a third sense of "interchangeable". Raise: three one-line disambiguations |

**Weighted readiness sum = 2.90** (`0.10×2 + 0.20×4 + 0.25×3 + 0.15×3 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×3`; round 5: **2.90**; round 4: **3.05**). **Overall score: 5/10, threshold 4/10** — borderline negative, weak-reject band upper edge.

**Why the overall is unchanged at 5/10 and not raised.** The calibrated 1-10 stance follows the strongest *unresolved decision-relevant* weakness, which this revision did not touch: no prediction endpoint survives Holm on any block, and the paper's own new evidence shows the full calibration program is unnecessary for the structural gain it is credited with (the projection alone carries it). The round-5 text defects that *were* closed were claim-management repairs, not new capability; closing a claim-management complaint returns the paper to the standard it should have met, it does not exceed it. Raising the stance would require the evidence axis to move, and nothing on that axis changed.

**The single strongest unresolved decision-relevant weakness that keeps the overall where it is.** The paper's own mechanism contrast shows that the calibration apparatus it is built around — the group-matching, variance and staleness terms of (P2), and the debt recursion at its frozen strength — is not what produces the structural gain; the gain is carried by projecting the reconstructed reference onto the feasible set. Combined with the absence of any significant prediction endpoint, this means the paper's central artefact is not shown to be necessary for the effect it is credited with. Everything else in this report is a sentence-level fix; this one needs an endpoint result or a demonstrated necessity argument (feasibility, accounting, or variance control) that the paper does not currently measure.

**Remaining blocking evidence (by weight).**
1. **Evidence (0.25):** one endpoint where alignment converts to prediction, or an externally meaningful task; the full-(P2)-necessity question is answered *against* the full apparatus and the paper must live with that answer.
2. **Soundness (0.20):** scope the debt claim to the frozen configuration (`R5-1`); state the band's decision rule and its non-test status (`R5-2`, `R5-15`); scope the L963 flatness phrasing to the `ℓ_1` surface (`F1`).
3. **Clarity (0.15):** print the closable-gap value once per dataset (`R5-3`); define `Proj_{C_r}` at first use (`R5-8`); label the (43) coefficients (`R5-10`).
4. **Reproducibility (0.10):** extend the bundle inventory to the ladder/band/trained-rule artifacts (`M7`).

---

## 10. Confidence And Comparability

**Confidence: 4/5** (`high but not full`). Reasons, reported separately from both scorecards per `version-comparison.md`:

- **What supports the 4.** The current `main.tex` was read in full; the round-5 snapshot was diffed line-by-line against it, so every claimed fix is verified against the exact pre-edit state rather than taken on trust; all headline numbers in the nine fixes were re-derived against the evidence files (`MYOPIC_DIAG.json` for the 3279-window/1e-13 flatness pair; `PART_B_REPORT.md:17,18` for the 2.0e-6/3.0e-6 and 2.9e-5/3.7e-5 residuals; `PART_A_REPORT.md:23-30` for the band rows; `PART_A_REPORT.md:59,77` for the exploratory status); the structural counts and compile state were re-measured directly, not inherited.
- **What holds it below 5.** (i) `supplemental.pdf`/`appendix.tex` was not re-read this round, so the `F1` L1-versus-L2 question cannot be settled from the artefacts I read — `MYOPIC_DIAG` measures the `ℓ_1` surface only, and whether the `ℓ_2` group term is equally flat is not determinable without the `‖M_rα − μ‖₂` range or the appendix proof's uniqueness argument. (ii) The band's denominator value is still *inferred* from `PHASE3_REPORT.md:77` plus the printed `−0.268`, not stated anywhere in the manuscript — so my reading of `R5-3`'s residual is an inference, and I flag it as unresolved rather than as established. (iii) No experiment was re-run and the public repro bundle's contents were not verified.
- **Comparability.** The contract is unchanged (`TMC-J-R4`, identical weights, anchors and threshold as rounds 4-5). The comparison is clean in a way round 5 was not: `\label` (96), `\begin{table` (4), `\begin{figure` (4), `\begin{equation` (37), `\cite{` (42), `\section{` (8), `\subsection{` (29), `\begin{proposition` (4) and `\begin{theorem` (2) are all identical between the pre-v4 snapshot, the round-5 snapshot and the current file, so there is no numbering drift and no reference breakage to discount. The residual comparability caveat is the same one round 5 disclosed: historical scores are inherited rather than recomputed, and the round-4 report is in Chinese while rounds 5-6 are in English with dimension identity preserved one-to-one.

---

## 11. Questions For Authors (updated)

1. For each dataset, what is the numerical value of the closable-gap denominator `Δ_unif − Δ*` in pp? The label at L607-608 is now correct, but without the value no band verdict is checkable by a reader.
2. What is the band's decision rule — point estimate or interval containment — and is it a test or a descriptive reporting convention? L246-247 now says "their paired intervals lie inside", which reads as containment, but no rule is stated anywhere and the sibling `+0.5 %` tolerance at L1632-1633 carries the disclaimer this one lacks.
3. Does the statement at L963 ("the per-window minimizer is not unique") refer to the `ℓ_1` group-mismatch surface or to the program `J_r`? If the latter, how does it reconcile with the unconditional uniqueness of Theorem 1 (L1249-1254)? And what evidence establishes that the group term "selects among equivalent solutions" (the cited `MYOPIC_DIAG` measures the `ℓ_1` surface only)?
4. Can the sentence "debt is an auditable accounting recursion ... rather than a structural contributor" (L1842-1843, echoed at L232-235) be scoped explicitly to the frozen `λ_g`=1, `η`=0.01 configuration, given that L2074-2077 prints the κ=1000 projection-with-debt rule as lowest on the group endpoint on both datasets?
5. Is `Proj_{C_r}(β̂)` defined anywhere, and can its definition be moved to its first use at L245?
6. Where in the body is the U-Air `6.55 %` RMSE cost of Design (abstract L87) printed?

---

## 12. Remaining Work List (ordered, smallest useful next actions)

| # | Priority | Action | Owner skill | Input needed | Why it is the right next action |
|---|---|---|---|---|---|
| 1 | P0 | Scope the debt claim to the frozen configuration in all three places (L1842-1843, L232-235, and the §VII-E ablation paragraph), and make L2074-2086 say in one clause that the κ=1000 rule and the frozen-strength contrast are the *same recursion at different weights* | `ccf-paper-writer` | `PART_A_REPORT.md:25`; `PART_B_REPORT.md:82` | `R5-1` is the largest remaining soundness deduction and the only one where the paper currently states a conclusion its own table contradicts. Two sentences. |
| 2 | P0 | Print the closable-gap denominator value once per dataset next to the band definition at L606-610 | `ccf-paper-writer` | `round_v2/PHASE3_REPORT.md:77` (3.44 pp SS); the U-Air counterpart | `R5-3`'s label fix is done; the value is the last missing piece and it is one clause. Without it no band verdict is convertible. |
| 3 | P0 | Add one sentence to the band definition stating the decision rule (interval containment) and that the band is a descriptive reporting convention rather than a test; give it a `\label`; scope the L963 sentence to the `ℓ_1` surface | `ccf-paper-writer` | L606-610; L1632-1633; `MYOPIC_DIAG.json` | Closes `R5-2`, `R5-15` and `F1` together in a single two-sentence edit in one paragraph. |
| 4 | P1 | Define `Proj_{C_r}(β̂)` at its first use (L245) and label its new-rule status there; label the (43) coefficients as U-Air at L2035-2037 | `ccf-paper-writer` | `main.tex` L245, L2035-2037; `\eqref{eq:Cr}` | Closes `R5-8` and `R5-10`. Three clauses, no new claims. |
| 5 | P1 | Add the missing mechanism half of `R5-5`: say that on these supports the covered per-window group coordinates are target-empty (each window covers a small subset of the 220 groups), name the `β̂` anchor as the surviving lever, and cite the tie-break result | `ccf-paper-writer` | `ERRATA_v2.md:35`; `EXECUTION_REPORT.md:132-134`; L2133-2134 | Converts the flatness fact into the explanation the §VII-F insensitivity finding needs. Two sentences. |
| 6 | P1 | Extend `RAVEN_MCS_PUBLIC_REPRO_R1` (L2203-2213) to cover the round-v3/v4 ladder, band-decision and trained-rule artifacts | `ccf-integrity-auditor` | bundle contents; `results_w1_ladder/round_v3`, `round_v4` | Closes `M7`, the whole of the Reproducibility deduction (weight 0.10). |
| 7 | P1 | Cross-reference the `M_r`-drift residual (L2217-2223) into the ruler clause (L606-608) and into Proposition 3's shared-`M_r` premise | `ccf-paper-writer` | `PART_B_REPORT.md:20`; L606-608; Prop. 3 | Finishes `R5-17`; one cross-reference in each of two places. |
| 8 | P2 | Repair the restored sentence at L1547-1551 (F4) and disambiguate "interchangeable" at L1679-1680 vs L1782/L1928 (F2) | `ccf-paper-writer` | L1547-1551; L1679-1681; L1782; L1928 | Two small clarity fixes with no claim consequences. |
| 9 | P2 | FedIPW/FedPALS variable-constraint-information mapping for the novelty boundary | `ccf-literature-searcher` | morishita2026who, listozec2024overcoming, goetze2025floss full texts | Closes `W4`; the only route to movement on Originality (0.10) and Related work (0.05). |
| 10 | P2 | Buy the space for the P0 text: delete Proposition 4's unused directional-derivative clause (`C1`, ~5 lines) and move the coverage-Gate appendix propositions/corollaries to the artifact (`C2`, ~35-45 lines) | `ccf-paper-writer` | L1349-1351; `appendix.tex` L1282-1526 | Both items are still fully open; the round-5 budget plan for the P0 text was not executed and the paper absorbed the edits inside 17 pp by net line reduction instead. |

---

## 13. Score Revision Criteria (version-comparison fields included)

```text
Raising the score would require: the P0 pair (R5-1 scoping + R5-2/R5-15/F1 band statement) as a single coherent edit; the closable-gap value printed (R5-3); then the repro-bundle inventory extended (M7). Those four would move Soundness to 5 and Clarity to 4 and lift the weighted readiness sum by roughly +0.30 to +0.40 without any new experiment.
Lowering the score would be triggered by: an error in the denominator value once printed, if it does not imply the printed -0.268; a reviewer independently noticing that L963's non-uniqueness phrasing reads against Theorem 1's unconditional uniqueness; or a reviewer noticing that the paper calls debt a non-contributor while its own table ranks the debt-weighted rule lowest.
Concerns unlikely to change before submission: W4 (FedIPW/FedPALS irreducibility); W6/M7 (bundle refresh); a task where target-mass alignment changes a decision.
Relative progress: weighted delta 0.00 => unchanged (threshold 0.05); 6 issues closed (R5-4, R5-6, R5-7, R5-9, R5-12, Table I caption), 7 partially closed (R5-1, R5-2, R5-3, R5-5, R5-11, R5-14, R5-17), 7 open or excluded (R5-8, R5-10, R5-13, R5-15, R5-16, C1, C2); no traceable increase, no traceable decrease
Absolute readiness: weighted sum 2.90 (unchanged from round 5; round 4 was 3.05), stance 5/10 held (threshold 4/10); held because the strongest unresolved decision-relevant weakness (evidence/significance) is untouched and this round's changes are claim-management repairs that restore an expected standard rather than exceed it
Confidence and comparability: 4/5; contract unchanged (TMC-J-R4); historical scores inherited verbatim from the round-5 report rather than recomputed; structure counts identical across the pre-v4, round-5 and current files, so no numbering-drift discount applies; the residual comparability caveat is the round-4 Chinese vs rounds 5-6 English dimension-identity mapping
New issue provenance: F1 = revision_regression (new text) + newly_revealed_by_evidence (v3 diagnostic); F4 = revision_regression; F2, F3 = previously_undetected (applies to both versions)
Traceable score decreases: none
Traceable score increases: none (the six closed issues were contributors to deductions that sibling open issues still carry)
```

---

## 14. Checks Run, Checks Skipped, Unresolved Risks

```text
Checks run: full read of main.tex (2230 lines); byte-level snapshot diff against snapshots/2026-10-03-pre-register-fix/main.tex (102 insertions / 107 deletions, 209 changed lines) with every hunk classified against the E1-E9 claim list; structural counts re-measured on current, round-5 snapshot and pre-v4 snapshot (all nine counts identical across all three); em-dash count (0); main.log parse (17 pages, 0 Overfull, 21 Underfull); main.aux parse (96 \newlabel matching 96 \label, 0 "??", mtime after main.tex); full-text greps for statistically equivalent (0 hits), Proj_ (11 hits, no definition), oracle (9 hits, all legitimate), closable gap / 3.44 / 1.32 (no semantic hit for the value); verification of the flatness numbers against MYOPIC_DIAG.json; verification of the replay residuals and gate statuses against PART_B_REPORT.md:15-21; verification of the exploratory status against PART_A_REPORT.md:59,77; verification of the band rows against PART_A_REPORT.md:23-30; re-derivation of the weighted readiness sum and the weighted progress delta
Checks skipped: line-by-line read of appendix.tex / supplemental.pdf; independent re-run of any experiment; verification of the public repro bundle contents; external related-work search; the L1-vs-L2 flatness comparison needed to settle F1 fully
Unresolved risks: (i) F1's severity depends on whether the L2 group term is equally flat, which MYOPIC_DIAG does not measure - if it is flat the claim is true and the fix is wording-only, if it is not the claim needs weakening; (ii) the closable-gap denominator value remains inferred from PHASE3_REPORT.md:77 plus the printed -0.268 rather than stated in the manuscript; (iii) the B-G2 gate's partial status and the A2 gate's reason are still undisclosed, though the exploratory labelling neutralises the over-read R5-4 was about; (iv) six undeclared edits were found beyond the E1-E9 list - none defective, but the declared edit list is not exhaustive
```

---

## 15. Output Self-Check

1. Section order follows the round-5 report's structure and `fixed-output-format.md`, with the two requested scorecards at §6/§9 and the closure table at §7. **Pass.**
2. Two scorecards are separate, computed under one frozen contract, and never fused. **Pass.**
3. Every score at or below 3 carries a concrete deduction and a raise condition. **Pass.**
4. Every claimed fix (E1–E9 + caption) is verified against the pre-edit snapshot with a quoted current line and an explicit verdict. **Pass** (§2).
5. No traceable score increase and no traceable score decrease is asserted without naming the issue IDs that decide it; the three-way classification of why closed issues do not raise a dimension is tabulated. **Pass** (§6).
6. Pre-existing issues (`R5-13`, `R5-10`, `R5-16`, `N1`, `W4`, `W6`, `M7`, `N2`) are explicitly excluded from the progress delta under the consistent-application rule. **Pass** (§6).
7. Every new finding carries severity, evidence, provenance, affected dimensions, fix class and owner skill. **Pass** (§8).
8. Confidence is reported separately with its reasons, and comparability is reported as a third field rather than a score dimension. **Pass** (§10).
9. No acceptance probability is stated; no score is rounded. **Pass.**
10. No file other than this report was created or modified; the pipeline was not run. **Pass.**
