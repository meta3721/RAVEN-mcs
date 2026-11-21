"""Second pass: academic-filler lexicon, participial-clause contexts, and the flagged uniform runs."""
from __future__ import annotations

import pathlib
import re

SRC = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean")
FILLER = ["ensure", "ensures", "provide", "provides", "demonstrate", "demonstrates", "highlight",
          "highlights", "emphasize", "exhibit", "exhibits", "facilitate", "enable", "enables",
          "significant", "significantly", "substantial", "substantially", "various", "diverse",
          "robust", "novel", "accurate", "effective", "extensive", "remarkable", "overall",
          "in summary", "it follows that", "note that", "observe that", "we note", "aligns",
          "align", "thereby", "whereby", "yielding", "indicating", "suggesting", "highlighting"]

for name in ("main.tex", "appendix.tex"):
    t = (SRC / name).read_text(encoding="utf-8")
    lines = t.splitlines()
    body = re.sub(r"(?m)^\s*%.*$", "", t)
    words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", body))
    low = body.lower()
    print(f"=== {name} ({words} words) ===")
    hits = {w: len(re.findall(rf"\b{w}\b", low)) for w in FILLER}
    hits = {k: v for k, v in hits.items() if v}
    print("  filler:", dict(sorted(hits.items(), key=lambda kv: -kv[1])))
    print(f"  total filler {sum(hits.values())} ({1000 * sum(hits.values()) / words:.2f}/1000w)")

    print("  --- trailing participial clauses (prose lines only, 12 shown)")
    n = 0
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("%") or "&" in ln or "tabular" in ln:
            continue
        if re.search(r",\s+(thereby|yielding|indicating|suggesting|highlighting|enabling|allowing|"
                     r"making|leading|providing|keeping|so)\b", ln):
            print(f"    L{i}: {ln.strip()[:118]}")
            n += 1
            if n >= 12:
                break
    if n == 0:
        print("    none with a formulaic connective")

    print("  --- the lines that produced the uniform-sentence-run warning")
    for target in {"main.tex": (80, 82, 108, 112), "appendix.tex": (51, 55)}.get(name, ()):
        if 1 <= target <= len(lines):
            print(f"    L{target}: {lines[target - 1].strip()[:118]}")
    print()
