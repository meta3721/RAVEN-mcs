# EXECUTION REPORT — endpoint screen S1 (bias, group-bias, exceedance)

```text
Round      : results_endpoint_screen/round_v1
Prereg     : PREREG.md sha256 e9ab6f1e471204f9c2df1755bf190e4d6e204283eacfe8ff3bd4f011123b7875
             (11959 bytes), recorded in MANIFEST.sha256 before any scoring
Executed   : 2026-10-04/05. 220 checkpoint evaluations, no training, elapsed 150.5 s
Writes     : results_endpoint_screen/round_v1/ only
Untouched  : src/, artifacts/, every existing results_* directory, the manuscript, git
DECISION   : gate = FAIL (City Scanner only) -> weighting_path = CLOSED,
             no slope interpreted (instruction 1.4, 5)
```

## 1. Gate — instruction §1.4

| block | rule | n | measured | result |
|---|---|---|---|---|
| SensorScope, all arms | `\|Δ\| ≤ 1e-12` | 100 | `max \|Δ\| = 0.0` | **PASS** |
| U-Air, seeds ∉ {30007, 30016, 30018} | `\|Δ\| ≤ 1e-12` | 85 | `max \|Δ\| = 0.0` | **PASS** |
| U-Air, the three trigger seeds, all five arms | recorded, not failed | 15 | `max \|Δ\| = 0.05661` | **recorded** |
| City Scanner, 20 runs | `\|Δ\| ≤ 1e-12` vs `CS_ACCEPTED.json` | 20 | `max \|Δ\| = 3.68033` | **FAIL** |

The trigger-seed pattern came out exactly as the instruction declares it: the 15 rows above
1e-12 are precisely `{30007, 30016, 30018} × {fedavg_window, raven, uniform_window, proj_beta,
proj_beta_debt}`, ranging 0.01495 to 0.05661. **U-Air is clean on 85/85 non-trigger rows with
`|Δ| = 0.0` exactly**, so the mirror/θ trigger is the only source of U-Air discrepancy and the
checkpoint score is canonical there, as the instruction says.

**Overall gate = FAIL, and the failure is City-Scanner-only.** The two decision blocks are exact.

## 2. Decision — mechanical application of §1.4 and §3

`SCREEN_DECISION.json`:

```text
gate: fail   gate_failed_blocks: [cityscanner_nyc_pm25]   cityscanner_only_failure: true
slopes_interpreted: false
E_mix  : {sensorscope: inapplicable, uair: inapplicable, path: closed}
E_group: {sensorscope: inapplicable, uair: inapplicable, path: closed}
E_dec  : {uair: inapplicable, path: closed}
weighting_path: closed
```

No slope is interpreted, because §1.4 says *"One unexpected failure stops the round. No slope is
interpreted. Do not fall back to retraining."* The instruction's only escape hatch for a City
Scanner problem is §5 (*"Treat a City Scanner slope … as permission to train"* is forbidden) and
the declared amendment A3 (CS is descriptive and outside the decision) — neither of which licenses
producing a SensorScope/U-Air verdict in the same round that a gate row failed. **The honest output
of this round is therefore "no verdict", not `null`.** `harm` and `inapplicable` are equally not
verdicts here, and no endpoint was closed on the merits.

## 3. What was computed but withdrawn

The pipeline produced a dose–response table before the gate verdict was applied. It has been moved
to `SCREEN_DOSE_provisional_WITHDRAWN.csv` and is not part of the deliverable set. Its numbers are
recorded here only as an operational fact — every 95 % CI contains 0, so had the gate passed the
labels would have been `null` on all four evaluable cells:

| ds | endpoint | n_obs | slope | ci_lo | ci_hi |
|---|---|---|---|---|---|
| sensorscope | `E_mix` | 80 | +0.03340 | −0.10064 | +0.15844 |
| sensorscope | `E_group` | 80 | +0.03340 | −0.10064 | +0.15844 |
| uair | `E_mix` | 80 | −0.14761 | −0.32148 | +0.04782 |
| uair | `E_group` | 80 | −0.13102 | −0.28292 | +0.04393 |
| uair | `E_dec` | 0 | — | — | — (no arm declares a physical scale) |
| cityscanner_nyc_pm25 | `E_mix` / `E_group` | 10 | +0.22895 | −0.27217 | +0.59040 |

**These are not results of this round and must not be cited as one.** They are recorded so that the
next round does not mistake their absence for "not run".

## 4. Why City Scanner failed — the diagnosis, not a guess

The City Scanner reconstruction is faithful on every identity the frozen evidence fixes:

| check | expected (frozen evidence) | measured |
|---|---|---|
| `eventtrace` hash | `CS_ACCEPTED.json:eventtrace_hash = 0178b5fe…b106386` | **identical** |
| dataset identity | `CS_PHI_DECISION.json:dataset = cityscanner_nyc_pm25` | used |
| `atomic_units.parquet` sha256 | `bcb3c07f1cbb0bad8799d5094930722f5af4cb26df2f335898953d4ea4104b55` | **identical** |
| `mu` vs `CS_TRAIN_SETUP.json` | equality within 1e-12 | `max abs diff = 0.0` |
| `n_pi_target_keys` | 1164 | 1164 |
| `n_pi_opp_keys` | 959 | 959 |
| train / test units | 9343 / 2090 | 9343 / 2090 |
| design flags | `design_on=true`, `gate_unused=true` | patch applied |

So the data, the trace, the target, the margins and the gate setting are all right, and the
prediction cost is still ~10× the stored `RMSE_mu` (3.1–3.7 against a stored 0.3641). Something in
the **runner/checkpoint wiring** differs from the lost original driver — not the setup. The
candidate classes, stated as candidates and not resolved this round:

1. the model's target-group space (`n_groups`) does not match the 4-region `h(i)` the setup uses,
   so the `μ`-weighted pairing is wrong (this would also explain why CS `E_mix` and `E_group` are
   large and nearly equal here);
2. the checkpoint was trained in a different standardized space than the one
   `data/processed/cityscanner_nyc_pm25` implies (raw `target_mean = 5.9782`,
   `target_std = 12.6469`);
3. `p2.LOCAL_STEPS = 2` / `p2.S_MAX = 5` are the Pilot-2 driver's constants, not necessarily C1's.

Resolving it requires the lost `run_c1_cityscanner.py` or its config; **no retraining is permitted
by this round**, and the instruction forbids substituting a story for a measurement.

## 5. A repository defect found while doing this (separate from the screen)

`scripts/run_nodesign_supplement.py` — the surviving reconstruction driver for this block — loads
**the wrong dataset**:

| | path it loads | hash it produces |
|---|---|---|
| `run_joint_ou_cs_p2.load_cityscanner_dataset()` | `data/processed/cityscanner_nyc_p2_measured_o` | `atomic_sha256 = 06e2953afad17b27…`, 13 029 rows |
| what `CS_PHI_DECISION.json` fixes for the frozen runs | `data/processed/cityscanner_nyc_pm25` | `bcb3c07f1cbb0bad…`, 14 723 rows |

Its module docstring already discloses that *"The original City Scanner driver
(scripts/run_c1_cityscanner.py) was lost; this driver rebuilds its training stage."* The rebuild
substituted the Pilot-2 measured-`O` dataset for the PM2.5 one. This screen did **not** use that
driver (amendment A3), but any result that came out of it for the City Scanner block inherits the
substitution and should be re-examined. This is reported, not repaired — it is outside this round's
write scope.

## 6. Side checks that came out clean

* `dropped_mu_mass = 0.0` on all 220 runs — every active group has test units, so the §1.2
  renormalization never had to drop mass, and the >0.01 stop never approached.
* `n_groups_scored`: 220 (SensorScope), 144 (U-Air), 4 (City Scanner) — exactly the manuscript's
  group counts, with no length mismatch or missing key, so §1.1's hard stop never fired.
* `E_mix` vs `E_group` differ on the decision blocks, as §1.2 intends (`E_group` does not cancel
  across groups); on City Scanner they are near-identical, which is consistent with §4's
  diagnosis 1.
* `E_dec` coverage: the two frozen U-Air arms only (20 runs each), base rate `0.0860` both times —
  inside `[0.02, 0.98]`, so not `inapplicable` on that ground. The three trained U-Air arms produce
  no `E_dec` because they ship no `metric_scale_policy.json` (amendment A6).
* `rmse_abs_diff = 0.0` exactly, not merely `≤ 1e-12`, on all 185 non-trigger decision rows.

## 7. Deviations and amendments (all declared before scoring)

```text
A1  `_mu_weights_for_test` / `_predict` are in raven_mcs/e3/real_runner/runner.py, not in the
    module defining `build_full_runner`. Import sites corrected; no weight definition changed.
A2  `rmse_mu`'s third parameter is named `target_weights`; passed positionally.
A3  City Scanner setup rebuilt from the frozen evidence rather than from the surviving driver's
    loader (which loads the wrong dataset, §5). Identities asserted before use.
A4  SensorScope has no `_scaler_*` attributes because `load_paper_dataset` does not z-score it
    (its metrics are already in °C). Expected; no inversion applied there.
A5  The City Scanner gate is reported, never silently relaxed.
A6  Runs without `metric_scale_policy.json` (all three trained arms, both datasets) yield no
    `E_dec`: the §1.3 inversion cannot be licensed from their own artifacts. Their stored
    `RMSE_mu` still reproduces exactly, so the other two endpoints are unaffected.

Also declared: one instruction-internal inconsistency, resolved as documented and not by
substitution — §1.1 says the weights come from `_mu_weights_for_test(pred, mu)` "in the same
module" as `build_full_runner` (false, per A1), and §1.3 says E_dec uses `w` "recomputed on the
physical-scale vectors". Since standardization is monotone and affine, the exceedance indicator is
identical in either space, and `_mu_weights_for_test` depends only on `pred["groups"]` and `mu`, so
the same weights are used and the requirement is satisfied by construction.
```

## 8. What this round establishes, and what it does not

* **Establishes:** every frozen SensorScope and U-Air checkpoint in this screen reproduces its
  stored `RMSE_μ` exactly from the checkpoint alone (`|Δ| = 0.0`, 185/185 non-trigger rows), so the
  endpoint screen's inputs are sound and re-scorable without training.
* **Establishes:** the City Scanner block **cannot** be re-scored from its frozen artifacts by the
  surviving code, and a repository driver exists that silently uses a different dataset for it.
* **Does not establish:** whether `E_mix`, `E_group` or `E_dec` move with `Δ_group`, and therefore
  whether the weighting path may open. **`weighting_path` stays `closed`**, as it was before this
  round; nothing in this round opened it, and the provisional slopes are withdrawn.

## 9. Files

```text
PREREG.md                                 the frozen rules + declared amendments
MANIFEST.sha256                           PREREG.md digest
SCREEN_RUNS.csv                           220 rows, one per checkpoint evaluation
SCREEN_DECISION.json                      gate fail (CS only), weighting_path closed
SCREEN_DOSE_provisional_WITHDRAWN.csv     computed, not interpreted, not a deliverable
EXECUTION_REPORT.md                       this file
```
