# Final one-factor w/o-Inst specification

RAVEN-w/o-Inst = full RAVEN with ONLY instantaneous/current target calibration removed.

## Required identities
{
  "Design": "full",
  "Obs": "full",
  "Use": "full",
  "Debt": "full",
  "lambda_beta": 1.0,
  "lambda_v": 0.1,
  "lambda_s": 0.1,
  "alpha_bounds": 0.5,
  "ESS_constraints": 3.0,
  "EventTrace": "matched E3 full-RAVEN per dataset\u00d7seed"
}

## Only change
{
  "lambda_group": 0.0,
  "instant_calibration": false
}
