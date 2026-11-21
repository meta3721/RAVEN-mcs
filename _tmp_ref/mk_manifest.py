import hashlib, pathlib
ROOT = pathlib.Path(".").resolve()
OUT = ROOT/"results_active_set_repair/round_v1"
lines = []
for p in sorted(OUT.iterdir()):
    if p.is_file() and p.name != "MANIFEST.sha256":
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
d = ROOT/"scripts/run_active_set_repair.py"
lines.append(f"{hashlib.sha256(d.read_bytes()).hexdigest()}  scripts/run_active_set_repair.py")
(OUT/"MANIFEST.sha256").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
print(f"MANIFEST.sha256: {len(lines)} entries")
for l in lines: print("   ", l[:16], l.split("  ",1)[1])
