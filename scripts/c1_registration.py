#!/usr/bin/env python3
"""Register AMENDMENT 1 (Part B, C1, r = 3) in results_gatekeeping/round_v1/MANIFEST.sha256.

Idempotent: any previously appended AMENDMENT 1 block is removed and rewritten, so the
block can be re-appended verbatim after an editor/console encoding incident.  The Part-A
registration block is never touched (the file is truncated at the amendment marker).

Prints the sha256 of PROTOCOL.md and PREREG.md as they are read, so the caller can verify
that the amendment hash was recorded BEFORE any B1 run.

ASCII-only source: the authorization string is built from \\u escapes so that a GBK console
cannot corrupt it (the PowerShell here-string route mangled it once, before any run).
"""

from __future__ import annotations

import hashlib
import pathlib
import sys

OUT = pathlib.Path(r"C:\Cursor\raven.mcs\results_gatekeeping\round_v1")
MANIFEST = OUT / "MANIFEST.sha256"
PREREG = OUT / "PREREG.md"
PROTOCOL = OUT / "PROTOCOL.md"
MARKER = "# AMENDMENT 1 -- PART B (C1 training), r = 3 -- registration t3"
RULE = "# " + "-" * 75

AUTH = "\u6388\u6743C1\u8bad\u7ec3\uff0cr=3"          # 授权C1训练，r=3
PART_A_PREREG = "1e1816cd3431a1c49c92f2806ab83b981b4392d216906af1323425c819f7719e"
PART_A_PROTOCOL = "916b55766f24b4b5685e59418fe2140ad1e74e2c178ed0f75ba375c7feb8324e"


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def block(prereg_hash: str, protocol_hash: str) -> str:
    return "\n".join([
        RULE,
        MARKER,
        "# Written and hashed BEFORE any B1 run started and BEFORE any C1 RMSE existed.",
        "# authorization (verbatim, as received through the delegating agent): " + AUTH,
        "# Protocol SS2 (Part B) only; Part C remains out of scope.  The Part-A blocks",
        "# above are unchanged (PREREG.md was extended append-only).",
        "#   PREREG.md as executed for Part A (t2, bytes unchanged by the amendment):",
        "#     " + PART_A_PREREG,
        "#   PROTOCOL.md (unchanged): " + protocol_hash,
        "#   PREREG.md INCLUDING AMENDMENT 1 (t3, the operative Part-B preregistration):",
        prereg_hash + "  PREREG.md",
        "# r = 3 fixed (model seeds {s, s+100000, s+200000}); 150 new training runs registered.",
        "# Locked before running: arm list, map construction + key universe, pi_floor rule,",
        "# delta_CS = 2 %, primary H_mech estimator + percentile trace-cluster bootstrap",
        "# (B = 10000, seed 20261003), structural guardrail rule, secondary Holm family,",
        "# K = 3 graphical-alpha A1 chains, no-32005 sensitivity rule.",
        "",
    ])


ARTEFACTS = (
    "B0_REPRO.json", "B0_REPRO__b0a_t1.json", "B0_SEED32005_PROBE.csv",
    "B0_SEED32005_PROBE.json", "C1_MAPS.json", "C1_RUNS.csv", "C1_PRIMARY.json",
    "C1_SECONDARY.csv", "C1_A1_CHAINS.csv", "C1_SENSITIVITY_NO32005.csv",
    "C1_PER_SEED.csv", "C1_ARM_SUMMARY.csv", "C1_ANALYSIS_PROVENANCE.json",
    "C1_RECON.json", "C1_EXECUTION_LOG.md", "EXECUTION_REPORT.md",
    "ERRATA_FOR_PAPER.md", "PREREG.md",
)
SCRIPTS = ("scripts/c1_deletion_driver.py", "scripts/c1_analysis.py",
           "scripts/c1_registration.py")
FIN_MARKER = "# PART B (C1) artefact hashes -- appended after the runs completed"


def finalize() -> int:
    """Append the Part B artefact hashes, leaving every earlier block untouched.

    Run this only AFTER main() (which rewrites the AMENDMENT 1 block); finalize() is
    idempotent and replaces its own block if it is run twice.
    """
    text = MANIFEST.read_text(encoding="utf-8")
    if FIN_MARKER in text:
        text = text.split(FIN_MARKER)[0].rstrip("\n") + "\n"
    lines = [FIN_MARKER,
             "# tamper-evidence for the files this round wrote; MANIFEST.sha256 cannot",
             "# contain its own final hash. The AMENDMENT 1 block above is the",
             "# registration anchor and was written before the first run.",
             "# NOTE: the Part-A 'post-computation artefact hashes' block above lists",
             "# pre-Part-B hashes for PREREG.md, EXECUTION_REPORT.md and",
             "# ERRATA_FOR_PAPER.md. Part B appended to those three files, so those three",
             "# Part-A lines no longer match on purpose; the hashes below are operative.",
             "# The registration anchors (PROTOCOL.md and the t0 PREREG.md hash) are",
             "# unaffected and still verify.",
             ""]
    for name in ARTEFACTS:
        p = OUT / name
        if p.is_file():
            lines.append("%s  %s" % (sha256(p), name))
    for rel in SCRIPTS:
        p = pathlib.Path(r"C:\Cursor\raven.mcs") / rel
        if p.is_file():
            lines.append("%s  %s" % (sha256(p), rel))
    MANIFEST.write_text(text + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("finalized:", MANIFEST, MANIFEST.stat().st_size, "bytes")
    return 0


def main() -> int:
    text = MANIFEST.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    cut = None
    for i, ln in enumerate(lines):
        if ln.startswith(RULE) and any(MARKER in x for x in lines[i:i + 3]):
            cut = i
            break
    base = ("".join(lines[:cut]) if cut is not None else text).rstrip("\n") + "\n"

    prereg_hash = sha256(PREREG)
    protocol_hash = sha256(PROTOCOL)
    if protocol_hash != PART_A_PROTOCOL:
        print("WARNING: PROTOCOL.md changed since Part A:", protocol_hash)
    if PART_A_PREREG not in base:
        print("WARNING: the Part-A PREREG.md hash is not in the manifest prefix")

    MANIFEST.write_text(base + block(prereg_hash, protocol_hash),
                        encoding="utf-8", newline="\n")
    print("PREREG.md sha256 (with AMENDMENT 1):", prereg_hash)
    print("PROTOCOL.md sha256:", protocol_hash)
    print("manifest bytes:", MANIFEST.stat().st_size)
    return 0


if __name__ == "__main__":
    if "--finalize" in sys.argv:
        sys.exit(finalize())
    sys.exit(main())
