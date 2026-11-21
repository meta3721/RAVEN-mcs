# Submission evidence index (single entry)

This is the one index for the numbers added after the frozen bundle was sealed. Every row names the
paper location, the quantity, the protocol or comparator it belongs to, the file that carries it, and
the scoring identity. Nothing here replaces the bundle's own `w1/PAPER_NUMBERS.csv`; that file remains the
index for the numbers it already covers.

Access status is stated per row and means exactly one of:

- `packaged` - the file is in `submission_evidence/` next to this index and ships with the submission;
- `local-only` - the file exists in the author's working tree and is not in the submitted material;
- `public` - an external public source.

Long paths are given relative to the working tree so the index is usable internally; none of them is a
C-drive path that a reviewer would be asked to open.

| paper location | quantity | unit | protocol / comparator | file | key or line | scoring identity | access |
|---|---|---|---|---|---|---|---|
| Table VI (matched support) | W1 trained-rule trade-off cells | `RMSE_mu`, `Delta` | matched active set, 20 seeds | `submission_evidence/W1_TRADEOFF_V51.csv` | per-contrast rows | theta-canonical (v5.1 errata) | packaged |
| Sec. VII-E, independent projection | `A1'` implementation values, incl. the `kappa=1000` variant | `eps_impl`, `Delta` | independent projection comparison | `submission_evidence/W1_A1P_IMPL_RERUN.csv` | per cell | `approximate`, `eps_impl <= 2.42e-05` | packaged |
| Table VIII (concentration) | oracle-margin gap vs target concentration, 4 rungs | % of uncorrected member | frozen server step, 20 seeds, declared target | `submission_evidence/TE2_CONCENTRATION_STEP4.json` | `ceiling_ladder[*]` | theta-consistent; single-region rung `+0.097 %` | packaged |
| Table VIII, primary cell | `kappa=5` primary contrast | `RMSE_mu` | frozen server step, 20 seeds | `submission_evidence/TE2_CONCENTRATION_STEP3.json` | `contrasts[*]` | frozen pre-registration | packaged |
| Table VIII, pre-registration | target artifact, ladder, endpoint, decision rule | - | fixed before the runs | `submission_evidence/TE2_FROZEN_PREREG.json` | whole file | frozen before runs | packaged |
| Table VIII, per-seed | 80 cells x metrics | `RMSE_mu`, `Delta` | as above | `submission_evidence/TE2_MAIN.csv` | per row | as above | packaged |
| Adam sensitivity (Sec. VII) | paired oracle-margin headroom after the Adam step | % (`H`) | 15 confirm seeds | `submission_evidence/TE1_ADAM_VERDICT.json` | `mean_H`, `MDE80` | `MDE80 = 5.80 %` | packaged |
| Adam sensitivity, per-seed | per-seed test `RMSE_mu` | `RMSE_mu` | 15 confirm seeds | `submission_evidence/TE1_CONFIRM.csv` | per seed | as above | packaged |
| Adam sensitivity, structural readout | `Delta_group`, `Delta_c-s` on the same runs | pp | scored after the prediction contrast | `submission_evidence/TS1_STRUCT_SUMMARY.json` | `mean`, `ci` | exploratory, post-hoc | packaged |
| Adam sensitivity, pairs | per-seed structural deltas | pp | as above | `submission_evidence/TS1_PAIRS.csv` | per seed | as above | packaged |
| Table XX (U-Air context) | active-set audit of the FedAvg row | `RMSE_mu`, `WorstGroupRMSE` | current runner, keeps every delivered client | `submission_evidence/UAIR_TABLE2_AUDIT_SUMMARY.csv` | per method | current-runner re-run | packaged |
| Table XX, audit metadata | recomputation check and seed count | - | - | `submission_evidence/UAIR_TABLE2_AUDIT_META.json` | whole file | as above | packaged |
| Figs. 5-6 (U-Air rows) | theta re-score of the four affected arms at seeds 30007/30016/30018 | `RMSE_mu`, `Tail_RMSE` | saved-checkpoint re-forward | `submission_evidence/UAIR_THETA_ARMS.csv` | per arm, per seed | theta-canonical | packaged |
| Figs. 5-6 provenance | mirror/theta cell diff and the applied corrections | - | - | `submission_evidence/SEED_PATH_AUDIT_CELL_DIFF.md` | whole file | applied 2026-09-29 | packaged |
| Sec. VII-F, Table IX, appendix Tables XXX-XXXI, Fig. 8 | learning and development geometry | various | `results_main_rebuild_r1/` | `results_main_rebuild_r1/` | summaries only | development-only, not RAVEN gain | local-only |
| Sec. VII-A | closable-gap `3.44` pp (SensorScope) and `1.32` pp (U-Air) | pp | protocol R always-on, 20 seeds | `submission_evidence/W1_PHASE3_REPORT_round_v2.md` | line 77 | **report-level source only**: not recomputed from raw values in this round | packaged |
| bundle-wide | frozen targets, EventTraces, paired results, figure/table sources | - | - | `README.md`, `w1/PAPER_NUMBERS.csv` | as indexed there | frozen bundle | packaged |

## City Scanner main-text evidence (2026-10-18 six-arm promotion)

The two ranking blocks are now Table II in Section VII-B, not appendix-only
rankings. Original CSV names and their protocols are unchanged. Five methods
are retained per block. All prediction scores are on each protocol's own
training-standardized scale, not a common physical scale. Locations below
are relative to this bundle unless explicitly labelled working-tree paths.

- Table II(a), real visit occupancy, controlled O/U: `cityscanner/CS_E3.csv`,
  `cityscanner/CS_E3_SUMMARY.csv`, `cityscanner/CS_E3_PAIRED.csv` (**packaged**).
  Fields `RMSE_mu`, `WorstGroupRMSE`, `Delta_group`, `Delta_c_s`; summary
  mean/SD over ten paired seeds. Paired relative differences are means of
  seed-level ratios, not ratios of displayed means.
- Table II(b), union-GPS R, measured PM observation, controlled U:
  `cityscanner_p2/JO_E3.csv`, `cityscanner_p2/JO_E3_SUMMARY.csv`,
  `cityscanner_p2/JO_E3_PAIRED.csv` (**packaged**). NO2 supplies GPS only.
  The missed original improvement criterion remains unchanged.
- Section VII-B, main Table III and appendix Table XXIX, separate six-arm trained map
  comparison: working-tree `results_gatekeeping/round_v1/C1_ARM_SUMMARY.csv`,
  `C1_RUNS.csv`, `C1_A1_CHAINS.csv`, `C1_PRIMARY.json`, `C1_SECONDARY.csv`,
  `C1_MAPS.json`, `C1_ANALYSIS_PROVENANCE.json`, `PREREG.md`, and
  `EXECUTION_REPORT.md` Part B (**local-only**).
  There are ten traces with three model seeds within each trace: 180 endpoint
  cells (150 newly trained, 30 reused), not 180 independent traces. Means/SD
  use trace means; the primary interval and p-value are the saved statistics,
  without re-testing. The 101.9% value is group-alignment gain retention.
  All three registered structural comparisons (floor/M1mu/M2mu vs FedAvg)
  reject: each has group mismatch lower on 10/10 traces and individual
  one-sided Wilcoxon p=0.0009765625 under the registered graphical allocation.
  This p is not Holm-adjusted. Their 2% prediction non-inferiority nodes do
  not reject; superiority is not tested. The separate four-member secondary
  Holm family has no significant member. Client-stratum gaps in Table XXIX
  refer to each arm's own target map. These files are not
  claimed to have been uploaded or inserted into the sealed bundle.

Current main tables: I datasets, II primary City Scanner five-method blocks,
III six-arm target maps, IV T-Drive, V controlled station protocols,
VI matched-support rules, VII ablations, VIII concentration, IX development
geometry. Appendix tables run X-XXXI; City Scanner construction and chain
details remain in Appendix J-D. The 25.8%/23.3% minimum-group claims apply
only to the five methods in each Table II block; Table III uses a distinct
three-model-seed trace aggregation. The six-arm M1mu/M2mu trained variants do
not validate disputed fixed-checkpoint population/311 rescoring.

## Open items this index does not close

1. `3.44` and `1.32` pp have a **report-level** source (the Phase 3 report, line 77) and remain
   `UNLOCATED` in `w1/PAPER_NUMBERS.csv`. This index records the report path and the limitation; it does
   **not** upgrade them to "recomputed from raw values".
2. The learning and development geometry material (`results_main_rebuild_r1/`) is **local-only** in this
   delivery. It is not claimed to be public or bundled.
3. Publishing or uploading the local-only material is left to the author; this round did not upload
   anything.
