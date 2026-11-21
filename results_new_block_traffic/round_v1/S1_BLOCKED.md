# S1 blocked at launch — a `src/` reuse guard forbids the entire ladder

Round: `results_new_block_traffic/round_v1/`
Instruction: `raven-mcs-new-block-traffic-execution-prompt.md`, sha256 `25f580aa…`
Authorization: `授权交通筛查` given by the user on 2026-10-07 (after confirming that
`授权交通检查` was a typo). S1 was then launched and refused by the codebase.

## 1 What happened

`scripts/new_block_traffic_stages.py s1` failed on its first run, before any run directory
was created:

```text
File "scripts/new_block_traffic_stages.py", line 125, in stage_s1
    d = run_arm("fedavg_window", s, ls, "s1", family)
File "scripts/new_block_traffic_stages.py", line 84, in run_arm
    run_e3_real(...)
File "src/raven_mcs/e3/real_runner/runner.py", line 222, in run_e3_real
    assert_schedulable_e3_run(...)
File "src/raven_mcs/e3/protocol_closure/reuse_guard.py", line 45
DuplicateReusedTrafficRunBlocked: DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED:
  dataset=traffic scenario=complete_aligned seed=30001 method=fedavg_window
  is REUSE_ONLY_NO_RERUN from sealed E2 Traffic Complete-aligned.
```

No run was created and no number was produced: `runs/` does not exist.

## 2 The guard, read from the source

`assert_schedulable_e3_run` refuses when all four hold
(`src/raven_mcs/e3/protocol_closure/reuse_guard.py` L24–L46):

| condition | value from `constants.py` |
| --- | --- |
| `dataset == "traffic"` | matches |
| `scenario == SCENARIO` | `SCENARIO = "complete_aligned"` |
| `seed ∈ FORMAL_SEEDS` | `FORMAL_SEEDS = range(30001, 30021)` — **every seed S1, S2 and F use** |
| `method ∈ E2_TRAFFIC_REUSED_METHODS` | `["fedavg_window", "fedasync_window", "flamf_timealign_adapted", "twostage_hajek", "raven"]` |

## 3 What that closes

The guard blocks on `(dataset, scenario, seed, method)` alone — it does **not** look at
`local_steps`, the trace family, or the target. So at the protocol's seeds:

| stage | arms it needs | blocked? |
| --- | --- | --- |
| S1 | `fedavg_window` | **blocked at every ladder level, all 12 runs** |
| S2 | `fedavg_window`, `raven_simoracle`, `central_delivered` | `fedavg_window` **blocked** ⇒ the whole stage |
| F | `fedavg_window`, `raven`, `local_hajek`, `debt_cal`, `inst_cal`, `twostage_hajek`, `raven_simoracle`, `central_delivered` | `fedavg_window`, `raven`, `twostage_hajek` **blocked** ⇒ the whole stage |

`fedavg_window` is the primary comparator of the ladder **and** the F-H1 denominator, so the
block is not partial: S1 cannot produce its first rung, and S2/F cannot produce their
comparator.

## 4 Why the block is not a mistake by the guard

The sealed E2 Traffic block is real and complete. `artifacts/e2_traffic_formal_runs_r1/runs/`
holds 6 conditions × 5 methods × 20 seeds = 600 run directories, and their
`config_snapshot.json` files record **`local_steps = 2`** for all of them. Among the six
conditions is `complete_aligned`, i.e. a traffic `complete_aligned` block already exists for
exactly the five methods the guard lists. So `fedavg_window / traffic / complete_aligned /
seed 30001–30020 / local_steps = 2` is an existing sealed artifact, and the guard's job is to
stop it being recomputed.

## 5 Why the instruction and the codebase disagree

The instruction's §0 says, of this block:

> "There is no frozen `raven` or `fedavg_window` here."

That is true of the **e3** tree (`artifacts/e3_formal_runs_r1/runs/traffic/`, whose six frozen
arms are `central_all`, `central_delivered`, `debt_cal`, `inst_cal`, `local_hajek`,
`raven_simoracle` — confirmed in `S0_FOLLOWUP.json`). It is not true of the repository: the
**e2** tree holds `fedavg_window`, `raven` and `twostage_hajek` for these seeds, and the
reuse guard is written so that those specific methods may never be scheduled again under
`complete_aligned`. S0 did not surface this because the guard fires at run time, not at
inventory time, and S0 is read-only.

## 6 Options, none of which I may take unilaterally

1. **Consume the sealed `complete_aligned` `local_steps = 2` runs for ladder level 2** and run
   only levels 5, 10, 20 fresh — which still requires the guard to permit those three, and it
   does not: the guard ignores `local_steps`.
2. **Amend the guard** (its `E2_TRAFFIC_REUSED_METHODS` list or its `assert_schedulable_e3_run`
   call site) so that a new `local_steps` may be trained. That is a **`src/` edit**, which the
   instruction forbids outright ("Do not edit `src/`"), so it needs an explicit user decision
   and a recorded protocol amendment.
3. **Run the ladder on a different trace family** — the guard is keyed on `scenario`, which
   `run_e3_real` hardcodes to `complete_aligned` for e3 runs. The e2-only families
   (`balanced`, `complete_counteracting`, `observation_only`, `opportunity_only`,
   `usable_only`) are not schedulable through the e3 entry point at all, so this is not a
   route without a `src/` change either.
4. **Stop the round and report the incompatibility**, which is what this file does.

I am not choosing among 1–3: 2 and 3 require editing `src/`, which the instruction forbids
without a new decision, and 1 does not work as stated.

## 7 State

* No training run exists anywhere in this round; `runs/` is absent.
* No confirm seed (30006–30020) has been read, trained on or scored.
* `src/`, the manuscript, `artifacts/` and every other `results_*` are untouched by this
  attempt. `main.tex` remains `02447bfe6256632b…`.
* S0 and its follow-ups stand: `S0_VERDICT.json` (`go: true`, `e3_complete_aligned`, mean TV
  0.35638), `S0_REPORT.md` §9.1–§9.3, `S0_FOLLOWUP.json`, `MANIFEST.sha256`.

## 8 What is needed from the user

A decision on option 2 or 4, i.e. either:

* **authorize a `src/` amendment** that lets the ladder train `fedavg_window` (and S2/F their
  `fedavg_window`, `raven`, `twostage_hajek` cells) at seeds 30001–30020 under
  `complete_aligned` at `local_steps ∈ {5, 10, 20}` while keeping the sealed `local_steps = 2`
  runs untouched and reused — plus confirmation that the sealed E2 block's own
  `local_steps = 2` runs may serve as ladder level 2; or
* **stop this round**, in which case the outcome is: the instruction's S1 is not executable
  against this codebase as written, and the reason is a sealed-block reuse guard rather than a
  measured property of the data.
