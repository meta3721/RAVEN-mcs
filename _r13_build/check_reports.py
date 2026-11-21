import pathlib
import re

for name in ("raven-mcs-tmc-review.md", "raven-mcs-integrity-audit.md"):
    p = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build") / name
    txt = p.read_text(encoding="utf-8")
    lines = txt.splitlines()
    print(f"=== {name}: {len(lines)} lines, {len(txt.encode('utf-8'))} bytes ===")

    # placeholder scan
    bad = []
    for i, ln in enumerate(lines, 1):
        if re.search(r"\b(TBD|TODO|FIXME|\[fill\]|XXX)\b", ln):
            bad.append((i, ln.strip()[:80]))
    print(f"  placeholders: {len(bad)}")
    for b in bad:
        print("    ", b)

    # table consistency: consecutive lines starting with |
    blocks = []
    cur = []
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("|"):
            cur.append((i, ln))
        else:
            if cur:
                blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    print(f"  table blocks: {len(blocks)}")
    problems = 0
    for blk in blocks:
        counts = {ln.count("|") for _, ln in blk}
        if len(counts) != 1:
            problems += 1
            print(f"    INCONSISTENT block starting line {blk[0][0]}: pipe counts {sorted(counts)}")
            for i, ln in blk[:6]:
                print(f"      {i}: {ln.count('|')} pipes :: {ln.strip()[:70]}")
    print(f"  inconsistent table blocks: {problems}")

    # unclosed code fences
    fences = sum(1 for ln in lines if ln.strip().startswith("```"))
    print(f"  code fences: {fences} ({'balanced' if fences % 2 == 0 else 'UNBALANCED'})")
    print()
