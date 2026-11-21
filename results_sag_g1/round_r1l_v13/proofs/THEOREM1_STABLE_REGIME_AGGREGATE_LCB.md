# Theorem 1 — Stable-regime aggregate lower-coverage guarantee

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
