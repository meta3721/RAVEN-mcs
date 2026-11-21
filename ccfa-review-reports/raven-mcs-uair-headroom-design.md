# U-Air headroom experiment — design (not executed)

```text
Mode: design. No runs were started; no result exists in this file.
Venue / assumptions: the design serves IEEE TMC evidence for RAVEN-MCS; the run outputs feed
        ccfa-review-reports/raven-mcs-experiment-report-20260924.md, not any manuscript table.
Contract: CCFA-Skills/ccf-experiment-designer, default full-design structure.
Question: the H headroom experiment returned STOP on 5 seeds. Its SensorScope half is conclusive;
        its U-Air half is not, and U-Air is where the only stable effect lives.
Inputs: results_h_headroom/round_v1/** (180 runs, H_summary.csv, H_DECISION.json, GATE_*.json);
        ccfa-review-reports/raven-mcs-h-headroom-preregistration.md;
        artifacts/e3_formal_runs_r1/**, artifacts/e4_core_mechanism_ablation_r1/**;
        results_table2_audit/**; scripts/run_h_headroom.py
```

---

## 1. Why an extension is needed at all

The pre-registered verdict is `STOP` (`H_DECISION.json`, `go_cells = []`, bar 0.005). The stopping
rule is sound, but its two datasets have very different resolving power, and the report's §5
conclusion ("±0.03% is the space ceiling") does not carry equally on both.

Paired-difference sd implied by the published 5-seed 95 % CIs, and the resulting minimum detectable
effect at 80 % power:

| condition | U-Air sd (derived) | SensorScope sd (derived) | U-Air MDE at n=5 | SensorScope MDE at n=5 |
|:---|---:|---:|---:|---:|
| C0 frozen | 1.13 pp | 0.103 pp | 1.88 pp | 0.17 pp |
| C1 strong tilt | 0.83 pp | 0.103 pp | 1.38 pp | 0.17 pp |
| C2 extreme tilt | 1.11 pp | 0.207 pp | 1.85 pp | 0.34 pp |
| C3 low capacity | 1.15 pp | 0.103 pp | 1.91 pp | 0.17 pp |
| C4 block-uniform | 1.13 pp | 0.113 pp | 1.88 pp | 0.19 pp |
| C5 combined | 1.11 pp | 0.218 pp | 1.84 pp | 0.36 pp |

`sd` is `(CI half-width)/t_{0.975,4} × sqrt(5)`; MDE is `(t_{0.975,4}+t_{0.8,4}) × sd/sqrt(5)`.
Both are arithmetic on published values, not new measurements.

Readings:

- **SensorScope's null is already conclusive.** MDE ≤ 0.36 pp and all six point estimates inside
  [−0.03 %, +0.08 %]. Extending SensorScope would buy nothing.
- **U-Air's null is not.** MDE 1.4–1.9 pp cannot exclude a 1 % effect, and U-Air carries the only
  effect whose CI excludes zero (`design_support_cost` +6.0 % to +8.8 %). The STOP on U-Air rests on
  the rule firing nowhere, not on demonstrated absence of headroom.
- The report's §5 sentence should therefore be restricted to SensorScope until this experiment runs.

## 2. Claim-evidence matrix

| claim under test | current evidence | status | this experiment |
|:---|:---|:---|:---|
| the correction family cannot move `RMSE_μ` by 0.5 % on U-Air | 6 conditions, n=5, MDE 1.4–1.9 pp | **not established** | U1 supplies it |
| Design's U-Air cost is a support loss, not estimator failure | one stable effect, +7.03 % [2.68, 11.38] on oracle arms | established but loosely bounded | U1 tightens to ≈±1.6 pp |
| the Design effect is endpoint-keyed (helps `Δ_c-s`, hurts `Δ_group`) | U-Air `Δ_c-s` −4.990 % (17.1 σ) vs `Δ_group` +6.943 % (12.7 σ), n=20, existing trees | **already established** | **no new runs** |
| after equalising the delivered set, U-Air `Δ_group` favours NoDesign | NoDesign 1.0165 vs current FedAvg 1.0446 / FedAU 1.0557 / ObsUse 1.0413, n=20 | **already established** | **no new runs** |
| U-Air FedAvg cell of the main comparison | `GATE_uair.json`: frozen 1.210848 vs rerun 1.171263, `known_nonrepro` | resolved as a defect | **no new runs** |

Two of the five open U-Air questions need zero new runs. The design deliberately spends nothing on
them.

## 3. Dataset and benchmark needs

- U-Air only. SensorScope is excluded on the MDE evidence in §1, and its exclusion must be stated as
  a power argument, not as a convenience.
- Protocol block, frozen windows and `s_max` as in the published E3 configuration.
- Seeds **30006–30020** are new. Seeds 30001–30005 are reused from `results_h_headroom/round_v1/`
  without re-running; re-running them would silently replace the pre-registered sample.
- C0, C3, C4 reuse the frozen E3 EventTraces (present for all 20 seeds).
- C1, C2, C5 require 45 regenerated traces (3 conditions × 15 seeds), same R3 generator, same
  seeds and windows, via the driver's existing materialization path.

## 4. Confirmed method and baseline versions

| arm | identity | why it is the right arm |
|:---|:---|:---|
| `fedavg_window` | the delivered samples, no correction — the denominator of `H` | matches the pre-registered definition; reproduces the frozen value bitwise on SensorScope (`GATE_sensorscope.json`, `abs_diff = 0.0`) |
| `raven_simoracle_nodesign` | true `p`, true `q`, `ζ ≡ 1` | won the better-arm comparison in **all six** U-Air cells |
| `raven_simoracle` | true `p`, true `q`, Design on | retained so the support cost stays measurable |

All three are already registered inside the driver; no `src/` change.

## 5. Baseline matrix

`H` needs a denominator and two oracle arms, nothing else. No external baseline participates: the
question is what the correction family can reach, not how RAVEN ranks.

| role | arm | reported quantity |
|:---|:---|:---|
| no-correction reference | `fedavg_window` | denominator |
| primary oracle | `raven_simoracle_nodesign` | `H_nodesign` |
| secondary oracle | `raven_simoracle` | `H_design`, and `design_support_cost = (design − nodesign)/nodesign` |

## 6. Main experiments

**Stage U1 — uniform 20-seed extension.**

| item | value |
|:---|:---|
| conditions | all six, unchanged (C0, C1, C2, C3, C4, C5) |
| arms | three, unchanged |
| seeds | 30006–30020 added to the reused 30001–30005 |
| new runs | 6 conditions × 3 arms × 15 seeds = **270** |
| new traces | 45 (C1, C2, C5 × 15 seeds) |
| decision statistic | `H_nodesign` on the 20-seed sample |
| decision rule | unchanged: **GO** iff some `c ∈ {C1…C5}` has `H ≥ 0.5 %` **and** CI lower bound `> 0`; otherwise **STOP** |

Extending all six conditions rather than only the informative ones is deliberate: C3 and C5 have a
dead capacity knob (already reported), but extending a subset after seeing the 5-seed results would
create a condition-selection degree of freedom. Uniform extension costs roughly one extra hour and
removes the objection.

**One pre-registered change to the estimator.** Revision 1 chose the oracle arm per cell by the
5-seed mean. Re-choosing it on 20 seeds would be post-hoc. Revision 2 therefore **freezes the U-Air
oracle arm to `raven_simoracle_nodesign`** for the reused and the new seeds alike. This changes no
existing number: the better-arm value and the NoDesign value are identical in all six U-Air cells
because `best_oracle = raven_simoracle_nodesign` everywhere. It removes a selection degree of
freedom at zero cost.

**Projected resolving power at n=20** (se = sd/4.4721, MDE = 2.9540 × se):

| condition | sd | se at n=20 | MDE at n=20 | GO threshold met if H exceeds |
|:---|---:|---:|---:|---:|
| C0 | 1.13 pp | 0.253 pp | 0.75 pp | 0.53 pp |
| C1 | 0.83 pp | 0.186 pp | 0.55 pp | 0.39 pp |
| C2 | 1.11 pp | 0.249 pp | 0.74 pp | 0.52 pp |
| C3 | 1.15 pp | 0.257 pp | 0.76 pp | 0.54 pp |
| C4 | 1.13 pp | 0.253 pp | 0.75 pp | 0.53 pp |
| C5 | 1.11 pp | 0.248 pp | 0.73 pp | 0.52 pp |

At n=20 the GO rule becomes **operative** on U-Air (it can fire at H ≈ 0.5 %), which it was not at
n=5. It still cannot certify a null below ≈0.75 pp for the worst conditions.

## 7. Ablations

None. `H` is a ceiling measurement over the existing arm set; the condition grid already is the
ablation of the generative knobs. Adding arms would change what `H` means.

## 8. Robustness, failure, escalation

**Pre-registered escalation rule (stage U2).** After U1, extend a condition to n=45 **only if** its
20-seed `H` lands in the ambiguous band **[0.30 %, 0.75 %]** — the interval in which more power can
still flip the verdict. A condition whose U1 `H < 0.30 %` or `> 0.75 %` gains nothing from U2.

| U1 outcome | action |
|:---|:---|
| any cell GO | stop; report GO; Phase 2 (method comparison) becomes schedulable |
| all cells in [0.30 %, 0.75 %] | run U2 on those cells only |
| all cells < 0.30 % | stop; the U-Air null is then conclusive at the 0.5 % bar and the report's §5 ceiling claim becomes valid on both datasets |

Cost of U2 if triggered for all six conditions: 6 × 3 × 25 new seeds = 450 runs, plus traces at
seeds 30021–30045.

**Failure modes to pre-empt.**

| failure | detection | handling |
|:---|:---|:---|
| a new seed's trace generation differs from C0/C3/C4 reuse | events equal ignoring the three metadata keys, as in revision 1 | abort that seed; do not substitute |
| the frozen FedAvg arm is used by mistake at the new seeds | the gate already flags `known_nonrepro` | C0's FedAvg values at 30001–30005 are the **rerun** values from `GATE_uair.json`, so all 20 seeds come from one runner vintage; re-run any seed whose ledger lacks the rerun marker |
| arms produce non-finite RMSE | finite-metric check on every run | drop the seed and report the drop count |
| reuse of seeds 30001–30005 silently replaced | compare the U1 input rows against `results_h_headroom/round_v1/tables/H_seed_rows.csv` | refuse to write the U1 table unless they match exactly |

## 9. Smoke scope and deduplication

- **Smoke**: one condition (C0), one seed (30020, not previously run), all three arms, finite-value
  assertion only. That is the single unique changed path — a wider seed list. No new smoke battery.
- **Do not re-run**: seeds 30001–30005; the endpoint split; the Table 2 FedAvg audit; any SensorScope
  cell; the gate cells.
- **Do not write** into `artifacts/e3_formal_runs_r1/`, `results_h_headroom/round_v1/runs/`, or any
  other frozen directory. U1 output goes to `results_h_headroom/round_u1/`.

## 10. Result tables

**Table U1-a — U-Air headroom at 20 seeds** (replaces the U-Air rows of `H_summary.csv`; the
SensorScope rows are carried over unchanged at n=5 with the power note).

| condition | `H_nodesign` [95 % CI] | `H_design` [95 % CI] | support cost [95 % CI] | MDE | GO |
|:---|---:|---:|---:|---:|:---|
| C0 | TBD | TBD | TBD | 0.75 pp | n/a (C0 excluded) |
| C1…C5 | TBD | TBD | TBD | 0.55–0.76 pp | TBD |

**Table U1-b — sample composition and provenance** (gate, not evidence).

| item | value |
|:---|:---|
| seeds reused / added | 30001–30005 / 30006–30020 |
| new runs / new traces | 270 / 45 |
| gate status per reused seed | reproduce `H_seed_rows.csv` exactly |
| runner vintage of the FedAvg arm | single vintage, verified by the rerun marker |
| dropped seeds | TBD, with reason |

## 11. Missing values

`TBD` marks every cell that this design would produce. Nothing in §1, §6 or §8 is a measurement: the
sds are derived arithmetically from published CIs, the MDEs and GO thresholds are arithmetic on those
sds, and the unit cost below is derived from the published E3 per-arm timings. No U-Air extension
result is claimed to exist.

## 12. Execution priority

1. **Write preregistration revision 2** (arm freeze to `raven_simoracle_nodesign`; seed extension;
   unchanged GO bar, conditions, θ, scalings, μ′; U2 escalation rule) **before any run.**
2. Smoke: C0 / seed 30020 / three arms, finite values.
3. Generate the 45 traces for C1, C2, C5 at seeds 30006–30020.
4. Run U1: 270 runs. Estimated cost **≈1.6 h**: 0.75 min per (condition, seed) for three U-Air arms
   (published per-arm costs 0.200 min for FedAvg, ≈0.275 min for each oracle arm) and ≈40 s per
   trace, against the measured H round of 180 runs in ≈80 min of wall time.
5. Rebuild the U-Air table, re-apply the unchanged GO rule, and write `U1_DECISION.json` next to —
   never over — `H_DECISION.json`.
6. Only then decide U2 from the band rule in §8.

## 13. No-fabrication status

No run was executed and no number produced by this design is reported as a result. Every figure
quoted is either read from a named artifact (`GATE_*.json`, `H_summary.csv`, `H_DECISION.json`,
`uair_paired_vs_fedavg.csv`, the E3 runtime manifests) or is arithmetic on those readings, and each
is labelled as derived. The design changes no frozen directory, no `src/` file, and no manuscript
text.

## 14. Next CCFA owner

`ccf-experiment-designer` holds this design until revision 2 is written; execution is a plain
driver invocation (`scripts/run_h_headroom.py --stage runs --dataset uair --seeds 30006,…,30020`)
plus the trace stage. If U1 returns GO, the pre-registered Phase 2 comparison becomes schedulable and
`ccf-paper-writer` takes the write-up either way.

---

## 15. Outcome — U1 executed 2026-09-25

```text
Executed: 270 new runs + 45 new traces in results_h_headroom/round_u1/; seeds 30001-30005 reused
          from round_v1 unchanged. Wall time ≈1.7 h. Verdict: STOP, go_cells = [].
Gate:     re-run at the NEW seed 30006 — raven_simoracle abs_diff = 0.00e+00, trace events equal
          ignoring the three metadata keys, fedavg_window flagged known_nonrepro as expected.
Integrity: reused rows bit-identical to round_v1 on all three metrics (|diff| = 0.000e+00);
          H == H_nodesign in every U-Air cell, so the revision-2 arm freeze is inert as predicted;
          0 non-finite runs; SensorScope carries at n=5.
```

**The pre-registered rule fired nowhere, and the one cell that looked close was noise.**

| condition | `H_nodesign` at 20 seeds [95 % CI] | at 5 seeds | shift | sd | MDE | GO threshold | GO |
|:---|---:|---:|---:|---:|---:|---:|:---|
| C0 | **−0.2166 %** [−0.7154, +0.2822] | +0.22 % | −0.44 pp | 1.07 pp | 0.70 pp | 0.50 % | no |
| C1 | **−0.0044 %** [−0.5378, +0.5291] | **+0.77 %** | **−0.78 pp** | 1.14 pp | 0.75 pp | 0.53 % | no |
| C2 | **+0.0371 %** [−0.5281, +0.6023] | −0.07 % | +0.11 pp | 1.21 pp | 0.80 pp | 0.57 % | no |
| C3 | **−0.2107 %** [−0.7094, +0.2881] | +0.24 % | −0.45 pp | 1.07 pp | 0.70 pp | 0.50 % | no |
| C4 | **−0.2161 %** [−0.7155, +0.2833] | +0.22 % | −0.44 pp | 1.07 pp | 0.70 pp | 0.50 % | no |
| C5 | **+0.0283 %** [−0.5360, +0.5926] | −0.09 % | +0.12 pp | 1.21 pp | 0.80 pp | 0.56 % | no |

**Support cost at 20 seeds** (oracle arms, `(design − nodesign)/nodesign`): **+6.317 % to +6.991 %**,
every 95 % CI lower bound between **+4.751 %** and **+5.834 %**, i.e. all six exclude zero.

**Goal status, against §1 and §8.**

- **Achieved.** The U-Air half of the ceiling claim is now supported by a pre-registered rule at
  20 seeds rather than by a rule that could not fire: all six point estimates have |H| ≤ 0.2166 %,
  and the rule's threshold (0.50–0.57 %) was reachable and was not reached. §8's third row applied,
  so **U2 is not run** — every point estimate sits below the 0.30 % band floor.
- **Achieved, with a stronger number than the 5-seed round had.** The support cost tightened from
  +5.98…+8.76 % with wide CIs to **+6.32…+6.99 %** with all lower bounds above +4.75 %, and it is
  invariant to the tilt strength, the backbone and the target law (C0 ≈ C3 ≈ C4 ≈ +6.98 %;
  C2 ≈ C5 ≈ +6.31 %). It is now the only well-powered effect in the U-Air evidence base.
- **The headline is a collapse, not a confirmation.** C1 — the cell the report flagged as "closest
  to GO" — moved from +0.77 % to **−0.0044 %**. The apparent near-breach was small-sample noise.
- **Caveat to carry.** The realized sd (1.07–1.21 pp) landed at the top of the projected range, so
  the realized MDE is **0.70–0.80 pp**, slightly worse than the projected 0.55–0.76 pp. The correct
  statement is: 80 % power excludes true effects ≥ ≈0.75 pp; C2 and C5 have 95 % upper bounds at
  +0.60 %, so those two cells do not yet exclude a true effect of about 0.5 % at 95 %. The ceiling
  sentence in the source report should be scoped accordingly rather than stated as ±0.03 %.

**Artifacts.** `results_h_headroom/round_u1/` (`U1_DECISION.json`, `tables/H_summary.csv`,
`tables/H_seed_rows.csv` with a `source` column, `EXECUTION_LOG.md`, `runs/`, `eventtraces/`).
Regression evidence for the driver patch: `results_h_headroom/round_v1_verify/`, which reproduces
`round_v1/tables/H_summary.csv` to **0.000e+00** across all 40 numeric columns and 12 rows using the
reuse path and zero runs. `round_v1` and `artifacts/e3_formal_runs_r1/` were not written.
