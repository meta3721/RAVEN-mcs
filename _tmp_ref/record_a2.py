import pathlib
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
L = p.read_text(encoding="utf-8").replace("\r\n","\n").split("\n")
log = []

# 1) close the two ceiling rows and the F-1 row in the open-defects table
for pat in ("recoverable-gain ceiling is nowhere stated", "**the F-1 result is in no manuscript**"):
    hits = [i for i,l in enumerate(L) if l.startswith("|") and pat in l]
    for i in reversed(hits):
        del L[i]; log.append(f"deleted open-defect row @{i+1}: {pat[:44]}")
    if not hits: log.append(f"NOT FOUND: {pat[:50]}")

# 2) new open-defect row for the Inst contradiction, inserted right after the table header
hdr = next(i for i,l in enumerate(L) if l.startswith("| item | where | note |"))
newrow = ("| **the U-Air `Inst` ablation row contradicts the E4 arm it names** | Table IV "
          "(`tab:e4_ablation`); `E4_ABLATION_RELATIVE_CHANGE.csv`; "
          "`artifacts/e4_core_mechanism_ablation_r1/runs/uair/raven_wo_inst` | The bundle CSV's "
          "`full_RAVEN` mean equals the E3 tree's `raven` exactly (`1.092362`), but its RAVEN-w/o-Inst "
          "ablation mean is `1.091385` while the tree's `raven_wo_inst` is `1.119606`. Published row "
          "`-0.089 %`; tree `+2.494 %`. Same-named arm, different run. Bears on M8's mechanism "
          "attribution, and if the tree is authoritative the published row is wrong |")
L.insert(hdr+1, newrow); log.append(f"inserted new open-defect row @{hdr+2}")

# 3) close §8 action 3
for i,l in enumerate(L):
    if l.startswith("3. **Add the ceiling to the paper**"):
        L[i] = ("3. ~~**Add the ceiling to the paper**~~ **done 2026-09-27**: §VII-F "
                "\"Recoverable-Gain Ceiling\" states the frozen GO rule, the negative result on both "
                "blocks, the U-Air MDE caveat, and the F-1 hardening test. Closes review M2/M5.")
        log.append(f"closed §8 action 3 @{i+1}"); break
else: log.append("NOT FOUND: §8 action 3")

# 4) changelog item 33
anchor = "### Open manuscript defects NOT changed"
block = """| 33 | **New §VII-F "Recoverable-Gain Ceiling".** States the headroom definition $H$, the pre-registered $0.5\\%$ GO rule, that it did not fire on either block, the SensorScope MDE of $0.17$--$0.36$ points, the U-Air $20$-seed re-run with $|H|\\le0.217\\%$ and its $0.70$--$0.80$ point MDE caveat, and the F-1 hardening result ($15$--$21\\times$, $0.104\\%$ / $0.251\\%$, H-A refuted). Closes review M2/M5 and the open-defect rows for the ceiling and the F-1 result. 220 words; main stays **16 pages** | `main.tex` §VII-F |

"""
i = L.index(anchor)
L[i:i] = block.split("\n")
log.append(f"changelog item 33 inserted before line {i+1}")

p.write_bytes("\n".join(L).encode("utf-8"))
raw = p.read_bytes()
print("\n".join(log))
print("record: %d lines, CRLF=%d, size=%dB" % (len(L), raw.count(b"\r\n"), len(raw)))
