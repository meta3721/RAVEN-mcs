# S1' gates

- Instruction: `ccfa-review-reports/raven-mcs-s1prime-server-optimizer-execution-prompt.md`
- Instruction sha256: `14b09cbfafa40db088fb65d117229810916b0a8ef12037f0305eb3c7e22aebd4`
- Driver: `results_server_optimizer/round_v1/driver/s1p_driver.py` sha256 `2363528e7e91a51edf6b2a237300d3be84923da82d95ce67223378d39afcc95a`
- Injection: `raven_mcs.training.window_runner.FullWindowRunner` is rebound to `ServerOptWindowRunner`; `build_full_runner` resolves that name at call time, so **no `src/` file was edited**.

## Amendments confirmed by the user on 2026-10-07, before any run

| id | amendment |
| --- | --- |
| A1 | G0 is a **true identity test**: subclass with the optimizer set to plain SGD at `eta_s = eta`, compared against an **unmodified `FullWindowRunner` re-run in the current tree**. The frozen-artifact comparison is a disclosed diagnostic, not a gate (the prompt was written expecting a bit-exact match with the frozen files, which `P0_REPORT.md` section 5 shows is not achievable for reasons of artifact vintage). |
| A2 | G0 is **not gated on NSW-Traffic**: the E3 traffic tree has no `fedavg_window` and no `raven` arm. The E2 `complete_aligned` contract is disclosure only. |
| A3 | Stage C evaluates `MDE80` at **n = 5** per section 2; n = 15 is left to a separately authorized confirmatory run. |

## G0 — identity test

- **deterministic verdict (the gate): True**
- literal verdict including the wall-clock field: False (runtime_seconds is a wall-clock measurement, not a function of the computation; any two runs differ there)

| block | arm | fields compared | deterministic mismatches | final theta byte-identical | wall-clock field |
| --- | --- | --- | --- | --- | --- |
| sensorscope | fedavg_window | 32 | 0 | True | `runtime_seconds` = [15.694416199999978, 15.12775380000005] |
| sensorscope | raven | 32 | 0 | True | `runtime_seconds` = [20.06011019999994, 21.010255500000085] |
| uair | fedavg_window | 32 | 0 | True | `runtime_seconds` = [8.015443600000026, 7.752348100000063] |
| uair | raven | 32 | 0 | True | `runtime_seconds` = [7.000710900000058, 7.342877599999952] |

Every deterministic field of `final_metrics.json` is bit-exact and the final `checkpoints/final.pt` is byte-identical between the unmodified runner and the subclass with the optimizer set to plain SGD. `runtime_seconds` is the only field that ever differs, because it is a wall clock and not a function of the computation; it is named in one place in the driver (`WALL_CLOCK_FIELDS`) and reported here with both values rather than silently dropped.

### Frozen-artifact diagnostic (disclosure only, per A1)

| block | arm | field | frozen | re-run | abs diff | rel diff |
| --- | --- | --- | --- | --- | --- | --- |
| sensorscope | fedavg_window | `Delta_c_s` | 1.2422979138143753 | 1.2422979138143753 | 0.000e+00 | 0.000e+00 |
| sensorscope | fedavg_window | `Delta_group` | 1.0433329926179937 | 1.0433329926179937 | 0.000e+00 | 0.000e+00 |
| sensorscope | fedavg_window | `Head_RMSE` | 7.5148050228514345 | 7.5148050228514345 | 0.000e+00 | 0.000e+00 |
| sensorscope | fedavg_window | `RMSE_mu` | 7.914361980993586 | 7.914361980993586 | 0.000e+00 | 0.000e+00 |
| sensorscope | fedavg_window | `Tail_RMSE` | 8.436411883047754 | 8.436411883047754 | 0.000e+00 | 0.000e+00 |
| sensorscope | raven | `Delta_c_s` | 1.214493695326521 | 1.214493695326521 | 0.000e+00 | 0.000e+00 |
| sensorscope | raven | `Delta_group` | 0.9984597031193984 | 0.9984597031193984 | 0.000e+00 | 0.000e+00 |
| sensorscope | raven | `Head_RMSE` | 7.514267663509899 | 7.514267663509899 | 0.000e+00 | 0.000e+00 |
| sensorscope | raven | `RMSE_mu` | 7.913791224192832 | 7.913791224192832 | 0.000e+00 | 0.000e+00 |
| sensorscope | raven | `Tail_RMSE` | 8.435797825584572 | 8.435797825584572 | 0.000e+00 | 0.000e+00 |
| uair | fedavg_window | `Delta_c_s` | 1.2480410574750196 | 1.3154871914305875 | 6.745e-02 | 5.404e-02 |
| uair | fedavg_window | `Delta_group` | 1.1131258678428484 | 1.0467286693701783 | 6.640e-02 | 5.965e-02 |
| uair | fedavg_window | `Head_RMSE` | 1.2013683736925316 | 1.1640685117331944 | 3.730e-02 | 3.105e-02 |
| uair | fedavg_window | `RMSE_mu` | 1.210848485707097 | 1.1712625825964957 | 3.959e-02 | 3.269e-02 |
| uair | fedavg_window | `Tail_RMSE` | 1.2199078552171159 | 1.1781486886837496 | 4.176e-02 | 3.423e-02 |
| uair | raven | `Delta_c_s` | 1.210200108193248 | 1.210200108193248 | 0.000e+00 | 0.000e+00 |
| uair | raven | `Delta_group` | 1.0832400542605098 | 1.0832400542605098 | 0.000e+00 | 0.000e+00 |
| uair | raven | `Head_RMSE` | 1.1928102980862099 | 1.1928102980862099 | 0.000e+00 | 0.000e+00 |
| uair | raven | `RMSE_mu` | 1.201716880706229 | 1.201716880706229 | 0.000e+00 | 0.000e+00 |
| uair | raven | `Tail_RMSE` | 1.2102316408991802 | 1.2102316408991802 | 0.000e+00 | 0.000e+00 |

Reading: SensorScope `fedavg_window`, SensorScope `raven` and U-Air `raven` reproduce the frozen artifacts **exactly** (U-Air `raven` even with a byte-identical checkpoint, `eb8137dd02b0ebfd58f8d208`). **U-Air `fedavg_window` does not**: it moves from `1.210848485707097` to `1.1712625825964957` (-3.27 %), with the active-window count rising from 66 to 74 and `a_r_size` systematically one larger in the re-run. That arm is a Table II baseline, so this is a real artifact-reproducibility miss on the current tree and is reported as a finding; it does not affect this round, whose Stage A/C comparisons are internally consistent (all arms re-run in the same tree).

Correction recorded for honesty: an earlier check in this session compared `theta_hash_after` between frozen and re-run `window_metrics.json` and reported 'identical on 80/80'. That comparison was vacuous — `window_metrics.json` does not serialise the theta hashes, so both sides were `None`. The checkpoint byte-comparison above is the real evidence.

## G1 — reads-after-update audit

- STOP condition fired: **False**. `final_metrics.json` has 32 keys and no hash / theta / model key, so none of the affected logged values reaches the decision metric.

| line | code | sees theta_new | note |
| --- | --- | --- | --- |
| `L1170-L1172` | `self.model.load_state_dict(self.theta); new_version = self.clock.apply_server_update(); self.model_versions[new_version] = copy.deepcopy(self.theta)` | True | these are the writes the override re-does after the optimizer step; the override re-loads the model and re-registers the latest version with theta_new |
| `L1173-L1190` | `memmap flush/close of mm, mmap_obj` | not_applicable | touches no theta / model / model_versions |
| `L1191-L1198` | `debt update, self.scale += eta, self.omega_sum += eta*omega` | not_applicable | reads omega, self.mu, self.eta only |
| `L1200-L1202` | `self._update_lagged_estimators(window_slice, client_data); self._update_variance_state(local_updates, a_r_clients)` | not_applicable | both methods (L1289, L1384) take window/client arguments and contain no reference to self.theta, self.model or self.model_versions (verified by full-file scan) |
| `L1204` | `after_hash = self._theta_hash()` | False | REAL FINDING: _theta_hash() (L253-L255) iterates sorted(self.theta.items()), so under the override it is computed BEFORE the optimizer step and therefore hashes theta_sgd, while the run continues from theta_new |
| `L1231, L1236-L1237` | `per-client 'global_model_hash': after_hash; 'model_hash_before'/'model_hash_after'` | False | derived from the same stale after_hash |
| `L1269-L1287` | `return WindowMetrics(..., theta_hash_after=after_hash, ...)` | False | WindowMetrics.theta_hash_after carries the pre-optimizer hash |

The one real finding is **L1204** `after_hash = self._theta_hash()`: it is evaluated inside `super()._process_window(...)`, therefore **before** the server-optimizer step, so `WindowMetrics.theta_hash_after` (L1275) and the per-client `global_model_hash` / `model_hash_after` (L1231, L1236-L1237) record `theta_sgd` while the run continues from `theta_new`. These are log-only fields; they appear in `window_metrics.json` diagnostics, not in `final_metrics.json`. Under FedAdam they will therefore differ from the values an unmodified run would log, which is expected and disclosed.

## G2 — determinism

- **pass: True** (`results_server_optimizer/round_v1/runs/g2_det_a/sensorscope/fedavg_window/seed30001` vs `results_server_optimizer/round_v1/runs/g2_det_b/sensorscope/fedavg_window/seed30001`, eta_s = 1e-3, FedAdam)
- deterministic differences: none
- wall-clock field excluded: {'runtime_seconds': [16.223075799999947, 14.980286399999954]}

## Gate conclusion

All three gates pass. The grid may run.
