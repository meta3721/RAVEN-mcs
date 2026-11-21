# A6a / A6b clause audit and the stabilization error `eps_stab`

Frozen 2026-09-28. Read-only audit for the Proposition 3 repair. No training, no
solver, no change to `src/`, to any `.tex`, or to any existing artifact.

- Script: `compute_a5a6_eps_stab.py` (this directory)
- Results: `A5A6_EPS_STAB.json` (this directory)
- Constants: `a_max = 20.0`, `p_min = 0.05`, `pi_min = 1e-6`, `d_max = 10.0`,
  `q_min = 0.05` — the defaults of
  `raven_mcs.training.window_runner.build_full_runner`, which
  `raven_mcs.e3.real_runner.runner.run_e3_real` calls without overriding them
  (`runner.py:471-484`). The value `a_max = 40.0` belongs to the E1-R2
  weight-safety calibration (`configs/frozen/e1_r2_weight_safety.yaml`) and to
  the E2 traffic runner; it is not what these blocks ran with.
- Inputs: `artifacts/e3_formal_runs_r1/eventtraces/<dataset>/<seed>/training_eventtrace/events.parquet`
  (true margins and observed-unit counts);
  `artifacts/e3_formal_runs_r1/runs/<dataset>/local_hajek/<seed>/window_metrics.json`
  (the active set `A_r` of each window);
  `configs/frozen/e1_pi_target_client_stratum.parquet` (SensorScope `pi_tar`);
  U-Air `pi_tar` rebuilt exactly as `run_e3_real` does with
  `pi_target_mode='test'` (288 client-strata pairs, 72 of them zero-mass,
  matching `results_active_set_repair/round_v1/PI_TAR_HOLES.csv`).

## Definition

For each active window `r` of a Design-on run of the 20 formal seeds:

```
zeta_T = pi_tar / max(pi_opp_true, pi_min)      [Design on]   or 1   [Design off]
a_T    = min(a_max, zeta_T / max(p_obs_true, p_min))
d_T    = min(d_max, 1 / max(q_use_true, q_min))
b_T    = n_obs * a_T * d_T,      beta_T    = b_T / sum(b_T)

zeta_s = pi_tar / pi_opp_true                   [Design on]   or 1   [Design off]
a_s    = zeta_s / p_obs_true,    d_s = 1 / q_use_true
b_s    = n_obs * a_s * d_s,      beta_star = b_s / sum(b_s)

eps_stab(r) = || beta_T(r) - beta_star(r) ||_1
```

## Results

| reading | SensorScope | U-Air |
|:---|:---|:---|
| active windows (20 seeds, `local_hajek`) | 1877 | 1402 |
| active client-windows | 4849 | 2923 |
| `eps_stab` median / p95 / max, Design on | 0 / 0.0719 / 0.5530 | 0 / 0.0528 / 0.6800 |
| `eps_stab` fraction of windows > 0, Design on | 10.71 % | 11.13 % |
| `eps_stab` median / p95 / max, Design off | 0 / 0.0806 / 0.6610 | 0 / 0.0254 / 0.9048 |
| `eps_stab` fraction of windows > 0, Design off | 10.71 % | 6.92 % |
| A6a Design-on ceiling ratio `max pi_tar/(pi_opp p_obs)` vs `a_max = 20` | 19.263 (**holds, narrowly**) | 23.473 (**fails**) |
| client-windows above the ceiling, Design on | 0 / 4849 (0 %) | 80 / 2923 (2.74 %) |
| A6a Design-off ceiling ratio `max 1/p_obs` vs `a_max = 20` | 5.195 (holds) | 5.195 (holds) |
| worst Design-on cell | seed30002, window 80, client-000 | seed30001, window 34, client-003 |

The Design-on ceiling clause is **threshold-dependent**: 23.47 exceeds the
`a_max = 20` these runs used and would pass at the E1-R2 value 40. The
earlier audit text claimed the clause was satisfied at both values; that
claim came from reading the clause as a bound on `1/p_obs`, which does not
bound `zeta/max(p_obs, p_min)` because the implemented weight also carries
`pi_tar/pi_opp`.

## Independent re-check of the released readings

`released_audit_recheck` in the JSON recomputes the published audit numbers
from `artifacts/a5_a6_audit/audit_records.csv`:

| reading | recomputed | printed in the supplement |
|:---|:---|:---|
| SensorScope records / observed | 16000 / 12346 | 16000 / 12346 |
| U-Air records / observed | 12800 / 9760 | 12800 / 9760 |
| `min p_obs_true`, both datasets | 0.1925 | 0.1925 |
| `q_min` floor active (observed) | 5.224 % / 5.184 % | 5.22 % / 5.18 % |
| `q < 1/d_max` (observed) | 24.218 % / 23.750 % | 24.22 % / 23.75 % |
| `q < 1/d_max` (all records) | 41.525 % / 41.859 % | 41.52 % / 41.86 % |

## Independent replication

A second, independently written implementation in this directory
(`compute_eps_stab.py`, results in `EPS_STAB.json`, per-window values in
`eps_stab_windows.csv`) reproduces these numbers on the frozen active sets to
twelve significant digits:

| quantity (frozen `A_r`) | this script | `EPS_STAB.json` |
|:---|:---|:---|
| SensorScope Design on, n / p95 / max / frac>0 | 1877 / 0.0718913827552520 / 0.5529816210137829 / 0.10708577517314864 | 1877 / 0.0718913827552503 / 0.5529816210137711 / 0.10708577517314864 |
| SensorScope Design off, p95 / max | 0.0806156442593430 / 0.6609762244170909 | 0.0806156 / 0.660976 |
| U-Air Design on, n / p95 / max / frac>0 | 1402 / 0.0527512886562340 / 0.6800165984717579 / 0.11126961483594865 | 1402 / 0.0527513 / 0.680017 / 0.11127 |
| U-Air Design off, p95 / max / frac>0 | 0.0254320685750476 / 0.9048084096678065 / 0.06918687589158345 | 0.0254321 / 0.904808 / 0.06919 |

That replication also adds four checks this script does not perform:

1. `pi_tar` matches the values recorded in the **frozen run state**
   (`delta_cs_state_v6.parquet`): 27054 SensorScope and 16227 U-Air rows
   compared, maximum absolute difference `0.0`, none unresolved. The rebuilt
   target map is therefore the one the runs used, not merely a reproduction of
   its construction.
2. The active set `A_r` is identical across all nine arms that write
   `window_metrics.json`, so using one Design-on arm costs nothing.
3. **Corollary (b) of the proposition is corroborated on the traces**: with
   Design off, the observation-side contribution to `eps_stab` is exactly `0`
   (`max_eps_with_a_side_only = 0.0`) and the whole residual is the
   usable-update term.
4. Internal consistency: windows with a single active client always have
   `eps_stab = 0`, and no window has `eps_stab > 0` without a biting floor or
   ceiling.

## Caveats

1. The active set is taken from one Design-on arm (`local_hajek`), whose
   restricted support is licensed by its own definition. `eps_stab` itself
   depends on the active set only through which clients enter the window
   normalization.
2. `pi_tar` is the evaluation-derived target map of the frozen protocol
   (`split='test'`); this audit inherits that construction and does not
   address it.
3. `eps_stab` is computed at the *true* margins, so it isolates what the
   floors and ceilings move; it is not a bound on the realized plug-in error,
   which Proposition 3 covers separately through `eps_pi`, `eps_p`, `eps_q`.
4. The `q_min`-floor share on the *active* sets (0.31 % / 0.21 %) differs from
   the released 5.22 % / 5.18 %, which is computed over all observed
   client-windows. Both are reported with their own denominators; this note
   does not restate the released reading.
