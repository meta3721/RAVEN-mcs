# P2 paper wording (final)

Although the solver emitted numerical-inaccuracy warnings on a subset of P2
invocations, an offline audit of all affected formal runs verified that the
returned allocations satisfied the reconstructable frozen feasibility
constraints within the prescribed numerical tolerance. Exact optimality could
not be reconstructed because the complete native solver state and objective
inputs were not persisted.

Semantic levels:
- LEVEL 1 feasibility is certified for the warning-affected sealed outputs.
- LEVEL 2 exact optimality is not certified.
- LEVEL 3: optimality is not reconstructable from sealed outputs.

Do not write that “all inaccurate solves were proven optimal.”
