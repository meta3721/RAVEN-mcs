# R1E window context provenance

Required mapping: `window_id -> public window timestamp -> TOD block`
via `RepeatableTimeOfDayMapper` (UTC hour // 6).

## Search

- EventTrace metadata UTC schedule present: False
- metadata keys: ['dataset', 'generator', 'notes', 'num_clients', 'num_windows', 's_max', 'seed']
- E3 generator abstract index clock: True
- E3 risk sets independent of wall-clock: True
- E2 300-window schedule reusable for sealed E3 traces: False
- raw window_id accepted by RepeatableTimeOfDayMapper: False

## Decision

- legal: False
- verdict: NO_LEGAL_PREWINDOW_CONTEXT_FOR_R1E

Sealed E3 EventTrace metadata stores only dataset/seed/num_windows/num_clients/s_max/generator. The complete-aligned R3 generator clocks windows as abstract index time (deadline = window_id + 1.0), not UTC. Risk sets are sampled from the train pool independently of dataset absolute_time. RepeatableTimeOfDayMapper requires a UTC datetime; raw window_id is not a legal input. Reusing the E2 300-window SensorScope schedule would invent a mapping that is not the sealed E3 protocol. No frozen window_id -> UTC timestamp table exists. Inferring the block from the current window's first EventTrace row would use current-window event presence and is forbidden.

Current-window EventTrace event presence was not used.
No invented UTC origin was attached to `window_id`.
