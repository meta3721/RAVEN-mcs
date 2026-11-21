# CCFA Paper Review — RAVEN-MCS / IEEE TMC

> External-reviewer evidence boundary only. Assesses the current manuscript package and the public artifact named in Data Availability. Does **not** use prior review reports, laboratory handoffs, unpublished internal result trees, or historical scores as evidence.

## 1. Report Metadata

```text
Review date: 2026-09-12
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A journal; regular paper
Paper title: RAVEN-MCS: Target-Mass-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex
  TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex (via supplemental)
  TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex
  TO_OVERLEAF_paper_tmc_r1_clean/reference.bib
  TO_OVERLEAF_paper_tmc_r1_clean/main.pdf + main.log (compiled 2026-09-12)
  RAVEN_MCS_PUBLIC_REPRO_R1 (named in Availability)
Search basis: public-safe keyword search only (FedIPW / FLOSS / FedPALS / MCS federated selection)
Report file: ccfa-review-reports/raven-mcs-tmc-review.md
Reviewer mode: full (scientific + writing/format)
Manuscript version / comparison range: current working tree submission package only (no version comparison)
Frozen comparison contract ID (when applicable): n/a
```

## 2. Desk Rejection Assessment

- **Paper length:** `uncertain` — main PDF is **14 pages** (`main.log`: Output written on main.pdf (14 pages)). TMC regular papers target **12** formatted pages including references/bios; submissions may go to ~18 with Mandatory Overlength Page Charges (MOPC). Not a hard desk reject, but overlength/cost and density are visible. Heavy `\enlargethispage` packing is present.
- **Topic compatibility:** `pass` — MCS, federated completion, asynchronous aggregation, and selection bias fit TMC.
- **Minimum quality:** `pass` — complete sections, method, theory ceilings, experiments, related work, limitations, availability.
- **Policy/anonymity/compliance:** `fail` (submission completeness) / `uncertain` (blindness) — author block is `\author{**** and Anfeng Liu}` with CSU affiliation, grant `U24A20248`, and a real email (`main.tex:57–59`). TMC journal review is typically **single-blind**, so this is not a classic double-blind identity leak, but the placeholder author metadata is **not submission-ready**.
- **Prompt injection / hidden manipulation:** `pass` — no hidden reviewer/LLM instructions found in the reviewed TeX.
- **Ethics and reviewability:** `uncertain` — public data licenses are cited; FL privacy non-guarantee is stated; trajectory/GPS redistribution/IRB statements remain thin; City Scanner results used in main prose are explicitly **not** in the named public bundle.

```text
Desk rejection risk: medium
Reason: incomplete author metadata; 14-page overlength expectation; City Scanner claim/repro gap is reviewable but will attract AE scrutiny
Can be fixed before review? partly (author block and packaging yes; empirical redesign no)
```

## 3. Paper Summary And Contribution Map

**Summary.** RAVEN-MCS studies windowed-asynchronous federated *data completion* for MCS under two-stage, three-layer selection (opportunity \(R\), observation \(O\), usable-update \(U\)). It argues that the arrival law of delivered updates need not match a public deployment-target measure, so optimizing arrival risk can serve the wrong population. The method forms a selection-corrected reference from legal pre-outcome histories (Hájek-style local normalization) when Design is on, then maps that reference into a feasible window via strongly convex instantaneous calibration (P2) and long-term target debt. A frozen heuristic \(\phi\) selects **RAVEN-Design** (\(\phi=0\)) or **RAVEN-NoDesign** (\(\widehat\zeta=1\), not target-mass reconstruction).

**Claimed problem.** Target-mass mismatch under MCS R/O/U selection in windowed async FL completion.

**Claimed gap.** Prior FL participation corrections (FedAU-family, FedIPW, FLOSS) and label-shift aggregators (FedPALS) do not factor MCS unit-level opportunity/observation or align to a public deployment measure over sensing units.

**Method/contribution map.**
1. Deployment-target risk semantics and non-interchangeability when laws differ.
2. Selection-layer-aware reference reconstruction with Design/NoDesign gated by \(\phi\).
3. Feasibility-aware calibration (unique P2 under A4) plus debt as accounting.

**Evidence package.** E2 risk non-interchangeability; E3 Table II on SensorScope/U-Air (protocol \(R\)); T-Drive hybrid with real taxi \(R\); NSW four-region and City Scanner hybrid rankings (tables largely in supplemental); E4 ablations; public tabular bundle for several sealed tables.

**Stated limitations.** No proof of deployment-risk optimization; NoDesign is not reconstruction; no jointly measured \(R/O/U\); SensorScope/U-Air not claimed as real mobile clients; FedAU/ObsUse are windowed adaptations; bundle is not a pinned retraining archive; City Scanner tables not bundled.

## 4. Search And Related-Work Basis

```text
Queries used:
  FedIPW FLOSS FedPALS federated inverse propensity
  federated learning mobile crowdsensing selection bias asynchronous
Sources searched:
  arXiv / OpenReview / DOI landing pages (public abstracts)
Closest works found:
  FedIPW / “Who Trains Matters” (enrollment–participation IPW) — cited as morishita2026who
  FLOSS (opt-out/straggler IPW) — cited
  FedPALS (target label-shift aggregation) — cited
  FedAU-style participation weighting — used as adapted baseline
Unverified related-work risks:
  Broader MCS sparse completion / recruitment literature is cited densely but not re-audited paper-by-paper here
  Whether any concurrent 2025–2026 MCS unit-level target-mass FL completion paper exists beyond the cited nearest-neighbor table was not exhaustively verified
Source-quality screening status:
  Closest FL selection papers above are peer-reviewed or arXiv preprints; manuscript already positions against them
```

## 5. Expected Review Outcome

```text
Expected outcome: Major revision (borderline negative)
Main accept signal: Clear MCS-specific R/O/U vs deployment-target framing; unusually honest claim ceilings and retained negatives
Main reject signal: No decisive prediction win on sealed main table; Design disabled on hard-support mobile/station blocks; City Scanner used in main narrative but absent from named public artifact; incomplete author metadata; package verify currently fails
Confidence: 4 / 5
```

## 6. Strengths And Weaknesses

### Strengths

- **Problem cut is TMC-native.** Separating deployment-target mass from arrival/usable-update law under MCS R/O/U is a coherent systems+learning formulation.
- **Claim ceilings are unusually disciplined.** Abstract/Intro/Theory/Conclusion repeatedly refuse “optimizes deployment risk,” refuse Holm RMSE wins, and label NoDesign as non-reconstruction.
- **Closest FL selection work is positioned honestly.** FedIPW/FLOSS/FedPALS are cited as client-roster or label-marginal objects, not pretended MCS unit baselines.
- **Negatives are retained in main text.** T-Drive loss to FedAU/ObsUse; U-Air forced-Design reversal; Use ablation null effects.
- **Core Table II / T-Drive / NSW tabular cells are auditable** when rebuild scripts run, and numbers match the manuscript at four decimals.

### Weaknesses

```text
Weakness: Author block is incomplete / inconsistent
Evidence basis: main.tex:57–59 (**** + Anfeng Liu + grant + emails)
Reviewer deduction: submission-readiness / professionalism; possible AE bounce before full review
Required fix: finalize anonymity or camera-ready author metadata consistently
```

```text
Weakness: Headline Design correction is off precisely where support conflict is largest
Evidence basis: U-Air φ=35.4% and T-Drive φ=47.4% use RAVEN-NoDesign; paper admits ζ̂=1 is not target-mass reconstruction
Reviewer deduction: Soundness/Evidence — method identity fragments into Design vs fallback
Required fix: keep separate claim/tables (already partly done) and demote “target-mass calibrated” marketing on NoDesign rows
```

```text
Weakness: Main empirical centerpiece does not show a decisive RMSE win
Evidence basis: Table II caption and prose: descriptive +0.5% tolerance; no Holm-significant RMSE win; strongest recurring signal is structural Δ
Reviewer deduction: Evidence/Significance for a systems method paper
Required fix: either strengthen prediction evidence under jointly measured selection, or narrow contribution to structural target-mass alignment
```

```text
Weakness: City Scanner is used in main prose/conclusion but not in the named public bundle
Evidence basis: main.tex Availability 1958–1960; MANIFEST has 0 city/scanner hits; tables live in supplemental/appendix
Reviewer deduction: Reproducibility and Evidence auditability for abstract/hybrid narrative
Required fix: ship SUMMARY/PAIRED/PHI for City Scanner or remove those rankings from main claim chain
```

```text
Weakness: Named public package currently fails integrity verification
Evidence basis: python verify.py → checked=1886 mismatches=2 (scripts/rebuild_table_ii.py, tdrive/TD_R_FREEZE.json)
Reviewer deduction: Reproducibility — “frozen” artifact claim is not currently true as delivered
Required fix: refresh MANIFEST or restore exact bytes; document scipy for Holm rebuild
```

## 7. Potentially Missing Related Work

```text
Work: FedIPW / Who Trains Matters (enrollment–participation IPW)
Status: searched + already cited in manuscript
Why relevant: closest two-stage FL selection vocabulary
Overlap: client-roster selection correction
Needed comparison: conceptual only (already argued); not required as MCS completion baseline
```

```text
Work: FLOSS
Status: searched + cited
Why relevant: opt-out/straggler IPW aggregation
Overlap: participation reweighting
Needed comparison: already positioned as client-level, not unit-level R/O/U
```

```text
Work: FedPALS
Status: searched + cited
Why relevant: target-aware aggregation under label shift
Overlap: “target” language
Needed comparison: manuscript correctly distinguishes label marginals vs MCS deployment measure; optional empirical comparator if space allows
```

```text
Work: Broader MCS sparse-completion / incentive / privacy concurrent 2025–2026 pieces
Status: unverified exhaustively
Why relevant: dense citation dump in Related Work may still miss a concurrent unit-level target-mass FL completion paper
Overlap: unknown
Needed comparison: AE may ask for one clearer nearest MCS system baseline table in main text (supplement already has nearest-neighbor table)
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| Arrival vs deployment risks need not be interchangeable | Abstract; Prop. risk | E2 figure/analysis; theory | adequate–strong | none if kept functional | keep current ceiling |
| Ideal Design recovers compatible target moments/group mass | Intro; Prop. reconstruction | Assumptions A1–A3; proofs in supplemental | adequate | does not imply Y-risk optimization (already hedged) | none |
| RAVEN-Design improves structural alignment on SensorScope | Table II | Δ_group / Δ_c-s numbers; rebuild OK | adequate | not an RMSE win | keep structural primary |
| U-Air NoDesign stays within +0.5% worst-group tolerance vs FedAU/ObsUse | Table II prose | TEST +0.48/+0.44; ALL20 +0.002/+0.075; Holm n.s. | adequate | tolerance is descriptive, slice-sensitive messaging remains | keep BOTH slices in captions |
| T-Drive shows real-\(R\) ranking where FedAU/ObsUse win | Main T-Drive table | packaged CSV match; +2.39/+2.43 outside tolerance | strong (negative) | weakens deployment-dominance claim | keep honesty |
| City Scanner hybrid supports multi-city narrative | Intro/Eval/Conclusion | supplemental tables; **not bundled** | weak for public audit | reproducibility | bundle or demote |
| Bundle enables verification of tabulated cells | Availability | verify currently **fails** (2 mismatches); rebuild scripts otherwise OK | weak–adequate | frozen-artifact claim overstated today | repair MANIFEST |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines:** FedAvg-Window, TwoStage-Hájek, FedAU-Window, ObsUse-Window, plus supplemental same-backbone family. FedAU/ObsUse correctly disclosed as adaptations, not official reproductions — fair but lowers authority.
- **Ablations:** E4 component effects present; residual risk that a short Holm CSV may disagree with table asterisks if both are inspected (paper tracks the component-effects table).
- **Datasets:** SensorScope, U-Air (protocol, not claimed mobile clients); T-Drive real \(R\) with controlled \(O/U\); NSW four-region; City Scanner hybrid/P2.
- **Metrics:** RMSE\(_\mu\), WorstGroupRMSE, \(\Delta_{\mathrm{group}}\), \(\Delta_{c\text{-}s}\). Structural metrics carry much of the positive story.
- **Statistical rigor:** Wilcoxon/Holm families disclosed; descriptive +0.5% point-estimate tolerance explicitly not NI; ALL20 vs TEST10 now stated. Good for honesty; still not a strong superiority package.
- **Robustness/failure:** Design reversal on U-Air; T-Drive loss; forced Design diagnostic retained.
- **Artifacts:** Table II, Holm-vs-FedAU/ObsUse, slice relatives, T-Drive, NSW `new_target/` present. City Scanner absent. Train dumps/checkpoints not included (disclosed). **`verify.py` currently reports 2 hash mismatches.**
- **Limitations:** Mostly honest and aligned with evidence.

## 10. Multi-Reviewer Panel

```text
Reviewer: Best-Justified
Expertise: MCS systems / FL applications
Likely score: 6 / 10
Confidence: 4
Main positive signal: Genuine MCS selection factorization and honest multi-dataset negatives
Main negative signal: Weak prediction dominance; hybrid/protocol evidence
Evidence basis: Intro contributions; Table II; T-Drive; Availability
Score-change condition: one jointly measured R/O/U mobile study with stable prediction benefit
```

```text
Reviewer: Critical
Expertise: skeptical CCF-A gatekeeping
Likely score: 3–4 / 10
Confidence: 4
Main positive signal: Claim hygiene reduces fraud risk
Main negative signal: Method becomes NoDesign on hard blocks; City Scanner unreproducible from named bundle; author metadata incomplete
Evidence basis: φ>0 rows; Availability 1958–1960; author block
Score-change condition: bundle CS + single deployable method identity + clean submission metadata
```

```text
Reviewer: Method / Soundness
Expertise: selection bias / survey sampling / FL theory
Likely score: 4 / 5 criterion (~ borderline overall)
Confidence: 4
Main positive signal: Theory ceilings match proofs; Design/NoDesign named
Main negative signal: φ is heuristic not positivity; NoDesign changes estimand
Evidence basis: eqs scd_phi; A1/A5 discussion; Alg. 1
Score-change condition: support tests on target-positive pairs or permanently demote φ to deployment rule only
```

```text
Reviewer: Evidence / Experiment
Expertise: empirical FL / MCS evaluation
Likely score: 3 / 5 criterion
Confidence: 5
Main positive signal: Table II/T-Drive/NSW numbers match package; Holm/ALL20 disclosed
Main negative signal: mixed prediction; CS missing; verify hash drift
Evidence basis: verify.py; rebuild scripts; MANIFEST
Score-change condition: clean verify + CS package or demotion; stronger mobile win
```

```text
Reviewer: Novelty / Positioning
Expertise: FL participation / target shift
Likely score: 3 / 5 criterion
Confidence: 4
Main positive signal: FedIPW/FLOSS/FedPALS distinctions are real and cited
Main negative signal: ingredients (IPW, Hájek, calibration) are established; novelty is integration
Evidence basis: Related Work L300–314; public search
Score-change condition: sharper one-sentence delta vs nearest MCS completion system paper in main text
```

```text
Reviewer: Writing / Clarity
Expertise: scientific communication
Likely score: 3–4 / 5 criterion
Confidence: 4
Main positive signal: Design/NoDesign vocabulary reduces earlier confusion
Main negative signal: dense abstract; off-main tables cited with numbers; 14-page packing; Table II overfull
Evidence basis: abstract; City Scanner cites; main.log Overfull 5.6pt
Score-change condition: compress abstract; move one hybrid table into main or demote numbers
```

```text
Reviewer: Ethics / Reproducibility
Expertise: artifacts / data governance
Likely score: 2–3 / 5 criterion
Confidence: 5
Main positive signal: Availability discloses table-only scope and CS omission
Main negative signal: verify fails; CS used in narrative; author placeholders; thin trajectory governance
Evidence basis: Availability; verify.py; author block
Score-change condition: MANIFEST repair + CS packaging decision + complete author metadata
```

```text
Agreement: Claim honesty and MCS framing are strengths; empirical prediction dominance is not established
Disagreement: Whether NoDesign honesty is enough for acceptance vs fatal method-identity fracture
Decisive positive axis: R/O/U vs deployment-target formulation + disciplined ceilings
Decisive negative axis: missing decisive mobile/joint evidence + incomplete public packaging for cited hybrid results + submission metadata
Unresolved evidence: end-to-end retrain; official FedAU/ObsUse reproductions; exhaustive concurrent MCS literature
AC stance: Major revision — do not accept in present form; not a clear desk reject if author metadata is fixed and AE tolerates overlength
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | major | Incomplete author metadata (`****` + real coauthor) | main.tex:57–59 | Ethics / Quality | ethics/limitations | Finalize author block for ScholarOne | ccf-paper-writer | Required before clean submission; +0.5 overall if only blocker removed |
| C2 | major | Design off on hard-support blocks; NoDesign is different estimand | U-Air/T-Drive φ>0; Alg. 1 | Soundness / Evidence | method/soundness | Keep Design/NoDesign claims strictly separated; demote target-mass marketing on NoDesign | ccf-paper-writer | +0.5 if identity unambiguous and abstract matches |
| C3 | major | No decisive sealed RMSE win; tolerance/structure carry the story | Table II; Holm n.s. | Evidence / Significance | experiment | Narrow claim to structural alignment or add joint R/O/U mobile win | ccf-experiment-designer | +1 Evidence if joint mobile prediction win appears |
| C4 | major | City Scanner cited in main but not in named public bundle | Availability 1958–1960; MANIFEST | Reproducibility / Evidence | reproducibility | Bundle CS tables or remove from abstract/conclusion emphasis | ccf-submission-checker | +1 Repro if bundled with rebuild check |
| C5 | major | Public package `verify.py` currently fails (2 mismatches) | verify.py output | Reproducibility | reproducibility | Repair MANIFEST / restore bytes; pin scipy for Holm | ccf-submission-checker | +0.5–1 Repro when verify is clean |
| C6 | moderate | 14-page main + packing / Table II overfull | main.log | Clarity / venue | compression | Reduce density or accept MOPC consciously | ccf-paper-writer | Clarity +0.5 if readable without stuffing |
| C7 | moderate | φ heuristic / cross-block π^tar constructions | main + appendix φ freeze | Soundness | method/soundness | Keep heuristic label; optional target-positive support test | ccf-paper-writer | Soundness +0.5 with stronger support test |
| C8 | minor | Abstract still dense; math tokens in abstract | abstract ~191 words | Clarity / writing | writing | Compress; remove `$...$` | ccf-paper-writer | Clarity local fix |

## 12. AC / Meta-Review

Reviewers agree the paper is **scientifically careful** and **topic-fit for TMC**, with a real MCS selection framing and unusually honest negatives. They also agree it is **not acceptance-ready**: the sealed main prediction story is interchangeability/tolerance rather than superiority; Design is inactive on the hardest blocks; City Scanner evidence is off-bundle while still used narratively; and the delivered public package currently fails hash verification. The incomplete author block is a practical submission blocker even under single-blind journal review.

**AC stance:** **Major revision.** Borderline-negative calibrated quality. A sympathetic AE may send for review after metadata cleanup; a strict AE may bounce on packaging/overlength first.

**Discussion risks:** Reviewers may talk past each other—one praising honesty, one rejecting for lack of a clean empirical win. Authors should decide whether the paper is a *structural target-mass systems* paper or a *prediction-accuracy* paper and align abstract, tables, and artifact to that choice.

## 13. Quantitative Scores

| Dimension | Score (1–5) | Confidence | Evidence basis | Deduction | Repair condition | Expected score movement |
| --- | ---: | ---: | --- | --- | --- | --- |
| Quality | 3 | 4 | Complete but not decisive package | Mixed prediction + packaging gaps | Clean artifact + clearer empirical win or narrowed claim | +1 if C3–C5 fixed |
| Clarity | 3 | 4 | Design/NoDesign helps; density/overlength hurts | Dense abstract; off-main numeric cites | Compress; move/demote CS numbers | +0.5–1 |
| Significance | 3 | 4 | Relevant MCS problem | No joint R/O/U deployment win | Joint mobile study | +1 |
| Originality | 3 | 4 | Integration novelty over FedIPW/FLOSS/FedPALS | Ingredients known | Sharper main-text nearest MCS delta | +0.5 |
| Soundness | 4 | 4 | Theory ceilings match text; Design/NoDesign named | φ heuristic; estimand switch | Keep ceilings; optional support test | +0.5 |
| Evidence | 3 | 5 | Table II/T-Drive/NSW match; CS missing; mixed ranks | CS + weak prediction dominance | Bundle CS or demote; strengthen mobile evidence | +1 |
| Reproducibility | 2 | 5 | verify fails; table rebuilds otherwise OK; no train archive | Hash drift + CS omission | Repair MANIFEST; bundle CS or demote | +1–2 |
| Ethics / Limitations | 3 | 4 | Strong claim honesty; weak author metadata / thin GPS governance | Author placeholders | Complete metadata; strengthen data governance | +0.5–1 |

```text
Quality: 3
Clarity: 3
Significance: 3
Originality: 3
Soundness: 4
Evidence: 3
Reproducibility: 2
Ethics / Limitations: 3
Overall: 5 / 10
Confidence: 4 / 5
Score-change conditions:
  +1 overall if City Scanner is bundled or removed from main claim chain AND verify.py is clean AND author metadata is complete
  +1 further if a jointly measured R/O/U mobile ranking shows a stable prediction benefit under the claimed method identity
  −1 if Design/NoDesign ceilings are re-blurred or CS is marketed without packaging
```

**Calibrated stance:** **Major revision / borderline negative (5/10).**  
**CSPaper-style band (approximate):** average/borderline for TMC CCF-A — not bottom-tier, not accept-ready.

## 14. Questions For Authors

1. Under single-blind TMC submission, when will the `****` author placeholder be replaced with final metadata?
2. Should City Scanner be treated as a main claim or a supplemental illustration? If main, where are the public CSVs?
3. For U-Air/T-Drive, is the claimed deployed method RAVEN-NoDesign, and if so should the title/abstract lead with “support-conditional Design with NoDesign fallback” rather than uniform target-mass calibration?
4. Why should a reader treat the descriptive +0.5% TEST tolerance as decision-relevant when ALL20 relatives are near zero and Holm tests are non-significant?
5. Can `verify.py` be made to pass on the exact bytes reviewers download?

## 15. Score Revision Criteria

```text
Raising the score would require:
  complete author metadata; clean public-package verify; City Scanner packaging decision executed; and either a joint R/O/U mobile win or an explicitly narrowed structural-alignment claim ceiling matched by abstract/title
Lowering the score would be triggered by:
  re-introducing RMSE-superiority language without Holm/joint evidence; silently relying on unbundled tables; or theory claims that Design-off reconstructs target mass
Concerns unlikely to change before submission:
  FedAU/ObsUse remaining adaptations; SensorScope/U-Air not being real mobile clients; train-level repro remaining optional unless a pinned archive is released
```

## 16. Action Plan And CCFA Handoffs

```text
Priority: P0
Action: Replace author placeholders; decide single-blind final author list
Owner skill: ccf-paper-writer
Input needed: real author metadata
Expected output: submission-ready author block
Handoff required: yes
```

```text
Priority: P0
Action: Repair RAVEN_MCS_PUBLIC_REPRO_R1 MANIFEST (or restore drifted files) until verify.py is clean; document scipy for Holm rebuild
Owner skill: ccf-submission-checker
Input needed: current bundle bytes
Expected output: verify checked=N mismatches=0
Handoff required: yes
```

```text
Priority: P0
Action: Bundle City Scanner ranking CSVs + rebuild check, OR demote CS from abstract/conclusion/main numeric emphasis
Owner skill: ccf-submission-checker / ccf-paper-writer
Input needed: CS SUMMARY/PAIRED/PHI or revised prose
Expected output: claim–artifact alignment
Handoff required: yes
```

```text
Priority: P1
Action: Align title/abstract method identity with Design vs NoDesign evidence map; compress abstract; fix Table II overfull
Owner skill: ccf-paper-writer
Input needed: current main.tex
Expected output: clearer contribution sentence + cleaner PDF
Handoff required: yes
```

```text
Priority: P2
Action: Add jointly measured R/O/U mobile evidence, or permanently adopt protocol/hybrid-only claim ceiling
Owner skill: ccf-experiment-designer
Input needed: new study or explicit ceiling text
Expected output: significance upgrade or locked narrower claim
Handoff required: yes
```

```text
Checks run:
  desk pass on main.tex/pdf/log
  contribution/evidence/adversarial passes on main+appendix
  public-safe related-work keyword search (FedIPW/FLOSS/FedPALS)
  python verify.py (1886 checked, 2 mismatches)
  rebuild_table_ii.py OK
  rebuild_table_ii_tolerance.py OK
  Holm/SLICE CSV consistency check (scipy available in local venv)
Checks skipped:
  full GPU retraining
  exhaustive concurrent MCS literature audit
  official FedAU/ObsUse reproduction from upstream repos
  reading prior ccfa-review-reports / lab handoffs (excluded by evidence boundary)
Unresolved risks:
  whether AE treats 14-page packing + CS off-bundle as pre-review bounce
  whether NoDesign-on-hard-blocks is judged fatal by a theory-oriented reviewer
```

## Output Self-Check

- Section order matches `fixed-output-format.md`.
- Scores: overall 5 matches strongest unresolved major concerns (C3–C5), not averaged away.
- No acceptance probability claimed.
- Evidence boundary excludes historical reviews and lab-only materials.
- Recommended next CCFA owner: `ccf-paper-writer` for metadata/claim identity; `ccf-submission-checker` for artifact repair/CS packaging.
