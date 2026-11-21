import json
from collections import Counter
from pathlib import Path

p = Path(r"D:\Cursor\raven.mcs\_paper_work\ccfa-review-reports\citation_audit_compare.json")
data = json.loads(p.read_text(encoding="utf-8"))
print("COUNTS", dict(Counter(r["verdict"] for r in data)))
print()
for v in ["needs_fix", "check_suggested", "unverifiable", "verified"]:
    print("====", v, "====")
    for r in data:
        if r["verdict"] != v:
            continue
        rec = r.get("record") or {}
        print(f"[{r['n']}] {r['key']} src={r['source']}")
        print("  BIB year/vol/iss/pages/doi:", r["bib"]["year"], r["bib"]["volume"], r["bib"]["number"], r["bib"]["pages"], r["bib"]["doi"])
        print("  BIB authors:", r["bib"]["author"][:120])
        if rec:
            print("  SRC year/vol/iss/pages/doi:", rec.get("year"), rec.get("volume"), rec.get("issue"), rec.get("pages"), rec.get("doi"))
            print("  SRC authors:", "; ".join(rec.get("authors") or [])[:160])
            print("  SRC title:", (rec.get("title") or "")[:110])
        for iss in r["issues"]:
            print("   -", iss)
        print()
