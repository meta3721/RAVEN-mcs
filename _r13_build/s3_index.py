"""S3: one submission evidence index + package the small certified summaries + short main.tex entry."""
from __future__ import annotations

import hashlib
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
BUNDLE = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1"
DEST = BUNDLE / "submission_evidence"
DEST.mkdir(parents=True, exist_ok=True)

# small, certified summaries the paper's numbers point at; (source, dest name, status)
CANDIDATES = [
    ("results_w1_ladder/round_v5_1/TRADEOFF_V51.csv", "W1_TRADEOFF_V51.csv"),
    ("results_w1_ladder/round_v5_1a/A1P_IMPL_RERUN.csv", "W1_A1P_IMPL_RERUN.csv"),
    ("results_w1_ladder/round_v2/PHASE3_REPORT.md", "W1_PHASE3_REPORT_round_v2.md"),
    ("results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json", "TE2_CONCENTRATION_STEP4.json"),
    ("results_traffic_e2/round_v1/TE2_VERDICT.json", "TE2_CONCENTRATION_STEP3.json"),
    ("results_traffic_e2/round_v1/TE2_FROZEN_PREREG.json", "TE2_FROZEN_PREREG.json"),
    ("results_traffic_e2/round_v1/tables/TE2_MAIN.csv", "TE2_MAIN.csv"),
    ("results_traffic_e1/round_v1/TE1_VERDICT.json", "TE1_ADAM_VERDICT.json"),
    ("results_traffic_e1/round_v1/te1/tables/TE1_CONFIRM.csv", "TE1_CONFIRM.csv"),
    ("results_traffic_struct/round_v1/TS1_SUMMARY.json", "TS1_STRUCT_SUMMARY.json"),
    ("results_traffic_struct/round_v1/tables/TS1_PAIRS.csv", "TS1_PAIRS.csv"),
    ("results_table2_audit/uair_table2_summary_with_current_fedavg.csv", "UAIR_TABLE2_AUDIT_SUMMARY.csv"),
    ("results_table2_audit/AUDIT_META.json", "UAIR_TABLE2_AUDIT_META.json"),
    ("results_seed_path_audit_r1/C7_E3_ARMS_THETA.csv", "UAIR_THETA_ARMS.csv"),
    ("results_seed_path_audit_r1/C3_CELL_DIFF.md", "SEED_PATH_AUDIT_CELL_DIFF.md"),
]
copied, missing = [], []
for rel, name in CANDIDATES:
    src = ROOT / rel
    if not src.is_file():
        missing.append(rel)
        continue
    if src.stat().st_size > 2_000_000:
        missing.append(rel + " (too large)")
        continue
    shutil.copy2(src, DEST / name)
    copied.append((name, src.stat().st_size,
                   hashlib.sha256((DEST / name).read_bytes()).hexdigest()[:16]))
print("packaged:", len(copied), " files;  skipped:", missing)
for n, sz, h in copied:
    print(f"  {n:<38} {sz:>7} B  {h}")

INDEX = """# Submission evidence index (single entry)

This is the one index for the numbers added after the frozen bundle was sealed. Every row names the
paper location, the quantity, the protocol or comparator it belongs to, the file that carries it, and
the scoring identity. Nothing here replaces the bundle's own `w1/PAPER_NUMBERS.csv`; that file remains the
index for the numbers it already covers.

Access status is stated per row and means exactly one of:

- `packaged` - the file is in `submission_evidence/` next to this index and ships with the submission;
- `local-only` - the file exists in the author's working tree and is not in the submitted material;
- `public` - an external public source.

Long paths are given relative to the working tree so the index is usable internally; none of them is a
C-drive path that a reviewer would be asked to open.

| paper location | quantity | unit | protocol / comparator | file | key or line | scoring identity | access |
|---|---|---|---|---|---|---|---|
| Table IV (matched support) | W1 trained-rule trade-off cells | `RMSE_mu`, `Delta` | matched active set, 20 seeds | `submission_evidence/W1_TRADEOFF_V51.csv` | per-contrast rows | theta-canonical (v5.1 errata) | packaged |
| Sec. VI, independent projection | `A1'` implementation values, incl. the `kappa=1000` variant | `eps_impl`, `Delta` | exact projection oracle | `submission_evidence/W1_A1P_IMPL_RERUN.csv` | per cell | `approximate`, `eps_impl <= 2.42e-05` | packaged |
| Table VI (concentration) | oracle-margin gap vs target concentration, 4 rungs | % of uncorrected member | frozen server step, 20 seeds, declared target | `submission_evidence/TE2_CONCENTRATION_STEP4.json` | `ceiling_ladder[*]` | theta-consistent; single-region rung `+0.097 %` | packaged |
| Table VI, primary cell | `kappa=5` primary contrast | `RMSE_mu` | frozen server step, 20 seeds | `submission_evidence/TE2_CONCENTRATION_STEP3.json` | `contrasts[*]` | frozen pre-registration | packaged |
| Table VI, pre-registration | target artifact, ladder, endpoint, decision rule | - | fixed before the runs | `submission_evidence/TE2_FROZEN_PREREG.json` | whole file | frozen before runs | packaged |
| Table VI, per-seed | 80 cells x metrics | `RMSE_mu`, `Delta` | as above | `submission_evidence/TE2_MAIN.csv` | per row | as above | packaged |
| Adam sensitivity (Sec. VII) | paired oracle-margin headroom after the Adam step | % (`H`) | 15 confirm seeds | `submission_evidence/TE1_ADAM_VERDICT.json` | `mean_H`, `MDE80` | `MDE80 = 5.80 %` | packaged |
| Adam sensitivity, per-seed | per-seed test `RMSE_mu` | `RMSE_mu` | 15 confirm seeds | `submission_evidence/TE1_CONFIRM.csv` | per seed | as above | packaged |
| Adam sensitivity, structural readout | `Delta_group`, `Delta_c-s` on the same runs | pp | scored after the prediction contrast | `submission_evidence/TS1_STRUCT_SUMMARY.json` | `mean`, `ci` | exploratory, post-hoc | packaged |
| Adam sensitivity, pairs | per-seed structural deltas | pp | as above | `submission_evidence/TS1_PAIRS.csv` | per seed | as above | packaged |
| Table XVIII (U-Air context) | active-set audit of the FedAvg row | `RMSE_mu`, `WorstGroupRMSE` | current runner, keeps every delivered client | `submission_evidence/UAIR_TABLE2_AUDIT_SUMMARY.csv` | per method | current-runner re-run | packaged |
| Table XVIII, audit metadata | recomputation check and seed count | - | - | `submission_evidence/UAIR_TABLE2_AUDIT_META.json` | whole file | as above | packaged |
| Figs. 5-6 (U-Air rows) | theta re-score of the four affected arms at seeds 30007/30016/30018 | `RMSE_mu`, `Tail_RMSE` | saved-checkpoint re-forward | `submission_evidence/UAIR_THETA_ARMS.csv` | per arm, per seed | theta-canonical | packaged |
| Figs. 5-6 provenance | mirror/theta cell diff and the applied corrections | - | - | `submission_evidence/SEED_PATH_AUDIT_CELL_DIFF.md` | whole file | applied 2026-09-29 | packaged |
| Sec. V, Table VII, appendix Tables XXIX-XXX, Fig. 8 | learning and development geometry | various | `results_main_rebuild_r1/` | `results_main_rebuild_r1/` | summaries only | development-only, not RAVEN gain | local-only |
| Sec. V (p. 8) | closable-gap `3.44` pp (SensorScope) and `1.32` pp (U-Air) | pp | protocol R always-on, 20 seeds | `submission_evidence/W1_PHASE3_REPORT_round_v2.md` | line 77 | **report-level source only**: not recomputed from raw values in this round | packaged |
| bundle-wide | frozen targets, EventTraces, paired results, figure/table sources | - | - | `README.md`, `w1/PAPER_NUMBERS.csv` | as indexed there | frozen bundle | packaged |

## Open items this index does not close

1. `3.44` and `1.32` pp have a **report-level** source (the Phase 3 report, line 77) and remain
   `UNLOCATED` in `w1/PAPER_NUMBERS.csv`. This index records the report path and the limitation; it does
   **not** upgrade them to "recomputed from raw values".
2. The learning and development geometry material (`results_main_rebuild_r1/`) is **local-only** in this
   delivery. It is not claimed to be public or bundled.
3. Publishing or uploading the local-only material is left to the author; this round did not upload
   anything.
"""
(DEST / "SUBMISSION_EVIDENCE_INDEX.md").write_text(INDEX, encoding="utf-8")
for name, sz, h in copied:
    pass
print("\nwrote", (DEST / "SUBMISSION_EVIDENCE_INDEX.md").relative_to(ROOT).as_posix(),
      (DEST / "SUBMISSION_EVIDENCE_INDEX.md").stat().st_size, "B")

# README pointer: one line, so there is exactly one list
R = BUNDLE / "README.md"
rt = R.read_bytes()
marker = b"## What is in the bundle"
assert rt.count(marker) == 1
eol = b"\r\n" if rt.count(bytes([13, 10])) == rt.count(bytes([10])) else b"\n"
add = (eol + b"The index for the numbers added after the bundle was sealed, with per-row scoring identity"
       b" and" + eol + b"access status, is `submission_evidence/SUBMISSION_EVIDENCE_INDEX.md`." + eol)
if b"SUBMISSION_EVIDENCE_INDEX.md" not in rt:
    R.write_bytes(rt.replace(marker, marker + add, 1))
    print("README: pointer added")
else:
    print("README: pointer already present")

# main.tex availability sentence -> name the entry (length-neutral)
M = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
mt = M.read_bytes()
OLD = (b"Later corrected W1 scores, concentration, Adam, learning, and\n"
       b"geometry diagnostics remain in their separate result directories.  Their\n"
       b"locations and scoring identities are indexed in the revision evidence record.\n")
NEW = (b"Later corrected W1 scores, concentration, Adam, learning, and\n"
       b"geometry diagnostics are indexed, with file paths and scoring identities, in\n"
       b"\\texttt{submission\\_evidence/SUBMISSION\\_EVIDENCE\\_INDEX.md} beside the bundle.\n")
print("main.tex anchor count:", mt.count(OLD))
assert mt.count(OLD) == 1
M.write_bytes(mt.replace(OLD, NEW, 1))
print("main.tex availability entry updated;", len(NEW) - len(OLD), "B delta")
