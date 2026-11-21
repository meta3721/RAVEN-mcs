# Local-Hajek weight dependency proof

## Decision
`MODEL_INDEPENDENT` with respect to model parameters, loss, gradients, prediction residuals, and post-update theta.

## Formal source binding
- Formal source revision: `b01db69e8554a33446c438c060ac464dcfadac24`
- Frozen `window_runner.py` hash: `f7bff5e30c76898f5ab3e3998021f9b09e52ccf73f135b44bc4e141d9e13c436`
- Current file hash: `f7bff5e30c76898f5ab3e3998021f9b09e52ccf73f135b44bc4e141d9e13c436` (exact match to formal freeze)

## Construction path
In `_process_window`, Local-Hajek weights are built before local SGD:

1. `zeta = _compute_zeta(client, opportunity_strata)`
   - Formal runs supply frozen `pi_opp_joint`, so zeta uses frozen `pi_target` + `pi_opp_joint` via `zeta_hat_stratum`.
   - The online `OpportunityEstimator` branch is not used on this formal path.
2. `p_hat = _compute_p_hat(features)`
   - Features are EventTrace-derived (`bias`, `hour_block`, `planned_workload_pre`).
   - `ObservationPropensity.predict` / lagged `update_records_after_completion` consume only those features and `rec.O`.
3. `a_raw = raw_weights(zeta, p_hat)` then `a_bar = normalized_weights(rec.O, a_raw, m_total)`.
4. Applied training weights are `a_bar[obs_mask]` when `uses_hajek_local_loss` is true.

## Zero-update implication
Replacing local SGD with zero updates changes theta, but theta is not an input to zeta, p_hat, or a_bar. Lagged propensity still updates from immutable EventTrace observations, identically under zero-update replay.

## Conclusion
Formal Local-Hajek `a_bar` is determined by immutable/public pre-training and EventTrace/protocol state. Zero-update replay can certify formal weight provenance.
