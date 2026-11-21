# E2_CLAIM_MATRIX

## C1: SUPPORTED
Biased scenarios alter arrival-weighted risk (RMSE_rho)
- Evidence: SCENARIO_VS_BALANCED_STATS
- Permitted: State the claim with corrected significance references.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C2: SUPPORTED
Biased scenarios alter target-weighted risk (RMSE_mu)
- Evidence: SCENARIO_VS_BALANCED_STATS
- Permitted: State the claim with corrected significance references.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C3: SUPPORTED
Arrival and target risks are not interchangeable under selection bias
- Evidence: COMPLETE_ALIGNED_DOD / Gap_mis
- Permitted: State the claim with corrected significance references.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C4: UNSUPPORTED
Complete-aligned: target-risk deterioration larger than arrival-risk
- Evidence: COMPLETE_ALIGNED_DOD_SUMMARY
- Permitted: State that the preregistered claim is not supported.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C5: UNSUPPORTED
Complete-counteracting frequently yields arrival improvement without target improvement
- Evidence: COMPLETE_COUNTERACTING_EVENT
- Permitted: State that the preregistered claim is not supported.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C6: PARTIALLY_SUPPORTED
RAVEN significantly improves RMSE_mu over all baselines
- Evidence: RAVEN_VS_BASELINE_SECONDARY
- Permitted: State limited/qualified support only.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C7: UNSUPPORTED
RAVEN significantly improves RMSE_rho over all baselines
- Evidence: RAVEN_VS_BASELINE_SECONDARY
- Permitted: State that the preregistered claim is not supported.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C8: INCONCLUSIVE
RAVEN reduces arrival-target discrepancy in biased scenarios
- Evidence: Gap_mis signed; ABS_GAP secondary only
- Permitted: State evidence is inconclusive.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C9: NOT_TESTABLE_FROM_FROZEN_OUTPUTS
Tail/group disparity controlled better by RAVEN
- Evidence: HEAD_TAIL_RESULTS MISSING_EVIDENCE
- Permitted: Do not claim; mark missing evidence.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.

## C10: PARTIALLY_SUPPORTED
E2 supports paper central target-risk-misalignment motivation
- Evidence: claim synthesis
- Permitted: State limited/qualified support only.
- Forbidden: Do not upgrade this claim beyond its matrix status; no 'significantly outperforms all' language unless SUPPORTED.
