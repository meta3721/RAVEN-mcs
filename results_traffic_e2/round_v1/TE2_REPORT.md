# TE2 step 3 — primary cell (kappa = 5, priority region 1)

Frozen server step (the round's only changed variable is the **deployment target distribution**).
The target artifact was injected through `run_e3_real(target_artifact=...)` with no edit to `src/`,
which works on this block because `FROZEN_TARGET_ARTIFACTS` contains only `sensorscope` and `uair`.

## Pre-registration, and a hash caveat

- `TE2_FROZEN_PREREG.json`, frozen 2026-10-10T13:56:56.428063+00:00
- priority region `region1`, kappa `5.0`
- priority rule: region holding the largest share of the frozen pre-outcome target mass at kappa=1; ties broken by ascending region id
- tie note: region1/2/3 tie at 0.255814 under kappa=1; the tie-break rule above is part of the pre-registration and was fixed after Phase 0
- arms: control `local_hajek`, treatment `['inst_cal', 'debt_cal']`, oracle ceiling `raven_simoracle`; roles from runner.py L498-L502 p2_methods
- seeds 30001-30020 (20)
- endpoint: RMSE_mu under the concentrated target weights
- decision rule: supported only if the bootstrap interval lies entirely favourable AND the mean exceeds its own MDE80 AND the effect is at least 2 % of the control's deployment-weighted error; every ladder cell is reported as measured

**Two hashes exist for the same content and must not be conflated.** Each run's
`config_snapshot.json` records the runner's own digest `sha256_json({mu, head_groups, tail_groups,
n_groups})`, which is `fbade3683aaf3e72...`; the artifact file's own
`_artifact_sha256` field was produced with a different serialisation and reads
`f34e5b9403036cd6...`. The runner's value is the anchor: it is written into every run. The runner
also labels the path itself as `inline_fixture_freeze` and overwrites any caller-supplied label,
so the label is not a discriminator; the digest is.

## Smoke test (the only one, on the changed critical path)

One cell, `local_hajek` seed 30001. Stored `RMSE_mu` `1.01148448233591` equals a manual re-score of
the same checkpoint under the concentrated weights to the last digit, differs from the re-score
under the frozen weights (`1.0055697313116083`), and that frozen-weight re-score reproduces the
frozen uniform-target run of the same cell (`1.0055697313116085`). The injection is therefore in
force, the metric uses the new weights, and the cell still reproduces the frozen protocol when
scored with the frozen target. `optimizer_steps = 0` on every run confirms the server step was not
replaced.

## Scores under the concentrated criterion

| arm | mean test `RMSE_mu` | sd | mean concentrated validation `RMSE_mu` | mean `K_r <= 3` share |
|---|---:|---:|---:|---:|
| `local_hajek` | 1.014396 | 0.003767 | 0.991176 | 0.1478 |
| `inst_cal` | 1.014247 | 0.003933 | 0.991151 | 0.1478 |
| `debt_cal` | 1.014008 | 0.004052 | 0.991122 | 0.1478 |
| `raven_simoracle` | 1.014168 | 0.003919 | 0.991139 | 0.1478 |

## The pre-registered contrast

Bar = 2 % of the control's deployment-weighted error = `0.020288`; `n = 20`.

| contrast | mean D | sd D | MDE80 | bootstrap 95 % | interval favourable | mean > own MDE80 | effect >= 2 % bar | **separated** |
|---|---:|---:|---:|---|---|---|---|---|
| control - `debt_cal` | +0.000388 | 0.000846 | 0.000559 | [+0.00004, +0.00076] | True | False | False | **False** |
| control - `inst_cal` | +0.000149 | 0.000442 | 0.000292 | [-0.00003, +0.00034] | False | False | False | **False** |
| control - `raven_simoracle` | +0.000228 | 0.000438 | 0.000289 | [+0.00006, +0.00042] | True | False | False | **False** |

**Result under the pre-registered rule: no treatment arm is separated.** Every treatment contrast fails at least one of the three conditions, so the structural-concentration claim is not supported at this cell.

The control-versus-oracle contrast is the ceiling of what any weighting inside this class could buy
at this concentration; where it is small, the treatment has little room by construction rather than
by failure of the projection.

## The number this step was run to obtain

Phase 0 could only give a lower bound on the paired sd, because its checkpoints were trained under
the uniform target. These arms were trained **for** the concentrated target, so this paired sd is the
real one:

- control vs `debt_cal`: paired sd `0.000846` (0.0834 % of the control level), `MDE80 = 0.000559`, against the 2 % bar `0.020288`.
- control vs `inst_cal`: paired sd `0.000442` (0.0436 % of the control level), `MDE80 = 0.000292`, against the 2 % bar `0.020288`.
- control vs `raven_simoracle`: paired sd `0.000438` (0.0432 % of the control level), `MDE80 = 0.000289`, against the 2 % bar `0.020288`.

## Feasible-set slack under the concentrated target

Mean `K_r <= 3` share across the 80 cells: `0.1478`. The design required this
to be re-measured because the aggregation weights feed back into the active set; the frozen
uniform-target value was `0.1111` on one cell and `0.1508` pooled on the confirm set.

## What this step does not do

- It does not run the `kappa` ladder, the priority-region sensitivity, or the attribution ablations.
  Steps 4 and 5 are unstarted and their cost is unchanged.
- It is not evidence about real deployments: the priority region and its weight were chosen by the
  authors and declared before the runs, which is what makes the contrast interpretable, and it is
  also what limits the claim to the declared scenario.
- No manuscript change follows from it.
