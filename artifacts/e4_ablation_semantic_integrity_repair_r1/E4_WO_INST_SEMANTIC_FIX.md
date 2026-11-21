# E4 raven_wo_inst semantic fix

## Bug
raven_wo_inst skipped P2 via window_runner uses_instant_calibration gate

## Parent evidence
- formal wo_inst runs: 40
- all P2_invoked=false: True

## Fix
{
  "window_runner": "always call aggregator.compute_server_weights",
  "aggregator": "RavenWoInstAggregator(lambda_group=0, lambda_beta=1e-8, instant_calibration=False)",
  "validate_p2_lambdas": "instant_calibration=False allows lambda_group=0 (ablation only)",
  "runner_p2_methods": "include raven_wo_inst"
}

## One-factor regression
- passes: True

