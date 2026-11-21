# PAPER_H_MAPPING_SPEC

Authority used: PostAudit III–VI; `FINAL_H_S_MANUSCRIPT_SEMANTICS_R1.json`; TABLE I dataset protocol; G2 PROTOCOL; `RepeatableTimeOfDayMapper`.

## 1) What `h(i)` is

The **deployment group** of atomic unit `i`. It identifies the application-level mass the deployed predictor should serve. Public target group mass is

```
μ_g = ∑_{i: h(i)=g} ϖ_i^{tar}
```

For SensorScope and U-Air the sealed manuscript semantics freeze:

| g | label | UTC hours |
|---:|---|---|
| 0 | H1 | 00–06 |
| 1 | H2 | 06–12 |
| 2 | H3 | 12–18 |
| 3 | H4 | 18–24 |

Construction: `RepeatableTimeOfDayMapper` = `(pd.to_datetime(absolute_time, utc=True).dt.hour // 6)`.  
`μ` is the **train-split** supported atomic mass marginalized to these four groups. Test labels are not used. Train/val/test share the same unit→`h` map because `absolute_time` is public metadata.

## 2) How `h(i)` differs from `s(i)`

PostAudit: `h(i) ≠ s(i)` in general.

- `h(i)`: application-level deployment group (here, four UTC TOD blocks).
- `s(i)`: opportunity stratum for selection modeling. Sealed E3 map is `spatial_id × four time blocks × weekday/weekend`.

`π^{tar}_{k,s}` and `C_cov` remain on `(k, s)`, not on `h(i)`.

## 3) Application-level group?

Yes. The paper’s four-group deployment partition is the service/evaluation grouping for `μ`, `M_r`, `ω_r = M_r α_r`, `Δ_group`, Theorem-4 `|G|`, and G2 WorstGroupRMSE.

## 4) May `h(i)` equal atomic spatial identity?

Not for SensorScope/U-Air. Sealed writing rule: **do not write `h(i)` as spatial × time.** Atomic identity and spatial×time `target_group` (`n_groups_runtime` 220/144) are a different object used in E3 pair-domain wiring.

## 5) How to construct from public/frozen metadata

1. Load processed atomic table (public `unit_id`, `absolute_time`, `split`, `support_flag`).
2. Map every unit with `RepeatableTimeOfDayMapper` (no labels, no current window, no test outcome).
3. Freeze `unit_id → {0,1,2,3}` and its hash.
4. Build `μ` from train-split supported units only, uniform over those units, then marginalize by `h(i)`.
5. Use that same map for `M_r` columns (`c^g_{k,r}`), P2 `|G|`, `B_srv = √|G|(…)`, and diagnostic WorstGroupRMSE.

This mapping is unique given the sealed semantics. Verdict is not `H_MAPPING_NOT_FROZEN`.
