"""Option 1 verification: no phi-as-selector text survives in the built PDFs."""
import pymupdf

STALE = (
    "forced RAVEN-Design", "RAVEN-Design (forced)", "frozen heuristic",
    "Design fraction", "NoDesign fallback", "Selection rule",
    "RAVEN-Design if and only if", "frozen zero-target heuristic",
)
NEED_MAIN = ("Design factor", "RAVEN-NoDesign", "7.9384", "8.6711", "1.0265", "1.2719",
             "Both Design settings are reported", "endpoint-dependent")
NEED_SUPPL = ("Design factor", "descriptive statistic", "7.4907", "8.6711", "does not select")

for tag, path, need in (("main", "main.pdf", NEED_MAIN), ("suppl", "supplemental.pdf", NEED_SUPPL)):
    doc = pymupdf.open(path)
    txt = " ".join(" ".join(p.get_text().split()) for p in doc)
    stale = [s for s in STALE if s in txt]
    print(f"{tag}: {doc.page_count} pages")
    print("   stale:", stale if stale else "none")
    for n in need:
        print("   " + ("FOUND  " if n in txt else "MISSING") + " " + repr(n))
    doc.close()
