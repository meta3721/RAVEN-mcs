# W1 round v5.1 — EXECUTION_REPORT

Protocol: `results_w1_ladder/round_v5_1/PROTOCOL.md`
(byte-identical copy of the round-v5.1 execution prompt,
sha256 `4e1c52372a9bb155eb9f5db142bcf3d9ad9f56df8a7683bd9a0ac9c1c748742e`, 13360 bytes).
Amendments: `AMENDMENTS.md`, sha256
`113429b97ef10d04d8bc99ba49e4d99ca541464406dfcefaa48c76e14ff359e4`.
Both are hashed in `MANIFEST.sha256` **before** any v5.1 number was computed.

Round executed: A0′ (AMENDMENTS + hash) → A1′ → A2′ → A3′ → report.
**No training was run.** Part B (R1b) stays closed. `results_w1_ladder/round_v5/`
was not modified. All writes are confined to `results_w1_ladder/round_v5_1/` and
`scripts/w1_v51_*.py`.

**Status line added 2026-10-03 (record Part IV, item 4).** `round_v5_1a`
(`AMENDMENT_AM-6.md`) superseded this round's **oracle implementation**, not its
conclusions: the v5.1 oracle was suboptimal (O-G1 sample objective exceeded a
feasible comparator by `+1.11e-06`), and the AM-6 rerun returns
`O-G0 primal 6.66e-16 (pass)`, `O-G0 complementary slackness 4.88e-17 (pass)`,
`O-G0 stationarity 6.67e-01 (fail)`, `O-G1 objective 9.64e-12 (fail, 7/200)`,
`O-G2 0.0 (pass)`. **Sections 1, 2 and 3 of this report stand with these
superseding readings:** the A1′ verdict remains `approximate` (all four cells),
`max eps_impl = 2.42e-05`, `alpha_linf_trained = 0.0`, and the §1.1 structural
re-check is confirmed on the rerun with **0/20 verdict changes** and max
`|Δpp| = 6.18e-04`. The oracle's remaining failures are a stationarity-residual
artefact and comparator-limited; the point-level evidence target (`1e-12`) is
still missed at `1e-8`. Every A2′ and A3′ number in this report is untouched.

---

## 0 Amendments (AM-1 … AM-5)

| id | replaces | new rule | reason | status |
|---|---|---|---|---|
| **AM-1** | G-self `α L∞ = 0` | `α L∞ ≤ 1e-8` **and** both endpoints ≤ 1e-12 vs `final_metrics` | solver tolerance; v5 measured 6.45e-09 with endpoints ≤ 4.4e-15 | applied; gate passes 120/120 |
| **AM-2** | G-xref spread over a 12-cell grid, `τ_x ≤ 5e-6` | **O-gate**: exact numpy oracle + O-G0 (KKT per window), O-G1 (objective vs fresh CVXPY CLARABEL at 1e-12, projected back onto `C_r`), O-G2 (uniform control); verdict `certified` iff `max eps_impl ≤ 5e-6` else `approximate` | a strictly convex projection has a unique optimum, so the distance to the exact optimum is the right ruler; the v5 `raw`/`norm` β axis projected a different point | implemented; **O-G0 and O-G1 fail**, all four cells `approximate` |
| **AM-3** | A2-G0 "any mismatch stops" | three-part G0; trigger set fixed in advance as `{uair} × {30007,30016,30018} × 6 arms` = 18 rows; θ-canonical score for every row | known mirror/θ defect documented before v5 (record items 46–47); the paper already uses θ for these cells | applied; **all three parts pass** |
| **AM-4** | WG tolerance 1e-10 absolute | 1e-8 **relative** | different summation path; 1.9e-09 relative observed in v5 | applied; observed 1.95e-09 relative |
| **AM-5** | 4 TOST labels | 5 labels + `inconclusive` (`equivalent_zero`, `equivalent_cost`, `equivalent_gain`, `harm`, `benefit`) | v5 let "equivalent" and "harm (lower bound > 0)" overlap | applied in A2′ and A3′ |

Thresholds unchanged from v5: δ_P = 0.5 %, δ_WG = +0.5 %, Holm families,
bootstrap 10 000 / seed 20261002, implementation budget 5e-6.

---

## 1 A1′ (R4) — exact oracle for both trained rules

Script: `scripts/w1_v51_oracle.py` (oracle + gates + measurements),
`scripts/w1_v51_struct.py` (structural re-check),
`scripts/w1_v51_uniform_rows.py`, `scripts/w1_v51_frozen_rows.py` (row completion),
`scripts/w1_v51_gates.py` (`GATES_V51.csv`), `scripts/w1_v51_recon.py` (θ-path check).
Outputs: `A1P_ORACLE_GATES.json`, `A1P_IMPL.csv`, `A1P_OG0_RUNS.csv`,
`A1P_OG1_SAMPLE.csv`, `A1P_STRUCT_PAIRED.csv`, `A1P_STRUCT_SUMMARY.json`,
`GATES_V51.csv`.

**Oracle.** `project_Cr` is numpy-only (no CVXPY): exact capped-simplex solve by
bisection with an affine Newton polish, plus a three-level active-set enumeration
(`x = τ′ + λ′v` with coordinates at 0, at the cap, or free) and an SLSQP
cross-check, keeping the closest **verified-feasible** candidate;
`proj_beta` oracle = `P_C(β̂/Σβ̂)`; `proj_beta_debt` oracle =
`P_C(β̂/Σβ̂ + κ M_rᵀQ_r)` with the exact closed loop
`Q_{r+1} = max(Q_r + 0.01(μ − M_rα_r), 0)`, `κ = 1000`. The algebraic self-check is
in `A1P_ORACLE_GATES.json["self_check_debt_algebra"]`: the two objective forms
differ by an α-independent constant (`‖β‖²/2κ`), so the projection is *exactly*
the minimiser of `−Q_rᵀM_rα + (1/(2κ))‖α−β‖²` on `C_r`.

**Oracle gates.**

| gate | observed | tolerance | tolerance_source | pass |
|---|---|---|---|---|
| O-G0 primal (6558 windows) | 9.41e-13 | 1e-13 | protocol §2.2 | **no** |
| O-G0 stationarity | 7.22 | 1e-12 | protocol §2.2 | **no** |
| O-G0 complementary slackness | 3.81e-08 | 1e-12 | protocol §2.2 | **no** |
| O-G0 primal (200-window sample) | 4.80e-13 | 1e-13 | protocol §2.2 | **no** |
| O-G0 stationarity (sample) | 36.35 | 1e-12 | protocol §2.2 | **no** |
| O-G1 objective gap | +1.11e-06 | 1e-12 | protocol §2.2 | **no** |
| O-G2 uniform control | **0.0** | 0.0 | protocol §2.2 | **yes** |

O-G1 detail: 200 windows, half projection halves debt; the CVXPY comparator was
solved at the preregistered 1e-12 with the default-tolerance tier available as a
fallback (used 0/200). At 1e-12 CLARABEL returns `optimal_inaccurate` on 139/200
windows with raw feasibility up to 4.8e-08, so the comparator is itself only
accurate to ≈1e-06; that is the scale of the observed gap. The oracle's
`α` differs from the CVXPY solution, projected back onto `C_r`, by at most
1.76e-06.

**Per the protocol's stop rule ("One failing window stops A1′"), the O-gate
verdict is `approximate` for both arms on both datasets.** The measurements are
reported as measured; nothing was re-run, tightened or relaxed.

**Measurements** (`A1P_IMPL.csv`, 160 measured rows + 40 analytic
`uniform_window` rows + 120 comparator rows):

| cell | max `eps_impl_group` | max `eps_impl_cs` | `alpha_linf_trained` | `alpha_linf_ref` | seeds `certified` | verdict |
|---|---|---|---|---|---|---|
| `proj_beta` / SensorScope | 9.07e-06 | 9.07e-06 | 0.0 | 1.05e-04 … 1.85e-04 | 19/20 | `approximate` |
| `proj_beta` / U-Air | 1.03e-05 | 1.03e-05 | 0.0 | 9.11e-05 … 2.14e-04 | 13/20 | `approximate` |
| `proj_beta_debt` / SensorScope | 1.26e-05 | 2.42e-05 | 0.0 | 1.54e-04 … 5.74e-03 | 1/20 | `approximate` |
| `proj_beta_debt` / U-Air | 2.40e-05 | 2.40e-05 | 0.0 | 3.84e-04 … 1.17e-03 | 1/20 | `approximate` |

`first_q_div` (debt arm, threshold 1e-12): first divergence at window **3**
(SensorScope) and window **5** (U-Air); `NaN` for `proj_beta`. `alpha_linf_trained`
is exactly 0.0 on all 160 cells — the trained implementations reproduce their own
replay at the level the round-v5 machinery defines as exact — while the oracle
differs from them in α by up to 1.9e-04 (SensorScope `proj_beta`), which is the
open quantitative question recorded in §4.

**Remaining gates.**

| gate | observed | tolerance | tolerance_source | pass |
|---|---|---|---|---|
| B-G1 | 0 mismatching windows | 0 | exact active-set identity vs frozen `raven` | **yes** (120/120) |
| G-self (AM-1) α L∞ | 0.0 | 1e-08 | AM-1 | **yes** |
| G-self (AM-1) endpoints | 6.44e-15 | 1e-12 | AM-1 | **yes** |
| O-gate | 2.42e-05 | 5e-06 | protocol §2.3 | **no** (all four cells `approximate`) |

### 1.1 A1′ structural re-check (protocol §2.4)

`A1P_STRUCT_PAIRED.csv` — the Δ_group and Δ_c-s rows of
`round_v4/TRADEOFF_PAIRED.csv` recomputed with the oracle endpoints in place of
the trained ones (same 5 contrasts, same bootstrap 10 000 / seed 20261002, same
Wilcoxon, same Holm family = one dataset × endpoint). Oracle endpoints replace
the trained ones for the three Part B arms; the three frozen arms keep the
round-v4 endpoints, exactly as in the trained comparison.

* **20/20 rows recomputed; 0 verdict changes.**
* Max |Δpp| = **6.18e-04 pp** (`Delta_group`, `proj_beta_debt − proj_beta`,
  SensorScope); max |Δpp| on Δ_c-s = 3.38e-04 pp.
* Largest p_holm moves: SensorScope `Delta_group proj_beta_debt − proj_beta`
  1.0e-05 → 4.0e-06; U-Air `Delta_group proj_beta − uniform_window`
  1.66e-02 → 8.31e-03. No move crosses 0.05 in either direction.

---

## 2 A2′ (R3) — worst-group scores with the θ-canonical rule

Script: `scripts/w1_v51_a2.py`. Outputs: `WORSTGROUP_V51.csv`,
`WORSTGROUP_PAIRED.csv`, `WORSTGROUP_NI.csv`, `TRADEOFF_V51.csv`,
`A2P_G0B_TRIGGER.csv`, `A2P_G0A_NONTRIGGER.csv`, `A2P_RESCORE.csv`,
`A2P_SUMMARY.json`.

**θ path pinned down first** (`scripts/w1_v51_recon.py`, `recon/RECON_TRIGGER.json`):
loading `checkpoints/final.pt` into a fresh `CommonNDMF` and predicting the test
split directly (`c_impact_recalc.py` path) gives **bit-identical** predictions to
the `build_full_runner` + `runner._predict` path used by `w1_v5_a2.py` —
max |Δy_pred| = **0.0** on all 18 trigger rows, identical unit lists — so the two
readings are the same observable and the θ framing is not a different metric.

### 2.1 Three-part G0 (AM-3, AM-4)

| part | expected | observed | tolerance | pass |
|---|---|---|---|---|
| **G0-a** | 222/222 non-trigger rows | **222/222**, max \|ΔRMSE_μ\| = max \|ΔHead\| = max \|ΔTail\| = **0.0** | 1e-12 | **yes** |
| **G0-b** trigger set | 18 rows, all confirmed | 18/18 confirmed (final window id 79 inactive, `a_r_size` = 0, `alpha` empty); **0** unlisted trigger rows; **0** listed rows without the trigger | — | **yes** |
| **G0-b** θ vs Table II | ≤ 1e-8 rel | max **1.56e-09** relative | 1e-8 rel | **yes** |
| **G0-c** frozen stored WG | ≤ 1e-8 rel | max **1.95e-09** relative (80/80) | 1e-8 rel | **yes** |

**The documented mechanism is confirmed on all 18 trigger rows**: in each run the
final window does not aggregate, and the θ re-score (which matches Table II per
seed) differs from the stored `final_metrics.json` by 1.5e-02 … 5.7e-02 in
`RMSE_mu` — the run-time in-memory-module reading, exactly as record items 46–47
describe. A sweep of all 240 runs found the trigger in *only* those 18 rows.

### 2.2 Analysis (v5 A2 unchanged) and non-inferiority

Canonical means and the `argmax_group` confirmation are in
`ERRATA_FOR_PAPER.md` E-v51-2; `WORSTGROUP_PAIRED.csv` holds the five paired
contrasts per dataset with bootstrap CI, Wilcoxon and Holm, and
`WORSTGROUP_NI.csv` the 12 non-inferiority rows with AM-5 labels.

**`argmax_group` = R2 in 240/240 runs** — round v5's raw observation is
confirmed.

Non-inferiority summary: SensorScope all six rows `equivalent_zero`; U-Air —
vs `raven`: `equivalent_gain` (`uniform_window`), `equivalent_cost`
(`proj_beta`), `equivalent_zero` (`proj_beta_debt`); vs `fedavg_window`:
`inconclusive` (`uniform_window`), `harm` (`proj_beta`, p_holm = 0.3848),
`inconclusive` (`proj_beta_debt`).

`TRADEOFF_V51.csv` = the round-v4 columns with θ-canonical
`RMSE_mu`/`Head_RMSE`/`Tail_RMSE`, the canonical `WorstGroupRMSE`, `argmax_group`
and a `source ∈ {final_metrics, theta_trigger}` column (222 `final_metrics`,
18 `theta_trigger`).

---

## 3 A3′ (R1 wording) — no new decision

Script: `scripts/w1_v51_a3.py`. Outputs: `A3P_TOST_V51.csv`,
`A3P_TOST_WG.csv`, `A3P_DOSE.csv`, `A3P_SIDE_BY_SIDE.csv`,
`A3P_RESOURCE_UPAIR.csv`, `A3P_SUMMARY.json`.

**Side by side (v5 preregistered vs v5.1 θ-canonical, AM-5 labels):**

| ds | contrast | v5 mean | v5 label→AM-5 | v5.1 mean | v5.1 rel | v5.1 90 % CI | v5.1 δ_P | v5.1 label | v5.1 p_holm |
|---|---|---|---|---|---|---|---|---|---|
| SensorScope | `proj_beta − uniform_window` | −0.002057 | `equivalent_zero` | −0.002057 | −0.026 % | [−0.006221, +0.002199] | 0.039697 | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta − fedavg_window` | −0.001643 | `equivalent_zero` | −0.001643 | −0.021 % | [−0.005897, +0.002694] | 0.039694 | `equivalent_zero` | 0.0000 |
| SensorScope | `raven − proj_beta` | +0.000739 | `equivalent_zero` | +0.000739 | +0.009 % | [−0.000905, +0.002371] | 0.039686 | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta_debt − proj_beta` | +0.001170 | `equivalent_zero` | +0.001170 | +0.015 % | [−0.002201, +0.004935] | 0.039686 | `equivalent_zero` | 0.0000 |
| U-Air | `proj_beta − uniform_window` | +0.003120 | `equivalent_cost` | +0.003418 | +0.286 % | [+0.001290, +0.005512] | 0.005967 | `equivalent_cost` | 0.0454 |
| U-Air | `proj_beta − fedavg_window` | +0.004240 | `harm` | +0.004658 | +0.391 % | [+0.000347, +0.009319] | 0.005961 | `harm` | 0.3137 |
| U-Air | `raven − proj_beta` | −0.001363 | `equivalent_gain` | −0.001544 | −0.129 % | [−0.002591, −0.000518] | 0.005985 | `equivalent_gain` | 0.0000 |
| U-Air | `proj_beta_debt − proj_beta` | −0.002103 | `equivalent_gain` | −0.002212 | −0.185 % | [−0.003978, −0.000457] | 0.005985 | `equivalent_gain` | 0.0015 |

All eight rows keep their v5 verdict under the AM-5 vocabulary; SensorScope is
unchanged to the last digit (its θ re-score is bit-exact), U-Air moves by
2.6e-04 … 4.2e-04 RMSE_μ. **The v5 decision (R1 closed) is not re-opened.** MDE
exceeds δ_P on exactly one row (U-Air `proj_beta − fedavg_window`,
0.009336 > 0.005961) and that row is `harm`, not `inconclusive`, so the
"inconclusive and MDE > δ_P" branch of the decision rule remains unreachable.

**Secondary endpoint — WorstGroupRMSE TOST** (`A3P_TOST_WG.csv`, δ = 0.5 % of
the comparator's mean):

| ds | contrast | mean diff | rel | 90 % CI | label (AM-5) | p_holm |
|---|---|---|---|---|---|---|
| SensorScope | `proj_beta − uniform_window` | −0.002133 | −0.0246 % | [−0.006407, +0.002219] | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta − fedavg_window` | −0.001716 | −0.0198 % | [−0.006047, +0.002722] | `equivalent_zero` | 0.0000 |
| SensorScope | `raven − proj_beta` | +0.000769 | +0.0089 % | [−0.000909, +0.002444] | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta_debt − proj_beta` | +0.001197 | +0.0138 % | [−0.002243, +0.005041] | `equivalent_zero` | 0.0000 |
| U-Air | `proj_beta − uniform_window` | +0.003800 | +0.3014 % | [+0.001431, +0.006138] | `equivalent_cost` | 0.0798 |
| U-Air | `proj_beta − fedavg_window` | +0.005188 | +0.4119 % | [+0.000363, +0.010438] | `harm` | 0.3562 |
| U-Air | `raven − proj_beta` | −0.001715 | −0.1356 % | [−0.002884, −0.000572] | `equivalent_gain` | 0.0000 |
| U-Air | `proj_beta_debt − proj_beta` | −0.002438 | −0.1928 % | [−0.004395, −0.000491] | `equivalent_gain` | 0.0027 |

SensorScope is `equivalent_zero` on all four rows; U-Air mirrors the
primary-endpoint pattern, including the same directional-cost row for
`proj_beta − fedavg_window` (label `harm`, p_holm = 0.3562, i.e. not
multiplicity-robust). The WorstGroupRMSE dose matches the RMSE_μ dose: the
secondary endpoint adds no new signal.

**Re-sourcing check.** All six U-Air Part B `RMSE_mu` cells and all five U-Air
`RMSE_mu` paired rows differ from v4 at the 4th significant digit; the full list,
with old and new values, is in `ERRATA_FOR_PAPER.md` E-v51-4 and
`A3P_RESOURCE_UPAIR.csv`. The three values named in the prompt (1.19248 /
1.19037 / 1.19112) are the `proj_beta`, `proj_beta_debt` and `inst_cal` cells and
all three change. SensorScope cells do not change.

---

**Algebraic self-check** (`A1P_ORACLE_GATES.json["self_check_debt_algebra"]`):
with `w = β + κMᵀQ`,

```
(1/(2κ))‖a − β‖² − QᵀMa  =  (1/(2κ))‖a − w‖²  +  ( −QᵀMβ − (κ/2)‖MᵀQ‖² )
```

The bracket is independent of `a`, so the argmin over `C_r` is `P_C(w)` exactly.
Numeric check on a real window: identity residual **1.56e-17**, and the oracle
point is not beaten by feasible perturbations of 1e-6 … 1e-2 in a simplex
direction (`perturbation_not_better = true`).

## 4 What this round did not settle
1. **The oracle's own gates failed** (O-G0, O-G1) and the O-gate verdict is
   `approximate` everywhere. The gap between the trained implementations and the
   oracle is 1e-05 in endpoint units, one to two orders of magnitude below the
   v3/v4 reference-path gap (up to 5.7e-03) but 2–5× above the preregistered
   budget. Whether a tighter exact solver closes it is an open question this
   round did not answer; the honest reading is that the *trained* rules are
   closer to the true projection than the *reference* paths, and both are
   approximate at the 1e-05 level.
2. **`alpha_linf_trained = 0.0` on all 160 cells while `eps_impl` ≈ 1e-05** is
   consistent only if the trained α and the oracle α differ on a set of windows
   whose effect on the *mean* endpoints is small — which the per-window traces in
   `scripts/w1_v51_dbg_compare.py` support (divergence concentrated on windows
   where the feasible set is nearly a point). The per-window α comparison is
   diagnostic-only and not part of any gate.
3. **A2′ / A3′ carry no such caveat**: G0-a is exact 222/222, G0-b and G0-c pass
   with three orders of margin, and the A3′ tables are computed exactly as
   preregistered.

## 5 Reproduction

```text
python scripts/w1_v51_recon.py            # theta-path recon (recon/RECON_TRIGGER.json)
python scripts/w1_v51_oracle.py           # oracle, O-G0/O-G1/O-G2, A1P_IMPL.csv
python scripts/w1_v51_uniform_rows.py     # analytic uniform_window rows
python scripts/w1_v51_frozen_rows.py      # frozen comparator rows
python scripts/w1_v51_struct.py           # A1P_STRUCT_PAIRED.csv
python scripts/w1_v51_a2.py --rescore     # theta re-score + G0 + paired + NI
python scripts/w1_v51_a3.py               # TOST / MDE / dose / re-sourcing
python scripts/w1_v51_gates.py            # GATES_V51.csv
```

All are read-only with respect to the repository outside
`results_w1_ladder/round_v5_1/`.

## 6 No-fabrication statement

Every cell in this round is produced by the scripts above from the read-only
inputs listed in the protocol. No value is imputed. Where a gate failed it is
reported as failed (`GATES_V51.csv`, §1); where a v5 conclusion moved it is
reported as moved (§3, and E-v51-3 states explicitly that no verdict moved).
