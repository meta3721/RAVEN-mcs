"""Round-15 review inputs: verify the manuscript revision, the new evidence, and the build."""
from __future__ import annotations

import hashlib
import pathlib
import subprocess

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
P = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
BASE = ROOT / "_r13_build/main_prev_68D9B44F.tex"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


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
d4 = BASE.read_bytes().replace(OLD_BLOCK, NEW_BLOCK)
print("d4fb164d (round-14 target) :", sha(d4)[:16], len(d4), "B  match:",
      sha(d4).startswith("d4fb164df90f5948"))

cur = P.read_bytes()
print("current   (round-15 target):", sha(cur)[:16], len(cur), "B")
print("line endings: CRLF", cur.count(b"\r\n"), "| LF", cur.count(b"\n"))

import difflib
a = d4.decode("utf-8").splitlines(keepends=True)
b = cur.decode("utf-8").splitlines(keepends=True)
print("\n=== diff round-14 -> round-15 ===")
for l in difflib.unified_diff(a, b, "d4fb164d", "current", n=1):
    print("  " + l.rstrip("\n"))

print("\n=== new evidence trees ===")
for t in ("results_traffic_e1", "results_traffic_struct"):
    d = ROOT / t / "round_v1"
    fs = [p for p in d.rglob("*") if p.is_file() and "__pycache__" not in p.as_posix()
          and "/runs/" not in p.as_posix()]
    print(f"  {t}/round_v1: {len(fs)} files")
    for p in sorted(fs)[:8]:
        print("     ", p.relative_to(d).as_posix(), p.stat().st_size, "B")

print("\n=== rebuild and page count ===")
out = ROOT / "_r13_build/build_r15"
out.mkdir(parents=True, exist_ok=True)
for tex in ("supplemental.tex", "main.tex", "main.tex"):
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                    f"-output-directory={out}", tex], cwd=str(P.parent), capture_output=True)
log = (out / "main.log").read_text(encoding="utf-8", errors="replace")
slog = (out / "supplemental.log").read_text(encoding="utf-8", errors="replace")
for tag, lg in (("main", log), ("supplemental", slog)):
    line = [l for l in lg.splitlines() if "Output written on" in l]
    print(f"  {tag}: {line[0].strip() if line else 'NO PDF'} | errors={lg.count(chr(10) + '!')} "
          f"overfull={lg.count('Overfull')}")
print("\n  shipped tree main.pdf:", (P.parent / "main.pdf").stat().st_size, "B",
      __import__("datetime").datetime.fromtimestamp((P.parent / "main.pdf").stat().st_mtime))
