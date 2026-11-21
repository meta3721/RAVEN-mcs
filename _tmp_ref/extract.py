import re, pathlib
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
lines = p.read_text(encoding="utf-8").splitlines()
def grab(a, b):
    return " ".join(lines[a-1:b])
# authored passages only; strip the record's own label dashes and markdown emphasis
parts = [
    grab(309, 320).replace("T3 — ", "T3: "),          # restated T3
    grab(399, 402),                                     # restated F-2
    grab(92, 93),                                       # D-6 changed sentence
    grab(237, 239),                                     # L7 changed sentence
]
out = re.sub(r"\*\*|`", "", "\n\n".join(parts))
pathlib.Path("_tmp_ref/t3_corrected_prose.txt").write_text(out + "\n", encoding="utf-8")
print("authored words:", len(out.split()))
print("em dashes in authored text:", out.count("\u2014"))
