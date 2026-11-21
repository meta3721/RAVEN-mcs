import pathlib
lines = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md").read_text(encoding="utf-8").split("\n")
for n in (1008, 1009, 1017):
    L = lines[n-1]
    print("line %d | pipes=%d | len=%d" % (n, L.count("|"), len(L)))
    print("   repr:", repr(L[:260]))
