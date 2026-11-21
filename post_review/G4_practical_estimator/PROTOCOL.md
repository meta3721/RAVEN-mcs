# G4 protocol — practical-estimator theory (W5 + W4)

Date: 2026-08-24  
Gate: handbook §8  
Does not train. Does not rewrite `main.tex`. Does not change Path B.

## What this gate is

Proposition 2 is an identification/consistency statement for **ideal untruncated** sequential ratios under A1–A3. The implementation uses plug-in \(\hat\pi,\hat p,\hat q\) and clips \(a\le a_{\max}\), \(d\le d_{\max}\). The paper already says those two objects are not the same. G4 must **connect** them with an explicit perturbation bound, not add another convexity lemma.

## Theorem target (pre-registered form)

Fix an active window in which \(\mathcal{A}_r\), \(M_r\), and \(\mathcal{C}_r\) are the same for the two references. Under a quantitative positivity assumption A5:

\[
\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_1
\le
C_1\bigl(\varepsilon_\pi+\varepsilon_p+\varepsilon_q+\varepsilon_{\mathrm{clip}}\bigr),
\]

\[
\|\widehat{\boldsymbol\alpha}_r-\boldsymbol\alpha_r^\star\|_2
\le
\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_2,
\]

\[
\|M_r(\widehat{\boldsymbol\alpha}_r-\boldsymbol\alpha_r^\star)\|_2
\le
\|M_r\|_2\,\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_2.
\]

\(\boldsymbol\beta_r^\star\) is the **same-window** ideal reference (true propensities, no clip, same realized \(R,O,U\)).  
\(C_1\) is built from positivity margins, the Hájek denominator floor \(B_{\min}\), and the weight caps.  
A pooled sampling remainder \(\varepsilon_{\mathrm{sample}}\) is stated separately and sent to Proposition 2; it is not hidden inside \(C_1\).

## What we will not claim

- Unbiased practical estimator.
- Bound when \(\mathcal{A}_r\) changes (U-Air Design vs No-Design).
- Identification on \(\{\pi^{\mathrm{tar}}=0\}\).
- That the numerical \(C_1\) is tight, or that it “explains” the U-Air RMSE reversal.

## Correspondence (must be filled, not decorative)

| Symbol | G1 object |
|---|---|
| \(\varepsilon_\pi\) | frozen \(\pi^{\mathrm{opp}}\) vs realized; production Design uses frozen generator, so implemented \(\varepsilon_\pi=0\) |
| \(\varepsilon_p,\varepsilon_q\) | \(\hat p/\hat q\) panel; oracle-vs-estimated \(a\) gap |
| \(\varepsilon_{\mathrm{clip}}\) | clip rates; \(\zeta\) vs \(a_{\max}=20\) |
| \(B_{\min}\) / ESS | `ess_ratio_on_mean` |
| P2 perturbation | oracle-vs-estimated endpoints (same Design, \(\mathcal{A}_r\) shared) |
| A5 failure | U-Air \(25.5\%\) zero-target units; \(\mathcal{A}_r\) overlap \(51.6\%\) |

## Gate

| Verdict | Rule |
|---|---|
| `G4_ACCEPTED` | Statement + proof with explicit \(C_1\); clip residual is a named term; A5 failure on U-Air recorded; G1 table filled; no “unbiased plug-in” sentence. |
| `G4_FAIL` | Bound only works by setting clip \(=0\), or \(C_1\) is left as an unspecified constant, or the text claims the practical estimator is unbiased. |

Outputs stay under `post_review/G4_practical_estimator/`. A paste-ready TeX fragment is allowed. The submission `main.tex` is not edited in this gate.
