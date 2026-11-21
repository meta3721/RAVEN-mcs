import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
raw = p.read_bytes(); txt = raw.decode("utf-8"); lines = txt.split("\n")
def pipes(s): return s.replace("\\|", "").count("|")   # count UNESCAPED pipes only
i=0; tables=0; bad=0; rows=0
while i < len(lines):
    if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
        hdr = pipes(lines[i]); j=i
        while j < len(lines) and lines[j].startswith("|"):
            rows+=1
            if pipes(lines[j]) != hdr:
                bad+=1; print("  MISMATCH line %d: header=%d row=%d" % (j+1, hdr, pipes(lines[j])))
            j+=1
        tables+=1; i=j
    else: i+=1
print("FINAL: tables=%d rows=%d mismatched=%d | size=%dB lines=%d CRLF=%d" % (tables, rows, bad, len(raw), len(lines), raw.count(b"\r\n")))
print("escaped-pipe rows:", sum(1 for l in lines if "\\|" in l))
