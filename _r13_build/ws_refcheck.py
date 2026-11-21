"""Reference check: for each candidate top-level entry, does any bounded text file mention its name?"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")

CANDIDATES = [
    ".pytest_cache", ".sync_diag", "_probe_new", "_tmp_pack", "_tmp_ref", ".upstream_backup",
    "_handoff_sag_v1.1", "_handoff_sag_g1_r1", "_handoff_sag_g1_r1b", "_handoff_sag_g1_r1c",
    "_handoff_sag_g1_r1d", "_handoff_sag_g1_r1e",
    "literature-search-20260910-mcs-mobile-field-datasets",
    "literature-search-20260911-cityscanner-no2-bounds",
    "literature-search-20260919-raven-mcs-citation-verify",
    "literature-search-20260922-exogenous-mobile-datasets",
    "literature-search-20261009-concentrated-target",
    "literature-search-20261010-selection-corrected-aggregation",
    ".r11_work", ".rb_work", ".m7_work", ".r3_work", ".s1_work", "_r13_build",
    "tmp", "outputs", "deliverables", "evidence", "logs", "snapshots",
    "paper_ready_r1", "paper_ready_r2", "_paper_work", "post_review", "archive",
    "results_traffic_e2", "results_w1_ladder", "results_main_rebuild_r1",
]

# bounded scan set: text files in the dirs that actually carry references
SCAN_DIRS = ["", "ccf-review-report", "ccfa-review-reports", "snapshots", "scripts", "src",
             "TO_OVERLEAF_paper_tmc_r1_clean", "RAVEN_MCS_PUBLIC_REPRO_R1", "_r13_build",
             "configs", "docs", "tools", "_paper_work"]
SUFFIX = {".md", ".tex", ".py", ".json", ".csv", ".txt", ".yml", ".yaml", ".toml"}
LIMIT = 12          # files >12 MB are skipped (data blobs)

texts: list[tuple[str, str]] = []
for d in SCAN_DIRS:
    base = ROOT / d if d else ROOT
    if d == "":
        for p in base.glob("*"):
            if p.is_file() and p.suffix.lower() in SUFFIX:
                texts.append((p.name, str(p)))
    else:
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in SUFFIX:
                texts.append((str(p.relative_to(ROOT)), str(p)))
print(f"scanned {len(texts)} text files")

bodies: list[tuple[str, str]] = []
for rel, path in texts:
    try:
        if pathlib.Path(path).stat().st_size > LIMIT * 1024 * 1024:
            continue
        bodies.append((rel, pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")))
    except OSError:
        continue
print(f"loaded {len(bodies)} files\n")

print(f"{'candidate':<56}{'hits':>6}  first referencing file")
for c in CANDIDATES:
    n = 0
    first = ""
    for rel, body in bodies:
        if c in body:
            n += body.count(c)
            if not first:
                first = rel
    print(f"  {c:<54}{n:>6}  {first}")
