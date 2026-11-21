import pathlib, re
for f in ("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md",
          "results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md"):
    p = pathlib.Path(f); raw = p.read_bytes(); lines = raw.decode("utf-8").split("\n")
    def pipes(s): return s.replace("\\|","").count("|")
    i=0;t=0;b=0;r=0
    while i < len(lines):
        if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
            h=pipes(lines[i]); j=i
            while j < len(lines) and lines[j].startswith("|"):
                r+=1
                if pipes(lines[j])!=h: b+=1; print("  MISMATCH", f, "line", j+1)
                j+=1
            t+=1; i=j
        else: i+=1
    print("%-58s tables=%d rows=%d bad=%d | %dB CRLF=%d" % (pathlib.Path(f).name, t, r, b, len(raw), raw.count(b"\r\n")))
