# Root-cause mechanism split

## Mechanism 1 — within-window support / co-occurrence

Affects **oracle coverage ceiling**. CF-M1 holds sampling budget matched to CF0 and only restricts the source pool to the same natural hour.
Observed mean Delta_oracle: {'sensorscope': 0.05018820751441073, 'uair': 0.06531997187060479}.

## Mechanism 2 — temporal continuity / order

Affects **pre-window predictability**, not the oracle ceiling itself. R1g CF1 vs CF2: same oracle mass, lag-1 Jaccard rises when order is restored (CF2).
    dataset cf_id  n_windows  mean_C_real_support  mean_C_oracle_safe  max_C_oracle_safe  n_oracle_pass  fraction_oracle_pass  mean_active_pair_count  lag1_jaccard
sensorscope   CF1        100             0.068521            0.068521           0.093340             76                  0.76                    30.0      0.048082
sensorscope   CF2        100             0.068521            0.068521           0.093340             76                  0.76                    30.0      0.381319
       uair   CF1         80             0.093333            0.093333           0.236287             32                  0.40                    32.0      0.157592
       uair   CF2         80             0.093333            0.093333           0.236287             32                  0.40                    32.0      0.683763

Do not collapse both into “sampling destroyed coverage”.
