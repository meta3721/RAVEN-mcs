# Claim-to-Data Map

## C1
Two-stage non-random selection can create deployment-target mismatch.
- Primary: `01_core_data/e2/E2_RISK_NONINTERCHANGEABILITY_MASTER.csv`
- Strength: `supported`
- Excluded: none

## C2
Arrival/usable risk is not generally interchangeable with deployment-target risk.
- Primary: `01_core_data/e2/E2_D_ALIGNED_SUMMARY.csv`
- Strength: `supported`
- Excluded: none

## C3
RAVEN reduces structural target mismatch on SensorScope + U-Air.
- Primary: `01_core_data/e3/E3_STRUCTURAL_METRICS_MASTER.csv`
- Strength: `supported`
- Excluded: NSW-Traffic NOT_COMPARABLE

## C4
RAVEN prediction risk is competitive with selective significant gains, not universal superiority.
- Primary: `01_core_data/e3/E3_PREDICTION_METRICS_MASTER.csv`
- Strength: `supported_selective`
- Excluded: Traffic

## C5
RAVEN components have endpoint-dependent roles/trade-offs.
- Primary: `01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv`
- Strength: `supported`
- Excluded: wo_inst Gen0/Gen1

## C6
Use currently has no robust marginal effect under Complete-aligned E4.
- Primary: `01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv`
- Strength: `NO_CLEAR_EFFECT`
- Excluded: none

## C7
Debt has statistically stable but quantitatively small structural effect.
- Primary: `01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv`
- Strength: `STRUCTURAL_ONLY_SUPPORTED`
- Excluded: none

## C8
Traffic E3 cross-vintage comparison is NOT_COMPARABLE.
- Primary: `02_supporting_data/e3/E3_TRAFFIC_NOT_COMPARABLE_INDEX.csv`
- Strength: `NOT_COMPARABLE`
- Excluded: must not enter main inference tables

## C9
P2 warning-affected outputs are feasibility-audited; exact optimality not reconstructable.
- Primary: `02_supporting_data/solver/P2_FEASIBILITY_SUMMARY.csv`
- Strength: `feasibility_certified_optimality_not_reconstructable`
- Excluded: none
