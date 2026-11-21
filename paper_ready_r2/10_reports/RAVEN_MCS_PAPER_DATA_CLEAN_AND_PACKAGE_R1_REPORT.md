# RAVEN-MCS-PAPER-DATA-CLEAN-AND-PACKAGE-R1 Report

## 1. Executive summary
- Final status: `PAPER_DATA_R1_COMPLETE_TDRIVE_NOT_READY`
- E2 runs: 600; EventTraces: 120
- E3 index rows: 660 (formal+reused)
- E4 core cells: 240 (wo_inst Gen2 only in core)
- Gates: 30/30 pass

## 2. No-training/no-rerun attestation
- training_started=false
- formal_runs_started=false
- No E1/E2/E3/E4 reruns; no T-Drive formal runs; no E5+.

## 3. Source roots discovered
- See `00_index/ALL_RELEVANT_SOURCE_PATHS.csv`

## 4. E1 collection status
- {'round': 'E1', 'n_valid_runs': 25, 'sources_found': ['aggregate_summary', 'gate_report', 'holm', 'no_harm_summary', 'per_seed', 'stats_report', 'table_main', 'table_no_harm', 'table_per_seed', 'wilcoxon'], 'sources_missing': [], 'core_complete': True, 'notes': 'E1 sealed outputs taken from outputs/aggregate/E1_R2 and outputs/statistics/E1_R2_FINAL_SEALED'}

## 5. E2 collection status
- {'round': 'E2', 'n_valid_runs': 600, 'n_eventtraces': 120, 'n_d_aligned_rows': 100, 'expected_runs': 600, 'expected_eventtraces': 120, 'core_complete': True, 'raw_files_copied': 4328}

## 6. E3 collection status
- {'round': 'E3', 'n_index_rows': 660, 'n_formal_status_rows': 560, 'n_reused_traffic': 100, 'n_main_comparable': 440, 'n_traffic': 220, 'expected_merged': 660, 'core_complete': True}

## 7. E4 collection status
- {'round': 'E4', 'n_core_cells': 240, 'expected_cells': 240, 'n_wo_inst_gen2': 40, 'wo_inst_policy': 'Only Generation 2 FINAL_VALID_ONE_FACTOR enters PAPER_CORE', 'gen0_archive': 'artifacts/e4_core_mechanism_ablation_r1', 'gen1_archive': 'artifacts/e4_ablation_semantic_integrity_repair_r1', 'gen2_source': 'artifacts/e4_wo_inst_reference_penalty_final_correction_r1', 'core_complete': True, 'design_774_present': True}

## 8. w/o-Inst generation handling
- Gen0 INVALID_P2_OFF → FULL_ARCHIVE only
- Gen1 SUPERSEDED_REFERENCE_PENALTY_MISMATCH → FULL_ARCHIVE only
- Gen2 FINAL_VALID_ONE_FACTOR → PAPER_CORE (40 cells)

## 9. Traffic comparability handling
- E2 Traffic: paper-core for risk non-interchangeability
- E3 Traffic: NOT_COMPARABLE_CROSS_VINTAGE; supporting/reference only

## 10. Local-Hajek provenance
- Collected under `02_supporting_data/e3/` and `03_raw_evidence/e3/local_hajek/`

## 11. P2 solver evidence
- Collected under `02_supporting_data/solver/`

## 12. Theory-diagnostic availability
- See `02_supporting_data/diagnostics/THEORY_DIAGNOSTIC_AVAILABILITY.csv`

## 13. Runtime/system data availability
- See `02_supporting_data/runtime/`

## 14. T-Drive readiness
- status=`NOT_READY_OTHER`
- blockers=['Not ready: opportunity_definition', 'Not ready: eventtrace_generation', 'Not ready: train_val_test_split_frozen', 'EventTrace / split / opportunity freeze incomplete']

## 15. Master evidence table status
- `01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv`
- `01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL.csv`

## 16. Main table-source files
- `06_table_sources/TABLE_E*.csv` (+ meta JSON)

## 17. Main figure-source files
- `07_figure_sources/FIG1_*.csv`, `FIG2_*.csv`, `FIG3_*.csv`

## 18. Extra optional data collected
- See `EXTRA_DATA_COLLECTED.md`

## 19. Missing potentially useful data
- See `MISSING_POTENTIALLY_USEFUL_DATA.md`

## 20. Package contents
- CORE: `D:\Cursor\raven.mcs\deliverables\RAVEN_MCS_PAPER_DATA_CORE_R1.zip` members=101
- FULL: `D:\Cursor\raven.mcs\deliverables\RAVEN_MCS_PAPER_DATA_FULL_EVIDENCE_R1.zip` members=4753

## 21. Hash verification
- CORE pass=True
- FULL pass=True

## 22. Recommended next step
- Use CORE zip for paper drafting; consult FULL for audits/appendix.
- T-Drive formal block only after separate authorization if readiness reaches READY.
