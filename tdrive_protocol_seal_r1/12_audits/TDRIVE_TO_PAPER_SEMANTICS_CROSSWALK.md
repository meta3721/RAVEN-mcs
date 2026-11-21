# T-Drive → paper semantics

| T-Drive concept | Paper symbol | Data field | Source | Real/controlled |
|---|---|---|---|---|
| client-fleet taxi | k | client_id = vehicle::{id} | processed client_measurements | REAL_FROM_TDRIVE |
| 500 m cell × 30 min slot | i | unit_id | processed atomic_units | REAL_FROM_TDRIVE geometry/time |
| H1–H4 local TOD | h(i) | protocol fallback | PRE_REGISTERED_PROTOCOL_FALLBACK | public metadata |
| processed target_group | not paper h(i) | target_group | adapter | recovered, unused as h |
| spatial×block×weekday | s(i) | opportunity_stratum | processed | public metadata |
| taxi in cell×slot | R | client_measurements row | processed | REAL_FROM_TDRIVE |
| valid observed speed after filters + controlled p_obs | O | EventTrace O | adapter + E3 transfer | DETERMINISTIC_DATA_QUALITY + CONTROLLED_EXPERIMENTAL |
| usable federated update | U | EventTrace U | E3 complete_aligned | CONTROLLED_EXPERIMENTAL |
| reference-fleet mean speed | Y_i | target_value | processed | REAL_FROM_TDRIVE (reference fleet) |
| public target weights | mu | TDRIVE_TARGET_MU.csv | test-unit frequency over h(i) | deterministic metadata |
| arrival-risk factors | pi, nu, p_obs, q_use | EventTrace + method hats | mixed | p_obs/q controlled; pi/nu method-internal |
