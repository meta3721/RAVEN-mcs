# RAVEN-MCS final paper data asset freeze R1

Round: `RAVEN-MCS-FINAL-PAPER-DATA-ASSET-FREEZE-R1`

## 1. Executive decision

**B. RAVEN_MCS_FINAL_DATA_R1_FROZEN_CORE_READY_SUPPORTING_GAPS_REMAIN**

Manuscript-critical E1–E4 data are complete. Supporting gaps remain and do **not** justify new experiments.

## 2. No-new-experiment attestation

All flags false. Writes only under `RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1/` and `deliverables/`. Original sealed evidence and R2 were not modified.

## 3. Frozen paper theme

Selection-induced deployment-target mismatch → selection-layer-aware correction → feasibility-aware target calibration → reduced structural mismatch with competitive prediction risk.

## 4. Frozen contributions

(1) deployment-target risk semantics; (2) selection-layer-aware reconstruction; (3) feasibility-aware instantaneous and long-term calibration. Not five independent component innovations.

## 5. Frozen structure

Sections I–IX + Appendix as specified in the freeze instruction.

## 6. Frozen RQs

Exactly RQ1–RQ3.

## 7. Evidence authority hierarchy

`paper_ready_r2` scientific values > sealed E3/E4 raw referenced by R2 > earlier only if not superseded. Manuscript-closure R1 is the paper-facing table/figure presentation layer.

## 8. Master catalog

`00_MASTER_CATALOG/MASTER_DATA_CATALOG.csv` — every freeze file hashed and classified.

## 9. E1 assets

25 valid paired runs (expected 25). PAPER_CORE / appendix sanity. No-harm; not superiority.

## 10. E2 assets

600 formal accepted runs (expected 600). 120 EventTraces hash-indexed. D_aligned is the core quantity. Not a RAVEN ranking block.

## 11. E3 assets

660 indexed cells (expected 660). SensorScope/U-Air scientifically comparable cells captured (expected 440 including reference methods). Traffic isolated as NOT_COMPARABLE. Central/SimOracle = REFERENCE_ONLY.

## 12. E4 assets

240 final valid core cells (expected 240). w/o-Inst Gen2 count=40. Labels: {'Design': 'ENDPOINT_TRADEOFF', 'Obs': 'ENDPOINT_TRADEOFF', 'Use': 'NO_CLEAR_EFFECT', 'Inst': 'ENDPOINT_TRADEOFF', 'Debt': 'STRUCTURAL_ONLY_SUPPORTED'}. Debt quantitatively small.

## 13. Run-level archive

`04_ALL_RUN_METRICS/ALL_VALID_RUNS_MASTER.csv` + parquet. N/A preserved.

## 14. Window-level archive

Existing `WINDOW_ACTIVE_CLIENTS_R2` indexed. No new windows.

## 15. Selection-process assets

Indexed from existing window/EventTrace provenance. Full atomic R/O/U stays in original EventTraces (hash index).

## 16. Propensity assets

Not sealed as distributions. Status MISSING_NOT_RECORDED. No new estimation.

## 17. Weight assets

Window alpha presence summarized; Local-Hajek degeneracy provenance preserved.

## 18. Calibration assets

Target composition trajectory MISSING_NOT_RECORDED.

## 19. Debt assets

Trajectory MISSING_NOT_RECORDED. Ablation effect is in E4 statistics.

## 20. P2 assets

Warning/feasibility masters copied. Claim boundary: feasibility audited; exact optimality not reconstructable.

## 21. ESS/variance assets

Run-level ESS scalars where recorded. Trajectory MISSING_NOT_RECORDED.

## 22. Runtime/system assets

Existing RUNTIME_MASTER indexed. No scalability rerun.

## 23. EventTrace assets

E2 120-trace index; E3/E4 identity manifests; T-Drive protocol-only fixture. Bulky traces not forced into CORE.

## 24. Config/source provenance

`FINAL_CONFIG_MASTER.csv`, `SOURCE_PROVENANCE_MASTER.csv`, `OFFLINE_DERIVATION_PROVENANCE.csv` (`scientific_semantics_changed=false`).

## 25. Dataset metadata

`DATASET_METADATA_FINAL.csv`. T-Drive = REVIEWER_RESERVE_PROTOCOL_ONLY, not an evaluated dataset.

## 26. Statistical-version audit

One paper-facing E4 Holm: R2 rebuilt. Pre-R2 / Gen1 Inst stats SUPERSEDED.

## 27. Superseded assets

`17_SUPERSEDED/` including w/o-Inst Gen1 and pre-R2 E4 stats.

## 28. Invalid/Canary assets

`18_INVALID_CANARY/` including w/o-Inst Gen0 P2-off.

## 29. Not-comparable assets

`19_NOT_COMPARABLE/` Traffic E3 cross-vintage.

## 30. T-Drive reserve

`formal_runs_completed=0`, `paper_result_status=NOT_RUN`, `protocol_status=SEALED`, `default_action=DO_NOT_RUN_BEFORE_SUBMISSION`.

## 31. Figure source library

FIG1–FIG4 sources ready. FIG5 insufficient existing data — do not run. FIG6–FIG8 optional appendix.

## 32. Table source library

Tables I–III + E1 appendix required; IV–VI appendix/optional.

## 33. Figure readiness

See `22_REPORTS/FIGURE_DATA_READINESS_AUDIT.csv`. No candidate has `needs_new_experiment=true` as an accepted action.

## 34. Table readiness

See `22_REPORTS/TABLE_DATA_READINESS_AUDIT.csv`.

## 35. Rebuttal asset map

`00_MASTER_CATALOG/REBUTTAL_ASSET_MAP.csv`. T-Drive marked REVIEWER_RESERVE.

## 36. Missing data

No CORE missing fields. Supporting/optional gaps listed in `MISSING_DATA_FINAL.csv`. None trigger experiments.

## 37. Data consistency

Conflicts=0. Unresolved CORE conflicts are not allowed.

## 38. Evidence counts

{'E1': 25, 'E2': 600, 'E3_total': 660, 'E3_comparable_SS_UAir': 440, 'E4': 240, 'wo_inst_gen2': 40}

## 39. Reproducibility

`14_SOURCE_PROVENANCE/REPRODUCIBILITY_INDEX.csv`.

## 40. Package verification

CORE pass=True n=202; FULL pass=True n=5022.

## 41. Is all manuscript-critical data available?

**YES.** RQ1/RQ2/RQ3 core fields are present. Supporting gaps do not block writing.

## 42. Recommended main figures

Fig.1 E2 D_aligned; Fig.2 E3 structural; Fig.4 E4 ablation. Optional main: Fig.3 E3 prediction if page budget allows (Table II already covers prediction).

## 43. Recommended appendix figures

Local-Hajek provenance; ESS/P2 diagnostic. Not FIG5.

## 44. Recommended main tables

Table I datasets; Table II E3; Table III E4. Appendix: E1, statistical summary, full methods.

## 45. Exact next action

STOP DATA EXPERIMENT WORK. Write Sections III–IX from frozen semantics and these assets. Do not activate T-Drive.
