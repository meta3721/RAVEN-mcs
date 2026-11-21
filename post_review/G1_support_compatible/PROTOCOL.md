# Path A protocol — support-compatible Design target

Pre-registered before looking at new-method test endpoints.
Date: 2026-08-24

## Formula (no free parameter)

Let \(S_{\mathrm{feas}}\) be the frozen TRAIN client×stratum support and \(\pi^{\mathrm{opp}}\) the frozen joint opportunity law already used as the Design denominator.

\[
\pi^{\mathrm{test,feas}}
=
\Pi_{S_{\mathrm{feas}}}(\pi^{\mathrm{test}}),
\qquad
\pi^{\mathrm{sc}}
=
\tfrac12\pi^{\mathrm{test,feas}}
+
\tfrac12\pi^{\mathrm{opp}}.
\]

Evaluation \(\mu\) stays the sealed test artifact. Only the Design-ratio numerator changes. The 1/2 weights are the unique equal barycenter; they are not tuned on any endpoint.

## Seeds

- VAL: 30001–30010
- TEST: 30011–30020 (one look, only if the val gate passes)

## Methods

- `raven_sc_target`: full RAVEN, `pi_target_mode=support_compatible`
- Contrasts (sealed, not retrained): `raven`, `raven_wo_design`, `raven_simoracle`

## Val gate (must all hold)

1. U-Air VAL: `raven_sc_target` vs `raven_wo_design` on \(\Delta_{\mathrm{group}}\), RMSE\(_\mu\), Tail RMSE — mean relative change \(\ge -0.5\%\) (non-inferior).
2. U-Air VAL: \(\Delta_{c\text{-}s}\) of `raven_sc_target` still \(\le\) `raven_wo_design` (keep the structural direction).
3. SensorScope VAL: `raven_sc_target` vs sealed `raven` on \(\Delta_{\mathrm{group}}\) and \(\Delta_{c\text{-}s}\) — mean relative change \(\ge -0.5\%\).

If any fail: **PATH_A_FAILS**, stop, do not open TEST, recommend Path B.

If all pass: one TEST look with the same three rules (report only; do not retune).
