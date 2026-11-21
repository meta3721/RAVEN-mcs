# T-Drive speed-target semantics

Recovered from `TDriveSpeedAdapter` and the processed-data manifest (adapter=TDriveSpeedAdapter, seed=26001).

- Consecutive in-bbox GPS points form a segment.
- Distance is haversine kilometres (radius 6371 km).
- Time gap must satisfy `0 < dt <= 0.25` hours.
- Speed = distance / dt, kept only if in `[5, 120]` km/h.
- Reference fleet (30% of vehicles by trajectory length, seed 26001) builds `Y_i`.
- Client fleet (70%) supplies `potential_measurement`; the same GPS record cannot build both.
- `Y_i` is the mean reference speed in the 500 m cell × 30 min slot.

No label rule was selected from model performance.
