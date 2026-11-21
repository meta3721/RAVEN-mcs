import pathlib, re
p = pathlib.Path("results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md")
raw = p.read_bytes(); lines = raw.decode("utf-8").split("\n")
def pipes(s): return s.replace("\\|","").count("|")
i=0;t=0;b=0;r=0
while i < len(lines):
    if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
        h=pipes(lines[i]); j=i
        while j < len(lines) and lines[j].startswith("|"):
            r+=1
            if pipes(lines[j])!=h: b+=1; print("  MISMATCH line %d hdr=%d row=%d"%(j+1,h,pipes(lines[j])))
            j+=1
        t+=1; i=j
    else: i+=1
print("tables=%d rows=%d mismatched=%d | size=%dB lines=%d CRLF=%d"%(t,r,b,len(raw),len(lines),raw.count(b"\r\n")))
