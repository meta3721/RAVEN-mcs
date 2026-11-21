# TE1 gates

## G0 identity (traffic, eta_s = 0.003, R = 1, seed 30001)

| arm | S1' RMSE_mu | re-run RMSE_mu | bit match | differing fields |
|---|---:|---:|---|---|
| fedavg_window | 0.8274680256045374 | 0.8274680256045374 | True | ['runtime_seconds'] |
| raven_simoracle | 0.8102506853916549 | 0.8102506853916549 | True | ['runtime_seconds'] |

Server optimizer (frozen): `{"mode": "adam", "eta_s": 0.003, "beta1": 0.9, "beta2": 0.99, "tau": 0.001}`

LOCAL_STEPS = 2; copy of the S1' driver sha256 `46e46328a78053d187595f76a035fc69d499fbe818aef331abe083c2a011640f`.
