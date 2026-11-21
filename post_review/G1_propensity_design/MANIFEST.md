# G1 propensity / Design diagnosis

Status: diagnosis only. No algorithm change. No sealed overwrite.

Script: `run_g1_diagnosis.py`
Inputs: G0 pointers in `../G0_MANIFEST.md`
Outputs: `tables/`, `figures/`, `DIAGNOSIS_REPORT.md`, `DECISION.md`

Included in this gate:
- Three-layer propensity panel from Complete-aligned EventTraces
- Six diagnostic figures
- Sealed Oracle-Design (`raven_simoracle`) vs Estimated (`raven`) vs No-Design (`raven_wo_design`)

Not included until the decision tree asks:
- G1-B gating (`zeta_tilde`)
- validation clipping grid on RMSE
- `lambda_g:lambda_beta` Pareto
- paper rewrite
