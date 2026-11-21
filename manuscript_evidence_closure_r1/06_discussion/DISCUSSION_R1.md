# Discussion

## 1. Why structural target alignment is the primary empirical success criterion

The paper's problem is that usable-update distributions can differ from the intended deployment target. Reducing \(\Delta_{\mathrm{group}}\) and \(\Delta_{c,s}\) directly measures whether correction/calibration moved mass toward that public target. RMSE\(_\mu\) remains necessary as a deployment-risk companion, but it is not the sole success definition.

## 2. Why improved structural alignment need not yield universal RMSE gains

Target-weighted RMSE can stay similar when methods already fit the observed support well, when residual error is dominated by measurement noise, or when structural reweighting trades error across groups. Selective RMSE gains (and null RMSE Holm tests against window baselines on SensorScope) are therefore compatible with a structural success.

## 3. Why component trade-offs are expected

RAVEN couples design, observation, usability, instantaneous calibration, and debt. Removing one factor can help one endpoint while hurting another because the remaining modules re-equilibrate. Fig.~3 is intended to display mixed signs, not a uniform benefit story.

## 4. What Use = NO_CLEAR_EFFECT means and does not mean

It means that, in the sealed Complete-aligned E4 family, dropping usable-update IPW produced no Holm-significant robust marginal effect. It does **not** mean that usable updates are scientifically irrelevant, that \(U\) can be ignored in the generative model, or that Use is proven unnecessary in every MCS regime.

## 5. Why Debt can be statistically stable but practically small

Paired tests can detect a consistent direction whose magnitude is tiny relative to \(\Delta_{\mathrm{group}}\) level. The paper therefore reports Debt as structurally supported and quantitatively small, not as a large practical lever.

## 6. Traffic source-vintage limitation

E2 Traffic is valid for C1–C2. E3 reused-old versus new-current Traffic is `NOT_COMPARABLE`. No table or figure may treat them as one homogeneous performance block.

## 7. P2 feasibility versus exact optimality

Warning-affected windows were feasibility-audited. Exact post-hoc optimality is not reconstructable from sealed outputs (C10). Theoretical uniqueness under stated assumptions is a theory claim, not an experimental certificate.

## 8. External-validity limitation

Current core evidence does not contain a formal T-Drive performance block. Real taxi-mobility opportunity remains a protocol-sealed reserve, not a present result.
