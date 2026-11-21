import json,hashlib,pathlib
p=pathlib.Path(r'C:\Cursor\raven.mcs\results_server_optimizer\round_v1\runs\A_eta0.003\traffic\fedavg_window\seed30001\target_wiring.json')
d=json.loads(p.read_text())
print(json.dumps(d['head_tail'],indent=1)[:1500])
for blk in ('sensorscope','uair','traffic'):
    f=pathlib.Path(r'C:\Cursor\raven.mcs\data\processed')/blk/'atomic_units.parquet'
    print(blk, f.is_file(), hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None)
