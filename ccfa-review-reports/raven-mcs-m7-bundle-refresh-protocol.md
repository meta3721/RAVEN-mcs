# Executable instruction: M7 — public reproducibility bundle refresh (Option A: inventory + provenance)

```text
Mode: design + one execution prompt. This file starts no run.
Contract: CCFA-Skills/ccf-experiment-designer.
Inputs (read-only): RAVEN_MCS_PUBLIC_REPRO_R1/ (existing bundle), results_w1_ladder/round_v2 … round_v5_1a/,
                    results_gatekeeping/round_v1/, results_exogenous_target/round_v1/,
                    TO_OVERLEAF_paper_tmc_r1_clean/{main.tex,supplemental.tex}.
Output: additions INSIDE RAVEN_MCS_PUBLIC_REPRO_R1/ only (new subtrees + updates to its three index files).
No manuscript edits, no src/ edits, no build() run, no git, no upload.
Purpose: close review item M7 — the numbers the paper prints from the W1 rounds are not auditable from the released bundle.
```

## 0 Why this is the item

The bundle predates the W1 work. The paper now prints structural and mechanism numbers whose only产出物 live in `results_w1_ladder/*` and `results_gatekeeping/*`. A reader following the paper's availability pointer cannot locate them, so those numbers are "trust the paper" — that is exactly what the Reproducibility dimension penalises, and M7 is its only carrier.

**What "auditable" means here (and what it does not):** every number printed in `main.tex`/`supplemental.tex` that originates in these rounds resolves to *a named file inside the bundle, a named row/key inside that file, and a sha256 of that file*. It does **not** mean the bundle can recompute the numbers (that is Option B, explicitly out of scope), and it changes **no claim and no number**.

## 1 Facts already verified about the current bundle (2026-10-04)

- Top level: `certificate/ cityscanner/ cityscanner_p2/ configs/ eventtraces/ figures/ new_target/ processed/ scripts/ tables/ tdrive/` plus `BUNDLE_SUMMARY.json`, `LICENSE.txt`, `MANIFEST.csv` (261 KB), `PROTOCOL.json`, `README.md`, `verify.py`.
- `tables/` holds 21 files; `scripts/` 4; total bundle size **169.04 MB**, overwhelmingly `eventtraces/`.
- A builder exists (`scripts/build_public_repro_bundle.py`, 18.4 KB) and a verifier (`RAVEN_MCS_PUBLIC_REPRO_R1/verify.py`).
- **Do not assume** the column layout of `MANIFEST.csv`, the schema of `BUNDLE_SUMMARY.json`, or the README's section structure: read them first and follow their existing conventions exactly.

## 2 Artifact classes to add (copy byte-identical; do not reformat, re-delimit or rename columns)

Proposed destination subtrees — adjust names only if the bundle's existing convention requires it, and say so in the report.

| destination | source | files |
|---|---|---|
| `w1/frontier/` | `results_w1_ladder/round_v2/` | `FRONTIER.csv`, `FRONTIER_ARMS.csv`, `FRONTIER_CHECKS.csv`, `G_F_BOTH.csv`, `CERT.csv`, `COST.csv`, `COST_MACHINE.json`, `CROSS_RULER.csv`, `ENDPOINT_SEMANTICS.csv`, `LADDER.csv`, `LADDER_PAIRED.csv`, `LADDER_DECISIONS.csv`, `LADDER_REPORT_SEEDS.csv`, `G5_REPLAY_CHECK.csv`, `PHASE3_REPORT.md`, `PHASE4_REPORT.md`, `PHASE4_INPUT_GAPS.md`, `PHASE5_REPORT.md`, `EXECUTION_REPORT.md`, `PREREG.md`, `MANIFEST.sha256` |
| `w1/ladder_v3/` | `results_w1_ladder/round_v3/` | `SOURCE_LADDER.csv`, `SOURCE_LADDER_CHECKS.csv`, `SOURCE_LADDER_CONTRASTS.csv`, `SOURCE_LADDER_CONTINUITY.csv`, `GAP_DECOMPOSITION.csv`, `SAME_RULER_AUDIT.csv`, `DEBT_RECURSION.csv`, `MYOPIC_DIAG.json`, `MYOPIC_WINDOWS.csv`, `EXECUTION_REPORT.md`, `ERRATA_v2.md`, `PREREG.md`, `MANIFEST.sha256` |
| `w1/tradeoff_v4/` | `results_w1_ladder/round_v4/` | `TRADEOFF.csv`, `TRADEOFF_PAIRED.csv`, `TRAIN_GATES.csv`, `TRAIN_SUMMARY.json`, `A2A3_SUMMARY.json`, `GRID_EXTENSION.csv`, `DEBT_STRENGTH.csv`, `PART_A_REPORT.md`, `PART_B_REPORT.md`, `PREREG.md`, `ERRATA_v3.md`, `MANIFEST.sha256`, plus **per-run `final_metrics.json` only** under `runs/<ds>/<arm>/seed<seed>/` (small); **exclude `checkpoints/final.pt`, `window_metrics.json`, `pair_state.parquet`** from the copy and record them as hash-listed-but-not-redistributed (§5) |
| `w1/audit_v5/` | `results_w1_ladder/round_v5/` and `round_v5_1/` and `round_v5_1a/` | `GATES_V5.csv`, `A1_SENS_GRID.csv`, `A1_SENS_SUMMARY.json`, `A1P_IMPL_RERUN.csv`, `A1P_STRUCT_PAIRED_RERUN.csv`, `A1P_ORACLE_GATES.json`, `O_GATES_RERUN.json`, `ORACLE_EVIDENCE.json`, `WORSTGROUP_V51.csv`, `WORSTGROUP_PAIRED.csv`, `WORSTGROUP_NI.csv`, `TRADEOFF_V51.csv`, `A3P_TOST_V51.csv`, `A3P_TOST_WG.csv`, `A3P_DOSE.csv`, `A3P_SIDE_BY_SIDE.csv`, `A3P_RESOURCE_UPAIR.csv`, `R1A_TOST.csv`, `R1A_DOSE.csv`, `A1_DESCRIPTIVE.csv` (if present), each round's `EXECUTION_REPORT.md`, `PREREG.md`, `AMENDMENTS.md`, `ERRATA_FOR_PAPER.md`, `MANIFEST.sha256` |
| `w1/gatekeeping/` | `results_gatekeeping/round_v1/` | `A1_DESCRIPTIVE.csv`, `A1_DESCRIPTIVE_DETAIL.csv`, `A1_POWER.csv`, `A1_SENSITIVITY_NO32005.csv`, `C1_PRIMARY.json`, `C1_MAPS.json`, `C1_RUNS.csv`, `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv`, `C1_SENSITIVITY_NO32005.csv`, `B0_REPRO.json`, `B0_SEED32005_PROBE.csv`, `EXECUTION_REPORT.md`, `PREREG.md`, `ERRATA_FOR_PAPER.md`, `MANIFEST.sha256` |
| `w1/exogenous/` | `results_exogenous_target/round_v1/` | `MAPS_KEY_LEVEL.csv`, `MAP_SUMMARY.csv`, `MAP_MARGINALS.csv` (skip any file already present elsewhere in the bundle — detect duplicates by sha256 and keep one copy, noting the choice) |

Rules: byte-identical copies (`Copy-Item`); never "clean" whitespace, never re-encode (write nothing through a text round-trip); preserve each source file's own name; if a source file is missing, record `MISSING` and continue (do not substitute).

## 3 The core deliverable: `w1/PAPER_NUMBERS.csv`

One row per number printed in `main.tex`/`supplemental.tex` that originates in these rounds, with columns:

```
paper_file, paper_line, printed_value, quantity, unit, ruler_or_condition, source_file, source_row_or_key, source_sha256, status
```

Cover at least: closable gap 3.44 / 1.32 pp; `B1−B1(uniform)` +0.768 / +0.286 pp; `B1−B0` +1.188 / +1.399 pp; group-matching −0.135 pp (Δ_c-s) and +0.039 [+0.013,+0.063] (ΔG); variance/staleness ≤0.008 (ΔG); frozen-strength debt +0.0073 [0.0064,0.0083] and +0.0024 pp; ζ +0.922 [0.721,1.141] pp with ΔG −0.268 [−0.320,−0.214]; the 0/20 structural-verdict invariance; 3,279 windows and the 1e-13 flatness median; the tie-break 1.05140 / 1.06213 / 0.0107 pp / 0.0337; `ε_impl ≤ 2.42e-5` with its 17 % / 0.13 % / 0.16 % conversions and the Δ↔pp conversion factors; the κ=1000 deltas +1.347 / +0.580 pp with Holm ≈1e-5; WorstGroupRMSE means and the non-inferiority verdicts; the City Scanner A1 power range 0.120–0.153 and MDE80 range; the C1 primary (HL −0.000192, CI [−0.018930,+0.122754], p 0.9219, retained share 101.9 %); the trace-32005 probe range +24…+38 %; the FedAvg→RAVEN decomposition 68.96 % / 83.07 % and FedAU 77.58 % / ObsUse 74.58 %; the MDE/n table values and the dose-response slopes (+0.0325 [−0.0966,+0.1525]; −0.1224 [−0.2685,+0.0362]).

**Locate, do not guess.** Each row must be checkable by opening the named file at the named row/key. If a printed number cannot be located, set `status=UNLOCATED` with the search you performed — never fill in a plausible source.

## 4 Gates

| id | condition | on failure |
|---|---|---|
| **G-M7-1 coverage** | every row of `PAPER_NUMBERS.csv` has `status=located` **or** an explicit `UNLOCATED` with the search record; the scan of `main.tex`/`supplemental.tex` for numeric claims from these rounds is reported (how many found, how many mapped) | report the unlocated set; do not pad it |
| **G-M7-2 integrity** | `MANIFEST.csv` gains one row per added file (matching its existing columns), `BUNDLE_SUMMARY.json` counts/sizes updated, `README.md` gains a short "W1 evidence" section mapping the paper's new claims to bundle paths, and the bundle's own `verify.py` still passes | stop and report which index file refused |
| **G-M7-3 no drift** | every added file's sha256 equals the sha256 of the working-tree source it was copied from; no source file modified; existing bundle files unchanged except the three index files | stop; restore from the copy if a source was touched |
| **G-M7-4 size** | added payload (excluding the excluded weights) **≤ 20 MB**; report exact added size | for any class over budget, switch that class to hash-only listing and say so |

## 5 Hash-listed but not redistributed (record explicitly in `README.md` and `w1/EXCLUDED_HASHES.csv`)

For each excluded file: path, size, sha256. Cover the 120+120 Part B run trees' `checkpoints/final.pt`, `window_metrics.json`, `pair_state.parquet`, and any single file > 2 MB that is not already in the bundle. State the reason ("size; available on request") — do not silently omit.

## 6 Forbidden

- Editing `src/`, `main.tex`, `appendix.tex`, `supplemental.tex`, any `results_*` directory, `tdrive_protocol_seal_r1/`, or any report outside the bundle.
- Running `build_public_repro_bundle.py`'s full `build()`; any training; any git or upload/publish action.
- Changing any number, claim, caption or qualifier; renaming/relabelling columns; reformatting copied CSVs; deleting or overwriting existing bundle content.
- Substituting a different file when a source is missing.

## 7 Deliverables and report

Deliverables: the new `w1/…` subtrees, `w1/PAPER_NUMBERS.csv`, `w1/EXCLUDED_HASHES.csv`, `w1/MANIFEST_ADDITIONS.csv` (the exact rows added to `MANIFEST.csv`, for reviewability), and updated `MANIFEST.csv` / `BUNDLE_SUMMARY.json` / `README.md`.

Report: files added with count and total size; the three index-file diffs summarised; G-M7-1…4 results with the number of located vs UNLOCATED rows and the unlocated list verbatim; the excluded-hash list summary; the bundle's own verifier output; and anything that deviated.

## 8 Open decisions to settle before execution (none block drafting)

1. **Per-run detail level**: copy per-run `final_metrics.json` only (proposed), or additionally hash-list `window_metrics.json` + `pair_state.parquet` (§5 covers the latter), or copy those too (adds ~10–15 MB).
2. **Exogenous maps**: include `results_exogenous_target/round_v1/` (proposed) even though `new_target/` and `cityscanner/` already exist — decide whether they belong there instead.
3. **Version label**: keep the directory name `RAVEN_MCS_PUBLIC_REPRO_R1` and record a `bundle_revision` string (proposed `R1.1`) inside `BUNDLE_SUMMARY.json`, or add a versioned subdirectory.
4. **Paper-side pointer (separate authorization, not part of this instruction)**: `main.tex` L2211-2221's availability sentence currently points at the bundle generally; if the new subtree is to be citable, that sentence needs a one-clause change naming `w1/`. This is a manuscript edit and must be authorised on its own.

## 9 Cost

≈45–75 min, all local file work plus the bundle's own verifier; no compute, no training.
