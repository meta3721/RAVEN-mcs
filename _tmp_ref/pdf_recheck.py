import pathlib
t = " ".join(pathlib.Path("_tmp_ref/main_all2.txt").read_text(encoding="utf-8", errors="replace").split())
print("PDF re-check:", "ceiling present" if "Recoverable-Gain Ceiling" in t and "0.217%" in t else "MISSING")
