import csv, difflib, hashlib, os
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\extras.txt")
L=[]
def w(s=""): L.append(s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

# --- eventtraces breakdown + sample ---
w("EVENTTRACES BREAKDOWN")
sub = {}
for dp, dn, fn in os.walk(B/"eventtraces"):
    for n in fn:
        p = Path(dp)/n
        rel = p.relative_to(B/"eventtraces").as_posix()
        key = rel.split("/")[0] if "/" in rel else "(index files)"
        if rel.split("/")[0] in ("e1_formal","e2","e3"):
            parts = rel.split("/")
            key = "/".join(parts[:2]) if len(parts) > 2 else rel.split("/")[0]
        sub.setdefault(key, []).append(rel)
tot = 0
for k in sorted(sub):
    tot += len(sub[k])
    w(f"  {k:<28} {len(sub[k]):>5} files")
w(f"  TOTAL {tot}")
w("")
w("  representative sample (5 per subtree), bundle sha256 vs worktree twin:")
for k in sorted(sub):
    for rel in sorted(sub[k])[:5]:
        full = f"eventtraces/{rel}"
        h = sha(B/full)
        w(f"    {full}  {h}")

# --- build script diff ---
w("")
w("="*100)
w("BUNDLE scripts/build_public_repro_bundle.py  vs  WORKTREE scripts/build_public_repro_bundle.py")
w("="*100)
a = (B/"scripts/build_public_repro_bundle.py").read_text(encoding="utf-8", errors="replace").splitlines()
b = (W/"scripts/build_public_repro_bundle.py").read_text(encoding="utf-8", errors="replace").splitlines()
w(f"  bundle lines={len(a)} bytes={(B/'scripts/build_public_repro_bundle.py').stat().st_size} sha256={sha(B/'scripts/build_public_repro_bundle.py')}")
w(f"  worktree lines={len(b)} bytes={(W/'scripts/build_public_repro_bundle.py').stat().st_size} sha256={sha(W/'scripts/build_public_repro_bundle.py')}")
d = list(difflib.unified_diff(a, b, "bundle", "worktree", lineterm="", n=1))
w(f"  unified diff lines: {len(d)}")
for line in d[:120]:
    w("   " + line.encode("ascii", "replace").decode("ascii"))

# --- TABLE_E3_MAIN_EFFECTIVENESS two versions ---
w("")
w("="*100)
w("TABLE_E3_MAIN_EFFECTIVENESS.csv: bundle/P0 copy vs paper_ready_r2 copy")
w("="*100)
p1 = B/"tables/TABLE_E3_MAIN_EFFECTIVENESS.csv"
p2 = W/"paper_ready_r2/06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv"
w(f"  bundle           {p1.stat().st_size} B {sha(p1)}")
w(f"  paper_ready_r2   {p2.stat().st_size} B {sha(p2)}")
r1 = list(csv.reader(open(p1, encoding="utf-8-sig", newline="")))
r2 = list(csv.reader(open(p2, encoding="utf-8-sig", newline="")))
w(f"  headers: {r1[0]}")
w(f"           {r2[0]}")
d = list(difflib.unified_diff([",".join(x) for x in r1], [",".join(x) for x in r2], "bundle", "paper_ready_r2", lineterm="", n=0))
w(f"  diff lines {len(d)}")
for line in d:
    w("   " + line.encode("ascii","replace").decode("ascii"))
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L))
