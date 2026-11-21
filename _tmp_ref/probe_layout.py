import pathlib
ROOT = pathlib.Path(".")
for base in ["artifacts/e3_fedau_window_r1/runs","artifacts/e3_obsuse_window_r1/runs","artifacts/e4_core_mechanism_ablation_r1/runs","results_c1_cityscanner/round_v1","results_joint_ou/round_v1","results_nodesign_supplement/round_v1"]:
    b = ROOT/base
    if not b.exists(): print(base, "MISSING"); continue
    runs = sorted({p.parent for p in b.rglob("final_metrics.json")})
    print(f"{base}: {len(runs)} run dirs")
    for r in runs[:8]:
        print("    ", r.relative_to(b))
    if len(runs) > 8: print(f"     ... +{len(runs)-8} more")
