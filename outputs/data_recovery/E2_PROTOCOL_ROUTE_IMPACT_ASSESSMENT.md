# E2 Protocol Route Impact Assessment

Selected route: **B** (READY_WITH_REPLACEMENT_DATASET)

## Route A — Full SensorScope, keep 100×6h
- Feasible now: False
- Common span hours: 4254.933055555555
- Max complete 6h windows (common): 709
- Spatial: SPATIAL_METADATA_NOT_RECOVERED
- Impact on III–VI theory: none if restored
- Impact on E1: none (E1 remains immutable on current processed identity)

## Route B — Replacement dataset, keep 100×6h + theory
- Feasible now: True
- Selected: traffic
- Requires dataset mapping round before Balanced/Canary
- Must not alter RAVEN core theory

## Route C — Revise E2 window protocol
- Evaluated only this round; implementation forbidden without teacher approval
- Would affect experimental design, paper explanation, and data-protocol freeze
- Does not invalidate E1 formal results

## Decision reason
SensorScope joint fail; selected replacement=traffic
