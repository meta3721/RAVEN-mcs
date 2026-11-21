import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-tier2-directions-20260927.md")
raw = p.read_bytes(); txt = raw.decode("utf-8"); lines = txt.split("\n")
def pipes(s): return s.replace("\\|","").count("|")
i=0;t=0;b=0;r=0
while i < len(lines):
    if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
        h=pipes(lines[i]); j=i
        while j < len(lines) and lines[j].startswith("|"):
            r+=1
            if pipes(lines[j])!=h: b+=1; print("  MISMATCH line", j+1, h, pipes(lines[j]))
            j+=1
        t+=1; i=j
    else: i+=1
print("tables=%d rows=%d bad=%d | %dB lines=%d CRLF=%d" % (t,r,b,len(raw),len(lines),raw.count(b"\r\n")))
nums = [int(m.group(1)) for m in re.finditer(r"^\| (\d+) \|", txt, re.M)]
print("method rows:", len(nums), "->", "1..44 complete, no gaps" if nums == list(range(1,45)) else "PROBLEM")
print("group headings:", len(re.findall(r"^### .、", txt, re.M)), "(expect 7)")
for k in ("ζ","π^tar","π^opp","RMSE_μ","RMSE_ρ","γ ∈ [0,1]","ε > 0","local_steps","L1","CVaR","KLIEP","AIPW","MNAR","FedNova","MIFA","FedVARP","L2RW","FedLAW","e3_drifting"):
    if k not in txt: print("  missing token:", k)
