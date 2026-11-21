import csv, hashlib
from pathlib import Path

W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\figdiff3.txt")
L = []
def w(s=""): L.append(s)
def sha(p):
    h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()

PAIRS = [
 ("figures/FIG_W1_DESIGN_GATE.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_W1_DESIGN_GATE.csv", ["dataset","variant"]),
 ("figures/FIG_E4_E4_COMPONENT_ABLATION.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv", ["dataset","component","metric"]),
 ("figures/FIG_E3_E3_PREDICTION_RISK.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv", ["dataset","method","seed"]),
]

for brel, wrel, KEY in PAIRS:
    bp, wp = B / brel, W / wrel
    w("=" * 100)
    w(f"PAIR {brel}")
    w(f"  bundle   sha256 {sha(bp)}  {bp.stat().st_size} B")
    w(f"  worktree {wrel}")
    w(f"           sha256 {sha(wp)}  {wp.stat().st_size} B")
    br = list(csv.DictReader(open(bp, encoding="utf-8-sig", newline="")))
    wr = list(csv.DictReader(open(wp, encoding="utf-8-sig", newline="")))
    hdr = list(br[0].keys())
    w(f"  header identical: {hdr == list(wr[0].keys())}")
    w(f"  rows: bundle={len(br)} worktree={len(wr)}")
    w(f"  key: {KEY}")
    bd = {tuple(r[k] for k in KEY): r for r in br}
    wd = {tuple(r[k] for k in KEY): r for r in wr}
    w(f"  duplicate keys: bundle={len(br)-len(bd)} worktree={len(wr)-len(wd)}")
    onlyb, onlyw = sorted(set(bd)-set(wd)), sorted(set(wd)-set(bd))
    w(f"  keys only in bundle ({len(onlyb)}): {onlyb[:8]}")
    w(f"  keys only in worktree ({len(onlyw)}): {onlyw[:8]}")
    common = sorted(set(bd) & set(wd))
    diffs = [k for k in common if bd[k] != wd[k]]
    w(f"  common keys: {len(common)}   DIFFERING ROWS: {len(diffs)} ({100.0*len(diffs)/max(1,len(common)):.1f}%)")
    colstat = {}
    for k in diffs:
        for c in hdr:
            if bd[k][c] != wd[k][c]:
                colstat.setdefault(c, []).append((k, bd[k][c], wd[k][c]))
    for c in hdr:
        if c in KEY: continue
        if c not in colstat:
            w(f"    column '{c}': identical in all {len(common)} common rows")
            continue
        lst = colstat[c]
        w(f"    column '{c}': {len(lst)} differing cells")
        nums = []
        for k, bv, xv in lst:
            try: nums.append((abs(float(bv)-float(xv)), k, bv, xv))
            except ValueError: pass
        if nums:
            nums.sort()
            w(f"      min|diff| = {nums[0][0]!r}  (key {nums[0][1]})")
            w(f"      max|diff| = {nums[-1][0]!r}  (key {nums[-1][1]})")
        else:
            w("      (non-numeric column)")
        for k, bv, xv in lst[:10]:
            w(f"        {k}: bundle={bv!r} worktree={xv!r}")
        if len(lst) > 10:
            w(f"        ... {len(lst)-10} more")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L), "lines")
