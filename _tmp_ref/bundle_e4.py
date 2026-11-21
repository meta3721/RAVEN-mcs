import csv
for f in ("E4_ABLATION_RELATIVE_CHANGE.csv","E4_ABLATION_HOLM_RESULTS.csv","E4_COMPONENT_EFFECTS.csv","TABLE_E4_CORE_ABLATION.csv"):
    p = "RAVEN_MCS_PUBLIC_REPRO_R1/tables/"+f
    try: rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    except Exception as e: print(f"  {f}: {e}"); continue
    print(f"  {f:<38} rows={len(rows):<5} cols={list(rows[0].keys())}")
