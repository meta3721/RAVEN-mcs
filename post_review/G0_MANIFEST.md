# G0 snapshot — post-review working directory

Date: 2026-08-23
Git HEAD (dirty working tree; not a new commit): `201e1092b53f76e16dc0aa7cf9acdfa55a386b30`
Branch: `paper-data-clean-and-package-r1`

This directory is a **read-only pointer + new G1 outputs**. It does **not** overwrite sealed E1–E4 artifacts, `paper_ready_r2/`, or T-Drive seals.

## Current manuscript (do not mix)

| Role | Path |
|---|---|
| Clean 21-page submission copy | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` + `main.pdf` |
| Richer working manuscript | `_paper_work/main.tex` + `main.pdf` |
| Sealed paper-ready package | `paper_ready_r2/` (**do not modify**) |

## Table / figure provenance (one-click)

| Paper object | Frozen source |
|---|---|
| Table II main effectiveness | `manuscript_evidence_closure_r1/01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv` |
| Table III core ablation | `manuscript_evidence_closure_r1/01_table_sources/TABLE_III_E4_CORE_ABLATION_FINAL.csv` |
| Fig. 3–6 source CSVs | `TO_OVERLEAF_paper_tmc_r1_clean/figure_data/` |
| Fig. 3–6 rendered | `TO_OVERLEAF_paper_tmc_r1_clean/figures/` |

## Sealed run trees used by G1

| Bundle | Path | Role |
|---|---|---|
| E3 formal | `artifacts/e3_formal_runs_r1/runs/{ds}/{raven,raven_simoracle}/seed{30001–30020}/` | Estimated-Design + Oracle-Design endpoints |
| E3 EventTraces | `artifacts/e3_formal_runs_r1/eventtraces/{ds}/seed{...}/training_eventtrace/` | Shared Complete-aligned traces (oracle_p/q present) |
| E4 core ablation | `artifacts/e4_core_mechanism_ablation_r1/runs/{ds}/raven_wo_design/seed{...}/` | No-Design endpoints |
| Phase A audit | `_paper_work/design_noharm_results/phase_a/` | Support-shift / window alignment (no new training) |

G0 gate: the rows above locate Table II, Table III, Fig. 3–6, and the U-Air Design reversal numbers without copying sealed bytes.

## Policy for new work

- New outputs only under `post_review/`.
- No test-set tuning. Test metrics are reported once after a val/pre-registered rule.
- Full RAVEN, w/o-Design, and SimOracle stay backward-comparable.
- G1 does **not** change the algorithm.
