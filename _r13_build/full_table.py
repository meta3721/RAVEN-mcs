import csv, hashlib, json, os
from pathlib import Path
from collections import defaultdict

W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\full_table.txt")
L=[]
def w(s=""): L.append(s)

matches = json.loads((W/"_r13_build/matches.json").read_text())

# basename index of worktree (paths only)
byname = defaultdict(list)
for dp, dn, fn in os.walk(W):
    ap = os.path.abspath(dp)
    if any(ap.startswith(e) for e in (str(B), str(W/".venv_new"), str(W/".git"), str(W/"_r13_build"))):
        dn[:] = []; continue
    for n in fn:
        byname[n].append(str(Path(dp)/n))

groups = ["certificate","cityscanner","cityscanner_p2","configs","eventtraces","figures",
          "new_target","processed","scripts","tables","tdrive","w1","(top-level)"]
def grp(rel):
    p = rel.split("/")
    return p[0] if len(p) > 1 else "(top-level)"

summary = {}
for g in groups:
    rels = [r for r in matches if grp(r) == g]
    rels.sort()
    matched = [r for r in rels if matches[r]]
    unmatched = [r for r in rels if not matches[r]]
    summary[g] = (len(rels), len(matched), len(unmatched))
w("GROUPED SUMMARY: files | with >=1 byte-identical worktree twin | with none")
for g in groups:
    a,b,c = summary[g]
    w(f"  {g:<16} {a:>5} {b:>5} {c:>5}")
w(f"  {'TOTAL':<16} {sum(v[0] for v in summary.values()):>5} {sum(v[1] for v in summary.values()):>5} {sum(v[2] for v in summary.values()):>5}")

w("")
w("="*100)
w("BASENAME NEAR-MISS SCAN: bundle files with NO byte-identical twin that DO have same-basename worktree files")
w("="*100)
nm = [r for r in sorted(matches) if not matches[r]]
for r in nm:
    bn = r.split("/")[-1]
    others = byname.get(bn, [])
    w(f"{r}  (bundle sha256 {(B/r).read_bytes() and __import__('hashlib').sha256((B/r).read_bytes()).hexdigest()})")
    if not others:
        w("    -> NO worktree file with this basename at all")
    else:
        for o in others:
            p = Path(o)
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            w(f"    -> {p.relative_to(W).as_posix()}  ({p.stat().st_size} B, sha256 {h})  SAME={'YES' if h==hashlib.sha256((B/r).read_bytes()).hexdigest() else 'NO'}")

w("")
w("="*100)
w("w1/ SOURCE DISTRIBUTION (byte-identical worktree twins)")
w("="*100)
srcs = defaultdict(int); multi = 0
for r in sorted(matches):
    if not r.startswith("w1/"): continue
    m = matches[r]
    if not m:
        srcs["<NONE>"] += 1; continue
    if len(m) > 1: multi += 1
    # take a representative: prefer dirs not under snapshots/deliverables/archive
    prim = None
    for cand in m:
        cp = Path(cand).relative_to(W).as_posix()
        if cp.startswith(("snapshots/","deliverables/","archive/","_tmp","outputs/")): continue
        prim = cp; break
    if prim is None: prim = Path(m[0]).relative_to(W).as_posix()
    srcs[prim.split("/")[0]] += 1
w(f"  w1 files with >1 twin: {multi}")
for k, v in sorted(srcs.items(), key=lambda x: -x[1]):
    w(f"  {k:<40} {v}")
w("")
w("w1 sample rows (path | n_twins | representative):")
cnt = 0
for r in sorted(matches):
    if not r.startswith("w1/"): continue
    m = matches[r]
    prim = ""
    for cand in m:
        cp = Path(cand).relative_to(W).as_posix()
        if cp.startswith(("snapshots/","deliverables/","archive/","_tmp","outputs/")): continue
        prim = cp; break
    if not prim and m: prim = Path(m[0]).relative_to(W).as_posix()
    w(f"  {r} | {len(m)} | {prim or '<NONE>'}")
    cnt += 1
    if cnt >= 25: break
w("  ... (full list of 217 rows omitted here; counts above are exhaustive)")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L))
