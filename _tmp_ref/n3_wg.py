import pathlib, csv
ROOT = pathlib.Path(".")
repro = [r for r in csv.DictReader(open(ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv", newline="", encoding="utf-8")) if r["dataset"]=="uair"]
def m(mth,k="WorstGroupRMSE"): return {int(r["seed"]): float(r[k]) for r in repro if r["method"]==mth}
TEST=set(range(30011,30021))
nd=m("raven_wo_design")
print("WorstGroupRMSE, TEST10 paired relative vs:")
for ref in ("fedavg_window","twostage_hajek","fedau_window","obsuse_window"):
    b=m(ref); ks=sorted(s for s in nd if s in b and s in TEST)
    print(f"   NoDesign vs {ref:<16} : {sum((nd[s]-b[s])/b[s] for s in ks)/len(ks)*100:+.3f}%   (ALL20: {sum((nd[s]-b[s])/b[s] for s in nd)/len(nd)*100:+.3f}%)")
print("\nWorstGroupRMSE means (ALL20 / TEST10):")
for ref in ("fedavg_window","twostage_hajek","fedau_window","obsuse_window","raven_wo_design","raven"):
    b=m(ref); ks=sorted(s for s in b if s in TEST)
    print(f"   {ref:<16} ALL20={sum(b.values())/len(b):.6f}  TEST10={sum(b[s] for s in ks)/len(ks):.6f}")
