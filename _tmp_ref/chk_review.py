import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-tmc-review.md")
raw = p.read_bytes(); lines = raw.decode("utf-8").split("\n")
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
print("review: tables=%d rows=%d mismatched=%d | %dB lines=%d CRLF=%d" % (t,r,b,len(raw),len(lines),raw.count(b"\r\n")))
# arithmetic self-check of both scorecards
W = [0.10,0.20,0.25,0.15,0.10,0.10,0.05,0.05]
hist = [2,3,2,4,3,2,3,4]; cur_prog = [2,4,2,4,2,2,3,4]; cur_abs = [2,4,2,4,2,2,3,4]
print("historical weighted (corrected) = %.4f   (round 2 printed 2.85)" % sum(w*s for w,s in zip(W,hist)))
print("progress weighted delta         = %+.4f" % sum(w*(c-h) for w,c,h in zip(W,cur_prog,hist)))
print("absolute readiness weighted     = %.4f -> 4/10 weak reject" % sum(w*s for w,s in zip(W,cur_abs)))
