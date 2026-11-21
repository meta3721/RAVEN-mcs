# F-1 — does the constructed selection regime cap the gain? Experiment summary

```text
Date: 2026-09-24
Status: EXECUTED. Verdict: H-A is refuted.
Question: record §3 T8, hypothesis H-A — is the block-level, stratum-constant construction the
          reason no method separates on the reported endpoints?
Design: ccfa-review-reports/raven-mcs-f1-experiment-design.md
Record: ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md (§3 T8, §3 T9)
Scale: 160 new runs = 2 arms x {raven, raven_oracle_p} x {SensorScope, U-Air} x 20 paired seeds
Artifacts: artifacts/e3_f1_score_dependent_r1/ (arm N), artifacts/e3_f1_theta1_r1/ (arm S)
Readout: _tmp_ref/f1_readout.py
```

---

## 1. The question

The paper's headline is that RAVEN is *competitive* rather than *better*: no predictive endpoint
separates it from its own ablated variants by more than about 0.5%. Record §3 T8 asked whether that
flatness is an artifact of the testbed. In the published protocol blocks the observation propensity
is two-valued and constant within every opportunity stratum, so the correction problem the method
solves has four parameters per client-window and the frozen propensity model can represent all of
them. Hypothesis H-A said: the construction is too easy, and on a harder one the correction would be
worth more.

H-A is falsifiable. Give the observation propensity a genuinely within-stratum, label-correlated
component while holding the marginal fixed, and see whether an *exact* propensity becomes worth
anything. If it does not, the construction was not the constraint.

## 2. Why the test had to be redesigned before it could run

The test as first written asked for the E2 generator's score-dependent propensity to be ported into
E3. That port is vacuous, for a structural reason: **in E3 the opportunity stratum is nested inside
the target group** — `h(i) = s93::block0` while `s(i) = s93::block0::weekend` — and E3's
`tail_score` analogue *is* the block (`_stratum_is_tail(stratum, {2, 3})`). A block-indexed score is
therefore constant on every stratum, so a "score-dependent" `p_obs` built from it would reproduce the
existing construction under a new name. Verified numerically on the released traces: 0 of 800
SensorScope and 0 of 640 U-Air client-windows contain a risk set spanning two groups, and 0 of 312 /
0 of 232 strata span two groups.

The executed manipulation therefore moves the propensity **inside** the stratum, which is the only
axis where the frozen model is blind.

## 3. What was varied, and what was not

**Arm N** (`θ_O = 0`) reuses the published EventTraces, copied byte-for-byte.
**Arm S** (`θ_O = 1.0`) is a regenerated trace differing in exactly one line:

```text
published   p_i = clip(mean_observation_rate * scale, 0.05, 0.95),  scale = 0.55 on blocks {2,3}
arm S       p_i = clip(sigmoid(beta0(block) + theta_O * z_i), 0.05, 0.95)
```

`z_i ∈ {−1, 0, +1}` is the tercile of the unit's `time_index` inside its stratum, and
`beta0(block)` is solved by bisection so the mean of `p` over that block's training units equals the
published block rate. Frozen in both arms: seeds 30001–30020, splits, target maps, opportunity law,
risk-set size, stage-2 usable process, MC q, and the whole training configuration.

Two arms within the comparison matter:

- `raven` — the published method: estimated `p̂`, estimated `q̂`.
- `raven_oracle_p` — added for this experiment: identical to `raven` except that the atomic
  observation propensity is the true `p_obs_true_by_unit`, while `q` stays estimated.

The second arm is the one that makes the test decisive. `RAVEN-SimOracle` already existed but flips
**both** propensities through a single flag, so it cannot separate them; `raven_oracle_p` isolates
the observation member. The contrast `RMSE_μ(raven) − RMSE_μ(raven_oracle_p)` is measured on **the
same trace**, so it removes the model-capacity confound that a RAVEN-versus-baseline criterion
carries: it asks whether *any* propensity model could have helped, not whether this one did.

## 4. Gates

**Harness reproduction.** Arm N `raven` reproduces the published `raven` exactly:
`RMSE_μ` = 7.937989 vs 7.937989 (SensorScope) and 1.191114 vs 1.191114 (U-Air), **0.0000%** on both,
over all 20 seeds. The new execution path is the published path.

**Generator faithfulness.** At `θ_O = 0` the new generator reproduces the published trace
bit-for-bit: 800/800 and 640/640 event rows identical on `tau`, `U`, `model_age` and `oracle_q`, and
0 of 800 / 0 of 640 observed-unit sets differ. No extra random draws were introduced.

**Marginal preservation.** At `θ_O = 1.0` the pool-weighted mean of `p` equals the published block
rate on all eight block cells with `|Δ| ≤ 5.6e-17`. The manipulation changes the *shape* of the
propensity, not its level.

**Manipulation is real.** Distinct `p` per stratum rises from exactly 1 to a mean of 2.76
(SensorScope) and 2.83 (U-Air), maximum 3. Minimum `p` is 0.0671, above `p_min = 0.05` by 1.34×.

**No clip or sample collapse.** `clip_rate_stage1` does not rise (SensorScope 0.000421 → 0.000234;
U-Air 0.025958 → 0.022612) and `ESS` moves by ≤1.8%.

## 5. Result

`Δ_oracle = RMSE_μ(raven) − RMSE_μ(raven_oracle_p)`, paired by seed, same trace. Positive means the
plug-in model is losing to an exact one.

| dataset | arm | `Δ_oracle` | paired sd | MDE | σ |
|:---|---:|---:|---:|---:|---:|
| SensorScope | N (`raven` = the table method) | −0.005% | 0.0011 | 0.009% | 1.7 |
| SensorScope | S (`θ_O = 1.0`) | **+0.104%** | 0.0079 | 0.062% | **4.7** |
| U-Air | N (`raven` = forced Design, not the table method) | +0.017% | 0.0004 | 0.020% | 2.3 |
| U-Air | S (`θ_O = 1.0`) | **−0.251%** | 0.0065 | 0.342% | **2.1** |

On U-Air both arms run the forced-Design configuration rather than the deployed one (Table III's
U-Air method is `RAVEN-NoDesign` = 1.1131). The verdict is unaffected because the contrast is
within-trace and within-policy, but the U-Air number is not a property of the paper's U-Air method.

`Tail_RMSE` tracks `RMSE_μ` to two decimals in every row (SensorScope −0.005%, +0.100%; U-Air
+0.017%, −0.262%). `Δ_group` is not significant on either dataset (−0.150% at 1.7 σ, −0.095% at
1.6 σ).

**Pre-registered rule:** `|Δ_oracle| ≤ 0.5%` refutes H-A. Both datasets are inside that bound, the
larger at 0.251%, and on U-Air the sign is negative. **H-A is refuted.**

## 6. How to read that

The refutation is not a flat null, and the distinction matters.

- **The mechanism is confirmed in direction.** Between the two arms the value of an exact propensity
  rose **15–21×**, from 0.005% to 0.104% (SensorScope) and from 0.017% to 0.251% (U-Air). Making the
  selection law harder did exactly what H-A said it would.
- **The magnitude is refuted.** After that 15–21× amplification the figure still sits 2–5× below the
  paper's own 0.5% practical threshold, and on U-Air an exact propensity is *worse* than an estimated
  one by 0.25%. The constructed regime is not what keeps the gains flat.
- **What survives is H-B**: the endpoint is close to indifferent to the aggregation weights, which is
  also what the Stage A ceiling map shows from the other side (§8 below).

A useful side effect: the harder construction itself costs prediction. SensorScope `raven` moves from
7.9380 to 7.9809 (+0.54%) between the arms, so within-stratum propensity heterogeneity is a real
burden on this pipeline, just not one the correction can relieve.

## 7. What F-1 settled about record §3 T3

T3 previously read the joint oracle (`RAVEN-SimOracle`, exact `p` **and** `q`) as evidence about `q`
alone, which it cannot support. `raven_oracle_p` supplies the missing half:

| member | SensorScope `RMSE_μ` | U-Air `RMSE_μ` |
|:---|---:|---:|
| exact `p` only | −0.005% | +0.017% |
| exact `p` and `q` | +0.008% | −0.028% |
| `q`'s share (by difference) | ≈ +0.013% | ≈ −0.045% |

Neither member carries the null. T3's conclusion is unchanged and no longer has to be inferred.

## 8. The ceiling this experiment sits inside

Read from the frozen artifacts before any new run (record §3 T9): the `raven` cell against the E4
one-factor ablations, 20 paired seeds, `delta%` = (ablated − reference)/reference.

**Anchor caveat.** `raven` is the paper's table method on SensorScope, but on U-Air it is the row
Table III labels `RAVEN-Design (forced)` (1.1911); the U-Air table method is `RAVEN-NoDesign` =
1.1131 = `runs/uair/raven_wo_design` (`main.tex` 1754–1757, 1821–1822). The U-Air column below is
therefore a forced-Design factorial, and it is labelled as one.

| change | SensorScope `RMSE_μ` | U-Air `RMSE_μ` (forced) | σ (SS / UA) |
|:---|---:|---:|:---|
| remove design (ζ̂ + Gate) | +0.005% | −6.553% | 0.3 / 10.0 |
| remove observation IPW | +0.012% | −0.010% | 2.5 / 1.0 |
| remove usable IPW | +0.012% | +0.024% | 2.5 / 1.1 |
| remove Inst (P2 group term) | −0.090% | +2.086% | 1.6 / 6.4 |
| remove debt | +0.000% | +0.001% | 0.1 / 0.7 |
| exact `p` and `q` | −0.008% | +0.028% | 0.5 / 0.5 |

Against the `raven` cell, the best any reweighting can reach (`Central-Delivered`) is −0.112%
(SensorScope) / −1.100% (U-Air), and the undelivered-sample bound (`Central-All`) is −4.442% /
−12.841%. Re-anchored to the deployed U-Air method (1.1131), `Central-Delivered` (1.1782) is **5.85%
worse**, and `Central-All` is 5.17% better and unreachable.

On SensorScope every module is worth at most 0.09%. On U-Air the −6.553% design row looks like a
large available move and is not one: it is the branch assignment the paper's own φ rule already
makes, reported in Table III beside the forced row. The entire propensity family is ≤0.03% either
way. F-1's refutation is what this map predicted.

## 9. Not run, and the boundaries of the claim

- **E2** (change in RAVEN's lead over uncorrected baselines between arms) would need 120 further
  runs. Not run: E1 is decisive and the design's own stop rule applies. Its absence does not touch
  the verdict, which is an E1 statement.
- **The `θ_O` sweep** (0.5, 1.5; 80 runs) was not run, for the same reason. `θ_O = 1.0` matches the
  frozen E2 strength profile `PROFILE-S2`.
- **F-1-R** (opportunity-law day-type tilt) was not run. So the test bounds the *observation* member
  of H-A, not the design-ratio branch.
- F-1 is a simulation study on constructed selection. A positive result would have shown the
  published regime hides headroom; a negative one shows it does not. Neither is a claim about real
  sensing.
- It does not touch the target-provenance defect (record §1): `RMSE_μ` remains evaluation-derived in
  every arm.

## 10. Reproduce

```text
scripts/run_e3_f1.py --stage copy-traces --arm N          # published traces -> arm N root
scripts/run_e3_f1.py --stage run --arm N                  # 80 cells
scripts/run_e3_f1.py --stage gen-theta --arm S --theta 1.0  # 40 F-1-O traces
scripts/run_e3_f1.py --stage check-traces --arm S --theta 1.0  # refuses a theta mismatch
scripts/run_e3_f1.py --stage run --arm S --theta 1.0      # 80 cells
_tmp_ref/f1_readout.py                                    # gates, E1 on both arms, verdict
_tmp_ref/f1_generator_check.py                            # theta=0 bit-identity, marginals, dispersion
_tmp_ref/f1_stage_a_ceilings.py                           # section 8 reference bounds
_tmp_ref/f1_ablation_ceilings.py                          # section 8 module table
```

New code: `src/raven_mcs/e3/real_runner/generator_r3_score.py` (the `θ_O` generator), the
`raven_oracle_p` policy (`aggregation/method_policy.py`, `aggregation/methods.py`,
`training/window_runner.py`), and `scripts/run_e3_f1.py` (driver plus a trace guard that refuses to
run an arm whose traces are missing or carry the wrong `θ_O`, so a missing trace can never be
silently regenerated at `θ_O = 0`).

No file under `artifacts/e3_formal_runs_r1/` was written, and no manuscript file was touched.

## 11. What this means for the paper

The paper currently reports that RAVEN is competitive and does not state that the construction was
probed for hidden headroom. F-1 is the probe, and it came back empty in the strongest form the
testbed allows: an exact observation propensity, under a construction deliberately built to make it
matter, is worth 0.10% and −0.25%.

Two routes follow, and they are the user's call:

1. **Report F-1.** A new §VII subsection plus one table. It converts "we are competitive" into "we
   tested whether our own testbed was hiding an advantage, and it was not", which is a stronger and
   more defensible contribution than the current framing.
2. **Report the missing anchor.** The labelling defect this summary uncovered is itself worth
   fixing: the `raven` cell is the forced-Design row on U-Air, so any analysis that treats it as
   "the published method" is comparing against the wrong run. That is a documentation fix in the
   analysis layer, and it costs nothing.

What is *not* available is the route this work originally advertised. There is no unexploited 6.55%
on U-Air: the design branch is already removed there by the paper's own φ rule. What remains open is
the question underneath φ itself — the record's D-1 decided to withdraw φ from the Design-switch
role and that decision is still unimplemented in the manuscript (`main.tex` Algorithm 1 line 1042,
§V-E, and the frozen-φ appendix table all still gate on it).
