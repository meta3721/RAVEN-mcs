# Anti-post-hoc audit

- 1. 是否改 tau_cov？必须 false。 `False`
- 2. 是否改 delta_cal？必须 false。 `False`
- 3. 是否改 pi_safe q10 rule？必须 false。 `False`
- 4. 是否扫 L？必须 false。 `False`
- 5. 是否比较多个 predictor 后挑最好？必须 false。 `False`
- 6. 是否使用 current R/O/U？必须 false。 `False`
- 7. 是否使用 dataset name 做 predictor/Gate feature？必须 false。 `False`
- 8. 是否根据 RMSE 选择 predictor/calibration？必须 false。 `False`
- 9. Stage2 是否只有在预注册 bottleneck trigger 下运行？ `True`
- 10. 是否运行 SAG？必须 false。 `False`
- 11. 是否运行 5-seed？必须 false。 `False`
- 12. 是否执行 synthetic stress？必须 false。 `False`
- 13. 是否改 TARGET_LAW_RULE_V1？必须 false。 `False`
- 14. 是否重写 R1d 原 artifacts？必须 false。 `False`

protocol_ok: True
