# TARGET_SOURCE_AUDIT

## varpi_tar (atomic deployment law)

| field | value |
|---|---|
| object | `varpi_i^{tar}` |
| intended (paper / R1b) | unique public atomic law; SS/U-Air = train-split supported uniform |
| current R1b source | implicit only: `TargetBuilder.build(..., split="train")` inside `deployment_groups.build_paper_h_payload` |
| current `π^{tar}` source | **different law**: `build_pi_target(..., split="test")` in `sag_runtime.prepare_sag_bundle` |
| train metadata | yes (paper μ) |
| val metadata | no |
| test metadata | **yes for π^{tar}** (test-split support), public covariates only |
| labels / outcomes | no (TargetBuilder does not read Y) |
| public deployment metadata | `unit_id`, `split`, `support_flag`, `spatial_id`, `absolute_time`, sealed `s(i)`, frozen client map |

**BUG_CONFIRMED:** paper `μ` and Gate `π^{tar}` are not derived from one `varpi`.

## mu

| field | value |
|---|---|
| object | `μ_g` |
| R1b function | `paper_mu` / `build_paper_h_payload` |
| source split | **train** |
| formula | uniform on train+supported atoms, then `∑ 1{h(i)=g}` |
| h(i) | `RepeatableTimeOfDayMapper` UTC hour//6 |
| labels | no |

## pi_tar

| field | value |
|---|---|
| object | `π^{tar}_{k,s}` |
| function | `raven_mcs.correction.pi_target.build_pi_target` |
| call site | `src/raven_mcs/experiments/sag_runtime.py` line `build_pi_target(..., split="test")` |
| source split | **test** |
| formula | `π_{k,s}=Λ_s λ_{k\|s}` from **test-split** `TargetBuilder` atom masses |
| `target_group_main` at call | E3 `target_group` string (spatial×time), not used for π mass except via which units are in the split |
| labels | no |

Also `window_runner.build_full_runner` rebuilds π with `split="test"` if caller omits `pi_target`.

## Compatibility

R1b: `μ` train / `π` test ⇒ `TARGET_COMPATIBILITY_BUG_CONFIRMED`.

R1c fix: freeze one train-split `varpi`, derive both `μ` and `π` from it. Test Y / residuals never enter. Test-side **public** covariates may exist on atoms but do not receive `varpi` mass.
