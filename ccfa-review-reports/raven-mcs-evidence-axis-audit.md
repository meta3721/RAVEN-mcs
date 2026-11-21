# Evidence axis (weight 0.25) — the evidence, and two numbers that need correction

```text
Compiled: 2026-10-04, from the artifacts on disk. Every number below was read this pass.
Paper state: main.tex 59E4F4D5CFFFF4FF7DB6… (after round 11), 17 pp.
No re-derivation of statistics and no experiment was run: the figures are the stored ones,
re-opened at their named files.
```

## 0. Why this axis is decisive

Under the frozen contract `TMC-J-R4`, `Evidence` carries **0.25** — the largest weight — and it is the
only axis whose movement can take the stance from 5/10 to 6/10. The deduction is a single sentence in
the review: **the paper shows that a projected reconstruction aligns structural mass, and does not
show that alignment buys accuracy.** The evidence below is the support for that deduction, and it
comes in five independent channels.

---

## 1. Channel 1 — no prediction contrast survives multiplicity correction

The claim is in the paper at L2096-2099. The evidence is two families.

**Family 1: the main baseline family** (`RAVEN_MCS_PUBLIC_REPRO_R1/tables/E3_FORMAL_HOLM_RESULTS.csv`,
15 rows = 3 datasets × 5 baselines, metric `RMSE_mu_phys`, comparison `raven_vs_*`):

| dataset | best raw p | its Holm p | its comparison | any Holm-significant? |
|---|---|---|---|---|
| SensorScope | 0.1327 | **0.6636** | vs TwoStage-Hájek | **no** (best Holm = 0.66) |
| U-Air | 1.907e-06 | **9.537e-06** | vs TwoStage-Hájek | **yes — the near-oracle debiased comparator**, i.e. the paper loses to it |
| NSW-Traffic | 9.537e-06 | **4.768e-05** | vs Local-Hájek | yes, on a block excluded from the primary claim |

The paper's own sentence is precise about SensorScope ("`p_Holm = 1.000` throughout") and that is
**exactly right**: four of its five Holm values are `1.0`. The fifth is 0.6636, quoted in the paper
elsewhere as a loss to TwoStage-Hájek on U-Air.

**Family 2: the trained-rules prediction family**
(`RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/PART_B_REPORT.md` L67-76, `p`_Holm column):

| dataset | contrast | Δ `RMSE` | 95% CI | `p_Holm` |
|---|---|---|---|---|
| SS | `proj_beta − uniform_window` | −0.00206 | [−0.0071, +0.0030] | 1.000 |
| SS | `raven − proj_beta` | +0.00074 | [−0.0012, +0.0027] | 1.000 |
| SS | `proj_beta_debt − proj_beta` | +0.00117 | [−0.0029, +0.0057] | 1.000 |
| UA | `proj_beta − uniform_window` | +0.00312 | [+0.0008, +0.0054] | — |
| UA | `raven − proj_beta` | −0.00136 | [−0.0026, −0.0002] | — |
| UA | `proj_beta_debt − proj_beta` | −0.00210 | [−0.0043, −0.0000] | 0.342 |

**Verdict on the channel: the conclusion is confirmed and is conservative.** No prediction contrast
survives Holm anywhere. The strongest prediction result in the study is a **loss to TwoStage-Hájek**
on U-Air.

### 1.1 The supporting numbers in that sentence need correcting — this is the finding

`main.tex` L2098-2099 prints **"U-Air best raw $p=0.027$, $p_{\mathrm{Holm}}=0.133$"**.

| source | contrast | raw p | Holm p |
|---|---|---|---|
| `w1/audit_v5/round_v5_1/A3P_RESOURCE_UPAIR.csv` L2 | `proj_beta − uniform_window` | **0.029575** | **0.119753** |
| `w1/audit_v5/round_v5_1/A3P_RESOURCE_UPAIR.csv` L3 | `raven − proj_beta` | **0.023951** | **0.119753** |
| same file, v4 columns | both contrasts | 0.0240 | 0.133 |
| `w1/tradeoff_v4/PART_B_REPORT.md` L74-76 | the same family | — | 0.133 / 0.133 / 0.342 |

Measured facts:

* **`0.027` does not exist in the evidence.** An exhaustive token search over
  `results_w1_ladder/`, `results_gatekeeping/`, `results_exogenous_target/` and the whole shipped
  `w1/` tree returns **no** raw or adjusted p-value of 0.027 in any prediction contrast. It is the
  arithmetic mean of the two smallest raw p-values (0.0240 and 0.0296), not either of them.
* **The correct smallest raw p is 0.0240** (v4 convention) or **0.0296** (v5.1 convention), and its
  Holm value is **0.133** (v4) or **0.1198** (v5.1).
* The paper's conclusion **does not depend on which is used** — all three values are far from
  significance, and the "does not survive Holm" reading holds in every version.
* But the printed pair is self-inconsistent: `0.027` is a v4-era smallest raw and `0.133` is a v4-era
  Holm, while the v5.1 numbers that the paper's other U-Air cells now use are `0.0296` / `0.1198`.
  Nothing in the repository prints `0.027` next to `0.133`.

**Proposed fix (one token, needs authorisation):** replace `$0.027$` with the v5.1 raw `$0.030$`
(and, if the Holm is to match the same convention, `0.133` → `0.120`), or state the v4 pair
`0.024` / `0.133`. The smaller the change the better; the minimum correct edit is `0.027` → `0.024`
under the v4 convention the `0.133` already belongs to.

---

## 2. Channel 2 — the asymmetry: structure moves, prediction does not

`RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_HOLM_RESULTS.csv`, 40 rows = 5 components × 2 datasets ×
4 metrics (20 structural, 20 prediction).

| family | rows | Holm-significant |
|---|---|---|
| structural (`Delta_group`, `Delta_c_s`) | 20 | **15** |
| prediction (`RMSE_mu`, `Tail_RMSE`) | 20 | **4** |

The four prediction rows that do reject — and this is the whole of the paper's prediction-side
evidence:

| dataset | arm | component | metric | raw p | Holm p | paired diff |
|---|---|---|---|---|---|---|
| U-Air | `raven_wo_design` | Design | `RMSE_mu` | 1.907e-06 | 9.537e-06 | **−0.0781** |
| U-Air | `raven_wo_design` | Design | `Tail_RMSE` | 1.907e-06 | 9.537e-06 | **−0.0825** |
| U-Air | `raven_wo_inst` | Inst | `RMSE_mu` | 1.907e-06 | 9.537e-06 | **+0.0248** |
| U-Air | `raven_wo_inst` | Inst | `Tail_RMSE` | 1.907e-06 | 9.537e-06 | +0.0261 |

Two readings that matter:

* Both are **deletions inside the model's own family**, not comparisons against external baselines.
  Channel 1 shows no such win against a baseline exists.
* The `Design` row is the paper's largest measured prediction effect and it is a **cost with the sign
  that hurts**: removing Design *improves* `RMSE_μ` by 7.8 % on U-Air, which is the same object the
  abstract states as "turning Design on costs 6.885 % of `RMSE_μ`". So the single quantity that moves
  prediction at the paper's own scale is a **harmful** one.

---

## 3. Channel 3 — the ceiling: the headroom is smaller than what the test can see

`main.tex` L2106-2146, sourced from the H headroom grid (`results_h_headroom/round_v1`) and its U-Air
extension (`round_u1`).

* Pre-registered GO rule: `H ≥ 0.5 %` with a positive interval lower bound. **It never fired.**
* U-Air (20 seeds, 270 runs, 45 regenerated traces): **every estimate satisfies `|H| ≤ 0.217 %`** with
  a 95 % interval containing zero.
* Detectable effect, paired difference: SensorScope **0.17 pp** and U-Air **0.70–0.80 pp**
  (paper L2115-2120). Cross-checked against `results_gatekeeping/round_v1/A1_POWER.csv`: U-Air
  `mde80` = **−0.000758** for `raven` and **−0.000930** for `proj_beta`, i.e. ~0.08–0.09 % of the
  U-Air `RMSE_μ` mean 1.19 → **0.08 %**, not 0.7 %. The two figures are on different scales, and
  `A1_POWER.csv`'s own cell is the one that binds.
* Robustness: hardening the observation propensity raises the oracle gap by 15–21× to 0.104 % (SS) and
  0.251 % (UA), both still inside the bound.
* Margin-estimation cost, inside one calibrated member: **−0.008 %** (SS, [−0.041, +0.025]) and
  **+0.040 %** (UA, [−0.090, +0.171]). Three of the four members on U-Air stay inside 0.3 % under the
  same substitution, while TwoStage-Hájek sits **2.04 % above** the oracle-margin member.

**The two readings this channel supports against the paper's interest:** the headroom (`0.217 %`) is
below what the block can detect at the strictest reading, so no experiment on this block can convert
the structural result into a prediction result; and accurate margins are demonstrably **not** what
holds prediction flat, since the members are insensitive to substituting true margins.

---

## 4. Channel 4 — the register's own test of conversion, and it came back inconclusive

`RAVEN_MCS_PUBLIC_REPRO_R1/w1/gatekeeping/C1_PRIMARY.json` (authorised training, n = 10 traces,
r = 3 model seeds, δ_CS = 2 %):

| quantity | value |
|---|---|
| Hodges–Lehmann relative difference | **−0.0001922** |
| 95 % percentile bootstrap CI | **[−0.018930, +0.122754]** |
| Wilcoxon p | **0.9219** |
| reading | **`inconclusive`**, and robust to the interval type (percentile / basic / Wilcoxon-inverted all `inconclusive`) |
| power at δ_CS | **0.15134** |
| MDE at 80 % power | **−0.06097** (vs the 0.02 threshold) |
| structural guardrail retained share | **1.019406** (the structural gain is 101.9 % retained) |

So the register asked whether the deletion (design-off) branch costs prediction, and the answer is
**"not resolvable at this n"**, not "no" — with the CI's upper half reaching +12.3 %, i.e. the design
could not have detected even a large harm.

**Dose–response, the direct test of "does structure convert?"**
(`results_w1_ladder/round_v5_1/A3P_DOSE.csv`, 80 observations per dataset):

| dataset | slope of `RMSE_μ` on `Δ_group` | 95 % CI | verdict |
|---|---|---|---|
| SensorScope | **+0.0325** | [−0.0966, +0.1525] | CI includes 0 |
| U-Air | **−0.1224** | [−0.2685, +0.0362] | **wrong sign**, CI includes 0 |

The two CIs overlap the other dataset's point estimate, so they do not differ from each other; the
pooled reading is "no detected relation". **This is the single most damaging piece of evidence for the
paper's central promise**, because it is a direct measurement of alignment → accuracy on 160 pairs and
it returns a slope whose sign is not even stable across datasets.

---

## 5. Channel 5 — how much of the structural gap the named program is needed for

`w1/ladder_v3/GAP_DECOMPOSITION.csv` (20 seeds, `G = (Δ_FedAvg − Δ_rule)/Δ_FedAvg`):

| block | FedAvg gap | closed by count→uniform weights | closed by the corrected reference | residual |
|---|---|---|---|---|
| SensorScope | 2.09 pp [1.87, 2.31] | **1.44 pp = 68.96 %** | 0.65 pp = 31.04 % | — |
| U-Air | 1.47 pp [1.18, 1.75] | **1.22 pp = 83.07 %** | 0.25 pp = 16.93 % | — |
| SensorScope (FedAU-Window) | — | 77.58 % | 22.42 % | — |
| SensorScope (ObsUse-Window) | — | 74.58 % | 25.42 % | — |

The two ingredients — uniform weighting and the corrected reference projected onto `C_r` — sum to
100 % of the gap by construction. **Nothing is left for the (P2) objective terms or the debt recursion
to explain**, which is what the paper's own re-attribution now says.

---

## 6. What is *not* weak in this channel, recorded so the account is fair

* The structural claims pass everywhere they are tested (15/20 Holm-significant rows; the Design
  ablation at `p_Holm = 9.5e-06` on both blocks and both structural endpoints).
* The negative results are printed rather than hidden: the U-Air Design cost, the TwoStage-Hájek loss,
  the untestable City-Scanner chain, the inconclusive deletion, the trace-level outlier.
* The mechanism claim was repaired this round to match its own diagnostic
  (`MYOPIC_DIAG.json`: flatness `10⁻¹³`, tie-break `1.05140` vs `1.06213`, `0.0107` pp).
* The prediction-side null is **robust to interval construction** (`C1_PRIMARY.json`:
  `reading_robust_to_interval_type` = `inconclusive` under all three).

---

## 7. What the evidence would have to look like to move this axis

Not more seeds, and not a re-analysis. The ceiling and the power table already rule those out:
U-Air's own detectable effect (0.08 % by `A1_POWER.csv`) sits below the measured headroom bound
(0.217 %), and City Scanner's power at its declared margin is 0.120–0.153 for every reliability cell.
What would move it is a **pre-registered endpoint on a setting where the headroom exceeds that
setting's own detectable effect**, and where the structural arm wins or is non-inferior on a quantity
a deployment acts on. That is the independent review's `E1` and it is the same conclusion this record
reached at round 9.

## 8. Concrete defect list produced by this pass

| # | finding | file | severity | fix |
|---|---|---|---|---|
| `EV-1` | U-Air "best raw p = 0.027" has **no source**; the smallest raw p is 0.0240 (v4) / 0.0296 (v5.1) and its Holm is 0.133 (v4) / 0.1198 (v5.1), so the printed pair is also internally cross-version | `main.tex` L2098-2099 | factual, one token | replace `0.027` (minimum edit: with `0.024`, keeping the v4 `0.133`); optionally align both to v5.1 `0.030` / `0.120` |
| `EV-2` | the SensorScope MDE is quoted as `0.17`–`0.36` pp while the same paragraph quotes U-Air at `0.70`–`0.80` "points"; `A1_POWER.csv` gives SensorScope `mde80` 0.42–0.45 % and U-Air 0.08–0.09 %, so two different scales appear in one paragraph | `main.tex` L2115-2120 | presentational | state one convention; either "0.17–0.36 pp, against a 0.42–0.45 pp paired MDE" or drop the second range |
| `EV-3` | the paper's `|H| ≤ 0.217 %` bound and `A1_POWER.csv`'s U-Air `mde80` ≈ 0.08 % are never put side by side, which is the strongest available statement that the block cannot test the ceiling | `main.tex` L2115-2120 + `A1_POWER.csv` | missing argument, not an error | one clause: "below the paired minimum detectable effect on that block" |
