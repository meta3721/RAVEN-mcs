import re, pathlib
p = pathlib.Path("TO_OVERLEAF_paper_tmc_r1_clean/reference.bib")
txt = p.read_text(encoding="utf-8", errors="replace")
entries = re.split(r"\n@", txt)
rows=[]
for e in entries:
    if not e.strip(): continue
    def g(f):
        m = re.search(f + r"\s*=\s*[{\"](.+?)[}\"],?\s*\n", e, re.S|re.I)
        return m.group(1).strip() if m else ""
    j = g("journal"); b = g("booktitle"); y = g("year"); t = re.sub(r"\s+"," ", g("title"))
    if re.search(r"mobile computing|internet of things|infocom|transactions on", j+" "+b, re.I):
        rows.append((y, (j or b)[:44], t[:78]))
rows.sort()
print(f"{'year':<6} {'venue':<46} title")
for y,v,t in rows: print(f"{y:<6} {v:<46} {t}")
print("\ntotal bib entries:", len([e for e in entries if e.strip()]))
