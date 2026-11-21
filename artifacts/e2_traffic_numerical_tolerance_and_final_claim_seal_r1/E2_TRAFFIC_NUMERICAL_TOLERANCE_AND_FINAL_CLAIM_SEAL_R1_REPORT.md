# E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1_REPORT

## 1. Executive decision

**E2_TRAFFIC_SCIENTIFICALLY_SEALED**

## 2. No-training attestation

No model was trained. No formal run was re-executed. Only offline paired-inference tolerance correction and claim/report consistency fixes were performed.

## 3. Frozen 600-result identity

Verification: `PASS` — 600 logical runs unchanged.

## 4. Numerical tolerance defect

Prior Delta_group RAVEN-vs-baseline comparisons treated ~1e-16 floating differences as nonzero Wilcoxon effects, creating pseudo-significance.

## 5. EPS_ZERO policy

EPS_ZERO = `1e-12` applied to paired differences before win/tie/loss, Wilcoxon, signs, and significance. See `NUMERICAL_TOLERANCE_POLICY.md`.

## 6. Delta_group corrected statistics

Holm-significant RAVEN-vs-baseline Delta_group count after correction: **0/24**.
ALL_TIES comparisons forced to non-significant inference.

## 7. Head/Tail corrected statistics

Recomputed under the same EPS_ZERO policy in `STRUCTURAL_STATS_TOLERANCE_CORRECTED.csv`.

## 8. Holm correction audit

Families unchanged: scenario-vs-Balanced = 5 per (method, metric); RAVEN-vs-baseline = 24 per metric.

## 9. Corrected Claim Matrix

See `E2_CLAIM_MATRIX_FINAL.md`. C9 = **UNSUPPORTED**.

## 10. Claim Validator results

See `CLAIM_EVIDENCE_VALIDATION_FINAL.json`.

## 11. Ledger anomaly final wording

- START = **601**
- FINISH = **600**
- accepted logical runs = **600**
- interrupted/orphan START = **1**
- historical ledger not rewritten

See `LEDGER_FINAL_SEAL_NOTE.md`.

## 12. Figure/table corrections

Pseudo-significant RAVEN structural-advantage figures removed/replaced. Final tables in `paper_tables/`.

## 13. Final supported claims

- C1 (with scenario qualification)
- C3 (non-interchangeability)
- C2/C10 partially

## 14. Final unsupported claims

- C4, C5, C6, C7, C8, C9

## 15. Paper-ready wording

See `E2_FINAL_PAPER_WORDING.md`.

## 16. Remaining limitations

- Delta_pair not reconstructable from frozen outputs.
- Signed Gap_mis is not absolute misalignment magnitude.

## 17. Final E2 closure status

**E2_TRAFFIC_SCIENTIFICALLY_SEALED**

## 18. Next-step recommendation

Stop E2 experiment expansion. Proceed to paper drafting under the final claim matrix and wording constraints. Do not start E3–E9 unless a new sealed experiment stage is explicitly authorized.
