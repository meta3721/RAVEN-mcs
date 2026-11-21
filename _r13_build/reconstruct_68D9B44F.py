"""Reconstruct 68D9B44F... (the version my round-13 review scored) and diff it against the current
manuscript, so the review knows exactly what changed at 2026-10-07 22:57."""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
CUR = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
BASE = ROOT / "_r13_build/main_prev_02447bfe.tex"
B3 = (ROOT / "_r13_build/BLOCK3_mechanism.txt").read_bytes().split(b"\n")
B4 = (ROOT / "_r13_build/BLOCK4_limitations.txt").read_bytes().split(b"\n")

cur = CUR.read_bytes()
base = BASE.read_bytes()
print("current  sha256:", hashlib.sha256(cur).hexdigest().upper()[:16], len(cur), "B")
print("02447bfe sha256:", hashlib.sha256(base).hexdigest().upper()[:16], len(base), "B")
print("block3 lines:", len(B3), "| block4 lines:", len(B4))

lines = base.split(b"\n")
recon = lines[:2151] + B3 + lines[2151:2197] + B4 + lines[2197:]
data = b"\n".join(recon)
h = hashlib.sha256(data).hexdigest().upper()
print()
print("reconstructed len   :", len(data))
print("reconstructed sha256:", h[:16])
print("target 68D9B44F...  : MATCH" if h.startswith("68D9B44F17A4E48D") else "NO MATCH - reconstruction is off")

if h.startswith("68D9B44F"):
    out = ROOT / "_r13_build/main_prev_68D9B44F.tex"
    out.write_bytes(data)
    print("wrote", out)
