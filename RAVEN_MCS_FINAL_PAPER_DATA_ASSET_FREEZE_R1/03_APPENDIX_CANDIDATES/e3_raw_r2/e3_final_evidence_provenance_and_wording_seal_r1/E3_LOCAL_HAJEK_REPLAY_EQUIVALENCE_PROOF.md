# Local-Hajek formal-path vs replay-path equivalence

## Decision
`REPLAY_EQUIVALENCE_CERTIFIED = true`

## Paths compared
- **FORMAL:** accepted Local-Hajek run → EventTrace/prestate → Local-Hajek weight construction → `a_bar` → weighted local loss → backward.
- **REPLAY:** same immutable EventTrace/prestate → same weight construction → reconstructed `a_bar` (parent zero-update forensic replay).

## Equivalence checklist
1. Same source / hash-equivalent implementation: frozen `window_runner.py` hash `f7bff5e30c76898f5ab3e3998021f9b09e52ccf73f135b44bc4e141d9e13c436`.
2. Same inputs: all 40 formal×replay identity rows match (`all_identity_fields_match=true`).
3. Same branching: formal Local-Hajek uses `uses_hajek_local_loss` and frozen `pi_opp_joint`.
4. Same normalization: `raw_weights` → `normalized_weights`.
5. Same dtype/tolerance: float64 Hájek path; parent audit used `EPS_WEIGHT=1e-12` uniformity.
6. No training-state dependency for weights: `MODEL_INDEPENDENT`.
7. No post-hoc substitution of weights.
8. No synthetic replacement of EventTrace/prestate.

## Checkpoint identity
Parent checkpoint explanation remains CASE A for all audited seeds: accepted Local-Hajek checkpoints equal FedAvg, and the 9,666 effective client-windows are uniform. Collapse is therefore a protocol/data degeneracy, not an implementation failure.
