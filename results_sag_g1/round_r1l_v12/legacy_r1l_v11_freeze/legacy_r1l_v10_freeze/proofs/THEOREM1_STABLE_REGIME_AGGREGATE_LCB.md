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
