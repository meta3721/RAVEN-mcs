import hashlib
import pathlib

cur = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean\main.tex")
outdir = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build")
dst = outdir / "main_prev_02447bfe.tex"

data = cur.read_bytes()
lines = data.split(b"\n")
print("current lines      :", len(lines))
print("current bytes      :", len(data))
print("current sha256     :", hashlib.sha256(data).hexdigest().upper())

# hunk3 @@ -2147,0 +2152,17 @@  -> new lines 2152..2168  -> idx 2151..2167
# hunk4 @@ -2176,0 +2198,19 @@  -> new lines 2198..2216  -> idx 2197..2215
block3 = lines[2151:2168]
block4 = lines[2197:2216]
print("block3 (mechanism) :", len(block3), "lines")
print("block4 (limitats)  :", len(block4), "lines")

out = lines[:2151] + lines[2168:2197] + lines[2216:]
newdata = b"\n".join(out)
dst.write_bytes(newdata)

print("rebuilt lines      :", len(out))
print("rebuilt bytes      :", len(newdata))
print("rebuilt sha256     :", hashlib.sha256(newdata).hexdigest().upper())
print("target prefix      : 02447BFE6256632B")
print("MATCH              :", hashlib.sha256(newdata).hexdigest().upper().startswith("02447BFE6256632B"))

for name, blk in (("BLOCK3_mechanism.txt", block3), ("BLOCK4_limitations.txt", block4)):
    p = outdir / name
    p.write_bytes(b"\n".join(blk))
    print("wrote", p)
