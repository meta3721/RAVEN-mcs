import csv, hashlib, json, os, sys
from pathlib import Path

B = Path(r"C:\Cursor\raven.mcs\RAVEN_MCS_PUBLIC_REPRO_R1")
W = Path(r"C:\Cursor\raven.mcs")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

# ---- manifest ----
with open(B / "MANIFEST.csv", encoding="utf-8", newline="") as f:
    rdr = csv.reader(f)
    hdr = next(rdr)
    rows = list(rdr)
print("MANIFEST header:", hdr)
print("MANIFEST data rows:", len(rows))
print("MANIFEST columns count:", len(hdr))

mrows = []
for r in rows:
    mrows.append({"path": r[0], "bytes": r[1], "sha256": r[2]})
mkeys = [r["path"].replace("\\", "/") for r in mrows]
print("dup manifest paths:", len(mkeys) - len(set(mkeys)))

# ---- actual files ----
actual = []
for dp, dn, fn in os.walk(B):
    for n in fn:
        p = Path(dp) / n
        actual.append(str(p.relative_to(B)).replace("\\", "/"))
actual.sort()
print("actual bundle files:", len(actual))

mset = set(mkeys)
aset = set(actual)
print("in manifest not on disk:", sorted(mset - aset))
print("on disk not in manifest:", sorted(aset - mset))

# ---- summary json ----
s = json.loads((B / "BUNDLE_SUMMARY.json").read_text(encoding="utf-8"))
print("BUNDLE_SUMMARY file_count:", s["file_count"])
print("BUNDLE_SUMMARY total_bytes:", s["total_bytes"])
tot = sum((B / a).stat().st_size for a in actual)
print("actual total bytes:", tot)

# ---- hash agreement bundle vs manifest ----
bad = 0
for r in mrows:
    p = B / r["path"]
    if not p.is_file():
        print("MANIFEST_MISSING_ON_DISK", r["path"]); bad += 1; continue
    if sha(p) != r["sha256"]:
        print("MANIFEST_HASH_MISMATCH", r["path"]); bad += 1
    if p.stat().st_size != int(r["bytes"]):
        print("MANIFEST_BYTES_MISMATCH", r["path"]); bad += 1
print("manifest self-consistency bad:", bad)
