import pathlib

AUD = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\raven-mcs-integrity-audit.md")
REV = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\raven-mcs-tmc-review.md")


def patch(path, pairs):
    txt = path.read_text(encoding="utf-8")
    for old, new in pairs:
        n = txt.count(old)
        assert n == 1, f"{path.name}: anchor count {n} for {old[:70]!r}"
        txt = txt.replace(old, new)
    path.write_text(txt, encoding="utf-8")
    print(f"{path.name}: patched, {len(txt.splitlines())} lines, {len(txt.encode('utf-8'))} bytes")


# ---------------------------------------------------------------- integrity audit
A1_OLD = """Also confirmed: `BUNDLE_SUMMARY.json` `file_count: 2117` against **2 118** files actually present."""

A1_NEW = """A systematic sweep of the whole bundle (2 118 files) shows the lag is **not confined to the
figures**, and that it reaches numbers the paper prints.

* **`figures/FIG_E3_E3_PREDICTION_RISK.csv`**: 27 of 440 rows differ (the nine U-Air arms at seeds
  `30007`, `30016`, `30018`), columns `RMSE_mu` (max `|Δ| = 0.117272`) and `Tail_RMSE` (max
  `0.060681`); `MAE_mu`, `RMSE_rho` and `comparison_class` are identical. The bundle's U-Air 20-seed
  arm means round to `1.1911 / 1.1911 / 1.1882 / 1.2160 / 1.1914`; **none of those digits occurs in
  `main.tex`, `supplemental.tex` or `appendix.tex`**, whereas the worktree version gives exactly the
  printed `1.1954` (L1897, appendix L1927), `1.1954` (appendix L1925), `1.1923` (appendix L1923),
  `1.2202` (L1894, appendix L1924) and `1.1958` (appendix L1928). `results_seed_path_audit_r1/C3_CELL_DIFF.csv`
  independently records these as "MIRROR (replace)".
* **`tables/TABLE_II_MAIN_EFFECTIVENESS.csv`, `TABLE_E3_MAIN_EFFECTIVENESS.csv`,
  `TABLE_E4_COMPONENT_EFFECTS.csv`, `TABLE_E4_CORE_ABLATION.csv` and `TABLE_II_FREEZE.json`** all
  still carry the superseded pre-repair values (`1.18824`, `1.19111`, `1.19112`, parent
  `1.191113924600986`). For these the bundle *agrees with its worktree source* — the sources are
  stale too — so this is a bundle↔manuscript defect rather than a copy error, and `verify.py` is
  blind to it either way.
* The bundle **documents the correction it fails to ship**: `w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md`
  gives the mapping `fedavg_window 1.18824 → 1.19225`, `raven 1.19111 → 1.19537`,
  `inst_cal 1.19112 → 1.19537`, and `A3P_RESOURCE_UPAIR.csv` is the **only** file in the bundle that
  holds the corrected `1.195365574077496`.
* **The released bundle contains its own truncated files.** `scripts/rebuild_table_ii.py` is a **2-byte**
  file (`sha256 7eb70257593d…`), manifest-registered at 2 bytes, while `README.md` L14 and L96 instruct
  the reader to run it to check Table II's 4-decimal cells. `tdrive/TD_R_FREEZE.json` is also 2 bytes
  with the same hash and no worktree counterpart, yet `README.md` L18 lists it as a deliverable. This is
  the §4.2 truncation class *inside the artifact a reader is told to verify with*.
* `README.md` L42 is **false**: it states that round v2's `PHASE3_REPORT.md` "is not redistributed",
  but `w1/frontier/PHASE3_REPORT.md` is in the bundle and its line 77 states the `3.44` pp and `1.32` pp
  figures. Consequently the first two rows of `w1/PAPER_NUMBERS.csv` print `UNLOCATED` with the reason
  "that file … was not copied" — a false reason.
* The shipped `scripts/build_public_repro_bundle.py` (`c8d9f0ac…`, 14 814 B) is an older revision than
  the worktree copy (`d400bdf4…`, 18 354 B) and contains no reference to `cityscanner/`, `overlay/` or
  `w1/EXCLUDED`, so **the shipped builder cannot reproduce the bundle it ships**. No R1.1 (w1) build
  script exists anywhere in the worktree.
* Manifest coverage: 2 116 data rows, 0 duplicates, 0 hash or byte mismatches, and only two files
  present on disk but unlisted — `MANIFEST.csv` itself (conventional) and
  `w1/MANIFEST_ADDITIONS.csv`, which `README.md` L38 describes as the rows this revision added to the
  manifest and which is therefore the one addition neither manifested nor hashed.
* `BUNDLE_SUMMARY.json` `file_count: 2117` against **2 118** files actually present, and
  `total_bytes: 179 916 789` against **180 207 845** actual — short by exactly the 291 056 bytes of
  `MANIFEST.csv`. Both fields exclude that one file. `created_utc` still reads 2026-09-05 while
  `bundle_revision` is `R1.1` (mtime 2026-10-04).
* A record correction: `ccfa-review-reports/raven-mcs-tmc-review-round10.md` §V.3 states that
  `PROTOCOL.json` and `verify.py` are "likewise not manifest-registered". Both **are**
  manifest-registered. That claim is refuted.

Reader-visible net effect, in the bundle's own numbers: someone rebuilding the paper's tables from
`RAVEN_MCS_PUBLIC_REPRO_R1` recovers `-6.553 / -6.875 / 0.131 / 0.136 / 1.1911 / 1.1882 / 1.2160`
where the paper prints `-6.885 / -7.221 / 0.143 / 0.149 / 1.1954 / 1.1923 / 1.2202`."""

A2_OLD = """Scope note: none of the three drivers produces a number in either new block, so the direct impact on
this revision is nil. The impact is on the bundle's reproducibility claim, and it is a
release-integrity defect regardless of this revision. Two earlier records
(`ccfa-review-reports/raven-mcs-experiment-report-20260924.md` L27,
`results_endpoint_screen/round_v1/EXECUTION_REPORT.md` L99/L113) already recorded this loss and a
partial rebuild (`scripts/run_nodesign_supplement.py`), so the truncation is recurrent, not new."""

A2_NEW = """Scope note: none of the three drivers produces a number in either new block, so the direct impact on
this revision is nil. The impact is on the bundle's reproducibility claim, and it is a
release-integrity defect regardless of this revision. Two earlier records
(`ccfa-review-reports/raven-mcs-experiment-report-20260924.md` L27,
`results_endpoint_screen/round_v1/EXECUTION_REPORT.md` L99/L113) already recorded this loss and a
partial rebuild (`scripts/run_nodesign_supplement.py`), so the truncation is recurrent, not new.

The class is wider than the three worktree scripts. §4.1 records that `scripts/rebuild_table_ii.py`
**inside the released bundle** is also a 2-byte stub while `README.md` tells the reader to run it;
`tdrive/TD_R_FREEZE.json` is a 2-byte stub listed as a deliverable; and three further shipped files
(`scripts/rebuild_e3_scd_holm_fedau_obsuse.py`, `tables/E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv`,
`tables/E3_SCD_WORSTGROUP_SLICE_REL.csv`) have no counterpart anywhere in the worktree. So the
truncation is not only a worktree loss: it reaches files the release presents as runnable checks."""

A3_OLD = """| §4.2 lost drivers, City Scanner tables | **high (Reproducibility)** | three delivered tables have no surviving generator and no copy exists |"""

A3_NEW = """| §4.1b bundle ships superseded printed values | **high (Reproducibility)** | readers rebuilding Table II/III and Table IV recover different digits than the paper prints |
| §4.2 lost drivers, City Scanner tables | **high (Reproducibility)** | three delivered tables have no surviving generator and no copy exists; two stubs sit inside the bundle itself |"""

patch(AUD, [(A1_OLD, A1_NEW), (A2_OLD, A2_NEW), (A3_OLD, A3_NEW)])

# ---------------------------------------------------------------- review
R1_OLD = """| NEW-r13-3 | round 13 | unresolved | previously_undetected | both | Reproducibility | 3 of 9 `figure_data` files differ from their bundle counterparts (`FIG_E3_E3_PREDICTION_RISK.csv`, `FIG_E4_E4_COMPONENT_ABLATION.csv`, `FIG_W1_DESIGN_GATE.csv`); `BUNDLE_SUMMARY.json` `file_count 2117` vs 2 118 present; `verify.py` cannot detect any of it | none |"""

R1_NEW = """| NEW-r13-3 | round 13 | unresolved | previously_undetected | both | Reproducibility | 3 of 9 `figure_data` files differ from their bundle counterparts (`FIG_E3_E3_PREDICTION_RISK.csv`, `FIG_E4_E4_COMPONENT_ABLATION.csv`, `FIG_W1_DESIGN_GATE.csv`), and the divergence reaches **printed cells**: the bundle's U-Air arm means round to `1.1911/1.1911/1.1882/1.2160/1.1914`, none of which occurs in any `.tex`, against the printed `1.1954/1.1923/1.2202/1.1958`; `tables/TABLE_II_MAIN_EFFECTIVENESS.csv`, `TABLE_E3_MAIN_EFFECTIVENESS.csv`, `TABLE_E4_COMPONENT_EFFECTS.csv`, `TABLE_E4_CORE_ABLATION.csv` and `TABLE_II_FREEZE.json` all still carry the superseded `1.18824 / 1.19111 / 1.19112`, while the bundle's own `w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md` documents the correction it fails to ship; `BUNDLE_SUMMARY.json` `file_count 2117` vs 2 118 present and `total_bytes` short by exactly `MANIFEST.csv`; `README.md` L42 falsely says `w1/frontier/PHASE3_REPORT.md` is not redistributed; the shipped `scripts/build_public_repro_bundle.py` cannot rebuild the bundle; `verify.py` detects none of it by construction | none |"""

R2_OLD = """**NEW-r13-3/-4. Independent of this revision, the release bundle does not currently reproduce the paper.** Three of nine `figure_data` files differ from their bundle counterparts, `BUNDLE_SUMMARY.json` reports 2 117 files against 2 118 present, and `verify.py` is a hash-only self-check whose `MANIFEST.csv` carries no provenance column, so it cannot detect inconsistency with the manuscript by construction. Three drivers underlying the City Scanner and Pilot-2 tables are truncated to 2 bytes with no surviving copy, so those tables ship as data with no generator. Neither is caused by this revision; both bear on the Reproducibility axis and neither is charged against the current version alone. Owner: user; `ccf-integrity-auditor` for the record."""

R2_NEW = """**NEW-r13-3/-4. Independent of this revision, the release bundle does not reproduce the paper, and it ships stubs it tells the reader to run.** The divergence is not confined to figures. Three of nine `figure_data` files differ from their bundle counterparts, and for `FIG_E3_E3_PREDICTION_RISK.csv` (27 of 440 rows) the bundle's U-Air arm means round to `1.1911 / 1.1911 / 1.1882 / 1.2160 / 1.1914` — **no such digits occur anywhere in the manuscript**, which prints the worktree values `1.1954 / 1.1923 / 1.2202 / 1.1958`; the E4 ablation figure reaches the abstract's own `-6.885 / -7.221`, which the bundle stores as `-6.553 / -6.875`. Five bundle tables still carry the superseded `1.18824 / 1.19111 / 1.19112`, and the bundle's **own** `w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md` documents the correction the bundle does not carry. Separately, `scripts/rebuild_table_ii.py` — which `README.md` L14/L96 instructs the reader to run — is a **2-byte** file inside the released bundle, as is `tdrive/TD_R_FREEZE.json`; three further shipped files have no worktree original. `verify.py` is a hash-only self-check against a manifest generated *after* copying, so stale content is hashed stale and passes: it prints `checked=2116 mismatches=0` and cannot detect any of this by construction. None of it is caused by this revision, so none of it is charged against the current version alone; all of it bears on the Reproducibility axis and on whether the artifact can support the paper's claims at all. Owner: user; `ccf-integrity-auditor` for the record."""

R3_OLD = """- The bundle sweep for files outside `figure_data` / `figures` was in progress at the time of writing; the `figure_data` comparison (3 of 9 differing) is complete and the in-progress sweep can only widen, not narrow, NEW-r13-3."""

R3_NEW = """- The full bundle sweep is complete: 2 118 files, 2 099 byte-identical to a worktree twin, 19 with none, and the three figure files plus five tables differing from what the manuscript prints. The sweep also found that `MANIFEST.csv` carries no source or provenance column, so bundle↔worktree provenance rests on basename/size/hash matching and on reading the (itself non-shipped) build script; that is closed for `w1/` (unique twins) but structurally open elsewhere. A table-numbering conflict is likewise unresolved: L2252–L2253 and the bundle README call `TABLE_II_MAIN_EFFECTIVENESS.csv` "canonical Table II" while `C3_CELL_DIFF.csv` labels the same manuscript table "Table III (UA)"."""

patch(REV, [(R1_OLD, R1_NEW), (R2_OLD, R2_NEW), (R3_OLD, R3_NEW)])
