import csv, hashlib, os, json
from pathlib import Path
from collections import defaultdict

W = Path(r"C:\Cursor\raven.mcs")
B = Path(r"C:\Cursor\raven.mcs\RAVEN_MCS_PUBLIC_REPRO_R1")
EXCL = [str(B), str(W/".venv_new"), str(W/".git"), str(W/"_r13_build")]

def sha(p):
    h = hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return h.hexdigest()

NAMES = [
 "FIG_E3_E3_PREDICTION_RISK.csv","FIG_E4_E4_COMPONENT_ABLATION.csv","FIG_W1_DESIGN_GATE.csv",
 "E4_ABLATION_RELATIVE_CHANGE.csv","TABLE_E3_MAIN_EFFECTIVENESS.csv",
 "TABLE_II_MAIN_EFFECTIVENESS.csv","EXCLUDED_HASHES.csv","PAPER_NUMBERS.csv",
 "MANIFEST_ADDITIONS.csv","SCD_PHI_DECISION.json","JO_PHI.csv","design_rule.json","seeds.json",
 "E3_SCD_WORSTGROUP_SLICE_REL.csv","E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv",
 "CERTIFICATE_PROTOCOL.json","rebuild_e3_scd_holm_fedau_obsuse.py","rebuild_table_ii_tolerance.py",
]
want = set(NAMES)
found = defaultdict(list)
for dp, dn, fn in os.walk(W):
    ap = os.path.abspath(dp)
    if any(ap.startswith(e) for e in EXCL):
        dn[:] = []; continue
    for n in fn:
        if n in want:
            found[n].append(Path(dp)/n)

res = {}
for n in NAMES:
    lst = []
    for p in sorted(found.get(n, [])):
        try: lst.append({"p": p.relative_to(W).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size})
        except OSError: pass
    res[n] = lst
    # bundle versions with this basename
    bset = []
    for dp, dn, fn in os.walk(B):
        for f in fn:
            if f == n:
                bp = Path(dp)/f
                bset.append({"p": bp.relative_to(B).as_posix(), "sha256": sha(bp), "bytes": bp.stat().st_size})
    res[n+"__BUNDLE"] = bset
    print(f"--- {n}: worktree copies={len(lst)} bundle copies={len(bset)}")
    for e in bset: print(f"    BUNDLE {e['sha256'][:16]} {e['bytes']:>9} {e['p']}")
    for e in lst[:25]:
        print(f"    WT     {e['sha256'][:16]} {e['bytes']:>9} {e['p']}")
Path(r"C:\Cursor\raven.mcs\_r13_build\copies.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
