import pathlib
p = pathlib.Path("results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md")
L = p.read_text(encoding="utf-8").replace("\r\n","\n").split("\n")
s = next(i for i,l in enumerate(L) if l.startswith("### 4.4"))
e = next(i for i in range(s+1, len(L)) if L[i].startswith("---"))
new = """### 4.4 Why two E4 arms are bitwise identical, and a corrected reading of the ablation

Found this round. Comparing stored trees at full precision:

| arm A | arm B | relationship |
|:---|:---|:---|
| `raven_wo_inst` (E4 tree) | `twostage_hajek` (E3 tree) | **bit-identical per seed** on `RMSE_mu`, `Delta_group`, `Delta_c_s` |
| `inst_cal` (E3 tree) | `raven_wo_debt` (E4 tree) | **bit-identical per seed** (`Delta_c_s` differs by `2.2e-16`) |

**Revision 2 read the first identity as "TwoStage-Hajek *is* RAVEN without instant calibration" and
called the family's arms duplicates. That reading is wrong.** `E4_WO_INST_FINAL_DECISION.json`
(2026-08-12) records `proven_invalid: true` and `authorized_corrective_reruns: 40` for that arm, because
it skipped P2 through the gate described in SS0.2. Every sibling E4 U-Air arm carries a
`p2_invocation_states.json` of 0.87-1.23 MB; `raven_wo_inst` carries **3 bytes, an empty list**.
TwoStage-Hajek takes the same `alpha = beta` branch for its own reasons, since its policy has no
instant-calibration flag either, so the two coincide **through a shared control-flow path, not by being
the same method**. The corrective reruns give `Delta_group` `1.0914` on U-Air, not `1.1196`, and they are
what Table IV reports (SS0.3).

The second identity does carry a finding: `inst_cal` and `raven_wo_debt` differ only in
`uses_hajek_local_loss`, so **the Hajek local loss is numerically inert on U-Air**. `inst_cal` is a row
of `tab:app_e3_uair` while `raven_wo_debt` is not, so this coincidence does not create a duplicate row.

**Corrected statement of the levers.** With P2 preserved, the corrected ablation moves `Delta_group` by
`-0.089 %` on U-Air and `-0.260 %` on SensorScope when instant calibration is removed, and by at most
`0.26 %` for any other single component, against `-6.943 %` for the Design factor on U-Air. On U-Air the
Design factor is the only component that moves `Delta_group` materially, and **instant calibration is
not a lever**. Revision 2's claim that the effective levers are "{design factor, P2 instant calibration}"
is withdrawn. What survives is the weaker and better-supported statement that the manuscript's stored
ablation family shows one dominant component and five inert ones.
"""
L[s:e] = new.split("\n")
p.write_bytes("\n".join(L).encode("utf-8"))
raw = p.read_bytes()
print("4.4 replaced: lines %d-%d (%d lines) -> %d lines" % (s+1, e, e-s, len(new.split("\n"))))
print("report: %d lines, CRLF=%d, %dB" % (len(L), raw.count(b"\r\n"), len(raw)))
