# G4 decision

**G4_ACCEPTED.**  
There is now a practical-estimator theorem that starts from the implemented clipped plug-in and ends at the P2 decision, with an explicit \(C_1\). It does not claim unbiasedness. It does not reopen Path B.

## What was proved

Same-window ideal \(\boldsymbol\beta_r^\star\) (true \(p,q,\pi\), no clip) versus implemented \(\widehat{\boldsymbol\beta}_r\):

\[
\|\widehat{\boldsymbol\beta}-\boldsymbol\beta^\star\|_1
\le
C_1(\varepsilon_\pi+\varepsilon_p+\varepsilon_q+\varepsilon_{\mathrm{clip}}),
\quad
\|\widehat{\boldsymbol\alpha}-\boldsymbol\alpha^\star\|_2
\le
\|\widehat{\boldsymbol\beta}-\boldsymbol\beta^\star\|_2,
\]

\[
\|M_r(\widehat{\boldsymbol\alpha}-\boldsymbol\alpha^\star)\|_2
\le
\|M_r\|_2\,\|\widehat{\boldsymbol\beta}-\boldsymbol\beta^\star\|_2.
\]

\(C_1=\dfrac{2K_r n_r}{B_{\min}}\max\{\ldots\}\) uses only positivity margins, the Hájek floor \(B_{\min}\), and the caps \(a_{\max},d_{\max}\). Clipping enters as \(\varepsilon_{\mathrm{clip}}=( \widetilde a-a_{\max})_+\), not as zero. A pooled \(\varepsilon_{\mathrm{sample}}\) is a separate Proposition 2 remainder; it is not stuffed into \(C_1\).

The already-proved P2 non-expansion is reused. No new convexity lemma.

## What G1 does with the bound

| Dataset | A5 | Theorem | G1 fact the bound explains |
|---|---|---|---|
| SensorScope | holds (\(\pi^{\mathrm{tar}}=0\) nowhere; \(\mathcal{A}_r\) stable) | applies | Oracle ≈ estimated. Plug-in error is a remainder after a 1-Lipschitz P2 map. |
| U-Air Design-on | **fails** (25.5% zero-target; \(\mathcal{A}_r\) overlap 51.6%) | **does not apply** | Oracle still reverses vs No-Design. That comparison changes \(\mathcal{A}_r\). W4 is not W1. |

Production Design uses frozen \(\pi^{\mathrm{opp}}\), so implemented \(\varepsilon_\pi=0\). Clip is modest (\(\zeta_{\max}\ll 20\)). ESS is a \(B_{\min}\) diagnostic, not the U-Air mechanism.

Numerical \(C_1 B_{\min}\) at unit scale is large if one uses the global \(\min\pi^{\mathrm{opp}}\) (\(\sim 10^{-3}\)), and still conservative if one uses \(1/\zeta_{\max}\). **Do not quote those numbers as a tight certificate.** The usable statement is: \(C_1<\infty\) iff A5 holds; on U-Air Design-on it does not.

## What was not done

- No edit to `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` or `_paper_work/main.tex`.
- No new training, no clip grid, no \(\lambda\) Pareto.
- No claim that Path B is “theory-justified Design gating” beyond: the bound’s hypothesis fails exactly where Design reverses.

Paste-ready TeX: `prop3_practical_estimator.tex`. Elementary inequalities: `tests/unit/test_g4_practical_estimator_lemmas.py` (passed).

## Next

G5 (solver/KKT audit + practical significance) is the next gate. Do not start it from this file. Do not rewrite the paper in this step.
