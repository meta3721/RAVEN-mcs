import pathlib, re
for f in ("EXPERIMENT_REPORT_FOR_VERIFICATION.md","REVIEW_OF_REVIEW_20260927.md"):
    p = pathlib.Path("results_active_set_repair/round_v1")/f
    raw = p.read_bytes(); lines = raw.decode("utf-8").split("\n")
    def pipes(s): return s.replace("\\|","").count("|")
    i=0;t=0;b=0;r=0
    while i < len(lines):
        if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
            h=pipes(lines[i]); j=i
            while j < len(lines) and lines[j].startswith("|"):
                r+=1
                if pipes(lines[j])!=h: b+=1; print("  MISMATCH", f, "line", j+1, h, pipes(lines[j]))
                j+=1
            t+=1; i=j
        else: i+=1
    print("%-44s tables=%d rows=%d bad=%d | %dB CRLF=%d" % (f, t, r, b, len(raw), raw.count(b"\r\n")))
