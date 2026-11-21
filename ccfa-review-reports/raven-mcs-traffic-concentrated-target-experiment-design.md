# NSW-Traffic concentrated-target structural test (experiment design)

`ccf-experiment-designer`, mode `design`. Planning artifact only: it asserts no result and contains no
measured effect. Numbers quoted are either analytic or taken from existing frozen artifacts, and each is
labelled.

## Mode

`design`. Route A of the block screen: keep the one block that has feasible-set slack and make the
deployment target concentrate at the aggregation level, using frozen artifacts only.

## Venue and assumptions

IEEE TMC, method plus measurement. The design targets the one question the two reviews said no wording
can settle: whether concentrating the deployment target gives the corrected reference room to move a
**deployment-weighted error**, rather than only the mismatch statistics. Nothing here is a manuscript
change and no result from it may be written into the paper without a separate authorial decision.

## Claim-evidence matrix

| claim under test | evidence this design supplies | why the existing evidence does not |
|---|---|---|
| The projection onto `eq:Cr` changes the deployment-weighted prediction error when the target concentrates | paired per-seed contrast of `RMSE_mu` under the concentrated target weights, control versus treatment, over a pre-registered concentration grid | under the uniform targets of every existing block, `RMSE_mu` is an unweighted mean error that no weighting can move; the observed effect lives only in `Delta_group` and `Delta_c-s` |
| The mechanism is the concentration of the target, not the arm | the same contrast across a pre-registered ladder of target concentration, one variable changed | the existing rounds vary the server step, the aggregation rule, or the target *statistic*, never the target *distribution* |
| There is a concentration below which the effect disappears | reported as a measured boundary of the effect, not as a defensive case | absent |

## Dataset / benchmark needs

NSW-Traffic, scenario `complete_aligned`, the frozen protocol: `172` deployment groups (`43` stations x
`4` UTC blocks), `local_steps = 2`, one server update per window, the frozen server step. The frozen
artifact list already holds what the design needs:

- the frozen `43 -> 4` region mapping (`build_label_free_regions`, E2 public-target identity), with
  station counts `{region0: 10, region1: 11, region2: 11, region3: 11}` — **near-equal, so a
  station-count priority rule cannot create concentration and must not be used**;
- the frozen target artifact (`freeze_fixture_target(atomic)`), which the re-weighting extends;
- feasible-set slack, measured on the frozen runs: `88.9 %` of active windows have `K_r > 3`, median
  `K_r = 12`, max `26`. This is the property no other block has: SensorScope `24.7 %`, U-Air `19.7 %`.

**The lever, stated precisely.** `eq:Cr` bounds `||alpha||_2^2 <= 1/Ebar_r` with
`Ebar_r = min(E_min, K_r) = 3` whenever `K_r > 3`, so at most about three clients can carry the
aggregation in any such window. The design therefore tests whether those roughly three effective clients
can be placed on the priority region. That is a real mechanism, and it is the one the uniform-target
blocks leave untested.

## Confirmed method / baseline versions

All arms are the repository's E3 real-runner methods, run at the frozen configuration. From
`runner.py` L498-L502, the set that invokes the P2 calibration and projection is
`{inst_cal, debt_cal, raven, raven_simoracle, raven_wo_*}`; `local_hajek` and `fedavg_window` are not in
it and aggregate without P2. Arm semantics are fixed by that list, not by this document.

## Baseline matrix

| Baseline | Why included | Implementation source | Fairness constraints | Expected metric | Can run? |
|---|---|---|---|---|---|
| `local_hajek` (control) | the no-P2 aggregation: uniform reference without the projection | E3 runner, 20 frozen seeds exist under the uniform target | same target artifact, same seeds, same scenario, same server step | `RMSE_mu` under the concentrated target | yes |
| `inst_cal` (treatment) | P2 invoked: corrected reference calibrated inside the feasible set | same | identical to the control except the aggregation weights | same | yes |
| `debt_cal` (treatment, second form) | P2 invoked with the debt recursion active | same | same | same | yes |
| `raven_simoracle` (oracle upper bound) | the true-margin member: how much any weighting inside the class could buy | same, 20 frozen seeds exist | same | same | yes |
| `central_delivered` | out-of-family reference; also the bookkeeping for the earlier N3' work | same | same | same | yes |
| `fedavg_window` | second control, the window-FedAvg aggregation used in the recent rounds | E3 runner; also produced by the recent round for seeds 30006-30020 | same | same | yes |
| `raven_wo_design`, `raven_wo_inst`, `raven_wo_debt` | component attribution if the treatment separates | E3 runner | same | same | yes, priority 3 |

No literature baseline is introduced: the two reviews established that the arms are this repository's
re-implementations sharing one server step, and no external baseline is claimed.

## Main experiments

**One treatment variable: the deployment target distribution.** The target artifact is replaced by a
version in which one pre-declared priority region carries `kappa` times the per-region weight of the
other three, renormalized to unit mass. `kappa` is a pre-registered ladder, not a sweep to be selected
from:

| `kappa` | top-1 region share | top-2 share | effective groups |
|---|---:|---:|---:|
| 1 (frozen target) | 25.0 % | 50.0 % | 4.0 |
| 2 | 40.0 % | 60.0 % | 3.2 |
| 5 | 62.5 % | 75.0 % | 2.5 |
| 10 | 76.9 % | 84.6 % | 2.1 |

(analytic from the four-group structure; the realised masses must be recomputed and frozen before any
run, exactly as the earlier round froze its validation constant.)

**Primary cell.** `kappa = 5`, priority region declared before any run by a rule that cannot see the
outcome: the region holding the largest share of the **frozen, pre-outcome target mass** under
`kappa = 1`. The rule, the resulting region id, the four-region mass table and the target-artifact hash
are frozen in `TE2_FROZEN_PREREG.json` before the first run.

**Primary endpoint.** `RMSE_mu` computed with the concentrated target's `mu` weights — that is the
deployment-weighted prediction error. Secondary: `WorstGroupRMSE` under the same weights, `Tail_RMSE`,
and `Delta_group` / `Delta_c-s` for continuity with the existing tables.

**Contrast and analysis.** Per seed `s` and per `kappa`, with the two arms paired on the seed and on the
frozen event traces:

```text
D_s(kappa) = RMSE_mu(local_hajek, s, kappa) - RMSE_mu(inst_cal, s, kappa)
```

Report the mean, the sample sd (`n-1`), a percentile bootstrap interval (10 000 draws, a fixed rng), and
`MDE80 = (t_{0.975,n-1} + t_{0.80,n-1}) * sd / sqrt(n)`. The oracle gap
`(local_hajek - raven_simoracle)` is reported beside it as the ceiling of what any weighting inside the
class could buy at that concentration, because a treatment effect means nothing without it.

**Decision rule, pre-registered.** The structural-concentration claim is supported only if, at the
primary cell, the bootstrap interval for `D_s` lies entirely on the favourable side of zero **and** the
mean exceeds its own `MDE80`, **and** the effect is at least `2 %` of the control's deployment-weighted
error. Every other cell of the ladder is reported as measured, including cells where the effect vanishes,
and no cell may be promoted after seeing the numbers.

## Ablations

| Component or assumption | Why it matters | Removal or replacement | Metric affected | Interpretation if it fails |
|---|---|---|---|---|
| the concentration itself | this is the treatment, so the ladder is the mechanism test | `kappa` from 1 to 10, and a single-region limit as exploratory | `RMSE_mu` under the concentrated weights | if the effect does not grow with `kappa`, the projection's reach is not the target distribution but the feasible set or the learner |
| the projection (P2) | separates "the reference is corrected" from "the weights are re-optimised" | `local_hajek` versus `inst_cal` at fixed `kappa` | same | if the projection changes nothing at any `kappa`, the whole structural route is bounded |
| the debt recursion | the paper's own contribution 4 refuses to attribute a gain to debt | `debt_cal` versus `inst_cal`, and `raven_wo_debt` | same | any gain attributable to debt must be reported as such, not to the projection |

## Robustness / failure / efficiency

- **Priority-region sensitivity.** Repeat the primary cell for each of the four regions as the priority
  region. This is the test of whether the result is a property of the mechanism or of one region. Cost is
  known up front and is included in the plan, not added later.
- **Slack re-measurement.** `K_r` is a property of the active set, and the active set can shift with the
  target because the weights feed back into the aggregation. Report the `K_r > 3` share per `kappa` and per
  arm; if the slack collapses at high `kappa`, that is a measured boundary of the design and is reported,
  not corrected.
- **Efficiency.** Runs per window are unchanged, so runtime is unchanged; record wall-clock only.
- No defensive failure cases are enumerated: the run is 20 seeds over a fixed ladder, and every cell is
  reported.

## Smoke scope and deduplication

One smoke test only, on the single changed critical path: a one-seed, one-`kappa` dry run whose purpose
is to confirm that the re-weighted target artifact loads, that `RMSE_mu` is computed against the new
weights, and that the run directory records the new target hash. The earlier rounds already proved the
override identity, determinism, and the guard exemption; those are not repeated here. The smoke test is
excluded from the publication evidence and must not be reported as a result.

## Power gate before any confirmatory run (Phase 0, no training)

The recent round showed the cost of skipping this: its `80 %` minimum detectable effect was `5.80 %`
against an estimate of `1.49 %`, so the design could not test the bar it was aimed at. Phase 0 therefore
runs first and can stop the round:

1. From the **existing 20 frozen seeds** at `kappa = 1`, compute the paired sd of `RMSE_mu` between the
   control and each treatment arm on the same seeds, using the concentrated weights of the primary cell
   as the scoring weights (a re-scoring of stored checkpoints, no training).
2. Compute `MDE80` at `n = 20`.
3. **STOP** if `MDE80` exceeds `2 %` of the control's deployment-weighted error, because the design would
   then be unable to resolve the effect size the claim needs. The STOP writes `TE2_BLOCKED.md` with the
   measured sd, and adding seeds is **not** the fallback: at the observed paired sd, resolving a small
   effect would need thousands of pairs, and the honest response is to say so.

## Result tables or figure specs

`tables/TE2_MAIN.csv`: one row per (`kappa`, arm, seed) with the validation and test `RMSE_mu`,
`WorstGroupRMSE`, `Tail_RMSE`, `Delta_group`, `Delta_c-s`, the realised target top-1 share, the `K_r > 3`
share, and stability flags.

`tables/TE2_CONTRAST.csv`: one row per (`kappa`, treatment arm, priority region) with `n`, mean `D`,
sd, bootstrap interval, `MDE80`, the oracle gap, and the pre-registered decision booleans.

`figures/TE2_LADDER.pdf` (spec only; visual composition belongs to `ccf-visual-composer`): `x` =
`kappa` on a log scale, `y` = mean `D` as a percentage of the control's error, the oracle gap as a
horizontal reference at each `kappa`, and the bootstrap interval as whiskers. No curve smoothing, no
truncated axis.

## Missing values

Every cell of every table above is `TBD` until the round runs. The only numbers in this document are
(a) analytic concentration arithmetic from a four-group structure, (b) the region station counts
`10/11/11/11`, (c) the measured slack `88.9 %` with median `K_r = 12`, and (d) the frozen arm inventory —
each traceable to `results_text_repairs/round_v1/BLOCK_SCREEN.json`, the runner source, or the frozen
artifacts.

## Execution priority

1. **Phase 0 power gate** (re-scoring only, minutes). A STOP here saves the whole round.
2. **Freeze** the target artifact, the priority-region rule and its outcome, the `kappa` ladder, the
   endpoint, the decision rule, and the seed list, into `TE2_FROZEN_PREREG.json`.
3. **Primary cell**: `kappa = 5`, one region, arms `local_hajek`, `inst_cal`, `debt_cal`,
   `raven_simoracle` at 20 seeds = 80 runs, about 55 minutes at the observed runtime.
4. **Ladder**: `kappa in {1, 2, 10}` plus the single-region limit for the same arms and seeds = 320 runs
   more.
5. **Priority-region sensitivity**: the primary cell repeated for the other three regions = 240 runs.
6. **Attribution ablations** (`raven_wo_*`) only if a cell separated in step 3 or 4.

Steps 3 to 6 total roughly 640 runs, about 7 hours of the same single-threaded path the earlier rounds
used. Steps 1 and 2 are prerequisites and cannot be skipped. If the total is too large, cut step 5 before
step 4, and record the cut.

## No-fabrication status

No result is asserted anywhere in this document. Arm semantics come from the runner's own method list;
the region mapping, station counts, slack measurement and arm inventory come from frozen artifacts or
measured files; the concentration arithmetic is analytic and must be re-derived and frozen before any
run. If any prerequisite is missing — the re-weighted target cannot be built from the frozen artifact, or
the arms do not load under it — the round stops and writes `TE2_BLOCKED.md` rather than substituting a
proxy.

## Next CCFA owner

`ccf-experiment-designer` again if a cell separates and the attribution ablations are needed; otherwise
`ccf-paper-reviewer` to re-read the Evidence axis against the new numbers, and `ccf-paper-writer` only
after an explicit authorial decision to put a result into the manuscript.
