# E4 source diff classification (Task A)

## Full-mode equivalence
E3 window_runner hash f7bff5e... always called compute_server_weights. E4 pre-repair 3d44cecb... gated that call on uses_instant_calibration; for method=raven that flag is True, so the gate is a no-op and full-mode matches E3. Other ablation policy flips are False only on the ablated factor and do not execute under full RAVEN.

- E3 window_runner: `f7bff5e30c76898f5ab3e3998021f9b09e52ccf73f135b44bc4e141d9e13c436`
- E4 pre-repair window_runner: `3d44cecb6fb08d843f582f41799da99c590ee2676effdd9e7ec5a8c11004144e`
- Current window_runner: `77f579719a73b80b69e09ebd00017bd9d507d77af8cfa5b3d0b5f216f007a676`
- Classification: `FULL_MODE_EQUIVALENT_NOOP_GATES`

## Ablation switch regression
- status: `PASS`
- full-mode P2 fixture passes: `True`

