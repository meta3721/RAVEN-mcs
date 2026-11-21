"""Locate and repair the byte damage: the original main.tex contained lone CR bytes, which
universal-newline reading normalised to LF. Find them by hash search and restore the exact original."""
from __future__ import annotations

import hashlib
import pathlib
import subprocess

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
P = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
PRE = "d4fb164df90f59484bfe901b117399536cd727f4cb01fca6a3e09cb902486e60"
NEW = b"federated learner, not the weighting, limits the prediction endpoint."
OLD = b"federated learner, not the weighting, therefore limits the prediction endpoint."

cur = P.read_bytes()
R = cur.replace(NEW, OLD)
print("current:", len(cur), "B | reverted:", len(R), "B | original size recorded: 116806 B")
print("CR in current file:", cur.count(b"\r"), "| CR in reverted:", R.count(b"\r"))

# what does git's HEAD blob look like? (tells us the file's newline convention)
head = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:TO_OVERLEAF_paper_tmc_r1_clean/main.tex"],
                      capture_output=True).stdout
print("HEAD blob:", len(head), "B | CRLF:", head.count(b"\r\n"), "| lone CR:",
      head.count(b"\r") - head.count(b"\r\n"), "| LF:", head.count(b"\n"))

target = PRE
found = []

# k = 1: turn one LF back into a lone CR
pos = [i for i, b in enumerate(R) if b == 0x0A]
print("\nscanning", len(pos), "newline positions for a single lone-CR restoration ...")
for i in pos:
    cand = R[:i] + b"\r" + R[i + 1:]
    if hashlib.sha256(cand).hexdigest() == target:
        found = [i]
        break
print("k=1 result:", found if found else "not found")

if not found:
    # k = 2, but only among positions that are plausible (bounded: all pairs of newline positions)
    print("trying k=2 over", len(pos), "positions ...")
    for a in range(len(pos)):
        ia = pos[a]
        base = R[:ia] + b"\r" + R[ia + 1:]
        for b in range(a + 1, len(pos)):
            ib = pos[b]
            cand = base[:ib] + b"\r" + base[ib + 1:]
            if hashlib.sha256(cand).hexdigest() == target:
                found = [ia, ib]
                break
        if found:
            break
    print("k=2 result:", found if found else "not found")

out = ROOT / "_r13_build/CR_LOCATIONS.json"
out.write_text(__import__("json").dumps({"found": found, "n_newlines": len(pos)}, indent=2), encoding="utf-8")
print("\nwrote", out)
