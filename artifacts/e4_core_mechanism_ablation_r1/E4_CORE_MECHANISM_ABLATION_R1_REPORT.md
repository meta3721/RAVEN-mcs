# E4 core mechanism ablation R1 report

## 1. Executive decision
`E4_CORE_MECHANISM_ABLATION_COMPLETE_AND_SEALED`

## 2. Paper-mainline purpose
Identify which RAVEN components are responsible for the E3 structural mismatch reduction (Delta_group / Delta_c_s) on SensorScope and U-Air Complete-aligned.

## 3. No-scope-expansion attestation
No Traffic, no new datasets/baselines/seeds/metrics, no retuning, no post-hoc ablations, no w/o-Ref/Variance/Staleness in this round.

## 4. E3 full-RAVEN reference reuse
40 E3 RAVEN formal runs reused after identity audit; not rerun.

## 5. Ablation semantic freeze
Five one-factor ablations: Design, Obs, Use, Inst, Debt. See `E4_ABLATION_SEMANTICS_FREEZE.json`.

## 6. Source/EventTrace identity
Formal source freeze: `E4_FORMAL_SOURCE_FREEZE.json`. Per dataset×seed EventTraces reused from E3 formal artifacts.

## 7. SensorScope execution
100 new ablation runs (5×20).

## 8. U-Air execution
100 new ablation runs (5×20).

## 9. Raw-result seal
`E4_RAW_RESULTS_SEAL.json` status=SEALED accepted=200/200.

## 10–13. Endpoint results
See `E4_ABLATION_SUMMARY.csv`, `E4_ABLATION_PAIRED_TESTS.csv`, `E4_ABLATION_HOLM_RESULTS.csv`, `E4_ABLATION_EFFECT_SIZES.csv`.

## 14–18. Component interpretations
See `E4_COMPONENT_CLAIM_MATRIX.md` and `E4_CORE_MECHANISM_EVIDENCE_SYNTHESIS.md`.

## 19. Component claim matrix
Statuses: {'Debt': 'STRUCTURAL_ONLY_SUPPORTED', 'Design': 'COUNTEREVIDENCE', 'Inst': 'CORE_MECHANISM_SUPPORTED', 'Obs': 'COUNTEREVIDENCE', 'Use': 'NO_CLEAR_EFFECT'}

## 20. Structural-to-prediction relationship
Structural endpoints are primary; prediction endpoints are secondary.

## 21. Main table
`E4_ABLATION_SUMMARY.csv`

## 22. Main figures
`figures/FIG_E4_1.*` (Delta_c_s), `figures/FIG_E4_2.*` (Delta_group)

## 23. Tests/Gates
See `E4_GATES.json` after gate script.

## 24. Limitations
One-factor ablations only; no Traffic; P2 warnings may occur but invocation state is persisted; no claim that every component is indispensable.

## 25. Whether any further experiment is truly needed
Decision: `PROCEED_TO_E5_THEORY_REACHABILITY_VALIDATION`

## 26. Exact next action
E4 identified mechanism-relevant components on the sealed structural endpoints; E5 can close the theory-to-experiment loop if still needed for the paper. Do not auto-schedule E6/E7.
