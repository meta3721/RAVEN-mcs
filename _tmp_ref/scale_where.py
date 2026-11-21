import csv, pathlib, json, re
ROOT = pathlib.Path(".")
# 1) the immediate upstream of the sealed source
for cand in ROOT.glob("**/E3_FINAL_STATISTICS.csv"):
    try: rows = list(csv.DictReader(open(cand, newline="", encoding="utf-8")))
    except Exception as e: print("ERR", cand, e); continue
    hits = [r for r in rows if r.get("dataset","").lower().replace("-","")in ("uair","u-air") and "fedavg" in r.get("method","").lower()]
    print(f"--- {cand.relative_to(ROOT)}  ({len(rows)} rows, cols={list(rows[0].keys())[:8]})")
    for r in hits[:4]:
        vals = {k:v for k,v in r.items() if re.search(r"rmse|tail|delta", k, re.I)}
        print("    ", vals)
