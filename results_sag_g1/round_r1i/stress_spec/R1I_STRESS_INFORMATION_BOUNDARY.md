# Stress information boundary

Availability level `a` is a scenario-level public exogenous parameter known before the window.
The realized entity mask is **not** pre-window fully observed information.
A future predictor/certificate may use `a` and must not use the current-window realized mask unless the paper model explicitly allows it.
This round computes oracle only.
