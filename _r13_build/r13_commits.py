import json,pathlib,collections
RUNS=pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\runs")
c=collections.Counter()
first={}
for p in RUNS.rglob("ledger.jsonl"):
    for l in p.read_text().splitlines():
        r=json.loads(l)
        if r.get("event")=="START":
            c[r.get("git_commit")]+=1
            first.setdefault(r.get("git_commit"), str(p.relative_to(RUNS)))
for k,v in c.items():
    print(" commit",k,"n=",v,"example",first[k])
