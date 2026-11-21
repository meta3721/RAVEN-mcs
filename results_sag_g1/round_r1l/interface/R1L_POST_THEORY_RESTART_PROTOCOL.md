# Post-R1l experiment restart protocol

Formal experiments restart only after THEORY_CLOSURE_PASS.

They must NOT jump to SAG.

## Next round: R1m

R1m — Aggregate Certificate Implementation under Frozen Theory

Must:
- implement the exact R1l definitions;
- use n_min = 19;
- forbid clipped-k conformal as a 95% certificate;
- freeze one predictor before results;
- freeze one stable-regime rule before results;
- implement WARMUP/CERTIFIED/RESET;
- test theorem conditions;
- report empirical validity, false-safe, false-unsafe, non-vacuity;
- focus on SensorScope a=0.40 and U-Air a=0.20;
- retain the full frozen stress track {1.00, 0.80, 0.60, 0.40, 0.20};
- STOP before SAG.

Only if R1m passes: SAG 1-seed functional validation.
Only after that passes: 5-seed main validation.
