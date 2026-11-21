# Pair Metric Name and Definition Audit

Outcome: **CURRENT_V4_IS_DELTA_C_S_NOT_DELTA_PAIR**

Frozen V3 defines atomic Delta_pair on (client, atomic_unit). Frozen V1/protocol and distribution.delta_c_s define client×stratum L1. Production V4 common support is client×target_group and uses delta_c_s — therefore it is Delta_c_s, not atomic Delta_pair.

Sources: protocol_closure pair defs, V3 E3_DELTA_PAIR_EXACT_DEFINITION, V4 common-support domain, P10 Delta_c-s note, FORMULA_TO_CODE_MAP F7.4/F7.5.
