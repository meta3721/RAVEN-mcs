import json, pathlib
for p in ("results_c1_cityscanner/round_v1/CS_TRAIN_LEDGER.json", "results_joint_ou/round_v1/JO_TRAIN_LEDGER.json"):
    q = pathlib.Path(p)
    d = json.loads(q.read_text(encoding="utf-8"))
    print("---", p, "| type", type(d).__name__)
    if isinstance(d, dict):
        print("   keys:", list(d.keys())[:10])
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print(f"   {k}: list of {len(v)}, fields={list(v[0].keys())[:14]}")
                print("   first:", json.dumps(v[0])[:300]); break
    elif isinstance(d, list):
        print("   list of", len(d), "fields:", list(d[0].keys())[:14] if d else None)
        print("   first:", json.dumps(d[0])[:300] if d else None)
