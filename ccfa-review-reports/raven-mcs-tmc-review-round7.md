# RAVEN-MCS — IEEE TMC Independent Re-Review, Round 7 (version-comparison)

```text
Review date: 2026-10-03
Target venue/year/track: IEEE Transactions on Mobile Computing, journal revision; method + measurement long paper
Paper title: RAVEN-MCS: Target-Mass-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex (2226 lines, 17 pp, 0 errors / 0 undefined / 0 overfull)
  TO_OVERLEAF_paper_tmc_r1_clean/main.aux (20538 bytes, mtime 10:41:33 > main.tex 10:40:43; 97 \newlabel, 0 "??")
  TO_OVERLEAF_paper_tmc_r1_clean/main.log (17 pages, 886558 bytes; 0 Overfull, 21 Underfull)
  snapshots/2026-10-03-pre-design-fix/main.tex (2230 lines) — the exact pre-edit state
  snapshots/2026-10-03-pre-v4-contribution/main.tex (2294 lines) — structural-count reference
  results_w1_ladder/round_v2/{PHASE3_REPORT,EXECUTION_REPORT,PHASE4_REPORT,PHASE5_REPORT,PHASE4_INPUT_GAPS}.md
  results_w1_ladder/round_v3/{PREREG,EXECUTION_REPORT,ERRATA_v2}.md
  results_w1_ladder/round_v4/{PREREG,PART_A_REPORT,PART_B_REPORT,FULL_SEED_DECISIONS,FULL_SEED_LADDER,SOURCE_LADDER}.csv/md
  ccfa-review-reports/raven-mcs-experiment-design-audit.md (the repair pass's own design audit)
  ccfa-review-reports/raven-mcs-tmc-review-round6.md (immediate predecessor; closure baseline)
  ccfa-review-reports/raven-mcs-tmc-review-round5.md, ccfa-review-reports/raven-mcs-tmc-review.md (round 4)
Search basis: no new external search this round (see §4)
Report file: ccfa-review-reports/raven-mcs-tmc-review-round7.md
Reviewer mode: version-comparison; centrepiece = verification of the experiment-design repair pass (P0-1..P0-3, EA-1/EA-2, two deletions)
Manuscript version / comparison range: round-6 manuscript (snapshot 2026-10-03-pre-design-fix, 2230 lines) -> current 17-pp revision (2226 lines)
Frozen comparison contract ID: TMC-J-R4 (inherited verbatim; unchanged)
```

**Naming-convention note (skill rule 8).** `ccf-paper-reviewer` rule 8 asks for one canonical `ccfa-review-reports/` report rather than a dated copy per iteration. The requesting agent explicitly asked for a separate round-7 file. This file is the round-7 canonical report; `raven-mcs-tmc-review.md`, `-round5.md` and `-round6.md` are deliberately left untouched. No other file was created or modified; all temporary analysis files were removed.

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

**Rubric deviation, stated explicitly (inherited).** The project-frozen 8-dimension rubric uses *Originality/novelty, Soundness/technical quality, Evidence/experiments, Clarity/presentation, Reproducibility, Significance/impact, Related work/positioning, Terminology/notation*, which is **not** the skill's default set (which ends in *Ethics/limitations*). Per instruction the round-4/round-5/round-6 names and weights are kept unchanged.

**Materials asymmetry disclosed.** Historical (round-6) scores are inherited verbatim from `raven-mcs-tmc-review-round6.md` §6/§9 and were not recomputed. Only the current version was rescored. All line numbers in this report index the **current 2226-line file**; pre-fix line numbers are labelled as such.

---

## 2. Verification Of The Claimed Repair

The diff between `snapshots/2026-10-03-pre-design-fix/main.tex` and the current file is **9 hunks / 29 insertions / 33 deletions**, exactly matching the scope declared by the repair pass. Every edit was read at its current location and, where it carries a number, checked against the evidence file that produces it.

| ID | Claimed fix | Verified at | Verdict |
|---|---|---|---|
| `P0-1a` | frozen-configuration scope in the contributions | L232-236 | **Present, and the verdict clause itself is scoped.** "Target debt is an internal accounting recursion for residual group under-service, not a standalone performance contribution; **at the frozen configuration ($\lambda_g=1$, $\eta=0.01$, the strength used by the frozen runs)**, instantaneous calibration and debt are neither prediction drivers nor structural contributors." The scope is an adverbial on the verdict, not a label. Config verified: `PHASE4_INPUT_GAPS.md:72` ("与冻结 run 的 λ 一致：λ_g=1.0, λ_β=1.0, λ_v=0.1, λ_s=0.1") and `ERRATA_v2.md:55` / `round_v4/PREREG.md:52` (η = 0.01). |
| `P0-1b` | frozen-configuration scope at the results verdict | L1842-1846 | **Present, and verdict-level, not label-level.** "…stay inside the band of Section~\ref{subsec:equivalence_band} **at the frozen configuration ($\lambda_g=1$, $\eta=0.01$, the strength used by the frozen runs), so at that strength** debt is an auditable accounting recursion for residual under-service rather than a structural contributor". The κ=1000 rule is now outside the verdict *by construction*: the verdict is bound to the frozen strength and L2078-2080 identifies the κ=1000 arm as one that "sets the debt weight to $\kappa=1000$ rather than the frozen value". This meets round 6's standard (round 6 rejected the label-only variant at the same site). |
| `P0-2` | closable-gap value printed once per dataset + ruler qualifier + subset caveat | L611-620 | **Present and numerically correct.** "That gap is $3.44$ pp of target mass on SensorScope and $1.32$ pp on U-Air (protocol~$R$ always-on) over the $20$ seeds." Verified against `round_v2/PHASE3_REPORT.md:77` ("`(Δ_unif − Δ*)/2 = 3.44 pp`" SensorScope; "U-Air `R_on` 为可回收 **1.32 pp**"), whose seed block is the 20-seed table (`PHASE3_REPORT.md:26`). The unit chain closes exactly: pp = Δ/2×100 is defined at L606-607, and 0.922 pp / 3.44 pp = **0.268**, which is the printed G-unit value at L1837 — matching `round_v4/FULL_SEED_DECISIONS.csv:6` (`B1:raven − B1:raven_wo_design`, `n_all20 = 20`, `pp_all20 = 0.922283`, `dG_all20 = −0.268095`, CI `(−0.3197, −0.2145)`). The debt row closes the same way: 0.0073/3.44 = 0.0021, and `FULL_SEED_DECISIONS.csv:9` (`L6 − L5`, `n_all20 = 20`) gives `pp_all20 = 0.007289`, `dG_all20 = −0.002119` — inside ±0.10. |
| `P0-2` (Δ* variants) | two Δ* variants not conflated | L618-620 | **Present and evidence-backed.** "Read-only ladder contrasts instead use the report-half subset, whose same-support optimum differs slightly, so band verdicts are not convertible between the two." Evidence: `round_v2/EXECUTION_REPORT.md:118` uses the report-half `Δ* = 0.97276` (SS) / `1.06311` (UA) for ladder rows (gaps 3.12 pp / 1.33 pp) and the 20-seed `Δ* = 0.95813` / `1.07103` for the frozen-arm rows, stating "两套 `Δ*` 参考分行标注，未混用". The printed 3.44 / 1.32 pp are the 20-seed pair, and every §VII-C band verdict quoted in the manuscript is an `n_all20` row — so the printed denominator is the correct ruler for them and the caveat covers the family it names. |
| `P0-3a` | decision rule + non-test status + registered necessity half + label | L613-617, L573 | **Present and correctly placed.** "The pre-registered equivalence band is $\pm0.10$ in those units, **and a contrast is read as inside the band when its paired interval lies within $\pm0.10$; a component removal is read as necessary only when that interval lies entirely beyond the band in the worsening direction, and the band itself is a practical-significance convention rather than a hypothesis test.**" All three clauses trace to `round_v1/PREREG.md:43-44` ("`τ_eq` `0.10`: …配对区间完全落在 [−0.10, 0.10] 内，才可称'等效'"; "必要性方向 `+0.10`") and `round_v3/PREREG.md:97-98`. The rule is stated **in the paragraph that defines the band and that the results text now cites**. Label resolves: `main.aux` -> `\newlabel{subsec:equivalence_band}{{\mbox {III-F}}{5}{}{subsection.3.6}{}}`, cited once from the results at L1842 (`band of Section~\ref{subsec:equivalence_band}`). |
| `P0-3b` | ℓ₁ scoping of the flatness sentence | L971-976 | **Present; the clash is removed at the source.** "…has median $10^{-13}$, so **that $\ell_1$ surface is flat and its minimizer over $\mathcal{C}_r$ is not unique, and the group term selects among the solutions that are equivalent in $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ rather than among all of $\mathcal{C}_r$.**" The theorem it previously read against is the uniqueness theorem, currently at **L1261-1266** ("has a unique global minimizer $\boldsymbol\alpha_r^\star$"; pre-fix L1249-1254 — round 6's anchor) with its own self-limiting sentence at L1272-1273 ("The theorem concerns the program, not post-hoc exact optimality of every logged solve"). The sentence no longer makes a claim about the minimizer of $J_r$, so the unconditional uniqueness statement is no longer contradicted. |
| `EA-1` | the +0.5 % device no longer borrowed as a decision ruler for the ablation | L2058-2065 | **Substantively done.** "…but only by $0.0141\%/0.0040\%$ on SensorScope and $0.0043\%/0.0024\%$ on U-Air, **far below the descriptive $+0.5\%$ worst-group tolerance that governs the external comparisons of Section~\ref{subsec:eval_rq2} on a different endpoint**.  That matches the accounting of \eqref{eq:debt_bound}…" The decision-ruler framing is gone ("minimum practical effect used elsewhere" is deleted) and the different-endpoint fact is now stated in the same sentence. **Residual (not a new finding):** the sentence still *quantitatively compares* 0.0141 % against a foreign ruler while disclaiming it; a stricter form would cite the ablation's own resolution. One clause, optional. |
| `EA-2` | "interchangeable" no longer used for the +0.5 % tolerance | L1781-1783 | **Present at the defect site.** "Four-block worst-group RMSE **stays within the descriptive $+0.5\%$ worst-group tolerance versus** FedAU-Window and ObsUse-Window (TEST $-0.01\%$ and $+0.05\%$; ALL20 $+0.02\%$ and $+0.10\%$)." Full-text grep: no remaining occurrence of "interchangeable" attaches to the tolerance device. One residual site survives (L1923, "target RMSE is interchangeable rather than a Holm-significant win") — see `F2` in §7. |

**Deletions verified (the task's highest-risk check: a deletion that loses content is a defect).** Both deletions are genuine duplication; **every deleted statement is retained elsewhere, and several are retained in a more precise form.** No content was lost.

| Deleted passage (pre-fix lines) | Surviving line(s) in the current file | Verdict |
|---|---|---|
| Roadmap: "The balanced control is a no-harm check, and a risk-interchangeability experiment tests whether arrival-weighted and deployment-target-weighted risks are interchangeable." | L263 ("a no-harm control, a risk-semantic block"), L1440-1441 (RQ bullet 1), L1641-1644 (balanced control: "a sanity check, not a superiority test"), L1646-1663 (risk-interchangeability experiment) | retained, in three places |
| Roadmap: "Independent rankings follow on T-Drive taxi replay, NSW-Traffic regions, and City Scanner occupancy with controlled or measured $O$; none of those rows is mixed into Table~\ref{tab:main_effectiveness}." | L265-268 (Introduction: "Independent hybrid ceilings, namely a T-Drive taxi replay under real $R$ with controlled $O$ and $U$, an NSW-Traffic four-region protocol table, and the City Scanner {PM}$_{2.5}$ and Pilot~2 tables … are not mixed into that development table"), L1500-1504 (Table I caption), L2148-2150 (Limitations) | retained |
| Roadmap: "The main comparison is a development table under always-on protocol $R$ on station traces, not a jointly measured mobile ranking; an intermittent-occupancy protocol table on the same station clients is in the supplemental material." | L263-265 (Introduction), L274-275 ("A supplemental occupancy-robustness block thins protocol $R$ on the same station clients"), L1531-1532, L1851-1854 (Table II caption: "a development table on station traces whose $O$ and $U$ layers are protocol-constructed, not a real-mobility ranking") | retained |
| Roadmap: "A component-removal ablation drops one component at a time: on SensorScope, Design moves $\Delta_{\mathrm{group}}$ while $\mathrm{RMSE}_{\mu}$ stays essentially flat, so $\Delta_{\mathrm{group}}$ is a structural diagnostic." | L1945-1946 ("The component-removal ablation drops Design, Obs, Use, Inst, or Debt under the same Complete-aligned selection trace and paired seeds") — **note this sentence already existed pre-fix at L1950, so the deleted copy was a true duplicate** — plus L1776-1780 (numbers) and L1445-1446 (RQ bullet 3) | retained; pre-existing duplicate confirmed |
| Recap: "of that gap, $68.96\%$ on SensorScope and $83.07\%$ on U-Air is already recoverable by uniform server weights, the surviving part is carried by the projected reference, and the terms of (P2) and the debt recursion stay inside the equivalence band." | L1821-1828 (with CIs: "$1.44$ pp ($68.96\%$, $[1.22,1.65]$) … $1.22$ pp ($83.07\%$)"), L1830-1831, L1839-1845 | retained, with intervals the recap lacked |
| Recap: "against the no-Design baselines it ties all six on prediction while keeping the structural advantage against five" | L1801-1802 ("against the no-Design baselines RAVEN-NoDesign ties all six on prediction and worst-group RMSE"), L1802-1804 ("lowers $\Delta_{\mathrm{group}}$ by $2.4\%$ to $3.7\%$ and $\Delta_{c\text{-}s}$ by $1.4\%$ to $2.6\%$ against FedAvg, FedAsync, TimeAlign, FedAU and ObsUse, all $20/20$") | retained **and sharpened**: the recap gave a count ("five"), the survivor names the five baselines and adds the $20/20$ seed accounting |
| Recap: "with Debt-Cal tying on both endpoints and TEST mean relative worst-group differences of $+0.48\%$ and $+0.44\%$ versus FedAU-Window and ObsUse-Window" | L1804-1805 ("and ties Debt-Cal on both"), L1793-1795 ("the TEST mean relative differences versus FedAU-Window and ObsUse-Window are $+0.48\%$ and $+0.44\%$ (seeds $30011$--$30020$), and $+0.002\%$ and $+0.075\%$ over all $20$ table seeds") | retained, with a second seed slice added |
| Recap: "On U-Air, RAVEN-NoDesign improves primaries and worst-group RMSE over Design-on" | L1785-1786 ($1.1131$ vs $1.1954$ on $\mathrm{RMSE}_{\mu}$), L1805-1806 (Design-on worst-group $1.2630$), Table~\ref{tab:main_effectiveness} L1885-1886 (U-Air worst-group $1.2630$ vs $1.1703$) | retained in text and table |

**Structure, length and compile state (re-measured, not inherited).**

| Check | pre-v4 snapshot | pre-fix snapshot | **Current** | Verdict |
|---|---|---|---|---|
| `\label{` | 96 | 96 | **97** | +1 = the declared band label; the diff contains exactly one added `\label` and no deleted label |
| `\begin{table` / `\begin{figure` / `\begin{equation` | 4 / 4 / 37 | 4 / 4 / 37 | **4 / 4 / 37** | identical |
| `\cite{` / `\section{` / `\subsection{` | 42 / 8 / 29 | 42 / 8 / 29 | **42 / 8 / 29** | identical |
| `\begin{proposition` / `\begin{theorem` | 4 / 2 | 4 / 2 | **4 / 2** | identical |
| em dashes (U+2014) | 0 | 0 | **0** | ≤ 3 required |
| pages | 17 pp | 17 pp | **17 pp** (`Output written on main.pdf (17 pages, 886558 bytes)`) | identical |
| errors / undefined / overfull | 0 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** (0 `!` lines, 0 `undefined`, 0 `Overfull`, 21 `Underfull`, `main.aux` 97 `\newlabel` matching 97 `\label`, aux mtime 10:41:33 > tex 10:40:43) | identical |
| lines / words / characters | 2294 / — / 112726 | 2230 / 11245 / 112608 | **2226 / 11218 / 112386** | −4 lines / −27 words / −222 chars; the repair's own length accounting reproduced exactly |

**Declaration accuracy.** The repair pass's declared edit list is exhaustive this round: 9 diff hunks, all accounted for by P0-1a, P0-1b, P0-2, P0-3a, P0-3b, EA-1, EA-2, and the two deletions. No undeclared text change was found (round 6 found six).

**Two documentation slips in the audit itself (not manuscript defects).** (i) `raven-mcs-experiment-design-audit.md` §FL-3 refers to "Theorem 2 at L1249-1254"; L1249-1254 in the current file is the close of Proposition 3, the uniqueness theorem is currently at L1261-1266, and it is the first theorem of the paper (round 6 called it Theorem 1) — the audit quoted pre-fix line numbers while declaring post-fix numbering. (ii) The audit's availability section lists the unapplied hygiene items at "L245-246", "L2030-2032", "L1679-1680", "L1547-1551"; all four match the current file, so only the FL-3 anchor is off.

---

## 3. Search And Related-Work Basis

```text
Queries used: none this round
Sources searched: repository artifacts only (manuscript, exact snapshot diff, main.aux/log, round_v1-v4 ladder evidence, the repair pass's design audit, rounds 4-6 review reports)
Closest works found: not re-searched; round 4 carried FedIPW (morishita2026who), FedPALS (listozec2024overcoming), FLOSS (goetze2025floss), FedAU (wang2024lightweight) as the nearest neighbours, cited at main.tex L1556-1568
Unverified related-work risks: W4 (novelty boundary vs FedIPW/FedPALS) remains unresolved and was NOT re-verified in this round
Source-quality screening status: not performed; no citation was checked against its source
```

Honest statement: this round's budget went to verifying the experiment-design repair and re-scoring. Any novelty or positioning statement below is a carry-over, not a fresh judgement.

---

## 4. Expected Review Outcome

```text
Expected outcome: weak reject, upper edge (5/10); stance held, weighted readiness sum 2.90 -> 2.90
Main accept signal: the repair pass did what round 6 asked and did it at verdict level - the debt verdict is now bound to the frozen configuration in both places, the band has a decision rule, a non-test status, the registered necessity half, a resolvable label and a printed denominator whose arithmetic closes exactly against the evidence CSVs, and the flatness sentence no longer contradicts the uniqueness theorem; both deletions are provably duplication-only, and the repair's structure/length/compile declarations reproduce exactly
Main reject signal: the decisive axis is untouched - no prediction endpoint survives Holm on any block, and the paper's own mechanism contrast still shows the calibration program is not what produces the structural gain - and one half of the newly scoped debt verdict ("neither prediction drivers") is now in direct tension with the paper's own ablation table at exactly the configuration the verdict names
Confidence: 4/5 (full main text available and the repair sites read in full; exact snapshot diff and all repair numbers re-derived against the source files; supplemental/appendix not re-read; the L1-vs-L2 flatness question of F1/R5-5 remains unresolvable from the files read)
```

---

## 5. Relative-Progress Scorecard (round 6 -> current)

Historical scores are the round-6 scores, inherited verbatim from `raven-mcs-tmc-review-round6.md` §6/§9.

| # | Dimension | Historical | Current | Delta | Weight | Weighted delta | Explanation (issue IDs) |
|---|---|---|---|---|---|---|---|
| 1 | Originality / novelty | 2 | 2 | 0 | 0.10 | 0.00 | `W4` unresolved; this repair is claim-management only |
| 2 | Soundness / technical quality | 4 | 4 | 0 | 0.20 | 0.00 | `R5-2` **closed** (band rule + non-test status, L613-617); `F1` **closed** (ℓ₁ scoping, L971-976); `R5-1` **partially closed** — the scoping half is now verdict-level in both places (L232-236, L1842-1846), but the "same recursion at different weights" clause was not added and the ablation half (L2058-2060) still needs the registered necessity verdict. Deduction carried by `R5-1` ⇒ 4 stands |
| 3 | Evidence / experiments | 3 | 3 | 0 | 0.25 | 0.00 | No new experimental evidence of any kind; no endpoint contrast added or re-tested. `R5-5` unchanged in substance (the flatness scoping sharpens the *statement*, not the evidence) |
| 4 | Clarity / presentation | 3 | 3 | 0 | 0.15 | 0.00 | `R5-3` **closed** (denominator printed, L611-612); `R5-14` **closed** (every band verdict is now convertible: 0.0073/3.44 = 0.0021 matching `FULL_SEED_DECISIONS.csv:9`); `F1` **closed**; both deletions clean. But `R5-8`, `R5-10`, `F3`, `F4`, `N1` are still open and `R5-15` is only partially closed ⇒ deduction stands |
| 5 | Reproducibility | 2 | 2 | 0 | 0.10 | 0.00 | `M7` unresolved (bundle inventory L2197-2207 still does not list the ladder, band-decision or trained-rule artifacts, so the newly printed 3.44/1.32 pp values are not checkable from the stated bundle); `R5-17` unchanged |
| 6 | Significance / impact | 2 | 2 | 0 | 0.10 | 0.00 | Unchanged reachable-effect axis: no prediction endpoint is significant and the paper's own decomposition still shows the bulk of the structural headroom is closed by uniform weights |
| 7 | Related work / positioning | 3 | 3 | 0 | 0.05 | 0.00 | `W4` unresolved; not re-searched this round |
| 8 | Terminology / notation | 3 | 3 | 0 | 0.05 | 0.00 | `R5-3`/`R5-14` closed (the "closable gap" is now valued and convertible). Still open: the frozen `+0.0073` pp quantity is called "the debt recursion" (L1840-1841) while the κ=1000 quantity is a "rule" (L2078) although both are the same recursion at different weights; `R5-16`; `F2` residual at L1923 ⇒ deduction stands |

**Weighted progress delta = 0.00 ⇒ `unchanged`** under the frozen rule (|weighted Δ| < 0.05).

**Traceable score increases this round: none.** Five issues moved forward (`R5-2`, `R5-3`, `R5-14`, `R5-15`, `F1`), and every one of them was scored in round 6 as a *contributor to a deduction already taken*, not as a standalone point deduction. Closing a contributor removes part of a deduction without reversing it while a sibling issue under the same dimension remains open. The mapping is explicit:

| Dimension | Round-6 deduction was carried by | Status after round 7 | Which closures now unlock the score |
|---|---|---|---|
| Soundness | `R5-1`, `R5-2`, `F1` | `R5-2` closed, `F1` closed, `R5-1` partial ⇒ **deduction stands** | Soundness -> 5 once `R5-1`'s remaining half lands (one clause naming the κ=1000 arm and the frozen-strength contrast as the same recursion at different weights, plus the per-component necessity verdict or an explicit disclaimer at L2058-2060) |
| Clarity | `R5-3`, `R5-11`, `R5-12`, `R5-15`, `N1`, `F1`, `F3`, `F4` | `R5-3` and `F1` closed; `R5-15` partial; `R5-12` was already closed | Clarity -> 4 once `R5-8` (`Proj_{C_r}` defined at first use) and `R5-10` (label the (43) coefficients) land and `F4` is repaired; `F3` and `N1` must also be resolved or explicitly accepted |
| Terminology | `R5-1`, `R5-16`, `R5-3`, `F2` | `R5-3` closed; `R5-1` (terminology half) and `R5-16` open; `F2` reduced to one site | Terminology -> 4 once the recursion/rule naming collision and "recoverable" are disambiguated |
| Reproducibility | `M7`, `R5-17` | unchanged | Reproducibility -> 3 once the bundle inventory covers the ladder/band/trained-rule artifacts |
| Evidence | the endpoint/necessity axis | unchanged | Evidence -> 4 requires a result, not an edit |

Per the frozen continuity rule ("if an inherited issue is resolved and the revision introduces no corresponding defect … the affected dimension must not decrease"), **no dimension decreased**. The symmetric rule does not force an increase while sibling issues under the same deduction remain open.

**Traceable score decreases this round: none.**

**Issues excluded from the delta as applying to both versions** (consistent-application rule; the same set round 6 excluded):

| Issue | Why excluded |
|---|---|
| `R5-13` (abstract `6.55 %` at L87 vs body `6.885 %` at L1577) | pre-existing and present in the pre-fix snapshot; not a penalty on the revised version alone. **Corrected characterisation:** round 6 read these as "different contrasts/objects"; they are not. Both name the U-Air $\mathrm{RMSE}_{\mu}$ cost of Design (abstract L87 "on U-Air it costs $6.55\%$ of RMSE"; body L1577 "costs $6.885\%$ of $\mathrm{RMSE}_{\mu}$ … on U-Air"; Table~\ref{tab:e4_ablation} L1975 U-Air Design $\mathrm{RMSE}_{\mu} = -6.885^\ast$), so this is a plain abstract/body numeric inconsistency, not two objects |
| `R5-10` ((43) coefficients unlabelled, L2031) | pre-existing at the pre-fix snapshot; untouched |
| `R5-16` ("recoverable" at L1823/L2096/L2180 vs the headroom objects) | pre-existing; untouched |
| `N1` (key-level vs region-level `ρ_r`) | carried unchanged from round 4 |
| `W4`, `W6`, `M7`, `N2` | inherited, untouched by this repair |

**Inherited issue reconciliation:** `R5-4`, `R5-6`, `R5-7`, `R5-9`, `R5-12` stay `closed`. `W2`, `W5`, `W7`, `N3`, `M8` stay `resolved`; `W3` stays `resolved` for its core ask. `W1` stays `unresolved`. `W4`, `W6`, `M7`, `N1`, `N2` unchanged.

---

## 6. Closure Table — R5-1 … R5-17, C1, C2, F1 … F4

Status vocabulary: `closed` / `partially closed` / `open`. Every line number indexes the current 2226-line `main.tex`. Standard applied: **a label-level wording change does not close a verdict-level issue; the verdict sentence itself must be scoped.**

| ID | Status | Deciding line | Deciding quote | Note |
|---|---|---|---|---|
| `R5-1` debt magnitudes / non-contributor claim | **partially closed** | L1842-1846 (fixed) vs L2058-2060 and L2078-2082 (not fixed) | L1842-1846: "…stay inside the band of Section~\ref{subsec:equivalence_band} **at the frozen configuration ($\lambda_g=1$, $\eta=0.01$, the strength used by the frozen runs), so at that strength** debt is an auditable accounting recursion for residual under-service rather than a structural contributor". Still unqualified for the ablation: L2058-2060 "Debt has the narrowest but most consistent role: **removing it significantly increases both structural mismatches on both datasets**". Still no identity clause: L2078-2080 "The projection-with-debt rule, a new rule of this study that **sets the debt weight to $\kappa=1000$ rather than the frozen value**" | The scoping ask is **met at verdict level in both required places** (L232-236 and L1842-1846), which is the standard round 6 set. What remains: (a) round 6's second ask — one clause stating that the κ=1000 rule and the frozen-strength contrast are *the same recursion at different weights* — is absent, so the terminology collision survives; (b) the ablation at L2058-2060 reports Holm-significant structural increases for debt without the registered necessity verdict, so a reader can still read Table IV's stars as necessity (the pass states the necessity *rule* at L615-616 but never applies it to those rows) |
| `R5-2` "statistically equivalent to zero" with no test | **closed** | L613-617 | "and a contrast is read as inside the band when its paired interval lies within $\pm0.10$; a component removal is read as necessary only when that interval lies entirely beyond the band in the worsening direction, and the band itself is a practical-significance convention rather than a hypothesis test." | Both halves of the round-6 ask are now present: the decision rule (interval, not point estimate) and the non-test status. Verified against `round_v1/PREREG.md:43-44` and `round_v3/PREREG.md:97-98`. Full-text grep: `statistically equivalent` = 0 hits. |
| `R5-3` band denominator mislabelled and unvalued | **closed** | L611-612 | "That gap is $3.44$ pp of target mass on SensorScope and $1.32$ pp on U-Air (protocol~$R$ always-on) over the $20$ seeds." | Value verified against `round_v2/PHASE3_REPORT.md:77` and made checkable end-to-end: 0.922/3.44 = 0.268 = the printed G-unit point estimate, matching `round_v4/FULL_SEED_DECISIONS.csv:6` exactly. The seed block is named and the report-half family is declared non-convertible at L618-620. |
| `R5-4` failed pre-registered gates undisclosed at the point of use | **closed** | L2080, L2220-2221 | L2080: "on a rule reported as exploratory"; L2220-2221: "The projection-with-debt results use a debt weight chosen on the tuning seeds and are reported as exploratory." | Unchanged from round 6; re-verified present. |
| `R5-5` exact flatness / inertness of the (P2) group term absent | **partially closed** | L971-976 (statement); mechanism and tie-break still absent | L971-976: "…has median $10^{-13}$, so that $\ell_1$ surface is flat and its minimizer over $\mathcal{C}_r$ is not unique, and the group term selects among the solutions that are equivalent in $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ rather than among all of $\mathcal{C}_r$." | The *why* is still absent: grep for `target-empty` / a group-coverage explanation = 0 hits, and the tie-break result (`Δ_myo_tb = 1.05140` vs uniform `1.06213`, `MYOPIC_DIAG.json:20-23`) is still not cited (grep `1.05140` = 0 hits). The sentence is now narrowly scoped but still infers the group term's behaviour on the $\ell_1$ class from an $\ell_1$-only measurement; the $\ell_2$ range remains unmeasured. |
| `R5-6` (27) cited as assigning a non-contributor role | **closed** | L1845-1847 | "\eqref{eq:debt_bound} carries debt as a one-sided residual bound, not as a benefit term." | Unchanged; re-verified. |
| `R5-7` "does not amplify" beyond its metric | **closed** | L229-231 | "…is a Lipschitz perturbation of the same-window ideal reference that the calibration program does not amplify in $\boldsymbol\alpha$, per \eqref{eq:g4_alpha}." | Unchanged; re-verified. |
| `R5-8` `Proj_{C_r}(β̂)` never defined; new-rule status late | **open** | L245-246 (first use), L2084-2085 | L245-246: "the part carried by the projected reference $\mathrm{Proj}_{\mathcal{C}_r}(\widehat{\boldsymbol\beta}_r)$ and". Grep `Proj` across the file: 12 hits, none a definition. | Not touched by this repair. The status sentence remains 1,839 lines after first use. |
| `R5-9` "their oracle values" claimed band-inside, unsupported | **closed** | L1839-1841 | "The group-matching, variance, and staleness terms, the observation and usable-update factors, and the debt recursion ($+0.0073$ pp, …)" | Unchanged; the unsupported clause stays deleted. |
| `R5-10` (43) coefficients printed unlabelled | **open** | L2031 | "the two settings are indifferent when $w_c\,4.990=w_g\,6.943+w_\mu\,6.885+w_t\,7.221$, so a deployment that reads structure only keeps Design on if and only if $w_c/w_g>1.39$" | Untouched. The coefficients are the U-Air Table IV entries (`4.990` = U-Air $\Delta_{c\text{-}s}$) but the sentence still does not say so. Excluded from the progress delta as pre-existing. |
| `R5-11` abstract `1.24 %` vs contributions `+0.922 pp` | **partially closed** | L86-87 (abstract); L1575-1579 (body) | L86-87: "Design is worth $1.24\%$ of group mismatch on SensorScope at unchanged prediction, and on U-Air it costs $6.55\%$ of RMSE while improving cross-sensor mismatch by $4.99\%$." L1575-1579: "Design is worth $1.237\%$ of $\Delta_{\mathrm{group}}$ and $0.597\%$ of $\Delta_{c\text{-}s}$ on SensorScope at unchanged prediction, and costs $6.885\%$ of $\mathrm{RMSE}_{\mu}$, $6.943\%$ of $\Delta_{\mathrm{group}}$, and $7.221\%$ of tail RMSE on U-Air…" | Numbers were frozen this round, so status is unchanged from round 6. Correction of record: the body **does** print the U-Air RMSE cost (L1577), so the surviving gap is (i) the abstract sentence has no ruler and no baseline, and (ii) `6.55 %` contradicts `6.885 %` (= `R5-13`). |
| `R5-12` dangling duplicated clause in §VI-A | **closed** | L1546-1550 | "The reported predictive gains describe this construction rather than the range attainable when selection varies at the unit level, and the compounding direction is therefore part of the construction rather than a measured property of these traces, and the structural-alignment results of Table~\ref{tab:main_effectiveness} are conditional on it." | The duplicate is gone. Residual grammar defect `F4` remains in the same sentence. |
| `R5-13` `6.55 %` vs `6.885 %` | **open** (excluded from delta) | L87 vs L1577 (and Table~\ref{tab:e4_ablation} L1975) | L87: "on U-Air it costs $6.55\%$ of RMSE"; L1577: "costs $6.885\%$ of $\mathrm{RMSE}_{\mu}$ … on U-Air"; L1975: U-Air `Design` row `$-6.885^\ast$` on $\mathrm{RMSE}_{\mu}$ | Unchanged. Pre-existing in the pre-fix snapshot, so no progress delta. Correction of record: this is one object with two values, not two objects — the evidence (`tables/E4_ABLATION_HOLM_RESULTS.csv`; `PART_A_REPORT.md`) supports only `6.885`, so the abstract figure has no source. |
| `R5-14` band verdicts quoted in mixed units | **closed** | L611-612 with L1836-1837 and L1840-1842 | L611-612 prints the denominator; L1837: "outside the equivalence band in the same units ($-0.268$, $[-0.320,-0.214]$)"; L1840-1842: "the debt recursion ($+0.0073$ pp, $[0.0064,0.0083]$ …) stay inside the band…" | The missing piece round 5 and round 6 both identified was the conversion factor. It is now printed once per dataset, and both verdict classes convert consistently: design 0.922/3.44 = 0.268 (`FULL_SEED_DECISIONS.csv:6`), debt 0.0073/3.44 = 0.0021 (`FULL_SEED_DECISIONS.csv:9`, `dG_all20 = −0.002119`). Every pp verdict in §VII-C is now checkable by a reader. |
| `R5-15` band placement, no label, no disclaimer | **partially closed** | L573 (label), L613-617 (rule + disclaimer), L1842 (citation) | L573: `\label{subsec:equivalence_band}` (aux: III-F, page 5); L617: "the band itself is a practical-significance convention rather than a hypothesis test"; L1842: "the band of Section~\ref{subsec:equivalence_band}" | Two of the three round-6 asks landed (label + resolvable cross-reference from the results text; the disclaimer its weaker `+0.5 %` sibling already carried). Placement is unchanged: the band is still defined inside §III-F "Structural Alignment Objective", a modelling subsection rather than where verdicts are read, and there is still no pointer to the preregistration artifact. |
| `R5-16` "recoverable" names two headroom objects | **open** (excluded from delta) | L1823, L2096, L2180 vs L2100-2104 | L2096: "The recoverable gain is bounded inside the class the method defines"; L2101: "$H=(\mathrm{RMSE}_{\mu}(\text{FedAvg})-\mathrm{RMSE}_{\mu}(\text{oracle}))/\mathrm{RMSE}_{\mu}(\text{FedAvg})$" | Untouched. Pre-existing; excluded from the progress delta. |
| `R5-17` `M_r`-drift caveat only in the availability section | **partially closed** | L2212-2219 (improved); L608-620 and Prop. 3 still silent | L2213-2219: "…miss the replay tolerance of $10^{-9}$ used for the frozen arms, by $2\times10^{-6}$ to $3.7\times10^{-5}$ on the structural endpoint, so their closed-loop agreement is reported as a residual rather than an identity…" | No change this round. The ruler clause at L608-620 now carries a *different* ruler caveat (the report-half subset), but the `M_r`-drift cross-reference into that clause and into Proposition 3's shared-`M_r` premise is still absent. |
| `C1` Proposition 4's unused directional-derivative clause | **open** | L1361-1363 | "and along a feasible direction $d$ of the simplex, $\sum_g d_g=0$, the directional derivative is $\sum_g d_g\,\mathrm{RMSE}_g^2/(2\,\mathrm{RMSE}_{\mu})$" | Still present, still unused: the only citation of Proposition~\ref{prop:group_decomposition} (L2037-2041) uses the block decomposition, "though that decomposition covers neither $\Delta_{\mathrm{group}}$ nor $\Delta_{c\text{-}s}$". Zero space recovered. |
| `C2` Coverage-Gate apparatus supports an instrument that never acts | **open** | L486-502, L1004-1090, L1385-1431 (unchanged) | Not touched by this repair. | Zero space recovered. The `C1`/`C2` savings were the round-5 budget for the P0 text; this pass again absorbed its insertions inside 17 pp by net line reduction (−4 lines, −222 characters). |
| `F1` flatness sentence reads against Theorem 1's unconditional uniqueness | **closed** | L971-976 vs L1261-1266 | L973-976: "so that $\ell_1$ surface is flat and its minimizer over $\mathcal{C}_r$ is not unique, and the group term selects among the solutions that are equivalent in $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ rather than among all of $\mathcal{C}_r$." | The sentence no longer asserts anything about the minimizer of $J_r$, so the theorem's unconditional uniqueness claim is no longer contradicted. The residual "does the cited $\ell_1$ measurement establish what the group term selects?" question is carried by `R5-5`, not by a new finding — round 6 had already recorded it as an unresolved risk. |
| `F2` "interchangeable" names several relations | **partially closed** | L1781-1783 (fixed) vs L1923 (not fixed) | L1781-1783: "Four-block worst-group RMSE stays within the descriptive $+0.5\%$ worst-group tolerance versus FedAU-Window and ObsUse-Window…"; L1923: "…so target RMSE is interchangeable rather than a Holm-significant win." | The tolerance site is fixed and the word no longer attaches to the `+0.5 %` device. One site remains, using the paper's term of art for Proposition 1's risk functionals to mean "not statistically distinguishable". Recorded correction: round 6's third sense ("rankings", cited at pre-fix L1439) was a line-wrap misread of the deleted risk sentence — the real count was two sites, so `F2` is now one site from closure. |
| `F3` abstract `1.24 %` has no ruler and no in-body companion | **open** | L86-87 abstract; L1575-1579 body | L86: "Design is worth $1.24\%$ of group mismatch on SensorScope at unchanged prediction" | Unchanged (numbers frozen). Evidence correction: the body carries `1.237 %` (L1575) **and** the U-Air pair (`6.885 %` RMSE, `4.990 %` cross-sensor, L1577-1579), so the "no in-body companion" half of round 6's finding does not hold; what remains is the missing ruler/baseline in the abstract and the `6.55 %` mismatch (`R5-13`). |
| `F4` restored sentence contains doubled connectives | **open** | L1546-1550 | "…describe this construction **rather than** the range attainable when selection varies at the unit level, **and** the compounding direction is therefore part of the construction **rather than** a measured property of these traces, **and** the structural-alignment results…" | Unchanged. The repair pass explicitly did not apply it (the sentence lies outside the four paragraphs it was authorised to edit). Two doubled connectives and a three-clause chain. |

**Closure summary: 9 closed (`R5-2`, `R5-3`, `R5-4`, `R5-6`, `R5-7`, `R5-9`, `R5-12`, `R5-14`, `F1`), 6 partially closed (`R5-1`, `R5-5`, `R5-11`, `R5-15`, `R5-17`, `F2`), 8 open (`R5-8`, `R5-10`, `R5-13`, `R5-16`, `C1`, `C2`, `F3`, `F4`).** 23 rows total.

**Status changes since round 6:** `R5-2` partial -> closed; `R5-3` partial -> closed; `R5-14` partial -> closed; `R5-15` open -> partially closed; `F1` (new in round 6) -> closed; `F2` (new in round 6) -> partially closed; `R5-1` partial -> partial (scope half completed, identity clause still absent); all other rows unchanged. No row regressed.

**Regression check on round 6's closed set:** `R5-4`, `R5-6`, `R5-7`, `R5-9`, `R5-12` and the Table I caption fix are all still intact at the current lines; none was undone by this repair.

---

## 7. New Findings Introduced By This Repair

Severity-ranked. Provenance uses the frozen vocabulary. `Fix class` uses the skill's values. Neither finding is charged as a progress decrease (both are latent in the historical version or would penalise only the current version, which the continuity rule forbids).

| ID | Severity | Finding | Evidence | Provenance | Affected dimensions | Fix class | Owner skill |
|---|---|---|---|---|---|---|---|
| `F5` | moderate | The frozen-configuration scoping of `P0-1a`/`P0-1b` puts the **prediction half** of the scoped verdict in direct tension with the paper's own ablation at exactly the configuration the verdict names: removing instantaneous calibration worsens U-Air $\mathrm{RMSE}_{\mu}$ and Tail RMSE significantly, so "instantaneous calibration … [is not a] prediction driver" is contradicted by Table~\ref{tab:e4_ablation} | L235-236: "at the frozen configuration ($\lambda_g=1$, $\eta=0.01$, the strength used by the frozen runs), instantaneous calibration and debt are neither prediction drivers nor structural contributors" vs L1978 (U-Air `Inst` row: `+0.143^\ast` on $\mathrm{RMSE}_{\mu}$, `+0.149^\ast` on Tail RMSE) and L2056-2058: "removing Inst worsens $\mathrm{RMSE}_{\mu}$ and tail RMSE by $0.143\%$ and $0.149\%$ (both $p_{\mathrm{Holm}}=0.0194$)" | `previously_undetected` (the tension exists in both versions; the repair's explicit scope now binds the verdict to the configuration where the contradiction is observable, so the reader meets it directly) | Soundness, Clarity | writing | `ccf-paper-writer` |
| `F6` | minor | The new caveat introduces the term "read-only ladder contrasts" with no definition, 1,459 lines before its only other use, and the paper contains no ladder table or description of that family | L618: "Read-only ladder contrasts instead use the report-half subset…"; L2077: "the value the read-only ladder above also gives". Full-text grep for `ladder` = these 2 hits only; no ladder table, figure or arm list exists in the paper | `previously_undetected` (latent — L2077's dangling reference pre-dates the repair) with a newly added earlier use at L618 | Clarity, Terminology | writing | `ccf-paper-writer` |

**Not new findings, recorded for completeness.** (i) The double `\label` on one subsection (L572-573) is legal and both labels resolve; the band label resolves to III-F/page 5. (ii) `EA-1`'s residual (comparing 0.0141 % to a disclaimed foreign tolerance) is a stylistic residual of a fix that removed the decision-ruler framing, not a defect class round 6 raised. (iii) The audit's Theorem-2 / L1249-1254 anchor slip is a documentation error in the repair report, not in the manuscript (`R5-3`, `R5-14`, `F1` all verified against primary evidence). (iv) No numbering drift: `\begin{equation` 37, `\begin{proposition` 4, `\begin{theorem` 2, `\begin{table` 4, `\begin{figure` 4, `\cite{` 42 and `main.aux` 97 `\newlabel` with 0 `??` mean no cross-reference was broken by the label insertion.

---

## 8. Absolute-Readiness Scorecard (current version only)

| # | Dimension | Current /5 | Confidence | Deduction basis and raise condition |
|---|---|---|---|---|
| 1 | Originality | 2 | high | Combination-and-scenario novelty; the nearest two-stage IPW work already contains the key structure (`W4`, unchanged). Raise: complete the FedIPW/FedPALS variable-constraint-information mapping and prove an irreducible difference |
| 2 | Soundness | 4 | high | Deduction: `R5-1` remains partially closed — the verdict is now correctly scoped (L232-236, L1842-1846) but the κ=1000 identity clause is absent and the ablation's Holm-significant structural increases at L2058-2060 are not resolved against the registered necessity rule; `F5` adds a live contradiction on the prediction half of the same verdict. Credit: `R5-2`, `R5-4`, `R5-6`, `R5-7`, `R5-9` and `F1` are closed, the band now has a registered decision rule with an authoritative source, and no proof error was found. Raise: one clause naming the κ=1000 arm and the frozen-strength contrast as the same recursion at different weights, plus either the per-component necessity verdict or an explicit non-necessity disclaimer, plus `F5`'s one-clause narrowing — all text-only |
| 3 | Evidence | 3 | high | Deduction: still no prediction-endpoint contrast that survives Holm on any block (L2086-2090: SensorScope $p_{\mathrm{Holm}}=1.000$; U-Air best raw $0.027$, $p_{\mathrm{Holm}}=0.133$), and the paper's own decomposition shows the projection alone carries the structural gain while the group/variance/staleness terms sit inside ±0.10 (`FULL_SEED_DECISIONS.csv:4,5,8`). Raise: one endpoint with an externally meaningful win, or a task where structure converts to prediction |
| 4 | Clarity | 3 | high | Deduction: `R5-3` and `R5-14` are now closed, but `R5-8` (`Proj_{C_r}(β̂)` undefined at L245-246), `R5-10` (unlabelled (43) coefficients, L2031), `F4` (doubled connectives, L1546-1550), `F3` (abstract without a ruler) and `N1` remain open, `R5-15` is partially closed (band still defined in a modelling subsection), and `F6` adds one undefined term. Credit: the two deletions are clean and provably duplication-only, and the band paragraph is now self-contained. Raise: define `Proj_{C_r}` at first use, label the (43) coefficients, define the ladder family, repair `F4` — four clauses |
| 5 | Reproducibility | 2 | medium | `M7` unresolved: `RAVEN_MCS_PUBLIC_REPRO_R1` (L2197-2207) still lists only seeds, targets, EventTraces, table sources, `SCD_PHI.csv`, canonical Table II, the worst-group Holm family, slice relatives and the hybrid-ranking CSVs — no round-v2/v3/v4 ladder, band-decision, debt-strength or trained-rule artifact. The newly printed 3.44/1.32 pp values therefore cannot be checked from the stated bundle. `R5-17` partially closed. Raise: refresh the bundle and extend its inventory |
| 6 | Significance | 2 | medium | Unchanged. The reachable large effect is still the single Design ablation; the structural headroom is unchanged and the paper's own decomposition still shows the bulk of it is closed by uniform weights. Raise: a task where target-mass alignment changes a decision, not a diagnostic |
| 7 | Related work | 3 | medium | Reasonable positioning; `W4` unresolved and not re-searched. Raise: the irreducibility mapping |
| 8 | Terminology | 3 | high | Deduction: the frozen `+0.0073` pp quantity is still called "the debt recursion" (L1840-1841) while the κ=1000 quantity is a "rule" (L2078); "closable gap" is now correctly named **and valued** (credit: `R5-3`/`R5-14` closed); "recoverable" still names two headroom objects (L2096 vs L2101); `F2` residual at L1923; `F6` adds an undefined "read-only ladder". Raise: three one-line disambiguations |

**Weighted readiness sum = 2.90** (`0.10×2 + 0.20×4 + 0.25×3 + 0.15×3 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×3`; round 6: **2.90**; round 5: **2.90**; round 4: **3.05**). **Overall score: 5/10, threshold 4/10** — borderline negative, weak-reject band upper edge.

**Why the overall is unchanged at 5/10 and not raised.** Five issues moved forward and three of them closed outright, which is real progress in claim management; but every one of them was a contributor to a deduction that a sibling open issue still carries, so **no dimension can rise** under the continuity rule, and the weighted sum is therefore identical at 2.90. The calibrated stance follows the strongest *unresolved decision-relevant* weakness, and that weakness is on the evidence axis (weight 0.25), which this repair did not touch. The concrete arithmetic of what the closures unlock: if `R5-1`'s remaining half lands and `R5-8`/`R5-10`/`F4` are repaired, Soundness -> 5 and Clarity -> 4, and the weighted sum rises to **3.25**; the overall would then sit at the very top of the borderline band, and moving it to 6/10 would still require the evidence axis to move.

**The single strongest unresolved decision-relevant weakness that keeps the overall where it is.** The paper's own mechanism contrast still shows that the calibration apparatus it is built around — the group-matching, variance and staleness terms of (P2), and the debt recursion at its frozen strength — is not what produces the structural gain; the gain is carried by projecting the reconstructed reference onto the feasible set (`FULL_SEED_DECISIONS.csv:2` gives the projection $+0.768$ pp against uniform, while `:4`, `:5`, `:8`, `:9` put every other term inside ±0.10). Combined with the absence of any significant prediction endpoint, the paper's central artefact is still not shown to be necessary for the effect it is credited with. Everything else in this report is a sentence-level fix; this one needs an endpoint result or a demonstrated necessity argument (feasibility, accounting, or variance control) that the paper does not currently measure.

**Remaining blocking evidence (by weight).**
1. **Evidence (0.25):** one endpoint where alignment converts to prediction, or an externally meaningful task.
2. **Soundness (0.20):** finish `R5-1` (κ identity clause; necessity verdict or disclaimer at the ablation) and narrow `F5`'s prediction clause.
3. **Clarity (0.15):** define `Proj_{C_r}` at first use (`R5-8`); label the (43) coefficients (`R5-10`); define the ladder family (`F6`); repair `F4`.
4. **Reproducibility (0.10):** extend the bundle inventory to the ladder/band/trained-rule artifacts (`M7`).

---

## 9. Confidence And Comparability

**Confidence: 4/5** (`high but not full`). Reported separately from both scorecards per `version-comparison.md`.

- **What supports the 4.** The current `main.tex` was diffed exhaustively against `snapshots/2026-10-03-pre-design-fix/main.tex` (9 hunks, 29 insertions / 33 deletions) and every claimed edit was read at its current location; all seven substantive repair numbers were re-derived from the source files rather than taken from the repair's own audit (`PHASE3_REPORT.md:77` for 3.44/1.32 pp; `FULL_SEED_DECISIONS.csv:6,9` for 0.922 pp / −0.268 dG and 0.0073 pp / −0.0021 dG; `PHASE4_INPUT_GAPS.md:72` and `ERRATA_v2.md:55` for λ_g=1 and η=0.01; `round_v1/PREREG.md:43-44` and `round_v3/PREREG.md:97-98` for the band rule and the necessity direction; `EXECUTION_REPORT.md:118` for the report-half Δ* pair). The structure counts, em-dash count, page count and compile state were re-measured on the current file, the pre-fix snapshot and the pre-v4 snapshot independently; the label resolution was read out of `main.aux`.
- **What holds it below 5.** (i) `appendix.tex`/`supplemental.pdf` was not re-read, so the L1-versus-L2 flatness question behind `R5-5` cannot be settled from the files read — `MYOPIC_DIAG.json` measures the ℓ₁ surface only, and whether the ℓ₂ group term is equally flat is not determinable without the `‖M_rα − μ‖₂` range or the appendix uniqueness argument. (ii) The public repro bundle's contents were not verified, and it does not appear to contain the ladder/band/trained-rule artifacts, so the newly printed denominators are checkable from the repository but not from the released bundle. (iii) No experiment was re-run. (iv) This round read the repair sites, the full diff and the argument-bearing sections in depth, but did not re-read all 2,226 lines paragraph by paragraph; the round-6 read is relied on for unchanged regions.
- **Comparability.** The contract is unchanged (`TMC-J-R4`, identical weights, anchors and threshold as rounds 4-6). The comparison is clean: `\begin{table` (4), `\begin{figure` (4), `\begin{equation` (37), `\cite{` (42), `\section{` (8), `\subsection{` (29), `\begin{proposition` (4) and `\begin{theorem` (2) are identical across the pre-v4, pre-fix and current files, and the only moved count is `\label{` 96 -> 97, which the repair declared in advance and which is exactly the one added label. So no numbering-drift discount applies. The residual comparability caveat is the one rounds 5-6 disclosed: historical scores are inherited rather than recomputed, and the round-4 report is in Chinese while rounds 5-7 are in English with dimension identity preserved one-to-one.

---

## 10. Questions For Authors (updated)

1. At the frozen configuration, removing instantaneous calibration worsens U-Air $\mathrm{RMSE}_{\mu}$ and Tail RMSE at $p_{\mathrm{Holm}}=0.0194$ (Table~\ref{tab:e4_ablation}). How is that consistent with "instantaneous calibration … [is not a] prediction driver" at the same configuration (L235-236)?
2. What distinguishes "the debt recursion" from "the projection-with-debt rule" other than the weight $\kappa$, and can one clause say so at L2078-2082?
3. Which family do the band verdicts at L1839-1845 belong to — the 20-seed `FULL_SEED_DECISIONS` rows or the report-half ladder? Themselves they convert correctly against the printed 3.44 pp, but the paper's new caveat leaves the assignment implicit.
4. Is the ℓ₂ group term of (P2) as flat as the ℓ₁ surface measured at L971-976? If not, on what measurement does "the group term selects among the solutions that are equivalent in $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$" rest?
5. Is `Proj_{C_r}(β̂)` defined anywhere, and can its definition move to its first use at L245?
6. Where does the abstract's `6.55 %` U-Air RMSE cost come from, given that L1577 and Table~\ref{tab:e4_ablation} both give `6.885 %` for that object?

---

## 11. Remaining Work List (ordered, smallest useful next actions)

| # | Priority | Action | Owner skill | Input needed | Why it is the right next action |
|---|---|---|---|---|---|
| 1 | P0 | Add one clause at L2078-2082 stating that the κ=1000 rule and the frozen-strength contrast are the same recursion at different weights, and one clause at L2058-2060 giving the registered necessity verdict (or an explicit "not a necessity test") for the debt row | `ccf-paper-writer` | `FULL_SEED_DECISIONS.csv:9`; `round_v1/PREREG.md:43-44`; L2078-2082 | Closes `R5-1`, the only issue still carrying the Soundness deduction (weight 0.20) |
| 2 | P0 | Narrow the prediction half of the L232-236 verdict, e.g. "neither a structural contributor nor a driver of any headline prediction result" — or state the U-Air Inst effect it must be read against | `ccf-paper-writer` | L235-236; L1978; L2056-2058 | Removes the one contradiction this repair introduced into the reader's path (`F5`); one clause |
| 3 | P1 | Define `Proj_{C_r}(β̂)` at L245 and label the (43) coefficients as U-Air Table IV entries at L2031; repair `F4` at L1546-1550 | `ccf-paper-writer` | L245-246; L2031; L1546-1550; `\eqref{eq:Cr}` | Three clauses that close `R5-8`, `R5-10` and `F4` and are the remaining carriers of the Clarity deduction (weight 0.15) |
| 4 | P1 | Define the "read-only ladder" family once, at L618 or at its first results use (`F6`) | `ccf-paper-writer` | L618; L2077; `FULL_SEED_LADDER.csv` | The new caveat is load-bearing for `R5-3`/`R5-14`; one clause makes it usable |
| 5 | P1 | Extend `RAVEN_MCS_PUBLIC_REPRO_R1` (L2197-2207) to cover the round-v2/v3/v4 ladder, band-decision, debt-strength and trained-rule artifacts, pinned by hash | `ccf-integrity-auditor` | bundle contents; `results_w1_ladder/round_v2|v3|v4` | Closes `M7`, the whole of the Reproducibility deduction (weight 0.10), and makes the newly printed denominators auditable from the bundle |
| 6 | P1 | Add the missing mechanism half of `R5-5`: state that the covered per-window group coordinates are target-empty on these supports, and cite the `Δ_myo_tb` tie-break | `ccf-paper-writer` | `ERRATA_v2.md:35`; `EXECUTION_REPORT.md:134`; `MYOPIC_DIAG.json:20-23` | Converts the now-correctly-scoped flatness fact into the explanation §VII-E/F needs; two sentences |
| 7 | P2 | Reconcile the abstract's `6.55 %` with the body/table `6.885 %`, and add the ruler/baseline the abstract's `1.24 %` lacks (`R5-13`, `F3`, `R5-11`) | `ccf-paper-writer` | L86-87; L1575-1579; `tables/E4_ABLATION_HOLM_RESULTS.csv` | Pre-existing, so it carries no progress credit — but it is the last numeric inconsistency in the abstract |
| 8 | P2 | Buy the space for all of the above: delete Proposition 4's unused directional-derivative clause (`C1`, ~3 lines) and move the coverage-Gate propositions/corollaries to the artifact (`C2`, ~35-45 lines) | `ccf-paper-writer` | L1361-1363; `appendix.tex` | Both items are still fully open and are the only remaining free space in a 17-pp paper |
| 9 | P2 | FedIPW/FedPALS variable-constraint-information mapping for the novelty boundary | `ccf-literature-searcher` | morishita2026who, listozec2024overcoming, goetze2025floss full texts | Closes `W4`; the only route to movement on Originality (0.10) and Related work (0.05) |

---

## 12. Score Revision Criteria (version-comparison fields included)

```text
Raising the score would require: the two P0 items above (R5-1's remaining half + F5's narrowing) plus the three P1 clauses (R5-8, R5-10/F4, F6); those move Soundness to 5 and Clarity to 4 and lift the weighted readiness sum from 2.90 to about 3.25 with no new experiment. Movement of the overall stance above 5/10 requires the evidence axis (0.25).
Lowering the score would be triggered by: a reviewer reading Table IV's debt/Inst rows against the L232-236 verdict as an unresolved contradiction (F5) without the narrowing; the printed 3.44 pp denominator failing an independent re-derivation (it does not - it reproduces exactly against FULL_SEED_DECISIONS.csv:6,9); or the report-half/20-seed distinction being shown to have been applied to the wrong rows somewhere in §VII-C.
Concerns unlikely to change before submission: W4 (FedIPW/FedPALS irreducibility); M7/W6 (bundle refresh); a task where target-mass alignment changes a decision.
Relative progress: weighted delta 0.00 => unchanged (threshold 0.05); 9 closed (R5-2, R5-3, R5-4, R5-6, R5-7, R5-9, R5-12, R5-14, F1), 6 partially closed (R5-1, R5-5, R5-11, R5-15, R5-17, F2), 8 open (R5-8, R5-10, R5-13, R5-16, C1, C2, F3, F4); no traceable increase, no traceable decrease
Absolute readiness: weighted sum 2.90 (unchanged from rounds 5-6; round 4 was 3.05), stance 5/10 held (threshold 4/10); held because no dimension may rise while a sibling issue under the same deduction stays open, and the decisive axis (Evidence, 0.25) is untouched
Confidence and comparability: 4/5; contract unchanged (TMC-J-R4); historical scores inherited verbatim from the round-6 report; all structural counts identical to the pre-v4 and pre-fix snapshots except the declared label 96 -> 97, so no numbering-drift discount applies; residual caveat is the round-4 Chinese vs rounds 5-7 English dimension-identity mapping
New issue provenance: F5 = previously_undetected (latent in both versions; the P0-1 scoping makes it observable at the named configuration); F6 = previously_undetected (latent at L2077) with a newly added earlier use at L618
Traceable score decreases: none
Traceable score increases: none (the five moved issues were contributors to deductions that sibling open issues still carry)
```

---

## 13. Checks Run, Checks Skipped, Unresolved Risks

```text
Checks run: full unified diff of snapshots/2026-10-03-pre-design-fix/main.tex vs the current file (9 hunks, 29 insertions/33 deletions) with every hunk classified against the P0/EA claim list and the two deletions; all seven substantive repair numbers re-derived from primary evidence (PHASE3_REPORT.md:77; FULL_SEED_DECISIONS.csv:6,9; PHASE4_INPUT_GAPS.md:72; ERRATA_v2.md:55; round_v4/PREREG.md:52; round_v1/PREREG.md:43-44; round_v3/PREREG.md:97-98; EXECUTION_REPORT.md:118); structural counts re-measured on current, pre-fix and pre-v4 files (nine counts identical, \label 96 -> 97); em-dash count (0); main.log parse (17 pages, 886558 bytes, 0 Overfull, 21 Underfull, 0 "!" lines, 0 undefined); main.aux parse (97 \newlabel vs 97 \label, 0 "??", \newlabel{subsec:equivalence_band} -> III-F/page 5, aux mtime after tex); full-text greps for statistically equivalent (0), Proj (12, no definition), ladder (2), target-empty (0), 1.05140 (0), 6.55/6.885, 3.44/1.32, interchangeable (all uses classified by sense), statistically-equivalent, ties all six (line-wrapped survivor at L1801-1802), advantage against five (0 — replaced by five named baselines); deletion retention traced statement by statement to surviving lines; length accounting reproduced (2230 -> 2226 lines, -27 words, -222 characters); re-derivation of the weighted readiness sum and the weighted progress delta
Checks skipped: line-by-line read of appendix.tex / supplemental.pdf; independent re-run of any experiment; verification of the public repro bundle contents; external related-work search; the L1-vs-L2 flatness comparison needed to settle R5-5 fully
Unresolved risks: (i) F5's severity depends on whether "prediction driver" is read as a statistical claim (then it is contradicted by the U-Air Inst row) or as a headline-result claim (then it is defensible but unexplained); (ii) whether the L2 group term of (P2) is as flat as the measured L1 surface, which MYOPIC_DIAG.json does not measure; (iii) the printed 3.44 pp is consistent with the frozen-arm/decision rows (verified exactly for the design and debt rows) but the paper does not label which family each §VII-C verdict belongs to, so a reader must rely on the non-convertibility caveat; (iv) the B-G2 partial status and the A2 gate's reason remain undisclosed, though the exploratory labelling neutralises the over-read R5-4 was about; (v) the repair's declared edit list is exhaustive this round, unlike round 6
```

---

## 14. Output Self-Check

1. Section order follows the round-6 report's structure and `fixed-output-format.md`, with the verification at §2, the two scorecards at §5/§8, the closure table at §6 and the new findings at §7. **Pass.**
2. Two scorecards are separate, computed under one frozen contract, and never fused. **Pass.**
3. Every score at or below 3 carries a concrete deduction and a raise condition. **Pass.**
4. Each claimed repair (P0-1a, P0-1b, P0-2, P0-3a, P0-3b, EA-1, EA-2) is verified against the pre-edit snapshot with a quoted current line, a verdict, and — where the fix carried a number — a named source file and line. **Pass** (§2).
5. Both deletions are verified statement by statement against surviving lines; no deleted content is unaccounted for. **Pass** (§2).
6. Structure counts match the pre-v4 snapshot except `\label{` 96 -> 97, which the repair declared; em dashes 0; 17 pp; 0 errors / 0 undefined / 0 overfull. **Pass** (§2).
7. No traceable score increase and no traceable score decrease is asserted without naming the issue IDs that decide it; the closures-to-scores mapping is tabulated. **Pass** (§5).
8. Pre-existing issues (`R5-13`, `R5-10`, `R5-16`, `N1`, `W4`, `W6`, `M7`, `N2`) are explicitly excluded from the progress delta, and `F5`/`F6` are excluded as latent-in-both-versions. **Pass** (§5, §7).
9. Every new finding carries severity, evidence, provenance, affected dimensions, fix class and owner skill. **Pass** (§7).
10. Confidence is reported separately with its reasons, and comparability is reported as a third field rather than a score dimension. **Pass** (§9).
11. No acceptance probability is stated; no score is rounded. **Pass.**
12. No file other than this report exists as a product of this review; all temporary analysis files were removed and the pipeline was not run. **Pass.**
