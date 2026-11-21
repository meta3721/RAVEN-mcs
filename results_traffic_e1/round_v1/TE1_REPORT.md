# TE1: FedAdam headroom confirmation on NSW-Traffic

- Instruction: `ccfa-review-reports/raven-mcs-traffic-e1-confirm-execution-prompt.md`, sha256 `2ffb1fb006f5e45e01bfccaa43936a63bf0225d87f9bf604f0bd728f064a70cb`
- Driver: copy of the S1' driver, sha256 `46e46328a78053d187595f76a035fc69d499fbe818aef331abe083c2a011640f`
- Frozen server optimizer: `{"mode": "adam", "eta_s": 0.003, "beta1": 0.9, "beta2": 0.99, "tau": 0.001}`, `LOCAL_STEPS = 2`, one server update per window
- Block `traffic`, scenario `complete_aligned`, `eta_s = 0.003`, arms ['fedavg_window', 'raven_simoracle']
- Screen seeds 30001-30005 (closed, not re-tested); confirm seeds 30006-30020

## Gates

G0 identity passed on both arms: the re-run `RMSE_mu` equals the S1' file exactly (0.8274680256045374 and 0.8102506853916549), with differences confined to ['runtime_seconds'].

G-const frozen before any confirm test prediction: `n = 6192`, weighted mean `0.00877759`, `c_val = 0.99448683`, ceiling `2*c_val = 1.988974`, weight-vector sha256 `31b71588621220f666498199fd239eccf66b0c46a17d20ea3864b14410d890ad`. The weight vector is identical when recomputed from the G0 re-run checkpoint (True). The prompt's unweighted check value (sd 0.99457, mean 0.00878) agrees with the scoring-path value to four decimals.

## Screen diagnostic

Five S1' screen seeds, stability rule of section 4 applied, no GO column: seed 30001 raven_simoracle = pass (validation RMSE_mu 0.794624), seed 30002 raven_simoracle = pass (validation RMSE_mu 0.843190), seed 30003 raven_simoracle = pass (validation RMSE_mu 0.803949), seed 30004 raven_simoracle = pass (validation RMSE_mu 0.856495), seed 30005 raven_simoracle = pass (validation RMSE_mu 1.125605). The seed 30005 oracle arm passes the ceiling as the prompt expected.

## Confirm seeds and the primary estimand

`n_confirm_pairs = 15`, stability failures = `0`, analysis set `n = 15`.

Mean `H = -0.014921` (sample sd `0.074593`), percentile bootstrap 95% interval `[-0.054230, 0.017568]` (10000 draws, rng 20261007), `MDE80 = 0.058027` at `n = 15`, confirm `K_r <= 3` share `0.150819` (fedavg arm; simoracle arm `0.150819`).

| GO condition | value | holds |
|---|---:|---|
| H >= 0.01 | -0.014921 | False |
| bootstrap lower > 0.005 | -0.054230 | False |
| MDE80 < 0.5 * H | 0.058027 vs -0.007461 | False |
| K_r <= 3 share <= 0.25 | 0.150819 | True |

**Verdict: `NO-GO-H`.**

| seed | validation RMSE_mu fedavg | validation RMSE_mu oracle | test RMSE_mu fedavg | test RMSE_mu oracle | H_s |
|---|---:|---:|---:|---:|---:|
| 30006 | 1.069603 | 1.030345 | 1.073919 | 1.039378 | 0.032163 |
| 30007 | 0.657375 | 0.802230 | 0.659320 | 0.815323 | -0.236611 |
| 30008 | 0.989810 | 0.947237 | 1.002919 | 0.960605 | 0.042191 |
| 30009 | 0.802366 | 0.805168 | 0.811735 | 0.814077 | -0.002885 |
| 30010 | 0.774819 | 0.783985 | 0.782185 | 0.795153 | -0.016579 |
| 30011 | 0.924052 | 0.867494 | 0.929087 | 0.874588 | 0.058659 |
| 30012 | 0.909874 | 0.931027 | 0.926373 | 0.945179 | -0.020301 |
| 30013 | 1.580249 | 1.480575 | 1.571563 | 1.459449 | 0.071340 |
| 30014 | 1.003529 | 0.996542 | 1.014801 | 1.008008 | 0.006694 |
| 30015 | 0.796326 | 0.841656 | 0.812224 | 0.857771 | -0.056077 |
| 30016 | 0.907088 | 0.880657 | 0.918593 | 0.893217 | 0.027624 |
| 30017 | 0.965263 | 1.043257 | 0.956362 | 1.043219 | -0.090820 |
| 30018 | 1.088905 | 1.121653 | 1.092105 | 1.126299 | -0.031311 |
| 30019 | 0.875841 | 0.878566 | 0.896074 | 0.899307 | -0.003609 |
| 30020 | 1.032385 | 1.036146 | 1.059702 | 1.064255 | -0.004296 |

## Deviations

- The execution order of the prompt's section 8 was followed: driver copy, G0, freeze, screen table, then the 15 confirm pairs, then sections 4 and 5.
- The prompt fixes the arms as `fedavg_window` and `raven_simoracle`; `raven` was not run. Stage B was not run and `eta_s` was not re-selected.
- `K_r <= 3` is reported per seed and per arm in `tables/TE1_KR.csv`; the GO condition uses the analysis-set mean over the fedavg arm, with the simoracle mean reported alongside so the reading does not depend on that choice.
- The finiteness limb of the stability rule scans every JSON file in the run directory and every checkpoint tensor. The runner writes no separate training-loss series, so no loss file exists beyond those.
- No `src/`, paper, frozen artifact or `results_server_optimizer/round_v1/` path was modified; the traffic runs used the reuse-guard exemption already recorded in the diagnosis ledger Part IX item 65.

## What this round does not claim

The screen seeds are not re-tested and are not combined with the confirm seeds. A `GO-H` would be the prediction-headroom clause only, not a deployment-decision result and not a full E1. No edit to the paper follows from this round.

## Addendum (recorded after the run)

1. **A defect in this round's own pre-run checker wrote a spurious `TE1_BLOCKED.md`.** The first
   invocation compared the requested server optimizer against `ServerOptWindowRunner.SERVER_OPT`
   *before* any `install()` call, which returns the un-installed default
   `{"mode": "off", "eta_s": null}`. It is not a section-1 STOP condition: no confirm seed was started
   and no run directory was created. The file is kept as `TE1_BLOCKED.voided-selfcheck.md` for audit,
   and the checker now installs the configuration and compares it against the S1' frozen
   `SERVER_OPT_META.json`, which matched exactly
   (`{"mode": "adam", "eta_s": 0.003, "beta1": 0.9, "beta2": 0.99, "tau": 0.001}`, `local_steps` 2).

2. **Interpretation of "the test split is read only after `TE1_FROZEN_CONST.json` exists and G0 has
   passed" (section 5).** Read here as: no *confirm* test prediction is computed before the freeze. G0
   necessarily reads the screen seeds' stored test `RMSE_mu`, and section 8 places G0 before the
   freeze, while section 0 states that those seeds are design inputs which have already seen the test
   split. No confirm seed's test value was computed before `TE1_FROZEN_CONST.json` was written.

3. **The prompt's planning `MDE80` was conservative.** It projected `MDE80(n = 15) = 0.163696` from the
   screen sd `0.210430`. The confirm sd is `0.074593`, so the realised `MDE80` is `0.058027`. The
   screen sd was inflated by seed 30005 (`H = -0.456978`); the confirm set has no comparable outlier,
   its most negative seed being 30007 at `H = -0.236611`, and its sign split is 6 positive to 9
   negative. The verdict is unchanged.

4. **`K_r <= 3` is identical for both arms on every confirm seed** (mean `0.150819`, range
   `0.100000`-`0.222222`), so which arm supplies the GO-condition value does not affect the reading.

5. **The finiteness limb of the stability rule** scanned every JSON file in each run directory and
   every checkpoint tensor. The runner writes no separate training-loss series, so no loss file exists
   beyond those.

6. No `src/`, paper, frozen artifact or `results_server_optimizer/round_v1/` file was modified by this
   round; the 18 traffic runs here used the reuse-guard exemption already recorded in the diagnosis
   ledger Part IX item 65, and each carries `REUSE_GUARD_EXEMPTION.json` for the `fedavg_window` arm.

7. **The exemption record is written per traffic run, not per refused arm.** The driver passes
   `allow_reused_traffic_rerun` for every `traffic` cell and therefore stamps
   `REUSE_GUARD_EXEMPTION.json` (and `reuse_guard_exemption: true` in `SERVER_OPT_META.json`) on
   15/15 `fedavg_window` confirm runs **and** on 15/15 `raven_simoracle`
   confirm runs. Only the `fedavg_window` arm is on the sealed list `E2_TRAFFIC_REUSED_METHODS`
   (`fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `twostage_hajek`, `raven`); the
   `raven_simoracle` arm is not, so the guard would have scheduled it with no opt-in at all. The record
   is faithful to what the caller passed, but it does not by itself imply that the guard refused a cell.
