# Seed-path audit — design and findings (round_v1)

Adjudication experiment for X-4 / record item 36: at U-Air seeds 30007, 30016,
30018 the run-time `RMSE_mu` in the frozen tree differs from a re-evaluation of
the same run's `checkpoints/final.pt`. Which value is the model the run
produced, and which one the published metric definition selects?

Read-only throughout. Nothing outside this directory was written; no training was
run in A0/A1/A2.

## Pre-registered design (fixed before execution)

- **A0** — compare the run-time source revision against the current tree, focused
  on the `model`/`theta` sync and the metric call site. → `A0_CODE_DIFF.md`
- **A1** — sweep every tree that feeds a printed cell; record whether the last
  window is active. → `A1_INACTIVE_FINAL_SWEEP.csv`
- **A2** — recompute `RMSE_mu` from the checkpoint with an implementation written
  from the published definition (`main.tex:1600–1609`), and compare with the
  run-time value, the round's re-evaluated cells, and the public-repro CSV.
  → `A2_PATH_COMPARISON.csv`, script `a2_path_comparison.py`
- **B** (only if A0/A2 leave the mechanism open) — one instrumented rerun of a
  single disputed seed that prints both the live model's and the reloaded
  theta's `RMSE_mu`. Not executed.
- Decision rule: if the divergence is triggered by a condition that the current
  code also exhibits, the paper-conformant value is the one the definition
  selects from the checkpoint; if it is a property of the old revision alone,
  the tree's run-time value stands. No manuscript cell changes before this is
  settled.

## Findings

**A1.** Inactive final windows occur at exactly `{30007, 30016, 30018}` in every
U-Air tree: E3 27/180 runs, E4 12/100, E1 repair 6/86; FedAU and ObsUse 0/20.
**SensorScope has zero inactive-final runs in any tree** (180 + 100 + 20 + 20 + 3
runs), so the natural replication block does not exist and the finding stays
U-Air-only.

**A2.** With the published definition implemented independently (weights
`mu_g / n_g`, one model, 1908 supported test units, weight sum exactly 1):

| tree | arm | seed | last window active | run-time | re-evaluated | relative |
|:---|:---|--:|:---|--:|--:|--:|
| E3 | raven | 30006 | yes | 1.282805 | 1.282805 | 0.0000 % |
| E3 | raven | 30007 | no | 1.142487 | 1.189413 | +4.1073 % |
| E3 | raven | 30016 | no | 1.170926 | 1.152670 | −1.5591 % |
| E3 | raven | 30018 | no | 1.125360 | 1.181723 | +5.0084 % |
| E3 | twostage_hajek | 30007 | no | 1.144180 | 1.186848 | +3.7291 % |
| E3 | twostage_hajek | 30016 | no | 1.224208 | 1.208514 | −1.2819 % |
| E3 | twostage_hajek | 30018 | no | 1.128633 | 1.186398 | +5.1181 % |
| E3 | local_hajek | 30007 | no | 1.145170 | 1.193597 | +4.2288 % |
| E3 | local_hajek | 30016 | no | 1.167526 | 1.144226 | −1.9957 % |
| E3 | local_hajek | 30018 | no | 1.123620 | 1.178757 | +4.9071 % |
| **E1** | **raven** | 30007 | no | **1.142487** | **1.189413** | +4.1073 % |
| **E1** | **raven** | 30016 | no | **1.170926** | **1.152670** | −1.5591 % |
| **E1** | **raven** | 30018 | no | **1.125360** | **1.181723** | +5.0084 % |
| **E1** | **twostage_hajek** | 30007 | no | **1.144180** | **1.186848** | +3.7291 % |
| **E1** | **twostage_hajek** | 30016 | no | **1.224208** | **1.208514** | −1.2819 % |
| **E1** | **twostage_hajek** | 30018 | no | **1.128633** | **1.186398** | +5.1181 % |

Four consequences:

1. **The independent implementation reproduces the round's re-evaluated cells
   exactly** (compare with `E2_UAIR_CELLS.csv`, column shown in the CSV), so the
   comparison is not circular.
2. **The trigger is the inactive final window, not the seed number and not the
   tree.** Control seeds with an active final window agree to 0.0000 %.
3. **The E1 repair tree — produced by the current code a month later — shows the
   same divergence**, and its run-time values are bit-identical to the E3 tree's.
   So the divergence is *reproducible in the current code*; it is not a property
   of the old revision.
4. Therefore neither "old code" nor "stale checkpoint in one tree" explains it.
   What remains is the question the design parked in Stage B: which model the
   run-time metric evaluates when the final window does not aggregate. Stage B
   needs one instrumented rerun and was not executed.

**Stake if the re-evaluated path turns out to be the conformant one**: the
20-seed means of the U-Air Design-on rows move by about +0.34 % to +0.37 %
(`raven` 1.191114 → 1.195366, `inst_cal` → 1.195374, `local_hajek` 1.188238 →
1.192251, `twostage_hajek` → 1.220198, `raven_simoracle` → 1.195830), so every
derived percentage that uses those rows has to be recomputed, and the Local-Hájek
question in X-4 has to be re-answered on consistent numbers.

## Stage B — executed, decisive

`b_two_copy_capture.py` reran U-Air / raven / seed 30007 through the production
path (`run_e3_real`, condition `C0_frozen`, sealed trace) with `_predict` wrapped
so that at metric time it records both copies in one process. The rerun is on the
same trajectory: its `RMSE_mu` is `1.1424870864095478`, identical to the frozen
tree, and **its checkpoint is byte-identical to the frozen one**
(`sha256 da0edc1924b533c5…`).

`B_TWO_COPY_CAPTURE.json`:

| quantity | value |
|:---|:---|
| max abs(model parameter − theta parameter) | **0.03477** (all 13 parameters differ; largest in `head.8.bias`) |
| RMSE_mu from the live `runner.model` | **1.1424870864095478** — equals the frozen tree's stored value |
| RMSE_mu from a fresh module loaded with `runner.theta` | **1.189412616781117** — equals the E2 cell, the public-repro CSV and the independent implementation |
| max abs per-unit prediction difference | 0.07071 |
| test units / weight sums | 1908 / 1.0 and 1.0 |
| last window | id 79, **inactive**; 75 active windows |

So the divergence is not a weighting, unit-set or precision effect: **the run-time
metric evaluates the in-memory module, which at that moment is not the parameter
vector the run saves.** `theta` is the state the algorithm updates
(`theta_{r+1} = theta_r − eta Σ alpha u`), the object written to
`checkpoints/final.pt`, the object a resumed or deployed run would use, and the
object every downstream consumer evaluates (E2 cells, public-repro bundle,
appendix audit, the independent implementation here). The module is the mirror,
and with an inactive final window the two are not equal at metric time.

**Verdict (per the pre-registered rule, case 1):** the paper-conformant value is
the `theta` copy; the three cells stored in the frozen tree at seeds
30007/30016/30018 carry the mirror's value and are superseded. This also means the
route-A round's G1c ruling ("the E3 tree is the source, the public-repro CSV is
the outlier") was drawn from the mirror-based numbers and does not hold at those
three seeds.

### Exact scope of affected cells (from A1 + the tree layout)

| tree | affected arms (inactive final window at 30007/16/18) | clean arms |
|:---|:---|:---|
| E3 (U-Air) | **all nine**: fedavg_window, fedasync_window, flamf_timealign_adapted, debt_cal, inst_cal, local_hajek, raven, raven_simoracle, twostage_hajek | central_all, central_delivered |
| E4 (U-Air) | raven_wo_debt, raven_wo_inst, raven_wo_obs, raven_wo_use | **raven_wo_design** (the Design-off comparator) |
| E1 repair (U-Air) | raven, twostage_hajek (G1c's reruns only) | the four rebuilt printed rows |
| FedAU / ObsUse (U-Air) | — | fedau_window, obsuse_window |
| every SensorScope tree | — | all arms |

Printed cells therefore affected: Table III's U-Air **RAVEN-Design** row;
`tab:app_e3_uair`'s five Design-on rows; and the U-Air ablation rows in Table IV
that use `raven_wo_{inst,obs,use,debt}`. Clean: Table III SensorScope, U-Air
FedAvg/TwoStage/FedAU/ObsUse/**RAVEN-NoDesign**, the four rebuilt appendix rows,
the central reference rows, and the FedAU/ObsUse trees.

Impact if re-sourced: the 20-seed means of the five U-Air Design-on rows move by
**+0.338 % to +0.372 %** (raven 1.191114 → 1.195366, inst_cal → 1.195374,
local_hajek 1.188238 → 1.192251, twostage_hajek 1.215961 → 1.220198,
raven_simoracle 1.1914 → 1.195830), so every percentage derived from them has to
be recomputed, and X-4's Local-Hájek question re-answered on consistent numbers.

## Threats to validity

- SensorScope has no inactive-final run, so there is no replication block.
- The run-time revision of `e3/real_runner/runner.py` was not recovered; A0
  cannot inspect the metric call site of the actual run.
- Stage B observes a *reproduction* of the live model, not the original object.
- The A2 implementation shares the model/feature path with the run (it must, to
  be comparable); only the metric assembly is independent.
