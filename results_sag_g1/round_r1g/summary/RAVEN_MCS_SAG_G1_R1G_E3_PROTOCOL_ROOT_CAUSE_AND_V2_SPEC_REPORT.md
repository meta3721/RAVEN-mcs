# RAVEN-MCS SAG G1 R1G E3-v1 Root-Cause + E3-v2 Spec Report

## Executive verdict: E3V2_ORACLE_REGIME_NOT_USABLE

STOP. No dynamic certificate, no SAG, no 5-seed.

## Answers

1. Raw timestamps exist in processed atomic `absolute_time` (UTC).
2. Timestamp drops at E3-v1 logical window construction: deadline=window_id+1.0, metadata has no UTC.
3. Raw natural train windows keep continuity: SS lag1 Jaccard=0.8333333333333334; U-Air=0.8343949044585988.
4. E3-v1 does not: SS lag1=0.012217412217412217; U-Air=0.01952983725135624.
5. lag-1 Jaccard drop is the raw−E3 difference in E3V1_TEMPORAL_RETENTION_SUMMARY.csv.
6. Autocorr raw vs E3-v1: see same CSV `opportunity_mass_autocorr_lag1`.
7. Persistence raw vs E3-v1: `mean_persistence_length`.
8. Co-occurrence: raw vs E3 mean risk-set size in E3V1_SAMPLING_DISTORTION_SUMMARY.csv.
9. Target-mass-weighted support: raw vs E3 means in the same summary.
10. Sampler resamples from the global train pool each logical window (replace=False, k=4), mixing original hours.
11. Target vs realized mismatch TV: SS=0.45454545454545675; U-Air=0.36810990490616774.
12. CF1 vs CF0 mean C_oracle_safe SS: 0.06852142509896524 vs 0.018335267991494025; U-Air 0.09333333333333334 vs 0.02785908931082979.
13. CF2 vs CF1 SS: 0.06852142509896524 vs 0.06852142509896524; U-Air 0.09333333333333334 vs 0.09333333333333334.
14. Root cause codes: RC-A+RC-B+RC-C+RC-D.
15. Single dominant cause: False.
16. Strict 'sampling caused ceiling': True.
17. Cautious statement: Cross-time train-pool resampling (E3-v1) removes natural co-occurrence and temporal continuity. CF1/CF2 restore within-window membership at the frozen k=4 cap; treat them as diagnostics, not E3-v2.
18. E3-v2 uses real UTC timestamp (window_start_utc).
19. Window rule frozen before precheck: `078eb96bfe869489edd75a17950537cd191babc37f38235fe1260680a9e3299f`.
20. E3-v2 windows follow chronological real hours (test split).
21. Natural co-occurrence: full units in that UTC hour, no global resample.
22. Public context is pre-window (start UTC / TOD / weekday).
23. Current R/O/U forbidden (ContextLeakageError).
24. Target law unchanged: True.
25. pi_safe rule hash `aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7`.
26. tau_cov still 0.05: True.
27. EventTrace maps to raw interval via window_start_utc + time_index + raw_window_source_hash.
28. Hash replay match SS=True U-Air=True.
29. E3-v2 windows: SS=62 U-Air=53 (test split hours).
30. mean/median/max C_oracle_safe_v2 SS=0.13339412011138765/0.14056531703590525/0.17112299465240646; U-Air=0.21151182230714122/0.22784810126582278/0.2658227848101266.
31. fraction_oracle_pass_v2 SS=1.0 U-Air=0.9056603773584906.
32. Multiple safe/unsafe: SS pass=62 fail=0; U-Air pass=48 fail=5.
33. Routing SS=E3V2_ORACLE_ALL_SAFE U-Air=E3V2_ORACLE_ALL_SAFE.
34. Joint E3V2_ORACLE_REGIME_USABLE: False.
35. Predictor modified: False.
36. Calibration modified: False.
37. tau modified: False (still 0.05).
38. SAG run: False.
39. 5-seed run: False.
40. pytest R1g: PASS passed=27 failed=0.
41. full pytest: PASS passed=30 failed=0.
42. R1G-S0–S24 artifact-derived: n_pass=25 n_fail=0.
