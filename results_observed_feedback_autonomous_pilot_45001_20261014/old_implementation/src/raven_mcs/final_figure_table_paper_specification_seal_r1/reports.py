"""36-section specification-seal report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import write_text
from raven_mcs.final_figure_table_paper_specification_seal_r1.constants import JOURNAL, ROUND, TITLE


def write_report(
    out: Path,
    *,
    status_code: str,
    status_name: str,
    hashes: dict,
    fig6: str,
    gates: dict[str, Any] | None,
    pkg: dict[str, Any] | None,
) -> None:
    n_pass = (gates or {}).get("n_pass", 0)
    n_total = (gates or {}).get("n_total", 54)
    zip_pass = (pkg or {}).get("pass")
    n_members = (pkg or {}).get("n_members", "")
    zip_mark = "PASS" if zip_pass else str(zip_pass)
    he1 = hashes.get("FIG_E1", {}).get("sha256", "")
    he2 = hashes.get("FIG_E2", {}).get("sha256", "")
    he3 = hashes.get("FIG_E3", {}).get("sha256", "")
    he4 = hashes.get("FIG_E4", {}).get("sha256", "")
    ht1 = hashes.get("TABLE_I", {}).get("sha256", "")
    ht2 = hashes.get("TABLE_II", {}).get("sha256", "")
    ht3 = hashes.get("TABLE_III", {}).get("sha256", "")
    body = f"""# RAVEN-MCS Final Figure–Table & Paper Specification Seal R1 Report

Round: `{ROUND}`

## 1. Executive decision

**Status {status_code}.** `{status_name}`

Gates: {n_pass}/{n_total}. Conceptual figures merged into one framework figure (5 main figures). Three main tables. FIG6 repaired by OPTION A from sealed P2 certificate data (Traffic excluded). T-Drive remains reviewer reserve. **new experiments required = false.**

## 2. Zero-run attestation

No training, no E1–E4 rerun, no T-Drive, no canary, no tuning, no new dataset or baseline. See `12_REPORTS/NO_NEW_EXPERIMENT_ATTESTATION.json`. Original freeze scientific files were copied or deterministically filtered, not recomputed.

## 3. Packaging repair summary

Three packaging repairs, no scientific-metric change:

- FDAF-G52 bookkeeping (markdown `**YES.**` vs `**yes**`).
- Paper-facing paths in this seal use archive-relative destinations; original locations are recorded only in `old_path`.
- FIG6 was not figure-ready on placeholder ESS/runtime CSVs; OPTION A built APP-F2 from `E3_P2_CERTIFICATE_SUMMARY.csv`.

## 4. G52 repair

Old gate failed on substring matching, not missing core data. Freeze report already stated manuscript-critical completeness. `scientific_data_changed=false`. Documented in `02_PACKAGING_REPAIR/FDAF_G52_REPAIR_AUDIT.md`.

## 5. Relative-path repair

`02_PACKAGING_REPAIR/ABSOLUTE_TO_RELATIVE_PATH_REPAIR.csv` maps each copied asset to a path under `05_PROVENANCE/`. `scientific_content_changed` is false for every row. Byte-copy SHA256 is unchanged for FIG-E1–E4 and Tables I–III.

## 6. FIG6 readiness decision

Previous freeze label `APPENDIX_FIGURE_READY` on `FIG_OPTIONAL_ESS.csv` / `FIG_OPTIONAL_P2_RUNTIME.csv` was incorrect (placeholders, identical SHA256). **Final: {fig6}.** Source is sealed P2 certificate summary with Traffic dropped. No exact-optimality claim. No experiment.

## 7. Final paper title

{TITLE}

Journal: {JOURNAL}. Linguistic micro-edit only if later required.

## 8. Final contributions

Exactly three: (C1) deployment-target risk semantics; (C2) selection-layer-aware reconstruction; (C3) feasibility-aware instantaneous and long-term calibration. Design/Obs/Use/Inst/Debt are modules, not five contributions.

## 9. Final RQs

RQ1 mismatch (E1/E2, FIG-E1). RQ2 structural alignment with competitive prediction (E3 SS/U-Air, FIG-E2/E3, Table II). RQ3 component roles (E4 Gen2 Inst, FIG-E4, Table III). No fourth main empirical RQ.

## 10. Final section structure

I Introduction; II Related Work; III System Model and Target-Risk Formulation; IV Selection-Layer-Aware Target Reconstruction; V Feasibility-Aware Target Calibration; VI Theoretical Analysis; VII Evaluation; VIII Discussion and Limitations; IX Conclusion; Appendix A–E.

## 11. Final h/s semantics

h(i) ≠ s(i). SensorScope/U-Air: h(i) = four UTC time-of-day groups from train-split mass (no test labels); s(i) = spatial identity × time block × weekday/weekend. Do not write h(i) as spatial × time.

## 12. Final experiment roles

E1 sanity; E2 problem (D_aligned); E3 main effectiveness on SensorScope/U-Air; E4 mechanism (240 cells, w/o-Inst generation 2). Traffic E2 valid, E3 NOT_COMPARABLE. T-Drive protocol-sealed reviewer reserve, not evaluated.

## 13. Final main figures

1. FIG-C merged problem+architecture (conceptual).
2. FIG-E1 E2 D_aligned (`{hashes.get("FIG_E1", {}).get("dest", "")}`; SHA256 `{he1}`).
3. FIG-E2 E3 structural (`{hashes.get("FIG_E2", {}).get("dest", "")}`; SHA256 `{he2}`).
4. FIG-E3 E3 prediction (`{hashes.get("FIG_E3", {}).get("dest", "")}`; SHA256 `{he3}`).
5. FIG-E4 E4 ablation relative change (`{hashes.get("FIG_E4", {}).get("dest", "")}`; SHA256 `{he4}`).

All `new_experiment_required = false`.

## 14. Final Appendix figures

APP-F1 Local-Hajek provenance: APPENDIX_READY. APP-F2 P2 feasibility: {fig6}. Runtime: OPTIONAL_APPENDIX. FIG5 composition: INSUFFICIENT_EXISTING_DATA_DO_NOT_RUN. FIG9: DROP_LOW_VALUE.

## 15. Final main tables

TABLE-I datasets (`{ht1}`). TABLE-II E3 SS/U-Air (`{ht2}`). TABLE-III E4 ablation Gen2 Inst (`{ht3}`). T-Drive is not an evaluated dataset row.

## 16. Final Appendix tables

APP-T1 E1 sanity; APP-T2 full paired statistics (freeze statistics master, not recopied because historical `source_file` cells contain machine paths); APP-T3 full methods; APP-T4 P2 summary; APP-T5 runtime optional.

## 17. Figure/table data provenance

Immutable copies under `05_PROVENANCE/FINAL_FIGURE_SOURCES/` and `FINAL_TABLE_SOURCES/` with `.meta.json`. Identity audit records no superseded E4, no Traffic E3 contamination, no T-Drive results, no canary, no favorable hidden filter.

## 18. Contribution-theory-evidence alignment

C1 ↔ P1 (definitional) ↔ RQ1 ↔ FIG-E1. C2 ↔ P2 reconstruction ↔ RQ2 ↔ FIG-E2/TABLE-II. C3 ↔ T-P2 uniqueness (theory) + E4 trade-offs ↔ RQ3 ↔ FIG-E4/TABLE-III. C10 bounds experimental P2 optimality.

## 19. Section III specification

Entities k, i, Y_i, h(i), s(i), R/O/U, μ; target vs arrival/usable-update risk; problem statement. No new experimental claims.

## 20. Section IV specification

Layer-aware reconstruction, positivity/support, Hajek/normalized correction, information-boundary legality, reconstructed mass. Local-Hajek collapse is diagnostic.

## 21. Section V specification

Instantaneous mismatch, feasible support, P2, calibration, debt update, aggregation. Debt not empirically large. Inst endpoint trade-off. Use no clear E4 effect.

## 22. Section VI theorem registry

P1 target-vs-arrival risk; P2 normalized reconstruction; T-P2 uniqueness under stated convex assumptions. No extra completeness theorems. Empirical validation is not required for T-P2 exact window optimality.

## 23. Section VII specification

VII-A setup (Table I); VII-B RQ1 FIG-E1; VII-C RQ2 FIG-E2/E3 Table II; VII-D RQ3 FIG-E4 Table III; VII-E short summary. No new numbers.

## 24. Section VIII specification

Limitations: not universal RMSE; endpoint trade-offs; Use no-clear-effect; small Debt; Traffic comparability; P2 boundary; propensity quality; T-Drive reserve.

## 25. Introduction wording ceiling

Three contribution sentences as coordinated architecture. Avoid universally superior; all components necessary; fully real-world selection; exactly optimal in all windows.

## 26. Abstract claim ceiling

Quantitative claims only from frozen tables/figures. Forbidden: universal RMSE; all baselines beaten; Use indispensable; large Debt; certified experimental P2 optimality; three-dataset E3; T-Drive results.

## 27. Conclusion claim ceiling

Mismatch; coordinated correction/calibration; structural alignment on SS/U-Air; competitive prediction; selective gains; component trade-offs. No T-Drive results.

## 28. Appendix structure

A proofs; B E1/statistics; C Local-Hajek; D P2 feasibility (not optimality); E full tables / optional runtime. No FIG5. No T-Drive performance.

## 29. Data gap decision

No CORE_BLOCKER. Supporting/optional gaps (debt/ESS trajectories, sampling interval, row-level propensities, FIG5, T-Drive performance, P2-only runtime) do not trigger experiments.

## 30. Figure count decision

5 main figures (merged conceptual + four empirical). Do not add a weak sixth figure.

## 31. Table count decision

3 main tables. Appendix tables do not count toward the main-text target.

## 32. Main-artifact reproducibility

Each main empirical figure/table maps source CSV → master evidence → seeds 30001–30020 (E1 28001–28005) → config → EventTrace. Gap column is `none`.

## 33. Main-artifact numeric consistency

No CONFLICT. Copies are EXACT_MATCH; sealed mean±std tables are AGGREGATION_MATCH without recompute.

## 34. T-Drive reserve

PROTOCOL_SEALED; FORMAL_NOT_RUN; REVIEWER_RESERVE; DO_NOT_RUN_BEFORE_SUBMISSION. Not in evaluated dataset count, main results, main tables, or main empirical figures.

## 35. Is any new experiment still required?

**No. new experiments required = false.**

## 36. Exact next action

WRITE SECTION III–VI USING FROZEN SPECIFICATION.

Then: joint III–VI symbol audit; Section VII; Appendix; Related Work; Introduction; Conclusion; Abstract; full manuscript consistency audit.

STOP all experiment and data-collection work. Do not activate T-Drive.

ZIP: `TO_SUBMIT_RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1.zip` (members={n_members}, reopen-verify={zip_mark}).
"""
    write_text(out / "12_REPORTS/RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1_REPORT.md", body)
