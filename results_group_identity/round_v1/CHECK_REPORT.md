# Group-decomposition identity check (`RMSE_mu`)

stamp_utc: 2026-10-02T06:21:33.104577+00:00

## E1 — `RMSE_mu^2 = sum_b W_b RMSE_block_b^2`

- rows checked: 470 (City Scanner 150 cells; SensorScope/U-Air 320 rows from `post_review/G2_external_baselines/tables/per_seed.csv`)
- max absolute error over same-source rows: 1.776e-15 (pass line 1e-12; stop line 1e-08)
- rows marked `source_mismatch`: 0; rows marked `fail` above the stop line: 0
- block masses rebuilt from the scoring `mu` and the test-unit group counts via `_mu_weights_for_test`; the four blocks are never set to 0.25

## E2 — exact layer and Taylor layer (City Scanner)

- run->M1: exact 1.431e-16, taylor 1.092e-05
- run->M2: exact 9.021e-17, taylor 7.153e-06
- M1->M2: exact 8.153e-17, taylor 1.986e-05
- run->run+d (frozen d=(0.02,-0.01,-0.01,0)): exact 6.462e-17, taylor 4.579e-07  (target from the identity itself: the exact layer is not an independent check for this shift)

## E3 — pair order vs sign of `D(mu)`

- pairs checked: 30 (5 arms, 3 weight vectors)
- order/sign inconsistencies: 0
- all-four-components-same-sign violations: 0

## E4 — Design on/off `RMSE_mu` gap (RMSE only)

- sensorscope: published +0.00500%, identity +0.00536%, status recovered
- uair: published -6.88500%, identity -6.87500%, status recovered

`Delta_group`, `Delta_c-s` and Tail are **not** part of this check.

## E5 — within-group weight variance

- sensorscope (target_group (as scored)): max within-group variance 2.939e-39
- uair (target_group (as scored)): max within-group variance 1.175e-38
- cityscanner (target_group (region)): max within-group variance 1.175e-38

## Prohibited-claim audit

No claim of the following kinds is asserted anywhere in this report or in the artefacts of this run; they are listed here only so the audit is greppable.
- not asserted: "the model was retrained under an exogenous target"
- not asserted: "the switch point has been proved"
- not asserted: "the support loss is bounded"
- not asserted: "a rank flip means one method is better"
