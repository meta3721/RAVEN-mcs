"""TE1 setup: copy the S1' driver into results_traffic_e1/round_v1/driver/ and repoint its output root.
Byte-level copy so line endings are preserved exactly; records the diff."""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
SRC = ROOT / "results_server_optimizer/round_v1/driver/s1p_driver.py"
DSTDIR = ROOT / "results_traffic_e1/round_v1/driver"
DST = DSTDIR / "s1p_driver.py"

DSTDIR.mkdir(parents=True, exist_ok=True)

raw = SRC.read_bytes()
src_sha = hashlib.sha256(raw).hexdigest()

OLD = b'OUT = ROOT / "results_server_optimizer" / "round_v1"'
NEW = b'OUT = ROOT / "results_traffic_e1" / "round_v1"'
assert raw.count(OLD) == 1, f"OUT anchor count {raw.count(OLD)}"
out = raw.replace(OLD, NEW)
DST.write_bytes(out)

print("copied:", SRC.relative_to(ROOT).as_posix(), "->", DST.relative_to(ROOT).as_posix())
print("  source sha256 :", src_sha, len(raw), "B")
print("  copy   sha256 :", hashlib.sha256(out).hexdigest(), len(out), "B")
print("  byte delta    :", len(out) - len(raw), "(path string only)")
print("  CRLF in copy  :", out.count(b"\r\n"), "| LF:", out.count(b"\n"))
print()
print("  the single change:")
print("   -", OLD.decode())
print("   +", NEW.decode())
print()
print("=== inventory of one frozen S1' run directory (what the finiteness scan must cover) ===")
d = ROOT / "results_server_optimizer/round_v1/runs/C_raven_simoracle/traffic/raven_simoracle/seed30001"
for p in sorted(d.rglob("*")):
    if p.is_file():
        print(f"   {p.relative_to(d).as_posix():<46} {p.stat().st_size:>9} B")
