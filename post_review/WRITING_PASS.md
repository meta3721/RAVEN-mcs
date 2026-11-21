# Writing pass (TO_OVERLEAF_paper_tmc_r1_clean)

Date: 2026-08-27
Target: `TO_OVERLEAF_paper_tmc_r1_clean/` only. Seals untouched. No git commit.

## Claim ceiling respected
- Exactly 3 contributions. Gating = practical realization of Contrib 2. G4 bound = Contrib 3 + Prop 2 scope. Debt internal.
- Path B default: SensorScope Design on; U-Air Design off. Full Design U-Air reversal kept.
- Reason: support-incompatible π^tar, not estimated propensity failure.
- Path A named as a failed repair, not a method.
- G2: 4-block WorstGroupRMSE; NI vs adapted FedAU/ObsUse; no “best worst-group”; FedCure not run.
- G3: T-Drive evidence A (real R; O/U controlled). No T-Drive ranking. T-Drive remains in the main evaluation; it was dropped only from the abstract for length.
- G4: stable perturbation under A5; not unbiased; bound does not explain U-Air Design.
- G5: feasibility certified; CLARABEL–SCS tail 0.0056; no formal rerun; 20 seeds = EventTrace randomness.
- G6: paper name is “pre-registered under-served-block check,” not G6. VAL-only recorded negative. TEST not opened. No unique-endpoint win. No “cannot copy.” Informed copies not trained. U-Air −0.44% vs FedAU is not a win. Path B unchanged.

## Compression (2026-08-27)
TMC regular papers: 12 published pages including refs/bios; submissions may be up to 18 pages (MOPC). Supplemental must be a separate PDF.

| PDF | Pages | Role |
|---|---|---|
| Before | 23 (appendix in main) | Over the 18-page submission cap if uploaded as one file |
| `main.pdf` | **16** (body I–IX through p.14; refs p.15–16) | Submission PDF |
| `supplemental.pdf` | **8** | Separate ScholarOne upload |

Result allocation:
- Core kept in main: Table II (gated E3), W1 Design gate, E2 D_aligned figure, T-Drive figure, E4 ablation, under-served-block VAL table (qualification / recorded negative).
- Relocated to supplemental: proofs A–E, E1/E2/E3 extra tables, P2 diagnostics, runtime, Design provenance, sealed same-backbone Fig. 3–4 (U-Air bars = full Design, not the default).

Prose: abstract shortened (T-Drive sentence removed from abstract only); intro no longer dumps E3/E4 numbers; underserved and discussion claim-ceiling repeats compressed.

## Not done
- Author-line fill; Algorithm 1; GitHub URL.
- `_paper_work/` not started.
- No commit.
- Publication-length 12 pages would still incur MOPC (~4 pages). Further cuts would have to gut theory or Related Work.
