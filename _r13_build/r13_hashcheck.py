import json,hashlib,pathlib,copy
p=pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\S1P_FROZEN_CONFIG.json")
d=json.loads(p.read_text())
cur=hashlib.sha256(p.read_bytes()).hexdigest()
def h(o): return hashlib.sha256((json.dumps(o,indent=2,sort_keys=True,default=str)+"\n").encode()).hexdigest()
print("current      ",cur)
d2=copy.deepcopy(d); d2["created_utc"]="2026-10-08T08:45:12.000000+00:00"
print("utc-changed  ",h(d2))
d3=copy.deepcopy(d); d3["created_utc"]="2026-10-08T08:56:00.000000+00:00"
print("utc-changed2 ",h(d3))
# explicitly show the selections
print("selections:", {b:v["eta_s_star"] for b,v in d["per_block"].items()})
# N3 verdicts recorded at each freeze, from logs
