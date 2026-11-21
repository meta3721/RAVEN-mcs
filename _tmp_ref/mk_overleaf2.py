import pathlib, zipfile
root = pathlib.Path("TO_OVERLEAF_paper_tmc_r1_clean")
out  = pathlib.Path("TO_OVERLEAF_paper_tmc_r1_clean.zip")
# the five components the user named, plus build-support derived from main/supplemental
TOP = ["main.tex","appendix.tex","supplemental.tex","reference.bib",
       "main.aux","main.bbl","supplemental.aux","supplemental.bbl"]
files = []
for f in TOP:
    p = root/f
    if p.is_file(): files.append(p)
    else: print("  MISSING (skipped):", f)
files += sorted(p for p in (root/"figures").rglob("*") if p.is_file())
if out.exists(): out.unlink()
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, (pathlib.Path(root.name)/p.relative_to(root)).as_posix())
print("packaged %d files -> %s (%.2f MB)" % (len(files), out.name, out.stat().st_size/1e6))
for p in sorted(files, key=lambda q: str(q)):
    print("   %-52s %8d B" % (str(p.relative_to(root)).replace("\\","/"), p.stat().st_size))
