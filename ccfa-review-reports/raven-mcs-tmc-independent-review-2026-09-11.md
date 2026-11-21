# CCFA Paper Review — RAVEN-MCS / IEEE TMC

> Independent current-version review. This report was produced without using prior review reports, prior scores, laboratory handoffs, or unpublished result files. It assesses the reviewer-visible current sources and the artifact named in the manuscript.

## 1. Review Metadata

```text
Review date: 2026-09-11
Target venue: IEEE Transactions on Mobile Computing (TMC), CCF-A
Materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex
  TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex and appendix.tex
  TO_OVERLEAF_paper_tmc_r1_clean/reference.bib
  RAVEN_MCS_PUBLIC_REPRO_R1
Evidence boundary:
  reviewer-visible TeX and manuscript-named artifact only
Not assessed:
  full GPU retraining, unbundled City Scanner results, unpublished records,
  source-code implementation beyond the released tabulation/check scripts
```

## 2. Summary

RAVEN-MCS frames windowed asynchronous federated data completion as alignment between a public deployment target and the distribution induced by opportunity (`R`), observation (`O`), and usable-update (`U`) selection. It reconstructs compatible target mass using sequential Hájek-style factors and then solves a convex, finite-window calibration problem with a target-debt term. Its operational Design factor is enabled only when the training-unit fraction with zero target mass, \(\phi\), is zero.

The paper is unusually explicit about scope: target-mass recovery is not claimed to prove target-risk optimization; the \(\phi=0\) switch is labeled a safeguard rather than a theorem; the +0.5% result is labeled a descriptive point-estimate tolerance rather than formal non-inferiority; and the T-Drive/City Scanner experiments are labeled hybrid rather than end-to-end MCS. These claim ceilings are a strength. The remaining concern is that the hard global switch does not implement the stated target-mass correction when \(\phi>0\), the coverage/Design target-mass notation is not consistently defined, and the released artifact currently fails its own integrity verifier.

## 3. Main Strengths

1. **Well-separated statistical objects.** The paper distinguishes public target mass, opportunity strata, observation, usable update, corrected reference mass, and feasible aggregation. The R/O/U ordering and pre-outcome information boundaries are unusually clear (`main.tex:360–440`, `610–805`).
2. **Appropriate claim ceilings.** The manuscript explicitly limits Proposition 2 to compatible target moments/group mass, not \(Y\)-risk optimization or asynchronous convergence (`main.tex:200–210`, `1030–1037`, `1152–1167`).
3. **Candid experimental reporting.** It reports negative or mixed findings: T-Drive loses to FedAU/ObsUse; FedAvg or TwoStage-Hájek wins several prediction endpoints; Use has no isolated effect; and Debt's effect is practically tiny (`main.tex:1540–1579`, `1590–1617`, `1805–1846`).
4. **Improved statistical wording.** The manuscript calls the +0.5% criterion a descriptive point-estimate tolerance with no coverage guarantee (`main.tex:1458–1471`), avoiding a formal non-inferiority claim unsupported by the stated test.
5. **Useful artifact additions.** Canonical Table II data, per-seed worst-group values, table and tolerance reconstruction scripts, and SCD labels make the main-table audit materially easier.

## 4. Major Concerns

### C1 — The global \(\phi=0\) switch is neither a positivity criterion nor a target-mass-preserving fallback

`main.tex:973–987` enables Design for an entire dataset iff **no** training unit has zero target mass. The authors correctly say it is not derived from A1/A5 (`main.tex:983–987`, `1431–1440`, `1850–1854`). More importantly, the OFF branch assigns \(\widehat\zeta^o_{k,t,i}=1\) to *all* observed pairs (`main.tex:1000–1007`), even though the ideal ratio has a zero numerator on target-zero pairs (`main.tex:625–633`). Thus the fallback can train and aggregate target-zero observations with positive weight rather than restrict them or assign them zero weight.

The number of target-zero training units is neither a calibrated overlap measure nor an argument that every target-positive pair is safe for Design. A small amount of target-zero support flips the whole method, while a serious positivity defect confined to target-positive events is not directly measured by \(\phi\). The NSW and City Scanner applications help demonstrate transfer of the frozen rule, but do not fix this estimand change. Replace the rule with a target-positive overlap diagnostic and a defined restricted-support/partial-identification policy; otherwise present the OFF branch as an uncorrected baseline rather than target-mass reconstruction.

### C2 — The coverage and SCD objects use an undefined, inconsistent atomic target mass

The deployment risk is defined using normalized atomic mass \(\varpi_i^{\mathrm{tar}}\) (`main.tex:445–470`, `494–505`). The coverage object and \(\phi\) instead use \(\pi_i^{\mathrm{tar}}\), while \(I_{\mathrm{tar}}\) and \(\pi_{i,t}^{\mathrm{opp}}\) are not formally defined in the main text (`main.tex:475–491`, `973–981`). In the appendix, \(\pi_i^{\mathrm{tar}}=\mu_{h(i)}\) is stated “on unique train units” (`appendix.tex:2089–2093`). That is group mass repeated over atomic units and is not a normalized atomic probability law unless further divided by within-group unit mass.

Consequently, neither the zero-mass count nor \(C_t\) is uniquely reproducible from the stated target distribution. Define one normalized atomic target measure, define the target-positive set and atomic opportunity mass from it, and derive the train-unit SCD quantity from exactly that object. Until then, the Gate theorem can only be read as conditional mathematics for an incompletely specified operational quantity.

### C3 — TMC systems evidence remains hybrid, and the practical endpoint story is mixed

The main E3 comparison is always-on protocol opportunity on station traces (`main.tex:1324–1412`). T-Drive measures real taxi opportunity but controls O/U; City Scanner visit occupancy is likewise hybrid; Pilot 2 measures O but controls U (`main.tex:1350–1370`, `1590–1617`). The paper labels this accurately, but it means no ranking jointly measures mobility opportunity, actual sensing, and delivered updates.

On T-Drive, SCD is outside the stated +0.5% tolerance against FedAU/ObsUse (`main.tex:1540–1579`). On City Scanner, it is lower than those adapted baselines but FedAvg (or TwoStage-Hájek on Pilot 2) is best on prediction. The strongest consistent result is reduced \(\Delta_{\mathrm{group}}\), not predictive improvement. The abstract and title should continue to foreground *mass/structural alignment* rather than imply a demonstrated end-to-end completion advantage.

### C4 — Artifact integrity and code-to-result provenance are not closed

Running the supplied verifier on 2026-09-11 checked 1,883 manifest rows and found three hash mismatches:

```text
scripts/rebuild_table_ii.py
scripts/rebuild_table_ii_tolerance.py
tdrive/TD_R_FREEZE.json
```

The two Table II scripts themselves pass: the canonical table matches the displayed four-decimal cells and the disclosed tolerance percentages. Nevertheless, an artifact advertised as frozen cannot pass with a nonzero manifest mismatch count.

The supplied `configs/e3_source_hashes.json` identifies E3 code commit `b01db69e8554a33446c438c060ac464dcfadac24`. The workspace implementation is currently at `2e47464c2c15d7dae4ceb059592782b9542de625`, and the four core implementation files listed by the E3 provenance record (`method_policy.py`, `methods.py`, `p2_cvxpy.py`, and `window_runner.py`) have local modifications. This does not prove the tabulated results are wrong—later development is plausible—but it does mean the current implementation cannot be verified as the generator of the frozen results. The artifact must contain or link to an immutable, public source archive at the exact logged commit, with an environment lock and executable training entry point.

Moreover, the manuscript explicitly says that the City Scanner tables are not among bundled files (`main.tex:1924–1934`), although they carry a substantial portion of the new empirical story. Update the manifest after finalizing all files, add a CI/pre-submission verifier that must pass, and release the City Scanner source tables, per-seed results, frozen target/trace specifications, and reconstruction commands.

### C5 — Target-risk semantics and implemented learning objective are separated but not connected

The paper now states this boundary correctly: the target risk uses \(Y_i\), whereas local steps minimize weighted squared error against client observations \(Z_{k,r,i}\) (`main.tex:494–545`, `725–753`, `1030–1037`). Proposition 2 only proves moment/group-mass recovery. This should not be presented as a defect in a claim the paper no longer makes, but it limits the contribution: without a measurement model relating \(Z\) to \(Y\), a gradient argument, and an analysis of local/asynchronous steps, “target-risk-calibrated” is best understood as *target-mass-calibrated aggregation*. The title/abstract should either reflect that narrower meaning or add the missing bridge.

### C6 — The arrival-law plug-in needs a more explicit sequential marginalization argument

The paper states a product \(P^{\mathrm{opp}}(k,i)p^{\mathrm{obs}}_{k,i}q^{\mathrm{use}}_k\) for a sequential contribution (`main.tex:510–528`), while \(q^{\mathrm{use}}\) is conditioned on a post-sensing legal history that may include registration state (`main.tex:420–440`). At the event level this factorization can be valid conditional on the realized history. At the evaluation level, however, the displayed \(\widehat q^{\mathrm{use}}_{k,s}\) is described as a marginal. The paper should define whether it is a history-conditional factor averaged jointly with observation/registration, or demonstrate the factorization under a stated conditional-independence/marginalization assumption. Otherwise the estimand for \(\mathcal R_\rho\) is ambiguous.

## 5. Submission, Presentation, and Minor Concerns

- **P0 submission compliance:** The author block combines placeholders with a real name, institution, email, and grant (`main.tex:57–60`; `supplemental.tex:59–62`). Choose complete single-anonymous metadata or complete double-anonymous removal before upload.
- **P0 format:** The current compile log records a 14-page main PDF (`main.log:664`). This exceeds the usual 12-page regular-article publication target; confirm the applicable submission/camera-ready limit and required overlength process before upload. The abstract (`main.tex:67–95`) is also dense and substantially longer than a typical Transactions abstract; compress it to the problem, method, one aggregate finding, and scope limit.
- The paper relies on manually coordinated main/supplemental counters (`supplemental.tex:67–78`), a fragile source of numbering drift. Compile the exact upload pair in clean CI.
- FedAU-Window, ObsUse-Window, and TimeAlign are adaptations, not official implementations (`main.tex:1416–1429`). Provide adaptation pseudocode/configs and, if feasible, an official or stronger target-aware comparator.
- The \(\phi\) symbol is reused as a generic test function in Proposition 2 and a Design-switch statistic. Rename one of them.
- The coverage Gate is responsibly demoted to a diagnostic, but it still occupies nontrivial theoretical space; moving it fully to the supplement would sharpen the main contribution.

## 6. Scores

| Dimension | Score (1–5) | Confidence | Rationale |
| --- | ---: | ---: | --- |
| Novelty | 2 | 4 | The R/O/U and feasible-calibration combination is coherent, but the constituents are established IPW/Hájek, convex calibration, and debt accounting. |
| Soundness | 2 | 5 | The conditional results are scoped clearly, but the SCD fallback changes the target and the coverage/atomic-mass definitions do not close. |
| Evidence | 3 | 4 | Multiple datasets and candid negatives improve credibility, but controlled O/U and mixed prediction results constrain the central utility claim. |
| Significance | 3 | 4 | The target-versus-arrival framing is relevant to MCS; end-to-end impact remains unshown. |
| Clarity | 2 | 4 | Definitions are rigorous but dense; symbols and target objects are inconsistent, and the abstract over-enumerates results. |
| Reproducibility | 1 | 5 | Main Table II checks pass, but the manifest fails, the exact E3 source archive is absent, and City Scanner evidence is unbundled. |
| Ethics / limitations | 2 | 4 | Hybrid limits and no-privacy-guarantee boundary are candid; GPS-data governance and complete source/redistribution conditions need closure. |

**Overall recommendation: Major revision — 4/10.**  
**Review confidence: 4/5.**

## 7. Required Revision Plan

```text
P0 — release correctness
  1. Regenerate MANIFEST.csv and require verify.py to pass at zero mismatches.
  2. Archive and publicly link the exact b01db69... E3 source revision, environment lock,
     raw-data acquisition/preprocessing path, and a deterministic training command.
  3. Add City Scanner/Pilot 2 raw-to-table provenance, per-seed data, frozen maps,
     traces, and a deterministic reconstruction command.
  4. Define one normalized atomic target quantity for risk, coverage, and SCD;
     publish its construction and the target-positive set.
  5. Resolve the author/anonymity mode and page-length procedure before submission.

P1 — claim and method closure
  5. Replace the φ=0 OFF fallback with a target-positive support policy that does
     not give positive correction weight to target-zero observations.
  6. State whether q_use in the arrival law is conditional or jointly marginalized;
     supply the required derivation/assumption.
  7. Keep “target-mass alignment” distinct from target-risk optimization throughout
     title, abstract, and conclusions unless the Z-to-Y/optimization bridge is added.

P2 — evidence and presentation
  7. Add a jointly observed R/O/U mobile study, or narrow the paper’s empirical
     claim to hybrid/protocol evaluation.
  8. Publish exact baseline adaptations and add a strong target-aware comparator.
  9. Move Gate material to the supplement and simplify notation/table density.
```

## 8. Decision Rationale

This is a reviewable submission whose restraint on non-inferiority, target-risk optimization, and hybrid evidence is a real strength. It is not ready for acceptance because the operative SCD fallback is not target-mass preserving, its target-mass symbols do not consistently define the coverage/SCD quantities, the end-to-end systems claim is not yet supported, and the released artifact fails its own hash verification. These are repairable, but not solely through copyediting.

