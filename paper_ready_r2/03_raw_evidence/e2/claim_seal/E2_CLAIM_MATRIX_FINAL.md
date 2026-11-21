# E2_CLAIM_MATRIX_FINAL

## C1: SUPPORTED_WITH_SCENARIO_QUALIFICATION
Biased traffic-selection scenarios alter arrival-weighted risk
- Evidence: SCENARIO_VS_BALANCED_STATS RMSE_rho (Observation-only, Complete-aligned)
- Allowed: Traffic-selection bias can alter arrival-weighted risk, especially under Observation-only and Complete-aligned.
- Prohibited: All biased scenarios significantly alter arrival risk.

## C2: PARTIALLY_SUPPORTED
Biased traffic-selection scenarios alter target-weighted risk
- Evidence: SCENARIO_VS_BALANCED_STATS RMSE_mu
- Allowed: Target-weighted risk changes are limited and scenario-specific under the formal matrix.
- Prohibited: All biased scenarios significantly alter target risk.

## C3: SUPPORTED
Arrival-weighted and target-weighted risk are not interchangeable under selection bias
- Evidence: COMPLETE_ALIGNED_DOD_SUMMARY
- Allowed: Arrival-weighted and deployment-target-weighted risk are not interchangeable under traffic-selection bias.
- Prohibited: Complete-aligned always worsens target risk more than arrival risk.

## C4: UNSUPPORTED
Complete-aligned causes target-risk deterioration larger than arrival-risk deterioration
- Evidence: COMPLETE_ALIGNED_DOD_SUMMARY
- Allowed: The originally hypothesized Complete-aligned directional DoD is not supported.
- Prohibited: Complete-aligned confirms larger target-risk deterioration.

## C5: UNSUPPORTED
Complete-counteracting frequently yields arrival improvement without target improvement
- Evidence: COMPLETE_COUNTERACTING_EVENT_SUMMARY
- Allowed: The preregistered Complete-counteracting directional event is unsupported.
- Prohibited: Complete-counteracting confirms the preregistered event.

## C6: UNSUPPORTED
RAVEN significantly improves RMSE_mu over all baselines
- Evidence: RAVEN_VS_BASELINE_SECONDARY RMSE_mu (0/24 Holm-significant)
- Allowed: Formal E2 evidence does not establish RAVEN RMSE_mu dominance over baselines.
- Prohibited: RAVEN significantly improves RMSE_mu / outperforms all baselines.

## C7: UNSUPPORTED
RAVEN significantly improves RMSE_rho over all baselines
- Evidence: RAVEN_VS_BASELINE_SECONDARY RMSE_rho
- Allowed: Formal E2 evidence does not establish RAVEN RMSE_rho dominance over baselines.
- Prohibited: RAVEN significantly improves RMSE_rho.

## C8: UNSUPPORTED
RAVEN significantly reduces arrival-target risk discrepancy
- Evidence: signed Gap_mis + ABS_GAP secondary; no Holm advantage
- Allowed: No corrected evidence supports a RAVEN discrepancy-reduction claim.
- Prohibited: RAVEN significantly reduces misalignment / smaller Gap_mis means less misalignment.

## C9: UNSUPPORTED
RAVEN improves Tail/group disparity
- Evidence: STRUCTURAL_STATS_TOLERANCE_CORRECTED + DELTA_GROUP_..._TOLERANCE_CORRECTED; Delta_pair unavailable
- Allowed: Corrected analysis does not support a statistically significant RAVEN advantage in Head/Tail RMSE or Delta_group.
- Prohibited: RAVEN significantly improves tail fairness/group disparity.

## C10: PARTIALLY_SUPPORTED
E2 supports the paper's target-risk-misalignment motivation
- Evidence: C3 supported; algorithm directional claims unsupported
- Allowed: E2 supports explicitly reasoning about target risk under selection bias, without claiming universal RAVEN superiority.
- Prohibited: E2 proves RAVEN solves target-risk misalignment.
