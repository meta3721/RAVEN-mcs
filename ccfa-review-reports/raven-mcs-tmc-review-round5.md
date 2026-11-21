# RAVEN-MCS — IEEE TMC Review, Round 5 (version-comparison, formalization-focused)

```text
Review date: 2026-10-03
Target venue/year/track: IEEE Transactions on Mobile Computing, journal revision; method + measurement long paper
Paper title: RAVEN-MCS: Target-Mass-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex (2235 lines, 17 pp, 0 errors / 0 undefined / 0 overfull)
  TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex (2611 lines; compiled into supplemental.pdf, 16 pp)
  TO_OVERLEAF_paper_tmc_r1_clean/main.aux (authoritative numbering), main.log, supplemental.log
  snapshots/2026-10-03-pre-v4-contribution/main.tex (2294 lines) — pre-revision snapshot
  results_w1_ladder/round_v2/{PHASE3,PHASE4,PHASE5,EXECUTION}_REPORT.md
  results_w1_ladder/round_v3/{EXECUTION_REPORT,DEBT_RECURSION,ERRATA_v2}.md
  results_w1_ladder/round_v4/{PREREG,PART_A_REPORT,PART_B_REPORT,ERRATA_v3}.md
  ccfa-review-reports/raven-mcs-tmc-review.md (round-4 report; frozen rubric + historical scores)
Search basis: no new external search this round (see §4)
Report file: ccfa-review-reports/raven-mcs-tmc-review-round5.md
Reviewer mode: version-comparison, centrepiece = global impact of the manuscript's formalization
Manuscript version / comparison range: round-4 manuscript (frozen at ccfa-review-reports/raven-mcs-tmc-review.md) -> current 17-pp revision that incorporates the v3/v4 evidence rounds
Frozen comparison contract ID: TMC-J-R4 (inherited verbatim from the round-4 report §1; see §1)
```

**Naming-convention note (skill rule 8).** `ccf-paper-reviewer` rule 8 asks for one canonical `ccfa-review-reports/` report rather than a dated copy per iteration. The requesting agent explicitly asked for a separate round-5 file with the round-4 file preserved as the historical artifact, so this file is the round-5 canonical report and `raven-mcs-tmc-review.md` is deliberately left untouched as the frozen historical record.

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

**Rubric deviation, stated explicitly:** the round-4 report used a project-frozen 8-dimension rubric whose dimension names are *Originality/novelty, Soundness/technical quality, Evidence/experiments, Clarity/presentation, Reproducibility, Significance/impact, Related work/positioning, Terminology/notation*. That is **not** the skill's default 8-dimension set (which ends in *Ethics/limitations*). Per instruction, this round keeps the round-4 names and weights, and this report is written in English whereas round 4 was written in Chinese; dimension identity is preserved one-to-one so the deltas remain comparable.

**Materials asymmetry disclosed:** the round-5 historical scores are *inherited verbatim* from the round-4 report §2/§5 and were not recomputed; the anchor evidence for every historical score is quoted in that file. Only the current version was rescored.

---

## 2. Desk-Rejection Assessment

- Paper length: **pass** — 17 pp main + 16 pp supplemental; `main.log` reports `Output written on main.pdf (17 pages)`. No page-budget violation.
- Topic compatibility: **pass** — federated mobile crowdsensing completion under non-random selection is squarely TMC.
- Minimum quality: **pass** — full proofs, pre-registered statistics, artifact inventory, explicit null results.
- Policy/anonymity/compliance: **pass** — author block is `****`-masked as expected for review; public datasets cited with DOIs/terms.
- Prompt injection / hidden manipulation: **pass** — no instruction-like text found in the manuscript or evidence files.
- Ethics and reviewability: **pass with note** — no human-subjects or PII content; the paper states at L2169-2170 that "Federated learning itself does not provide a privacy guarantee."

---

## 3. Paper Summary And Contribution Map

**Summary.** RAVEN-MCS reframes windowed-asynchronous federated MCS completion as *deployment-target mass alignment*. The server updates once per window from usable client updates; a selection-corrected reference is formed from legal pre-outcome opportunity/observation/usable-update histories (RAVEN-Design) or left uncorrected (RAVEN-NoDesign, `ζ̂ = 1`); the reference is then calibrated inside the current feasible aggregation set `C_r` by a strongly convex program (P2) that carries a long-term group target-debt vector `Q_r`.

**Claimed problem.** Arriving federated updates are selected by mobility, observation and usable-delivery, so the arrival law need not match the public deployment law; optimizing arrival risk can optimize the wrong population risk.

**Claimed gap.** Sparse-MCS completion, asynchronous federated completion and participation-aware FL each address part of this, but do not formulate deployment-target risk under sequential sensing-side selection (L132-147).

**Contribution / evidence map.**

| # | Contribution | Main-text anchor | Evidence | Formal support |
|---|---|---|---|---|
| 1 | Deployment-target risk semantics; risks not interchangeable | L184-195; L501-566 | NSW risk-interchangeability experiment, `D_aligned` = −0.0209…−0.0214, 17-18/20 seeds negative, `p` = 4.83e-4…5.86e-4 (L1656-1663) | Proposition 1 (L1145), proof appendix L146-231 |
| 2 | Selection-layer-aware target reconstruction | L197-217; L639-855 | Rung ladder: `B1 = Proj_{C_r}(β̂)` strongest; `ζ` necessary, +0.922 pp [0.721, 1.141] on SensorScope, not identifiable on U-Air (L1833-1842) | Proposition 2 (L1194), proof appendix L232-606 |
| 3 | Feasibility-aware instantaneous + long-term calibration | L219-234; L857-1034 | T1 recursion exact 80/80; C3 bound 240/240, ratio 0.717-0.821, min margin 0.2492 | Theorem 1 (L1243), Proposition 3 (L1279), `eq:debt_bound` (27) at L924-933 |
| 4 | Attribution of the structural gain against a uniform-weight ruler | L236-253; L1818-1847 | FedAvg gap 2.09 pp = 1.44 (68.96 %) + 0.65 pp; U-Air 1.47 = 1.22 (83.07 %) + 0.25 pp. Registered `±0.10` G-unit band | `eq:debt_bound` (27); Proposition 4 (L1335) for the switch decomposition |

**Evidence package.** Two protocol-constructed development blocks (SensorScope, U-Air) under always-on `R` with constructed `O`/`U` (L1532-1547); a T-Drive taxi replay with real `R` (L1704-1713); NSW four-region, City Scanner `PM_{2.5}` and Pilot 2 rankings (supplemental); a risk-interchangeability block; a no-harm balanced control; a 20-seed rung ladder with a pre-registered equivalence band; three retrained server-weight rules (120 runs); a recoverable-gain ceiling with a GO rule that did not fire (L2110-2111).

**Stated limitations.** `O`/`U` protocol-constructed except Pilot 2 measured `O` (L1532-1534, L2195-2196); usable-update correction has no isolated significant effect (L2058-2062); debt is internal accounting (L2073-2075); no ranking jointly measures `R`, `O`, `U` (L93, L2198); A6a fails on both datasets so Proposition 3 is used in its `ε_stab` form (L2161-2164); the repro bundle "is not a pinned retraining archive" (L2216-2218).

---

## 4. Search And Related-Work Basis

```text
Queries used: none this round
Sources searched: repository artifacts only (manuscript, appendix, aux/log, snapshots, results_w1_ladder rounds v2-v4, round-4 review report)
Closest works found: not re-searched this round; round-4 carried FedIPW (morishita2026who), FedPALS (listozec2024overcoming), FLOSS (goetze2025floss), FedAU (wang2024lightweight) as the nearest neighbours, as cited at main.tex L314-323
Unverified related-work risks: W4 (novelty boundary vs FedIPW/FedPALS) remains unresolved and was NOT re-verified in this round
Source-quality screening status: not performed; no new citation was checked against its source
```

Honest statement: this round deliberately spent its budget on the formalization and the new evidence rounds, not on positioning. Any novelty statement in this report is therefore a *carry-over*, not a fresh judgement.

---

## 5. Expected Review Outcome

```text
Expected outcome: weak reject, upper edge (5/10); unchanged stance, weighted readiness sum down 3.05 -> 2.90
Main accept signal: the evidence round is real, pre-registered and honestly reported; formal claims are correctly scoped; every headline number I re-derived from the artifacts transcribed exactly
Main reject signal: no prediction-endpoint win anywhere, and the paper's own new evidence now shows the full calibration apparatus is unnecessary for the structural gain it is credited with - while two of its own paragraphs contradict each other about debt
Confidence: 4/5 (full main text + targeted appendix proofs + all four evidence rounds read; supplemental not re-read line by line; band denominator inferred, not stated)
```

---

## 6. Strengths And Weaknesses

### Strengths (each anchored)

1. **Number fidelity is exact.** Every headline number I checked reproduces from the artifacts: FedAvg gap 2.09 pp = 1.44 + 0.65 pp (L1824-1827 vs `round_v3/EXECUTION_REPORT.md:33,38`); U-Air 1.47 = 1.22 + 0.25 (L1827-1829 vs `:36,38`); `ζ` +0.922 pp [0.721, 1.141] (L1839 vs `round_v4/PART_A_REPORT.md:38`); projection +0.768 pp / +0.286 pp (L1835-1838 vs `PART_A_REPORT.md:34`); the six ladder values at L2082-2084 match `FULL_SEED_LADDER.csv`; the `κ` interior optimum at 1000 (L2077-2097 region vs `PART_A_REPORT.md:45-48`).
2. **Retractions were absorbed, not buried.** `ERRATA_v3` R1 withdrew "B1 closes ~25 % of the gap" on U-Air; the manuscript now says "+0.286 pp ([0.098,0.471]) on U-Air, below that line and unstable across the halves (+0.170 tune, +0.402 report)" (L1837-1838) — the same two half-values as the errata.
3. **Negative results are stated as negative.** "The GO rule, frozen before the runs, required some condition to reach `H ≥ 0.5 %` with a positive interval lower bound, and it did not fire" (L2110-2111); "No prediction-endpoint contrast survives Holm correction on either dataset" (L2093-2095); "we claim no best worst-group method" (L1808-1809).
4. **Mechanism attribution is correct at the top level.** L1833-1835 "The projected reference carries that reference-side part, and the design factor is the only further component that survives", and L1924-1925 "the surviving part is carried by the projected reference" — this is exactly what the ladder shows (`round_v3/EXECUTION_REPORT.md:83,116`).
5. **The formal claims are scoped against their own evidence.** L1907-1918 and L2161-2164 correctly state that Proposition 2 proves moment recovery, not `R_μ` optimisation, and that A6a fails on both datasets so Proposition 3 is used in its `ε_stab` form.

### Weakness records (skill format)

**Weakness W-a: the paper states two irreconcilable magnitudes for "the debt recursion" and carries the stronger one into the conclusion.**
- Evidence basis: L1842-1847 "the debt recursion (+0.0073 pp, [0.0064,0.0083], on SensorScope and +0.0024 pp on U-Air) stay inside that band, so debt is an auditable accounting recursion for residual under-service rather than a structural contributor" versus L2081-2090 "the group endpoint orders the same way on both datasets, with the projection-with-debt rule lowest ... the debt recursion adds +1.347 pp and +0.580 pp (Holm ≈1e-5 on both)". Round-v4 `PART_A_REPORT.md:25` (+0.0073 pp, "带内") and `PART_B_REPORT.md:82` ("`proj_beta_debt` 相对 `proj_beta` 再增益 +1.35 pp（SS）/ +0.58 pp（UA）") are the two different sources.
- Reviewer deduction: a reader cannot tell that these are different contrasts (frozen-`λ_g`=1, `η`=0.01 term vs a newly retrained, `κ`=1000-weighted rule). Converted into the band's own G-units the second is ≈0.39 (SS) and ≈0.44 (UA), i.e. roughly four times the registered ±0.10 band — so within one section the paper says debt is inside a null band and simultaneously reports a debt effect far outside it.
- Required fix: name the two contrasts distinctly and scope the "not a structural contributor" claim to the frozen configuration, in both places and in contributions L231-234 and conclusion L2197.

**Weakness W-b: the registered ±0.10 band is over-read as a statistical equivalence test.**
- Evidence basis: L246-247 "which is statistically equivalent to zero inside a pre-registered ±0.10 band of the closable gap"; the same reading recurs at L1842-1845 and L1925-1926. In the evidence package no equivalence procedure exists (no TOST, no `α`, no interval-inclusion rule; `round_v4/PREREG.md:24` states only "G 单位 + pp（0.5 pp）双线"), and the band-inside rows' intervals **exclude zero**: SS `B2−B1` ΔG = +0.039 [+0.013, +0.063]; SS `L6−L5` ΔG = −0.0021 [−0.0024, −0.0019]; SS `p` ΔG = −0.015 [−0.030, −0.001] (`PART_A_REPORT.md:23,25,26`). The paper elsewhere is careful in the opposite direction: for the weaker `+0.5 %` tolerance it writes "The tolerance is descriptive rather than a formal non-inferiority test" (L1632-1633).
- Reviewer deduction: "statistically equivalent to zero" is not what the artifact supports; what it supports is "the paired interval lies inside ±0.10 in G-units", which for at least the `L6−L5` row is a *detected but small* effect. Because the paper disclaims the better-documented convention and over-claims the less-documented one, the asymmetry is itself a credibility signal.
- Required fix: replace "statistically equivalent to zero" with interval-containment wording, and state the band's decision rule and its status as a practical-equivalence band rather than a test.

**Weakness W-c: the band's unit is mislabelled and its denominator is never valued.**
- Evidence basis: L605-608 "in units of the closable gap between uniform weighting and the projected reference, at the same active set, the same `M_r`, the same `C_r`, and with all windows known in advance; the pre-registered equivalence band is ±0.10 in those units." But the printed conversion at L1839-1840 (`+0.922 pp` ↔ `−0.268`) implies a denominator of 3.44 pp, which is the SensorScope distance from uniform weights to the **same-support hindsight-optimal** reference (`round_v2/PHASE3_REPORT.md:77`: "只有 `(Δ_unif − Δ*)/2 = 3.44 pp` 可回收"), not uniform→projected reference, which is 0.768 pp (L1835, and 0.922/0.768 = 1.20, not 0.268). Neither the closable gap's value nor the `1.32 pp` U-Air counterpart appears anywhere in `main.tex` (verified by full-text search).
- Reviewer deduction: read literally, the manuscript's own G-unit number is wrong by 4.5×; read charitably, the definition points at an object the paper never reports, so no band verdict can be converted into pp by a reader.
- Required fix: name the denominator (`Δ_unif − Δ*`, same active set/`M_r`/`C_r`, all windows known) and print its pp value once for each dataset.

**Weakness W-d: failed pre-registered gates behind the new numbers are not disclosed where the numbers are reported.**
- Evidence basis: L2077-2097 reports the `κ`=1000 rule and the `+1.347`/`+0.580` pp increments as results. The artifacts record that (i) the A2 projection gate failed — `PART_A_REPORT.md:59,77`: "α L∞ 差 = 3.34e-08 > 1e-8" → "A2 的 κ 数值只作探索性读数"; and (ii) Part B's own gates failed — `PART_B_REPORT.md:17,18,21`: `proj_beta` 0/40 with max residual 2.0e-6 (SS)/3.0e-6 (UA), `proj_beta_debt` max residual 2.9e-5/3.7e-5, "按协议字面，B-G2 失败 → 应停 Part B；B-G3 失败 → 该臂作废". The manuscript discloses only the residual magnitude, in the Data-and-Code section (L2224-2226).
- Reviewer deduction: the paper's own gate discipline (the GO rule "did not fire" at L2110-2111, A6b "untested" at L1915, the under-served rule not met at L1946-1948) raises the expectation that these failed gates would be reported next to the affected numbers; their absence reads as selective disclosure and is the single cheapest integrity complaint available to a hostile reviewer.
- Required fix: one sentence per gate at L2077-2097 giving the gate status and marking the `κ`=1000 arm exploratory.

**Weakness W-e: the exact flatness of the per-window group objective is absent, so the paper cannot explain its own insensitivity finding.**
- Evidence basis: `round_v3/EXECUTION_REPORT.md:132-133`: per-window `‖M_rα − μ‖₁` on `C_r` has median `range_r` = −1.13e-13 over 3,279 active windows, `min` median = `max` median = 1.97275, "argmin **完全不唯一**"; `ERRATA_v2.md:35` gives the mechanism ("每个窗口只覆盖 144/220 个组中的少数几个"). The manuscript presents `α`/`ω_r`/`M_r` as the structural lever (L578 "the effective deployment-group composition in an active window is `ω_r = M_rα_r`"; L596-599; L634-636), keeps a group-matching term `(λ_g/2)‖M_rα − μ‖₂²` in (P2) (L946-947), and at L2134-2136 reports the *consequence* — "three of the four members are insensitive to a large change in their own aggregation weights" — with no mechanism.
- Reviewer deduction: the paper documents that its own group term is structurally inert but does not say so; `B2−B1` inside the band is then presented as an empirical outcome rather than as a geometric consequence.
- Required fix: one sentence in §III-F or §VII-E stating that on these supports every active window's covered groups are target-empty, so the per-window group term carries no information and the surviving lever is the `β̂` anchor.

---

## 7. Potentially Missing Related Work

```text
Work: FedIPW (morishita2026who)
Status: user-provided (cited at main.tex L315-320); NOT searched this round
Why relevant: nearest two-stage (enrollment then participation) IPW factorisation toward a target-population mean
Overlap: factors two stages and reweights toward a target; differs in roster-level vs sensing-unit-level selection and in the target object
Needed comparison: variable / constraint / information-availability / conclusion mapping against RAVEN-MCS
```

```text
Work: FedPALS (listozec2024overcoming), FLOSS (goetze2025floss)
Status: user-provided (cited at main.tex L321-323); NOT searched this round
Why relevant: known-target aggregation and opt-out/straggler reweighting
Overlap: target alignment (labels vs deployment mass) and reweighting mechanics
Needed comparison: an explicit statement of what RAVEN-MCS can do that neither can, under the same information set
```

Unverified related-work risk (unchanged, provenance `inherited`): `W4` — the novelty axis stays at 2 because the positioning claim is still "combination of semantics", not a proved irreducibility.

---

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| When deployment and arrival laws differ, their risks are not interchangeable | Abstract L77-78; L191-193; Prop. 1 L1145 | NSW `D_aligned` = −0.0209…−0.0214, 17-18/20 seeds negative, `p` = 4.83e-4…5.86e-4 (L1656-1663) | strong (experiment) / adequate (formalism: Prop. 1 is a separating-functional statement) | The experiment tests the premise on one block; Proposition 1 is true but nearly tautological for two distinct laws on a finite domain | none |
| The ideal sequential correction recovers compatible target moments or group mass | Abstract L78-80; Prop. 2 L1194-1228 | Proof appendix L232-606 under A1-A3 | adequate | Correctly scoped at L1226-1227 ("not optimization of `R_μ(θ)`") | none |
| Calibration is uniquely solvable | Abstract L80-81; Thm 1 L1243-1248 | Standard strong convexity over non-empty compact convex `C_r` (A4, L1105-1108) | adequate | Correct; the theorem disclaims post-hoc optimality of logged solves at L1254 | none |
| The clipped plug-in is a stable perturbation of that reference when target support is compatible | Abstract L81; L229-230; Prop. 3 L1279-1316 | `eq:g4_beta` (38); paper itself notes `L_π ≤ 2×10^13` at `π_min = 1e-6`, so "the informative part of (38) is `ε_stab,r`" (L1330-1333) | weak (as a numeric bound) / adequate (as a stability statement) | Honest self-limitation, but "does not amplify" (L230) is only proved in the `α`-metric; `eq:g4_comp` (40) carries an extra `‖M_r‖₂` factor | qualify "does not amplify" to the `α`-metric |
| Design is worth 1.24 % of group mismatch on SensorScope at unchanged prediction | Abstract L86-87 | Table IV Design row +1.237* (L1977); ladder value +0.922 pp (L1839) | weak (two magnitudes, one name) | 1.237 % of Δ_group ≈ 0.63 pp, whereas the ladder reports 0.922 pp for "removing the design factor"; the two cannot both describe one contrast | state which contrast each number is, in both places |
| The surviving structural part requires the reconstructed reference projected onto the feasible set | Conclusion L2187-2189; L1833-1840 | Rung ladder `B1 = Proj_{C_r}(β̂)` strongest; `+0.768` pp over uniform (L1835-1836) | strong | Correct direction; `Proj_{C_r}(β̂)` is nevertheless never defined in the manuscript, and its status as a new trained rule appears ~250 lines later (L2090-2091) | define `Proj_{C_r}` once and label the new-rule status at first use |
| The remaining terms of (P2) are statistically equivalent to zero inside a pre-registered ±0.10 band | Contributions L243-247; L1842-1845; L1925-1926 | Band rows in `PART_A_REPORT.md:23-30`; several intervals exclude zero | absent (as stated) | No test, no `α`; the artifact's verdict is interval-containment in G-units | replace with containment wording + state the rule |
| Target debt is internal accounting, not a structural contributor | Contributions L231-234; L1845-1847; L2073-2075; Conclusion L2197 | `L6−L5` = +0.0073 pp inside the band; **and** `proj_beta_debt − proj_beta` = +1.347 pp (SS)/+0.580 pp (UA), Holm ≈1e-5 (L2088) | contradictory | The claim holds only for the frozen `λ_g`=1, `η`=0.01 configuration; the strongest structural arm in the paper's own new evidence is debt-driven | re-scope the claim and reconcile the two contrasts |
| Usable-update correction has no isolated effect in the tested family | L2058-2062; Conclusion L2196-2197 | Removing Use: no significant change in any core endpoint on either dataset (Table IV) | strong (a clean negative) | Correctly reported as a negative | none |
| The recoverable prediction gain is bounded and the GO rule did not fire | L2099-2120 | `abs(H) ≤ 0.217 %` with intervals containing zero; detectable effect 0.17-0.36 pp (SS) | strong | Honest null; makes "no RMSE win" a measured statement | none |

---

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines.** FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hájek, TwoStage-Hájek, FedAU-Window, ObsUse-Window; `Inst-Cal` and `Debt-Cal` expose reconstruction→calibration; Centre-All/Centre-Delivered/RAVEN-SimOracle are reference-only (L1556-1571). No official reproduction is claimed, which is correctly disclosed.
- **Ablations.** One-factor component removal (Table IV, L1964-1991) plus the new rung ladder and three retrained server-weight rules. The retrained-rule arm is the mechanism contrast that earlier rounds (`M8`, `W3`) demanded: same window policy, only server weights change, `B-G1` passed 120/120 (`PART_B_REPORT.md:16`).
- **Datasets / benchmarks.** SensorScope, U-Air (protocol-constructed `R`/`O`/`U`), NSW-Traffic (risk interchangeability + four-region), T-Drive (real `R`, controlled `O`/`U`), City Scanner `PM_{2.5}` and Pilot 2 (real `R`; measured `O` in Pilot 2 only). Non-mixing into Table II is stated repeatedly and consistently.
- **Metrics.** `RMSE_μ` (exact formula at L1591-1597), `WorstGroupRMSE`, `Δ_group`, `Δ_c-s`, `TV`, `H`. Two unit systems coexist (`pp = Δ/2×100` at L601-603; G-units at L605-608) and the G-unit denominator is undefined in the paper (see `R5-3`).
- **Statistical rigor.** Paired Wilcoxon with Holm within pre-declared families at `α` = 0.05, ties below 1e-12 (L1623-1626); paired bootstrap 95 % intervals (10,000 draws) in the evidence rounds; a `+0.5 %` descriptive tolerance whose non-inferiority status is disclaimed (L1632-1633). This is stronger than typical for the venue.
- **Robustness / failure cases.** `A6a` support audit fails on both datasets (L1915, L2161-2164); coverage-stress oracle pooled CERTIFIED validity 0.959, U-Air `a`=1.00 at 0.750 (L2166-2168); intermittent-occupancy protocol table; under-served-block check fails its rule (+0.05 %/+0.15 % and −0.44 %/−0.27 %, L1946-1948).
- **Implementation details.** 20 paired seeds except the balanced control (5) and four ten-seed tables (L1584-1586); `S_max = 5`; frozen `π_min`, `p_min`, `a_max`, `d_max`; runtime 18.5-20.0 s vs 27.1 s (L2091-2092).
- **Artifacts.** `RAVEN_MCS_PUBLIC_REPRO_R1` inventory at L2208-2218. The new round-v3/v4 ladder, band decisions and trained-rule artifacts are **not** listed in that inventory, so the band's verification path is not stated in the manuscript (`M7` remains open).
- **Limitations.** Well handled: protocol-constructed `O`/`U`, development-table status, no privacy guarantee from FL alone, design factor as an explicit configuration.

---

## 10. Multi-Reviewer Panel

```text
Reviewer: R1 — method / soundness
Expertise: federated optimisation, IPW estimators, convex programs
Score / score tendency: 4/5 dimensionally, lean-reject overall
Confidence: 5
Main positive signal: the four propositions are correctly scoped; `eq:g4_alpha` (39) is a valid non-expansiveness statement for a proximal map; `eq:debt_bound` (27) is proved correctly and I found no derivation error
Main negative signal: L1846-1847 cites (27) as assigning debt the role of non-contributor, but (27) is a one-sided inequality that cannot exclude a contribution, and its informative consequence `‖Q_R‖₁ = o(S_R)` is explicitly not established (L2075)
Evidence basis: main.tex L924-935, L1257-1333, L1842-1847, L2064-2075; appendix.tex L932-1144
Score-change condition: one sentence re-scoping the debt claim and the ground of the (27) citation
```

```text
Reviewer: R2 — evidence / experiment
Expertise: measurement studies, preregistration, equivalence testing
Score / score tendency: 3/5 dimensionally
Confidence: 4
Main positive signal: an unusually honest evidence round — failed gates, null prediction results and retracted claims are all recorded somewhere in the artifacts
Main negative signal: the failed gates and the band's missing decision rule are recorded in the artifacts but not in the manuscript where the numbers appear
Evidence basis: round_v4 PREREG.md:24, PART_A_REPORT.md:23-30,59,77, PART_B_REPORT.md:17-21; main.tex L1842-1847, L2077-2097, L2220-2230
Score-change condition: disclose gate status and the band rule in-text
```

```text
Reviewer: R3 — novelty / positioning
Expertise: mobile crowdsensing, selection bias
Score / score tendency: 2/5 dimensionally (inherited)
Confidence: 3
Main positive signal: the deployment-target-mass framing under three sequential selection layers is a useful reframing
Main negative signal: the new evidence reduces rather than strengthens the claim that the full apparatus is needed; the strongest structural arm is a simple projection of the corrected reference
Evidence basis: main.tex L236-253, L2077-2097; round_v3 EXECUTION_REPORT.md:83,114-118
Score-change condition: a demonstrated irreducibility argument versus the nearest two-stage IPW work
```

```text
Reviewer: R4 — writing / clarity
Expertise: technical editing
Score / score tendency: 3/5 dimensionally
Confidence: 5
Main positive signal: §VII-C/D read cleanly and the new attribution paragraph is well structured
Main negative signal: a dangling duplicated clause survives in §VI-A (L1547-1549, verified as a revision regression against the snapshot), the band lives in a modelling section while its siblings live in the statistical-policy section, and three terms carry two meanings each
Evidence basis: main.tex L601-608, L1544-1550, L1623-1637, L1842-1847 vs L2081-2090; snapshots/2026-10-03-pre-v4-contribution/main.tex L1587-1590
Score-change condition: fix the fragment, relocate/label the band, disambiguate the terms
```

```text
Reviewer: R5 — reproducibility / artifact audit
Expertise: artifact evaluation
Score / score tendency: 2/5 dimensionally (inherited `M7`)
Confidence: 3
Main positive signal: the evidence rounds ship preregistrations, sha256 manifests and decision CSVs; the ladder ledger is machine-readable
Main negative signal: the public repro bundle inventory (L2208-2218) does not cover the ladder/band/trained-rule artifacts, so the new claims are not independently checkable from the stated bundle
Evidence basis: main.tex L2200-2230; results_w1_ladder/round_v4/{PREREG,PART_A_REPORT,PART_B_REPORT}.md
Score-change condition: extend the bundle inventory to the round-v3/v4 artifacts
```

```text
Reviewer: R6 — AC / meta
Expertise: synthesis
Score / score tendency: 4-5/10 stance
Confidence: 4
Main positive signal: the paper's evidence-culture is above venue norm; every defect I found is a text-level fix
Main negative signal: the formalization did not raise the paper's ceiling; it raised its floor and, in this round, exposed two self-contradictions
Evidence basis: §§2-9 of this report
Score-change condition: the four `R5` text fixes plus one new endpoint result
```

```text
Agreement: the formalization is correctly scoped and the new evidence is honestly generated; the damage is in how the revision reports it
Disagreement: R2/R5 would penalise the reporting defects harder than R1, who finds the mathematics intact
Decisive positive axis: pre-registered, gate-checked, retraction-honest evidence with exact number fidelity
Decisive negative axis: no prediction-endpoint win, and the paper's own new evidence shows the full P2 apparatus is unnecessary for the structural gain
Unresolved evidence: the closable-gap denominator value; whether "their oracle values" at L1843 refers to the `simoracle` contrast; the closing status of ERRATA_v3 R1/R2/R3/E7/E8
AC stance: weak reject, upper edge; salvageable by text-only fixes plus one substantive endpoint result
```

---

## 11. Relative-Progress Scorecard (historical = round-4 manuscript -> current)

| # | Dimension | Historical | Current | Delta | Weight | Weighted delta | Explanation (issue IDs) |
|---|---|---|---|---|---|---|---|
| 1 | Originality / novelty | 2 | 2 | 0 | 0.10 | 0.00 | `W4` unresolved; the new round adds negative and attribution evidence, not a novelty axis |
| 2 | Soundness / technical quality | 5 | 4 | −1 | 0.20 | −0.20 | `R5-1` two contradictory debt magnitudes (L1842-1847 vs L2088); `R5-2` "statistically equivalent to zero" without a test; `R5-4` failed pre-registered gates undisclosed. `W2`/`W5` remain resolved and are not re-charged |
| 3 | Evidence / experiments | 2 | 3 | +1 | 0.25 | +0.25 | `M8`/`W3` mechanism contrast now exists in-manuscript: three retrained server-weight rules, same policy, only weights changed, `B-G1` 120/120; plus the rung ladder, the hindsight frontier, `κ` diagnostics and the degeneracy diagnostic |
| 4 | Clarity / presentation | 4 | 3 | −1 | 0.15 | −0.15 | `R5-3` band denominator mislabelled and unvalued; `R5-15` band defined in §III-F with no label; `R5-11` two magnitudes for "Design"; `R5-12` dangling duplicated clause at L1547-1549 (`revision_regression`); `N1` carried over |
| 5 | Reproducibility | 2 | 2 | 0 | 0.10 | 0.00 | `M7` unresolved; the band/ladder/trained-rule artifacts are absent from the stated bundle inventory (L2208-2218) |
| 6 | Significance / impact | 2 | 2 | 0 | 0.10 | 0.00 | No change in the reachable-effect axis: the structural headroom is 3.44 pp (SS)/1.32 pp (UA) and the full P2 captures 15-34 % of it; no prediction endpoint is significant |
| 7 | Related work / positioning | 3 | 3 | 0 | 0.05 | 0.00 | `W4` unresolved; no new positioning evidence |
| 8 | Terminology / notation | 4 | 3 | −1 | 0.05 | −0.05 | `R5-1` "the debt recursion" names two contrasts 185× apart; `R5-16` "recoverable" names two different headroom objects (L1826/L1924 vs L2102-2107); `R5-3` "closable gap" names the wrong reference |

**Weighted progress delta = +0.25 (Evidence) − 0.20 (Soundness) − 0.15 (Clarity) − 0.05 (Terminology) = −0.15 ⇒ `regressed`** under the frozen threshold (|delta| < 0.05 = unchanged).

Why this is not a contradiction of the round-4 "+0.20 improved": the round-4 gain came from resolving inherited hard faults (`W2`, `W5`, `W7`) with no regression. This round the revision adds the strongest evidence of the project's history *and* introduces four text-level defects that the same revision created. Under the frozen contract both facts must be scored; the contract does not let good new evidence offset new self-contradiction.

**Traceable score decreases** (all with current-version evidence, per the continuity rule):

| Decrease | Issue ID | Origin | Affected dimension | Current-version evidence | Delta |
|---|---|---|---|---|---|
| Soundness 5 -> 4 | `R5-1`, `R5-2`, `R5-4` | `revision_regression` (new text) + `newly_revealed_by_evidence` (v3/v4 records) | Soundness | L1842-1847 vs L2081-2090; L246-247; L2077-2097 vs `PART_A_REPORT.md:59,77`, `PART_B_REPORT.md:21` | −0.20 |
| Clarity 4 -> 3 | `R5-3`, `R5-11`, `R5-12`, `R5-15` | `revision_regression` | Clarity | L605-608 + L1839-1840 (implied 3.44 pp denominator); L86-87 vs L250-251; L1547-1549 vs snapshot L1587-1590; L601-608 vs L1623-1637 | −0.15 |
| Terminology 4 -> 3 | `R5-1`, `R5-16`, `R5-3` | `revision_regression` | Terminology | L1844 vs L2088; L1826/L1924 vs L2102-2107; L605-606 vs the printed `−0.268` | −0.05 |

**Consistently applied to both versions (no progress delta):** `R5-13` abstract "6.55 %" vs body "6.885 %" (`previously_undetected`; present in the snapshot at L89 and in the body at snapshot L1621 — it does not penalise only the current version). `N1` (region-level vs key-level `ρ_r`) carried over unchanged from round 4.

**Inherited issue reconciliation:** `W2`, `W5`, `W7`, `N3` stay `resolved`. `W3` moves `partially_resolved -> resolved` for its core ask (fixed-active-set, weight-only mechanism contrast) though its second ask ("rule out a single explanation" versus "locate the unique cause") is only partly met. `M8` is now `resolved` (the contrast exists and passes its integrity gate, `B-G1` 120/120). `W1` stays `unresolved` but its *shape has changed*: the comparison now exists, and its result is unfavourable to the full apparatus. `W4`, `W6`, `M7`, `N1`, `N2` unchanged.

**New issue provenance this round:** `R5-1` `revision_regression`; `R5-2` `revision_regression`; `R5-4` `revision_regression` + `newly_revealed_by_evidence`; `R5-3` `revision_regression`; `R5-5` `newly_revealed_by_evidence`; `R5-6` `revision_regression`; `R5-7` `revision_regression`; `R5-8` `revision_regression`; `R5-9` `newly_revealed_by_evidence`; `R5-10` `previously_undetected`; `R5-11` `revision_regression`; `R5-12` `revision_regression` (verified against the snapshot); `R5-14`, `R5-15`, `R5-16` `revision_regression`; `R5-17` `newly_revealed_by_evidence`.

---

## 12. THE CENTREPIECE: Global Impact Of The Formalization

**Formal inventory (verified).** `main.tex`: 4 `proposition` environments — Proposition 1 at L1145, 2 at L1194, 3 at L1279, 4 at L1335; 2 `theorem` environments — Theorem 1 at L1243, Theorem 2 at L1390; 1 `assumption` at L1382; the debt bound is equation (27) at L924-933 (confirmed against `main.aux`). Counts are **unchanged** by the latest revision (snapshot: 7 formal environments, same as current). `appendix.tex` actually carries **six** formal environments, not two: two unnumbered `proposition*` restatements (L149, L235) plus the coverage cluster — `proposition` L1320, `corollary` L1328, `corollary` L1340, `proposition` L1350. The proofs of Propositions 1-4, Theorem 1 and the debt bound run appendix L146-1146, with further consequences at L1147-1281; all of this is in `supplemental.pdf` (16 pp), not in the 17-pp main paper, which references it as "the supplemental material".

**Page cost.** `§VI Theoretical Analysis` = L1074-1413, i.e. 340 of 2235 lines ≈ 2.6 pp of the 17-pp main paper (~15 % of the budget). The appendix formal apparatus ≈ 1,280 of 2,611 lines ≈ 7.9 pp of the 16-pp supplemental (~half of it). With "zero slack", the marginal cost of each formal statement is real but the main-paper share is small; the compression pressure is therefore an *opportunity* question (what else could those 2.6 pp carry), not an overflow emergency.

### 12.1 The six tensions, decided

#### Tension 1 — `prop:group_decomposition` (L1335) versus the exactly-flat per-window objective

**Verdict: partially (premise refuted; a different gap confirmed).**

The premise as posed does not hold: the proposition's "feasible direction `d` of the simplex, `Σ_g d_g = 0`" is a direction in the **evaluation-weight** simplex, not in `α`. The appendix proof says so explicitly — L909-913: "The within-group weights `μ^eval_g/n_g` do not depend on the masses of the other groups, so `RMSE_g` is independent of `d`" — and the ordering consequence is stated over "two evaluation weight vectors `μ^eval` and `μ'^eval`" (L1346-1349). The proposition therefore never presumes that `α` moves the within-window group distribution, and its scope paragraph is careful in the same direction: "It re-weights one fixed set of predictions, so it constrains how a reported value moves with the target map and not how a method would perform under a different map" (L1358-1360).

What the flatness does damage is elsewhere:
- **(a) The (P2) group term is inert and the paper does not say so.** `(λ_g/2)‖M_rα − μ‖₂²` sits in the objective (L946-947), and the manuscript's own ladder finds `B2 − B1` inside the registered band (`round_v3/EXECUTION_REPORT.md:114`, `round_v4/PART_A_REPORT.md:23`), while T7 shows the per-window L1 objective is *exactly* flat with a completely non-unique argmin (`round_v3/EXECUTION_REPORT.md:132-133`). §VII-C states only the positive half: "The projected reference carries that reference-side part, and the design factor is the only further component that survives" (L1833-1835).
- **(b) The paper does imply a per-window lever the evidence shows is absent — but at the geometry level, not in Proposition 4.** L578 defines "the effective deployment-group composition in an active window is `ω_r = M_rα_r`"; L596-599 defines `Δ_group` from it; L634-636 states the design goal as "keep `R_μ` low while reducing `Δ_group` and `Δ_c-s`"; and §VII-F reports the *consequence* of flatness without the mechanism — "three of the four members are insensitive to a large change in their own aggregation weights" (L2134-2136).
- **(c) The one limb of Proposition 4 that is dead weight is the derivative clause.** `Σ_g d_g RMSE_g²/(2 RMSE_μ)` (L1343-1345) is referenced nowhere else in the paper or appendix (full-text search: `directional` occurs once in each file).

**Consequence:** do not re-scope Proposition 4. Add one mechanism sentence (windows cover target-empty groups, so the per-window group term carries no information and the `β̂` anchor is the surviving lever), and consider dropping the derivative clause.

#### Tension 2 — `eq:debt_bound` (27) versus "debt is not a structural contributor"

**Verdict: partially (validity and necessity are kept separate in the appendix and in §VII-E's ablation paragraph, and conflated in exactly one clause that the paper then repeats as a conclusion).**

- The appendix keeps them separate and even pre-empts the over-read: the bound's consequence is explicitly conditional — "If the cumulative debt is sublinear in active step mass ... This is a conditional implication of the deterministic bound. It is not a separate claim that RAVEN guarantees sublinear debt" (appendix L1129-1144).
- §VII-E's ablation paragraph is also careful: "This matches the accounting of (27) rather than a standalone performance driver, and does not establish `‖Q_R‖₁ = o(S_R)`" (L2073-2075).
- The conflation is L1845-1847: "stay inside that band, so debt is an auditable accounting recursion for residual under-service rather than a structural contributor, **which is the role `(27)` assigns to it**". A one-sided inequality `Δ_group ≤ 2‖Q_R‖₁/S_R` cannot assign a non-contributor role; it is equally satisfied by a debt that contributes (and by a debt that is large). The sentence converts a *validity* certificate into a *necessity* verdict.
- The necessity verdict is then carried, unreconciled, into contributions L231-234 ("empirically, instantaneous calibration and debt are neither prediction drivers nor structural contributors") and the conclusion L2197 ("target debt remains internal accounting"), while §VII-E L2088 reports a debt-driven rule adding +1.347 pp (SS)/+0.580 pp (UA) at Holm ≈1e-5 — and the evidence file itself says the strongest structural arm on both datasets is `proj_beta_debt` (`PART_B_REPORT.md:82`).
- The bound is *not* motivated as establishing the mechanism's value anywhere (L920-922 is descriptive), so the reverse conflation the tension asks about is absent.

**Consequence:** delete or rephrase the "role (27) assigns" clause; scope "not a structural contributor" to the frozen `λ_g`=1, `η`=0.01 configuration and separate it from the debt-weighted rule.

#### Tension 3 — the registered ±0.10 band and ruler qualifiers inside a paper of identities and bounds

**Verdict: agree (the tension is real, and the paper currently loses this exchange).**

- **Defined once, used consistently?** Defined once at L601-608 and reused at L246, L1840, L1842-1845, L1925-1926. The *unit* is used consistently as the evidence's G-unit, but the *name* is wrong (see Tension 4 / `R5-3`), the denominator's value is never printed, the band has no `\label` and no cross-reference to the preregistration, and its verdicts are quoted in mixed units (L1842-1844 gives `+0.0073 pp` and then says "stay inside that band", whose unit is the closable gap).
- **Is the register shift signposted?** Only by the word "pre-registered" (L608). The band sits in §III-F "Structural Alignment Objective" — a modelling subsection — in the same paragraph as the mathematical definitions of `pp` and of the uniform-weight ruler. Its natural siblings (`α` = 0.05, Holm families, the `+0.5 %` tolerance) are in §VI-C "Metrics and statistical policy" (L1588-1637). A reader meets a preregistration convention before meeting the statistical-policy section that would explain it.
- **Is any earlier claim read as a band verdict?** Yes, at the most prominent place: contributions L243-247, "which is statistically equivalent to zero inside a pre-registered ±0.10 band of the closable gap". This asserts a *statistical equivalence* the artifacts do not perform. No TOST, no `α`, no interval rule exists in the v4 package (`PREREG.md:24` mentions only the G-unit and pp lines), and the band-inside rows' intervals exclude zero on several rows (`PART_A_REPORT.md:23,25,26`). The asymmetry with L1632-1633 — where the *weaker* `+0.5 %` tolerance is disclaimed as "descriptive rather than a formal non-inferiority test" — is what makes this a credibility rather than a pedantry issue.
- **Would a TMC reviewer accept the band in the manuscript rather than artifact-only material?** Yes, *if* it is fixed: it is pre-registered, it is the cleanest way to say "the remaining terms are small", and it should stay. If the authors will not state the decision rule, the honest fallback is the opposite move — demote the band from the contributions to a descriptive interval-containment report in §VII-C.

**Consequence:** keep in-manuscript; fix the unit name and value, state the rule and its non-test status, and replace "statistically equivalent to zero".

#### Tension 4 — the design-gate/switch structure (42)/(43) versus the reduced structural headroom

**Verdict: partially refute (the text has been re-scoped correctly in the two places that matter; three residual framing problems remain).**

- **Refuted strong form.** The surviving text does *not* present the structural channel as where the benefit lives: L1920-1926 "most of that gap, 68.96 % on SensorScope and 83.07 % on U-Air, is already recoverable by uniform server weights, the surviving part is carried by the projected reference, and the terms of (P2) and the debt recursion stay inside the equivalence band"; and the conclusion L2187-2189 "most of the FedAvg structural gap on both datasets is recoverable by uniform server weights, and the surviving part requires the reconstructed reference projected onto the feasible set". §VII-C L1833-1840 gives the projection `+0.768 pp`/`+0.286 pp` with the `0.5 pp` practical line and the seed-half stability flags. That is proper re-scoping.
- **(a) `eq:design_switch` (43) still trades the structural endpoints as co-equal objectives on the un-ruled scale.** L2029-2044 defines `Ĵ_r(D) = Σ_e w_e M_{e,r}(D)/M_{e,r}(on)` over `{Δ_group, Δ_c-s, RMSE_μ, Tail}` and prints "the two settings are indifferent when `w_c 4.990 = w_g 6.943 + w_μ 6.885 + w_t 7.221`". Those four coefficients are the **U-Air** ablation percentages, but the sentence never says so, and it uses relative changes of heterogeneous endpoints — the very scale that L242-247 repudiates for structural reporting. §VII-E's own caveat L2045-2051 ("a decision standard for blocks of this kind rather than a universal law ... that decomposition covers neither `Δ_group` nor `Δ_c-s`") mitigates but does not label the coefficients.
- **(b) The abstract sells a structural gain with no ruler.** L86-87 "Design is worth `1.24 %` of group mismatch on SensorScope at unchanged prediction" is the only performance-flavoured sentence in the abstract, and it breaks the reporting rule the paper itself sets at L242-243 ("Structural improvements are therefore quoted relative to uniform weights"). Recomputing from Table IV: `1.237 %` of `Δ_group` = `1.0139` is `0.0126` in L1 = `0.63 pp`, i.e. about 18.9 % of the `3.44 pp` closable headroom — the same share the evidence reports for RAVEN's own improvement over uniform weights (`PHASE3_REPORT.md:78`). Stated without that context, `1.24 %` invites the reader to over-read the effect; stated with it, the honest sentence is "the design factor closes about a fifth of the recoverable structural mass on SensorScope".
- **(c) The ratio between the two scales is never stated.** Design-on costs `0.0759` in `Δ_group` on U-Air = `3.8 pp`, versus a total U-Air FedAvg→RAVEN gap of `1.47 pp` and a closable headroom of `1.32 pp`. So the paper's largest structural contrast is ~2.6× the entire gap whose attribution it just decomposed. §VII-E disclaims this as "a decision standard for blocks of this kind" (L2045) but never gives the magnitudes in one place, so the reader cannot see that the Design decision dominates the attribution arithmetic.

**Consequence:** label the (43) coefficients as U-Air, state that (43) is a within-RAVEN endpoint trade on the raw scale, print the closable headroom once, and bring the abstract sentence onto the ruler.

#### Tension 5 — `prop:practical_plugin` / `prop:reconstruction` / `prop:risk` versus the new numbers

**Verdict: partially (no contradiction with any stated assumption, three soft conflicts with claim wording).**

- **Not in conflict.** `eq:g4_beta` (38) is acknowledged by the paper itself to be numerically vacuous at the frozen constants — "at `π_min = 10^-6` and `p_min = 0.05` the Design-on `L_π ≤ 2×10^13`, so the informative part of (38) is `ε_stab,r`" (L1330-1333) — so the measured reference perturbation (median `0.077` in `ℓ1`, up to `1.15`, L2131-2132) does not contradict it; it merely confirms the bound is uninformative. `A6a` failing on both datasets is disclosed twice (L1915, L2161-2164) and the proposition is explicitly stated as "not conditional on A6a" (L1328). The exact flatness is *consistent* with `eq:g4_comp` (40): the bound is loose exactly where the true composition change is zero.
- **(a) "Does not amplify" is only proved in the `α`-metric.** L229-230: "the implemented RAVEN-Design clipped plug-in is a Lipschitz perturbation of the same-window ideal reference **that the calibration program does not amplify**". `eq:g4_alpha` (39) gives non-expansiveness in `‖·‖₂` on `α`; `eq:g4_comp` (40) then multiplies by `‖M_r‖₂`, which for `A_r` of dozens of clients with near-identical group compositions is of order `√K_r ‖c‖₂ > 1`. Empirically the manuscript itself reports the opposite at the composition level: "The substitution is not small before aggregation ... and it reaches the aggregate composition at the same order" (L2130-2134). Both statements can be true of different metrics, but the introduction's phrasing reads as a claim about the composition.
- **(b) The `M_r`-is-trace-fixed premise is now known to fail at `2×10^-6`-`3.7×10^-5`.** Proposition 3 and A5 assume "the ideal and the implemented reference share `A_r`, `M_r`, and `C_r`" (L1283-1284, L1115), and the ruler clause requires the same `M_r` (L606-607). `PART_B_REPORT.md:20` records that `β̂` is "逐窗逐位相同（差 0.0）" while the residual "只能来自该 run 自身的 `M_r`/质量输入随模型轨迹的微弱变化——即门所依赖的前提'`M_r` 与模型无关'在 1e-9 量级上不成立（观测权重的 `p_hat` 是模型相关的）". The manuscript reports the residual and its cause (L2224-2229) but only in the Data-and-Code section, never next to the ruler definition or Proposition 3. A `4×10^-5` perturbation does not overturn any reported verdict, but a reviewer can legitimately ask whether the band's intervals (widths as small as `1.9e-4` on `L6−L5`) are robust to an input perturbation of that size.
- **(c) The oracle clause is not supported by this round's evidence.** L1843-1845: "the observation and usable-update factors, **their oracle values**, and the debt recursion ... stay inside that band". The round-v4 package contains **no** oracle contrast at all (`PART_A_REPORT.md:26-27,30` use `raven_wo_obs`/`raven_wo_use` as p and q; "oracle" survives only as a CSV arm label). The only oracle contrast I can find is the v3 `B1(simoracle) − B1(raven)` = `+0.0639` `[−0.0020, +0.1214]`, whose own verdict cell reads "**带外但跨 0**" (`round_v3/EXECUTION_REPORT.md:119`) — outside the band, because the interval's upper end exceeds `0.10`. Since the manuscript never states whether the band is read on the point estimate or the interval, this row is either inside (point estimate `0.064 < 0.10`) or outside (interval `0.121 > 0.10`) — and the artifact chose outside while the manuscript claims inside.

**Consequence:** qualify "does not amplify" to the `α`-metric; cross-reference the `M_r`-drift caveat into the ruler clause; either support or delete "their oracle values".

#### Tension 6 — formal apparatus versus the 17-pp budget

**Verdict: agree with the framing, no fatal compression need.**

The main paper's formal share is §VI only: 340 lines ≈ 2.6 pp ≈ 15 % of the budget. Nothing is so expensive that it must go for space reasons; the question is value per line. Ranked candidates:

1. **Coverage-Gate apparatus (largest, most defensible).** Theorem 2 + Assumption 1 in main (L1367-1413) plus §III-D (L483-499) and §V-E (L986-1007) ≈ 70 lines main, and appendix L1282-1526 = 245 lines. It certifies a diagnostic that, by the paper's own repeated statement, never switches anything: "A diagnostic Gate on a lower bound of `C_t` does not switch Design" (L499), "It does not switch Design" (L1007), "Algorithm 1 does not open Design from `Gate_t`" (L1412-1413), plus L273, L854, L2168. It answers a reviewer question and reports a real failure (pooled CERTIFIED validity 0.959; U-Air `a`=1.00 at 0.750, L2166-2168), so it should not be deleted — but the two appendix propositions/corollaries could move to the artifact and main could keep Theorem 2's statement and the validity numbers, recovering ~35-45 main lines.
2. **Proposition 3's constant expansion, corollaries and numerical-vacuity paragraph** (L1305-1333, ≈29 lines): keep the statement and one sentence of self-limitation, move `L_π/L_p/L_q/C_1` and corollaries (a)/(b) to the supplemental. Recovers ~20 lines.
3. **Proposition 4's directional-derivative clause** (main L1343-1345; appendix L897-898): referenced nowhere. Delete. Recovers ~5 lines.
4. **Keep all four propositions and both theorems.** Each carries distinct load for the W1 response (see §12.2). Compressing Proposition 1 (L1145-1169, 25 lines) into a remark is defensible but saves little and loses the abstract's formal backing.

### 12.2 What The Formalization Buys (reviewer-facing value)

- **`eq:debt_bound` (27) is the only object in the paper with two independent empirical verifications.** T1 replays the debt recursion `Q_{r+1} = max(Q_r + 0.01(μ − M_rα_r), 0)` against the frozen trajectory and matches exactly on **80/80** runs with `max_r e_r = 0.0` (`DEBT_RECURSION.md:24`); C3 checks the inequality itself on **240/240** runs with ratio `0.7174-0.8215` and minimum margin `0.2492` (`PHASE5_REPORT.md:13`). This is exactly the kind of "the recursion in the paper is the recursion in the code" evidence that closes a reproducibility objection — and the v2 claim that the recursion did not hold was itself retracted as a *tooling* error (`ERRATA_v2.md:57`), which the bound's existence made checkable.
- **Proposition 2 lets the paper draw the boundary that saves it from its own strongest objection.** Because it proves moment/group-mass recovery and explicitly not `R_μ` optimisation (L1226-1227), the paper can state at L1907-1911 that the new attribution findings "agree with the scope of the theory". Without it, the projection-carries-the-gain result would look like a refutation rather than a prediction.
- **Proposition 3 is what licenses the abstract's central stability sentence and §VII-F's composition bound.** "The clipped plug-in is a stable perturbation of that reference" (L81) and the composition-level argument at L2137-2141 depend on (38)-(40) — and (40) is the only statement that connects the reference perturbation to the aggregate composition. Its numerical vacuity is disclosed by the paper before a reviewer can raise it (L1330-1333), which converts a potential attack into a disclosure.
- **Proposition 4 makes the uniform-weight ruler argument legitimate rather than rhetorical.** It is what lets the paper say that `RMSE_μ` is not a method property but a property of the evaluation map (L1355-1365), which is the formal backing for the abstract's closing sentence, "No ranking jointly measures `R`, `O`, and `U`" (L93), and for the switch's prediction side being readable from per-group scores the deployment already reports (L2047-2051).
- **Theorem 1 plus the explicit feasible set `C_r` (25) give the projection a meaning.** The strongest new rung is defined as `Proj_{C_r}(β̂)`; without a stated non-empty compact convex `C_r` (A4, L1105-1108) the projection has no domain, and the feasibility diagnostics that make the new evidence credible — binding constraint is the ESS sphere, `frac_vertex = 0.0` (`PART_A_REPORT.md:54-57`) — would have nothing to be measured against.
- **The newly added conditional/registered layer converted a claim into a reportable null.** Before this revision the structural attribution rested on relative changes of a single table; now the paper quantifies 68.96 %/83.07 % of the gap as uniform-weight-carried, prints the projection's interval and seed-half stability, flags the U-Air projection as below the practical line and unstable, reports ζ's non-identifiability on U-Air, and states that no prediction contrast survives Holm (L2093-2095). For a reviewer, that is four independent statements of what the method does *not* achieve, which is the single most credibility-positive change in the revision.

### 12.3 What The Formalization Costs

- **Mixed epistemic register.** One paragraph (L601-608) now carries a mathematical normalization, a reporting ruler, and a preregistered statistical convention, and the strongest claim built on it ("statistically equivalent to zero", L246) has no procedure behind it. The formal statements themselves are identities and one-sided bounds, so a statistical-equivalence reading cannot be inherited from them.
- **A page-budget opportunity cost.** ~2.6 pp of a zero-slack paper sits in §VI, of which the coverage-Gate material (~0.5 pp) supports an instrument the paper says never acts.
- **Formal apparatus reused as rhetoric.** (27) is cited as assigning a role (L1846-1847); "does not amplify" (L230) generalizes a metric-specific bound; `Proj_{C_r}(β̂)` is used as the carrier of the gain (L244, L1835) without ever being defined.
- **No ceiling movement.** Neither the propositions nor the new conditional layer adds a reachable effect: the structural headroom is `3.44 pp`/`1.32 pp`, the best ladder rung captures `0.58`/`0.32 pp` of it, and prediction endpoints stay flat. The formalization raised the paper's floor (scope, verifiability, honesty) and left its ceiling where it was.

---

## 13. Absolute-Readiness Scorecard (current version only)

| # | Dimension | Current /5 | Confidence | Deduction basis and raise condition |
|---|---|---|---|---|
| 1 | Originality | 2 | high | Combination-and-scenario novelty; the nearest two-stage IPW work already contains the key structure (`W4`, unchanged). Raise: complete the FedIPW/FedPALS variable-constraint-information mapping and prove an irreducible difference |
| 2 | Soundness | 4 | high | Deduction: `R5-1` self-contradictory debt magnitudes (L1842-1847 vs L2088); `R5-2` "statistically equivalent to zero" with no test and band rows whose intervals exclude zero; `R5-4` failed pre-registered gates undisclosed at L2077-2097; `R5-6` (27) cited as assigning a non-contributor role; `R5-7` "does not amplify" beyond its metric. No proof error found; `W2`/`W5` repairs intact. Raise: the four text fixes, no new experiments |
| 3 | Evidence | 3 | high | Deduction: still no prediction-endpoint contrast that survives Holm on any block (L2093-2095), and the paper's own new evidence shows the full P2 captures only 15-34 % of a 1.3-3.4 pp recoverable headroom. Credit: the mechanism contrast `M8`/`W3` now exists (three retrained rules, `B-G1` 120/120), the ladder and frontier are in-manuscript, and the negative results are reported. Raise: one endpoint with an externally meaningful win, or a task where structure converts to prediction |
| 4 | Clarity | 3 | high | Deduction: `R5-3` band denominator mislabelled (`closable gap between uniform weighting and the projected reference`, L605-606) and never valued, while the printed number implies the hindsight-optimum denominator; `R5-11` the abstract's `1.24 %` and the contributions' `+0.922 pp` cannot describe one contrast; `R5-12` dangling duplicated clause at L1547-1549; `R5-15` band placement/label; `N1` carried over. Raise: relabel and print the denominator, relocate the band to §VI-C, fix the fragment, state which contrast each Design number is |
| 5 | Reproducibility | 2 | medium | `M7` unresolved: `RAVEN_MCS_PUBLIC_REPRO_R1` (L2208-2218) does not list the round-v3/v4 ladder, band-decision or trained-rule artifacts, so the new claims are not checkable from the stated bundle; `Common-NDMF` configuration, T-Drive `Y` construction and City Scanner evaluation rules remain incomplete (`W6`). Raise: refresh the bundle and extend its inventory |
| 6 | Significance | 2 | medium | The reachable large effect is still the single Design ablation, now shown to be a within-RAVEN contrast of `3.8 pp` on a `1.47 pp` gap; the structural channel is 1.3-3.4 pp of recoverable target mass. Raise: a task where target-mass alignment changes a decision, not a diagnostic |
| 7 | Related work | 3 | medium | Reasonable positioning; `W4` unresolved and not re-searched this round. Raise: the irreducibility mapping |
| 8 | Terminology | 3 | high | Deduction: "the debt recursion" names two contrasts 185× apart (L1844 vs L2088); "recoverable" names the Δ_group closable gap (L1826, L1924) and the §VII-F RMSE_μ headroom `H` (L2102-2107); "closable gap" names the wrong reference. Raise: three one-line disambiguations |

**Weighted readiness sum = 2.90** (round 4: **3.05**; round 3: 2.80). **Overall stance: 5/10 (borderline negative, weak-reject band upper edge), threshold 4/10.** The stance is held at 5 despite the −0.15 weighted movement because the calibrated 1-10 stance follows the strongest *unresolved decision-relevant* weakness, which is unchanged (evidence/significance: no prediction win, small reachable structural effect), while the new decreases are text-level claim-management defects that the authors can fix without new experiments. If those four fixes are not made, a reviewer who checks the band against the artifact will have grounds to move the stance to 4/10.

**Remaining blocking evidence (by weight).**
1. **Evidence (0.25):** one endpoint where alignment converts to prediction, or an externally meaningful task; the full-P2-necessity question is now answered *against* the full apparatus and the paper must live with that answer.
2. **Soundness (0.20):** disclose the failed gates; state the band's rule; reconcile the debt claims.
3. **Clarity (0.15):** fix the band's definition and value; fix the fragment; disambiguate the two Design magnitudes.
4. **Reproducibility (0.10):** extend the bundle inventory to the ladder/band/trained-rule artifacts.

---

## 14. Concerns Table

Severity values: fatal / major / moderate / minor. Fix classes: related-work, experiment, method/soundness, reproducibility, ethics/limitations, writing, compression, rebuttal-only, venue-mismatch.

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
|---|---|---|---|---|---|---|---|---|
| `R5-1` | major | Two irreconcilable magnitudes for "the debt recursion" (band-inside `+0.0073` pp vs Holm-significant `+1.347`/`+0.580` pp), with the non-contributor reading carried into contributions and conclusion | `main.tex` L1842-1847 vs L2081-2090; L231-234; L2197; `round_v4/PART_A_REPORT.md:25`; `PART_B_REPORT.md:82` | Soundness, Terminology, Significance | method/soundness | Rename the two contrasts (frozen `λ_g`=1/`η`=0.01 term vs `κ`=1000 debt-weighted retrained rule) in both places and scope the claim | `ccf-paper-writer` | Soundness +1 if fixed; −1 more if a reviewer finds it unaided |
| `R5-2` | major | "Statistically equivalent to zero inside a pre-registered ±0.10 band" asserts a test the artifact never performs; band-inside intervals exclude zero on several rows | `main.tex` L246-247, L1842-1845, L1925-1926; `round_v4/PREREG.md:24`; `PART_A_REPORT.md:23,25,26` | Soundness, Clarity | method/soundness | Replace with interval-containment wording and state the band's rule and non-test status | `ccf-paper-writer` | Soundness +1; fatal-adjacent if left unfixed and probed |
| `R5-3` | major | Band denominator mislabelled as uniform→projected reference while the printed conversion implies uniform→hindsight-optimal `Δ*` (`3.44` pp), and its value is never reported | `main.tex` L605-608 + L1839-1840; `round_v2/PHASE3_REPORT.md:77`; `main.tex` L1835 | Clarity, Terminology | writing | Name the denominator and print its pp value once per dataset | `ccf-paper-writer` | Clarity +1 |
| `R5-4` | major | Numbers derived from failed pre-registered gates are reported as results without the gate status | `main.tex` L2077-2097, L2220-2230; `round_v4/PART_A_REPORT.md:59,77`; `PART_B_REPORT.md:17,18,21` | Soundness, Reproducibility | method/soundness | One sentence per gate at the point of use; mark the `κ`=1000 arm exploratory | `ccf-paper-writer` | Soundness +1 |
| `R5-5` | major | The exact flatness / non-unique argmin of the per-window group objective is absent, so the paper cannot explain its own insensitivity finding or the inertness of (P2)'s group term | `round_v3/EXECUTION_REPORT.md:132-133`; `ERRATA_v2.md:35`; `main.tex` L578, L596-599, L634-636, L946-947, L2134-2136 | Soundness, Significance | method/soundness | Add one mechanism sentence and state that the surviving lever is the `β̂` anchor | `ccf-paper-writer` | Soundness +0.5; strengthens Significance framing |
| `R5-6` | moderate | `eq:debt_bound` (27) cited as "the role (27) assigns to it", converting a one-sided validity inequality into a necessity verdict | `main.tex` L1845-1847; `appendix.tex` L1129-1144; L2075 | Soundness | writing | Delete or rephrase the attribution clause | `ccf-paper-writer` | Soundness +0.5 when combined with `R5-1` |
| `R5-7` | moderate | "Does not amplify" (L230) generalizes `eq:g4_alpha` (39), which holds in the `α`-metric; `eq:g4_comp` (40) carries `‖M_r‖₂`, and L2130-2134 reports propagation at the same order | `main.tex` L229-230, L1295-1303, L2130-2134 | Soundness | writing | Qualify to the `α`-metric and cite (40) for the composition metric | `ccf-paper-writer` | Soundness +0.25 |
| `R5-8` | moderate | `Proj_{C_r}(β̂)` is the principal carrier of the structural gain yet is never defined, and its new-rule status appears ~250 lines after the attribution | `main.tex` L244, L1835, L2090-2091; `round_v4/PART_A_REPORT.md:67` | Clarity, Reproducibility | writing | Define the projection once and label its status at first use | `ccf-paper-writer` | Clarity +0.5 |
| `R5-9` | moderate | "their oracle values" are claimed band-inside, but the v4 package contains no oracle contrast and the v3 oracle row reads "outside the band" | `main.tex` L1843-1845; `round_v3/EXECUTION_REPORT.md:119`; `PART_A_REPORT.md:26-30` | Soundness | writing | Support the clause or delete it | `ccf-paper-writer` | Soundness +0.25 |
| `R5-10` | moderate | `eq:design_switch` (43) trades the structural endpoints as co-equal objectives on the un-ruled raw scale, with U-Air coefficients printed unlabelled | `main.tex` L2029-2044; L242-247 | Clarity, Significance | writing | Label the coefficients as U-Air and state the within-RAVEN scope | `ccf-paper-writer` | Clarity +0.25 |
| `R5-11` | moderate | Abstract's "`1.24 %` of group mismatch" and the contributions' "`+0.922 pp`" cannot describe one contrast (0.63 pp vs 0.922 pp), breaking the ruler rule set at L242-243 | `main.tex` L86-87, L250-251, L1782-1783, L1977, L1839 | Clarity, Terminology | writing | State which contrast each number is, and put the abstract sentence on the ruler | `ccf-paper-writer` | Clarity +0.5 |
| `R5-12` | moderate | Dangling duplicated clause in §VI-A | `main.tex` L1544-1550 vs `snapshots/2026-10-03-pre-v4-contribution/main.tex` L1587-1590 | Clarity | writing | Delete the fragment | `ccf-paper-writer` | Clarity +0.25 |
| `R5-13` | minor | Abstract "`6.55 %` of RMSE" vs body "`6.885 %`" (pre-existing; applied to both versions) | `main.tex` L87 vs L1577, L1984; snapshot L89 | Terminology | writing | Align to `6.885 %` | `ccf-paper-writer` | none in the progress scorecard |
| `R5-14` | minor | Band verdicts quoted in mixed units: `+0.0073 pp` then "stay inside that band", whose unit is the closable gap | `main.tex` L1842-1845; L601-608 | Terminology | writing | Print G-units and pp together, as the preregistration itself mandates | `ccf-paper-writer` | Terminology +0.25 |
| `R5-15` | minor | The band is defined in a modelling subsection, has no label, and lacks the "descriptive, not a test" disclaimer its weaker sibling carries | `main.tex` L601-608 vs L1623-1637 | Clarity | writing | Move/label the band and mirror the `+0.5 %` disclaimer | `ccf-paper-writer` | Clarity +0.25 |
| `R5-16` | minor | "Recoverable" names two different headroom objects (Δ_group closable gap vs §VII-F `H`) | `main.tex` L1826, L1924, L2188 vs L2102-2107 | Terminology | writing | Rename one of them | `ccf-paper-writer` | Terminology +0.25 |
| `R5-17` | minor | A5 / Proposition 3 assume `M_r` is shared and fixed, but `M_r` drifts with the model trajectory at `2e-6`-`3.7e-5`; the caveat sits only in the availability section | `main.tex` L1115, L1283-1284, L606-607, L2224-2229; `PART_B_REPORT.md:20` | Reproducibility, Soundness | writing | Cross-reference the drift caveat into the ruler clause and Proposition 3 | `ccf-paper-writer` | Reproducibility +0.25 |
| `C1` | minor | Proposition 4's directional-derivative clause is never referenced | `main.tex` L1343-1345; `appendix.tex` L897-898 | Clarity | compression | Delete the clause, keep the identity and the scoping paragraph | `ccf-paper-writer` | enables §VII space for `R5-2`/`R5-4` text |
| `C2` | minor | Coverage-Gate apparatus supports an instrument the paper states never acts | `main.tex` L483-499, L986-1007, L1367-1413, L273, L499, L854, L1007, L1412-1413, L2168; `appendix.tex` L1282-1526 | Clarity | compression | Move the two appendix propositions/corollaries to the artifact; keep Theorem 2 and the validity numbers | `ccf-paper-writer` | frees ~35-45 lines |
| `W1` | major (inherited) | Core benefit and necessity of the full method not closed | `main.tex` L2099-2142; `round_v4/PART_B_REPORT.md:67-78` | Evidence, Significance | experiment | New endpoint evidence; the comparison now exists and its answer is unfavourable | `ccf-experiment-designer` | Evidence +1 if a prediction endpoint becomes significant under a declared family |
| `W3` | resolved core / partial residual | Support diagnosis now carries the mechanism contrast; the "unique cause" ask is only partly met | `main.tex` L1776-1935; `PART_B_REPORT.md:16` | Evidence | experiment | State the remaining interpretive boundary explicitly | `ccf-experiment-designer` | no further movement expected |
| `W4` | major (inherited) | Novelty boundary vs FedIPW/FedPALS | `main.tex` L314-323 | Originality, Related work | related-work | Variable/constraint/information/ conclusion mapping | `ccf-literature-searcher` | Originality +1 |
| `W6` | major (inherited) | Representativeness / reproduction conditions | `main.tex` L1447-1490, L1584-1586 | Evidence, Reproducibility | experiment | Write the available off-manuscript evidence; complete training/label semantics | `ccf-experiment-designer` | Evidence/Reproducibility +0.5 |
| `M7` | major (inherited) | Public bundle inconsistent with the corrected tables; new artifacts absent from the inventory | `main.tex` L2208-2218 | Reproducibility | reproducibility | Refresh the bundle and its inventory | `ccf-integrity-auditor` | Reproducibility +1 |
| `N1` | moderate (inherited) | Key-level `ρ_r` vs region-level appendix row unstated | `appendix.tex` L2440; `main.tex` L2012-2020 | Clarity | writing | State the object relation and adjudicate the row | `ccf-paper-writer` + user | Clarity +0.25 |
| `N2` | opportunity (inherited) | Off-manuscript exogenous-target and endpoint evidence | `results_exogenous_target/`, `results_group_identity/` | Evidence, Significance | experiment | Write it into the paper | `ccf-paper-writer` | Evidence/Significance up if it lands |

---

## 15. AC / Meta-Review

- **Reviewer consensus.** The formalization is correctly scoped and the new evidence round is real, pre-registered and honestly generated; the revision's defect is claim management, not mathematics: two of its own paragraphs contradict each other about debt, and its strongest new statistical phrase has no procedure behind it.
- **Reviewer disagreement.** R1 regards the mathematics as intact and would call the defects editorial; R2 and R5 treat undisclosed failed gates and an unsupported equivalence claim as materially more serious, because they are the kind of finding that changes a reviewer's *trust* rather than a number.
- **Decisive acceptance axis.** Recoverability: a reader can see exactly which part of the structural gain is real (`Proj_{C_r}(β̂)`, `+0.768` pp SS / `+0.286` pp UA over uniform weights, of a `3.44`/`1.32` pp closable headroom) and which part is noise inside a registered band; the negative results are stated as negatives; the debt recursion and its bound are verified twice.
- **Decisive rejection axis.** Contribution sufficiency: no prediction endpoint survives Holm anywhere; the paper's own evidence shows the full P2 is unnecessary for the structural gain it is credited with; and the two headline claims a reviewer would probe first (the band and the debt role) are the two that do not currently hold up textually.
- **AC stance.** Weak reject, upper edge, with the readiness weighted sum down `3.05 -> 2.90` while the progress delta is `−0.15` (`regressed`). The paper is one endpoint result and four sentence-level fixes away from a materially different conversation.
- **Discussion risks.** (i) If the band over-claim reaches a reviewer before it is fixed, the paper acquires an integrity complaint that is disproportionate to its actual evidential honesty. (ii) Once the "full P2 is unnecessary" reading is stated in the paper's own terms (`B2−B1` and `B3−B2` inside the band), the calibration program must be defended as *accounting and feasibility*, not as performance — the manuscript partly does this but the contributions still read as if calibration earns structural credit.

---

## 16. Quantitative Scores

```text
Quality: 4
Clarity: 3
Significance: 2
Originality: 2
Soundness: 4
Evidence: 3
Reproducibility: 2
Ethics / Limitations: not a frozen dimension in this contract (round-4 rubric uses Terminology/notation = 3 instead; limitations handling itself is adequate)
Overall: 5/10 (threshold 4/10)
Confidence: 4/5
Score-change conditions: see the table below
```

**Canonical scorecard (frozen round-4 dimensions).**

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Originality / novelty | 2 | 4 | `main.tex` L197-217, L314-323 | `W4` unresolved; raise by completing the FedIPW/FedPALS irreducibility mapping |
| Soundness / technical quality | 4 | 5 | `main.tex` L1145-1413, L1842-1847, L2015-2051, L2077-2097; `appendix.tex` L889-1144 | Deduct for `R5-1`, `R5-2`, `R5-4`, `R5-6`, `R5-7`; raise to 5 when the four text fixes land |
| Evidence / experiments | 3 | 5 | `main.tex` L1776-1935, L2099-2142; `round_v3`, `round_v4` | Deduct for no significant prediction endpoint and a 15-34 % reachable structural capture; raise with one endpoint win |
| Clarity / presentation | 3 | 5 | `main.tex` L601-608, L1544-1550, L1623-1637, L1842-1847 | Deduct for `R5-3`, `R5-11`, `R5-12`, `R5-15`, `N1`; raise on the four relabels |
| Reproducibility | 2 | 3 | `main.tex` L2200-2230 | `M7` bundle refresh plus inventory extension to the ladder/band artifacts |
| Significance / impact | 2 | 4 | `main.tex` L1818-1847, L2099-2142 | Reachable effect still the single Design ablation; raise with a task where alignment changes a decision |
| Related work / positioning | 3 | 3 | `main.tex` L277-329 | No new positioning evidence; raise with the `W4` mapping |
| Terminology / notation | 3 | 5 | `main.tex` L1844 vs L2088; L1826/L1924 vs L2102-2107; L605-606 | Deduct for three term collisions; raise with three one-line disambiguations |

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | The four `R5` text fixes (`R5-1`..`R5-4`) land without adding claims | Soundness, Clarity, Terminology | +0.5 to +1 overall |
| Raise score | One prediction endpoint becomes Holm-significant under a declared family, or the off-manuscript exogenous-target evidence is written in | Evidence, Significance | +0.5 overall |
| Raise score | The public bundle is refreshed and its inventory covers the ladder/band/trained-rule artifacts | Reproducibility | +0.25 to +0.5 overall |
| Lower score | A reviewer independently discovers the band's missing rule or the debt contradiction before they are fixed | Soundness, Clarity | −1 overall (to 4/10) |
| No quick change | A task where target-mass alignment converts to prediction; the FedIPW/FedPALS irreducibility proof | Evidence, Originality, Significance | unlikely before this submission |

---

## 17. Questions For Authors

1. In G-units, what exactly is the denominator `Δ_unif − Δ*` for each dataset, and what is its value in pp? L605-606 names the projected reference, but the printed `+0.922 pp ↔ −0.268` implies the hindsight-optimal reference (3.44 pp on SensorScope). Which is it?
2. Is the ±0.10 band read on the point estimate or on the 95 % interval? The evidence's own verdict cell for `B1(simoracle) − B1(raven)` = `+0.0639` `[−0.0020, +0.1214]` reads "outside the band", while L1843-1845 claims the oracle values are inside it.
3. Which two contrasts produce `+1.347 pp` (SS) and `+0.0073 pp` (SS) for "the debt recursion"? If they are the `κ`=1000 retrained rule versus the frozen `λ_g`=1, `η`=0.01 term, can the paper say so where each number appears, and can the "not a structural contributor" claim be scoped to the frozen configuration?
4. Given that `B2−B1` and `B3−B2` lie inside the registered band, what does the full (P2) contribute that `Proj_{C_r}(β̂)` does not — feasibility, accounting, or variance control — and is any of these measurable?
5. `M_r` is assumed shared and fixed (L606-607, L1115, L1283-1284), yet the replay residual shows it drifts with the model trajectory at `2e-6`-`3.7e-5`. Do the band intervals, some as narrow as `1.9e-4`, survive that drift?
6. Is the Design gate's `ρ_r` (42) a key-level quantity, and how does it relate to the region-level City Scanner row in the appendix?

---

## 18. Score Revision Criteria (version-comparison fields included)

```text
Raising the score would require: the four R5 text fixes (R5-1..R5-4) with no new claims; one prediction endpoint significant under a declared family; the repro-bundle inventory extended to the ladder/band artifacts
Lowering the score would be triggered by: a reviewer independently finding the band's missing decision rule or the debt contradiction; an error in the implied 3.44 pp denominator that changes a band verdict
Concerns unlikely to change before submission: W4 (FedIPW/FedPALS irreducibility); W6/M7 (bundle refresh); a task with external utility
Relative progress: weighted delta −0.15 => regressed (threshold 0.05); Evidence +1 (M8/W3 mechanism contrast now in-manuscript), Soundness −1, Clarity −1, Terminology −1
Absolute readiness: weighted sum 2.90 (was 3.05), stance 5/10 held (threshold 4/10); the stance is held because the strongest unresolved decision-relevant weakness (evidence/significance) is unchanged and the new decreases are text-level
Confidence and comparability: 4/5; contract unchanged (TMC-J-R4); historical scores inherited verbatim from the round-4 report rather than recomputed; the one non-comparability risk is that the round-4 report is in Chinese while this report is in English, with dimension identity preserved one-to-one
New issue provenance: R5-1, R5-2, R5-3, R5-4, R5-6, R5-7, R5-8, R5-11, R5-12, R5-14, R5-15, R5-16 = revision_regression; R5-5, R5-9, R5-17 = newly_revealed_by_evidence; R5-10, R5-13 = previously_undetected (applies to both versions)
Traceable score decreases: Soundness 5->4 (R5-1, R5-2, R5-4); Clarity 4->3 (R5-3, R5-11, R5-12, R5-15); Terminology 4->3 (R5-1, R5-16, R5-3)
```

---

## 19. Action Plan And CCFA Handoffs

```text
Priority: P0
Action: Reconcile the two "debt recursion" contrasts and scope the non-contributor claim to the frozen configuration (R5-1); rewrite L246-247 as interval containment and state the band's rule (R5-2); disclose the failed A2/B-G2/B-G3 gates at L2077-2097 (R5-4)
Owner skill: ccf-paper-writer
Input needed: round_v4 PART_A/PART_B reports; main.tex L1842-1847, L2081-2090, L2220-2230
Expected output: three paragraphs that cannot be read as self-contradiction or over-claim
Handoff required: yes
```

```text
Priority: P0
Action: Name and print the band's denominator; state which contrast each Design magnitude is (R5-3, R5-11); delete the L1547-1549 fragment (R5-12)
Owner skill: ccf-paper-writer
Input needed: round_v2 PHASE3_REPORT.md:77; main.tex L601-608, L1835-1840, L1544-1550
Expected output: a band a reader can convert to pp, and one Design magnitude per contrast
Handoff required: yes
```

```text
Priority: P1
Action: Add the flatness/mechanism sentence and the β̂-anchor conclusion (R5-5); define Proj_{C_r}(β̂) and label its new-rule status (R5-8); qualify "does not amplify" (R5-7)
Owner skill: ccf-paper-writer
Input needed: round_v3 EXECUTION_REPORT.md:132-134; round_v4 PART_A_REPORT.md:67
Expected output: the calibration's role stated as feasibility and accounting, with the surviving lever named
Handoff required: yes
```

```text
Priority: P1
Action: Extend the public bundle inventory to the round-v3/v4 ladder, band-decision and trained-rule artifacts (M7)
Owner skill: ccf-integrity-auditor
Input needed: RAVEN_MCS_PUBLIC_REPRO_R1 contents; results_w1_ladder/round_v3, round_v4
Expected output: the band and ladder claims become independently checkable
Handoff required: yes
```

```text
Priority: P1
Action: FedIPW/FedPALS variable-constraint-information mapping for the novelty boundary (W4)
Owner skill: ccf-literature-searcher
Input needed: morishita2026who, listozec2024overcoming, goetze2025floss full texts
Expected output: an irreducibility statement or a re-scoped novelty claim
Handoff required: yes
```

```text
Priority: P2
Action: Compression to buy room for the P0 text: move the coverage-Gate appendix propositions/corollaries to the artifact (C2); delete Proposition 4's unused derivative clause (C1); move Proposition 3's constant expansion to the supplemental (C1/C2)
Owner skill: ccf-paper-writer
Input needed: main.tex L1305-1333, L1343-1345, L1367-1413; appendix.tex L1282-1526
Expected output: ~50-60 main lines recovered with no claim withdrawn
Handoff required: no
```

```text
Priority: P2
Action: Adjudicate the key-level vs region-level ρ_r object and the appendix City Scanner row (N1)
Owner skill: ccf-paper-writer + user decision
Input needed: CS_PHI_DECISION.json, MAP_SUMMARY.csv, appendix.tex:2440
Expected output: one stated object relation
Handoff required: yes
```

```text
Checks run: full read of main.tex (2235 lines); targeted read of appendix.tex proofs for Proposition 4 (L889-931) and the debt bound (L932-1146); formal-environment inventory and `main.aux` numbering verified; page counts from main.log/supplemental.log; snapshot diff for provenance of four claims and of the duplicated clause; all four evidence rounds read (v2 via dossier + direct reads, v3 and v4 via dossier + direct reads of the decisive tables); arithmetic re-derivation of the FedAvg decomposition, the ζ/projection intervals, the G-unit denominator, and the debt-rule magnitudes
Checks skipped: line-by-line read of the remaining ~1,400 lines of appendix.tex; independent re-run of any experiment; verification of the public repro bundle contents; external related-work search; the manuscript's own prose-quality script (it times out on appendix.tex and was not run there)
Unresolved risks: the band's exact denominator is inferred from the printed conversion rather than stated anywhere; whether "their oracle values" (L1843) refers to the simoracle contrast is my inference from arm naming and not confirmed by a v4 oracle row; ERRATA_v3's own summary still lists R1/R2/R3/E7/E8 as "待" while PART_A records A1/A3 outcomes, so the closing status of those items is not determinable from the files read
```

---

## 20. Output Self-Check

1. Section order follows `fixed-output-format.md` §§1-16, with the requested scorecards at §11/§13 and the formalization centrepiece at §12. **Pass.**
2. Two scorecards are separate, computed under one frozen contract, and never fused. **Pass.**
3. Every score at or below 3 carries a concrete deduction and a raise condition. **Pass.**
4. Every decrease cites an issue ID, current-version evidence, origin, dimension and delta. **Pass** (§11 table).
5. No acceptance probability is stated; no score is rounded. **Pass.**
6. New issues carry provenance labels; a latent issue present in both versions (`R5-13`) is explicitly excluded from the progress delta. **Pass.**
7. The user's six tensions are each answered with `agree` / `partially` / `refute`, a line-anchored quote, and a consequence. **Pass** (§12.1).
8. What the formalization buys and what it costs are both stated, with line anchors. **Pass** (§12.2, §12.3).
9. No manuscript file was modified; the only write is this report. **Pass.**
