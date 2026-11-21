# III–VI audit for \(\pi^{\mathrm{sc}}\)

## III. Target semantics

The public atomic deployment target \(\varpi^{\mathrm{test}}\) and its group marginal \(\mu\) are unchanged. P2 and RMSE still evaluate against the sealed test artifact.

\(\pi^{\mathrm{sc}}\) is a **working Design measure**: the unique equal mixture of the opportunity-supported projection of \(\pi^{\mathrm{test}}\) and the frozen \(\pi^{\mathrm{opp}}\). It is public, label-independent, and fixed before seeing outcomes.

Compatibility \(\sum_k\pi^{\mathrm{test}}_{k,i}=\varpi_i^{\mathrm{test}}\) still holds for the evaluation target. It is **not** claimed for \(\pi^{\mathrm{sc}}\). The paper must say Design uses a support-compatible working measure, not that \(\pi^{\mathrm{sc}}=\pi^{\mathrm{test}}\).

## IV. Identifiability / overlap

On \(S_{\mathrm{feas}}\), \(\pi^{\mathrm{sc}}_{k,s}\ge\tfrac12\pi^{\mathrm{opp}}_{k,s}\). Whenever the production denominator is positive, the numerator is positive. The G1 U-Air failure mode (\(\pi^{\mathrm{test}}=0\Rightarrow\zeta=0\Rightarrow m=0\)) is removed by construction.

The Design ratio is now
\[
\zeta^{\mathrm{sc}}
=
\frac{\pi^{\mathrm{test,feas}}}{2\pi^{\mathrm{opp}}}
+
\frac12,
\]
which is a shrinkage of the old ratio toward \(1/2\), plus a strictly positive floor on train-only strata.

## V. Estimation

No new propensity estimator. \(\pi^{\mathrm{opp}}\) is the same frozen joint law as E3. \(\hat p\) and \(\hat q\) are unchanged. Oracle vs estimated is therefore not reopened by this patch.

## VI. Finite-sample / training support

Clients whose current risk set lies on train-only strata keep \(m>0\) and can enter \(E_r/A_r\). That restores the sample Design had been discarding on U-Air. It also mildly shrinks SensorScope \(\zeta\) toward \(1/2\); the val gate checks that this does not break SensorScope.

## What this is not

- Not G1-B reliability gating (`g(\zeta-1)`).
- Not a test-tuned \(\varepsilon\)-floor.
- Not a claim that \(\pi^{\mathrm{sc}}\) is the unique theoretically mandated lift — it is the pre-registered equal barycenter.
