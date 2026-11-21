# A0 — run-time revision versus current source

Scope: does a code-revision difference explain why the run-time `RMSE_mu` and a
checkpoint re-evaluation disagree at U-Air seeds 30007 / 30016 / 30018?

## Files compared

| file | bytes | sha256 (16) | identity |
|:---|---:|:---|:---|
| `artifacts/e4_wo_inst_reference_penalty_final_correction_r1/recovered_source/window_runner.py` | 37 194 | `f7bff5e30c76898f` | **the run-time revision**: equals `method_source_hash` in every frozen run ledger |
| `src/raven_mcs/training/window_runner.py` | 62 933 | `55af5140f480bf0a` | current working tree |
| `…/recovered_source/methods.py` | 21 486 | — | run-time `methods.py`, also recovered |
| `src/raven_mcs/e3/real_runner/runner.py` | — | — | **not recovered**; this file holds the metric call site |

## What the two revisions do at the only place that matters

| behaviour | run-time revision | current |
|:---|:---|:---|
| inactive window (`window_slice.records` empty) | returns at lines 277–297: `clock.skip_empty_window()`, registers `model_versions[...] = deepcopy(theta)`, **no `theta` change, no model sync** | returns at lines 1034–1056: identical structure |
| `self.theta = …` | line 606, inside the active path | line 1169, inside the active path |
| `self.model.load_state_dict(self.theta)` | line 607, immediately after, **active path only** | line 1170, same position |
| `load_state_dict` occurrences in the file | exactly 1 (line 607) | exactly 1 (line 1170) |

Both revisions therefore share the same sync semantics: the module is re-synced
only when a window aggregates, and an inactive window changes neither `theta`
nor the module.

## Conclusion of A0

**A code-revision difference is not the explanation.** The run-time revision is
available and its sync logic matches the current one; the metric call site lives
in `e3/real_runner/runner.py`, which was not recovered, so A0 cannot see the
metric path itself. This is a stated coverage limitation, not a negative result
about the revision.

Also refuted here, with the same read-only evidence (recorded for completeness):

- **different revision / different batch**: `runner_source_hash = 2f5728de2d…`,
  `method_source_hash = f7bff5e30c…`, `git_commit = b01db69e8554…` are identical
  for all 20 U-Air seeds of an arm, and the ledger timestamps run 06:17 → 07:45
  continuously at ~4.5 min/seed with no batch boundary.
- **file damage or an overwritten artifact**: `events.parquet`,
  `checkpoints/final.pt` and `final_metrics.json` for the disputed *and* control
  seeds all match `E3_CANONICAL_HASH_MANIFEST.json`; the tree is also internally
  consistent (`final_metrics.json` ≡ `final_metrics_dual_domain.json`).
