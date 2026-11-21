# CCFA Paper Re-Review — RAVEN-MCS / IEEE TMC

> Independent current-version review after a second wording (+ artifact) pass. Assesses reviewer-visible sources and the manuscript-named public artifact only. Does not use prior review scores as evidence anchors.

## 1. Scope

```text
Review date: 2026-09-12 (second wording pass)
Materials:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex, appendix.tex, supplemental.tex
  Current main.log / main.pdf (14 pages)
  RAVEN_MCS_PUBLIC_REPRO_R1
Verified:
  verify.py → checked=1886, mismatches=0
  rebuild_table_ii.py → Table II 4-decimal freeze matched
  rebuild_table_ii_tolerance.py → TEST/ALL20 + T-Drive percentages matched
  rebuild_e3_scd_holm_fedau_obsuse.py → Holm family + slice relatives present
```

## 2. Summary

RAVEN-MCS still separates opportunity, observation, and usable-update selection from a public deployment target, forms a sequential Hájek-style reference when Design is on, and calibrates aggregation inside the current feasible set.

This pass is a **substantive honesty and packaging upgrade**, not only cosmetic polish. The manuscript now names **RAVEN-Design** versus **RAVEN-NoDesign** throughout; treats \(\phi\) as a frozen heuristic rather than a positivity certificate; discloses that NSW/City Scanner use locally constructed target maps; shortens the abstract to about **191** words; and ships ALL20/TEST10 slice relatives plus a public Holm family versus FedAU-Window/ObsUse-Window. Artifact integrity remains clean (`1886/0`).

The remaining barriers are mostly unchanged in substance: RAVEN-NoDesign is still a different estimand on hard support; no ranking jointly measures \(R/O/U\); City Scanner tables remain outside the public bundle (now disclosed); the author block is still placeholders; and the main PDF is still 14 pages.

**Recommendation: Major revision — 6/10.**  
**Review confidence: 4/5.**

## 3. What improved in this pass

1. **RAVEN-Design / RAVEN-NoDesign naming.** Abstract through Algorithm, Table II, and Limitations consistently mark \(\widehat\zeta=1\) as not target-mass reconstruction (`main.tex:79–83`, `662–666`, `1006–1023`, `1697–1699`).
2. **\(\phi\) as heuristic + cross-block disclosure.** The text states \(\phi\) does not test positivity on target-positive pairs and is not necessary/sufficient for A1/A5 (`main.tex:996–998`). Intro/Eval note that NSW and City Scanner use local target maps, not a transferred SensorScope/U-Air lookup (`main.tex:248–250`, `1610–1612`, `1626–1627`).
3. **Title / §III / acronym alignment.** Title remains Target-Mass-Calibrated; §III is *System Model and Target-Mass Formulation* (`main.tex:324`); expansion is now *Reference Alignment Via Exposure-aware Normalization…* (`main.tex:147–149`), not “Risk Alignment.”
4. **Abstract compressed.** About **191** words (was ~296). Still dense, but within a typical IEEE length band.
5. **ALL20 vs TEST10 disclosed and packaged.** Prose reports both slices (`main.tex:1659–1675`); CSVs `E3_SCD_WORSTGROUP_SLICE_REL.csv` match (U-Air TEST ~+0.48%/+0.44%; ALL20 ~+0.002%/+0.075%).
6. **Holm vs FedAU/ObsUse released.** `E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv` + rebuild script; all four ALL20 comparisons non-significant, matching the paper’s “no Holm-significant RMSE win.”
7. **Availability ceiling expanded.** Bundle contents now list Holm/ALL20–TEST10/T-Drive/NSW; City Scanner tables explicitly “not among those bundled files” (`main.tex:1951–1962`).

## 4. Major concerns

### C1 — RAVEN-NoDesign remains a different method on hard support

Naming and disclaimers are now adequate. The scientific point is unchanged: when \(\phi>0\), Algorithm 1 sets \(\widehat\zeta^o=1\) (`main.tex:662–666`, `1021–1023`). U-Air and T-Drive evaluate that fallback. Forced Design is retained only as a diagnostic row. Reviewers can accept this if the contribution is framed as “Design when support-compatible; honest NoDesign otherwise,” but it still weakens any claim that the *same* target-mass estimator drives the difficult-support rankings.

Required: keep Design/NoDesign tables and claim ceilings strictly separated (already mostly done); avoid reading NoDesign rows as target-mass confirmation.

### C2 — \(\phi\) is still a pre-registered heuristic, not a positivity certificate

Disclosure is much better, but the switch still uses attached-client zero-target mass and different frozen constructions per block. Cross-block “\(\phi=0\) confirms Design” should not be read as comparable positivity evidence.

Required: keep the heuristic label everywhere (done); optional next step is one frozen support test over target-positive pairs.

### C3 — Empirical story is clearer, still protocol/hybrid and prediction-mixed

Table II + ALL20/TEST10 + Holm packaging now support the SensorScope/U-Air narrative cleanly. T-Drive still loses the descriptive +0.5% rule to FedAU/ObsUse. City Scanner/Pilot 2 remain hybrid and still sit outside the public bundle. No jointly measured \(R/O/U\).

Required: either demote City Scanner from abstract/conclusion emphasis until bundled, or ship matching SUMMARY/PAIRED/PHI files; keep the protocol/hybrid claim ceiling.

### C4 — Reproducibility improved at table level; train-level and City Scanner gaps remain

`verify.py` is clean; Table II, tolerance, Holm, T-Drive, and NSW `new_target/` are auditable. The bundle is still not a pinned retraining archive. City Scanner remains unbundled (0 MANIFEST hits). Residual trap: `E4_ABLATION_HOLM_RESULTS.csv` can disagree with paper asterisks that track `TABLE_E4_COMPONENT_EFFECTS.csv`.

Required: bundle City Scanner or remove those tables from the main claim chain; align or deprecate the short E4 Holm CSV; keep train-level scope explicit.

### C5 — Submission / presentation blockers

Author block still mixes `****` / `***` with a real coauthor name and grant (`main.tex:57–59`). Main PDF is **14 pages** with `\enlargethispage` and one Overfull ~5.6pt (`main.log`). City Scanner/NSW table bodies remain in the supplemental PDF while main text cites numbers. Abstract still packs math tokens (`$+0.5\%$`, `$R,O,U$`).

Required: fix author mode; resolve overlength/MOPC policy; either bring one hybrid table into the main PDF or demote off-main numeric claims; strip math from the abstract if following IEEE CS guidance.

## 5. Moderate / compliance concerns

- Trajectory/GPS governance still thin beyond source terms and “FL is not a privacy guarantee.”
- FedAU/ObsUse/TimeAlign remain windowed adaptations, not official reproductions.
- Holm rebuild needs scipy; `PROTOCOL.json` table_verify still lists only numpy/pandas.
- README should state City Scanner exclusion (paper already does).
- Gate remains diagnostic; keep it out of the contribution spine.

## 6. Scorecard

| Dimension | Score (1–5) | Confidence | Basis |
| --- | ---: | ---: | --- |
| Novelty | 3 | 4 | MCS R/O/U separation plus feasible calibration remains coherent; ingredients established. |
| Soundness | 4 | 4 | Design/NoDesign and \(\phi\)-heuristic ceilings now match the proved/implemented scope. |
| Evidence | 4 | 4 | Table II / Holm / ALL20–TEST10 / T-Drive / NSW auditable; City Scanner still off-bundle. |
| Significance | 3 | 4 | Framing matters; no jointly measured R/O/U win; real-\(R\) rankings mixed. |
| Clarity | 4 | 4 | Naming and ceilings much clearer; abstract still dense; some tables live only in supplement. |
| Reproducibility | 3 | 5 | Strong table-level verify; Holm/slices added; no pinned retrain; City Scanner absent. |
| Ethics / limitations | 3 | 4 | Claim honesty strong; author placeholders and hybrid-table packaging remain. |

**Recommendation: Major revision — 6/10.**  
**Review confidence: 4/5.**

## 7. Revision priorities

```text
P0
  1. Resolve author anonymity / camera-ready mode (replace ****).
  2. Bundle City Scanner evidence or remove those rankings from abstract/conclusion emphasis.
  3. Keep Availability honest about table-only scope (already mostly done).

P1
  4. Align or remove the conflicting short E4 Holm CSV.
  5. Compress abstract further; remove inline math tokens.
  6. Resolve 14-page overlength / MOPC expectation; reduce Off-main numeric dumps.

P2
  7. Add jointly measured R/O/U mobile evidence, or keep an explicit protocol/hybrid-only ceiling.
  8. Publish a commit-pinned executable training archive if claiming end-to-end repro.
```

## 8. Verdict

Relative to the previous wording-pass review, this manuscript closed several previously Major packaging/honesty gaps (Design/NoDesign naming, \(\phi\) heuristic disclosure, ALL20/TEST10, public Holm-vs-FedAU family, Target-Mass section/acronym). It is still not acceptance-ready: author block, City Scanner off-bundle evidence, hybrid/mobile limits, and train-level reproducibility remain. Treat the score move **5 → 6** as credit for claim/artifact alignment, not for a new empirical win.
