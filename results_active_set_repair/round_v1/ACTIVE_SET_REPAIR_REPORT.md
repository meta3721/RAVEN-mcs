# Training active-set repair (route A) — execution report

```text
Contract:   raven-mcs-active-set-repair-design.md (Claude), executed verbatim except where
            flagged in SS0 and SS8 below.
Mode:       executed. G0 inventory, G1a-G1d gates (12 runs), E1 rebuild (80 runs),
            E2 re-evaluation, E3 downstream recomputation all completed 2026-09-27.
Driver:     scripts/run_active_set_repair.py (new, this round).
Outputs:    results_active_set_repair/round_v1/ only.
Boundary:   no src/ change, no frozen tree overwritten, no .tex edit, no table cell
            replaced, no commit. Verified: every frozen value read in this report was
            re-read from its stored artifact and matched.
Cost:       92 training runs total (12 gates + 80 E1); ~35 min wall clock on CPU.
```

---

## 0. TOLERANCE AMENDMENT — flagged as instructed

**The plan's G1a gate failed as written, and was executed under an amended tolerance with the
user's explicit authorization. This is the only gate whose pass rule was changed.**

| item | plan | as executed |
|:---|:---|:---|
| G1a pass rule | "final metrics bit-equal to the frozen tree" (tolerance `1e-9`) | `abs_diff <= 1e-6` |
| G1a failure action | **stop** — "a rebuild would confound two changes" | not taken; user authorized continuation |

**What failed.** SensorScope `debt_cal` seed 30001, the one cell of the 12 gates that is not
bit-exact:

| | value |
|:---|:---|
| frozen (`artifacts/e3_formal_runs_r1/runs/sensorscope/debt_cal/seed30001`) | `7.915297744846339` |
| current runner | `7.915297538076236` |
| \|diff\| | **`2.0677010326153322e-07`** (relative `2.61e-08`) |

**Why it is not a confound** (`G1_DEBT_CAL_DIAG.json`):

1. It is **deterministic, not flaky**. Three independent measurements return the identical
   `7.915297538076236`: `debt_cal` as the **first** `run_arm` call in a fresh process
   (`repair_solo`), a second call in the same process (`repair_again`), and the
   **third**-in-process call inside the original G1a sequence. So it is not in-process state
   leakage and not run-to-run noise; it is a fixed frozen-versus-current runner difference.
2. It is **5x below `1e-6`**, the tolerance that the plan's *own* E2 reference routine
   (`audit_table2_uair_fedavg.block_rmse`) is verified against (plan SS7 E2: "already verified
   against the per-seed file at 1e-6"). The plan is internally inconsistent in demanding `1e-9`
   at G1a while relying on `1e-6` at E2.
3. Its relative size is **`2.6e-08`**, roughly **10^6 times smaller** than the ~6.3 % active-set
   effect E1 exists to measure (SS3 below). It cannot move any conclusion at the reported
   precision.
4. E1's four rebuilt rows are compared **against each other and against RAVEN-NoDesign from the
   new batch**. The frozen `debt_cal` value is only the old cell being replaced, so the drift
   does not enter the comparison at all.

**Authorization:** user, 2026-09-27, verbatim: *"放宽容错，执行E1，然后写进实验报告，特别将其注明"*.
Recorded in `G1_REPORT.json["amendment"]` and in the driver as the `G1A_TOL` constant with the
same grounds. **Anyone reading R1-R4 must treat the `debt_cal` G1a arm as reproduced to `1e-6`,
not bit-exactly.**

---

## 1. G0 — inventory (no training): `ACTIVE_SET_INVENTORY.csv`, `PI_TAR_HOLES.csv`

`pi^tar` was rebuilt through the runner's own path
(`apply_sealed_opportunity_stratum` -> `build_pi_target(..., split="test")`) over the `pi^opp`
(client x stratum) support:

| block | strata | support pairs | zero `pi^tar` | share | plan SS2 claim | match |
|:---|--:|--:|--:|--:|:---|:--:|
| `uair` | 288 | 288 | **72** | **25.0 %** | "72 of 288" | ✓ |
| `sensorscope` | 440 | 440 | 0 | 0 % | "0/440" | ✓ |
| `traffic` | 32 | 344 | 0 | 0 % | "0/344" | ✓ |
| `tdrive_speed` | — | — | — | — | "not counted" | **NOT_COUNTED** |

Realized active sets vs frozen `fedau_window` (full delivery) on the same seed and window, over
all 640 stored `window_metrics.json` (16 methods x 20 seeds x 2 blocks):

| block | class | methods | windows identical to FedAU | mean active clients |
|:---|:---|:---|--:|--:|
| SensorScope | all 16 | full + design | **2000 / 2000** | 2.4245 |
| U-Air | `full` (licensed = full delivery) | `fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `debt_cal` | **826 / 1600** | **1.8269** |
| U-Air | `full`, clean batch | `fedau_window`, `obsuse_window`, `raven_wo_design` | **1600 / 1600** | **2.4500** |
| U-Air | `design_support` (licensed = restricted) | `local_hajek`, `twostage_hajek`, `inst_cal`, `raven`, `raven_simoracle`, 4 E4 arms | 826 / 1600 = licensed | 1.8269 |

**Verdict: 80 violations = 4 no-Design methods x 20 seeds, all on U-Air.** The plan's SS2 numbers
reproduce exactly (1.827 / 826-1600 / 2.450 / 1600-1600 / 2000-2000). SensorScope's Design-on rows
also read 2000/2000 because with zero `pi^tar` holes the restriction is a no-op there — consistent,
not a contradiction.

---

## 2. G1 — reproduction gates (12 runs): `G1_REPORT.json`

| gate | runs | result |
|:---|--:|:---|
| **G1a** | 3 | `fedasync_window` **0.0** ✓, `flamf_timealign_adapted` **0.0** ✓, `debt_cal` **2.07e-07** → **pass under the SS0 amendment** |
| **G1b** | 1 | `central_delivered` U-Air **0.0** ✓ → Central rows stay unchanged |
| **G1c** | 6 | **6/6 match the E3 tree bit-exactly; 0/6 match the public-repro CSV** |
| **G1d** | 2 | `fedavg_window` U-Air 30001 / 30006 both match `results_table2_audit` (2e-16, i.e. float noise) |
| **G2** | 6 | **NOT EXECUTED** — see SS8 |

**G1c resolves record item §2A N3.** The three seeds where the E3 tree and the public-repro CSV
disagree (30007 / 30016 / 30018) were re-run for both Design-on methods:

| method | seed | E3 tree | current runner | repro CSV | reproduces |
|:---|--:|:---|:---|:---|:---|
| `raven` | 30007 | 1.1424870864095478 | **1.1424870864095478** | 1.18941261605731 | **tree** |
| `raven` | 30016 | 1.1709258951551238 | **1.1709258951551238** | 1.1526704437327764 | **tree** |
| `raven` | 30018 | 1.125360082508588 | **1.125360082508588** | 1.1817229910128095 | **tree** |
| `twostage_hajek` | 30007 | 1.1441802550200664 | **1.1441802550200664** | 1.1868478786334546 | **tree** |
| `twostage_hajek` | 30016 | 1.2242075631780656 | **1.2242075631780656** | 1.2085144491379751 | **tree** |
| `twostage_hajek` | 30018 | 1.1286332988862726 | **1.1286332988862726** | 1.186397524006943 | **tree** |

Per the plan's G1c rule, **the E3 run tree becomes the single source for every Design-on U-Air
row**, and it is what E2 uses. Combined with the earlier finding that Table III's printed `1.1882`
*is* the tree's ALL20 mean `1.188238`, the public-repro per-seed CSV is the outlier artifact at
those three seeds. `abs_diff = 0.0` at all six re-runs is the strongest available statement.

---

## 3. E1 — rebuild on the licensed set (80 runs): `E1_RUNS.csv`, `E1_ASSERTIONS.csv`

Per-run assertion, checked before metrics were read: realized `active_clients` equals frozen
`fedau_window`'s on the same seed and window.

| method | windows compared | identical | expected |
|:---|--:|--:|:---|
| `fedavg_window` | 1600 | **1600** | 1600/1600 |
| `fedasync_window` | 1600 | **1600** | 1600/1600 |
| `flamf_timealign_adapted` | 1600 | **1600** | 1600/1600 |
| `debt_cal` | 1600 | **1600** | 1600/1600 |

No assertion fired. **All four rebuilt methods now train on exactly FedAU's full-delivery set.**

**Cell movement — the four affected U-Air rows (20 seeds):**

| method | old (Design-filtered) | new (licensed) | abs | relative |
|:---|:---|:---|:---|--:|
| FedAvg-Window | 1.188238 | **1.111932** | −0.076305 | **−6.4217 %** |
| FedAsync-Window | 1.188279 | **1.111924** | −0.076356 | **−6.4257 %** |
| TimeAlign-Agg | 1.188435 | **1.112002** | −0.076433 | **−6.4314 %** |
| Debt-Cal | 1.189318 | **1.114378** | −0.074940 | **−6.3011 %** |

**All four move by −6.30 % to −6.43 %.** Four different aggregation rules — plain averaging,
staleness-penalized, FLAME-timealign and debt-calibrated — shift by the same amount. A
method-independent shift of that uniformity is the cleanest possible confirmation that the cause
is the **active set**, not any method's behaviour.

**Independent cross-check.** E1's rebuilt FedAvg `1.111932` reproduces the earlier, separately
produced `results_table2_audit/uair_fedavg_current_per_seed.csv` mean `1.1119` to four decimals.
Two independent rebuilds agree.

---

## 4. E2 — single-batch re-evaluation: `E2_UAIR_CELLS.csv`, `E2_UAIR_SUMMARY.csv`

Every printed U-Air row re-evaluated from **one** checkpoint source per row; `RMSE_mu` and the four
block RMSEs recomputed from saved checkpoints, `WorstGroupRMSE = max` of the four blocks; both
domains stored.

### Table R1 — U-Air, no-Design family on the licensed set (20 seeds, std domain)

| method | `RMSE_μ` | `WorstGroupRMSE` | `Δ_group` | `Δ_c-s` | source |
|:---|:---|:---|:---|:---|:---|
| FedAvg-Window | 1.111932 ± 0.0603 | 1.169045 ± 0.0692 | 1.044620 | 1.313777 | E1 |
| FedAsync-Window | 1.111924 ± 0.0599 | 1.169044 ± 0.0688 | 1.045149 | 1.313666 | E1 |
| TimeAlign-Agg | 1.112002 ± 0.0597 | 1.169134 ± 0.0685 | 1.044768 | 1.314519 | E1 |
| Debt-Cal | 1.114378 ± 0.0645 | 1.171764 ± 0.0741 | **1.017533** | **1.294779** | E1 |
| FedAU-Window | 1.112813 ± 0.0600 | 1.170075 ± 0.0689 | 1.055671 | 1.329103 | frozen tree |
| ObsUse-Window | 1.112034 ± 0.0600 | 1.169211 ± 0.0689 | 1.041296 | 1.323475 | frozen tree |
| **RAVEN-NoDesign** | **1.113059** ± 0.0638 | **1.170275** ± 0.0734 | **1.016515** | **1.294934** | E4 tree |

Physical domain (`RMSE_mu_phys = *_std x 17.36325121670317`), 20-seed means: FedAvg 19.306761,
FedAsync 19.306615, TimeAlign 19.307969, Debt-Cal 19.349231, FedAU 19.322047, ObsUse 19.308533,
RAVEN-NoDesign **19.326325**.

**The no-Design family on prediction is a six-way tie.** Spread across FedAvg / FedAsync /
TimeAlign / FedAU / ObsUse / RAVEN-NoDesign is `1.1119`-`1.1131`, i.e. **0.11 %**. Debt-Cal is the
only row that separates, at `1.1144` (+0.22 %).

**Two exact confirmations of the N7 scale arithmetic** (independent rows, not the one used to
derive sigma):

| row | E2 physical domain | sealed `TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv` | match |
|:---|:---|:---|:--:|
| U-Air Central-All | **18.328143** | 18.328143 | ✓ |
| U-Air Central-Delivered | **20.456610** | 20.456610 | ✓ |

So the sealed table source **is** the physical domain of the same quantities the manuscript prints
in the standardized domain. `N7` is arithmetic-confirmed, not merely inferred.

---

## 5. E3 — downstream recomputation: `P2_COVERAGE.csv`, `PAIRED_STATS.csv`

### `tab:app_p2_coverage`, U-Air row, with the four rebuilt methods substituted

The published row was built from the 180-run U-Air windowed set (9 methods x 20 seeds; central
methods have no `window_metrics.json`). "Active windows" = windows with `active == true`. The
definition was first validated by reproducing **both** published rows exactly from the untouched
trees: U-Air `70.1000 / 63-75` (published `70.10 / 63-75`) and SensorScope `93.8500 / 88-98`
(published `93.85 / 88-98`).

| set | per-method mean active windows | recomputed row |
|:---|:---|:---|
| 4 rebuilt methods | **75.75** each (min 73, max 79) | — |
| 5 unchanged methods | 70.10 each (min 63, max 75) | — |
| **substituted total** | — | **runs 180, mean 72.6111, range 63-79** |
| published | — | runs 180, mean 70.10, range 63-75 |

**The substitution moves the U-Air row: mean `70.10` -> `72.6111`, max `75` -> `79`.** All four
rebuilt methods gain 5.65 active windows per run, because on the licensed set they see the full
delivered client set rather than the Design-filtered one.

### Table R2 — paired RAVEN-NoDesign minus comparator, relative (plan SS8, pre-registered)

t-intervals on n-1 df; Holm across the six comparators within each metric and slice.
Bold = interval excludes 0 and the ALL20 point estimate agrees in sign.

| comparator | `RMSE_μ` (TEST / ALL20) | `WorstGroupRMSE` | `Δ_group` (TEST / ALL20) | `Δ_c-s` |
|:---|:---|:---|:---|:---|
| FedAvg-Window | +0.545 % (3/10) / +0.089 % (7/20) | +0.581 % / +0.090 % | **−3.078 % / −2.711 %** (20/20) | **−1.360 % / −1.424 %** |
| FedAsync-Window | +0.604 % (3/10) / +0.089 % (8/20) | +0.644 % / +0.088 % | **−3.117 % / −2.760 %** (20/20) | **−1.348 % / −1.416 %** |
| TimeAlign-Agg | +0.560 % (3/10) / +0.080 % (8/20) | +0.596 % / +0.079 % | **−3.091 % / −2.722 %** (20/20) | **−1.405 % / −1.480 %** |
| **Debt-Cal** | −0.124 % (6/10) / −0.115 % (12/20) | −0.134 % / −0.124 % | **−0.052 % / −0.089 %** (10/20) — **not significant** | −0.055 % / +0.015 % — tie |
| FedAU-Window | +0.449 % (3/10) / +0.011 % (10/20) | +0.478 % / +0.002 % | **−3.942 % / −3.733 %** (20/20) | **−2.662 % / −2.553 %** |
| ObsUse-Window | +0.422 % (3/10) / +0.080 % (9/20) | +0.443 % / +0.075 % | **−2.532 % / −2.403 %** (20/20) | **−2.296 % / −2.143 %** |

Holm-adjusted p: `RMSE_μ` and `WorstGroupRMSE` are **non-significant against every comparator**
(min Holm p 0.69 and 0.72 respectively, TEST). `Δ_group` and `Δ_c-s` are significant against five
of six (Holm p `1.9e-5`-`7.5e-4` for `Δ_group` and `3.5e-4`-`6.5e-4` for `Δ_c-s`, TEST;
`≤1.7e-6` ALL20) and **not against Debt-Cal** (Holm p `0.71` and `0.67` TEST; `0.41` and `0.90`
ALL20).

### The pre-registered analysis outcome

The plan's SS8 wording rule: *"The `Δ_group` claim is stated as unqualified only if it holds
against all six comparators. Otherwise the text names the comparators it holds against and the
ones it does not."*

**It does not hold against all six.** Debt-Cal — the one no-Design comparator that also carries
instant calibration, a reference penalty and debt, whose frozen restricted `Δ_group` was `1.0976`
against NoDesign's `1.0165` — **removes the `Δ_group` advantage** once both are on the licensed
set: `1.017533` versus `1.016515`, a relative `−0.089 %` with a t-interval spanning zero.
The plan pre-registered this as "the open risk" and it materialised.

Consequences for the manuscript, per the plan's own wording rule:

- The `Δ_group` claim **must be qualified**: RAVEN-NoDesign beats FedAvg, FedAsync, TimeAlign,
  FedAU and ObsUse on `Δ_group` by 2.4-3.7 % (20/20 seeds each), and **ties Debt-Cal**.
- The `Δ_c-s` claim has the same shape: significant against five, tie against Debt-Cal.
- On prediction RAVEN-NoDesign is a **tie-to-slightly-worse** against all six (point estimates
  from −0.12 % to +0.60 %), with no significant difference in either direction.
- The old sentence "improves on TwoStage-Hájek and FedAvg (TEST −6.17 % and −9.11 %)" is
  **superseded**: those were `WorstGroupRMSE` paired TEST relatives against the contaminated
  batch, and the rebuilt comparison shows `+0.581 %` (vs FedAvg) on that same metric.

---

## 6. Table R3 — gates

| gate | runs | result |
|:---|--:|:---|
| G1a | 3 | 2 bit-exact `0.0`; `debt_cal` `2.0677e-07` → **pass under the SS0 amendment (`1e-6`)** |
| G1b | 1 | bit-exact `0.0` |
| G1c | 6 | **6/6 reproduce the E3 tree, 0/6 the repro CSV** → tree is the single source |
| G1d | 2 | both match `results_table2_audit` (2e-16) |
| G2 | 6 | **NOT EXECUTED** — see SS8 |

## 7. Table R4 — cell-replacement map (for the user's authorization; nothing replaced)

| manuscript location | cell(s) | old | replaced by | new |
|:---|:---|:---|:---|:---|
| Table III, U-Air FedAvg-Window | 4 | 1.1882 / 1.2596 / 1.1218 / 1.2621 | R1 FedAvg | **1.1119 / 1.1690 / 1.0446 / 1.3138** |
| `tab:app_e3_uair` | FedAvg, FedAsync, TimeAlign, Debt-Cal rows | 1.1882-1.1893 | R1 | **1.1119-1.1144** |
| `tab:app_e3_uair` | Design-on rows | — | unchanged (G1c selected the tree) | — |
| `tab:app_block_rmse`, UA FedAvg-Window | 5 | tree values | E2 | `E2_UAIR_CELLS.csv` |
| `tab:app_p2_coverage`, U-Air | 3 | 180 / 70.10 / 63-75 | E3 | **180 / 72.6111 / 63-79** |
| prose: "improves on ... FedAvg (TEST −6.17 %)"; Local-Hájek coincidence sentence | prose | — | R2 wording rule; "coincides with FedAvg restricted to the Design support" | — |

The `local_hajek` explanatory sentence: the rebuild shows `local_hajek` is unchanged and remains
`1.192251 / 1.1218 / 1.2621` — identical to the old contaminated `fedavg_window`. Its policy sets
`uses_design_ratio=True`, so its restricted active set is **licensed**, and its identity is an
identity with **FedAvg restricted to the Design support**. Only the sentence changes.

---

## 8. Deviations from the plan, and blockers

Executed verbatim except for the four items below. Each is a plan defect, not a shortcut.

1. **G1a tolerance amended** — SS0 above. The only changed pass rule.
2. **G2 cannot be executed as written.** The plan's G2 specifies 6 runs of `fedavg_window`,
   `fedau_window`, `obsuse_window` on City Scanner 32001 and Pilot 2 33001 "with active-set
   logging; metrics bit-equal to the frozen ledger **and** logged `A_r` equals full delivery".
   - `load_paper_dataset` supports only `sensorscope`, `uair`, `traffic`, `tdrive*`. City Scanner
     (`cityscanner_nyc_pm25`) and Pilot 2 (`cityscanner_nyc_p2_measured_o`) are served by separate
     modules (`src/raven_mcs/data/cityscanner*.py`) through different drivers
     (`scripts/run_path_a_no2.py`, `scripts/run_joint_ou_cs_p2.py`).
   - Their frozen runs live under `results_c1_cityscanner/round_v1/runs/` and
     `results_joint_ou/round_v1/runs/` with `CS_ACCEPTED.json` / `JO_ACCEPTED.json` ledgers and
     **no `window_metrics.json`**, so `A_r` cannot be read from stored artifacts — which the plan
     itself notes in SS2 item 4.
   - Producing the required `A_r` log needs instrumentation inside those drivers, which the plan's
     SS14 boundary ("no `src/` change") excludes. **Outcome: 0 of 6 G2 runs executed; City Scanner,
     Pilot 2 and T-Drive remain `unverified` exactly as the plan's SS2 item 4 already recorded.**
   - Reported in `G2_REPORT.json` with the ledger probes.
3. **T-Drive `pi^tar` hole count is `NOT_COUNTED`, not a number.** The plan's G0 asks for it, but
   `load_spatial_to_client` has no `tdrive` branch (`dataset_load.py:76-85`) so the runner's
   `pi^tar` support cannot be rebuilt for that block, and no stored hybrid `pi^tar` artifact exists
   under `results_tdrive_rank/` or `manuscript_evidence_closure_r1/09_tdrive_decision/`. T-Drive is
   outside route A's rebuild set. Recorded as `NOT_COUNTED` with the reason rather than guessed.
4. **The plan's E2 note about `store_fields` is factually wrong.** Plan SS7 E2 says `*_std`/`*_phys`
   "fills the `store_fields` contract that `metric_scale_policy.json` declares and **no run
   currently honours**". In fact **every run already honours it**, in
   `final_metrics_dual_domain.json` (`RMSE_mu_std`, `RMSE_mu_phys`, `MAE_mu_std`, `MAE_mu_phys`,
   `Tail_RMSE_*`, `Head_RMSE_*`, `RMSE_rho_*`), e.g. U-Air `fedavg_window` seed 30001:
   `RMSE_mu_std = 1.210848`, `RMSE_mu_phys = 21.024266`. E2's physical values in SS4 were therefore
   an arithmetic cross-check, not a contract repair. (This claim was inherited from record item
   `N7`, whose third clause has since been corrected.)

---

## 9. What this report does not establish

- **No manuscript file was touched and no table cell replaced.** R4 is a proposal awaiting the
  user's authorization.
- **City Scanner, Pilot 2 and T-Drive active sets remain unverified** (SS8 item 2-3). No claim in
  this report covers the hybrid blocks.
- **`debt_cal` G1a is reproduced to `1e-6`, not bit-exactly.** The residual `2.07e-07` is
  deterministic and unexplained at the code/version level; the frozen batch's producing runner
  version was never committed, so bisection is not available.
- **`Δ_group` and `Δ_c-s` for the rebuilt rows come from each run's own `final_metrics.json`**, not
  recomputed from checkpoints; only `RMSE_μ` and `WorstGroupRMSE` were recomputed
  (`E2_UAIR_CELLS.csv`). The plan's SS7 E2 named those two as the recomputation targets, so this is
  as specified.
- **No Holm correction across metrics** — Holm was applied across the six comparators within each
  metric and slice, as the plan's SS8 specifies.
- **The `WorstGroupRMSE` recomputation path inherits `audit_table2_uair_fedavg.block_rmse`**, which
  is verified against the per-seed file at `1e-6`; the Central rows required an added unwrap
  (`{"state_dict", "method", "seed"}`) in this driver only.

**Next CCFA owner (plan SS16):** `ccf-integrity-auditor` to check R1-R4 against the run trees, then
`ccf-paper-writer` for the R4 prose — after the user authorizes the cell replacements.
