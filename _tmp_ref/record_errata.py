import pathlib
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
L = p.read_text(encoding="utf-8").replace("\r\n","\n").split("\n")
log = []

# 1) remove the WRONG open-defect row
hits = [i for i,l in enumerate(L) if l.startswith("| **the U-Air `Inst` ablation row contradicts")]
for i in reversed(hits):
    del L[i]; log.append(f"deleted WRONG row @{i+1}")
if not hits: log.append("NOT FOUND: the Inst row")

# 2) insert the CORRECT residual row
hdr = next(i for i,l in enumerate(L) if l.startswith("| item | where | note |"))
newrow = ("| **the `wo_inst` ablation fix is unfinished at one call site** | "
          "`src/raven_mcs/sag/counterfactual_audit.py:106`; `feasibility.py:29-46`; "
          "`p2_cvxpy.py:56,70`; `src/raven_mcs/e4/wo_inst_final/` | The 2026-08-12 wo_inst repair added an "
          "`instant_calibration` flag so that `lambda_group=0` is legal for the ablation "
          "(`E4_WO_INST_SEMANTIC_FIX.json`), but `counterfactual_audit._solve_alpha` still calls `solve_p2` "
          "without the flag, so `RavenWoInstAggregator` raises `lambda_group must be >= max_server_learning_rate`. "
          "The arm cannot be re-run until that call site is covered. Nine lines of the repair also remain "
          "uncommitted. No manuscript value depends on this |")
L.insert(hdr+1, newrow); log.append(f"inserted correct residual row @{hdr+2}")

# 3) changelog item 34
anchor = "### Open manuscript defects NOT changed"
block = """| 34 | **Erratum: an open-defect row added on 2026-09-27 was wrong and has been removed and replaced.** It claimed that Table IV's U-Air `Inst` row contradicted the E4 arm it names, quoting a tree mean of `1.119606` against the printed `-0.089`. In fact `artifacts/e4_ablation_semantic_integrity_repair_r1/E4_WO_INST_FINAL_DECISION.json` (2026-08-12) records `proven_invalid: true` with `authorized_corrective_reruns: 40` and the reason "Parent raven_wo_inst skipped P2 by setting alpha=beta when uses_instant_calibration=False". The tree arm's `p2_invocation_states.json` is empty (`3` bytes) where every sibling arm logs 0.87-1.23 MB, confirming P2 never ran. The 40 corrective reruns reproduce Table IV to four decimals (`UAir_Delta_group` `-0.0894 %`, `Holm p = 0.105`). **Table IV is correct; the tree arm is the superseded one.** The row is replaced by the real residual (`wo_inst` fix unfinished at `counterfactual_audit._solve_alpha`) | this file; `results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md` SS0.3; `ccfa-review-reports/raven-mcs-tmc-review.md` M8/M9 |

"""
i = L.index(anchor)
L[i:i] = block.split("\n")
log.append(f"changelog item 34 inserted before line {i+1}")

p.write_bytes("\n".join(L).encode("utf-8"))
raw = p.read_bytes()
print("\n".join(log))
print("record: %d lines, CRLF=%d, %dB" % (len(L), raw.count(b"\r\n"), len(raw)))
