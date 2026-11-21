import json, pathlib, collections
ROOT = pathlib.Path(".")
for base in ["artifacts/e3_formal_runs_r1/runs", "artifacts/e3_fedau_window_r1", "artifacts/e3_obsuse_window_r1", "artifacts/e4_core_mechanism_ablation_r1"]:
    b = ROOT/base
    if not b.exists(): print(base, "MISSING"); continue
    n_runs = len(list(b.rglob("window_metrics.json")))
    lens = collections.Counter()
    for p in b.rglob("window_metrics.json"):
        try: lens[len(json.loads(p.read_text(encoding="utf-8")))] += 1
        except Exception: lens["ERR"] += 1
    print(f"{base:<48} runs={n_runs:<4} windows-per-run={dict(lens)}")
    print("    top dirs:", sorted({p.relative_to(b).parts[0] for p in b.rglob('window_metrics.json')})[:14])
