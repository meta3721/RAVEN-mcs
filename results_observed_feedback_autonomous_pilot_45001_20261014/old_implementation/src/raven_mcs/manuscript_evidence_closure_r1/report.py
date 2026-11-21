"""Final manuscript evidence closure report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import write_text
from raven_mcs.manuscript_evidence_closure_r1.constants import ROUND


def write_report(out: Path, status_code: str, status_name: str, tdrive: dict[str, Any]) -> Path:
    md = f"""# RAVEN-MCS manuscript evidence closure R1

Round: `{ROUND}`

## 1. Executive decision

**{status_code}. {status_name}**

T-Drive: `{tdrive.get("decision")}`. Experiment stop: `STOP_ALL_NEW_EXPERIMENTS_WRITE_MANUSCRIPT`.

## 2. Zero-run attestation

No training, no E1–E4 reruns, no Canary, no T-Drive formal runs. Writes only under `manuscript_evidence_closure_r1/`. R2 was not modified.

## 3. Frozen paper positioning

TMC target. Core topic: two-stage/multi-layer non-random selection induces usable-update vs deployment-target mismatch; RAVEN coordinates correction and calibration. Not a universal predictor, generic FL optimizer, imputation, routing, mobility-prediction, or fairness paper.

## 4. Final RQs

Exactly three main empirical RQs (RQ1 mismatch, RQ2 effectiveness, RQ3 components). Old RQ4–RQ6 are not main empirical RQs.

## 5. h(i)/s(i) manuscript semantics

SensorScope/U-Air: h(i) = four UTC TOD groups; s(i) = spatial × 4 blocks × weekday/weekend; h ≠ s. Traffic uses sealed E2 region-stratum semantics.

## 6. E1 evidence role

Balanced no-harm sanity. Statistical superiority not established. Appendix/compact paragraph.

## 7. E2 evidence role

Risk non-interchangeability (Fig. 1). Not a RAVEN ranking figure.

## 8. E3 evidence role

Main effectiveness on SensorScope and U-Air only (Table II, Fig. 2). Traffic E3 excluded.

## 9. E4 evidence role

Mechanism/ablation, 240 cells, w/o-Inst Generation 2 (Table III, Fig. 3). Inst = ENDPOINT_TRADEOFF.

## 10. Main Table I

Evaluated datasets: SensorScope, U-Air, NSW Traffic. T-Drive is not in Table I.

## 11. Main Table II

E3 mean±std with Holm metadata. Numerical best ≠ significance.

## 12. Main Table III

E4 core ablation mean±std. Component labels from R2.

## 13. Main Fig. 1

E2 \(D_{{\\mathrm{{aligned}}}}\) seed-level boxplots with zero line.

## 14. Main Fig. 2

E3 \(\\Delta_{{\\mathrm{{group}}}}\) and \(\\Delta_{{c,s}}\) for two datasets × two metrics.

## 15. Main Fig. 3

E4 relative change when a component is removed (mixed signs allowed).

## 16. Results draft

`05_results/SECTION_RESULTS_R1.md` (.tex companion). Organized by RQ, not by experiment ID.

## 17. Discussion draft

`06_discussion/DISCUSSION_R1.md`.

## 18. Limitations draft

`06_discussion/LIMITATIONS_R1.md`.

## 19. Introduction contribution audit

Proposed three-contribution registry; no module-necessity claim.

## 20. Section III–VI theory/evidence audit

Theorems may be theory-only. No new experiment demanded for theory-only claims.

## 21. Conclusion claim audit

Claim-safe conclusion drafted. No universal dominance.

## 22. Manuscript evidence completeness

External mobility validity is the only row pointing to T-Drive reserve. Cost/robustness do not trigger experiments.

## 23. Paper quality assessment

Internal heuristic in `10_report/PAPER_QUALITY_AUDIT_R1.md`. No invented acceptance probability.

## 24. T-Drive manuscript-level Go/No-Go

**{tdrive.get("decision")}**. Protocol Seal readiness is not authorization. Do not run before submission.

## 25. Experiment stop decision

`STOP_ALL_NEW_EXPERIMENTS_WRITE_MANUSCRIPT`. No non-T-Drive new family.

## 26. Exact next action

Write the manuscript from these tables/figures/Results/Discussion drafts. Do not start T-Drive or any other experiment without a later explicit teacher instruction.
"""
    return write_text(out / "RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1_REPORT.md", md)
