import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-literature-monitor-20260927.md")
raw = p.read_bytes(); txt = raw.decode("utf-8")
print("size:", len(raw), "B | lines:", txt.count("\n"), "| CRLF:", raw.count(b"\r\n"), "| LF-only:", raw.count(b"\n")-raw.count(b"\r\n"))
# markdown table integrity: every contiguous table block must have a consistent pipe count
lines = txt.split("\n"); i=0; tables=0; bad=0
while i < len(lines):
    if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
        hdr = lines[i].count("|"); rows=[]; j=i
        while j < len(lines) and lines[j].startswith("|"):
            rows.append((j+1, lines[j].count("|"))); j+=1
        tables+=1
        off = [(ln,c) for ln,c in rows if c!=hdr]
        if off: bad+=1; print(f"  MISMATCH table@line{i+1}: header pipes={hdr} offenders={off}")
        i=j
    else: i+=1
print(f"tables checked: {tables} | mismatched: {bad}")
# non-ascii sanity (CJK/arrows present means UTF-8 path is fine)
print("non-ascii chars:", sum(1 for c in txt if ord(c)>127))
print("headings:", [l for l in lines if l.startswith("#")])
