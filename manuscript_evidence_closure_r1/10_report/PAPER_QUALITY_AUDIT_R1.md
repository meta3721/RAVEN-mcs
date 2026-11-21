# Paper quality audit (internal heuristic, not an acceptance probability)

| Dimension | Score (1–10) | Note |
|---|---:|---|
| Problem novelty | 8 | Target-risk vs arrival-risk under two-stage MCS selection is a sharp TMC-relevant problem. |
| Methodological novelty | 8 | Coordinated correction + instantaneous/debt calibration is distinct from generic FL/imputation. |
| Theoretical strength | 7 | Architecture is specified; exact experimental P2 optimality is bounded (C10). |
| Evidence quality | 8 | Sealed E2–E4 with paired seeds, Holm families, and honest labels. |
| Experimental completeness | 7 | Core claims closed; mobility external validity reserved. |
| TMC fit | 8 | MCS selection/deployment mismatch is in-scope; do not oversell mobility traces. |
| Overclaim risk | 6 | Residual risk if Abstract/Intro drift toward universal RMSE or component necessity. Ceiling files exist. |
| Reproducibility | 8 | R2 hashes, configs, and EventTrace identity are sealed. |
| Limitations | 8 | Explicit: Traffic vintage, P2, Use, small Debt, no T-Drive performance. |
| Remaining acceptance risks | — | Reviewer may ask for real mobility, runtime, or broader robustness; answer with reserve/limitations rather than new families. |

T-Drive decision: `TDRIVE_RESERVE_FOR_REVIEWER_ONLY`.
