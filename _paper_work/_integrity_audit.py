"""CCF integrity audit: citation existence + BibTeX sanity for main.tex."""
import re
from pathlib import Path

BASE = Path(r"D:\Cursor\raven.mcs\_paper_work")
tex = (BASE / "main.tex").read_text(encoding="utf-8", errors="replace")
bib = (BASE / "reference.bib").read_text(encoding="utf-8", errors="replace")

# 1. collect citation keys (handle \cite{a,b}, \citep, \citet, multiple)
cite_keys = set()
for m in re.finditer(r"\\(?:cite|citet|citep|citealp|citeauthor|citeyear)\*?\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", tex):
    for k in m.group(1).split(","):
        k = k.strip()
        if k:
            cite_keys.add(k)

# 2. collect bib keys
bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))

# 3. duplicate bib keys
bib_key_list = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib)
dupes = sorted({k for k in bib_key_list if bib_key_list.count(k) > 1})

# 4. basic brace balance per entry (coarse)
brace_balance_ok = (bib.count("{") == bib.count("}"))

missing = sorted(cite_keys - bib_keys)
unused = sorted(bib_keys - cite_keys)

print(f"cited keys: {len(cite_keys)}")
print(f"bib keys:   {len(bib_keys)}")
print(f"cited-but-missing-in-bib: {len(missing)}")
for k in missing:
    print("  MISSING:", k)
print(f"bib-but-never-cited: {len(unused)}")
for k in unused:
    print("  UNUSED:", k)
print(f"duplicate bib keys: {dupes if dupes else 'none'}")
print(f"bib brace balance ok: {brace_balance_ok}")
