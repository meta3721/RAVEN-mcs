# G4 theorem — practical plug-in perturbation

This note is the G4 deliverable. It is not yet pasted into `main.tex`.  
Notation matches the clean submission draft (Proposition 2, eqs. for \(a\), \(d\), \(\widehat{\boldsymbol\beta}\), P2).

## Objects

Fix an active window \(r\) and a client set \(\mathcal{A}_r\). Realized marks \((R_{k,r,i},O_{k,r,i},U_{k,r})\) are held fixed.

**Ideal same-window reference** (A3 ratios, no clip), for \(k\in\mathcal{A}_r\):

\[
a^\star_{k,r,i}=\frac{\zeta^{o}_{k,r,i}}{p^{\mathrm{obs}}_{k,r,i}},
\quad
d^\star_{k,r}=\frac{1}{q^{\mathrm{use}}_{k,r}},
\quad
m^\star_{k,r}=\sum_i R_{k,r,i}O_{k,r,i}a^\star_{k,r,i},
\quad
b^\star_{k,r}=m^\star_{k,r}d^\star_{k,r},
\]

\[
\beta^\star_{k,r}=\frac{b^\star_{k,r}}{\sum_{j\in\mathcal{A}_r}b^\star_{j,r}}.
\]

**Practical reference** (implementation):

\[
\widetilde a_{k,r,i}=\frac{\widehat\zeta^{o}_{k,r,i}}{\max\{\widehat p^{\mathrm{obs}}_{k,r,i},p_{\min}\}},
\quad
a_{k,r,i}=\min\{a_{\max},\widetilde a_{k,r,i}\},
\]

\[
\widetilde d_{k,r}=\frac{1}{\max\{\widehat q^{\mathrm{use}}_{k,r},q_{\min}\}},
\quad
d_{k,r}=\min\{d_{\max},\widetilde d_{k,r}\},
\]

then \(m_{k,r}=\sum_i R_{k,r,i}O_{k,r,i}a_{k,r,i}\), \(b_{k,r}=m_{k,r}d_{k,r}\), \(\widehat\beta_{k,r}=b_{k,r}/\sum_j b_{j,r}\).

Clipping residuals (the terms the paper previously left unnamed):

\[
\rho^{a}_{k,r,i}=(\widetilde a_{k,r,i}-a_{\max})_+,
\qquad
\rho^{d}_{k,r}=(\widetilde d_{k,r}-d_{\max})_+.
\]

Then \(a=\widetilde a-\rho^{a}\) and \(d=\widetilde d-\rho^{d}\). These are nonnegative. They are **not** set to zero.

Let \(n_{k,r}=\sum_i R_{k,r,i}O_{k,r,i}\) and \(n_r=\max_{k\in\mathcal{A}_r}n_{k,r}\), \(K_r=|\mathcal{A}_r|\). Write \(B_r=\sum_j b_{j,r}\) and \(B_r^\star=\sum_j b^\star_{j,r}\).

## Assumption A5 (quantitative positivity on target support)

A1 already requires positivity wherever \(\pi^{\mathrm{tar}}_{k,i}>0\). A5 makes the margins numerical, on that same set, for the window under study:

1. \(\pi^{\mathrm{opp}}_{k,s}\ge\pi_{\min}>0\), \(p^{\mathrm{obs}}\ge p_{\min}^{\mathrm{true}}>0\), \(q^{\mathrm{use}}\ge q_{\min}^{\mathrm{true}}>0\).
2. Floors used by the code satisfy \(0<p_{\min}\le p_{\min}^{\mathrm{true}}\) and \(0<q_{\min}\le q_{\min}^{\mathrm{true}}\).
3. Uniform plug-in errors on that support: \(|\widehat\pi^{\mathrm{opp}}-\pi^{\mathrm{opp}}|\le\varepsilon_\pi\), \(|\widehat p-p|\le\varepsilon_p\), \(|\widehat q-q|\le\varepsilon_q\).
4. \(\widehat\pi^{\mathrm{opp}}\ge\pi_{\min}\) (or the \(\pi_{\min}\) floor is applied, and \(\varepsilon_\pi\) absorbs the floor gap).
5. Denominator floor: \(B_r,B_r^\star\ge B_{\min}>0\).
6. **The set \(\mathcal{A}_r\), the composition matrix \(M_r\), and the P2 feasible set \(\mathcal{C}_r\) are identical** for the ideal and practical references. All other P2 state (\(V_r\), \(\lambda\), debt) is held fixed.

If (1) fails because some risk unit has \(\pi^{\mathrm{tar}}=0\) while Design still changes \(\widehat\zeta\), A5 is **false** and the theorem does not apply. That is the U-Air Design case (G1: \(25.5\%\) zero-target units; \(\mathcal{A}_r\) overlap \(51.6\%\)).

Production Design uses the frozen generator \(\pi^{\mathrm{opp}}\), so the implemented \(\varepsilon_\pi\) is \(0\). The symbol is kept so the bound also covers a lagged \(\widehat\pi\) implementation.

## Lemma 1 (Hájek denominator)

Let \(b,b^\star\ge0\) and \(B=\mathbf{1}^\top b\), \(B^\star=\mathbf{1}^\top b^\star\), with \(B,B^\star\ge B_{\min}>0\). Then

\[
\bigl\|b/B-b^\star/B^\star\bigr\|_1
\le
\frac{2}{B_{\min}}\,\|b-b^\star\|_1.
\]

*Proof.*  
\(\widehat{\boldsymbol\beta}-\boldsymbol\beta^\star=(B^\star(b-b^\star)+(B^\star-B)b^\star)/(BB^\star)\).  
The \(\ell_1\) triangle inequality and \(|B-B^\star|\le\|b-b^\star\|_1\), \(\|b^\star\|_1=B^\star\) give

\[
\|\widehat{\boldsymbol\beta}-\boldsymbol\beta^\star\|_1
\le
\frac{B^\star\|b-b^\star\|_1+\|b-b^\star\|_1\,B^\star}{BB^\star}
=\frac{2\|b-b^\star\|_1}{B}
\le\frac{2\|b-b^\star\|_1}{B_{\min}}.
\]

Also \(\|\cdot\|_2\le\|\cdot\|_1\), so the same right-hand side bounds the \(\ell_2\) gap.

## Lemma 2 (clip is a residual, not zero)

\(\lvert\min\{c,x\}-x\rvert=(x-c)_+\) for \(c>0\). Hence \(\lvert a-\widetilde a\rvert=\rho^{a}\) and \(\lvert d-\widetilde d\rvert=\rho^{d}\). Write

\[
\varepsilon_{\mathrm{clip}}
=\max\Bigl\{\max_{k,i}\rho^{a}_{k,r,i},\;\max_k\rho^{d}_{k,r}\Bigr\}.
\]

## Lemma 3 (first-stage Lipschitz on target support)

On a target-supported observed unit, \(\zeta=\pi^{\mathrm{tar}}/\pi^{\mathrm{opp}}\) and \(\widehat\zeta=\pi^{\mathrm{tar}}/\max\{\widehat\pi^{\mathrm{opp}},\pi_{\min}\}\). Under A5,

\[
\lvert\widehat\zeta-\zeta\rvert
\le\frac{\varepsilon_\pi}{\pi_{\min}^2},
\qquad
\bigl\lvert\widetilde a-a^\star\bigr\rvert
\le
\frac{\varepsilon_\pi}{\pi_{\min}^2 p_{\min}}
+\frac{\varepsilon_p}{\pi_{\min}\,p_{\min}\,p_{\min}^{\mathrm{true}}}.
\]

*Proof.*  
\(\lvert\widehat\zeta-\zeta\rvert=\pi^{\mathrm{tar}}\lvert\widehat\pi-\pi\rvert/(\widehat\pi\,\pi)\le\varepsilon_\pi/\pi_{\min}^2\) because \(\pi^{\mathrm{tar}}\le1\).  
\(\widetilde a-a^\star=(\widehat\zeta-\zeta)/\widetilde p+\zeta(1/\widetilde p-1/p)\) with \(\widetilde p=\max\{\widehat p,p_{\min}\}\ge p_{\min}\) and \(p\ge p_{\min}^{\mathrm{true}}\), so \(\lvert1/\widetilde p-1/p\rvert\le\varepsilon_p/(\widetilde p\,p)\).  
\(\zeta=\pi^{\mathrm{tar}}/\pi^{\mathrm{opp}}\le1/\pi_{\min}\).

Then \(\lvert a-a^\star\rvert\le\lvert\widetilde a-a^\star\rvert+\rho^{a}\).

## Lemma 4 (second-stage Lipschitz)

\[
\bigl\lvert\widetilde d-d^\star\bigr\rvert
\le\frac{\varepsilon_q}{q_{\min}q_{\min}^{\mathrm{true}}},
\qquad
\lvert d-d^\star\rvert
\le
\frac{\varepsilon_q}{q_{\min}q_{\min}^{\mathrm{true}}}+\rho^{d}.
\]

## Lemma 5 (unnormalized mass)

\(\lvert m_k-m_k^\star\rvert\le n_r(\lvert\widetilde a-a^\star\rvert_\infty+\varepsilon_{\mathrm{clip}})\).  
\(\lvert b_k-b_k^\star\rvert\le m_k\lvert d-d^\star\rvert+d^\star\lvert m-m^\star\rvert\).  
Using \(m_k\le n_r a_{\max}\) and \(d^\star\le1/q_{\min}^{\mathrm{true}}\le d_{\max}\) (A5.2 plus \(d_{\max}\ge1/q_{\min}\)),

\[
\|b-b^\star\|_1
\le
K_r n_r
\Bigl(
\frac{d_{\max}}{\pi_{\min}^2 p_{\min}}\varepsilon_\pi
+\frac{d_{\max}}{\pi_{\min}p_{\min}p_{\min}^{\mathrm{true}}}\varepsilon_p
+\frac{a_{\max}}{q_{\min}q_{\min}^{\mathrm{true}}}\varepsilon_q
+(a_{\max}+d_{\max})\varepsilon_{\mathrm{clip}}
\Bigr).
\]

## Theorem (practical plug-in perturbation)

**Assume A1, A4, and A5.** Let \(\boldsymbol\alpha^\star(\boldsymbol\beta)\) be the unique P2 minimizer at a fixed \((\mathcal{C}_r,M_r,\ldots)\). Write \(\widehat{\boldsymbol\alpha}_r=\boldsymbol\alpha^\star(\widehat{\boldsymbol\beta}_r)\) and \(\boldsymbol\alpha_r^\star=\boldsymbol\alpha^\star(\boldsymbol\beta_r^\star)\). Then

\[
\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_1
\le
C_1\bigl(\varepsilon_\pi+\varepsilon_p+\varepsilon_q+\varepsilon_{\mathrm{clip}}\bigr),
\]

\[
\|\widehat{\boldsymbol\alpha}_r-\boldsymbol\alpha_r^\star\|_2
\le
\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_2
\le
\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_1,
\]

\[
\|M_r(\widehat{\boldsymbol\alpha}_r-\boldsymbol\alpha_r^\star)\|_2
\le
\|M_r\|_2\,\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_2,
\]

where

\[
C_1
=
\frac{2K_r n_r}{B_{\min}}
\max\Biggl\{
\frac{d_{\max}}{\pi_{\min}^2 p_{\min}},\;
\frac{d_{\max}}{\pi_{\min}p_{\min}p_{\min}^{\mathrm{true}}},\;
\frac{a_{\max}}{q_{\min}q_{\min}^{\mathrm{true}}},\;
a_{\max}+d_{\max}
\Biggr\}.
\]

*Proof.* Lemma 5 plus Lemma 1 give the \(\boldsymbol\beta\) bound. The \(\boldsymbol\alpha\) bound is the already-proved P2 reference non-expansion (appendix, variational inequality on the common convex \(\mathcal{C}_r\); \(\lambda_\beta>0\) is A4). The last display is the definition of the operator 2-norm. Columns of \(M_r\) are nonnegative and sum to one, so also \(\|M_r v\|_1\le\|v\|_1\).

## Corollary (link to Proposition 2)

Let \(\Phi_R\) be the pooled Hájek functional of Proposition 2 and let \(\varepsilon_{\mathrm{sample},r}\) be the finite-window gap between \(\boldsymbol\beta_r^\star\) and the restriction of that pooled limit to the current support (including the feasibility gap of the appendix). Then

\[
\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta^{\mathrm{pool}}_r\|_1
\le
C_1\bigl(\varepsilon_\pi+\varepsilon_p+\varepsilon_q+\varepsilon_{\mathrm{clip}}\bigr)
+\varepsilon_{\mathrm{sample},r}.
\]

Under A3, \(\varepsilon_{\mathrm{sample}}\) of the *pooled* functional vanishes in probability. **It need not vanish in one window.** That is already why P2 exists. This corollary does **not** say the practical estimator is unbiased.

## What the constant says

- If \(\pi_{\min}\to0\) or \(B_{\min}\to0\), \(C_1\to\infty\). The bound is vacuous exactly when Design hits a support hole or the Hájek denominator collapses.
- If clip is inactive on target support, \(\varepsilon_{\mathrm{clip}}=0\) and the remaining terms are ordinary plug-in errors.
- If production uses frozen \(\pi^{\mathrm{opp}}\), drop \(\varepsilon_\pi\).
- The map \(\boldsymbol\beta\mapsto M_r\boldsymbol\alpha^\star(\boldsymbol\beta)\) is 1-Lipschitz in \(\ell_2\) once \(M_r\) is absorbed. Plug-in error cannot be amplified by P2 **while \(\mathcal{A}_r\) is fixed**.

## Scope

The theorem is a **stability** result, not an unbiasedness result, and not a statement about Design versus No-Design when those two rules produce different \(\mathcal{A}_r\).
