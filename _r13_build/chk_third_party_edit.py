"""Characterise the third-party change to main.tex. Read-only except for a build into _r13_build."""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
SRC = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean"
P = SRC / "main.tex"
OLD = "3CC106CA4B6087D9D6A47D69936ABF0CD95914B0285E1A86D3C938ACB5AD161C"
SCOPE_PRE = {"abstract": "8ad25984072ed33e", "title": "b917a3c614517ece",
             "contribution_list": "82c33423ed680a72"}

txt = P.read_text(encoding="utf-8")
now = hashlib.sha256(P.read_bytes()).hexdigest()
st = P.stat()
print("=== the file now ===")
print(f"  sha256 {now}")
print(f"  {st.st_size} B (was 119922)   mtime {st.st_mtime}")
print(f"  equals the pre-edit hash: {now.upper() == OLD}")

print("\n=== did the four ceiling-ladder insertions land? ===")
MARKERS = {
    "1 ceiling paragraph": ["A third measurement bounds",
                            "Re-weighting the frozen spatial", "top-region shares",
                            "0.2558", "0.6322", "0.7746", "+0.097", "+0.130"],
    "2 limitations cross-ref": ["The concentration ladder of Section",
                                "not an artefact of a nearly uniform target"],
    "3 conclusion clause": ["the class's recoverable gain stays", "even when the whole deployment target is"],
    "4 availability naming": ["results\\_traffic\\_e2/"],
}
for site, keys in MARKERS.items():
    found = {k: txt.count(k) for k in keys}
    tot = sum(found.values())
    print(f"  {site:<26} {'PRESENT' if tot else 'absent':<8} {found}")

print("\n=== scope regions (I hold the pre-change hashes) ===")
def rh(a: int, b: int) -> str:
    return hashlib.sha256(txt[a:b].encode()).hexdigest()[:16]
cur = {"abstract": rh(txt.index("\\begin{abstract}"), txt.index("\\end{abstract}")),
       "title": hashlib.sha256(next(l for l in txt.splitlines()
                                    if l.startswith("\\title")).encode()).hexdigest()[:16],
       "contribution_list": rh(txt.index("Our main contributions are as follows."),
                               txt.index("\\end{itemize}",
                                         txt.index("Our main contributions are as follows.")))}
for k in SCOPE_PRE:
    print(f"  {k:<20} {SCOPE_PRE[k]} -> {cur[k]}  {'unchanged' if SCOPE_PRE[k] == cur[k] else '*** CHANGED ***'}")

print("\n=== other markers I tracked in earlier rounds ===")
for k in ("small margin", "0.175", "test-fitted constant", "training-mean predictor", "0.17 %",
          "we acknowledge", "publication-ready"):
    print(f"  {k:<26} {txt.count(k)}")

print("\n=== line/em-dash profile ===")
print(f"  lines {txt.count(chr(10))} (was 2345)   em dashes {txt.count('---')}")
print(f"  lines >120 chars: {sum(1 for l in txt.splitlines() if len(l) > 120)}")

OUT = ROOT / "_r13_build/build_chk"
OUT.mkdir(parents=True, exist_ok=True)
for tex in ("supplemental.tex", "main.tex", "main.tex"):
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                    f"-output-directory={OUT}", tex], cwd=str(SRC), capture_output=True)
log = (OUT / "main.log").read_text(encoding="utf-8", errors="replace")
m = re.search(r"Output written on .*main\.pdf \((\d+) pages", log)
n_err = len(re.findall(r"(?m)^!", log))
n_ovf = len(re.findall(r"Overfull \\[hv]box", log))
n_und = len(re.findall(r"(?i)undefined (reference|control|citation)", log))
pages = m.group(1) if m else "?"
print("\n=== build of the current file ===")
print(f"  main.pdf {pages} pages   errors={n_err}  overfull={n_ovf}  undefined={n_und}")
