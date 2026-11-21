import csv, hashlib, json, os, sys
from pathlib import Path
from collections import defaultdict

B = Path(r"C:\Cursor\raven.mcs\RAVEN_MCS_PUBLIC_REPRO_R1")
W = Path(r"C:\Cursor\raven.mcs")
SCRATCH = Path(r"C:\Cursor\raven.mcs\_r13_build")

EXCL_PREFIX = [str(B), str(W / ".venv_new"), str(W / ".git"), str(SCRATCH), str(W / "_tmp_pack")]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

# ---------- bundle side ----------
bundle = []
for dp, dn, fn in os.walk(B):
    for n in fn:
        p = Path(dp) / n
        bundle.append(p)
bundle.sort()
brec = {}
for p in bundle:
    rel = p.relative_to(B).as_posix()
    brec[rel] = sha(p)
print("bundle files hashed:", len(brec))

# ---------- worktree size index ----------
size_index = defaultdict(list)
nfiles = 0
for dp, dn, fn in os.walk(W):
    ap = os.path.abspath(dp)
    if any(ap.startswith(e) for e in EXCL_PREFIX):
        dn[:] = []
        continue
    for n in fn:
        p = Path(dp) / n
        try:
            st = p.stat()
        except OSError:
            continue
        size_index[st.st_size].append(str(p))
        nfiles += 1
print("worktree files indexed:", nfiles)

# hash cache for worktree candidates
cache = {}
def wsha(path):
    if path not in cache:
        try:
            cache[path] = sha(path)
        except OSError:
            cache[path] = None
    return cache[path]

matches = {}   # bundle rel -> list of worktree paths with identical sha256
for rel, h in brec.items():
    p = B / rel
    sz = p.stat().st_size
    cands = size_index.get(sz, [])
    same = [c for c in cands if wsha(c) == h]
    matches[rel] = same

out = SCRATCH / "matches.json"
out.write_text(json.dumps(matches, indent=1), encoding="utf-8")

nomatch = [r for r, m in matches.items() if not m]
print("bundle files with NO byte-identical worktree file:", len(nomatch))
for r in sorted(nomatch)[:60]:
    print("  NO_MATCH", r)
print("worktree files hashed for comparison:", len(cache))
