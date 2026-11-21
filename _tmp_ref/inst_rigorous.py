import csv, json, pathlib, statistics as st
E3 = pathlib.Path("artifacts/e3_formal_runs_r1/runs/uair")
E4 = pathlib.Path("artifacts/e4_core_mechanism_ablation_r1/runs/uair")
S = list(range(30001, 30021))
def vec(d, k): return [json.loads((d/f"seed{s}"/"final_metrics.json").read_text(encoding="utf-8"))[k] for s in S]

rows = [r for r in csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv", newline="", encoding="utf-8"))
        if r["dataset"]=="U-Air" and r["component"]=="Inst" and r["metric"]=="Delta_group"]
rows.sort(key=lambda r: int(r["seed"]))
csv_ab = [float(r["ablation"]) for r in rows]
csv_rel = [float(r["relative_change_percent"]) for r in rows]

raven = vec(E3/"raven", "Delta_group")
print("=== paper convention: per-seed (ablation - full)/full x 100, then paired mean ===")
print(f"  CSV      : full mean {st.mean(float(r['full_RAVEN']) for r in rows):.6f}  ablation mean {st.mean(csv_ab):.6f}  paired rel {st.mean(csv_rel):+.4f}%   <- matches Table IV line 1955")
for arm in ("raven_wo_inst","raven_wo_obs","raven_wo_use","raven_wo_debt","raven_wo_design","inst_cal","twostage_hajek"):
    d = (E4/arm) if (E4/arm).exists() else (E3/arm)
    if not d.exists(): continue
    try: a = vec(d, "Delta_group")
    except Exception: continue
    rel = [(x-y)/y*100 for x,y in zip(a, raven)]
    print(f"  tree {arm:<20} ablation mean {st.mean(a):.6f}  paired rel {st.mean(rel):+.4f}%   n={len(a)}")
print()
print("=== per-seed: does the CSV's ablation column equal ANY stored U-Air arm? ===")
cands = {}
for d in sorted(set(list(E3.iterdir()) + list(E4.iterdir()))):
    if not d.is_dir(): continue
    try: cands[f"{d.parent.parent.name[:2]}/{d.name}"] = vec(d, "Delta_group")
    except Exception: pass
for name, v in cands.items():
    dd = max(abs(x-y) for x,y in zip(v, csv_ab))
    if dd < 1e-9: print(f"  EXACT match: {name}   (max|diff| = {dd:.1e})")
print("  arms compared:", len(cands))
best = sorted(((max(abs(x-y) for x,y in zip(v, csv_ab)), n) for n,v in cands.items()))[:3]
for dd, n in best: print(f"  closest: {n:<28} max|diff| = {dd:.6f}")
