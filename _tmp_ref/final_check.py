import pathlib, re
files = ("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md",
         "ccfa-review-reports/raven-mcs-tmc-review.md",
         "results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md")
for f in files:
    raw = pathlib.Path(f).read_bytes(); lines = raw.decode("utf-8").split("\n")
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
    print("%-46s tables=%-3d rows=%-4d bad=%d  CRLF=%d  %dB" % (pathlib.Path(f).name, t, r, b, raw.count(b"\r\n"), len(raw)))
    for k in ("Inst` ablation row contradicts", "duplicate arms", "duplicate-arm",
              "the effective levers", "half-applied"):
        if k in raw.decode("utf-8"): print(f"     residual stale phrase: {k!r}")
