# R1l symbol glossary

Each symbol has one meaning.

| Symbol | Meaning |
|---|---|
| I_tar | Frozen target-positive pair index set |
| pi_i^tar | Frozen target mass of pair i; sum_i pi_i^tar = 1 |
| pi_safe | Frozen PI_SAFE_RULE_V1 threshold |
| pi_{i,t}^opp | Realized opportunity of pair i in window t |
| C_t | Realized aggregate coverage: sum_i pi_i^tar 1{pi_{i,t}^opp >= pi_safe} in [0,1] |
| tau_cov | Frozen operational threshold 0.05. Gate compares C_LCB to tau_cov, not C_hat |
| F_{t-} | Legal pre-window information. Current mask / current C_t / future are excluded |
| a_t | Public scenario-level availability retention. Mask identity is not in F_{t-} |
| C_hat_t | Pre-window predictor f_t(F_{t-}). Not a certificate |
| S_t | One-sided score C_hat_t - C_t |
| g | Frozen public certified-regime descriptor |
| n | Number of strictly historical same-regime calibration scores |
| alpha | Nominal miscoverage 0.05 |
| n_min | 19 = ceil(1/alpha)-1 |
| k_n | ceil((n+1)(1-alpha)) |
| q_t | S_{(k_n)} when k_n <= n; otherwise undefined (WARMUP) |
| C_LCB,t | Unique certified scalar lower bound: max{0, C_hat_t - q_t} in CERTIFIED; 0 otherwise |
| Gate_t | 1{C_LCB,t >= tau_cov} in CERTIFIED; OFF in WARMUP and RESET |
| WARMUP / CERTIFIED / RESET | Exclusive certificate states |

Forbidden aliases:
- Do not call C_hat_t a certificate.
- Do not call clipped-k conformal a 95% certificate.
- Do not call pairwise lower_pi the formal Gate object.
