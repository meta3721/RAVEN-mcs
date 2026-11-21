"""Complete R1l theory texts. Appendix-grade proofs, not sketches."""

from __future__ import annotations

GLOSSARY = """# R1l symbol glossary

Each symbol has one meaning.

| Symbol | Meaning |
|---|---|
| I_tar | Frozen target-positive pair index set |
| pi_i^tar | Frozen target mass of pair i; sum_i pi_i^tar = 1 |
| pi_safe | Frozen PI_SAFE_RULE_V1 threshold |
| pi_{i,t}^opp | Realized opportunity of pair i in window t |
| C_t | Realized aggregate coverage: sum_i pi_i^tar 1{pi_{i,t}^opp >= pi_safe} in [0,1] |
| tau_cov | Frozen operational threshold 0.05. Gate compares C_LCB to tau_cov, not C_hat |
| F_{t-} | Legal pre-window information. Current mask / current C_t / future are excluded |
| a_t | Public scenario-level availability retention. Mask identity is not in F_{t-} |
| C_hat_t | Pre-window predictor f_t(F_{t-}). Not a certificate |
| S_t | One-sided score C_hat_t - C_t |
| g | Frozen public certified-regime descriptor |
| n | Number of strictly historical same-regime calibration scores |
| alpha | Nominal miscoverage 0.05 |
| n_min | 19 = ceil(1/alpha)-1 |
| k_n | ceil((n+1)(1-alpha)) |
| q_t | S_{(k_n)} when k_n <= n; otherwise undefined (WARMUP) |
| C_LCB,t | Unique certified scalar lower bound: max{0, C_hat_t - q_t} in CERTIFIED; 0 otherwise |
| Gate_t | 1{C_LCB,t >= tau_cov} in CERTIFIED; OFF in WARMUP and RESET |
| WARMUP / CERTIFIED / RESET | Exclusive certificate states |

Forbidden aliases:
- Do not call C_hat_t a certificate.
- Do not call clipped-k conformal a 95% certificate.
- Do not call pairwise lower_pi the formal Gate object.
"""

PROP1 = r"""# Proposition 1 — Positive pairwise LCB barrier

## Statement

Let \(X_t \ge 0\) denote the realized opportunity of one target pair in window \(t\).
Let \(F_{t-}\) denote all information legally available before window \(t\).
Let \(L_t = L(F_{t-})\) be a deterministic pre-window lower bound (a measurable
function of \(F_{t-}\) only).

If
\[
  P(X_t = 0 \mid F_{t-}) > \alpha,
\]
then no strictly positive \(L_t > 0\) can satisfy
\[
  P(L_t \le X_t \mid F_{t-}) \ge 1-\alpha.
\]

## Scope (not a universal impossibility theorem)

The claim is restricted to:
- deterministic pre-window lower bounds;
- a zero-mass event that is possible given \(F_{t-}\);
- hidden current realization (current \(X_t\) not in \(F_{t-}\));
- a conditional validity claim given \(F_{t-}\).

The claim does not cover randomized certificates, Bayesian posterior intervals
under a correctly specified prior, or lower bounds that are allowed to depend on
the current hidden realization.

## Complete proof

Fix a version of the regular conditional probability given \(F_{t-}\).
On the event \(\{L_t > 0\}\), the inclusion
\[
  \{L_t \le X_t\} \subseteq \{X_t > 0\}
\]
holds pathwise: if \(X_t = 0\), then \(X_t < L_t\), so \(L_t \le X_t\) fails.
Therefore
\begin{align*}
P(L_t \le X_t \mid F_{t-})
&\le
P(X_t > 0 \mid F_{t-}) \\
&=
1 - P(X_t = 0 \mid F_{t-}) \\
&<
1-\alpha
\end{align*}
on the set where \(P(X_t=0\mid F_{t-})>\alpha\) and \(L_t>0\).

Hence no strictly positive deterministic \(L(F_{t-})\) can meet the \(1-\alpha\)
conditional coverage requirement on such \(F_{t-}\). Any deterministic lower
bound that does meet the requirement must satisfy \(L_t=0\) on that \(F_{t-}\),
or the coverage claim is false.

## Remark

This is a structural non-vacuity barrier, not a statement that pairwise
diagnostics are useless. A valid pairwise certificate may exist and be
identically zero.
"""

COR1 = r"""# Corollary 1 — Availability-induced pairwise barrier

## Statement

Suppose pair opportunity requires availability of at least one hidden stressed
entity, and only the scenario-level retention \(a\) is known pre-window.
A simple, auditable upper bound is
\[
  P(X_t > 0 \mid F_{t-}, a) \le a.
\]
Therefore, if \(a < 1-\alpha\), a strictly positive deterministic \(1-\alpha\)
pairwise LCB cannot be guaranteed under Proposition 1.

## Complete proof

Entity thinning retains each entity with probability at most \(a\) from the
certificate's pre-window information. Presence of the pair requires at least one
required entity to be available, hence
\[
  P(X_t > 0 \mid F_{t-}, a) \le a,
\]
and
\[
  P(X_t = 0 \mid F_{t-}, a) \ge 1-a.
\]
If \(a < 1-\alpha\), then \(P(X_t=0\mid F_{t-},a) > \alpha\). Proposition 1 applies.

A multi-entity conjunction would only decrease \(P(X_t>0)\). This round uses the
weakest (largest) simple upper bound \(a\).

## Frozen stress levels

For \(\alpha=0.05\), \(1-\alpha=0.95\). The frozen grid values
\(a\in\{0.80,0.60,0.40,0.20\}\) all satisfy \(a<0.95\), so they lie in the
barrier region. The value \(a=1.00\) does not create an availability zero-event;
any remaining barrier there comes from sparse natural presence, which is an
empirical fact (R1k: no target pair has historical presence \(\ge 0.95\)) and is
not required for Corollary 1.

This explains how a pairwise simultaneous certificate can be jointly valid and
identically vacuous.
"""

THM1 = r"""# Theorem 1 — Stable-regime aggregate lower-coverage guarantee

## Definitions used

Realized aggregate coverage
\[
  C_t = \sum_{i\in I_{\mathrm{tar}}} \pi_i^{\mathrm{tar}}
  \, 1\{\pi_{i,t}^{\mathrm{opp}} \ge \pi_{\mathrm{safe}}\},
\]
with \(\sum_i \pi_i^{\mathrm{tar}}=1\), hence \(C_t\in[0,1]\).

Predictor \( \widehat C_t = f_t(F_{t-}) \) is any \(F_{t-}\)-measurable map
obeying the information boundary (no current mask, no current \(C_t\), no future).

Score \( S_t = \widehat C_t - C_t \).

Calibration scores \(S_{j_1},\ldots,S_{j_n}\) are strictly historical and belong
to the same pre-registered certified stable regime \(g\) as window \(t\).

Order statistics \( S_{(1)}\le \cdots \le S_{(n)} \).
\[
  k_n = \lceil (n+1)(1-\alpha)\rceil, \qquad \alpha=0.05.
\]
A finite calibration quantile exists without clipping iff \(k_n \le n\).

## n_min derivation

We need \(\lceil(n+1)(1-\alpha)\rceil \le n\). If \((n+1)(1-\alpha) > n\), then
the ceiling is at least \(n+1\), so no finite order statistic of the calibration
sample can serve as \(q_t\). The inequality \((n+1)(1-\alpha)>n\) rearranges to
\[
  n+1 < \frac{1}{\alpha} \qquad \Leftrightarrow \qquad n < \frac{1}{\alpha}-1.
\]
Thus a finite \(q_t\) requires \( n \ge \lceil 1/\alpha\rceil - 1 \).
For \(\alpha=0.05\), \(n_{\min}=19\).

The implementation MUST NOT replace this requirement by clipping \(k_n\) to \(n\)
and still claiming a nominal 95% split-conformal guarantee. Clipping is exactly
the \(k_n=n+1\) / \(q=+\infty\) case disguised as a finite quantile; it does not
restore \(1-\alpha\) coverage for \(n<n_{\min}\). In particular \(n=8\) is not
sufficient for nominal 95% finite-sample split conformal.

## Assumption A

Conditioned on the frozen public regime descriptor \(g\), the current score
\(S_t\) and the \(n\) historical calibration scores are exchangeable.
This is not assumed globally over the entire deployment timeline.

## Statement

Assume:
1. window \(t\) is in state CERTIFIED;
2. \(n \ge n_{\min}=19\);
3. Assumption A holds for the current certified stable regime \(g\);
4. \(\widehat C_t\) is \(F_{t-}\)-measurable;
5. calibration scores are strictly historical.

Let \( q_t = S_{(k_n)} \) and
\[
  C^{\mathrm{LCB}}_t = \max\{0,\, \widehat C_t - q_t\}.
\]
Then
\[
  P\bigl( C^{\mathrm{LCB}}_t \le C_t \mid g \bigr) \ge 1-\alpha.
\]
For \(\alpha=0.05\), the right-hand side is \(0.95\).

## Complete proof

### Step 1: finite-n rank argument (almost surely distinct scores)

Let \(S_1,\ldots,S_n\) be the calibration scores and \(S_{n+1}:=S_t\) the current
score. Assumption A says these \(n+1\) random variables are exchangeable given
\(g\). First suppose they are almost surely pairwise distinct.

Let \(R\) be the rank of \(S_{n+1}\) among \(\{S_1,\ldots,S_{n+1}\}\), with
\(R=1\) the smallest. Exchangeability and a.s. distinctness imply that \(R\) is
uniform on \(\{1,\ldots,n+1\}\):
\[
  P(R=r \mid g) = \frac{1}{n+1}, \qquad r=1,\ldots,n+1.
\]
Let \(S_{(k)}^{\mathrm{cal}}\) be the \(k\)-th order statistic of
\(S_1,\ldots,S_n\). Then, pathwise,
\[
  S_{n+1} \le S_{(k)}^{\mathrm{cal}} \quad \Leftrightarrow \quad R \le k.
\]
Reason: \(R\le k\) means at most \(k-1\) of the other \(n\) scores are strictly
smaller than \(S_{n+1}\), hence the \(k\)-th calibration order statistic is at
least \(S_{n+1}\). The converse is the same count.

Therefore
\[
  P\bigl(S_t \le S_{(k_n)} \mid g\bigr)
  = P(R \le k_n \mid g)
  = \frac{k_n}{n+1}.
\]
The definition \(k_n=\lceil(n+1)(1-\alpha)\rceil\) yields
\(k_n/(n+1) \ge 1-\alpha\). CERTIFIED also enforces \(k_n\le n\), so
\(S_{(k_n)}\) exists as a calibration order statistic and \(q_t\) is finite.

### Step 2: ties

If ties have positive probability, \(R\) need not be uniform. We use a
conservative (non-randomized) convention that can only shrink the coverage event.

Draw i.i.d. Uniform\([-1,1]\) jitter \(\varepsilon_1,\ldots,\varepsilon_{n+1}\)
independent of the scores, and set \(S_i^{(\eta)} = S_i + \eta\varepsilon_i\)
for \(\eta>0\). The jittered vector remains exchangeable given \(g\) and is
a.s. distinct. Step 1 gives
\[
  P\bigl(S_{n+1}^{(\eta)} \le S_{(k_n)}^{(\eta),\mathrm{cal}} \mid g\bigr) \ge 1-\alpha.
\]
Define the conservative rank of the original scores by treating a tied current
score as strictly larger than tied calibration scores (equivalently: take
\(\eta\downarrow 0\) along the event \(\varepsilon_{n+1}>0\)). This convention
makes \(\{S_t \le q_t\}\) smaller than the jittered event in the limit, hence
\[
  P(S_t \le q_t \mid g) \ge 1-\alpha
\]
still holds. Randomized tie-breaking would restore exact uniformity; we do not
require it in the algorithm. The algorithm uses the non-randomized order
statistic \(S_{(k_n)}\) with the \(\le\) comparison, which is valid under this
conservative reading.

### Step 3: translating the score event

By definition \(S_t=\widehat C_t-C_t\), so
\[
  \{S_t \le q_t\} = \{\widehat C_t - q_t \le C_t\}.
\]

### Step 4: clipping at zero

Set \(C^{\mathrm{LCB}}_t=\max\{0,\widehat C_t-q_t\}\). Always \(C_t\ge 0\).

- If \(\widehat C_t-q_t \le 0\), then \(C^{\mathrm{LCB}}_t=0\le C_t\) holds
  pathwise, whether or not \(S_t\le q_t\).
- If \(\widehat C_t-q_t > 0\), then \(C^{\mathrm{LCB}}_t=\widehat C_t-q_t\), and
  \(\{S_t\le q_t\}\) is exactly \(\{C^{\mathrm{LCB}}_t \le C_t\}\).

In all cases
\[
  \{S_t \le q_t\} \subseteq \{C^{\mathrm{LCB}}_t \le C_t\}.
\]
Clipping cannot invalidate a valid lower bound. Therefore
\[
  P\bigl(C^{\mathrm{LCB}}_t \le C_t \mid g\bigr)
  \ge
  P(S_t \le q_t \mid g)
  \ge 1-\alpha.
\]

### Step 5: information boundary

\(\widehat C_t\) depends on \(F_{t-}\) only. Current \(C_t\) enters the score
only after window \(t\) completes, and only then may it be appended to the
calibration buffer for future windows. This is required for exchangeability of
the next step's calibration set with the next current score, but is not used to
form \(C^{\mathrm{LCB}}_t\) itself.

This completes the proof. There is no remaining sketch.
"""

COR2 = r"""# Corollary 2 — False-safe Gate bound

## Statement

Define \(\mathrm{Gate}_t = 1\{C^{\mathrm{LCB}}_t \ge \tau_{\mathrm{cov}}\}\).
Under the conditions of Theorem 1,
\[
  P\bigl(\mathrm{Gate}_t=1 \text{ and } C_t < \tau_{\mathrm{cov}} \mid g\bigr)
  \le \alpha.
\]

## Complete proof

On the event \(\{\mathrm{Gate}_t=1,\, C_t < \tau_{\mathrm{cov}}\}\) one has
\[
  C^{\mathrm{LCB}}_t \ge \tau_{\mathrm{cov}} > C_t,
\]
hence \(C^{\mathrm{LCB}}_t > C_t\). Therefore
\[
  \{\mathrm{Gate}_t=1,\, C_t < \tau_{\mathrm{cov}}\}
  \subseteq
  \{C^{\mathrm{LCB}}_t > C_t\}.
\]
Theorem 1 gives \(P(C^{\mathrm{LCB}}_t \le C_t \mid g)\ge 1-\alpha\), so
\[
  P(C^{\mathrm{LCB}}_t > C_t \mid g) \le \alpha.
\]
The false-safe probability is at most \(\alpha\).

This is the primary safety interpretation of the aggregate certificate.
The paper must emphasize false-safe control, not pairwise simultaneous coverage.

In WARMUP and RESET, \(\mathrm{Gate}_t=\mathrm{OFF}\) by definition, so the
false-safe event is empty on those windows. The bound is asserted only on
CERTIFIED windows, which is the scope of Theorem 1.
"""

PROP2 = r"""# Proposition 2 — Arbitrary-drift impossibility / applicability boundary

## Statement

Suppose two data-generating worlds have identical legal pre-window history
\(F_{t-}\) but different current aggregate coverage:
\[
  \text{World A: } C_t = c_{\mathrm{high}}, \qquad
  \text{World B: } C_t = c_{\mathrm{low}},
\]
with \(c_{\mathrm{low}} < \tau_{\mathrm{cov}} < c_{\mathrm{high}}\).

Any deterministic pre-window certificate must output the same \(C^{\mathrm{LCB}}_t\)
in both worlds. Therefore:
- if it outputs \(C^{\mathrm{LCB}}_t \ge \tau_{\mathrm{cov}}\) to be non-vacuous
  in World A, it is false-safe in World B;
- if it always outputs \(C^{\mathrm{LCB}}_t < \tau_{\mathrm{cov}}\) to protect
  World B, it cannot certify World A.

Hence, without additional assumptions linking the current window to observable
pre-window information, no method can simultaneously provide nontrivial
per-window certification and universal protection against arbitrary unannounced
regime shifts.

## Complete proof / construction

Let \(\mathcal{A}\) be any (possibly randomized, given extra bits independent of
the current world) map from \(F_{t-}\) to a real number \(C^{\mathrm{LCB}}_t\).
Because Worlds A and B share \(F_{t-}\), the law of \(C^{\mathrm{LCB}}_t\) is
identical in both worlds.

Write \(L\) for that common output. Exactly one of the following holds for each
realization: \(L \ge \tau_{\mathrm{cov}}\) or \(L < \tau_{\mathrm{cov}}\).

- If \(L \ge \tau_{\mathrm{cov}}\), then in World B one has \(L \ge \tau_{\mathrm{cov}} > c_{\mathrm{low}}=C_t\),
  so Gate ON is false-safe.
- If \(L < \tau_{\mathrm{cov}}\), then in World A the Gate is OFF even though
  \(C_t=c_{\mathrm{high}}>\tau_{\mathrm{cov}}\), so the window is not certified.

No choice of \(L=L(F_{t-})\) avoids both failures. This is an applicability
boundary, not a defect of a particular predictor.

A drift detector that uses only \(F_{t-}\) cannot protect the first unannounced
shift window if that window is indistinguishable from the certified regime in
\(F_{t-}\). After a detected change, the correct operational response is RESET
then WARMUP (Gate OFF) until \(n\ge 19\) in the new regime. The detector does
not restore Theorem 1 on the undetected first-shift window.

## What this does not claim

It does not say certification is impossible under Assumption A. It says
Assumption A (or a comparable link from \(F_{t-}\) to the current score law)
is necessary for a nontrivial per-window guarantee.
"""

STATE = r"""# Certificate state machine (frozen)

Exclusive states: WARMUP, CERTIFIED, RESET.

## WARMUP

Triggered when the current regime is certified as stable but \(n < 19\), or when
no certified regime is active and no RESET is required.
- \(C^{\mathrm{LCB}}_t = 0\)
- \(\mathrm{Gate}_t = \mathrm{OFF}\)
- Do not claim Theorem 1.

## CERTIFIED

Triggered only if:
- the frozen regime rule says window \(t\) belongs to a currently certified
  regime \(g\);
- \(n \ge 19\);
- \(k_n \le n\) (equivalent under \(\alpha=0.05\)).

Then compute \(\widehat C_t\), \(q_t=S_{(k_n)}\),
\(C^{\mathrm{LCB}}_t=\max\{0,\widehat C_t-q_t\}\),
\(\mathrm{Gate}_t=1\{C^{\mathrm{LCB}}_t\ge\tau_{\mathrm{cov}}\}\).
Theorem 1 and Corollary 2 apply.

## RESET

Triggered when the frozen regime rule says the current regime is no longer
certified (detected change using only legal pre-window public information and
past completed outcomes).
- invalidate the active calibration buffer;
- \(\mathrm{Gate}_t=\mathrm{OFF}\);
- \(C^{\mathrm{LCB}}_t=0\);
- transition to WARMUP for the new regime.

Both RESET and WARMUP force Gate OFF. The machine is deterministic given the
regime rule, \(n\), and the frozen quantile.

## Regime rule (semantic freeze, detector not chosen)

R1l freezes the semantic requirement, not one detector. The next
implementation (R1m) must pre-register one rule \(R_t\) that:
1. is frozen before formal experiments;
2. does not use current \(C_t\);
3. does not use current oracle-safe labels;
4. does not use future observations;
5. states the exchangeability claim inside each certified regime;
6. on detected change, issues RESET and Gate OFF.

Paper sentence (required):
"The finite-sample guarantee applies only within certified stable regimes.
Unannounced regime shifts outside this condition are an applicability boundary.
After a detected regime change, the certificate abstains until sufficient
calibration evidence is re-established."
"""

INTERFACE = r"""# Theory-to-algorithm interface (frozen)

## Input

- legal pre-window context \(z_t\) (public time/context only);
- scenario-level availability \(a_t\) (public); not the realized mask identity;
- historical certified-regime pairs \((\widehat C_j, C_j)\) for completed windows;
- current regime state / regime-rule output.

## Output

- certificate_state in {WARMUP, CERTIFIED, RESET};
- \(\widehat C_t\);
- n_cal;
- \(q_t\) if CERTIFIED, else undefined;
- \(C^{\mathrm{LCB}}_t\);
- Gate_t.

## Canonical logic

    if regime_not_certified:
        state = RESET if an active certified regime existed else WARMUP
        C_LCB = 0
        Gate = OFF
    elif n_cal < 19:
        state = WARMUP
        C_LCB = 0
        Gate = OFF
    else:
        state = CERTIFIED
        C_hat = predictor(F_{t-})
        q = finite_sample_conformal_quantile(scores, alpha=0.05)  # no clip
        C_LCB = max(0, C_hat - q)
        Gate = 1{C_LCB >= tau_cov}

No current mask is an input. Historical \(C_j\) is used only after window \(j\)
completes. Experimental oracle labels are not training inputs for the current
window. \(\widehat C_t\) is never reported as the certificate.

The predictor family is not frozen beyond: pre-register one measurable \(f_t\)
before the next experiment (R1m). Theorem 1 does not depend on the regression
class.
"""

FORBIDDEN = r"""# Forbidden claims (R1l)

The following claims are forbidden in the paper, code comments, and reports:

1. "95% conditional coverage for arbitrary nonstationary sequences."
2. "The drift detector guarantees safety on the first unseen shift window."
3. "The aggregate certificate is distribution-free under unrestricted drift."
4. "n=8 is sufficient for a nominal 95% finite-sample split-conformal guarantee."
5. "The pairwise certificate remains the formal core."
6. "Aggregate coverage is theoretically equivalent to simultaneous pairwise lower bounds."
7. "R1k empirical 92.2% validity already validates the new theorem."

R1k is a diagnostic. Theorem 1 is not validated by R1k's n_min=8 clipped conformal.
"""

PAPER_MAP = r"""# Paper changes implemented in R1l (theory sealed in Overleaf)

R1l edits `TO_OVERLEAF_paper_tmc_r1_clean` to seal the coverage-certificate
stack. Existing reconstruction Proposition~\ref{prop:risk} /
Theorem~\ref{thm:calibration} are not overwritten. Coverage results use
distinct labels.

## Section III (`subsec:agg_coverage_object`)

- Define \(C_t\) as the unique aggregate certification target (`eq:agg_Ct`).
- Keep TARGET_LAW_RULE_V1, PI_SAFE_RULE_V1, \(\tau_{\mathrm{cov}}=0.05\).
- Distinguish realized \(C_t\), predicted \(\widehat C_t\), certified \(C^{\mathrm{LCB}}_t\).

## Section IV (`subsec:pairwise_barrier`)

- Explain why pairwise simultaneous positive LCB is structurally vacuous under
  sparse/hidden availability (`prop:pairwise-lcb-barrier`, `cor:availability-barrier`).
- Introduce aggregate certification. Pairwise LCB remains motivation /
  diagnostic only, not the Gate object.

## Section V (`subsec:agg_certificate_alg`, `alg:agg_certificate`)

- Predictor information boundary.
- Score \(S_t=\widehat C_t-C_t\).
- Finite-sample quantile and \(n_{\min}=19\).
- WARMUP / CERTIFIED / RESET written into the algorithm.
- \(\mathrm{Gate}_t=1\{C^{\mathrm{LCB}}_t\ge\tau_{\mathrm{cov}}\}\).

## Section VI (`subsec:agg_coverage_theory`)

- `thm:agg-lcb`, `cor:false-safe-gate`, `prop:drift-boundary`,
  `ass:score-exchangeability`, stated completely.

## Appendix (`app:agg_coverage_proofs`)

- Complete proofs: rank, ties, \(k_n\), \(n_{\min}\), clipping at zero.
- Optional bounded-drift extension omitted.

## Formal Gate path in code

`window_runner` default `sag_cov_mode=aggregate_stable_regime`.
`compute_certificates` uses `r1l_state.certificate_step` for \(C_{\mathrm{cov}}^{\mathrm{LCB}}\).
Pairwise `event_count_cp` / `dynamic_max_residual` remain explicit diagnostic modes.
"""

RESTART = r"""# Post-R1l experiment restart protocol

Formal experiments restart only after THEORY_CLOSURE_PASS.

They must NOT jump to SAG.

## Next round: R1m

R1m — Aggregate Certificate Implementation under Frozen Theory

Must:
- implement the exact R1l definitions;
- use n_min = 19;
- forbid clipped-k conformal as a 95% certificate;
- freeze one predictor before results;
- freeze one stable-regime rule before results;
- implement WARMUP/CERTIFIED/RESET;
- test theorem conditions;
- report empirical validity, false-safe, false-unsafe, non-vacuity;
- focus on SensorScope a=0.40 and U-Air a=0.20;
- retain the full frozen stress track {1.00, 0.80, 0.60, 0.40, 0.20};
- STOP before SAG.

Only if R1m passes: SAG 1-seed functional validation.
Only after that passes: 5-seed main validation.
"""

CHECKLIST = r"""# Theory-algorithm consistency checklist

1. Every symbol in Theorem 1 is defined in the glossary before use. PASS
2. C_t has one meaning: realized aggregate coverage. PASS
3. C_hat_t is never called a certificate. PASS
4. C_LCB,t is the only certified scalar lower bound. PASS
5. Gate_t uses C_LCB,t and tau_cov only. PASS
6. alpha = 0.05 everywhere. PASS
7. n_min is exactly 19. PASS
8. Warm-up 8 is forbidden for nominal 95% certification. PASS
9. Pairwise lower bounds removed from the formal Gate path. PASS
   (`aggregate_stable_regime` is the window_runner default; pairwise modes are diagnostic.)
10. Current mask absent from legal pre-window inputs. PASS
11. Theorem 1 requires a certified stable regime. PASS
12. Corollary 2 is derived from Theorem 1. PASS
13. Proposition 2 prevents overclaiming under arbitrary drift. PASS
14. RESET leads to Gate OFF. PASS
15. WARMUP leads to Gate OFF. PASS
16. Algorithm cannot silently clip k=n. PASS
17. Experimental oracle is not a current-window training input. PASS
18. Stress a is public; mask identity is not. PASS
19. Historical C_j used only after window j completes. PASS
20. All proofs are complete (no 'Proof sketch'). PASS
"""

OPTIONAL = r"""# Optional bounded-drift extension: omitted

Section 16 of the R1l specification is optional. The core paper relies only on
Theorem 1, Corollary 2, and Proposition 2.

A bounded-TV robustness statement would require a legally frozen pre-test
epsilon_g with alpha' + epsilon_g <= alpha, not estimated post hoc from the
test sequence, plus a complete proof. Those conditions are not met in R1l, so
the extension is omitted. This is an explicit omission, not a pending claim.
"""

STACK = r"""# Final frozen R1l theory stack

Proposition 1: Positive pairwise-LCB barrier.
Corollary 1: Availability-induced pairwise barrier.
Definition: Aggregate realized coverage C_t.
Definition: Pre-window aggregate predictor C_hat_t (not a certificate).
Definition: One-sided residual S_t = C_hat_t - C_t.
Assumption A: Local score exchangeability within a certified stable regime.
Theorem 1: Finite-sample aggregate lower-coverage guarantee (n_min=19).
Corollary 2: False-safe Gate bound.
Proposition 2: Arbitrary-drift impossibility / applicability boundary.
State machine: WARMUP / CERTIFIED / RESET.
Operational rule: uncertified or insufficient-evidence windows => Gate OFF.

This is the unique R1l theory-closure target.
Pairwise simultaneous positive LCB is retired from the formal core.
"""

TEXTS = {
    "R1L_SYMBOL_GLOSSARY.md": GLOSSARY,
    "PROP1_POSITIVE_PAIRWISE_LCB_BARRIER.md": PROP1,
    "COROLLARY1_AVAILABILITY_BARRIER.md": COR1,
    "THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md": THM1,
    "COROLLARY2_FALSE_SAFE_GATE.md": COR2,
    "PROP2_ARBITRARY_DRIFT_BOUNDARY.md": PROP2,
    "R1L_STATE_MACHINE.md": STATE,
    "R1L_ALGORITHM_INTERFACE.md": INTERFACE,
    "R1L_FORBIDDEN_CLAIMS.md": FORBIDDEN,
    "R1L_PAPER_CHANGE_MAP.md": PAPER_MAP,
    "R1L_POST_THEORY_RESTART_PROTOCOL.md": RESTART,
    "R1L_THEORY_ALGORITHM_CHECKLIST.md": CHECKLIST,
    "R1L_OPTIONAL_DRIFT_EXTENSION_OMITTED.md": OPTIONAL,
    "R1L_THEORY_STACK.md": STACK,
}
