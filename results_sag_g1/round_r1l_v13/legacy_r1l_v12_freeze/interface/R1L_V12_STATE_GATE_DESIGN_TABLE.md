# R1L-v1.2 state / Gate / Design mapping

Frozen equality: `Design_t := Gate_t` (per window).

| certificate_state | C_LCB condition | Gate_t | Design_t |
|---|---|---:|---:|
| WARMUP | not certified | 0 | OFF |
| RESET | not certified | 0 | OFF |
| CERTIFIED | C_LCB < tau_cov | 0 | OFF |
| CERTIFIED | C_LCB >= tau_cov | 1 | ON |

`DESIGN_ON` iff `Gate_t=1`. `DESIGN_OFF` iff `Gate_t=0`.
Dataset-level Design flags are not a formal control.
