"""Targeted rhythm + disclosure scan on the abstract and introduction."""
from __future__ import annotations

import pathlib
import re
import statistics as st

t = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
a = t.index("\\begin{abstract}") + len("\\begin{abstract}")
b = t.index("\\end{abstract}")
abs_raw = t[a:b]
abs_clean = re.sub(r"\$[^$]*\$", " M ", abs_raw)
words = re.findall(r"[A-Za-z][A-Za-z'-]*", abs_clean)
print("=== abstract ===")
print("  words:", len(words), " (TMC regular paper range: 100-200)")
print("  paragraph breaks (blank lines):", len([l for l in abs_raw.splitlines() if not l.strip()]))
sents = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", re.sub(r"\s+", " ", abs_clean).strip())
sents = [s for s in sents if s.strip()]
print(f"  sentences: {len(sents)}")
for i, s in enumerate(sents, 1):
    print(f"    [{len(s.split()):>3}w] {s.strip()[:104]}")
lens = [len(s.split()) for s in sents]
print(f"  mean {st.mean(lens):.1f}  sd {st.pstdev(lens):.1f}  cv {st.pstdev(lens)/st.mean(lens):.2f}")

intro = t[t.index("\\section{Introduction}"):t.index("\\section{Related Work}")]
intro_clean = re.sub(r"\\(cite|ref|label|eqref)\{[^}]*\}", " ", intro)
intro_clean = re.sub(r"\$[^$]*\$", " M ", intro_clean)
intro_clean = re.sub(r"\\[a-zA-Z]+\*?", " ", intro_clean)
intro_clean = re.sub(r"[{}\\~^_&]", " ", intro_clean)
isents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", re.sub(r"\s+", " ", intro_clean)) if len(s.split()) >= 5]
ilens = [len(s.split()) for s in isents]
print("\n=== introduction prose ===")
print(f"  sentences {len(isents)}  mean {st.mean(ilens):.1f}  sd {st.pstdev(ilens):.1f}  "
      f"cv {st.pstdev(ilens)/st.mean(ilens):.2f}  share 18-30w {100*sum(1 for n in ilens if 18<=n<=30)/len(ilens):.0f}%")
for i in range(len(ilens) - 4):
    w = ilens[i:i + 5]
    if max(w) - min(w) <= 6:
        print(f"    near-uniform run {w}: \"{isents[i][:80]}\"")
        break

print("\n=== template markers in abstract + introduction ===")
PAT = ["however", "to bridge this gap", "to address the above", "existing approaches", "specifically",
       "furthermore", "in this way", "integrated framework", "rigorous", "extensive",
       "the major contributions", "demonstrate that", "novel", "comprehensive"]
both = (abs_clean + intro_clean).lower()
for p in PAT:
    n = both.count(p)
    if n:
        print(f"  {p!r}: {n}")

print("\n=== are the negatives still disclosed anywhere in main.tex? ===")
low = t.lower()
for probe in ["does not establish consistent prediction", "does not consistently improve prediction",
              "lower group mismatch and runtime than the full", "projection can achieve lower",
              "projection is faster", "not additive", "no consistent prediction",
              "does not improve prediction", "trade-off", "trade-offs"]:
    print(f"  {probe!r}: {low.count(probe)}")
