import pathlib, json, collections
ROOT = pathlib.Path(".")
base = ROOT/"artifacts/e3_formal_runs_r1/runs/uair"
tot = 0
for d in sorted(base.iterdir()):
    if not d.is_dir(): continue
    seeds = sorted(int(p.name.replace("seed","")) for p in d.glob("seed*") if (p/"window_metrics.json").is_file())
    tot += len(seeds)
    print(f"  {d.name:<28} runs={len(seeds):<3} seeds={seeds[0] if seeds else '-'}..{seeds[-1] if seeds else '-'}")
print("TOTAL runs with window_metrics:", tot)
