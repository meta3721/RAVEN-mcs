# R1m formal execution chain

C_t (R1i oracle, after completion) → C_hat_t (frozen ridge snapshot) →
S_t = C_hat - C_t → q_t (block conformal, n_min=19, no k_n clip) →
C_LCB = max(0, C_hat - q) → Gate_t = 1{C_LCB ≥ τ} → Design_t := Gate_t.

RESET: after CERTIFIED miscoverage, keep window t, then t+1 RESET / new block WARMUP.
