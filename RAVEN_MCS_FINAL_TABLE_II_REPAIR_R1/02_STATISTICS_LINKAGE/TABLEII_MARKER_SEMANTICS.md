# Table II marker semantics

**numerical_best / bold:** lowest mean among primary methods for that dataset×metric. Not a significance claim.

**holm_sig_vs_RAVEN / dagger:** Holm-adjusted paired Wilcoxon vs RAVEN is significant (p_holm < 0.05) in the frozen E3 Holm families.

These marks are independent. A numerically best cell is not marked statistically significant unless the frozen Holm result supports it.

Holm families and tests are unchanged. U-Air prediction *means* now use per-seed FIG-E3 RMSE_mu; sealed Holm files remain those computed on the original paired seed vectors (Wilcoxon ranks are invariant to a positive constant rescaling).
