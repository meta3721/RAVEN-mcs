"""Patch main.tex's availability entry line-based (EOL-agnostic), and report the real TE1 table path."""
from __future__ import annotations

import hashlib
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
M = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
raw = M.read_bytes()
crlf, nl = raw.count(bytes([13, 10])), raw.count(bytes([10]))
eol = b"\r\n" if crlf == nl else b"\n"
print("main.tex:", len(raw), "B  CRLF", crlf, " LF", nl, " -> eol", eol)
lines = raw.split(eol)
hits = [k for k, l in enumerate(lines) if b"remain in their separate result directories" in l]
print("  anchor lines:", [h + 1 for h in hits])
assert len(hits) == 1
i = hits[0]
print("  before:")
for l in lines[i - 2:i + 3]:
    print("   |", l.decode("utf-8"))
assert b"Later corrected W1 scores" in lines[i - 1], lines[i - 1]
assert b"revision evidence record." in lines[i + 1], lines[i + 1]
lines[i - 1:i + 2] = [
    b"Later corrected W1 scores, concentration, Adam, learning, and",
    b"geometry diagnostics are indexed, with file paths and scoring identities, in",
    b"\\texttt{submission\\_evidence/SUBMISSION\\_EVIDENCE\\_INDEX.md} beside the bundle.",
]
out = eol.join(lines)
M.write_bytes(out)
print("  after:", len(out), "B  sha256", hashlib.sha256(out).hexdigest()[:16])
for l in lines[i - 1:i + 3]:
    print("   |", l.decode("utf-8"))

# find the real TE1 per-seed table and package it
for cand in ("results_traffic_e1/round_v1/tables/TE1_CONFIRM.csv",
             "results_traffic_e1/round_v1/te1/tables/TE1_CONFIRM.csv"):
    p = ROOT / cand
    print(f"  {cand}: {'exists' if p.is_file() else 'missing'}")
    if p.is_file():
        dest = ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1/submission_evidence/TE1_CONFIRM.csv"
        shutil.copy2(p, dest)
        print("    packaged ->", dest.name, dest.stat().st_size, "B  sha256",
              hashlib.sha256(dest.read_bytes()).hexdigest()[:16])
        break
