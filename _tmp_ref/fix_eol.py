import pathlib
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
raw = p.read_bytes()
n_crlf = raw.count(b"\r\n")
txt = raw.decode("utf-8").replace("\r\n", "\n")
p.write_bytes(txt.encode("utf-8"))
raw2 = p.read_bytes()
crlf2 = raw2.count(b"\r\n")
lf2 = raw2.count(b"\n") - crlf2
print("was CRLF=%d  ->  now CRLF=%d  LF-only=%d  size=%dB" % (n_crlf, crlf2, lf2, len(raw2)))
