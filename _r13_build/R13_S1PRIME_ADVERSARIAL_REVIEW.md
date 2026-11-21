# R1.3 adversarial review of round S1' (`results_server_optimizer/round_v1/`)

Reviewer stance: falsify, not confirm. Everything below was recomputed from artifacts on
disk; nothing was taken from `S1P_REPORT.md` on trust.

## Artifacts relied on (sha256, full 64 hex)

| artifact | sha256 |
| --- | --- |
| `results_server_optimizer/round_v1/S1P_REPORT.md` | `3cfad4c49eea1c45a438567912a946b0b68b4f8928a3e642fdb0f004474268bb` |
| `results_server_optimizer/round_v1/S1P_FROZEN_CONFIG.json` | `a041ba42e9c139f70356a5cbe0213cb15f6819123dd16e4b678a45ed82df4cde` |
| `results_server_optimizer/round_v1/driver/s1p_driver.py` | `308007730989dafc1544b0ad3e60d0a3a949a3cb4f3b802cfb2084c6605ac98e` |
| `results_server_optimizer/round_v1/S1P_STAGE_C_H.json` | `1739e0cb75cae06fd577173eccb2541da2d2b862f5eb576e07635a8629fa233b` |
| `results_server_optimizer/round_v1/tables/STAGE_C_H.csv` | `272dccdaaac5b5aabf63baa50eb8e45fba37a32107fce376b6d431a6cbd7c51f` |
| `results_server_optimizer/round_v1/tables/STAGE_A_GRID.csv` | `d839258fa9b54a34a480e9ade27687189666dc600b4123ea7140b4d550d65970` |
| `results_server_optimizer/round_v1/tables/MOVEMENT.csv` | `ae2f7d6f3e68af37244ec1387956f55003317fd27d3ffbf05a3278b39f3ac8b0` |
| `results_server_optimizer/round_v1/S1P_STAGE_A_VERDICT.json` | `91bae4ae21f1be0d6d3228e63b92f6b511d483fe994e5ef6c130d84fc9729744` |
| `src/raven_mcs/training/window_runner.py` | `55af5140f480bf0a3d0c07849e8add7d8d4f275348f791d25a573d428681f4b5` |
| `src/raven_mcs/training/client.py` | `2881d6035c124a754ee14f8a84b38cebe5686196d7da8f322e1bf860158cb4a7` |
| `src/raven_mcs/e3/real_runner/central_real.py` | `10bc16fac89081b162743b9b11a046edc56bc025fa1cd6fbdfe6e05784ec7218` |
| `src/raven_mcs/e3/real_runner/runner.py` | `c82b261c10c3eb2b4df5307e96f0641753385474aba422d2f5e62a514231a69f` |
| `src/raven_mcs/e3/protocol_closure/reuse_guard.py` | `57223308d88df73df5beb688809ad78db84a3968f3d70f488ee2261d81677aae` |
| `results_new_block_traffic/round_v1/S0_REPORT.md` | `8f7d621f4adb21c5c44298ead59f6f579460e9ddd5ad0a4deeb0a12df8fd1895` |
| `data/processed/sensorscope/atomic_units.parquet` | `47581d5b04d3795b3fe663198ba32a53e83f35707718a82bd1ec0662daff88ce` |
| `data/processed/uair/atomic_units.parquet` | `0d57445890f7e1a21038c17106a8e7f332e95fe13fe81713f24b8fd0ab254eed` |
| `data/processed/traffic/atomic_units.parquet` | `db45a2ecc66c27abeaf58b0c03ce66de7bfaf6727f4523ea06ef226a9ce3de50` |
| S1' traffic ckpt seed30001 (`A_eta0.003`) | `635a476bce094e0282ffc96c3594b84abad15bd2e39482ee6718e361c2b24e16` (= `checkpoint_hash` in its own `runtime_manifest.json`) |
| S1' sensorscope ckpt seed30001 (`A_eta0.01`) | `3cc02cf42ae1affbcfba24851fc1005aaa02537acd40afbb1dcc2a2a8c26f89c` |
| S1' uair ckpt seed30001 (`A_eta0.003`) | `0891f684eed753237c36bb80e8a1544b9fc9e03a3ab3e00d8aa1bfbd27112412` |

## Headline numbers this review measured (all via the repo's own scoring path)

Target means on the **test** split (train z-scored space) and what predictors actually do:

| block | val mean | test mean | zero-predictor RMSE | best constant RMSE | new fedavg test RMSE | vs const |
| --- | --- | --- | --- | --- | --- | --- |
| sensorscope | 2.0186 | **7.6572** | 7.9367 | **2.0878** | 7.8453 | **-275.8 %** |
| uair | -0.1456 | **-0.8066** | 1.0537 | **0.6781** | 0.9775 | **-44.2 %** |
| traffic | 0.0088 | 0.0027 | 1.0067 | 1.0067 | 0.8351 | **+17.0 %** |

New fedavg (eta_s*) prediction statistics: sensorscope sd 0.005-0.33 with correlation -0.001..+0.159;
U-Air sd 0.03-0.22 (corr 0.20-0.34); traffic sd 0.33-0.96 (**corr 0.59-0.71**, weighted R^2 0.22-0.41).
Frozen `local_hajek`/`raven_simoracle` on traffic: sd 0.012-0.021, strictly 0.09-0.44 % better than a
constant - exactly the `S0_REPORT.md` section 9.2 "constant predictors near 0" regime.

## Objections

### O1 SURVIVES - the S1' traffic arms learn; the sensorscope and U-Air arms do not, and N3' "PASS" on those two blocks compares mis-scaled near-constants

Decided by (all recomputed with `runner._predict` / `runner._mu_weights_for_test` /
`metrics.accuracy.rmse_mu`, reproducing the stored `RMSE_mu` to 0.000e+00):

* sensorscope `runs/A_eta0.01/sensorscope/fedavg_window/seed30001/final_metrics.json`: `RMSE_mu`
  7.956738 vs the **zero** predictor 7.936699 (gain **-0.25 %**) and the best constant 2.087750
  (gain **-281 %**). Target mean 7.6572, model mean prediction -0.0207, sd 0.0279, corr -0.001.
* U-Air `runs/A_eta0.003/uair/fedavg_window/seed30001`: 1.048689 vs zero 1.053714 (**+0.48 %**) and
  constant 0.678052 (**-54.7 %**). Target mean -0.8066, model mean -0.0018, sd 0.0321.
* Every frozen sensorscope arm reproduces the same pathology (e.g. `frozen fedavg_window` 7.9144 vs
  zero 7.9367). `central_all` - the arm the report cites as proof that centralisation does move the
  model - is 7.6072 vs the constant 2.0878, i.e. also 264 % worse.
* traffic `runs/A_eta0.003/traffic/fedavg_window/seed30005`: 0.776281 vs constant 1.006693 = **+22.9 %**,
  corr +0.705. The frozen traffic arms are +0.09..+0.44 % vs the same constant.

Consequence: on sensorscope and U-Air `RMSE_mu` is dominated by the (wrong) constant level, so N3'
PASS there is a statement about which near-zero offset is marginally less wrong, not about learning.
On traffic the improvement is real and is the only genuine learning in the round.

Smallest fix: report, per block, `1 - RMSE_mu(arm)/RMSE_mu(best constant on the same test units and
weights)` next to `RMSE_mu`, and require a positive value on sensorscope and U-Air before any
"the learner now learns" language. One script, `_r13_build/r13_a_constants.py`.

### O2 SURVIVES - the N3' reference is unequal-effort: 20 Adam steps, batch 32, lr 1e-3

Decided by `src/raven_mcs/e3/real_runner/central_real.py:106` (`opt = torch.optim.Adam(model.parameters(), lr=lr)`),
lines 111-117 (`for _ in range(int(local_steps))` with `torch.randint(0, n, (min(32, n),))`), and
`artifacts/e3_formal_runs_r1/runs/traffic/central_delivered/seed30001/central_train_summary.json`
(`steps: 20`, `n_train_units: 1268`, `final_train_loss: 0.7284644246`). The federated arm performs
92-98 server updates on sensorscope, 73-76 on U-Air and 99-100 on traffic (active windows, from
`window_metrics.json`; `SERVER_OPT_META.json` `n_windows_optimizer_applied` agrees), 2 local SGD steps
each, with client-side `(θ_s - θ_local)/(lr·E_loc)`
normalisation (`src/raven_mcs/training/client.py:104-107`) and a hand-rolled server step
(`src/raven_mcs/training/window_runner.py:1155-1167`). `MOVEMENT.csv` (frozen rows) puts
`central_delivered` movement at 2.31-3.33 %, i.e. itself barely trained.

So `ratio_to_c` compares "FedAdam federated" with "Adam centralized for 20 minibatch steps", not
federated with centralized. The report already concedes this in deviation 7; what it does not do is
withhold the inference. The correct reading of traffic is the opposite of the standard one: pooled
central training loses to the federated arm (0.9738 vs 0.8351) because it is undertrained, not because
federation helps.

Smallest fix: retrain `central_delivered`/`central_all` with the same optimiser family and a step
budget matched to the federated arm's update count (>= 100 Adam steps, full-batch or larger minibatch),
then recompute N3'. Nothing else in the round can substitute for it.

### O3 SURVIVES - claim 4's headroom statement is uninterpretable on two of three blocks

Decided by the same cells as O1: on sensorscope the fedavg arm gains 1.15 % over the zero predictor and
loses 276 % to a constant, while `raven_simoracle` is *worse* than zero (-0.68 %); on U-Air fedavg is
+7.2 % over zero and -44 % to a constant. Both arms of the H contrast are therefore near-constant
predictors, so `H = (RMSE_mu(fedavg) - RMSE_mu(oracle))/RMSE_mu(fedavg)` measures the difference of two
constant offsets. `S1P_STAGE_C_H.json` sensorscope `H_by_seed` = [+0.004523, +0.004374, -0.010055,
-0.052361, -0.040224] is consistent with exactly that: seed-to-seed offset noise.
On U-Air the oracle is worse than fedavg on 4/5 seeds (mean H -0.1633, exact-t 95 % [-0.3165, -0.0102]).

Consequence: "the oracle-margin reference supplies no headroom once the learner trains" is not
established on sensorscope or U-Air - there is no trained learner there to supply headroom to.
It is established on traffic only, and only in the weak "not positive" sense (O5).

Smallest fix: state H for sensorscope and U-Air as `not evaluable (both arms are constant-equivalent:
see the constant-predictor column)`, and label only traffic's H as a measurement.

### O4 SURVIVES - the section-6 `K_r` clause was applied to the very blocks whose H it now excludes, and is recorded as a per-cell number, not the block number

Decided by `driver/s1p_driver.py:807` (`STAGE_C_KR_GUARD_BLOCKS = ("sensorscope", "uair")`), line 836
(`if star is None or n3 != "PASS": hres[block] = {"verdict": "not_run"}`) and line 874-876
(`guard = ... kr["share_kr_le3"] > STAGE_C_KR_EXCLUDE`). Stage C therefore ran the two new arms only on
traffic; sensorscope and U-Air `H` values in `S1P_STAGE_C_H.json` come from the Stage A
`A_eta0.01`/`A_eta0.003` fedavg runs, not from Stage C. The instruction's section 6 makes the `K_r`
clause a bar on *upgrading to GO*, not a bar on *measuring* H, so the two `not_run` verdicts are a
deviation that the report presents as a measured result for all three blocks.

Additionally, `kr_le3_share` is called once with the *first* matching grid row's `run_dir`
(`driver/s1p_driver.py:852-853`), so the recorded number is a single-seed share, not the block share.
I verified the driver's number is seed30001's: 73/97 = 0.7525773195876289 for sensorscope, 49/74 =
0.6621621621621622 for U-Air, 11/99 = 0.1111111111111111 for traffic. The block-level means over the
five seeds are 0.7548894423, 0.7538950616 and 0.1385454545. The direction of the verdict is unchanged
(all three exceed/below the 0.25 threshold as reported), but the label "share" is ambiguous and the
report's table implies a block quantity.

Smallest fix: run the two arms on sensorscope and U-Air under the frozen eta_s* and report
`verdict = "excluded_by_kr_clause"` with the block-level pooled share
(`sum(K_r<=3 over active windows) / sum(active windows)`, which is 0.7549 / 0.7539 for SS / UA).

### O5 SURVIVES - traffic's mean H is one outlier seed; the negative sign is not robust

Decided by `S1P_STAGE_C_H.json` traffic `H_by_seed` = [+0.020807, +0.009123, +0.006123, +0.017423,
**-0.456978**]. Recomputations (`_r13_build/r13_hstab.py`, `_r13_build/r13_boot.py`):

* median H = +0.009123; 4/5 seeds positive; leave-one-out mean = +0.013369 when seed30005 is dropped
  (range -0.1061..-0.0217 for dropping any other seed).
* exclude seed30005: mean +0.013369, CI [+0.007623, +0.019115], sd 0.006887, MDE80 0.014328 - which on
  four seeds clears the 1 % mean bar and the 0.5 % LCB bar.
* exact sign test, H > 0: 4/5, p = 0.1875; H > 1 %: 2/5, p = 0.8125.
* the driver's percentile bootstrap gives [-0.268877, +0.017194] where the exact Student-t interval is
  [-0.341984, +0.180583] and the jackknife t interval matches the exact one. The percentile bootstrap is
  anti-conservative here (lower bound *above* the exact one) because n = 5 with one extreme value.

So "H is negative on traffic" is what this rule on these 5 seeds returns, and the report says the
interval contains zero; but the sign is not stable and the magnitude is one seed.

Smallest fix: report the median, the sign test, and the leave-one-out range alongside the mean, or spend
the authorized confirm seeds 30006-30020; at n = 15 with this sd the MDE80 would be 0.1637 (still above
0.5·|mean H|), so more seeds alone will not settle traffic GO-H.

### O6 SURVIVES - MDE80 is at n = 5, while the instruction's section 6 says n = 15, and amendment A3 cites a heading

Decided by the instruction line 122-123 ("`MDE80 < 0.5·H` computed from the paired seed SD at n = 15"),
`S1P_FROZEN_CONFIG.json` (`screen_seeds` = 30001-30005), and `driver/s1p_driver.py:822-824`
(`mde80_paired(sd, n)` with `n = len(Hs) = 5`). The amendment is justified in the driver comments as
"section 2", which is the title line of the seeds table, not a statement about MDE80.
At n = 15 the same SDs give MDE80 = 0.020370 (SS), 0.095943 (UA), 0.163696 (traffic); all three
`cond_mde_lt_half_H` remain False because `mean H < 0`, so no reported verdict changes.
This is a deviation from the round's own instruction text, not an arithmetic error.

Smallest fix: report both columns (`MDE80_n5`, `MDE80_n15`) in `tables/STAGE_C_H.csv` and cite
amendment A3 explicitly in the report's deviations table (it is currently listed as an instruction
mismatch, not as an authorization).

### O7 SURVIVES - the driver's own Stage C CSV writer cannot produce the delivered `STAGE_C_H.csv`, and `STAGE_B_GRID.csv` is missing

Decided by `driver/s1p_driver.py:897-900`:
`w = csv.DictWriter(f, fieldnames=["block","arm","seed","blocked","error"]); w.writerows(rows)`.
If any cell was blocked, `rows` holds 5-key dicts (line 844-845) - `DictWriter` raises `ValueError` - and
if none was, it writes a 5-column file. The delivered `tables/STAGE_C_H.csv` (sha256
`272dccdaaac5b5aabf63ba50eb8e45fba37a32107fce376b6d431a6cbd7c51f`) has a different 18-column header.
No script in `driver/` writes `tables/MOVEMENT.csv` or `tables/STAGE_C_H.csv` (grep for
`MOVEMENT.csv|DictWriter|writerows` over `driver/*.py` returns only `STAGE_A_VALIDATION.csv`,
`STAGE_A_GRID.csv` and the Stage C writer above), so both delivered tables were assembled outside the
driver. **Their numbers are correct** - I recomputed `MOVEMENT.csv` against all 129 checkpoints
(ratio 1.0000) and `STAGE_C_H.csv` against `S1P_STAGE_C_H.json` - but the provenance chain from run to
table is manual, and the per-cell "blocked" reporting for Stage C does not exist. `STAGE_B_GRID.csv`,
required by the instruction even when Stage B is skipped, is absent.

Smallest fix: make the Stage C writer emit `tables/STAGE_C_CELLS.csv` with a uniform field list, emit
`STAGE_B_GRID.csv` carrying `not_run: all blocks PASS at Stage A`, and generate `MOVEMENT.csv` and
`STAGE_C_H.csv` from a committed script rather than by hand.

### O8 SURVIVES (weak) - the `_validation_mu` docstring misdescribes the code, and the stated seal is procedural

Decided by `driver/s1p_driver.py:563` (the full `dataset.atomic_df` copy is passed) versus the
`S1P_FROZEN_CONFIG.json` field `validation_metric` and the driver comment at lines 530-532
("`mu_g` taken from a `TargetBuilder(..., split='validation')` build"). `TargetBuilder.build` filters
`split` internally (`src/raven_mcs/data/target.py:115`), so the code is correct; **I verified the code,
not the docstring**, and the two are equivalent here: the driver's `mu_val` equals the validation-rows-only
build to machine precision, and the metric is applied to validation weights only (`tag == "test_mu":
continue`). Substituting pooled-split masses changes the validation number by at most 1.8e-3 and changes
the selected eta_s on none of the three blocks (val and test both select 0.01 / 0.003 / 0.003). So there is
no leak, but the guardrail is weaker than described: any future edit that makes the mass depend on the test
rows would leak silently.

On the seal: the last Stage A traffic cell finished `2026-10-08T11:16:44.159127+00:00` (its ledger
FINISH), and the frozen config's `created_utc` is `2026-10-08T11:16:45.444695+00:00` - **1.29 s later**.
The test values for all 45 Stage A cells were on disk before the freeze; only the code path kept them
unread. The report discloses this (deviation 4). `S1P_FROZEN_CONFIG.json` was rewritten four times
(driver stdout: `fe84a4c6`, `57b4bcec`, `f56f224c`, `a041ba42`; the last equals the on-disk hash and the
`frozen_config_sha256` recorded in `S1P_STAGE_A_VERDICT.json`). I reconstructed the freeze chain: the
first freeze (`stageA.log` L76) already selected sensorscope 0.01 and U-Air 0.003, the N3' ratios for
those two blocks are byte-identical across every freeze (`0.9865045223849438`, `0.8329209464984179`),
and every freeze is a full re-selection because the driver recomputes the config from all 45 grid rows
each invocation. So the pre-registration claim survives - but the hash differences are **not** all
timestamp-only (changing `created_utc` alone gives three different hashes), so the report's
"the first frozen configuration (`fe84a4c6...`) is superseded by `57b4bcec...`" is incomplete provenance:
the interim `f56f224c` freeze is not disclosed.

Smallest fix: `validation_metric` should read "group masses from a `TargetBuilder` build on the
validation split only"; log a per-block freeze record `{block, eta_s_star, freeze_sha256, created_utc}`
and disclose all four.

### O9 SURVIVES (housekeeping) - the round's runs are not reproducible from provenance, and `runner.py` changed mid-round

Decided by `driver/ledger.jsonl` of every run: `runner_source_hash`, `method_source_hash`,
`source_manifest_hash` and `dataset_hash` are **null for all 87 runs** (`driver/s1p_driver.py:226-237`
passes them, `runner.py:307-311` filters). The ledger records only
`git_commit = 2e47464c2c15d7dae4ceb059592782b9542de625`, and `src/raven_mcs/e3/real_runner/runner.py`
is **untracked in git** (`git ls-files --error-unmatch` fails), so no recorded hash binds the metrics to
a source revision. `runner.py` mtime is `2026-10-08T09:39:05Z`, i.e. **after** the sensorscope/U-Air
Stage A and Stage C runs (08:37-08:54Z) and before the traffic runs (11:10-11:38Z).
This does not invalidate any number: the current tree's scoring path reproduces all 75 checkpoint-derived
`final_metrics.json` values, the current `runner.py` is the one that ran every traffic cell (11:10+), and
G0's identity gate under the current tree is bit-exact with a byte-identical checkpoint on both
sensorscope and U-Air. But for the SS/UA numbers the provenance is an inference, not a witness.

Smallest fix: pass real `runner_source_hash`/`method_source_hash` through `source_identity` and make
`run_e3_real` record them, or `git add` the untracked `e3/real_runner/` sources and pin the commit.

### O10 REFUTED - claim 2's arithmetic and its sub-claim

`tables/MOVEMENT.csv` reconciles with the checkpoints exactly: all nine FedAdam cell means recompute to
ratio 1.0000, and all 129 rows are consistent. Frozen baselines over seeds 30001-30003:
sensorscope `fedavg_window` 0.261404 %, U-Air `fedavg_window` 0.396509 %, traffic `local_hajek`
0.278629 % - matching the report. New at eta_s*: 18.366235 % / 7.311324 % / 9.151184 %, giving
**70.26x / 18.44x / 32.84x** on the 3-seed basis the report uses (52.17x / 20.45x / 34.36x on 5 seeds).
"7-70x" is correct. The sub-claim "mostly through the output bias `head.8.bias`" also holds: its share of
total squared movement is 0.2963 (SS), 0.3786 (UA), 0.4303 (traffic), top-1 tensor on every block.
Parameter movement is therefore established; it just is not evidence of learning (O1).

### O11 REFUTED - claim 3's arithmetic

`S1P_STAGE_C_H.json` reproduces exactly from its own per-seed inputs: H_by_seed, `mean_H`, the 10,000-draw
percentile bootstrap with `np.random.default_rng(20261007)`, `paired_sd` (ddof=1) and
`MDE80 = (t_.975,n-1 + t_.80,n-1)·sd/sqrt(n)` all match to the last digit on all three blocks.
`kr_excluded_from_GO` is correctly True-on-SS/UA and False-on-traffic in `STAGE_C_H.csv`, and the
exclusion cannot be hiding a GO: mean H is negative everywhere, and even under the looser exact-t
interval no block clears the 1 % mean bar. The n=5-vs-n=15 issue is O6, and it changes no verdict.

### O12 CANNOT DETERMINE - only one thing I could not settle from artifacts

Whether a *like-for-like optimized* centralized reference would change any N3' verdict. No such
reference exists in this workspace (every centralized arm in `artifacts/e3_formal_runs_r1/` came from the
20-step `run_central_real` configuration). Settling it needs the O2 retrain.

## Verdict on the four claims

**Claim 2 (parameter movement 0.26-0.40 % -> 4-22 %, 7-70x): ACCEPT AS ESTABLISHED.** Every number
reconciles with the checkpoints and with the frozen tree; the sub-claim about `head.8.bias` is also
correct. Only caveat to carry in the wording: movement is not learning (see claim 1).

**Claim 3 (H negative on all three blocks, CIs as quoted): ACCEPT THE ARITHMETIC, WEAKEN THE READING.**
The values are exactly reproducible under the stated rule. But H was *computed* only on traffic; on
sensorscope and U-Air it is a Stage A-derived number whose two arms are both constant-equivalent, so it
cannot be read as a headroom measurement. Accepted weaker wording:
> Under the frozen eta_s*, H is negative on traffic (mean -0.0807, CI [-0.2689, +0.0172], driven by one
> outlier seed; median +0.0091, 4/5 seeds positive) and no block satisfies GO-H. On sensorscope and U-Air
> the section-6 K_r clause excluded both blocks from GO, and both of their H arms are constant-equivalent
> predictors (each within ~1-8 % of the zero predictor and 44-276 % worse than a constant), so their H
> values are not interpretable as headroom.

**Claim 1 (N3' PASS on all three blocks with those ratios): ACCEPT THE NUMBERS, REJECT THE INFERENCE.**
The ratios are correct on the stated rule and seed basis (I recomputed 0.9865045224, 0.8329209465,
0.8575895077 against 5-seed `central_delivered` means 7.9525971525 / 1.1735735655 / 0.9737694570).
What survives is only:
> Under the round's N3' rule, RMSE_mu(fedavg_window at the validation-selected eta_s*) is within 1 % of
> the frozen `central_delivered` mean on all three blocks. On NSW-Traffic this coincides with genuine
> learning: 0.8351 vs the best constant predictor 1.0067 (+17.0 %), prediction/ target correlation
> 0.59-0.71, against 0.09-0.44 % for every frozen traffic arm. On SensorScope and U-Air it does not:
> the arms remain constant-equivalent (within 0.25-7.2 % of the zero predictor and 44-276 % worse than
> the best constant), and the `central_delivered` reference is itself a 20-step, batch-32 Adam run that
> moves only 2.3-3.3 % of its parameter norm, so the comparison is not federated-versus-centralized.

**Claim 4 (a standard server optimizer makes the federated learner train; the oracle-margin reference
supplies no headroom once it does): PARTIALLY ACCEPT, MUST BE SPLIT BY BLOCK.**
The first half is established on NSW-Traffic only (17 % over a constant, corr 0.59-0.71, versus
near-constant frozen arms) and not on SensorScope or U-Air, where the "improvement" is movement of a
near-zero constant. The second half is a valid NO-GO-H on traffic, is vacuous on SensorScope and U-Air,
and is contaminated by the undertrained reference for any "does the learner train" reading. Accepted
weaker wording:
> FedAdam at the validation-selected server rate raises parameter movement 18-70x and, on NSW-Traffic
> only, turns the federated learner into a genuine predictor (17 % better than the best constant, where
> every frozen arm is within 0.5 % of one). On SensorScope and U-Air the same recipe still produces a
> constant-equivalent model that is 44-276 % worse than a constant predictor, so no headroom statement
> about a trained learner can be made there. On traffic the oracle-margin reference does not supply
> positive headroom, but that conclusion rests on 4/5 positive seeds and one extreme negative seed and
> is not robust at n = 5.

## Method - scripts written (all under `_r13_build/`, ASCII only)

| script | what it does | output |
| --- | --- | --- |
| `r13_a_constants.py` | loads every S1' and frozen checkpoint, scores it with the repo's `_predict`/`_mu_weights_for_test`/`rmse_mu` on test/validation, and computes zero/weighted-mean/median/oracle constants on the same units and weights | `r13_a_constants.json`, `r13_a_constants.out.txt` |
| `r13_c_hverify.py` | reproduces every H, bootstrap CI, paired SD and MDE80 from `S1P_STAGE_C_H.json`; recomputes N3' per eta level | `r13_c_hverify.out.txt` |
| `r13_de.py` | split composition and unit overlap; optimiser provenance; movement from logged counters; window/active/K_r recount; mtimes and vintages | `r13_de.out.txt` |
| `r13_movement.py` | `MOVEMENT.csv` vs every checkpoint (incl. frozen rows) | `r13_movement.out.txt` |
| `r13_claim2.py` | frozen movement baselines, the 7-70x arithmetic, `head.8.bias` share decomposition | `r13_claim2.out.txt` |
| `r13_b_selection.py` | per-cell validation (three target-mass recipes) vs test; rank agreement | `r13_b_selection.json` |
| `r13_z.py`, `r13_z2b.py` | seed inventory; gain-vs-zero and gain-vs-constant per arm and family | `r13_z.out.txt`, `r13_z2b.out.txt` |
| `r13_hstab.py`, `r13_boot.py` | leave-one-out H, exact Student-t and jackknife intervals, sign tests | `r13_hstab.out.txt`, `r13_boot.out.txt` |
| `r13_freeze.py`, `r13_hashcheck.py` | the four-freeze chain and the hash-difference test | `r13_freeze.out.txt` |
| `r13_groupmap.py` | proves the driver's group index equals `_predict`'s group index on all 3 blocks (0 mismatches) | stdout |
| `r13_n3.py` | N3' ratios recomputed on the 5-seed basis | stdout |

Exact key expressions:

```
RMSE_mu            = sqrt( sum_i w_i (y_pred_i - y_true_i)^2 ),  w_i = mu_g(i)/count_g(i), normalised to 1
                     (metrics/accuracy.py:52-66; runner._mu_weights_for_test)
best constant      = the weighted test mean  sum_i w_i y_i
H_s                = (fed[s] - sim[s]) / fed[s]           # paired by seed, s in 30001..30005
boot               = [mean(rng.choice(H, 5, replace=True)) for _ in range(10000)], rng = default_rng(20261007)
MDE80(sd, n)       = (t.ppf(.975, n-1) + t.ppf(.80, n-1)) * sd / sqrt(n)
rel_movement       = ||theta_final - theta_init|| / ||theta_init||, theta_init = deterministic_common_ndmf(n_spatial, seed)
                     computed per tensor in float64, summed in squares
```

Reproduce:

```
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe C:\Cursor\raven.mcs\_r13_build\r13_a_constants.py
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe C:\Cursor\raven.mcs\_r13_build\r13_c_hverify.py
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe C:\Cursor\raven.mcs\_r13_build\r13_b_selection.py
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe C:\Cursor\raven.mcs\_r13_build\r13_claim2.py
```

## Three things to do next, in order

1. Retrain `central_delivered` and `central_all` to a matched step budget (O2) and recompute N3'. Until
   then no federated-versus-centralized sentence is licensed.
2. Add the constant-predictor column to every arm table (O1) and re-state the sensorscope/U-Air N3'
   verdicts as PASS-against-a-weak-reference.
3. Report traffic H with median + sign test + leave-one-out, and spend seeds 30006-30020 to see whether
   the outlier seed recurs (O5).
