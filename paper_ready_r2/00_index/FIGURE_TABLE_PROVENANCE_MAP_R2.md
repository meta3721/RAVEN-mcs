# Figure/table provenance R2

## TABLE-1: Dataset summary
- CSV: `06_table_sources/TABLE_DATASET_SUMMARY_R2.csv`
- Filters: frozen metadata only; T-Drive readiness fields only
- Excluded: guessed fields; T-Drive formal results (none)
- Ceiling: Experimental Setup

## TABLE-2: E3 main effectiveness
- CSV: `06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv`
- Filters: SCI_COMPARABLE_MAIN SensorScope+U-Air
- Excluded: Traffic NOT_COMPARABLE
- Ceiling: C3,C4

## TABLE-3: E4 core ablation
- CSV: `06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv`
- Filters: 240 cells; w/o-Inst Gen2 only
- Excluded: w/o-Inst Gen0/Gen1
- Ceiling: C5,C6,C7,C8

## FIG-1: E2 risk non-interchangeability
- CSV: `07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv`
- Filters: E2 complete_aligned / D_aligned
- Excluded: E3 Traffic
- Ceiling: C1,C2

## FIG-2: E3 structural mismatch
- CSV: `07_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH.csv`
- Filters: SCI_COMPARABLE_MAIN
- Excluded: Traffic
- Ceiling: C3

## FIG-3: E4 component removal
- CSV: `07_figure_sources/FIG3_E4_COMPONENT_REMOVAL_R2.csv`
- Filters: final valid 240 cells
- Excluded: Gen0/Gen1 w/o-Inst
- Ceiling: C5,C6,C7,C8

## OPTIONAL-E1: E1 sanity
- CSV: `06_table_sources/TABLE_E1_BALANCED_SANITY.csv`
- Filters: E1_R2_FINAL_SEALED
- Excluded: 
- Ceiling: sanity / no-harm

## OPTIONAL-E3-RMSE: E3 RMSE
- CSV: `07_figure_sources/FIG_OPTIONAL_E3_RMSE.csv`
- Filters: SCI_COMPARABLE_MAIN
- Excluded: Traffic
- Ceiling: C4

## OPTIONAL-E3-TAIL: E3 Tail_RMSE
- CSV: `07_figure_sources/FIG_OPTIONAL_E3_TAIL_RMSE.csv`
- Filters: SCI_COMPARABLE_MAIN
- Excluded: Traffic
- Ceiling: C4

## OPTIONAL-P2: P2 diagnostics
- CSV: `06_table_sources/TABLE_P2_DIAGNOSTICS_SUPPLEMENT.csv`
- Filters: feasibility audit
- Excluded: certified exact optimality
- Ceiling: C10

## OPTIONAL-DEBT: Debt trajectory
- CSV: `07_figure_sources/FIG_OPTIONAL_DEBT_TRAJECTORY.csv`
- Filters: supporting only if present
- Excluded: do not promote to RQ
- Ceiling: supporting

## OPTIONAL-ESS: ESS
- CSV: `02_supporting_data/diagnostics_r2/RUNLEVEL_SEALED_SCALARS_R2.csv`
- Filters: run-level ESS scalar
- Excluded: not a trajectory
- Ceiling: supporting

## OPTIONAL-RUNTIME: runtime
- CSV: `02_supporting_data/diagnostics_r2/RUNLEVEL_SEALED_SCALARS_R2.csv`
- Filters: runtime_seconds
- Excluded: not P2-only runtime
- Ceiling: supporting
