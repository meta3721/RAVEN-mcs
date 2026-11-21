import pathlib, zipfile, hashlib
root = pathlib.Path("TO_OVERLEAF_paper_tmc_r1_clean")
out  = pathlib.Path("TO_OVERLEAF_paper_tmc_r1_clean.zip")
TOP  = ["main.tex","appendix.tex","supplemental.tex","reference.bib",
        "main.bbl","supplemental.bbl","main.aux","supplemental.aux",
        "main.pdf","supplemental.pdf","make_figures.py"]
DIRS = ["figures","figure_data"]
EXCL = ("ccfa-review-reports","__pycache__","_check.txt")
files=[]
for f in TOP:
    p = root/f
    if p.is_file(): files.append(p)
    else: print("  MISSING (skipped):", f)
for d in DIRS:
    files += sorted(p for p in (root/d).rglob("*") if p.is_file())
files = [p for p in files if not any(x in p.parts for x in EXCL)
         and p.suffix.lower() not in (".log",".blg")]
if out.exists(): out.unlink()
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, str(pathlib.Path(root.name)/p.relative_to(root)))
print("packaged %d files -> %s (%.2f MB)" % (len(files), out.name, out.stat().st_size/1e6))
for p in sorted(files, key=lambda q: str(q)):
    print("   %-58s %8d B" % (str(p.relative_to(root)), p.stat().st_size))
