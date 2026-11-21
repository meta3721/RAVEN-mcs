# GAP_MIS_SEMANTIC_AUDIT

## Formula (code)

`gap_mis(rmse_target, rmse_arrival) = RMSE_mu - RMSE_rho`

Source: `src/raven_mcs/metrics/accuracy.py`.

## Answers

1. **Signed or absolute?** Signed.
2. **Which sign means RMSE_mu > RMSE_rho?** Positive Gap_mis.
3. **Is "smaller" always better?** No. A smaller (more negative) signed Gap_mis means larger arrival-weighted error relative to target-weighted error, not necessarily less misalignment.
4. **Can a lower signed value mean a more negative gap rather than less misalignment?** Yes.
5. **Paper scientific target?** The preregistered primary endpoint is the signed bias `Gap_mis = RMSE_mu - RMSE_rho`. Absolute discrepancy may be reported only as a derived secondary diagnostic: `ABS_GAP = |RMSE_mu - RMSE_rho|`.

## Interpretation constraint

Do **not** claim "RAVEN has the smallest Gap_mis, therefore it controls misalignment best" without clarifying signed semantics.
