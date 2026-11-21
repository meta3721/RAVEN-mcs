# Gate-dose round — STOPPED by user instruction

Round: `results_gate_dose/round_v1/`
Stopped: 2026-10-06, on direct user instruction ("你现在做的是什么实验？请终止他，并开启我这一轮修复
Evidence 轴的实验").

## What was executed

**P0 only** — no training run was ever started. The gate (§2), the dose cells (§1 levels)
and the decision (§4) were never executed.

| stage | state |
| --- | --- |
| P0 masks / wiring / ρ / manifest | **complete** (`MASKS.json`, `TARGET_WIRING.json`, `RHO.csv`, `MANIFEST.sha256`, `P0_REPORT.md`) |
| P1 gate (8 training runs) | **not started** — `授权门控剂量` was never written |
| P2 dose cells (200 training runs) | **not started** |
| P3 tables / H1 / H2 / `DOSE_DECISION.json` | **not started** |

No `GATE.json` exists. No `tables/` exists. No `DOSE_DECISION.json` exists. No endpoint for
any dose cell was computed.

## What is kept, and why

The P0 artifacts are retained, not deleted, because they are a pre-registration record:
the mask permutation, the target-wiring assertions and the realized ρ were written and
hashed before any run, and they carry no result claim. Deleting them would destroy audit
trail without removing any claim.

Content hashes (timestamp-free, reproducible):
`masks 6b456bd378e92ead…`, `wiring b9de9d9b7d7e7823…`, `RHO.csv 302cd48c779e9a2a…`.

## Consequence of stopping here

The round has no result. The Evidence-axis question this round was aimed at (does a
pre-outcome structural statistic predict the sign and size of the Design cost?) is
**not answered**, and no `gate_law` label exists. Any future re-use of these masks must
re-enter through a fresh authorization, and the `P0_REPORT.md` §5 finding stands on its
own: the `raven` arm's frozen artifacts do not reproduce at m = 0 in the current working
tree (`|ΔRMSE_μ|` 4.2e-7 SensorScope / 3.8e-10 U-Air against a 1e-9 bound), while
`raven_wo_design` reproduces bit-exactly.

## Next round

The Evidence-axis work is opened as a separate round at `results_evidence_axis/round_v1/`:
`EVIDENCE_BASE.md` (the measured constraint map) and `DESIGN_BRIEF.md` (direction options,
awaiting the user's pick). No protocol has been written and no run has been made there
either.
