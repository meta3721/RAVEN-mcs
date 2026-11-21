# EXECUTION REPORT — response-shift headroom (scheme 2), Stage A + Stage B

```text
Round     : results_h_response_shift/round_v1
Prereg    : PREREG.md sha256 5efb5abd185d1807a028ce046c2923548dcf44eb96270aeb0988a52793dfd92b
            (9323 bytes), recorded in MANIFEST.sha256 before any number was computed
Authority : the user wrote "授权 H 测量" on 2026-10-05; Stage B then ran under §4
Driver    : scripts/h_response_shift.py (new; imports run_h_headroom's frozen runner and run_arm pattern)
Cost      : 80 training runs, 5 seeds x 2 datasets x 2 arms x 4 c values. No trace regeneration.
DECISION  : STOP — no c > 0 cell reaches GO; the c = 0 stop rule did not fire either
Writes    : results_h_response_shift/round_v1/ only
Untouched : src/, the manuscript, results_h_headroom/, every other results_* directory, artifacts/
Note      : the Stage-A-only report written before Stage B was run is kept as
            STAGE_A_REPORT_superseded.md. This file supersedes it.
```

## 1. Stage A — the mass gap (recap)

`μ` is the frozen deployment-group target (220 / 144 groups); `π_arr(g)` is the share of training
atomic units in group `g` among the units that appear in the trace.

| dataset | median ‖π_arr − μ‖₁ | median (risk-set variant) | median μ-mass on absent groups | bar | `stage_B` |
|---|---|---|---|---|---|
| SensorScope | **0.56750** | 0.43146 | 0.19707 | 0.02 | allowed |
| U-Air | **0.60147** | 0.43926 | 0.16352 | 0.02 | allowed |

Both clear the 0.02 bar by 25–30×, so Stage A forbade nothing. Per-trace rows and the two L1
definitions are in `MASS_GAP.csv`; amendments A-H1 (arrival vs risk set) and A-H2 (which μ
normalisation the bar tests) are declared in `PREREG.md`.

## 2. §4.1 driver check — PASS

`c = 0`, **production full model**, both datasets, seed 30001, both arms, against
`results_h_headroom/round_v1/gate/C0_frozen/`. Tolerance 1e-6.

| dataset | method | rerun | reference | `|Δ|` |
|---|---|---|---|---|
| sensorscope | fedavg_window | 7.914361980993586 | 7.914361980993586 | **0.0** |
| sensorscope | raven_simoracle | 7.903624828633094 | 7.903624828633094 | **0.0** |
| uair | fedavg_window | 1.1712625825964957 | 1.1712625825964957 | **0.0** |
| uair | raven_simoracle | 1.1968560479817063 | 1.1968560479817063 | **0.0** |

`DRIVER_CHECK.json: pass = true`. All four reproduce to the last bit, six orders inside the bar.

## 3. Stage B — the grid (80 runs, `H_SEED_ROWS.csv`)

`feature_blind` backbone (`DiurnalBlindNDMF` with a hard-zeroed spatial index), frozen C0 traces
(`θ = 1.25`, tail scale `0.55`), seeds 30001–30005, arms `fedavg_window` and `raven_simoracle`,
`c ∈ {0, 0.5, 1, 2}`, `δ(unit) = c·s(g(unit)) − δ̄` with `δ̄` the train-split mean, exactly as §2
declares. `c = 0` gives `δ = 0` exactly.

| ds | c | n | H | 95% CI | fedavg `RMSE_μ` | oracle `RMSE_μ` | GO |
|---|---|---|---|---|---|---|---|
| sensorscope | 0.0 | 5 | −0.000049 | [−0.001984, +0.001886] | 7.896610 | 7.897054 | never |
| sensorscope | 0.5 | 5 | +0.001358 | [−0.001581, +0.004296] | 7.935854 | 7.925119 | no |
| sensorscope | 1.0 | 5 | +0.002255 | [−0.003069, +0.007578] | 8.003967 | 7.986006 | no |
| sensorscope | 2.0 | 5 | +0.003521 | [−0.006648, +0.013690] | 8.221848 | 8.193157 | no |
| uair | 0.0 | 5 | **−0.074590** | [−0.130458, −0.018721] | 1.100723 | 1.180424 | never |
| uair | 0.5 | 5 | **−0.144537** | [−0.200928, −0.088146] | 1.198751 | 1.368582 | no |
| uair | 1.0 | 5 | **−0.158764** | [−0.199390, −0.118138] | 1.472982 | 1.704372 | no |
| uair | 2.0 | 5 | **−0.133546** | [−0.167982, −0.099109] | 2.272732 | 2.576230 | no |

**No `c > 0` cell is GO**: every SensorScope CI contains 0 and every U-Air CI lies entirely **below** 0.
The `c = 0` stop rule did not fire (`c0_stop_triggered = false`). Hence
**`H_DECISION.json: decision = STOP`, `winning_cells = []`**, and per §4.3 STOP ends the scheme: this
report does not propose training `proj_beta` or uniform weights, and a later comparison would need a
new protocol and the phrase `授权偏移对比`.

## 4. What the result actually says — the sign was diagnosed before it was read

A negative `H` means the **oracle did worse than the count-weighted baseline**, which is not the
direction a headroom measurement is supposed to have. Before reading anything into it, the reference
grid was checked at the same five seeds
(`results_h_headroom/round_v1/runs/C0_frozen`, production full model):

| dataset | H at `c = 0`, production full model, 5 seeds | interpretation |
|---|---|---|
| sensorscope | **+0.000211** (sd 0.000862) | no headroom — matches the H round's own non-GO |
| uair | **−0.068074** (sd 0.041919) | the oracle **already loses** to `fedavg_window` in the H round's own C0 runs |

So the negative sign is **pre-existing in this harness**, not created by the shift: on U-Air the
`raven_simoracle` arm has been 2–12 % worse than `fedavg_window` since the headroom round, whose own
`H_DECISION.json` records `decision: STOP`, `go_bar: 0.005`, `go_cells: []`. That is the context the
grid must be read in, and it cuts both ways:

* **The rule is applied as written.** §4.3 asks whether `H ≥ 0.01` with a CI lower bound above 0.
  Nothing reaches that, so STOP is forced with no judgement call.
* **On U-Air the grid cannot answer the §0 question.** §0 asks whether oracle reweighting moves
  `RMSE_μ` at all on a shift the model cannot represent. With the oracle already behind the baseline
  at `c = 0` and still behind at every `c > 0`, the grid shows that *this oracle configuration*, not
  *oracle reweighting in general*, fails to gain on U-Air. A test of the §0 question on U-Air would
  need an oracle that is at least non-inferior at `c = 0` — which this one is not, and which this
  round is not authorised to construct.

## 5. What the shift itself did, stated separately from the decision

* **The shift moves both arms, monotonically.** SensorScope: `fedavg_window` 7.8966 → 8.2218
  (+4.1 %) and the oracle 7.8971 → 8.1932 as `c` goes 0 → 2. U-Air: 1.1007 → 2.2727 (**+106 %**) and
  1.1804 → 2.5762 (**+118 %**). The perturbation is real and grows with `c`; it is not a no-op.
* **The shift does not create headroom.** The two arms stay the same distance apart or drift further
  in the baseline's favour (U-Air `H`: −0.075 → −0.145 → −0.159 → −0.134). More shift is not more
  opportunity.
* **The `feature_blind` backbone behaves like the full model at `c = 0`**: SensorScope
  `H = −0.000049` against the full model's `+0.000211`; U-Air `H = −0.074590` against `−0.068074`.
  Removing the spatial embedding row and zeroing the hour features does not change the picture, which
  is consistent with §0's premise that a deployment-group offset is not representable as a function of
  these inputs — and it is *not* evidence that the shift is absorbed.
* **Caveat carried forward:** the `−0.068` at `c = 0` on U-Air is a property of the frozen C0 runs, so
  any future round that wants to ask the §0 question on U-Air must first fix or replace that arm, and
  must say so before running.

## 6. Deviations and amendments

```text
A-H1  "among units that appear in the trace" = the union of observed_unit_ids (arrival), with the
      risk-set union reported as a companion column. The two differ materially (0.5675 vs 0.4315
      median on SensorScope) and both are in MASS_GAP.csv.
A-H2  The 0.02 bar is applied to the L1 computed on the groups present in the trace, both sides
      renormalized. The zero-extended variant including mass on absent groups is reported as
      l1_all_groups and is not what the bar tests. Both definitions were fixed before the numbers.
A-H3  μ is seed-independent, read once per dataset.
A-H4  Stage B was run only after the user wrote the required phrase and only after §4.1 passed. The
      decision field uses STOP (a measurement), not BLOCKED (an authorisation state).

Declared for the record, not changed by this round: target_group is a composite label
(s103::block2), so the label -> index map is taken from the dataset's own inventory and asserted equal
to n_groups_runtime (220 / 144) before use. The δ sign rule s(g) uses that same sorted inventory, so
it is deterministic and reproducible from PREREG.md.
```

## 7. Files

```text
PREREG.md                     the frozen rule set + amendments A-H1…A-H4, hashed first
MANIFEST.sha256               PREREG.md digest
MASS_GAP.csv                  Stage A: 10 rows, both L1 variants, per trace
STAGE_A_DETAIL.json           group inventory, unit counts, per-dataset medians
DRIVER_CHECK.csv / .json      §4.1: four runs, |Δ| = 0.0
H_SEED_ROWS.csv               80 rows: the grid, one row per run
H_SUMMARY.csv                 8 rows: H, CI, arms' means, GO flag
H_DECISION.json               stage_A verdicts, stage_B_ran = true, decision = STOP, no winners
EXECUTION_REPORT.md           this file
STAGE_A_REPORT_superseded.md  the Stage-A-only report written before Stage B was authorised
runs/                         the 80 run directories: c<c>/<dataset>/<arm>/seed<seed>
driver_check/                 the four §4.1 runs
```
