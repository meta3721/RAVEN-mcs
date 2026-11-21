import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-tier2-directions-20260927.md")
raw = p.read_bytes(); lines = raw.decode("utf-8").split("\n")
def pipes(s): return s.replace("\\|","").count("|")
i=0;t=0;b=0;r=0
while i < len(lines):
    if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
        h=pipes(lines[i]); j=i
        while j < len(lines) and lines[j].startswith("|"):
            r+=1
            if pipes(lines[j])!=h: b+=1; print("  MISMATCH line", j+1)
            j+=1
        t+=1; i=j
    else: i+=1
print("tables=%d rows=%d bad=%d | %dB lines=%d CRLF=%d" % (t,r,b,len(raw),len(lines),raw.count(b"\r\n")))
# item numbering completeness
nums = [int(m.group(1)) for m in re.finditer(r"^\| (\d+) \|", raw.decode("utf-8"), re.M)]
print("numbered method rows:", len(nums), "->", "1..44 complete" if nums == list(range(1,45)) else f"GAP: {sorted(set(range(1,45))-set(nums))}")
groups = re.findall(r"^### ([甲-庚])、(.+?) — (.+)$", raw.decode("utf-8"), re.M)
for g, name, layer in groups: print(f"  {g}  {name[:34]:<36} {layer}")
