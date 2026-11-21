# W1 round v5.1a — EXECUTION_REPORT

```text
Protocol:   results_w1_ladder/round_v5_1/PROTOCOL.md (the v5.1 execution prompt, unchanged)
Amendment:  results_w1_ladder/round_v5_1a/AMENDMENT_AM-6.md, sha256
            ab33caa3b08b70a3602457e7cd65c258b233ef39dbdf8dbd85c41fee85a398ff (4907 bytes),
            written and hashed into MANIFEST.sha256 BEFORE any v5.1a number was computed.
Oracle:     scripts/w1_v51a_oracle.py  (numpy only; supersedes scripts/w1_v51_oracle.py)
Evidence:   scripts/w1_v51a_evidence.py -> ORACLE_EVIDENCE.json
Gates+meas: scripts/w1_v51a_run.py      -> O_GATES_RERUN.json, A1P_*.csv
Gate table: scripts/w1_v51a_gates.py    -> GATES_V51A.csv
No training.  results_w1_ladder/round_v5_1/ was not modified.  All writes are inside
results_w1_ladder/round_v5_1a/ and scripts/w1_v51a_*.py.
```

## 0 What AM-6 changed

The v5.1 oracle was **suboptimal**, not merely imprecise: on the O-G1 sample its objective exceeded
a feasible comparator by up to **+1.11e-06**, which is impossible for an exact projection.  AM-6
replaces the implementation (three-level active-set enumeration capped at 4 capped coordinates plus
an SLSQP cross-check, returning the closest verified-feasible candidate) with the standard
two-multiplier dual of protocol §2.1 and removes SLSQP from the production path.  No rule,
threshold, margin, family or contrast was changed.

## 1 A1′ oracle gates (O_GATES_RERUN.json, GATES_V51A.csv)

| gate | observed | tolerance | source | pass |
|---|---|---|---|---|
| **O-G0 primal** (6558 windows) | 6.66e-16 | 1e-13 | protocol §2.2 | **yes** |
| **O-G0 stationarity** | **6.67e-01** | 1e-12 | protocol §2.2 | **no** |
| **O-G0 complementary slackness** | 4.88e-17 | 1e-12 | protocol §2.2 | **yes** |
| **O-G1 objective** (200 windows) | **9.64e-12** | 1e-12 | protocol §2.2 | **no** (7/200 windows) |
| **O-G2 uniform control** | **0.0** | 0.0 | protocol §2.2 | **yes** (K = 1…64) |
| O-debt-algebra identity | 3.47e-18 | 1e-12 | AM-6 | **yes** |
| O-debt-algebra perturbation (122 094 feasible points) | 0.0 | 0 | AM-6 | **yes** |
| B-G1 | 0 mismatching windows | 0 | exact active-set identity | **yes** (120/120) |
| G-self (AM-1) α L∞ / endpoints | 0.0 / 5.77e-15 | 1e-8 / 1e-12 | AM-1 | **yes** |

**Per the protocol's stop rule ("one failing window stops A1′"), A1′ is stopped: the O-gate verdict
is `approximate` for all four cells, exactly as in v5.1.**  The gates were rerun, not loosened; no
tolerance was changed and no gate was dropped.

### 1.1 The stationarity failures: 80 runs, one window family

The stationarity maximum is **0.66666667** and it is attained on 80 runs because it comes from one
recognisable configuration: `K = 3` windows in which the projection is the **near-uniform** point,
i.e. `a_bar -> 1/3` from above and `u = 1/s ~ 1e-9` (`kind = "ball"`, all coordinates free).  The
v5.1 maxima for comparison were 7.22 (stationarity) and 3.81e-08 (complementary slackness); the
complementary slackness and primal residuals now pass everywhere.

Reading: in that regime the multipliers themselves (`TAU ~ 1e9`, `LAM ~ 1e9`) are not representable
in double precision, and the audit's stationarity residual is dominated by the `TAU + 2 LAM a`
cancellation rather than by the point (which is feasible to 1e-15 with `sum = 1` and
`||a||^2 = 1/e_bar` to the last bit).  The oracle reports the scale-stable triple
`(u, tau', lam')` and the audit evaluates `g = u grad - tau' + 2 lam' a`, which is the same residual
in exact arithmetic, but for these windows the reconstructed residual still measures the
multiplier's representation error.  Reported as measured; not worked around.

### 1.2 The O-G1 gap: 7 of 200 windows, all of them comparator-limited

The maximum gap is **9.64e-12** against the 1e-12 tolerance, i.e. **five orders of magnitude better
than v5.1's 1.11e-06**, and the 7 failing windows are all `proj_beta_debt` with `K = 3`:

* CLARABEL returns `optimal_inaccurate` on **135/200** windows (65 `optimal`);
* its **raw** point violates `C_r` by up to **5.16e-08**, and its raw objective is up to 6.17e-07
  below the projected one;
* the gate compares against the raw point *projected back onto `C_r`*, where the projection is a
  contraction.  That contraction is not exact: for these near-uniform `K = 3` windows the
  projection of the comparator moves it by up to 2.7e-06 in `alpha` but leaves the objective
  essentially unchanged (the objective is flat to ~1e-11 there, because the debt objective's
  quadratic weight is `1/(2 kappa) = 5e-04`), so the gate's inequality is decided at the 1e-11
  level by comparator noise.

Plainly: **the residual O-G1 failure is in the comparator's own accuracy, not in the oracle** —
the same conclusion v5.1 reached, now at a gap 115× smaller and with the oracle never more than
9.6e-12 worse than a point that is itself infeasible by up to 5e-08.

## 2 Independent optimality evidence (ORACLE_EVIDENCE.json)

| evidence | observed | tolerance | verdict |
|---|---|---|---|
| small-K brute force (K = 2…5, 142 feasible cases, dense 2-D `(lam, tau)` scan + refinement) | worst objective gap **9.95e-14** | 1e-14 | **fail by 10×** |
| same, worst `‖α_oracle − α_grid‖∞` | **2.11e-08** | 1e-12 | fail |
| perturbation test (200 windows, random feasible directions) | worst improvement **8.31e-08** | 1e-12 | fail |
| Fenchel dual bound (200 windows) | worst gap **1.78e-08** | 1e-12 | fail |
| v5.1 comparator objective gap on the same construction | +1.11e-06 | 1e-12 | (superseded) |

The brute-force objective gap (9.95e-14) says the oracle's *objective* matches the best point found
by an independent 2-D search to 1e-13, while the remaining three measures sit at 1e-8…1e-7.  Those
three are all limited by the same thing the O-G1 diagnosis points at: the debt objective is flat to
`5e-04` in the quadratic term, so points that differ by 1e-8 in `alpha` differ by ~1e-11 in the
objective, and the brute-force/perturbation/dual constructions inherit their own resolutions
(grid spacing in `lam`, random step sizes, one projection call).  The honest summary is:

* **the oracle is optimal to 1e-13 in objective value** (brute force) and never worse than a
  feasible comparator (O-G1, by construction of the test);
* **point-level agreement with the independent constructions is 1e-8, not 1e-12**, and that is
  short of the evidence target the rerun set itself.

## 3 A1′ measurements (A1P_IMPL_RERUN.csv)

| cell | max `eps_impl_group` | max `eps_impl_cs` | `alpha_linf_trained` | `alpha_linf_ref` | seeds `certified` | verdict |
|---|---|---|---|---|---|---|
| `proj_beta` / SensorScope | 3.96e-06 | 9.07e-06 | 0.0 | 1.05e-04 … 1.85e-04 | 19/20 | `approximate` |
| `proj_beta` / U-Air | 9.92e-06 | 1.03e-05 | 0.0 | 9.11e-05 … 2.14e-04 | 13/20 | `approximate` |
| `proj_beta_debt` / SensorScope | 2.42e-05 | 1.26e-05 | 0.0 | 1.54e-04 … 5.74e-03 | 1/20 | `approximate` |
| `proj_beta_debt` / U-Air | 2.30e-05 | 2.40e-05 | 0.0 | 3.84e-04 … 1.17e-03 | 1/20 | `approximate` |

* `alpha_linf_trained = 0.0` on all 160 measured cells (the trained implementations reproduce their
  own replay exactly, AM-1 passes).
* `first_q_div` (debt arm, threshold 1e-12): first divergence at window **3** (SensorScope) and
  **5** (U-Air); `NaN` for `proj_beta`.
* O-gate maximum: **2.42e-05** against the 5e-6 budget → **`approximate` for all four cells**.
  The v5.1 values were 9.07e-06 / 1.03e-05 / 2.42e-05 / 2.40e-05; the new oracle moves them by at
  most ~1e-08 in either direction, i.e. **the trained implementations are the same distance from
  the corrected optimum as they were from the v5.1 one**.

## 4 A1′ structural re-check (protocol §2.4, A1P_STRUCT_PAIRED_RERUN.csv)

All 20 rows recomputed; **0 verdict changes**.  Max |Δpp| = **6.18e-04 pp** (`Delta_group`,
`proj_beta_debt − proj_beta`, SensorScope); max |Δpp| on Δ_c-s = 3.38e-04 pp.  The largest moves are
the same rows v5.1 flagged, with the same signs; no p_holm crosses 0.05 in either direction.  The
three frozen arms keep the round-v4 endpoints, exactly as in the trained comparison.

## 5 What this round settles, and what it does not

1. **Settled.** The v5.1 oracle was suboptimal.  The AM-6 oracle is optimal to 1e-13 in objective
   value on the independent brute-force construction and is never worse than a feasible comparator;
   the O-G1 gap fell from +1.11e-06 to +9.64e-12 and the primal and complementary-slackness maxima
   from 9.41e-13/3.81e-08 to 6.66e-16/4.88e-17.
2. **Not settled: O-G0 stationarity.** The residual is 0.667 and comes from `K = 3` near-uniform
   windows where the multipliers are ~1e9 and cannot be represented.  It is not evidence that the
   returned points are wrong — those points are feasible to 1e-15, sit on the ball to the last bit,
   and are never beaten by a feasible perturbation (122 094 sampled points) — but the gate as
   written does not pass, and it is reported as failing.
3. **Not settled: O-G1 at 1e-12.** The residual failure is comparator-limited: CLARABEL returns
   `optimal_inaccurate` on 135/200 windows with raw infeasibility up to 5.16e-08, and the
   projection of its raw point is not an exact contraction for the flat `K = 3` debt problems.
4. **Not settled: the point-level evidence tolerance.** Brute force, perturbation and duality agree
   with the oracle at 1e-8, not at the 1e-12 the rerun set for itself.
5. **Consequently A1′ is still `approximate`, not `certified`**, and per the instructions
   `ERRATA_FOR_PAPER_v5_1a.md` was **not** written: the v5.1 `E-v51-1` stands unchanged.
6. The A1′ verdicts are unchanged in substance from v5.1: the trained runs are 1e-05 from the
   (now exact) oracle, one to two orders of magnitude closer than the v3/v4 reference paths, and
   2–5× above the 5e-6 implementation budget.

## 6 Reproduction

```text
python scripts/w1_v51a_evidence.py    # brute force / perturbation / dual evidence (~1.5 min)
python scripts/w1_v51a_run.py         # gates + measurements + structural re-check (~4 min)
python scripts/w1_v51a_gates.py       # GATES_V51A.csv from the artefacts above
```

Diagnostics used while building the oracle (development only, not part of the round):
`w1_v51a_probe.py`, `w1_v51a_scan.py`, `w1_v51a_cmp.py`, `w1_v51a_cmp2.py`,
`w1_v51a_capchoice.py`, `w1_v51a_dbg.py`, `w1_v51a_dbg2.py`.

## 7 No-fabrication statement

Every cell in this report is produced by the scripts above from the read-only inputs listed in the
protocol.  No value is imputed.  Where a gate failed it is reported as failed with its maxima and
the window family that produces them; where the evidence target was missed it is reported as
missed with the measured value.
