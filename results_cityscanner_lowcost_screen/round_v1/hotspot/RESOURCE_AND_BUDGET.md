# Hotspot screen resources

H0 asset audit is recorded separately and is outside the inference cap.

## H0 audit file

# H0 step 1 resources

This is the cost of freezing the rules and checking assets and slots.
It is not part of the inference budget.

- wall_seconds: 0.921932
- cpu_seconds: 1.031250
- peak_rss_bytes: 109064192

## This driver

- Audit CPU seconds: 0.015625
- Audit wall seconds: 0.030581
- Inference CPU seconds, including failed attempts and cache verification: 51.125000
- Rows with cpu_not_sampled exited before the CPU watch. Their CPU is absent from the total and their wall is included.
- Inference cap CPU seconds: 600
- Inference active wall seconds: 59.293404
- Inference cap wall seconds: 1200
- Statistics CPU seconds: 33.093750
- Statistics cap CPU seconds: 180
- Statistics active wall seconds: 35.571642
- Statistics cap wall seconds: 600
- Peak RSS bytes across driver commands: 700751872
- Minimum available bytes observed: 1959743488
- Cache-reuse model count: 0
- Failure CPU seconds, already included in the pool totals: 0.000000

Shared prediction cost is recorded once in the inference pool. Later stages read the shards and charge their own statistics time.
