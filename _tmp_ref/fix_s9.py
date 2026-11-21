import pathlib
p = pathlib.Path("results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md")
t = p.read_text(encoding="utf-8").replace("\r\n","\n")
old = """6. **SS5's attribution, and the blocked 2x2.** The reviewer attributes NoDesign's `Delta_group` structure
   to "instant calibration **and debt**"; SS4.4 shows **debt is inert** (`raven` 1.092362 vs
   `raven_wo_debt` 1.092409) and instant calibration alone is decisive (`raven_wo_inst` 1.119606).
   Neither of us has the controlled 2x2 (SS4.3, blocked). Attack the attribution, not the direction."""
new = """6. **SS5's attribution, and the blocked 2x2.** No single component explains Debt-Cal's route to the
   same structural endpoint. On the corrected ablation the Design factor moves `Delta_group` by
   `-6.943 %` on U-Air, while debt moves it by `0.004 %`, observation IPW by `0.123 %`, usable IPW by
   `0.014 %` and instant calibration by `-0.089 %`. The family therefore isolates the Design factor and
   leaves the rest unattributed. An earlier version of this item claimed instant calibration was
   decisive, quoting `raven_wo_inst` at `1.119606`; that arm is invalidated (SS0.3). Neither of us has
   the controlled 2x2 (SS4.3, blocked). Attack the attribution, not the direction."""
assert old in t, "anchor not found"
t = t.replace(old, new)
p.write_bytes(t.encode("utf-8"))
print("report: SS9 item 6 corrected")
