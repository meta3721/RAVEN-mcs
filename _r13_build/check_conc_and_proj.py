import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")

print("=" * 78)
print("CLAIM G: largest group share 0.53% (SS, 220 groups) / 0.79% (UA, 144 groups)")
print("=" * 78)

cands = sorted((ROOT / "artifacts").glob("e3_*closure_r1/E3_*TARGET_SEMANTICS_R2.json"))
for p in cands:
    j = json.loads(p.read_text(encoding="utf-8"))
    raw = j.get("mu")
    if isinstance(raw, dict):
        mu = [float(v) for v in raw.values()]
    elif isinstance(raw, list):
        mu = [float(v) for v in raw]
    else:
        print(f"  {p.name}: mu type = {type(raw).__name__}")
        continue
    print(f"  {p.name}")
    print(f"     dataset         = {j.get('dataset')}")
    print(f"     n_groups (field)= {j.get('n_groups')}")
    print(f"     len(mu)         = {len(mu)}")
    print(f"     max(mu)         = {max(mu):.10f}  -> {100*max(mu):.4f} %")
    print(f"     min(mu)         = {min(mu):.10f}")
    print(f"     sum(mu)         = {sum(mu):.15f}")
    print(f"     mu_sum (field)  = {j.get('mu_sum')}")
    print(f"     n(mu>0)         = {sum(1 for x in mu if x > 0)}")
    print()

print("=" * 78)
print("CLAIM H: projection over uniform server weights  +0.768 / +0.286 pp")
print("=" * 78)
targets = [
    ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/PART_A_REPORT.md",
    ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/PART_B_REPORT.md",
    ROOT / "results_h_headroom/round_v3",
]
for t in targets:
    if t.is_file():
        txt = t.read_text(encoding="utf-8", errors="replace")
        hits = [ln.strip() for ln in txt.splitlines() if "0.768" in ln or "0.286" in ln]
        print(f"  {t.relative_to(ROOT)}: {len(hits)} line(s) mentioning 0.768 / 0.286")
        for h in hits[:6]:
            print(f"     > {h[:200]}")
    elif t.is_dir():
        found = 0
        for f in t.rglob("*"):
            if f.is_file() and f.suffix.lower() in {".md", ".csv", ".json", ".txt"}:
                try:
                    txt = f.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if "0.768" in txt:
                    print(f"  {f.relative_to(ROOT)}: mentions 0.768")
                    found += 1
                    if found >= 8:
                        break
        if not found:
            print(f"  {t.relative_to(ROOT)}: no file mentions 0.768")
print()
print("=" * 78)
print("where does the bundle README say the pair lives?")
print("=" * 78)
rd = (ROOT / "RAVEN_MCS_PUBLIC_REPRO_R1/README.md").read_text(encoding="utf-8")
for ln in rd.splitlines():
    if "0.768" in ln or "0.286" in ln:
        print("  " + ln.strip())
