import re, pathlib
t = pathlib.Path("TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
i = t.index("\\subsection{Recoverable-Gain Ceiling}")
j = t.index("\\subsection{Limitations}")
body = t[i:j]
body = re.sub(r"\\label\{[^}]*\}", "", body)
body = re.sub(r"\$[^$]*\$", "X", body)
body = re.sub(r"\\[a-zA-Z]+\{?", "", body).replace("}", "").replace("\\", "")
body = re.sub(r"\s+", " ", body).strip()
pathlib.Path("_tmp_ref/ceiling_prose.txt").write_text(body, encoding="utf-8")
print(f"  {len(body.split())} words")
print("  ", body[:300], "...")
