# Selection-layer crosswalk

Real trajectory → R (REAL_FROM_TDRIVE) → adapter valid speed (DETERMINISTIC_DATA_QUALITY)
→ O (CONTROLLED_EXPERIMENTAL p_obs) → E/U (CONTROLLED_EXPERIMENTAL complete_aligned)
→ local correction (MODEL_INTERNAL) → server aggregation (MODEL_INTERNAL).

Only the opportunity layer is guaranteed real-mobility-derived.
