# AMENDMENT AM-6 — W1 round v5.1a: replace the A1′ oracle *implementation*

Written and hashed into `MANIFEST.sha256` **before any v5.1a number is computed**.

```text
Round:      results_w1_ladder/round_v5_1a/  (new; round_v5_1/ stays frozen and is not modified)
Supersedes: nothing.  AM-6 is an amendment to the round-v5.1 execution of AM-2, not a new decision.
Scope:      the A1′ oracle IMPLEMENTATION only.
No training.  Writes confined to results_w1_ladder/round_v5_1a/ and scripts/w1_v51a_*.py.
```

## 1 What AM-6 changes

| item | v5.1 (as executed) | v5.1a (AM-6) |
|---|---|---|
| oracle algorithm | `project_Cr` = three-level active-set enumeration capped at `max_kc=4` + an SLSQP cross-check from four starts, returning the **closest verified-feasible candidate** | the standard **two-multiplier dual**: `x = clip((v−τ)/(1+2λ), 0, ā)`, τ by the capped-simplex projection (exact breakpoint solve, bisection fallback), λ by outer bisection on `‖x‖² = 1/ē` |
| role of SLSQP | part of the production path (a candidate the oracle may return) | **removed from the production path entirely** |
| candidate selection | "best of a bag of verified-feasible candidates" | a **single** KKT point with its own multipliers; no candidate bag, no selection |
| multipliers reported | refitted by least squares on the free coordinates | the **actual** (τ, λ) used to construct the point |
| optimality evidence | none beyond feasibility of the returned candidates | KKT audit + small-K brute force + perturbation test + dual bound (§4 of the rerun) |
| file | `scripts/w1_v51_oracle.py` (untouched, kept as the superseded record) | `scripts/w1_v51a_oracle.py` |

## 2 What AM-6 does **not** change (explicit non-scope)

* the projection problem: `C_r = {Σx = 1, 0 ≤ x ≤ ā, ‖x‖² ≤ 1/ē}`, `ā = min(1, max(0.5, 1/K))`,
  `ē = min(3, K)`;
* the rules: `proj_beta` = `P_C(β̂/Σβ̂)`; `proj_beta_debt` = `P_C(β̂/Σβ̂ + κ M_rᵀQ_r)` with
  `Q_{r+1} = max(Q_r + 0.01(μ − M_rα_r), 0)`, `Q_0 = 0`, `κ = 1000`;
* every gate, every tolerance, every threshold: O-G0 primal ≤ 1e-13, stationarity ≤ 1e-12,
  complementary slackness ≤ 1e-12; O-G1 oracle objective ≤ comparator objective + 1e-12;
  O-G2 exact uniform control; implementation budget `eps_impl ≤ 5e-6` (`certified` / `approximate`);
* the O-G1 comparator (fresh CVXPY CLARABEL at tolerance 1e-12, projected back onto `C_r`),
  the 80 runs / 6558 windows of O-G0, the 200-window O-G1 sample, the 20 seeds, the arms,
  the datasets;
* the A1′ measurement definitions, the structural re-check contrasts, the Holm families,
  the bootstrap (10 000, seed 20261002), δ_P, δ_WG, and the v4 contrast list.

**No margin, family, threshold or contrast is touched.** AM-6 replaces an implementation, not a rule.

## 3 Why

The v5.1 oracle failed its own optimality gates and — decisively — was **suboptimal**, not merely
imprecise: on the O-G1 sample its objective exceeded that of a feasible comparator by up to
**+1.11e-06**. An exact projection oracle can never be worse than a feasible point, so the v5.1
implementation was returning non-optimal points. The construction explains it:

1. the active-set enumeration cannot represent an optimum with more than 4 coordinates at the cap,
   and `K ≤ 64` with `ā = 0.5` permits many more;
2. the SLSQP cross-check is a local method started from a handful of points, and it was allowed to
   supply the returned point;
3. selection was by distance to `v` among *verified-feasible* candidates, and feasibility was tested
   with tolerances (1e-10 … 1e-7 in places) that admit points which are not the projection;
4. the reported multipliers were refitted by least squares rather than taken from the construction,
   so the O-G0 stationarity residual measured something other than the algorithm's own KKT error —
   hence the 7.22 outlier together with the 3.8e-08 complementary-slackness outlier.

Under AM-6 the oracle returns the KKT point of the preregistered two-multiplier dual, whose
optimality is checked by the audit in `O_GATES_RERUN.json` and, independently, by the brute-force,
perturbation and dual evidence in `ORACLE_EVIDENCE.json`.

## 4 Status of the v5.1 readings

The v5.1 artefacts (`round_v5_1/A1P_IMPL.csv`, `A1P_ORACLE_GATES.json`, `EXECUTION_REPORT.md §4`)
remain in place as the record of the superseded run. Every A1′ number in this round is recomputed
from scratch with the new oracle and supersedes the corresponding v5.1 number. The v5.1
`E-v51-1` erratum is superseded by `round_v5_1a/ERRATA_FOR_PAPER_v5_1a.md` **only if** the gates
pass; otherwise v5.1's `E-v51-1` stands and this round adds a diagnostic, not an erratum.

## 5 Stop rule (unchanged from round v5.1 protocol §2.2)

One failing window stops A1′. No tolerance is loosened, no gate is dropped, and `certified` is not
reported unless the gates pass.
