# R1L-v1.2 Gate-to-Design provenance schema

Fields (frozen):

| field | role |
|---|---|
| dataset | audit label only; never a Design control |
| window_id | window index |
| block_id | certified-block identifier |
| predictor_snapshot_id | frozen snapshot id |
| certificate_state | WARMUP / CERTIFIED / RESET |
| n_cal | calibration count |
| C_hat | pre-window predictor |
| q | conformal quantile (NaN if not CERTIFIED) |
| C_LCB | aggregate lower certificate |
| tau_cov | 0.05 |
| Gate_t | 1{C_LCB >= tau_cov} in CERTIFIED; else 0 |
| Design_t | Design_t := Gate_t |
| design_branch | DESIGN_ON iff Gate_t=1; DESIGN_OFF iff Gate_t=0 |

Authority: aggregate coverage certificate only.
Forbidden controls: dataset name, static Design flag, oracle C_t, current mask.
