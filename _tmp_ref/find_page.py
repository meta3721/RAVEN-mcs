import pathlib
pages = pathlib.Path("_tmp_ref/main_all.txt").read_text(encoding="utf-8", errors="replace").split("\f")
print("  total pages extracted:", len(pages))
for i, pg in enumerate(pages, 1):
    if "Recoverable-Gain" in pg or "selection-aware reweighting" in pg:
        print(f"  -> found on extracted page {i}")
        k = pg.find("Recoverable-Gain")
        if k < 0: k = pg.find("selection-aware")
        print("     context:", " ".join(pg[max(0,k-80):k+240].split()))
