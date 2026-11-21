# E3_FORMAL_RUNS_R1_REPORT

## 1. Executive decision
**E3_FORMAL_RUNS_COMPLETE_AND_SCIENTIFICALLY_SEALED**

## 2. No-extra-experiment attestation
No datasets/methods/metrics/seeds added. Canary seed 31001 excluded. No performance tuning.

## 3. Frozen source revision
`b01db69e8554a33446c438c060ac464dcfadac24` / manifest `4e0c37665eb6c75357de266c2df827a888d7ce42051b52b48b47027fa5cdace8`

## 4–11. Matrix / reuse / EventTrace / stages
New accepted: 560/560. Traffic reused: 100. Merged: 660.

## 12–14. Integrity / Ledger / raw seal
Raw seal present. Sealed five not rerun under formal art.

## 15–22. Results / statistics / claims
See `E3_FORMAL_SUMMARY.csv`, paired/Holm tables, `E3_CLAIM_MATRIX.md`.
Primary endpoint: RMSE_mu (physical domain).

## 23. Paper-mainline figures
`figures/E3_main_RMSE_mu.png`

## 24–25. Tests / hashes
`{'targeted': 0, 'integ': 0, 'full': 0, 'pip': 0}`

## 26. Remaining limitations
Traffic reused RMSE_rho may be NOT_COMPARABLE per frozen policy.

## 27. Recommendation
If sealed complete: stop E3 experimentation and write the paper from sealed evidence.
Do not retune or add experiments automatically.
