# Joint reading — Part I and Part II against the fixed III table

Instruction: `raven-mcs-estimand-gate-execution-prompt.md` §III, sha256 `ffb4bde6…`
Written 2026-10-07 after both decision files existed. The III table was fixed before either
result was known, so the row below is selected by its conditions, not by preference.

## Labels

| part | dataset | label | source |
| --- | --- | --- | --- |
| I | SensorScope | **`saturated`** (`d̄ = 0`, Wilson [0.000, 0.161]; regret 0.000000 [0, 0]) | `results_estimand_selection/round_v1/SELECTION_DECISION.json` |
| I | U-Air | **`saturated`** (same) | same |
| II | SensorScope | H1 **`null`** (slope +0.001365, CI [−0.003556, +0.006356]) | `results_gate_dose/round_v2/DOSE_DECISION.json` |
| II | U-Air | H1 **`null`** (slope −0.073079, CI [−0.165370, +0.022770]) | same |
| II | — | `gate_law = not supported`; H2 `not_tested`; H3 `null` | same |

## Row that applies

| Part I (SS / UA) | Part II | licensed contribution statement |
| --- | --- | --- |
| `null` / `saturated` / `inconclusive` on both | not `supported` | **Neither claim.** Fall back to writing up the bound (`results_evidence_axis/round_v1`, option C1), after the four corrections listed in that review. |

That is **line 4 of the III table**, and it is the row the labels select. The two positive
routes are foreclosed:

* **Not line 1 or 2.** Part I did not produce `open` on either dataset. Arrival-weighted
  validation never picks a different model than the deployment target does (`d̄ = 0`,
  regret identically 0), so the estimand does not convert into a selection cost. The
  misreport itself is large and real on SensorScope (`R_arr` understates deployment risk by
  ≈4.1 % for every candidate) but it is a level shift, not a ranking change.
* **Not line 3.** Part II did not produce `gate_law = supported`. The prediction cost of
  Design does not track ρ at a resolution the design can use: both slopes are `null`, and
  the only ρ-tracking movement is on the structural endpoint `Δ_c-s` (slope −0.1331 SS
  / −0.3565 UA, both intervals strictly negative), which is not the prediction endpoint.

## What the round does establish, and may be reported as measured

These are descriptive facts with intervals, not the table's headline claims:

1. **Arrival-weighted validation is a biased estimate of deployment risk** on SensorScope:
   `b = (R_arr − R_μ)/R_μ` is **−0.0411 to −0.0412** across all 9 candidates (Student-t 95 %
   intervals exclude zero), and **+0.0027 to +0.0062** on U-Air. The bias is near-constant
   across the candidate set, which is exactly why it does not move the ranking.
2. **The Design factor's cost does not follow ρ on the prediction endpoint.** SensorScope's
   dose response over ρ ∈ {0, 0.097, 0.245, 0.388} is at most **+0.17 %** against δ = 0.5 %;
   U-Air's is **+6.6 % to +7.5 %** at every level and *decreasing* in ρ (slope −0.073,
   CI containing zero).
3. **It does follow ρ on the calibration endpoint.** `r_Δc-s` is monotone in ρ on both
   datasets with intervals excluding zero (SensorScope −0.6 % → −5.8 %; U-Air −4.8 % →
   −8.8 %), a slope of −0.1331 (SS) / −0.3565 (UA).
4. **The gate cannot beat both fixed settings in this design**, structurally: at ρ = 0 the
   gate's rule *is* `always_on`, so that comparison is identically zero and the protocol's
   `open` condition is unreachable. `gate_decision = null` follows.
5. The round_v2 gate, under the amended and separately declared bound, confirms that the
   current tree's `raven` arm tracks its stored artifacts to ≤ 2.2e-6 relative with identical
   active sets, and `raven_wo_design` to 2.2e-15 absolute.

## Next owner

`ccf-paper-writer`, only on a separate request, and only for the bound write-up
(`results_evidence_axis/round_v1/WRITING_PROPOSAL.md`) **after** the four corrections listed
in that review: the MDE convention (audit `EV-2`), the evaluation-layer scope of the
fixed-checkpoint figures, the withdrawn "composition" relabel, and the per-dataset sourcing
of every table cell. No manuscript edit follows from this file.
