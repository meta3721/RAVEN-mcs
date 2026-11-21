# Amendment A1 — allow fresh `local_steps > 2` training on the sealed E2 Traffic methods

Round: `results_new_block_traffic/round_v1/`
Amended: 2026-10-07, authorized by the user's decision "授权修订闸门" after S1 was refused by
`src/raven_mcs/e3/protocol_closure/reuse_guard.py` (see `S1_BLOCKED.md`).
Instruction: `raven-mcs-new-block-traffic-execution-prompt.md`, sha256 `25f580aa…`

## 1 The conflict this resolves

The instruction's S1 needs `fedavg_window` on `traffic` at seeds 30001–30020 under
`complete_aligned` at `local_steps ∈ {2, 5, 10, 20}`. The repository forbids exactly that
combination: `assert_schedulable_e3_run` raises `DuplicateReusedTrafficRunBlocked` for
`traffic` × `complete_aligned` × any formal seed ×
`{fedavg_window, fedasync_window, flamf_timealign_adapted, twostage_hajek, raven}`, and it does
so **without looking at `local_steps`**. The sealed E2 block it protects is real — 600 run
directories at `local_steps = 2` — so the guard is not wrong; the instruction simply cannot be
executed against it as written.

## 2 What is amended, exactly

One behaviour change, in two files, plus one call site:

| file | change |
| --- | --- |
| `src/raven_mcs/e3/protocol_closure/reuse_guard.py` | `is_reused_e2_traffic_block` and `assert_schedulable_e3_run` gain an **optional keyword-only** `local_steps: int \| None = None`. The block applies when `local_steps is None` **or** `local_steps == 2`; a fresh `local_steps > 2` is schedulable. |
| `src/raven_mcs/e3/real_runner/runner.py` (call site, L222) | passes `local_steps=int(local_steps)` so the guard can see it. |

**Not amended:** the sealed method list, `FORMAL_SEEDS`, `SCENARIO`, the E2 artifacts, the
sealed `local_steps = 2` runs, `filter_new_schedule`, the canary guard
(`e3/canary/traffic_reuse_guard.py`, which still blocks the sealed five at any seed), the
instruction's ladder levels, arms, thresholds, endpoints, seed split or decision rules.

## 3 Why blocking `local_steps == 2` and not "anything but 2"

The sealed block is the `local_steps = 2` grid. Refusing to retrain that exact grid is the
guard's purpose and is preserved. Allowing only **strictly greater** budgets would be the
narrowest form, but the guard cannot distinguish "a different hyper-parameter" from "the same
one" for values below 2 either, so the rule is stated as `local_steps == 2` to keep it exactly
the sealed grid and no wider. Any level the ladder actually uses is therefore covered.

## 4 Backward compatibility, checked

* Every existing call site passes no `local_steps`, so `local_steps is None` ⇒ **unchanged
  behaviour**. The guard still blocks, and
  `tests/unit/test_e3_multidataset_protocol_closure_core.py::test_duplicate_reused_traffic_run_blocked`
  (which calls the guard without `local_steps` and expects the raise) still passes.
* `test_non_reused_traffic_method_schedulable` (a method outside the sealed five) is unaffected.
* The canary path uses its own guard and its own call, so canary behaviour is untouched.
* `reuse_guard.py` is pinned by sha256 in
  `artifacts/e3_real_runner_pair_oracle_correctness_closure_r1/E3_REAL_RUNNER_CORRECTNESS_SOURCE_HASHES.json`
  (`46d26da6…`). That pin describes a historical source state and cannot be satisfied by the
  working tree in any case — `git status` already reported 97 modified files under `src/`
  before this session — so this amendment does not make a previously valid hash check start
  failing. It is recorded here instead of being silently absorbed.

## 5 Consequence for the ladder: level 2 is reused, not retrained

With the amendment, ladder levels **5, 10 and 20 train fresh**. Level **2 cannot**, because it
*is* the sealed block. S1 will therefore take level 2 from the sealed E2 artifacts —
`artifacts/e2_traffic_formal_runs_r1/runs/<seed>/complete_aligned/fedavg_window/final_metrics.json`,
which carry `RMSE_mu` (for example `1.0063766454710172` at seed 30001) — and record
`local_steps_source` per rung so the provenance is visible.

**Disclosure.** Those sealed runs were produced by the E2 runner, not by
`run_e3_real`, so level 2 is not numerically interchangeable with the fresh rungs in the way
two `run_e3_real` runs are. This is a weaker comparison than the instruction intended and is
the price of not retraining a sealed grid. It is reported, not hidden: the ladder table
carries the level-2 source, and the verdict states that one rung of four is inherited. If the
inherited rung is the one that decides `L*`, `S1_VERDICT.json` will say so explicitly.

## 6 Reversal

Reverting is mechanical: drop the `local_steps` argument from the two guard functions and the
`run_e3_real` call site. Nothing in the amendment writes to, moves or invalidates any sealed
artifact.
