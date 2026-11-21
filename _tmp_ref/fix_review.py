import pathlib
p = pathlib.Path("ccfa-review-reports/raven-mcs-tmc-review.md")
L = p.read_text(encoding="utf-8").replace("\r\n","\n").split("\n")
log=[]

# 1) replace the M8 + M9 block
s = next(i for i,l in enumerate(L) if l.startswith("### M8"))
e = next(i for i in range(s+1, len(L)) if L[i].startswith("### Minor, this round"))
new = """### M8 — A simpler baseline matches the structural endpoints, and no component explains it. **Major. Newly revealed by evidence.**

On the licensed set, Debt-Cal ties RAVEN-NoDesign on both structural endpoints:

| metric | RAVEN-NoDesign | Debt-Cal | paired relative (TEST / ALL20) | Holm p |
|:---|:---|:---|:---|:---|
| `Delta_group` | 1.0165 | 1.0175 | -0.052 % / -0.089 % | 0.71 / 0.41 |
| `Delta_c-s` | 1.2949 | 1.2948 | -0.055 % / +0.015 % | 0.67 / 0.90 |
| `RMSE_mu` | 1.1131 | 1.1144 | -0.124 % / -0.115 % | n.s. |

Debt-Cal carries instant group calibration, debt and a reference penalty; it has no observation IPW, no
usable-update IPW and no Hajek local loss, and its reference term is set to `lambda_beta = 1e-8`.

**The mechanism sentence in the first version of this concern is withdrawn.** It read the manuscript's
ablation family as saying that removing instant calibration moves `Delta_group` from `1.0924` to
`1.1196`, and concluded that the P2 group-calibration term carries the U-Air structure. The `1.1196` came
from the E4 tree arm `raven_wo_inst`, which `E4_WO_INST_FINAL_DECISION.json` had already declared
**invalid** on 2026-08-12 (`proven_invalid: true`, 40 corrective reruns authorised) because it skipped P2
entirely. With P2 preserved, the corrected ablation moves `Delta_group` by `-0.089 %` on U-Air and
`-0.260 %` on SensorScope when instant calibration is removed, and by at most `0.26 %` for any other
single component, against `-6.943 %` for the Design factor.

The honest form of the concern is therefore stronger in one way and weaker in another. The **observation**
stands: a simpler method ties RAVEN-NoDesign on both structural endpoints, and the manuscript now says
so. The **attribution** does not: the paper's own ablation family attributes the U-Air `Delta_group`
structure to the Design factor alone, and no component explains why Debt-Cal reaches the same endpoint
without the correction family. *Diminishes* dims 3 and 6.

*Repair condition:* state in SSV that the U-Air structural effect is carried by the Design factor and that
the ablation family does not separate Debt-Cal's route to the same endpoint; or add the controlled
`design off x instant calibration off` arm, which first needs the unfinished call site recorded in the
verification report's SS0.2 to be covered.

### M9 — WITHDRAWN

The first version of this concern claimed that `tab:app_e3_uair` presents duplicate arms, on the strength
of two bitwise identities: `raven_wo_inst` (E4) equals `twostage_hajek` (E3), and `inst_cal` (E3) equals
`raven_wo_debt` (E4). **The concern is withdrawn.**

`raven_wo_inst` is not a row of that table, and the E4 directory of that name is the arm invalidated on
2026-08-12. It coincides with TwoStage-Hajek because both take the pre-repair `alpha = beta` branch of
`window_runner`, not because the paper presents one method twice. The second identity creates no
duplicate row either: `inst_cal` is a table row and `raven_wo_debt` is not, and their coincidence means
only that the Hajek local loss is numerically inert on U-Air. No manuscript table needs a duplicate-arm
marking, and dim 7's repair condition for this concern is removed below.
"""
L[s:e] = new.split("\n"); log.append(f"M8+M9 replaced: lines {s+1}-{e} -> {len(new.splitlines())} lines")

# 2) dim-7 scorecard row
for i,l in enumerate(L):
    if l.startswith("| 7 | Related work / positioning |"):
        L[i] = ("| 7 | Related work / positioning | 0.05 | 3 | medium | positioning against "
                "non-random-selection and MCS-sampling work is reasonable | no repair condition "
                "outstanding from this round |")
        log.append(f"dim-7 row patched @{i+1}"); break

# 3) action-table rows
for i,l in enumerate(L):
    if l.startswith("| `M8` simpler baseline"):
        L[i] = ("| `M8` simpler baseline matches the structure | **major** | 3, 6 | writing, or the 2x2 arm | "
                "`ccf-paper-writer`, `ccf-experiment-designer` | holds 3 at 2 until addressed |")
        log.append(f"M8 action row patched @{i+1}")
    if l.startswith("| `M9` duplicate arms"):
        L[i] = "| ~~`M9` duplicate arms in the family table~~ **withdrawn 2026-09-27** | — | — | — | — | no effect |"
        log.append(f"M9 action row patched @{i+1}")

# 4) erratum note in the header
for i,l in enumerate(L):
    if l.startswith("Snapshot of the prior canonical report:"):
        L[i:i] = ["",
                  "**Erratum 2026-09-27.** Concern `M9` is **withdrawn** and concern `M8`'s mechanism",
                  "attribution is **withdrawn**; `M8`'s observation stands. Both rested on the E4 tree arm",
                  "`raven_wo_inst`, which `artifacts/e4_ablation_semantic_integrity_repair_r1/E4_WO_INST_FINAL_DECISION.json`",
                  "had already declared invalid on 2026-08-12. `M7` is unaffected. Details in SS5."]
        log.append(f"erratum note inserted after line {i+1}"); break

p.write_bytes("\n".join(L).encode("utf-8"))
raw = p.read_bytes()
print("\n".join(log))
print("review: %d lines, CRLF=%d, %dB" % (len(L), raw.count(b"\r\n"), len(raw)))
