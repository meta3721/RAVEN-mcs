"""R1.3 adversarial audit - the freeze chain.

The driver froze S1P_FROZEN_CONFIG.json four times (hashes fe84a4c6, 57b4bcec,
f56f224c, a041ba42).  Reconstruct which eta_s_star each freeze selected, from the
driver's own stdout logs, and check whether the SS/UA selection changed after the
test split had already been opened for them.
ASCII only.
"""
import re, pathlib, json

D = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver")
PAT_FREEZE = re.compile(r"froze S1P_FROZEN_CONFIG\.json sha256=([0-9a-f]{64})")
PAT_ROW = re.compile(r"^\s*A\s+(sensorscope|uair|traffic)\s+eta=(\S+)\s+seed(\d+)\s+val=(\S+)\s+(.*)$")
PAT_N3 = re.compile(r"^\s*N3' (sensorscope|uair|traffic)\s+(\S+)\s+ratio_to_c=(\S+)")

logs = sorted(D.glob("*.log"))
events = []
for lg in logs:
    try:
        txt = lg.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    for i, line in enumerate(txt.splitlines(), 1):
        m = PAT_FREEZE.search(line)
        if m:
            events.append((lg.name, i, "FREEZE", m.group(1)))
        m = PAT_ROW.match(line)
        if m:
            events.append((lg.name, i, "CELL", "%s eta=%s seed%s val=%s %s"
                           % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))))
        m = PAT_N3.match(line)
        if m:
            events.append((lg.name, i, "N3", "%s %s ratio=%s" % (m.group(1), m.group(2), m.group(3))))

print("### per-log: freeze events, last cell before each freeze, N3 verdicts")
for lg in logs:
    sub = [e for e in events if e[0] == lg.name]
    if not sub:
        continue
    fr = [e for e in sub if e[2] == "FREEZE"]
    print("--- %s  (%d recorded lines of interest)" % (lg.name, len(sub)))
    for j, e in enumerate(fr):
        lo = fr[j - 1][1] if j else 0
        prior = [x for x in sub if x[2] == "CELL" and lo < x[1] < e[1]]
        blocks = {}
        for x in prior:
            blocks.setdefault(x[3].split()[0], []).append(x[3])
        print("    FREEZE %s at line %d   cells since previous freeze: %s"
              % (e[3][:16], e[1], {k: len(v) for k, v in blocks.items()} or "none"))
    n3 = [x for x in sub if x[2] == "N3"]
    for x in n3:
        print("    N3 %s" % x[3])

print()
print("### the freeze chain in order across logs (by hash)")
for e in events:
    if e[2] == "FREEZE":
        print("   %s:%d  %s" % (e[0], e[1], e[3]))

print()
print("### what the current config says, and the superseded hash the report names")
cfg = json.loads((D.parent / "S1P_FROZEN_CONFIG.json").read_text())
for b, v in cfg["per_block"].items():
    print("   %-11s eta_s_star=%s" % (b, v["eta_s_star"]))
print("   report names 57b4bcec0cb030cf... as the superseded first config")
