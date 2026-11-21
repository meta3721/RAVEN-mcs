import json,pathlib,collections
RUNS=pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\runs")
c=collections.Counter()
for p in RUNS.rglob("ledger.jsonl"):
    for l in p.read_text().splitlines():
        r=json.loads(l)
        if r.get("event")=="START":
            c[(r.get("runner_source_hash"),r.get("method_source_hash"),r.get("source_manifest_hash"),r.get("dataset_hash"))]+=1
for k,v in c.items(): print(" ",k,v)
