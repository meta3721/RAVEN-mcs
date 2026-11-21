# T-Drive real-mobility protocol master R1

This is the sole T-Drive protocol authority for later Canary/formal rounds.

## What is the real mobility evidence?
Beijing taxi GPS trajectories (MSR T-Drive sample) after bbox/gap/speed filters. Client-fleet presence in a 500 m × 30 min atomic unit is R=1.

## What exactly is a client?
One client-fleet taxi (`vehicle::{id}`). Reference-fleet taxis build Y and are not federated clients.

## What is an atomic unit?
`i = (spatial_id, 30-min slot)` with `Y_i` = mean reference-fleet speed (km/h).

## What is h(i)?
PRE_REGISTERED_PROTOCOL_FALLBACK: four Beijing-local time-of-day groups H1–H4. Processed `target_group` is not paper h(i).

## What is s(i)?
Processed `opportunity_stratum` = spatial_id × 4 TOD blocks × weekday/weekend. Distinct from h(i).

## What makes R=1?
A processed client_measurements row for that taxi and atomic unit.

## What makes O=1?
R=1 after data-quality filters, then a controlled Complete-aligned observation draw (p_obs=0.35). Not a recorded sensor failure log.

## What makes U=1?
Controlled compute AND network AND deadline AND tau≤5 AND nonempty observations. Not T-Drive hardware logs.

## How are splits defined?
Recovered processed 60/20/20 split by unique time slots (TemporalSplitConfig). Leakage audit must PASS.

## Which methods will run?
FedAvg-Window, FedAsync-Window, TimeAlign-Agg (`flamf_timealign_adapted`), TwoStage-Hajek, RAVEN-MCS.

## Which seeds will run?
30001–30010 matched across methods. Future formal size 50. This round executes 0.

## Which metrics are primary?
Delta_group, Delta_c_s, RMSE_mu. Success is not defined as an RMSE_mu win.

## What counts as success?
See claim decision rules: strong/partial/no-clear external consistency or counterevidence on structural endpoints.

## What claims are forbidden?
Universal RMSE superiority; treating controlled O/U as real failures; using T-Drive as a full ablation/scalability study.
