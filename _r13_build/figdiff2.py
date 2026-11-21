import csv, hashlib, itertools
from pathlib import Path

W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\figdiff2.txt")
L = []
def w(s=""): L.append(s)

def sha(p):
    h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()

PAIRS = [
 ("figures/FIG_W1_DESIGN_GATE.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_W1_DESIGN_GATE.csv"),
 ("figures/FIG_E4_E4_COMPONENT_ABLATION.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv"),
 ("figures/FIG_E3_E3_PREDICTION_RISK.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv"),
]

def uniq_key(hdr, rows, maxk=4):
    for k in range(1, maxk + 1):
        for combo in itertools.combinations(range(len(hdr)), k):
            keys = [tuple(r[i] for i in combo) for r in rows]
            if len(set(keys)) == len(rows):
                return combo
    return None

for brel, wrel in PAIRS:
    bp, wp = B / brel, W / wrel
    w("=" * 100)
    w(f"PAIR {brel}  vs  {wrel}")
    w(f"  bundle   sha256 {sha(bp)}  ({bp.stat().st_size} B)")
    w(f"  worktree sha256 {sha(wp)}  ({wp.stat().st_size} B)")
    br = list(csv.reader(open(bp, encoding="utf-8-sig", newline="")))
    wr = list(csv.reader(open(wp, encoding="utf-8-sig", newline="")))
    hdr = br[0]
    w(f"  header identical: {hdr == wr[0]}")
    brow, wrow = br[1:], wr[1:]
    w(f"  rows: bundle={len(brow)} worktree={len(wrow)}")
    kc = uniq_key(hdr, brow) if len(brow) == len(wrow) else None
    if kc is None:
        w("  !! could not find a unique key (or row counts differ); falling back to multiset compare")
        bs, ws_ = sorted(map(tuple, brow)), sorted(map(tuple, wrow))
        w(f"  row multisets identical: {bs == ws_}")
        onlyb = [r for r in bs if r not in ws_]
        onlyw = [r for r in ws_ if r not in bs]
        w(f"  rows only in bundle: {len(onlyb)}; only in worktree: {len(onlyw)}")
        for r in onlyb[:10]: w("    B " + " | ".join(r))
        for r in onlyw[:10]: w("    W " + " | ".join(r))
        continue
    w(f"  unique key columns: {[hdr[i] for i in kc]}")
    bd = {tuple(r[i] for i in kc): r for r in brow}
    wd = {tuple(r[i] for i in kc): r for r in wrow}
    w(f"  keys only in bundle: {len(set(bd)-set(wd))}  {sorted(set(bd)-set(wd))[:5]}")
    w(f"  keys only in worktree: {len(set(wd)-set(bd))}  {sorted(set(wd)-set(bd))[:5]}")
    common = sorted(set(bd) & set(wd))
    diffs = [k for k in common if bd[k] != wd[k]]
    w(f"  common keys: {len(common)}   DIFFERING ROWS: {len(diffs)}  ({100.0*len(diffs)/max(1,len(common)):.1f}%)")
    colstat = {}
    for k in diffs:
        b, x = bd[k], wd[k]
        for i, c in enumerate(hdr):
            if b[i] != x[i]:
                colstat.setdefault(c, []).append((k, b[i], x[i]))
    for c, lst in colstat.items():
        w(f"    column '{c}': {len(lst)} differing cells")
        nums = []
        for k, bv, xv in lst:
            try: nums.append((abs(float(bv) - float(xv)), k, bv, xv))
            except ValueError: pass
        if nums:
            nums.sort()
            w(f"      min abs diff = {nums[0][0]!r} at {nums[0][1]}")
            w(f"      max abs diff = {nums[-1][0]!r} at {nums[-1][1]}")
        for k, bv, xv in lst[:8]:
            w(f"        key={k}  bundle={bv!r}  worktree={xv!r}")
    # also flag reordering / any non-key column that never differs
    samecols = [hdr[i] for i in range(len(hdr)) if i not in kc and hdr[i] not in colstat]
    w(f"  non-key columns with NO differences: {samecols}")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L), "lines")
