# G5 protocol — P2 solver audit + practical significance

Date: 2026-08-24  
Gate: handbook §9  
No formal retrain. No edit to `main.tex`. Sealed E3/E4 / `paper_ready_r2/` are read-only.

## 9.1 P2 warning audit

The frozen E3 count remains **778 warnings / 85 runs / 6438 audited windows**, max constraint residual \(2.686\times10^{-8}<10^{-7}\). That audit certifies **feasibility**, not exact optimality (LEVEL 3 not reconstructable from sealed E3 outputs).

This gate adds the missing second-solver check on windows whose **full P2 inputs were persisted** (`p2_invocation_states.json`: \(M,\mu,\hat\beta,Q,V,\bar\tau,\lambda\)):

- `post_review/G1_support_compatible/runs/{sensorscope,uair}/raven_sc_target/seed30001–30010`
- `artifacts/e3_drifting_r1/runs/{sensorscope,uair}/raven/seed30001–30020` (same program; not a new formal)

Primary solver in production: CVXPY+CLARABEL, SCS fallback, then feasibility repair.  
**Second solver (independent):** a raw SOCP solve **without** the production SCS-fallback + feasibility-repair path. OSQP is installed but is QP-only and cannot encode \(\|\alpha\|_2^2\le 1/\bar E\); use ECOS if present, otherwise SCS. Primary logged solver remains CLARABEL.

All warning windows plus 20 non-warning windows per dataset (seed 30001 RNG) are re-solved. Agreement is **CLARABEL-raw vs second-raw**. Logged \(\alpha\) (often `feasible_repaired`) is compared separately as repair displacement, not as the second-solver test.

Pre-registered numerical agreement (not an MPID):

\[
\|\alpha^{(1)}-\alpha^{(2)}\|_1\le 10^{-4},\quad
\|M(\alpha^{(1)}-\alpha^{(2)})\|_1\le 10^{-4},\quad
\frac{|J_1-J_2|}{1+|J_1|}\le 10^{-4}.
\]

If every compared window meets this, the 778 warnings are **implementation tolerance** and we do **not** rerun sealed formal trees.  
If a window misses it, record the gap and decide whether it can move a run-level endpoint (see below). Do not retune \(\lambda\) or Design.

Also report primal residuals (simplex, box, ESS) and a first-order stationarity residual \(\|\nabla J(\alpha)-\overline{\nabla J}\|_2\) on the simplex tangent. Dual/KKT multipliers are recorded when the solver exposes them; they are not required for the gate.

“Affects main conclusion” if \(\max\|M\Delta\alpha\|_1\ge 10^{-3}\) (conservative: one window could then move \(\Delta_{\mathrm{group}}\) at a visible scale). Below that, solver disagreement is numerically irrelevant to paper endpoints.

## 9.2 Practical significance (MPID locked before this gate’s numbers)

**MPID = 0.5% paired relative mean.**  
This is the same threshold already used as a non-inferiority / do-not-break rule in G1 Path A and G2. It is not chosen after looking at G5 outputs. No external clinical/engineering MPID exists for these MCS endpoints.

Classification of a paired contrast:

| | \(|\mathrm{mean}\%| < 0.5\) | \(|\mathrm{mean}\%| \ge 0.5\) |
|---|---|---|
| Holm / Wilcoxon significant | **quantitatively small** (Debt-class) | practically meaningful |
| not significant | no clear effect | report the point estimate; do not upgrade to “large” |

Debt’s published \(0.002\%\)–\(0.014\%\) is below MPID by two orders of magnitude. Even if \(p<0.05\), write **quantitatively small**.

Primary contrasts to classify (existing sealed / post-review tables, no new training):

- E4 component removals (Design, Obs, Use, Inst, Debt)
- Path B TEST: gated vs full Design (U-Air) and Design vs No-Design (SensorScope)
- G2 TEST: gated vs FedAU / ObsUse WorstGroupRMSE

**Seed scope (must appear in the claim ceiling):** 20 formal seeds (or 10 VAL / 10 TEST) represent **algorithmic / EventTrace randomness**. They do not replace independent cities, calendar windows, or a T-Drive ranking.

## Gate

| Verdict | Rule |
|---|---|
| `G5_ACCEPTED` | Second-solver agreement holds (or disagreements stay below the \(10^{-3}\) composition flag); Debt < MPID; Path B / G2 contrasts classified; seed-scope sentence written. |
| `G5_SOLVER_DIVERGE` | A reconstructable window misses numerical agreement **and** \(\|M\Delta\alpha\|_1\ge10^{-3}\). Do not rerun formal from this file; stop and report. |
| `G5_FAIL` | Cannot load persisted P2 inputs and cannot restate the frozen 778 audit. |

Outputs only under `post_review/G5_solver_significance/`.
