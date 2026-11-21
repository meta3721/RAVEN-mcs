import sys
try:
    import fitz  # pymupdf
except Exception:
    import pymupdf as fitz
targets = {
    "TO_OVERLEAF_paper_tmc_r1_clean/main.pdf": [
        "not the range attainable when",
        "constant within a stratum rather than varying per",
        "drawn once",
    ],
    "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf": [
        "protocol quantities rather than per-unit",
        "constant within every",
        "without tilting",
        "Neither margin varies at the unit level",
    ],
}
for path, needles in targets.items():
    doc = fitz.open(path)
    flat = " ".join(p.get_text() for p in doc).replace("\n", " ")
    flat = " ".join(flat.split())
    print(f"{path}: {doc.page_count} pages")
    for n in needles:
        print(f"   {'FOUND' if n in flat else 'MISSING'}  {n!r}")
    doc.close()
