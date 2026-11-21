import hashlib, pathlib, subprocess
ROOT = pathlib.Path(".").resolve()
OUT = ROOT/"results_active_set_repair/round_v1"

def runb(*a) -> bytes:
    return subprocess.run(a, cwd=ROOT, capture_output=True).stdout

head = runb("git", "rev-parse", "HEAD").decode("ascii", "replace").strip()
status = runb("git", "status", "--porcelain").decode("utf-8", "replace").splitlines()
lines = [f"# git HEAD at hand-over: {head}",
         "# tracked-modified: sha256 of `git diff -- <path>` bytes;  untracked file: sha256 of file bytes;",
         "# untracked dir: literal UNTRACKED_DIR.  Exists because runtime_manifest.json's git_commit",
         "# does not reflect the working tree (review point SS6c)."]
n = 0
for l in sorted(x for x in status if x.strip()):
    code, path = l[:2].strip(), l[3:].strip().strip('"')
    if not path.startswith("src/"):
        continue
    p = ROOT/path
    if code == "??":
        h = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else \
            hashlib.sha256(b"UNTRACKED_DIR").hexdigest()
    elif p.is_file():
        h = hashlib.sha256(runb("git", "diff", "--", path)).hexdigest()
    else:
        h = hashlib.sha256(b"MISSING").hexdigest()
    lines.append(f"{h}  {code}  {path}")
    n += 1
(OUT/"WORKTREE_DIFF.sha256").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
print(f"WORKTREE_DIFF.sha256: {n} src/ entries, HEAD {head[:12]}")
ml = []
for p in sorted(OUT.iterdir()):
    if p.is_file() and p.name != "MANIFEST.sha256":
        ml.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
d = ROOT/"scripts/run_active_set_repair.py"
ml.append(f"{hashlib.sha256(d.read_bytes()).hexdigest()}  scripts/run_active_set_repair.py")
(OUT/"MANIFEST.sha256").write_bytes(("\n".join(ml) + "\n").encode("utf-8"))
print(f"MANIFEST.sha256: {len(ml)} entries")
