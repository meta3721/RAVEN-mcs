import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
raw = p.read_bytes(); txt = raw.decode("utf-8"); lines = txt.split("\n")
print("size %d B | lines %d | CRLF %d | LF-only %d" % (len(raw), len(lines), raw.count(b"\r\n"), raw.count(b"\n")-raw.count(b"\r\n")))
i=0; tables=0; bad=0
while i < len(lines):
    if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
        hdr = lines[i].count("|"); rows=[]; j=i
        while j < len(lines) and lines[j].startswith("|"):
            rows.append((j+1, lines[j].count("|"))); j+=1
        tables+=1
        off=[(ln,c) for ln,c in rows if c!=hdr]
        if off: bad+=1; print("  MISMATCH table@line%d: header=%d offenders=%s" % (i+1, hdr, off))
        i=j
    else: i+=1
print("tables %d | mismatched %d" % (tables, bad))
for s in ["N1\u2013N3", "+0.55 %", "five-way tie", "root cause not located", "0.35 %"]:
    print("  stale '%s': %d" % (s, txt.count(s)))
print("N-items:", sorted(set(re.findall(r"\bN[1-9]\b", txt))))
