# CCFA Paper Review — RAVEN-MCS / IEEE TMC

> `ccf-paper-reviewer` full re-review of the current canonical manuscript (pass 2026-09-11-post-revisions). This pass is an independent full re-read of the revised `main.tex` after the user's modifications, including the new hybrid rankings (T-Drive real-\(R\) ranking, City Scanner NY \(PM_{2.5}\) visit-occupancy hybrid, City Scanner Pilot~2 measured-\(O\) hybrid) and the honest mixed-ledger framing. Assessment only; no rewrite. Relative progress versus the prior canonical review and absolute TMC readiness are two non-fused scorecards. Conclusions are consistent with the prior pass (Overall 7, weak-accept / major-revision).

## 1. Report Metadata

```text
Review date: 2026-09-11 (post-revisions re-review, pass 3)
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A, regular paper (journal)
Paper title: RAVEN-MCS: Target-Risk-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex
  TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex (via supplemental.tex \input)
  TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex
  TO_OVERLEAF_paper_tmc_r1_clean/reference.bib
  compiled this cycle: main.pdf 14 pages; supplemental.pdf 13 pages
  RAVEN_MCS_PUBLIC_REPRO_R1/verify.py (checked=1883 mismatches=0)
  RAVEN_MCS_PUBLIC_REPRO_R1/tables/SCD_PHI.csv
  post_review/GPT_C2_atomic_target/GPT_C2_CLOSE_REPORT.md (locator only)
  prior canonical review overwritten in place
Search basis:
  Public-safe queries (no private manuscript sentences):
    IEEE Computer Society author-resources page length / MOPC (re-fetched 2026-09-11)
    FLOSS (Goetze et al., PACMI 2025, ACM 10.1145/3766882.3767180)
    FedIPW / Who Trains Matters (arXiv:2604.26604)
Report file: ccfa-review-reports/raven-mcs-tmc-review.md
Reviewer mode: full (scientific + writing + format + AC synthesis + re-review comparison)
Manuscript version / comparison range:
  historical = 2026-09-11 canonical after Table XXII ingest, before GPT-C1/C2 writing closes
  current = same tables/numbers; OFF presented as uncorrected ζ=1; I_tar / C_t / φ lookup defined (details in appendix)
Frozen comparison contract ID: raven-mcs-tmc-r1-2026-09-11-pass3 (re-review; contract/anchors/roles unchanged)```

## 2. Desk Rejection Assessment

```text
Check: Paper length
Status: uncertain / overlength-charge risk, not desk-fail
Evidence: main.pdf 14 double-column pages including references. IEEE CS author-resources (2026-09-11): Transactions regular papers 12 formatted pages including abstracts, references, and biographies; excess after final layout is MOPC ($220/page on that page). TMC is listed. A third-party TMC note still mentions submissions up to 18 pages subject to MOPC; first-party CS page states submission caps can differ from published length. Supplemental PDF is 13 pages, separate, no CS cap.
Consequence: not a scientific desk reject; camera-ready MOPC or compression remains.
Required action: confirm TMC ScholarOne submission cap; compress toward 12 if MOPC is unacceptable.
```

```text
Check: Topic compatibility
Status: pass
Evidence: windowed-asynchronous federated MCS completion under non-random R/O/U selection.
Consequence: inside TMC mobile-systems / crowdsensing / FL remit.
Required action: none
```

```text
Check: Minimum quality
Status: pass
Evidence: abstract, introduction, related work, model, method, theory, evaluation, limitations, conclusion, availability, bibliography, separate supplement. Algorithm 1, Tables II–III and hybrid tables, Prop. 1–2, coverage theorem.
Consequence: reviewable.
Required action: none
```

```text
Check: Policy / anonymity / compliance
Status: fail for ScholarOne readiness; not a scientific desk reject
Evidence: author block `**** and Anfeng Liu`, grant U24A20248, CSU affiliation and email. TMC is named-author.
Consequence: upload blocked until the placeholder is replaced or fully anonymized under the journal’s actual mode.
Required action: complete author list after explicit authorization.
```

```text
Check: Prompt injection and hidden manipulation
Status: pass
Evidence: no reviewer- or LLM-directed hidden instructions in running prose, captions, or bibliography keys inspected this pass. No C1/C2/kill-bar language in the manuscript.
Consequence: none
Required action: none
```

```text
Check: Ethics and reviewability
Status: pass with disclosure
Evidence: public datasets; City Scanner Zenodo 10.5281/zenodo.7961851, CC BY 4.0; T-Drive follows published terms; FL is not a privacy guarantee. Tables XXI/XXII disclosed as not in the named bundle.
Consequence: reviewable; artifact completeness is a reproducibility deduction, not ethics fail.
Required action: ship XXI/XXII sources if they remain part of the paper claim.
```

```text
Desk rejection risk: low
Reason: topic, minimum quality, and ethics clear a TMC desk. Author placeholders block a clean ScholarOne upload. Length is above the 12-page published length and inside common CS submission practice with MOPC.
Can be fixed before review? yes (author block); partly (compression / MOPC)
```

## 3. Paper Summary And Contribution Map

RAVEN-MCS treats windowed-asynchronous federated MCS completion as alignment with a public deployment target rather than with the arrival law of usable updates. Sensing is factored into opportunity \(R\), observation \(O\), and usable-update \(U\). The server reconstructs target-relevant mass from legal pre-outcome histories and calibrates that reference inside the current feasible window (P2), carrying residual group under-service as target debt. Design uses the lagged target-mass opportunity ratio if and only if the train-unit zero-target fraction \(\phi=0\); when \(\phi>0\), that factor is \(\widehat\zeta=1\) and is not target-mass reconstruction. Coverage \(C_t\) is now a mass of target-positive client–stratum pairs; \(\phi\) is a lookup of the same frozen \(\pi^{\mathrm{tar}}\) map.

- Claimed problem: arriving updates need not be sampled from the deployment population the predictor is intended to serve.
- Claimed gap: sparse MCS completion, asynchronous FL, and participation-aware FL do not jointly identify sensing-side availability versus update-side usability, nor map a reconstructed target onto a finite mobile window.
- Method/contribution map:
  1. Deployment-target versus arrival-risk semantics; non-interchangeability when the two laws differ.
  2. Layer-aware reconstruction (Design / Obs / Use) with legal histories; SCD \(\phi=0\) as a frozen support safeguard; OFF is an uncorrected opportunity factor.
  3. Feasibility-aware calibration (P2 unique minimizer) plus internal target debt.
- Evidence package: E1 no-harm; E2 NSW risk-semantic \(D_{\mathrm{aligned}}\); E3 Table II/III (20 seeds, protocol \(R\)); E4 one-factor ablation; T-Drive hybrid (10 seeds, main); NSW four-region (appendix); City Scanner controlled-\(O\) hybrid (Table XXI); Pilot~2 measured-\(O\) hybrid (Table XXII); occupancy-robustness and coverage-Gate audit in the supplement; named public bundle for Table II / T-Drive / NSW; `verify.py` 1883/0.
- Stated limitations: SCD not derived from A1/A5; SensorScope/U-Air retrospective for the switch; no Holm RMSE win over adapted FedAU/ObsUse on the main table; T-Drive outside the \(+0.5\%\) descriptive tolerance; Table XXI FedAvg lowest on prediction; Table XXII Hájek lowest on RMSE/WG; Gate does not switch Design; jointly measuring \(U\) remains future work.

## 4. Search And Related-Work Basis

```text
Queries used:
  IEEE Computer Society author-resources page length MOPC
  FLOSS federated learning inverse propensity weighting Goetze PACMI 2025
  Who Trains Matters FedIPW federated learning inverse propensity 2026 arXiv
Sources searched: computer.org author-resources (2026-09-11); ACM 10.1145/3766882.3767180; arXiv:2507.23115; arXiv:2604.26604
Closest works found:
  FLOSS (Goetze et al., PACMI 2025): client-level IPW for opt-out/stragglers
  FedIPW (“Who Trains Matters”, arXiv:2604.26604): two-stage enrollment then round participation toward a target-population mean update
  FedPALS (prior positioning, arXiv:2411.03799): aggregation toward a known target label distribution
  FedAU (Wang et al.): participation-history reweighting to preserve the original FL objective
Unverified related-work risks:
  FedCure is cited as excluded, not compared
  Official FedAU / TimeAlign reproductions are not claimed
  FedPALS bibliographic status remains preprint
  FedIPW camera-ready venue not confirmed this pass
Source-quality screening status: FLOSS ACM proceedings accepted as closest client-level IPW; FedIPW/FedPALS retained as object-split positioning already in §Related Work; MDPI excluded
```

The object split remains defensible: FLOSS/FedIPW/FedAU operate on the client roster; FedPALS on label marginals; RAVEN-MCS on MCS unit-level \(R/O/U\) and a public measure over \(h(i)\). Writing closes of GPT-C1/C2 do not collapse that split. They also do not make the implemented stack the best predictor on a jointly measured mobile process.

## 5. Expected Review Outcome

```text
Expected outcome: weak accept leaning (Overall 7/10)
Main accept signal: scoped TMC problem; honest hybrid ledger; Table XXII measured O with Hájek-lowest disclosed; OFF now stated as uncorrected ζ=1; I_tar and C_t defined; Table II unmixed; verify.py 0 mismatches.
Main reject signal: the method stack is still not the best mobile predictor (Hájek wins Table XXII; FedAvg wins Table XXI; FedAU/ObsUse win T-Drive); U remains controlled; Use/Debt have no isolated E4 effect; Table II is protocol R on station traces; φ=0 remains a frozen protocol, not a derived switch.
Confidence: 4/5
```

Stance band: **lean accept**. Relative interpretation (approximate, not an official cutoff): **above-average** as a scoped TMC problem-and-protocol paper with an honest hybrid ledger; **not yet a clear MCS-system accept** if the bar is “the proposed stack is the best predictor under jointly measured mobile layers.”

Relative progress versus the previous canonical review is **improved on definitional issues, unchanged on overall score**. Absolute readiness remains **weak accept / 7**, not a clear TMC accept. Those two statements are not fused.

## 6. Strengths And Weaknesses

**Strengths**

- Problem is TMC-native: windowed-asynchronous MCS completion under non-random \(R/O/U\), not a generic FL IPW rebrand.
- Claim language tracks the tables: T-Drive loss, Table XXI FedAvg-lowest, Table XXII Hájek-lowest, controlled \(U\), no mix into Table II.
- GPT-C1 is writing-closed: Design off is an uncorrected opportunity factor \(\widehat\zeta=1\), not target-mass reconstruction (abstract, Alg. 1 ELSE, limitations, conclusion).
- GPT-C2 is writing-closed: \(I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}\); \(C_t\) sums over those pairs; \(\phi\) looks up \(\pi^{\mathrm{tar}}(k(i),s(i))\) with missing key 0; constructions sit in `app:itar_lookup` and Table XX.
- Closest two-stage FL work (FedIPW) and client-level IPW (FLOSS) are cited with an object split.
- Named bundle verifier currently passes (`checked=1883 mismatches=0`).

**Weaknesses**

```text
Weakness: On the only ranking with real taxi mobility, support-conditional RAVEN loses the paper’s own external +0.5% rule versus adapted FedAU and ObsUse.
Evidence basis: tab:tdrive_hybrid; paired relative +2.39% / +2.43%; abstract and conclusion still state this.
Reviewer deduction: Significance cannot be 5 while the taxi hybrid favors the simpler corrections.
Required fix: jointly measure U (or a taxi O layer) on T-Drive, or keep T-Drive as the main negative taxi finding.
```

```text
Weakness: On the measured-O ranking, TwoStage-Hájek is lowest on RMSE_μ and WorstGroupRMSE; SCD is not the strongest method.
Evidence basis: Table XXII; Hájek 0.7097 / 0.7273 vs SCD 0.7135 / 0.7311.
Reviewer deduction: a TMC systems reader can still say the full stack is not needed for prediction on this table.
Required fix: do not write SCD as the Pilot~2 RMSE winner (current text does not).
```

```text
Weakness: The main effectiveness table is not a mobile-opportunity ranking.
Evidence basis: Table II; SensorScope/U-Air protocol R always-on; original traces not claimed to contain mobile clients.
Reviewer deduction: a TMC systems reader can treat Table II as a development table.
Required fix: keep Table II as protocol development; do not let it be read as the MCS-system ranking.
```

```text
Weakness: Usable-update correction and target debt have no isolated empirical effect in E4, and U is still a control on every hybrid ranking including Table XXII.
Evidence basis: §Limitations; E4; conclusion “Measuring the usable-update layer jointly with observation remains future work.”
Reviewer deduction: the implemented stack is larger than the empirically active factors (Design/Obs/P2).
Required fix: leave Use/Debt as factorization/accounting, or later shrink Algorithm 1; measuring U is a new experiment.
```

```text
Weakness: φ=0 remains a global frozen protocol. OFF sets ζ=1 on all observed pairs, including target-zero units. That is now labeled correctly; it is still not a restricted-support or positivity-derived rule.
Evidence basis: eq:scd_phi; Alg. 1 ELSE; A5; app:itar_lookup (φ is not #{i:ϖ_i=0}); Table XX per-block constructions differ.
Reviewer deduction: Soundness 5 would need a derived support rule or a restricted-support OFF policy. Writing close does not raise Soundness above 4.
Required fix: keep the current “safeguard not optimum / uncorrected OFF” wording, or change the OFF rule (would move U-Air/T-Drive; not authorized as writing).
```

```text
Weakness: Title and abstract still say target-risk alignment; Proposition 2 recovers compatible target moments or group mass, not Y-risk optimization.
Evidence basis: title; abstract lines 70–77; Prop. 2 scope; local steps use Z not Y.
Reviewer deduction: “target-risk-calibrated” is best read as target-mass-calibrated aggregation. Not a claim contradiction because the paper states the boundary, but a TMC reader can still over-read the title.
Required fix: leave the scoped Prop. 2 sentence; optional title/abstract narrowing is writing, not new evidence.
```

## 7. Potentially Missing Related Work

```text
Work: FLOSS (Goetze et al., PACMI 2025, ACM 10.1145/3766882.3767180)
Status: searched
Why relevant: client-level IPW for opt-out and stragglers
Overlap: IPW aggregation under non-random missingness; different object (client roster vs MCS units)
Needed comparison: citation-and-split is already in §Related Work; empirical comparator not required if the object split is kept
```

```text
Work: FedIPW / “Who Trains Matters” (arXiv:2604.26604)
Status: searched
Why relevant: two-stage enrollment then participation toward a target-population mean update
Overlap: two-stage selection vocabulary; still client-roster IPW, not unit-level R/O/U
Needed comparison: already cited as nearest enrollment–participation IPW, not as an MCS baseline
```

```text
Work: FedPALS (Listo Zec et al., arXiv:2411.03799)
Status: searched (prior positioning; preprint)
Why relevant: aggregation toward a known target label distribution
Overlap: “target-aware” wording only; object is class-label marginals
Needed comparison: already excluded as a comparator with an object-split sentence
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| Arrival and deployment risks are not interchangeable when the laws differ | Abstract; Prop. 1; Fig. 2 | NSW E2 \(D_{\mathrm{aligned}}\) negative shift | adequate | Keep as the theory headline | None |
| Design off is uncorrected \(\widehat\zeta=1\), not target-mass reconstruction | Abstract; Alg. 1 ELSE; limitations; conclusion | Same numbers as before; wording now matches the OFF branch | adequate as claim-scope | Does not make OFF target-mass-preserving | Do not restore “reconstruction when φ>0” |
| \(I_{\mathrm{tar}}\), \(C_t\), and \(\phi\) use the frozen \(\pi^{\mathrm{tar}}_{k,s}\) map | eq:agg_Ct; eq:scd_phi; app:itar_lookup; Table XX | Definitions now present; φ counts frozen and disclosed per block | adequate as protocol | φ is still not \(\varpi_i=0\); constructions differ by block | Do not unify φ by recomputing U-Air |
| SCD applies Design iff \(\phi=0\) | Abstract; Alg. 1; eq:scd_phi | Table XX: SS 0/10285 on; UA 2016/5688 off; T-Drive 135268/285659 off; others \(\phi=0\) | adequate as protocol | Switch is disclosed as non-optimal and retrospective on SS/UA | Do not call SCD independently confirmed |
| Main ranking: structural alignment and descriptive +0.5% worst-group tolerance, not an RMSE win over FedAU/ObsUse | Table II caption; Conclusion | SS \(\Delta_{\mathrm{group}}\) 1.0139; UA RMSE tied; Holm n.s. | adequate on SS/UA protocol | Tolerance is descriptive, not inferential | Keep the disclaimer |
| T-Drive hybrid: FedAU/ObsUse remain strongest; SCD outside +0.5% | Abstract; tab:tdrive_hybrid; Conclusion | SCD 1.1069 / 1.3106; +2.39% / +2.43% | adequate and honest | Taxi ranking remains a negative result for the stack | Do not bury this |
| City Scanner visit occupancy: SCD lower than FedAU/ObsUse; FedAvg lowest on RMSE and WG | Abstract; eval; Table XXI | Paired −1.71%/−1.34% RMSE; FedAvg 0.2379 / 0.2489 | adequate vs those two | Does not show SCD is the best predictor; O/U controlled | Keep FedAvg sentence |
| Pilot~2 measured O: Hájek lowest on RMSE/WG; SCD lower than FedAU, ObsUse, and FedAvg | Abstract; eval; Table XXII | Hájek 0.7097 / 0.7273; SCD 0.7135 / 0.7311 | adequate | Meets vs FedAvg/FedAU/ObsUse; does not beat Hájek; U controlled | Keep Hájek-lowest sentence |
| Ideal sequential correction recovers compatible target moments, not Y-risk optimization | Abstract; Prop. 2 | Stated boundary; no new Y-risk theorem | adequate | Title still says target-risk | Optional title narrowing |
| Measuring U jointly with observation remains future work | Conclusion | Table XXII U = \(s_{\max}=5\); T-Drive O/U controlled | adequate | Honest | None |

## 9. Experiment / Benchmark / Reproducibility Audit

- Baselines: FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hájek, TwoStage-Hájek, FedAU-Window, ObsUse-Window. Official FedAU/TimeAlign reproductions are not claimed.
- Ablations: E4 one-factor; U-Air and T-Drive full-Design diagnostics. Use and Debt idle as isolated terms.
- Datasets: SensorScope/U-Air protocol \(R\) (main table). NSW protocol \(R\). T-Drive real \(R\), controlled \(O/U\). Table XXI real visit occupancy, controlled \(O/U\), cell clients. Table XXII Pilot~2 measured \(O\), controlled \(U\). Not end-to-end MCS.
- Metrics: RMSE\(_\mu\), WorstGroupRMSE, \(\Delta_{\mathrm{group}}\), \(\Delta_{c\text{-}s}\). Descriptive +0.5% paired mean-relative tolerance is not a coverage-guaranteed non-inferiority test (one allowed `non-inferiority` disclaimer remains in main.tex).
- Statistical rigor: paired seeds; main table 20 seeds; hybrid/protocol rankings 10 seeds. This pass did not recompute JO_E3 paired relatives; prior pass matched rounding.
- Isolation: hybrid numbers are not mixed into Table II. Frozen SCD SensorScope 7.9380 / U-Air 1.1131 unchanged by C1/C2 writing.
- Artifacts: `verify.py` this pass `checked=1883 mismatches=0`. `SCD_PHI.csv` in the named bundle still contains only SensorScope and U-Air. Tables XXI and XXII remain unbundled (Availability states this). E3 training-code commit versus the current workspace was not re-audited this pass (unverified).
- Limitations: match the tables, including uncorrected OFF, Hájek-lowest, taxi loss, and future \(U\).

## 10. Multi-Reviewer Panel

```text
Reviewer: Best-justified
Expertise: TMC MCS / FL systems, sympathetic
Likely score: 8/10
Confidence: 4
Main positive signal: honest hybrid ledger; measured-O ranking; OFF and I_tar now defined; Table II unmixed
Main negative signal: Hájek still wins Table XXII; U still controlled; taxi hybrid still favors FedAU/ObsUse
Evidence basis: abstract; Tables II, T-Drive, XXI, XXII; eq:agg_Ct; Alg. 1
Fatal concern if any: none
Score-change condition: a ranking that also beats TwoStage-Hájek under measured O, or a measured-U taxi ranking
```

```text
Reviewer: Critical
Expertise: TMC systems skeptic
Likely score: 5/10
Confidence: 4
Main positive signal: writing no longer overclaims OFF as reconstruction or leaves I_tar undefined
Main negative signal: large stack; idle Use/Debt; protocol-R main table; taxi loss; Hájek wins measured-O; cells not vehicles; U still a control; φ still a hard global switch
Evidence basis: E4; Table II; tab:tdrive_hybrid; Tables XXI–XXII; eq:scd_phi
Fatal concern if any: none independently fatal if claims stay scoped
Score-change condition: end-to-end MCS ranking with real R and measured O and U in which the stack is the best predictor, including versus Hájek
```

```text
Reviewer: Method / soundness
Expertise: IPW / selection / calibration
Likely score: 7/10 (criterion Soundness 4)
Confidence: 4
Main positive signal: Prop. 1–2 scoped; P2 unique minimizer; OFF labeled uncorrected; I_tar and C_t specified; φ lookup disclosed
Main negative signal: φ=0 remains a frozen protocol; OFF still weights all observed pairs; q_use marginal versus sequential history is not fully spelled out; per-block φ constructions are not one formula
Evidence basis: theory; eq:scd_phi; app:itar_lookup; Table XX
Fatal concern if any: none after the writing close
Score-change condition: a derived support rule or restricted-support OFF (new method, not writing)
```

```text
Reviewer: Evidence / experiment
Expertise: empirical FL / MCS
Likely score: 7/10 (criterion Evidence 5)
Confidence: 4
Main positive signal: claims match tables; C1/C2 did not mix numbers
Main negative signal: Hájek lowest; T-Drive +2.4%; NSW Δ_group reversal; Table II protocol R; Use/Debt idle
Evidence basis: Tables II, XIV, XXI, XXII; T-Drive; E4
Fatal concern if any: none
Score-change condition: beat Hájek on a measured layer, or measure U
```

```text
Reviewer: Novelty / positioning
Expertise: FL selection bias
Likely score: 7/10 (criterion Originality 4)
Confidence: 4
Main positive signal: unit-level R/O/U plus public μ over h(i) plus finite-window P2 is not FedIPW
Main negative signal: IPW/Hájek is classical; Hájek wins the measured-O prediction endpoints
Evidence basis: §Related Work; Table XXII Hájek row
Fatal concern if any: none
Score-change condition: empirical uniqueness versus Hájek would need a new table
```

```text
Reviewer: Writing / clarity
Expertise: TMC readability
Likely score: 8/10 (writing score 4.0/5)
Confidence: 4
Main positive signal: abstract/conclusion carry T-Drive loss, XXI FedAvg, XXII Hájek, uncorrected OFF; I_tar defined in main with constructions in appendix
Main negative signal: hybrid-ledger density; 14 pages with \enlargethispage; title still “target-risk”; φ symbol reused as a test function in Prop. 2
Evidence basis: abstract; intro; subsec:target_measures; app:itar_lookup; limitations
Fatal concern if any: none
Score-change condition: compress toward 12 pages; optional title narrowing
```

```text
Reviewer: Ethics / reproducibility
Expertise: artifacts / licensing
Likely score: 7/10 (Reproducibility 4)
Confidence: 4
Main positive signal: verify.py 1883/0 this pass; Zenodo/CC BY; privacy non-claim; Availability names XXI/XXII as unbundled
Main negative signal: author placeholders; Tables XXI/XXII and extra φ rows not in named SCD_PHI.csv; E3 commit vs workspace unverified this pass
Evidence basis: Availability; verify.py; SCD_PHI.csv
Fatal concern if any: ScholarOne author block (policy, not science)
Score-change condition: complete author list; ship Table XX/XXI/XXII sources
```

```text
Reviewer: Domain application (MCS)
Expertise: mobile crowdsensing deployment
Likely score: 6/10 (criterion Significance 4)
Confidence: 4
Main positive signal: taxi R, visit occupancy, measured observation from dual-sensor GPS streams
Main negative signal: U never measured; stations are not mobile clients; City Scanner clients are cells not vehicles
Evidence basis: Table I; T-Drive caption; Tables XXI–XXII
Fatal concern if any: none
Score-change condition: vehicle-level clients, or a measured usable-update/network layer
```

```text
Reviewer: Evidence/ablation
Expertise: component isolation
Likely score: 6/10
Confidence: 4
Main positive signal: E4 one-factor removals; full-Design diagnostics on U-Air/T-Drive
Main negative signal: Use and Debt idle; Design is a dataset-level switch, so ON/OFF is not a within-dataset factorial on the main table
Evidence basis: E4; Alg. 1
Fatal concern if any: none
Score-change condition: a within-dataset Design factorial that does not violate the frozen φ rule, or shrink idle modules
```

```text
Reviewer: Reproducibility (artifact)
Expertise: release engineering
Likely score: 7/10
Confidence: 4
Main positive signal: named bundle and passing verifier
Main negative signal: City Scanner rankings not in the bundle; φ freeze CSV is SS/UA only
Evidence basis: Availability; SCD_PHI.csv
Fatal concern if any: none if the non-claim is kept
Score-change condition: ship the missing CSVs
```

```text
Reviewer: Novice advocate
Expertise: first-pass TMC readability
Likely score: 6/10 (accessibility 3)
Confidence: 4
Main positive signal: abstract states the hybrid losses in plain sentences
Main negative signal: abstract is a result ledger; I_tar lives in one line then points to the supplement; notation load is high before Table II
Evidence basis: abstract; subsec:target_measures; eq:agg_Ct
Fatal concern if any: none
Score-change condition: shorten the abstract to problem, method, one aggregate finding, and scope
```

```text
Agreement:
  Object split versus FedIPW/FLOSS is real.
  T-Drive is a negative hybrid ranking and is disclosed.
  Table II is protocol R on station traces.
  Table XXII exists, is not mixed into Table II, and does not claim an RMSE win over Hájek.
  GPT-C1/C2 writing issues are closed as claim-scope and definition, not as new experiments.
Disagreement:
  Whether beating FedAvg/FedAU/ObsUse on cell-level measured observation is enough TMC evidence, given Hájek still wins that table and taxis still favor FedAU/ObsUse.
  Whether an uncorrected global OFF is acceptable once labeled, or still a method defect.
Decisive positive axis:
  Honest scoped claims plus a frozen measured-O ranking, with definitional objects now stated.
Decisive negative axis:
  No ranking in which the proposed stack is the best predictor under jointly measured MCS layers.
Unresolved evidence:
  Measured U; vehicle-level clients; extra φ rows and Table XXI/XXII CSVs in the named bundle; E3 commit identity versus workspace.
AC stance:
  Lean accept / weak accept (7/10). Not a desk reject. Not a clear TMC MCS-system accept.
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | major | T-Drive hybrid ranking misses the paper’s +0.5% rule versus FedAU and ObsUse | tab:tdrive_hybrid +2.39% / +2.43% | Significance | experiment | Keep as the main negative taxi finding, or later measure U (or O) on T-Drive | ccf-experiment-designer | A taxi ranking that also beats FedAU/ObsUse would move Significance toward 5 and Overall toward 8 |
| C2 | major | Table II is always-on protocol opportunity on station traces | Table II; setup | Significance | writing | Keep it as a development table; do not let it be the MCS-system headline | ccf-paper-writer | Unlikely to move Overall alone |
| C3 | moderate | Design-on NSW four-region loses \(\Delta_{\mathrm{group}}\) to FedAU (0.0606 vs 0.1048) | Table XIV; main eval | Soundness of the structural headline | writing | Already reported in main; do not restore a structural-win slogan | ccf-paper-writer | A Design-on table where SCD also wins \(\Delta_{\mathrm{group}}\) would restore the headline |
| C4 | moderate | Use and Debt have no isolated E4 effect | E4; Limitations | Soundness of the stack | method/soundness | Keep as factorization/accounting or later shrink Alg. 1 | ccf-paper-writer | Removing idle modules from the algorithm story would reduce stack-size risk |
| C5 | resolved | City Scanner was previously a \(\phi\) freeze without ranking | Table XXI | Evidence | experiment | Ranking remains | — | Prior condition remains met |
| C6 | resolved | Abstract omitted the T-Drive loss | Abstract | Clarity | writing | Abstract still states FedAU/ObsUse remain strongest on T-Drive | — | Honesty condition met |
| C7 | moderate | Table XXI FedAvg remains lowest; that block’s O/U are controlled; clients are cells | Table XXI | Evidence; Significance | experiment | Do not claim SCD is the strongest CS visit-occupancy method (current text does not) | ccf-experiment-designer | Already partially closed on Table XXII versus FedAvg |
| C8 | moderate | Named bundle `SCD_PHI.csv` has only SS/UA; Tables XXI and XXII CSVs are not bundled | Availability; SCD_PHI.csv | Reproducibility | reproducibility | Ship extra φ rows and CS ranking sources, or keep the current non-claim | ccf-submission-checker | Reproducibility 4→5 if shipped |
| C9 | moderate | Author placeholders with a named co-author | author block | Policy | venue-mismatch | Replace `****` after explicit authorization | user / ccf-paper-writer | ScholarOne blocker only |
| C10 | moderate | 14 pages vs 12-page published length / MOPC | main.pdf 14 pp; CS author-resources | Format | compression | Compress toward 12 if MOPC is unacceptable | ccf-paper-writer | Not a scientific score change |
| C11 | moderate | Table XXII: Hájek lowest on RMSE/WG; SCD is not the strongest measured-O method | Table XXII | Significance | experiment | Keep Hájek-lowest wording (current text does) | ccf-experiment-designer | Beating Hájek on a measured layer would move Overall toward 8 |
| C12 | resolved | Abstract SCD clause vs FedAU/ObsUse/FedAvg did not name RMSE/WG | abstract now names RMSE and worst-group error | Clarity | writing | Closed in current abstract | — | Clarity-only; closed |
| C13 | resolved | GPT-C1: OFF presented as target-mass reconstruction | abstract; Alg. 1 ELSE; limitations | Soundness of claims | writing | Closed as uncorrected \(\widehat\zeta=1\) | — | Method change (restricted support) would be a new experiment |
| C14 | resolved | GPT-C2: \(I_{\mathrm{tar}}\) and \(\pi_i^{\mathrm{tar}}\) undefined / \(\mu_{h(i)}\) as global φ law | eq:agg_Ct; eq:scd_phi; app:itar_lookup; Table XX | Soundness of objects; Clarity | writing | Closed as writing unification; φ counts not recomputed | — | Unifying φ by recomputation would move U-Air/T-Drive |
| C15 | moderate | Title “target-risk” vs Prop. 2 mass recovery | title; abstract; Prop. 2 | Clarity; Originality of the claim | writing | Optional title/abstract narrowing | ccf-paper-writer | Clarity-only unless the title is read as Y-risk optimization |
| C16 | moderate | Arrival-law \(q^{\mathrm{use}}\) sequential versus evaluation marginal | eq:quse_def; eq:arrival_intensity | Soundness | method/soundness | State the marginalization assumption | ccf-paper-writer | Soundness stays 4 unless the estimand is shown inconsistent |
| C17 | minor | \(\phi\) is both the SCD statistic and a generic test function in Prop. 2 | eq:scd_phi; Prop. 2 | Clarity | writing | Rename one symbol | ccf-paper-writer | Clarity-only |

## 12. AC / Meta-Review

Reviewer consensus: the paper is a coherent TMC-topic manuscript with an honest hybrid ledger. GPT-C1 and GPT-C2 no longer block soundness as undefined objects or overclaimed OFF reconstruction. Table II remains a protocol-\(R\) development table. T-Drive remains a disclosed taxi loss. Table XXII remains a measured-\(O\) ranking in which Hájek wins RMSE/WG.

Reviewer disagreement: a sympathetic reviewer treats the writing closes plus beating FedAvg/FedAU/ObsUse on measured observation as enough for a weak TMC accept. A critical reviewer treats Hájek’s Table XXII win, the taxi loss, cell clients, still-controlled \(U\), and a global \(\phi\) switch as evidence that the architecture is still larger than the mobile result.

Decisive acceptance axis: scoped claims, defined objects, Table XXII not mixed into Table II, and no RMSE-over-Hájek overclaim.

Decisive rejection axis: reading Table II plus Table XXII as a completed MCS-system win over Hájek, dropping the T-Drive loss, claiming jointly measured \(O\) and \(U\), or restoring OFF as target-mass reconstruction.

AC stance: **lean accept / weak accept (Overall 7/10).** C1/C2 writing closes improve definitional soundness of presentation; they do not move the TMC systems bar. The remaining reject axis is “the stack is not the best mobile predictor, and \(U\) is still a control.”

Discussion risks: reviewers treating +0.5% as a failed non-inferiority test; reviewers asking why Hájek wins Table XXII if Design is the useful factor; reviewers asking why Use/Debt remain in Algorithm 1; reviewers asking why Table XXI and Table XXII disagree on FedAvg; reviewers asking why \(\phi\) constructions differ by block after C2.

## 13. Quantitative Scores

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 4 | 4 | §Related Work object split vs FLOSS/FedIPW; Table XXII does not collapse it | No deduction. Originality 5 would need empirical uniqueness versus Hájek, not just versus FedAU |
| Soundness | 4 | 4 | Prop. 1–2; P2; uncorrected OFF; \(I_{\mathrm{tar}}\) and \(C_t\) defined; app:itar_lookup | Deduction: \(\phi=0\) is still a frozen protocol (not derived). Repair to 5: derived support rule or restricted-support OFF |
| Evidence | 5 | 4 | Tables match stated claims; C1/C2 did not mix Table II; verify.py 1883/0 | Remaining Hájek-win and controlled U are claim-scope, not missing evidence for stated claims |
| Significance | 4 | 4 | Table XXII measured O; T-Drive still a loss; Hájek wins Table XXII | Repair to 5: taxi win or Hájek-beating measured layer |
| Clarity | 4 | 4 | Abstract/conclusion carry T-Drive, XXI FedAvg, XXII Hájek, uncorrected OFF; \(I_{\mathrm{tar}}\) defined | Deduction: dense abstract; 14 pages; title “target-risk”. Repair: compress; optional title narrowing |
| Reproducibility | 4 | 4 | Named bundle verifier passes; XXI/XXII disclosed as unbundled | 5 if those CSVs and extra \(\phi\) rows ship |
| Ethics / Limitations | 4 | 4 | Hybrid scope, cell clients, privacy non-claim, future U, uncorrected OFF | Adequate disclosure |

**Overall:** 7/10  | **Scholarly Confidence:** 4/5

**Recommendation:** weak-accept
**Verdict:** Overall stays 7 rather than 8 because Hájek still wins Table XXII, T-Drive still loses, and \(U\) is still a control. C1/C2 writing closes do not raise Overall. Overall would fall to 6 if Table XXII were written as an RMSE win over Hájek or mixed into Table II, or if OFF were restored as target-mass reconstruction.

```text
Quality: 4
Clarity: 4
Significance: 4
Originality: 4
Soundness: 4
Evidence: 5
Reproducibility: 4
Ethics / Limitations: 4
Overall: 7/10
Confidence: 4/5
Score-change conditions:
  Significance 4 -> 5 if a taxi or measured-U ranking also beats FedAU/ObsUse, or if SCD beats Hájek on a measured layer
  Overall 7 -> 8 under the same condition, with Table II still unmixed
  Overall 7 -> 6 if Table XXII is written as an RMSE win over Hájek, mixed into Table II, claimed as jointly measured O and U, or OFF restored as reconstruction
  Overall 7 -> 4 if the T-Drive loss is dropped
```

Writing/presentation scorecard (full mode):

| Dimension | Weight | Score (1-5) | Confidence | Evidence basis | Concrete repair |
| --- | ---: | ---: | ---: | --- | --- |
| Storyline and motivation | 10 | 4 | 4 | Intro gap before method | Optional compress of related-work list |
| Contribution display | 10 | 4 | 4 | Three bullets; OFF and SCD ceilings visible | None required |
| Paragraph logic | 10 | 4 | 4 | Hybrid ledger still dense | Reduce “not mixed into” repetition if compressing |
| Claim-evidence alignment | 12 | 5 | 5 | Abstract matches T-Drive, XXI, XXII, uncorrected OFF | Keep those sentences |
| Method readability | 9 | 4 | 4 | \(I_{\mathrm{tar}}\) in main; lookup in app:itar_lookup | Optional one-line pointer to app:itar_lookup by label |
| Experiment narration | 9 | 4 | 4 | Tables introduced before interpretation | None |
| Related-work positioning | 8 | 4 | 4 | FedIPW/FLOSS/FedPALS object split | Optional FedPALS venue-status clause |
| Terminology and notation consistency | 8 | 4 | 4 | SCD, φ lookup, uncorrected OFF; φ also a Prop. 2 test function | Rename one \(\phi\) |
| Prose discipline and voice | 10 | 4 | 4 | No C1/kill-bar language; 0 em dashes in main | None |
| LaTeX and format discipline | 6 | 3 | 4 | IEEEtran; 14 pp; `\enlargethispage{10\baselineskip}`; xr counters | Compress toward 12 |
| Reviewer-facing risk | 8 | 4 | 4 | Hájek-lowest, taxi loss, uncorrected OFF are visible | Do not overclaim Table XXII versus Hájek |
| **Writing score** | 100 | **4.0** | 4 | Weighted mean (LaTeX 3 pulls from 4.1) | Risk band: **moderate** |

## 14. Questions For Authors

1. On Table XXII, TwoStage-Hájek is lowest on RMSE\(_\mu\) and WorstGroupRMSE. What scientific work does Design-on SCD do there besides beating FedAvg/FedAU/ObsUse and \(\Delta_{\mathrm{group}}\)?
2. Table XXI (controlled \(O\)) has FedAvg lowest; Table XXII (measured \(O\)) has FedAvg beaten. Which table is the MCS-system ranking a TMC reader should believe?
3. T-Drive is still the only taxi-opportunity ranking and SCD loses. Is the mobile claim Table XXII, the negative taxi result, or both?
4. \(U\) remains a Complete-aligned control on Table XXII. Is measured observation enough, or is a network/usable-update ranking still required for the TMC systems bar?
5. Usable-update correction and target debt are retained with no isolated E4 effect. Which algorithm modules are load-bearing for TMC?
6. After C2, \(\phi\) constructions still differ by block. Should a TMC reader treat Table XX as one protocol with documented lookups, or as four different zero tests?

## 15. Score Revision Criteria

```text
Raising the score would require:
  A frozen ranking in which SCD also beats TwoStage-Hájek on RMSE_μ or WorstGroupRMSE under a measured layer, or a T-Drive (or other taxi) ranking that meets the paper’s +0.5% rule versus FedAU/ObsUse, without mixing Table II.
Lowering the score would be triggered by:
  Presenting Table II as an RMSE win; mixing Table XXII into Table II; dropping the T-Drive loss; claiming SCD is theoretically optimal; claiming SCD is the strongest Table XXII method; calling Table XXII jointly measured O and U; or restoring OFF as target-mass reconstruction.
Concerns unlikely to change before submission:
  Author placeholders (needs authorization); 14-page MOPC risk unless compressed; Use/Debt idle in E4; U not measured; cell-not-vehicle clients; φ constructions remaining per-block.
```

```text
Relative progress:
  Frozen contract raven-mcs-tmc-r1-2026-09-11-pass1
  Quality 4/4/0; Clarity 4/4/0; Significance 4/4/0; Originality 4/4/0;
  Soundness 4/4/0; Evidence 5/5/0; Reproducibility 4/4/0; Ethics 4/4/0
  Equal-weight criterion delta 0 on the 1–5 mean
  Classification: improved on issue ledger (C12, C13/GPT-C1, C14/GPT-C2 resolved as writing);
  unchanged on dimension scores and Overall
Absolute readiness:
  Current Overall 7/10, lean accept / weak accept
  Threshold for clear accept: 8, requiring a ranking in which the stack is the best predictor on a measured mobile layer
  Remaining blocking evidence for 8: Hájek-win on Table XXII; T-Drive loss; U still controlled
Confidence and comparability:
  Same venue, same tables, same numbers; writing-only revision
  Scholarly confidence 4/5 (full TeX + supplement + passing verifier; XXI/XXII CSVs and E3 commit not re-audited)
New issue provenance:
  C13/C14 resolved (writing); C15/C16 previously undetected GPT leftovers, apply to both versions as claim-scope/method gaps not introduced by this revision
Traceable score decreases:
  none
```

## 16. Action Plan And CCFA Handoffs

```text
Priority: P0
Action: Replace author placeholders before ScholarOne upload
Owner skill: user / ccf-paper-writer
Input needed: authorized author list
Expected output: complete named-author block
Handoff required: yes
```

```text
Priority: P0
Action: Confirm TMC submission page cap; compress toward 12 pages if MOPC is unacceptable
Owner skill: ccf-paper-writer
Input needed: ScholarOne length rule
Expected output: 12-page main or an accepted MOPC plan
Handoff required: yes
```

```text
Priority: P1
Action: Keep T-Drive loss, Hájek-lowest, uncorrected OFF, and Table II isolation; do not reopen GPT-C1/C2 as new rankings
Owner skill: ccf-paper-writer
Input needed: none
Expected output: claim ceiling preserved
Handoff required: no
```

```text
Priority: P1
Action: Optional: ship Table XXI/XXII CSVs and extra φ rows, or keep the Availability non-claim
Owner skill: ccf-submission-checker
Input needed: frozen CSVs
Expected output: Reproducibility 4→5 if shipped
Handoff required: yes
```

```text
Priority: P2
Action: Optional title/abstract narrowing from target-risk to target-mass calibration; optional q_use marginalization sentence
Owner skill: ccf-paper-writer
Input needed: none
Expected output: C15/C16 reduced; Overall stays 7
Handoff required: yes if the user asks
```

```text
Priority: P2
Action: New experiment only if seeking Overall 8: measured U, or a ranking that beats Hájek, or a taxi ranking inside +0.5%
Owner skill: ccf-experiment-designer
Input needed: authorization to train
Expected output: new frozen table, not mixed into Table II
Handoff required: yes
```

```text
Checks run:
  ccf-paper-reviewer full workflow (desk, contribution, evidence, adversarial)
  Public-safe related-work search (FLOSS, FedIPW, CS author-resources)
  verify.py on RAVEN_MCS_PUBLIC_REPRO_R1 (1883/0)
  Claim-evidence audit of abstract/intro/conclusion against frozen tables
  Writing rubric (full mode)
Checks skipped:
  Full GPU retraining
  Recomputation of JO_E3 paired relatives
  E3 source-commit vs workspace diff
  Official TMC ScholarOne first-party 18-page sentence (third-party only)
Unresolved risks:
  Author placeholders; 14-page MOPC; unbundled XXI/XXII; unmeasured U; Hájek-win; taxi loss
```

Next CCFA skills available:
- ccf-paper-writer: optional compression toward 12 pages, title narrowing, q_use sentence
- ccf-experiment-designer: only if seeking Overall 8 (measured U / beat Hájek / taxi win)
- ccf-submission-checker: ScholarOne author block, page cap, artifact bundle
- ccf-integrity-auditor: E3 commit vs workspace; XXI/XXII CSV identity
- ccf-rebuttal-writer: if a revision ledger is needed
