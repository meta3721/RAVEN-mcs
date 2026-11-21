import pathlib
p = pathlib.Path("results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md")
L = p.read_text(encoding="utf-8").replace("\r\n","\n").split("\n")
s = next(i for i,l in enumerate(L) if l.startswith("6. **SS5's attribution"))
e = next(i for i in range(s+1, len(L)) if L[i].startswith("## 10."))
new = """6. **SS5's attribution, and the blocked 2x2.** No single component explains Debt-Cal's route to the
   same structural endpoint. On the corrected ablation the Design factor moves `Delta_group` by
   `-6.943 %` on U-Air, while debt moves it by `0.004 %`, observation IPW by `0.123 %`, usable IPW by
   `0.014 %` and instant calibration by `-0.089 %`. The family therefore isolates the Design factor and
   leaves the rest unattributed. An earlier version of this item claimed instant calibration was
   decisive, quoting `raven_wo_inst` at `1.119606`; that arm is invalidated (SS0.3). Neither of us has
   the controlled 2x2 (SS4.3, blocked). Attack the attribution, not the direction.
"""
L[s:e] = new.split("\n")
p.write_bytes("\n".join(L).encode("utf-8"))
print("SS9 item 6 replaced: lines %d-%d -> %d lines" % (s+1, e, len(new.split("\n"))))
