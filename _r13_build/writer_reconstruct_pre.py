"""Reconstruct the exact pre-edit bytes (d4fb164d) from the byte-exact 68D9B44F copy plus the known
22:57 hunk, then diff my round-tripped content against it to see exactly what was damaged."""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
P = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
BASE = ROOT / "_r13_build/main_prev_68D9B44F.tex"      # byte-exact 68D9B44F, verified earlier
PRE = "d4fb164df90f59484bfe901b117399536cd727f4cb01fca6a3e09cb902486e60"

OLD_BLOCK = (b"delivered data for every local budget from $2$ to $20$ steps.  On that block\n"
             b"the federated learner, not the weighting, limits the endpoint.")
NEW_BLOCK = (b"delivered data.  The server applies $\\eta$ times the step-normalized client\n"
             b"update once per window, so the global step equals one gradient step whatever\n"
             b"the local budget, and raising that budget from $2$ to $20$ steps leaves the gap\n"
             b"unchanged.  Over the run the federated parameters move $0.26\\%$--$0.40\\%$ of\n"
             b"their initial norm on all three blocks, mostly through the output bias, while on\n"
             b"SensorScope the centralized reference, trained with Adam, moves its first layer\n"
             b"by $12\\%$.  The\n"
             b"federated learner, not the weighting, therefore limits the prediction endpoint.")

base = BASE.read_bytes()
assert base.count(OLD_BLOCK) == 1, f"old block count {base.count(OLD_BLOCK)}"
W = base.replace(OLD_BLOCK, NEW_BLOCK)
hw = hashlib.sha256(W).hexdigest()
print("reconstructed pre-edit bytes:", len(W), "B  sha256:", hw)
print("target d4fb164d...            :", PRE)
print("match:", hw == PRE)

if hw != PRE:
    raise SystemExit("reconstruction failed; cannot proceed safely")

# what does my round-tripped content look like versus the true original?
cur = P.read_bytes()
NEW_SENT = b"federated learner, not the weighting, limits the prediction endpoint."
OLD_SENT = b"federated learner, not the weighting, therefore limits the prediction endpoint."
R = cur.replace(NEW_SENT, OLD_SENT)
print("\nmy reverted content:", len(R), "B | true original:", len(W), "B | identical:", R == W)

if R != W:
    n = min(len(R), len(W))
    diffs = [(i, R[i], W[i]) for i in range(n) if R[i] != W[i]]
    print("differing byte positions:", len(diffs), "(plus a size difference of", len(R) - len(W), "B)")
    for i, a, b in diffs[:12]:
        ctx = W[max(0, i - 40):i + 20]
        print(f"  at {i}: mine=0x{a:02x} true=0x{b:02x} | context {ctx!r}")
    # where does the size difference sit?
    if len(R) > len(W):
        for i in range(n):
            if R[i:i + 20] != W[i:i + 20]:
                print("  first divergence at", i, "| mine:", R[i:i + 60], "| true:", W[i:i + 60])
                break
