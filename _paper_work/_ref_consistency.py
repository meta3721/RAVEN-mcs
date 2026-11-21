"""Static cross-reference consistency check for main.tex (no LaTeX engine needed)."""
import re
from pathlib import Path

tex = Path(r"D:\Cursor\raven.mcs\_paper_work\main.tex").read_text(encoding="utf-8", errors="replace")

labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
refs = set()
for m in re.finditer(r"\\(?:ref|eqref|autoref|Cref|pageref)\{([^}]+)\}", tex):
    refs.add(m.group(1))

dup_labels = [l for l in labels if len(re.findall(r"\\label\{" + re.escape(l) + r"\}", tex)) > 1]
undefined = sorted(refs - labels)
unused_labels = sorted(labels - refs)

print(f"labels: {len(labels)}")
print(f"refs (unique targets): {len(refs)}")
print(f"duplicate labels: {dup_labels if dup_labels else 'none'}")
print(f"UNDEFINED refs (no matching label): {len(undefined)}")
for u in undefined:
    print("  UNDEF:", u)
print(f"labels never referenced: {len(unused_labels)}")
for u in unused_labels:
    print("  unused-label:", u)
