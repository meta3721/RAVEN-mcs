# R1d non-vacuity attribution

C_real_support is a post-hoc diagnostic. It is not a certificate and does not enter the Gate.

## sensorscope

- n_warmup: 84
- mean C_real_support: 0.01833526799149408
- mean C_point: 0.1323157362118398
- point_zero_fraction: 0.0
- mean C_lcb: 7.176424288723723e-05
- lcb_zero_fraction: 0.9761904761904762
- median q / pi_safe: 74.09065879812032
- median q / median_positive_hat: 3.0
- joint_coverage: 0.9761904761904762

Primary vacuity source: calibration penalty (global max-residual q) shrinks an otherwise non-vacuous point predictor.

## uair

- n_warmup: 64
- mean C_real_support: 0.02785908931082983
- mean C_point: 0.19526305379746844
- point_zero_fraction: 0.0
- mean C_lcb: 0.0
- lcb_zero_fraction: 1.0
- median q / pi_safe: 33.677572180963786
- median q / median_positive_hat: 3.0
- joint_coverage: 1.0

Primary vacuity source: calibration penalty (global max-residual q) shrinks an otherwise non-vacuous point predictor.
