import csv, collections
rows = list(csv.DictReader(open("artifacts/a5_a6_audit/audit_records.csv", encoding="utf-8")))
for ds in ("sensorscope", "uair"):
    sub = [r for r in rows if r["dataset"] == ds]
    seeds = sorted({r["seed"] for r in sub})
    wins = sorted({int(r["window"]) for r in sub})
    cls = sorted({r["client"] for r in sub})
    print(f"{ds}: rows={len(sub)} seeds={len(seeds)} ({seeds[0]}..{seeds[-1]}) "
          f"windows={len(wins)} (min {wins[0]} max {wins[-1]}) clients={len(cls)}")
