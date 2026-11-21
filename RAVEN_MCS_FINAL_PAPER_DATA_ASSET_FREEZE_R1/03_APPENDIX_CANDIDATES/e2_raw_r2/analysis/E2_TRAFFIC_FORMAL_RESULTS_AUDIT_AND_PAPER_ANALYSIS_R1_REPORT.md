# E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1_REPORT

## 1. Executive conclusion

Final status: **E2_TRAFFIC_ANALYSIS_PARTIALLY_SEALED**

600 frozen formal runs were audited without retraining. Primary scenario-vs-Balanced analyses, Complete-aligned DoD, Complete-counteracting events, Gap_mis semantic audit, and Holm-corrected secondary RAVEN comparisons are complete. Protocol Head/Tail and Delta_group/Delta_pair are **MISSING_EVIDENCE** from frozen outputs.

## 2. Frozen 600-run identity

- Verification: `PASS`
- Rows: 600 (expected 600)
- Seeds: 30001–30020
- Scenarios: S1–S6
- Methods: 5 frozen methods
- Duplicate logical results: 0
- All completed_windows=100: True

## 3. Source-freeze retrospective audit

- Decision: **PASS**
- PRE_RUN_COMMIT: `e56687813f2bcb919a9208391f68a4db3488602e`
- LATER_RUNTIME_COMMIT: `b01db69e8554a33446c438c060ac464dcfadac24`
- Rationale: Working-tree SOURCE_HASHES for scientific result-producing files still MATCH. Git commit transition added previously untracked formal harness/runner files; no post-freeze scientific hash drift detected on disk. Git diff lists 1 SCIENTIFIC_CORE paths relative to empty pre-run tree; these are classified as commit-packaging of already-running code, not mid-run retuning.

## 4. Ledger attempt-level audit

- Training START count: 601
- Training FINISH count: 600
- Orphan START count: 1
- Interrupted attempts: 0
- Accepted logical runs: 600
- Historical ledger was **not** rewritten.

## 5. Metric reconstruction audit

| Metric | Status |
|---|---|
| RMSE_mu | reconstructed from formal_results |
| RMSE_rho | reconstructed from formal_results |
| Gap_mis | reconstructed from formal_results (signed) |
| ABS_GAP | derived secondary `|RMSE_mu-RMSE_rho|` available on demand |
| Head_RMSE / Tail_RMSE | MISSING_EVIDENCE |
| Delta_group / Delta_pair | MISSING_EVIDENCE |
| block0–block3 RMSE | available; descriptive group range used |

## 6. Gap_mis semantic audit

See `GAP_MIS_SEMANTIC_AUDIT.md`. Gap_mis is signed; smaller is not always better.

## 7–8. Scenario-vs-Balanced primary + Holm

See `SCENARIO_VS_BALANCED_STATS.csv`. Holm families: per (method, metric) across 5 non-Balanced scenarios. Alpha=0.05.

## 9. Complete-aligned DoD

See `COMPLETE_ALIGNED_DOD_SUMMARY.json`. Direction is reported honestly (not forced).

## 10. Complete-counteracting event

See `COMPLETE_COUNTERACTING_EVENT_SUMMARY.json`. Low event rates => C5 UNSUPPORTED where applicable.

## 11. Head/Tail/group disparity

Protocol Head/Tail/Delta_group/Delta_pair: MISSING_EVIDENCE. Descriptive block RMSE range analyses provided.

## 12. RAVEN-vs-baseline secondary

See `RAVEN_VS_BASELINE_SECONDARY.csv`. Significance only via Holm within per-metric scenario×baseline families.

## 13. Claim matrix

See `E2_CLAIM_MATRIX.md`.

## 14. Paper-ready result statements

- Execution: 600 formal runs completed and attempt-audited.
- Scientific: selection bias can separate arrival-weighted and target-weighted risk behavior; some directional hypotheses are unsupported.
- Algorithm: RAVEN is not assumed to dominate all baselines; only Holm-supported differences may be stated.

## 15. Negative and inconclusive findings

- Complete-counteracting directional event is generally rare/unsupported.
- Complete-aligned hypothesized D_aligned sign may be unsupported depending on method means.
- Head/Tail disparity claims are not testable from frozen outputs.

## 16. Limitations

- No offline re-evaluation from checkpoints (would be new computation beyond stored metrics).
- Signed Gap_mis must not be misread as absolute misalignment.
- One interrupted ledger START exists historically; acceptance uses PASS manifests.

## 17. Final E2 closure decision

**E2_TRAFFIC_ANALYSIS_PARTIALLY_SEALED**

## 18. Next-step recommendation

If full scientific seal is required for Head/Tail/Delta_group, authorize a separate **offline metric reconstruction round from frozen checkpoints** (still no training/retuning). Otherwise proceed to paper drafting using the claim matrix as the wording boundary.
