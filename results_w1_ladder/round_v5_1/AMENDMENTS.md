# W1 round v5.1 — AMENDMENTS.md (A0′)

Round directory: `results_w1_ladder/round_v5_1/`
Protocol: `results_w1_ladder/round_v5_1/PROTOCOL.md`
(byte-identical copy of the round-v5.1 execution prompt,
sha256 `4e1c52372a9bb155eb9f5db142bcf3d9ad9f56df8a7683bd9a0ac9c1c748742e`,
13360 bytes).
Superseded preregistration: `results_w1_ladder/round_v5/PREREG.md`
(sha256 `13ff49e5dc0a79faa5b52dadc304d2488b6e9809449472937daf617061d4d154`).

**Status: AMENDMENTS.md and PROTOCOL.md are hashed into
`results_w1_ladder/round_v5_1/MANIFEST.sha256` BEFORE any v5.1 number is
computed.** Every rule below that differs from `round_v5/PREREG.md` is listed
here with its reason, exactly as fixed by protocol §1. No margin, family,
contrast, or operational definition in this file may change after that hash is
taken.

This round executes A1′ (R4), A2′ (R3) and A3′ (R1 wording) only.
**No training is run in this round, and Part B (R1b) stays closed regardless of
the A3′ numbers** (protocol §6). `results_w1_ladder/round_v5/` is frozen and
read-only from this point on.

---

## 1 Amendments AM-1 … AM-5

| id | replaces (`round_v5/PREREG.md`) | new rule | reason |
|---|---|---|---|
| **AM-1** | G-self pass condition `α L∞ = 0` (§2.2, §2.5) | **G-self pass per run**: `α L∞ ≤ 1e-8` **and** `abs(Δ_group − final_metrics.Delta_group) ≤ 1e-12` **and** `abs(Δ_c-s − final_metrics.Delta_c_s) ≤ 1e-12` | A convex solver reproduces α only up to its tolerance. The v5 round measured α L∞ = 6.45e-09 (U-Air `proj_beta` seed 30001) and 1 ULP (seed 30011) while both endpoints still agreed to ≤ 4.4e-15; process-level caching of the parameterised CVXPY problem alone is enough to move α by 1e-9. The old condition (`α L∞` exactly 0) is therefore not informative and stopped A1 on a solver artefact, not on a rule difference. |
| **AM-2** | G-xref: tolerance `τ_x = 10 ×` the largest endpoint spread over the 12-cell A1-sens grid, plus `τ_x ≤ 5e-6` (§2.4) | **O-gate**: the distance of each implementation to an **exact projection oracle** (protocol §2.1–§2.3). The oracle is numpy-only (no CVXPY); the gates are O-G0 (KKT, per window), O-G1 (objective vs a fresh CVXPY CLARABEL solve at tolerance 1e-12 projected back onto `C_r`), O-G2 (uniform control). Verdict per arm × dataset ∈ {`certified`, `approximate`} from `max_seed eps_impl ≤ 5e-6` | A strictly convex projection problem has a **unique** optimum, so "spread across solver paths" is the wrong ruler; the right ruler is the distance to the exact optimum. The v5 β axis `raw` vs `β/Σβ` was not a perturbation at all: it projects a *different* point, i.e. a different problem with a different optimum. The debt rule's near-LP conditioning at κ = 1000 comes only from how it was written — it equals the projection of `β + κ M_rᵀ Q_r` onto `C_r` (verified algebraically in the oracle self-check) and is therefore solvable exactly in numpy. The v5 verdict "exploratory: reference not numerically stable" is a property of the reference *code*, not of the rule, and the phrase is deleted (see `ERRATA_FOR_PAPER.md` E-v51-1). |
| **AM-3** | A2-G0 "any mismatch stops A2" (§2.6 first bullet) | **three-part G0** (protocol §3.1): **G0-a** on all non-trigger rows the checkpoint re-score equals `final_metrics.json` within `1e-12` on `RMSE_mu`/`Head`/`Tail` (expected 222/222: SensorScope 120, U-Air 102); **G0-b** the trigger set is fixed in advance as `{uair} × {30007, 30016, 30018} × all 6 arms` = 18 rows, and for each the trigger must be confirmed in the run's own `window_metrics.json` (final window inactive or without α) and the θ re-score must match Table II per seed within `1e-8` relative; **G0-c** the stored `WorstGroupRMSE` of the frozen arms is reproduced within `1e-8` relative (AM-4). Any trigger row outside the set, or any listed row lacking the trigger, stops A2′ and is reported | The 18 mismatching rows are a **known defect documented before v5** (`results_seed_path_audit_r1/` record items 46–47; `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` §2A N3): when the final window does not aggregate, the run-time metric evaluates the in-memory module instead of the saved θ. The paper already uses θ as the canonical source for these cells (17 frozen + 3 θ). The v5 PREREG should have carried that rule; re-scoring under it is a re-classification of an already-measured quantity, not a re-run. |
| **AM-4** | WorstGroupRMSE tolerance `1e-10` absolute (§2.6 first bullet) | `1e-8` **relative** | The summation path differs between the stored column and the recomputation; the observed difference is 2.36e-09 absolute = **1.9e-09 relative**, seven orders of magnitude below any reported effect. The absolute 1e-10 tolerance was a tolerance on a rounding path, not on a quantity. |
| **AM-5** | TOST verdict labels `equivalent` / `harm` / `benefit` / `inconclusive` (§1.3, §2.7; NI labels §2.6) | **five labels plus `inconclusive`**: `equivalent_zero` (90 % CI inside δ **and** CI ∋ 0), `equivalent_cost` (CI inside δ, CI excludes 0, CI lower bound > 0), `equivalent_gain` (CI inside δ, CI excludes 0, CI upper bound < 0), `harm` (outside δ, CI lower bound > 0), `benefit` (outside δ, CI upper bound < 0), `inconclusive` (neither) | The v5 rule let "equivalent" and "harm (lower bound > 0)" overlap: U-Air `proj_beta − uniform_window` has +0.262 %, 90 % CI [+0.00118, +0.00504], which lies **inside** δ_P and **also excludes 0**. The honest label is `equivalent_cost`: equivalent within 0.5 % *with* a nonzero cost of +0.26 %. The v5 wording is not wrong about the decision, only about the vocabulary; the decision is unchanged (protocol §0.3). |

---

## 2 Thresholds kept unchanged from round v5 (protocol §1, last paragraph)

These are **not** amendments; they are carried over verbatim and are the values
written in the `tolerance` and `tolerance_source` columns of `GATES_V51.csv`:

| quantity | value | source |
|---|---|---|
| equivalence margin δ_P | 0.5 % of the comparator's mean `RMSE_mu` per dataset | `round_v5/PREREG.md` §1.3 |
| non-inferiority margin δ_WG | +0.5 % of the comparator's mean `WorstGroupRMSE` | `round_v5/PREREG.md` §1.1 |
| Holm families | one dataset × endpoint/contrast family, exactly the v5 families | `round_v5/PREREG.md` §1.2, §1.3, §2.6 |
| bootstrap | 10 000 resamples, `numpy.random.default_rng(20261002)` | `round_v5/PREREG.md` §2.6, §2.7 |
| implementation budget | 5e-6 (= 1e-3 × 0.005, the v5 τ_x upper bound) | `round_v5/PREREG.md` §1.4 |

New numeric tolerances introduced by AM-2/AM-3/AM-4, fixed here before
computation:

| quantity | value | source |
|---|---|---|
| O-G0 primal feasibility (per window) | ≤ 1e-13 | protocol §2.2 |
| O-G0 stationarity residual | ≤ 1e-12 | protocol §2.2 |
| O-G0 complementary slackness | ≤ 1e-12 | protocol §2.2 |
| O-G1 objective margin (200 random windows) | oracle objective ≤ CVXPY value + 1e-12 | protocol §2.2 |
| G-self α L∞ (AM-1) | ≤ 1e-8 | protocol §1 |
| G0-a endpoint equality on non-trigger rows | ≤ 1e-12 | protocol §3.1 |
| G0-b θ re-score vs Table II per seed | ≤ 1e-8 relative | protocol §3.1 |
| G0-c stored `WorstGroupRMSE` (frozen arms) | ≤ 1e-8 relative | protocol §3.1, AM-4 |
| A1′ verdict threshold `eps_impl` | ≤ 5e-6 ⇒ `certified`, else `approximate` | protocol §2.3 |

---

## 3 Files written before the first v5.1 number

Written and hashed into `MANIFEST.sha256` before any A1′/A2′/A3′ computation:

1. `PROTOCOL.md` — byte-identical copy of the execution prompt.
2. `AMENDMENTS.md` — this file.

`MANIFEST.sha256` then receives a second, appended block with the sha256 of
every artefact written by this round, added after those artefacts exist, so the
provenance of each file is checkable from the manifest alone.

## 4 No-fabrication status

At the time this file is written, **no v5.1 number exists**. Every cell of
`A1P_ORACLE_GATES.json`, `A1P_IMPL.csv`, `A1P_STRUCT_PAIRED.csv`,
`GATES_V51.csv`, `WORSTGROUP_V51.csv`, `WORSTGROUP_PAIRED.csv`,
`WORSTGROUP_NI.csv`, `TRADEOFF_V51.csv`, the A3′ side-by-side tables and
`EXECUTION_REPORT.md` is produced by the scripts `scripts/w1_v51_*.py` from the
read-only inputs listed in the protocol. If a step cannot be executed its cell
is written `TBD` with the reason in `EXECUTION_REPORT.md`; no value is imputed.
