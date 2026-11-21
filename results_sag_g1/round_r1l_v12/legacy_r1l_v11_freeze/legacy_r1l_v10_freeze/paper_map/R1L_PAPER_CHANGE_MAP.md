# Paper changes implemented in R1l (theory sealed in Overleaf)

R1l edits `TO_OVERLEAF_paper_tmc_r1_clean` to seal the coverage-certificate
stack. Existing reconstruction Proposition~\ref{prop:risk} /
Theorem~\ref{thm:calibration} are not overwritten. Coverage results use
distinct labels.

## Section III (`subsec:agg_coverage_object`)

- Define \(C_t\) as the unique aggregate certification target (`eq:agg_Ct`).
- Keep TARGET_LAW_RULE_V1, PI_SAFE_RULE_V1, \(\tau_{\mathrm{cov}}=0.05\).
- Distinguish realized \(C_t\), predicted \(\widehat C_t\), certified \(C^{\mathrm{LCB}}_t\).

## Section IV (`subsec:pairwise_barrier`)

- Explain why pairwise simultaneous positive LCB is structurally vacuous under
  sparse/hidden availability (`prop:pairwise-lcb-barrier`, `cor:availability-barrier`).
- Introduce aggregate certification. Pairwise LCB remains motivation /
  diagnostic only, not the Gate object.

## Section V (`subsec:agg_certificate_alg`, `alg:agg_certificate`)

- Predictor information boundary.
- Score \(S_t=\widehat C_t-C_t\).
- Finite-sample quantile and \(n_{\min}=19\).
- WARMUP / CERTIFIED / RESET written into the algorithm.
- \(\mathrm{Gate}_t=1\{C^{\mathrm{LCB}}_t\ge\tau_{\mathrm{cov}}\}\).

## Section VI (`subsec:agg_coverage_theory`)

- `thm:agg-lcb`, `cor:false-safe-gate`, `prop:drift-boundary`,
  `ass:score-exchangeability`, stated completely.

## Appendix (`app:agg_coverage_proofs`)

- Complete proofs: rank, ties, \(k_n\), \(n_{\min}\), clipping at zero.
- Optional bounded-drift extension omitted.

## Formal Gate path in code

`window_runner` default `sag_cov_mode=aggregate_stable_regime`.
`compute_certificates` uses `r1l_state.certificate_step` for \(C_{\mathrm{cov}}^{\mathrm{LCB}}\).
Pairwise `event_count_cp` / `dynamic_max_residual` remain explicit diagnostic modes.
