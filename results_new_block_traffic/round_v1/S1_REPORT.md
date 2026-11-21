# S1 report — learnability ladder (N3): **NO-GO**

Round: `results_new_block_traffic/round_v1/`
Instruction: `raven-mcs-new-block-traffic-execution-prompt.md`, sha256 `25f580aa…` §3
Authorization: `授权交通筛查` (user confirmed `授权交通检查` was a typo), plus amendment A1
(`GATE_AMENDMENT_A1.md`) permitting fresh `local_steps > 2` training on the sealed methods.
Driver: `scripts/new_block_traffic_stages.py s1`. Executed 2026-10-07.

## 1 Verdict

**`go: false`, `failed: "N3"`** — written by the driver to `S1_VERDICT.json`, whose record was
created before the stage's stop was raised. Per §8 the screen ends here: **S2 never ran, no F
seed was touched, and no number is retuned.**

## 2 The ladder

`fedavg_window` on the chosen family (`e3_complete_aligned`), seeds 30001–30003; `c` is
`central_delivered`'s mean `RMSE_μ` on the same family and seeds:

`c = 0.977673231150311`, threshold `1.01·c = 0.9874499634618141`.

| `local_steps` | mean `RMSE_μ` | min | max | ratio to `c` | source |
| ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 1.0066307 | 1.0063766 | 1.0067794 | **1.02962** | sealed E2, read-only |
| 5 | 1.0051849 | 1.0047191 | 1.0056992 | 1.02814 | fresh |
| **10** | **1.0048537** | 1.0036857 | 1.0064563 | **1.02780** | fresh |
| 20 | 1.0061325 | 1.0032864 | 1.0095952 | 1.02911 | fresh |

Selection rule, applied verbatim:

* **no level qualifies** — every level is above `1.01·c` by 2.78–2.96 %;
* the fallback needs the best level to be **≥ 1 % below level 2**; the best (10 steps) is
  **0.1765 %** below it;
* therefore **NO-GO on N3**.

## 3 What the numbers say

Raising the local budget from 2 to 20 steps moves mean `RMSE_μ` by **0.18 %** at best, and the
20-step rung is *worse* than the 10-step one (1.00613 vs 1.00485) while its seed spread widens
(1.00329–1.00960 against 1.00369–1.00646). Meanwhile `central_delivered` — which trains on the
same delivered data — sits **2.78 % lower** at the best federated level and **2.96 % lower** at
the sealed level.

That is the N3 reading the instruction anticipated, now measured rather than inferred: **the
gap is not optimisation budget.** Twenty times the local work does not close a 2.8 % deficit;
it does not even move 0.2 %. The evidence points to the constraint sitting somewhere other than
the number of local steps, which the protocol does not license this round to pursue further.

## 4 Provenance disclosure

One of the four rungs is inherited, not trained. Amendment A1 states why: the guard protects
the sealed E2 `local_steps = 2` grid by `(dataset, scenario, seed, method)` and cannot
distinguish budgets, so level 2 was **read** from
`artifacts/e2_traffic_formal_runs_r1/runs/<seed>/complete_aligned/fedavg_window/final_metrics.json`
(1.0063766 / 1.0067362 / 1.0067794) rather than recomputed. `S1_LADDER.csv` carries
`local_steps_source` per rung and `S1_VERDICT.json` carries `rung_sources` per cell.

Two consequences, both benign for this verdict and both recorded:

* the inherited rung comes from the **E2** runner, so it is not numerically interchangeable
  with the fresh rungs in the way two `run_e3_real` runs are. It did not decide `L*`: the
  verdict is NO-GO because **no** level cleared `1.01·c`, and the fresh levels 5, 10, 20 each
  fail that test on their own, by 2.81 %, 2.78 % and 2.91 %.
* `central_delivered`'s mean here is 0.977673 on the three S1 seeds, against 0.975425 on the
  twenty-seed set reported in `S0_FOLLOWUP.json`. The two differ because the seed sets differ;
  same source, same recipe.

## 5 Fresh-rung wall time, and the F projection refreshed

Measured on the nine fresh runs: 43.2–62.2 s, mean **45.9 s** at 5 steps, **45.9 s** at 10,
**61.6 s** at 20. §8 asked for the first S1 run's wall time for the F projection; the first
fresh run took **45.93 s** (recorded as `first_run_wall_seconds`).

This supersedes the §8 pre-run projection in the conservative direction. On the **20-step**
mean (61.6 s, the most expensive rung and the worst case for F), `F = 120 runs` projects to
**2.05 h**, against **22.5–24.6 h** estimated from the frozen 2-step artifacts before the
ladder existed. That earlier estimate was wrong by an order of magnitude because it scaled the
frozen per-run cost linearly in `local_steps`, which the measurements contradict (20 steps
costs 1.34× the 2-step cost, not 10×). The projection is moot for this round — F is not
licensed — but it is corrected here rather than left standing.

## 6 Per §6, what this licenses

> **S0 or S1 NO-GO.** NSW-Traffic cannot test the claim either. The reason is reported (N2 or
> N3). No F seed is used.

The reason is **N3**. So:

* the prediction/decision claim is not tested on this block, and **no F seed (30006–30020) was
  read, trained on or scored**;
* combined with S0 (`go: true`), the round's result is: **N1 holds** (6.69 % of windows with
  `≤ 2` clients, mean 12.06 — the condition SensorScope and U-Air fail hardest), **N2 holds**
  (mean `TV(π_arr, μ)` 0.35638), and **N3 fails** (the federated learner does not move toward
  `central_delivered` when given twenty times the local budget);
* this is reported as measured, with no claim beyond the label. The §0 N3 hypothesis — that
  the gap looked like optimisation budget rather than information — is **falsified** by the
  ladder.

For the Evidence axis this closes the last block tried: the route was opened precisely because
N1 fails on SensorScope and U-Air, and it stops at the next necessary condition. What is now on
record across the axis is a sequence of measured necessary conditions rather than a null
result: weights free (N1) ∧ arrival≠target (N2) ∧ learner off its floor moving with budget
(N3) ∧ group errors respond to the training mix with enough headroom (N4) — the first two hold
here, the third does not, and the fourth was never reached because §4 runs only after an S1 GO.

## 7 Outputs

`S1_LADDER.csv`, `S1_VERDICT.json`, `GATE_AMENDMENT_A1.md`, `S1_BLOCKED.md` (the pre-amendment
refusal, preserved), `MANIFEST.sha256`, and 9 fresh run directories under `runs/s1/`. The
sealed E2 level-2 artifacts were read and not modified.
