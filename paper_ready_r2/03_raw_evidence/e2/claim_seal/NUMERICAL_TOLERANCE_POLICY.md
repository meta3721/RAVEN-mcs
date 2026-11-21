# NUMERICAL_TOLERANCE_POLICY

- **EPS_ZERO** = `1e-12`
- **Rationale**: Paired Delta_group differences of order 1e-16..1e-17 are floating-point noise, not scientific effects. Zeroing abs(d)<=1e-12 before inference prevents Wilcoxon pseudo-significance from all-ties machine-epsilon vectors.
- **Metrics**: Head_RMSE, Tail_RMSE, Delta_group
- **Implementation**: `src/raven_mcs/e2/traffic_final_seal/__init__.py::apply_eps_zero`
- Raw reconstructed metric values are **not** modified; only paired-difference inferential analysis is tolerance-normalized.
