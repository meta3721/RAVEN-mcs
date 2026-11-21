# E3 Local-Hajek Wiring Audit

- WindowRunner computes a_bar from observed atomic records.
- uses_hajek_local_loss preserves a_bar; FedAvg replaces it with uniform 1/n.
- ClientTrainer passes a_bar to local_hajek_loss before backward().
- local_hajek_loss is differentiable weighted SSE.
- LocalHajekAggregator uses raw-count server aggregation.

**Classification:** LOCAL_HAJEK_IMPLEMENTATION_VALID.
