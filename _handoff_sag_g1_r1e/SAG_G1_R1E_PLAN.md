# SAG G1-R1e plan

R1d verdict is `DYNAMIC_COV_TOO_CONSERVATIVE`. This round freezes that evidence, attributes vacuity, and allows at most one pre-registered TOD predictor plus one calibration repair.

## Protocol

- Write only under `outputs/sag_g1_r1e/`. Do not rewrite `outputs/sag_g1_r1d/`.
- Keep TARGET_LAW_RULE_V1, thresholds, `pi_safe` q10, `delta=0.05`, `L=8`.
- Do not run SAG or 5-seed.

## Execution

1. Hash R1d inputs and copy frozen thresholds.
2. Repair `0.0 -> NaN` evidence serialization.
3. Artifact-freeze PI_SAFE_RULE_V1(q10) by reconstructing the same public-opportunity quantile R1d used.
4. Attribute R1d `C_real_support`, `C_point`, `C_lcb` from existing CSVs and draw three diagnostic figures.
5. Audit whether a legal pre-window UTC window schedule exists for sealed E3 traces.
6. If no legal `window_id -> UTC timestamp` mapping exists, STOP with `NO_LEGAL_PREWINDOW_CONTEXT_FOR_R1E` rather than inventing an origin or reading current EventTrace rows.
7. TOD predictor and Stage 1/2 helpers remain implemented and unit-tested, but sealed-trace Stage 1/2 run only if the context audit is legal.
8. Tests + anti-post-hoc + report + zip.
