import pathlib, re
t = " ".join(pathlib.Path("_tmp_ref/main_all.txt").read_text(encoding="utf-8", errors="replace").split())
for k in ("Recoverable-Gain Ceiling","selectionaware reweighting","It did not fire",
          "0.217%","270 runs","45 regenerated traces","0.104%","0.251%","0.17","0.36",
          "0.70","0.80","1521"):
    print(f"  {k:<32} {'FOUND' if k in t else 'NOT FOUND'}")
