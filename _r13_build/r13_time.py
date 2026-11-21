import json, pathlib
RUNS = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\runs")
for blk in ("sensorscope","uair","traffic"):
    for tag in ("A_eta0.001","A_eta0.003","A_eta0.01","C_raven_simoracle","C_raven"):
        d = RUNS/tag/blk/"fedavg_window" if tag.startswith("A") else RUNS/tag/blk/("raven_simoracle" if "simoracle" in tag else "raven")
        for s in (30001,30005):
            p = d/("seed%d"%s)
            if not p.is_dir(): continue
            meta = json.loads((p/"SERVER_OPT_META.json").read_text())["created_utc"] if (p/"SERVER_OPT_META.json").is_file() else "?"
            led = [json.loads(l) for l in (p/"ledger.jsonl").read_text().splitlines()] if (p/"ledger.jsonl").is_file() else []
            st = next((r["timestamp"] for r in led if r.get("event")=="START"), "?")
            fi = next((r["timestamp"] for r in led if r.get("event")=="FINISH"), "?")
            print("%-11s %-16s seed%d  META=%s  LEDGER_start=%s  LEDGER_finish=%s" % (blk,tag,s,meta,st,fi))
