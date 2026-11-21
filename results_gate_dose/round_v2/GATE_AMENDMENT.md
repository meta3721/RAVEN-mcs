# G3 amendment — bound relaxed from relative 1e-6 to relative 1e-5

Round: `results_gate_dose/round_v2/`
Amended: 2026-10-07, **after** the original G3 verdict was written and **before any dose
cell was run**. Authorized by the user's instruction "修订G3".
Instruction: `raven-mcs-estimand-gate-execution-prompt.md` §II-3, sha256 `ffb4bde6…`

## 1 What is being amended, and what is not

**Amended:** the G3 relative bound only.

| item | original (II-3) | amended |
| --- | --- | --- |
| `\|ΔRMSE_μ\| / RMSE_μ` | ≤ 1e-6 | **≤ 1e-5** |
| `\|ΔΔ_group\| / Δ_group` | ≤ 1e-6 | **≤ 1e-5** |
| `\|ΔΔ_c-s\| / Δ_c-s` | ≤ 1e-6 | **≤ 1e-5** |
| `active_clients` identical on every window | yes | **unchanged** |

**Not amended:** G1, G2, the arms, the configuration, the levels, the masks, the seeds
30001–30020 of the dose design, the θ-rescoring rule, the estimand, H1, H2, H3, δ = 0.5 %,
the bootstrap seed, the decision rules, `THETA_SCORED.csv`, or the output list.

## 2 The original verdict is preserved, not replaced

The executed G3 at 1e-6 stands as written and is **not** deleted or edited:

* `GATE_G3.json` — original per-cell record, `tol_rel: 1e-6`, `pass: false`, 3 fails;
* `GATE.json` — original stop record, `pass: false`, `failed_gate: "G3"`;
* `GATE_REPORT.md` — the stop report;
* the 40 `raven` m = 0 runs under `runs/m0/` — untouched.

The amended verdict is written as a **new file** (`GATE_G3_AMENDED.json`, and a new
`GATE.json` that carries both), so an auditor sees the pre-amendment state and the
amendment side by side. This amendment does not retroactively make the original run pass.

## 3 Why the bound was wrong

II-3 justifies 1e-6 with "four orders of magnitude below δ = 0.5 % and above the measured
drift (5.3e-8 relative on SensorScope)". The second half is not true of the distribution it
was meant to cover. Measured over the 40 executed cells (20 seeds × 2 datasets, all four
endpoints, `GATE_G3.json`):

| statistic | value |
| --- | --- |
| cells within 1e-6 | 37 / 40 |
| worst SensorScope | 1.516e-06 (`Delta_group`, seed 30019) |
| worst U-Air | 2.229e-06 (`RMSE_mu`, seed 30002) |
| drift quoted in II-3 | 5.3e-08 (seed 30001 `RMSE_mu` — one cell of the 40) |

So the bound was calibrated to a single favourable cell. The observed drift is a
floating-point path difference in the θ trajectory (the P2 CVXPY/CLARABEL solve is in the
`raven` arm and not in `raven_wo_design`, which reproduces bit-exactly at G2), so it is
unbounded by construction and cannot be assumed to sit below any fixed threshold; only its
magnitude relative to the effects under test matters.

## 4 Why 1e-5 is safe for what G3 is for

G3 exists to show "the code drift is negligible against the effects tested". The dose
design's smallest effect of interest is δ = 0.5 % = 5e-3. The amended bound is **500× below
δ**, and the largest observed drift (2.23e-06) is **2 200× below δ**. A drift at 1e-5 moves
`r_RMSE` by at most 1e-5 in absolute terms — two orders of magnitude below the slope
resolution the H1 bootstrap can produce from 20 seeds — so it cannot flip a label.

## 5 Confirmation rule, fixed before the confirmation runs

**A first confirmation rule was written and then withdrawn before it ran.** It proposed fresh
seeds **30021–30025**, and it is impossible: the frozen artifacts hold exactly seeds
30001–30020 (`artifacts/e3_formal_runs_r1/runs/<ds>/raven/seed30001…seed30020`), and there
are no EventTraces beyond seed 30020 either, so those seeds have neither a stored reference
to compare against nor a trace to train on. The rule is recorded here as withdrawn, and the
job that would have executed it was cancelled before writing any gate file. No confirmation
run of that kind exists.

### The rule actually used

G3's quantity is the **relative deviation between a fresh run and its stored artifact**. The
stored reference set is fixed at 20 seeds, and every one of them is already an original G3
cell, so no independent seed-based confirmation of *that* comparison is constructible. What
is instead fixed now, before the amended evaluation is written:

1. **Reused cells are labelled as reused.** The 40 m = 0 runs and the four G1 runs come from
   the pre-amendment execution (`results_gate_dose/round_v2/runs/m0`, `g1_rep1`, `g1_rep2`).
   G1 established that this process is bit-reproducible (θ bit-equal, endpoints exactly 0),
   so a re-run reproduces those bytes; the driver reuses them and says so rather than
   pretending to re-derive them. `M0_RUNS.json` records `n_new` and `n_reused`.
2. **The amended verdict is computed and reported together with the original one, per cell**
   (`pass_1e-5` and `pass_1e-6_original` in `GATE_G3_AMENDED.json`). The original verdict is
   never overwritten.
3. **The full deviation distribution is reported**, not just the worst cell: max, median and
   95th percentile of `|Δ|/value` per endpoint per dataset, so a reader can see how much
   headroom the amended bound has rather than only that it passes.
4. **The decision rule is conjunctive and fixed now:** the amendment passes only if all 40
   cells satisfy `active_clients` identical and all three relative bounds at **1e-5**, *and*
   the reported distribution's 95th percentile stays within **2e-6** — i.e. the amended bound
   must be at least 5× the bulk of the drift, not merely above its worst cell.
5. If any of that fails, the amendment fails and Part II stops again with `pass: false`.

The ten confirmation runs described in the withdrawn rule were never executed; the revised
rule executes **four G1 runs and four G2 runs** additionally — both cheap, and both freshly
generated under the amended protocol.
