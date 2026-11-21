# Theory-change decision (no paper edits this round)

**THEORY_DECISION_INCONCLUSIVE**

Overall R1k verdict: `R1K_ARCHITECTURE_AUDIT_INCONCLUSIVE`
Pairwise barrier: `STRUCTURAL_PAIRWISE_NONVACUITY_BARRIER_CONFIRMED`
Scale: `PREDICTOR_SCALE_DEFECT_PARTIAL`
Aggregate: `AGGREGATE_NOT_CALIBRATED`

This round does **not** modify Sections III–VI or any `.tex` file.
Aggregate C_LCB is a feasibility candidate, not a paper-method replacement.

If redesign is recommended, a later theory freeze would need to revisit:
- C_cov definition (pairwise opportunity LCBs vs aggregate coverage scalar)
- certificate theorem (simultaneous pair LCBs vs scalar conformal on C)
- Gate safety statement (what Y_cert guarantees)
- algorithm input/output (current mask still forbidden)
- experiment interpretation (natural vs stress tracks remain separate)

Correct next step after a redesign recommendation is theory reconstruction, not SAG.
