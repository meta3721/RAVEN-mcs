# Oracle ceiling derivation

Let the certified set at window `r` be

```
S_cert(r) = { (k,s) : lower_pi_opp[k,s,r] >= pi_safe }
```

If joint lower-bound validity holds:

```
lower_pi_opp[k,s,r] <= pi_opp_realized[k,s,r]  for all target-positive (k,s)
```

then `(k,s) in S_cert(r)` implies `pi_opp_realized[k,s,r] >= pi_safe`.

Define the oracle-safe support set:

```
S_oracle_safe(r) = { (k,s) : pi_opp_realized[k,s,r] >= pi_safe }
```

Hence `S_cert(r) subseteq S_oracle_safe(r)` and

```
C_cov(r) <= C_oracle_safe(r)
```

where `C_cov` is the formal certified target-mass fraction.

The loose realized-support ceiling uses any positive realized opportunity:

```
C_real_support(r) = sum pi_tar * 1{pi_opp_realized > 0} / sum pi_tar
C_oracle_safe(r) = sum pi_tar * 1{pi_opp_realized >= pi_safe} / sum pi_tar
```

Therefore:

```
C_cov(r) <= C_oracle_safe(r) <= C_real_support(r)
```

This derivation depends only on frozen target mass, frozen `pi_safe`,
and realized opportunity. No new predictor is required.

Numerical tolerance for pass comparisons: `1e-12`.
