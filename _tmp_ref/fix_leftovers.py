import pathlib
# report fixes
p = pathlib.Path("results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md")
t = p.read_text(encoding="utf-8").replace("\r\n","\n")
a = "| C3 | 0 | **BLOCKED** by the half-applied uncommitted diff (SS0.2, SS4.3) |"
b = "| C3 | 0 | **BLOCKED** by the unfinished call site in the `wo_inst` repair (SS0.2, SS4.3) |"
assert a in t; t = t.replace(a, b)
a2 = "3. **The half-applied uncommitted diff (SS0.2). New.** I claim the current working tree cannot run"
b2 = "3. **The unfinished `wo_inst` repair (SS0.2).** I claim the current working tree cannot run"
assert a2 in t; t = t.replace(a2, b2)
p.write_bytes(t.encode("utf-8")); print("report: 2 stale statements corrected")

# review fix
q = pathlib.Path("ccfa-review-reports/raven-mcs-tmc-review.md")
u = q.read_text(encoding="utf-8").replace("\r\n","\n")
a3 = "5. **The P2-component implication** (`M8`) and the duplicate-arm marking (`M9`), both now evidenced."
b3 = ("5. **The `M8` attribution gap**, now evidenced: the ablation family attributes the U-Air structural "
      "effect to the Design factor alone and does not separate Debt-Cal's route to the same endpoint.")
assert a3 in u; u = u.replace(a3, b3)
q.write_bytes(u.encode("utf-8")); print("review: 1 stale blocking-evidence item corrected")
