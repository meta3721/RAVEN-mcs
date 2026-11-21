"""Historical R1l coverage-controlled theory texts (legacy only).

The Design := Gate statements below describe the retained legacy method.
Configured Design is specified by r1l_design.DesignConfiguration, independently
of the same coverage diagnostic. These texts are not the current method freeze."""

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
| Design_t | Frozen Design_t := Gate_t. Unique window-close Design authority |
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

For a target pair \(i=(k,s)\) let the designated stressed entity be
\(e(i)=k\) (the pair's client; or the unique designated entity in the
paper's stress construction). Let \(A_{e(i),t}\in\{0,1\}\) be that entity's
availability in window \(t\).

Assume the necessary-condition
\[
  X_{i,t}>0 \;\Rightarrow\; A_{e(i),t}=1.
\]
Under the frozen availability stress,
\[
  P(A_{e(i),t}=1\mid F_{t-},a)\le a.
\]
Therefore
\[
  P(X_{i,t}>0\mid F_{t-},a)
  \le
  P(A_{e(i),t}=1\mid F_{t-},a)
  \le a,
\]
and \(P(X_{i,t}=0\mid F_{t-},a)\ge 1-a\). If \(a<1-\alpha\), then
\(1-a>\alpha\), and Proposition 1 implies that no strictly positive
deterministic \(1-\alpha\) pairwise LCB is guaranteed for that pair.

## Scope (do not overclaim)

The corollary applies only to pairs that satisfy
\(X_i>0\Rightarrow A_{e(i)}=1\).
It does NOT claim that "at least one entity in an arbitrary group is
unavailable implies \(P(\mathrm{active})\le a\)".

## Complete proof

The implication \(X_{i,t}>0\Rightarrow A_{e(i),t}=1\) yields the event
inclusion \(\{X_{i,t}>0\}\subseteq\{A_{e(i),t}=1\}\), hence the probability
bound above. Frozen independent (or nested) entity thinning gives
\(P(A_{e(i),t}=1\mid F_{t-},a)\le a\). If \(a<1-\alpha\), then
\(P(X_{i,t}=0\mid F_{t-},a)>\alpha\), so Proposition 1 applies to this pair.

## Frozen stress levels

For \(\alpha=0.05\), \(1-\alpha=0.95\). The frozen grid values
\(a\in\{0.80,0.60,0.40,0.20\}\) all satisfy \(a<0.95\) for pairs obeying the
designated-entity necessary condition.
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

Operational regime certification does not prove exchangeability.
It only defines the pre-registered subset of windows for which
Assumption A is posited.
Theorem 1 remains conditional on Assumption A even when the
algorithmic state is CERTIFIED.
The rule operationalizes the scope in which Assumption A is invoked.
CERTIFIED is not a proof that the scores are exchangeable.

## Statement

Assume:
1. window \(t\) is in operational state CERTIFIED (scope, not a proof of A);
2. \(n \ge n_{\min}=19\);
3. Assumption A holds for the current regime descriptor \(g\);
4. \(\widehat C_t=f_b(F_{t-})\) uses the frozen predictor snapshot of the
   current certified block \(b\);
5. calibration scores are strictly historical same-block scores.

Let \( q_t = S_{(k_n)}^{\mathrm{cal}} \) and
\[
  C^{\mathrm{LCB}}_t = \max\{0,\, \widehat C_t - q_t\}.
\]
Then
\[
  P\bigl( C^{\mathrm{LCB}}_t \le C_t \mid g \bigr) \ge 1-\alpha.
\]
For \(\alpha=0.05\), the right-hand side is \(0.95\).

## Complete proof

### Step 1: auxiliary continuous tie-break and randomized rank

Let \(S_{j_1},\ldots,S_{j_n}\) be the calibration scores and \(S_t\) the
current score. Assumption A says these \(n+1\) random variables are
exchangeable given \(g\). Draw auxiliary variables
\[
  U_{j_1},\ldots,U_{j_n},U_t
\]
i.i.d. Continuous\((0,1)\), independent of the scores. Form the pairs
\((S_j,U_j)\) and order them lexicographically. Because the pairs
\[
  (S_{j_1},U_{j_1}),\ldots,(S_{j_n},U_{j_n}),(S_t,U_t)
\]
are exchangeable given \(g\) and are almost surely pairwise distinct after
tie-break, the randomized rank \(R_t^\star\) of \((S_t,U_t)\) among the
\(n+1\) pairs is uniform on \(\{1,\ldots,n+1\}\):
\[
  P(R_t^\star = r \mid g) = \frac{1}{n+1}.
\]
Let \(S_{(1)}^{\mathrm{cal}}\le\cdots\le S_{(n)}^{\mathrm{cal}}\) be the
calibration order statistics and \(k_n=\lceil(n+1)(1-\alpha)\rceil\). Then
\[
  P(R_t^\star \le k_n \mid g) = \frac{k_n}{n+1} \ge 1-\alpha.
\]
CERTIFIED enforces \(k_n\le n\), so \(q_t=S_{(k_n)}^{\mathrm{cal}}\) exists.

### Step 2: event inclusion (correct direction)

We claim
\[
  \{R_t^\star \le k_n\}
  \subseteq
  \{S_t \le S_{(k_n)}^{\mathrm{cal}}\}.
\]
Proof by contradiction. If \(S_t > S_{(k_n)}^{\mathrm{cal}}\), then at least
\(k_n\) calibration scores are strictly smaller than \(S_t\). Hence, whatever
\(U_t\) is, the test pair ranks at least \(k_n+1\), contradicting
\(R_t^\star \le k_n\). Therefore the inclusion holds.

It is forbidden to argue that a "conservative" convention shrinks
\(\{S_t\le q_t\}\) relative to a coverage event of probability \(1-\alpha\)
and then conclude that the smaller event still has probability \(1-\alpha\).
If \(A\subset B\) and \(P(B)\ge 1-\alpha\), one cannot infer
\(P(A)\ge 1-\alpha\). The argument used here is the opposite inclusion:
the uniform-rank event is contained in \(\{S_t\le q_t\}\).

### Step 3: transferring the probability

\[
  P(S_t \le q_t \mid g)
  \ge
  P(R_t^\star \le k_n \mid g)
  \ge 1-\alpha.
\]

### Step 4: translating the score event

By definition \(S_t=\widehat C_t-C_t\), so
\[
  \{S_t \le q_t\} = \{\widehat C_t - q_t \le C_t\}.
\]

### Step 5: clipping at zero

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

### Step 6: frozen predictor snapshot and information boundary

\(\widehat C_t=f_b(F_{t-})\) uses the frozen snapshot of block \(b\).
Refitting the scoring rule on every window with new outcomes would take the
construction outside this split-conformal rank argument. Current \(C_t\)
enters the score only after window \(t\) completes, and only then may it be
appended to the same-block calibration buffer. The current window is never
used to form its own \(q_t\).

This completes the proof.
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
- the frozen operational regime rule says window \(t\) belongs to a currently
  active candidate regime \(g\) (this operationalizes the scope in which
  Assumption A is invoked; it does not prove exchangeability);
- \(n \ge 19\);
- \(k_n \le n\) (equivalent under \(\alpha=0.05\));
- the predictor snapshot \(f_b\) of the current block is frozen.

Then compute \(\widehat C_t=f_b(F_{t-})\), \(q_t=S_{(k_n)}^{\mathrm{cal}}\),
\(C^{\mathrm{LCB}}_t=\max\{0,\widehat C_t-q_t\}\),
\(\mathrm{Gate}_t=1\{C^{\mathrm{LCB}}_t\ge\tau_{\mathrm{cov}}\}\).
Theorem 1 remains conditional on Assumption A even when the algorithmic
state is CERTIFIED.

Forbidden: "the detector certifies exchangeability";
"CERTIFIED implies Assumption A holds";
"passing the stability test proves the conformal assumption".

## RESET

Triggered when the frozen regime rule says the current regime is no longer
certified (detected change using only legal pre-window public information and
past completed outcomes).
- \(\mathrm{Gate}_t=\mathrm{OFF}\);
- \(C^{\mathrm{LCB}}_t=0\);
- finalize the current block;
- refit a new predictor snapshot \(f_{b+1}\) using only completed past data;
- freeze \(f_{b+1}\);
- clear the calibration buffer;
- transition to WARMUP for the new block and re-accumulate \(n_{\min}=19\).

Refit is forbidden during WARMUP and CERTIFIED of the same block.

Both RESET and WARMUP force Gate OFF. The machine is deterministic given the
regime rule, \(n\), and the frozen quantile.

## Design mapping (R1l-v1.2)

Frozen equality: \(\mathrm{Design}_t := \mathrm{Gate}_t\).

| certificate_state | C_LCB condition | Gate_t | Design_t |
|---|---|---:|---:|
| WARMUP | not certified | 0 | OFF |
| RESET | not certified | 0 | OFF |
| CERTIFIED | C_LCB < tau_cov | 0 | OFF |
| CERTIFIED | C_LCB >= tau_cov | 1 | ON |

Dataset-level Design flags are not a formal control.

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
- historical same-block completed pairs;
- current regime-rule output.

## Maintained state

- block_id
- predictor_snapshot_id
- state in {WARMUP, CERTIFIED, RESET}
- regime_id
- n_cal
- calibration_buffer

## Output

- certificate_state;
- \(\widehat C_t=f_b(F_{t-})\);
- n_cal;
- \(q_t\) if CERTIFIED, else undefined;
- \(C^{\mathrm{LCB}}_t\);
- Gate_t;
- Design_t := Gate_t.

## Canonical logic

    if regime_change_detected:
        state = RESET
        Gate = OFF
        finalize current block
        fit new predictor f_{b+1} using only completed past data
        freeze f_{b+1}
        clear calibration buffer
        state = WARMUP
    elif state == WARMUP:
        use frozen f_b
        if n_cal < 19:
            C_LCB = 0
            Gate = OFF
        once n_cal >= 19 and operational regime rule remains active:
            state = CERTIFIED
    elif state == CERTIFIED:
        use same frozen f_b
        q_t = finite_sample_quantile(historical same-block scores, alpha=0.05)
        C_hat_t = f_b(F_{t-})
        C_LCB,t = max(0, C_hat_t - q_t)
        Gate_t = 1{C_LCB >= tau_cov}

Window-close RAVEN-MCS (formal):
    Design_t := Gate_t
    if Gate_t == 1: Design-enabled zeta branch
    else: Design-OFF fallback (zeta <- 1)
    Gate_t is produced by the aggregate coverage certificate.

No current mask is an input. Historical \(C_j\) is used only after window \(j\)
completes. The current window is never in its own \(q_t\). Experimental oracle
labels are not training inputs for the current window. \(\widehat C_t\) is
never reported as the certificate.

The scoring rule is frozen per certified block so that Theorem 1's ordinary
finite-sample exchangeable rank argument applies. Per-window refit would take
the construction outside that theorem.
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
8. "CERTIFIED implies Assumption A holds."
9. "The detector certifies exchangeability."
10. "Passing the stability test proves the conformal assumption."
11. "If A subset B and P(B)>=1-alpha then P(A)>=1-alpha."
12. "At least one hidden entity available implies P(X>0|F,a)<=a without a designated-entity necessary condition."
13. "A dataset-level Design flag is the formal Design control."
14. "SensorScope Design=ON / U-Air Design=OFF is the current method."

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
- \(\mathrm{Design}_t:=\mathrm{Gate}_t\) enters `alg:window_close`.
- Dataset-level Design flag removed from the formal algorithm.

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

## Current round after R1l-v1.2: R1m

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
21. Randomized-rank ties proof uses \{R^*\le k\}\subseteq\{S_t\le q_t\}. PASS
22. CERTIFIED does not prove Assumption A. PASS
23. Predictor snapshot frozen within block; refit only after RESET. PASS
24. Design_t := Gate_t is the unique formal Design authority. PASS
25. Formal window-close does not use a dataset-level Design flag. PASS
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
State machine: WARMUP / CERTIFIED / RESET with frozen predictor snapshot per block.
Operational CERTIFIED does not prove Assumption A.
Operational rule: uncertified or insufficient-evidence windows => Gate OFF.
Design_t := Gate_t is the unique window-close Design authority.

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
