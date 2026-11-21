"""AI-flavour scan for the manuscript prose. Read-only; prints ASCII only."""
from __future__ import annotations

import pathlib
import re
import statistics as st
from collections import Counter

SRC = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean")

LEXICON = {
    "inflated": ["delve", "tapestry", "crucial", "pivotal", "comprehensive", "holistic", "nuanced",
                 "multifaceted", "paradigm", "synergy", "harness", "navigate", "illuminate", "elucidate",
                 "showcase", "testament", "hallmark", "cornerstone", "endeavor", "myriad", "plethora",
                 "realm", "landscape", "intricate", "seamless", "foster", "leverage", "unprecedented",
                 "groundbreaking", "cutting-edge", "state-of-the-art", "underscore", "underscores"],
    "connectives": ["moreover", "furthermore", "additionally", "notably", "importantly", "consequently",
                    "in essence", "arguably", "in particular", "thus", "therefore", "hence"],
    "throat_clearing": ["it is worth", "it should be noted", "it is important", "in this paper",
                        "in this work", "we now turn", "as mentioned", "as noted above"],
    "modal_hedges": ["may", "might", "could", "potentially", "arguably", "relatively"],
}
FORMULAIC = ["not only", "but also", "plays a vital role", "plays a key role", "paves the way",
             "in the realm of", "aims to", "is designed to", "serves as", "acts as"]


def prose_of(p: pathlib.Path) -> str:
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"(?m)^\s*%.*$", "", t)
    t = re.sub(r"\\begin\{tabular\*?\}.*?\\end\{tabular\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{(equation|align|eqnarray)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", " ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " M ", t)
    t = re.sub(r"\\(cite|ref|label|eqref|includegraphics|url)\{[^}]*\}", " ", t)
    t = re.sub(r"\\(begin|end)\{[^}]*\}", " ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", " ", t)
    t = re.sub(r"[{}\\~^_&]", " ", t)
    return re.sub(r"[ \t]+", " ", t)


def sentences(prose: str) -> list[str]:
    flat = re.sub(r"\s+", " ", prose)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", flat)
    return [s.strip() for s in parts if len(s.split()) >= 4]


for name in ("main.tex", "appendix.tex"):
    prose = prose_of(SRC / name)
    sents = sentences(prose)
    lens = [len(s.split()) for s in sents]
    words = sum(lens)
    print(f"=== {name} ===")
    print(f"  sentences {len(sents)}  words {words}  mean len {st.mean(lens):.1f}  "
          f"sd {st.pstdev(lens):.1f}  cv {st.pstdev(lens) / st.mean(lens):.2f}  "
          f"median {st.median(lens):.0f}")

    # modal length concentration
    c = Counter(lens)
    top = c.most_common(4)
    print(f"  most common lengths: {top}  (share of sentences in 18-30 words: "
          f"{100 * sum(1 for n in lens if 18 <= n <= 30) / len(lens):.0f}%)")

    # five-sentence runs with near-identical length (the checker's warning)
    runs = []
    for i in range(len(lens) - 4):
        w = lens[i:i + 5]
        if max(w) - min(w) <= 4:
            runs.append((i, w, sents[i][:70]))
    print(f"  five-sentence near-uniform runs (max-min <= 4 words): {len(runs)}")
    for i, w, head in runs[:4]:
        print(f"    L{i}: {w}  \"{head}...\"")

    # lexicon
    low = prose.lower()
    for label, words_ in LEXICON.items():
        hits = {w: low.count(w) for w in words_ if re.search(rf"\b{re.escape(w)}\b", low)}
        hits = {k: v for k, v in hits.items() if v}
        tot = sum(hits.values())
        per1000 = 1000 * tot / words if words else 0
        print(f"  {label:<15} {tot:>4} hits ({per1000:.2f}/1000w)  {hits if hits else ''}")

    hits = {w: low.count(w) for w in FORMULAIC if w in low}
    print(f"  formulaic       {sum(hits.values()):>4} hits  {hits if hits else ''}")

    # openers
    openers = Counter(s.split()[0] for s in sents if s.split())
    print(f"  top sentence openers: {openers.most_common(6)}")
    anaph = sum(v for k, v in openers.items() if k in ("This", "These", "Such"))
    print(f"  'This/These/Such' openers: {anaph} ({100 * anaph / len(sents):.0f}% of sentences)")

    # triads: three comma-separated items ending with 'and'
    triads = len(re.findall(r"\b\w+, \w+(?:,)? and \w+", prose))
    print(f"  comma triads (X, Y, and Z): {triads} ({1000 * triads / words:.2f}/1000w)")

    # nominalisation density
    noms = len(re.findall(r"\b\w+(?:tion|tions|ment|ments|ity|ities|ness|ance|ence)\b", prose))
    print(f"  nominalisations: {noms} ({1000 * noms / words:.1f}/1000w)")

    # participial closers: sentence ends with ", <verb>ing ..."
    part = len(re.findall(r",\s+\w+ing\b[^.]*\.", prose))
    print(f"  trailing participial clauses: {part}")
    print()
