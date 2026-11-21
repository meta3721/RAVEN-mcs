import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")

TARGETS = [
    ("SensorScope Design ON ", ROOT / "artifacts/e3_formal_runs_r1/runs/sensorscope/raven"),
    ("U-Air       Design ON ", ROOT / "artifacts/e3_formal_runs_r1/runs/uair/raven"),
    ("U-Air       Design OFF", ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs/uair/raven_wo_design"),
    ("SensorScope Design OFF", ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs/sensorscope/raven_wo_design"),
]

print(f"{'arm':<24}{'seeds':>6}{'active':>8}{'<=3':>8}{'share<=3':>10}{'<=2':>8}{'==1':>7}{'==2':>7}{'==3':>7}{'max':>6}")
print("-" * 98)

for label, d in TARGETS:
    seeds = sorted([p for p in d.iterdir() if p.is_dir()])
    total = 0
    le3 = 0
    le2 = 0
    counts = Counter()
    mx = 0
    nseeds = 0
    for s in seeds:
        wm = s / "window_metrics.json"
        if not wm.is_file():
            continue
        nseeds += 1
        rows = json.loads(wm.read_text(encoding="utf-8"))
        for r in rows:
            if not r.get("active"):
                continue
            k = r.get("a_r_size")
            if k is None:
                k = len(r.get("active_clients") or [])
            total += 1
            counts[k] += 1
            mx = max(mx, k)
            if k <= 3:
                le3 += 1
            if k <= 2:
                le2 += 1
    share = 100.0 * le3 / total if total else float("nan")
    print(f"{label:<24}{nseeds:>6}{total:>8}{le3:>8}{share:>9.2f}%{le2:>8}{counts[1]:>7}{counts[2]:>7}{counts[3]:>7}{mx:>6}")

print()
print("=== manuscript claims to compare ===")
print("  '78.6% of the 1877 active windows on SensorScope have K_r <= 3'")
print("  '90.2% of 1402 windows with Design on and 79.0% of 1515 with Design off'  (U-Air)")
print()
print("=== exact fractions ===")
for label, d in TARGETS:
    tot = 0
    le3 = 0
    for s in sorted([p for p in d.iterdir() if p.is_dir()]):
        wm = s / "window_metrics.json"
        if not wm.is_file():
            continue
        for r in json.loads(wm.read_text(encoding="utf-8")):
            if r.get("active"):
                tot += 1
                k = r.get("a_r_size") if r.get("a_r_size") is not None else len(r.get("active_clients") or [])
                if k <= 3:
                    le3 += 1
    if tot:
        print(f"  {label}: {le3}/{tot} = {le3/tot:.10f}  -> {100*le3/tot:.4f}%")
