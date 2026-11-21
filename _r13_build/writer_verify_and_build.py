"""Final verification of the writer edit, then compile and prose check.

Verification: replacing the whole new sentence (including the added scope clause) with the original
sentence must recover the exact pre-edit bytes d4fb164d.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
P = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
W = ROOT / "_r13_build/main_prev_68D9B44F.tex"
PRE = "d4fb164df90f59484bfe901b117399536cd727f4cb01fca6a3e09cb902486e60"

OLD_FULL = (b"by $12\\%$.  The\n"
            b"federated learner, not the weighting, therefore limits the prediction endpoint.")
NEW_FULL = (b"by $12\\%$.  Inside the class the method defines, the\n"
            b"federated learner, not the weighting, limits the prediction endpoint.")

cur = P.read_bytes()
h = hashlib.sha256(cur).hexdigest()
print("=== verification ===")
print("  current file      :", len(cur), "B  sha256", h)
print("  contains new text :", cur.count(NEW_FULL) == 1)
print("  old text gone     :", cur.count(OLD_FULL) == 0)

# rebuild the true pre-edit bytes independently, from the byte-exact 68D9B44F copy
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
recon = W.read_bytes().replace(OLD_BLOCK, NEW_BLOCK)
print("  pre-edit rebuild  :", len(recon), "B  sha256", hashlib.sha256(recon).hexdigest())
print("  pre-edit matches  :", hashlib.sha256(recon).hexdigest() == PRE)

reverted = cur.replace(NEW_FULL, OLD_FULL)
ok = hashlib.sha256(reverted).hexdigest() == PRE
print("  reverse recovers pre-edit exactly :", ok)
print("  => the ONLY content change is the one sentence" if ok else "  => MISMATCH")
if not ok:
    sys.exit(1)

# byte-level diff summary
import difflib
a = recon.decode("utf-8").splitlines(keepends=True)
b = cur.decode("utf-8").splitlines(keepends=True)
d = [l for l in difflib.unified_diff(a, b, "before", "after", n=1)]
print("\n=== diff ===")
for l in d:
    print("  " + l.rstrip("\n"))

# ---------- mandatory compile + page count (skill step 7) ----------
out = ROOT / "_r13_build/build_r14c"
out.mkdir(parents=True, exist_ok=True)
for tex in ("supplemental.tex", "main.tex", "main.tex"):
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                    f"-output-directory={out}", tex],
                   cwd=str(P.parent), capture_output=True)
mlog = (out / "main.log").read_text(encoding="utf-8", errors="replace")
slog = (out / "supplemental.log").read_text(encoding="utf-8", errors="replace")
print("=== compile ===")
for tag, log in (("main", mlog), ("supplemental", slog)):
    pages = [l for l in log.splitlines() if "Output written on" in l]
    print(f"  {tag}: {pages[0].strip() if pages else 'NO PDF'}")
    print(f"    errors={log.count(chr(10) + '!')} undefined={log.lower().count('undefined')} "
          f"overfull={log.count('Overfull')}")
