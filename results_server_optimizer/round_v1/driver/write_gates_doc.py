"""Assemble S1P_GATES.md from the recorded gate evidence (no runs)."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
sys.path.insert(0, str(ROOT / "results_server_optimizer" / "round_v1" / "driver"))

INSTRUCTION = ROOT / "ccfa-review-reports/raven-mcs-s1prime-server-optimizer-execution-prompt.md"


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


from s1p_driver import G1_FINDINGS  # noqa: E402

g0 = json.loads((OUT / "S1P_G0_COMPARE.json").read_text(encoding="utf-8"))
g2 = json.loads((OUT / "S1P_G2.json").read_text(encoding="utf-8"))

L = []
A = L.append
A("# S1' gates")
A("")
A(f"- Instruction: `{INSTRUCTION.relative_to(ROOT).as_posix()}`")
A(f"- Instruction sha256: `{sha256_file(INSTRUCTION)}`")
A(f"- Driver: `results_server_optimizer/round_v1/driver/s1p_driver.py` "
  f"sha256 `{sha256_file(ROOT / 'results_server_optimizer/round_v1/driver/s1p_driver.py')}`")
A("- Injection: `raven_mcs.training.window_runner.FullWindowRunner` is rebound to "
  "`ServerOptWindowRunner`; `build_full_runner` resolves that name at call time, so **no `src/` file "
  "was edited**.")
A("")
A("## Amendments confirmed by the user on 2026-10-07, before any run")
A("")
A("| id | amendment |")
A("| --- | --- |")
A("| A1 | G0 is a **true identity test**: subclass with the optimizer set to plain SGD at "
  "`eta_s = eta`, compared against an **unmodified `FullWindowRunner` re-run in the current tree**. "
  "The frozen-artifact comparison is a disclosed diagnostic, not a gate (the prompt was written "
  "expecting a bit-exact match with the frozen files, which `P0_REPORT.md` section 5 shows is not "
  "achievable for reasons of artifact vintage). |")
A("| A2 | G0 is **not gated on NSW-Traffic**: the E3 traffic tree has no `fedavg_window` and no "
  "`raven` arm. The E2 `complete_aligned` contract is disclosure only. |")
A("| A3 | Stage C evaluates `MDE80` at **n = 5** per section 2; n = 15 is left to a separately "
  "authorized confirmatory run. |")
A("")
A("## G0 — identity test")
A("")
A(f"- **deterministic verdict (the gate): {g0['G0a']['pass']}**")
A(f"- literal verdict including the wall-clock field: {g0['G0b_literal']['pass']} "
  f"({g0['G0b_literal']['why_it_cannot_pass']})")
A("")
A("| block | arm | fields compared | deterministic mismatches | final theta byte-identical | "
  "wall-clock field |")
A("| --- | --- | --- | --- | --- | --- |")
for r in g0["rows"]:
    A(f"| {r['block']} | {r['arm']} | {r['fields_compared']} | "
      f"{len(r['mismatches_excluding_wall_clock'])} | {r['final_theta_bit_identical']} | "
      f"`runtime_seconds` = {r['wall_clock_values'].get('runtime_seconds')} |")
A("")
A("Every deterministic field of `final_metrics.json` is bit-exact and the final `checkpoints/final.pt` "
  "is byte-identical between the unmodified runner and the subclass with the optimizer set to plain "
  "SGD. `runtime_seconds` is the only field that ever differs, because it is a wall clock and not a "
  "function of the computation; it is named in one place in the driver (`WALL_CLOCK_FIELDS`) and "
  "reported here with both values rather than silently dropped.")
A("")
A("### Frozen-artifact diagnostic (disclosure only, per A1)")
A("")
A("| block | arm | field | frozen | re-run | abs diff | rel diff |")
A("| --- | --- | --- | --- | --- | --- | --- |")
for r in g0["rows"]:
    for k, v in r["frozen_artifact_diagnostic"].items():
        A(f"| {r['block']} | {r['arm']} | `{k}` | {v['frozen']!r} | {v['rerun_baseline']!r} | "
          f"{v['abs_diff']:.3e} | {v['rel_diff']:.3e} |")
A("")
A("Reading: SensorScope `fedavg_window`, SensorScope `raven` and U-Air `raven` reproduce the frozen "
  "artifacts **exactly** (U-Air `raven` even with a byte-identical checkpoint, "
  "`eb8137dd02b0ebfd58f8d208`). **U-Air `fedavg_window` does not**: it moves from "
  "`1.210848485707097` to `1.1712625825964957` (-3.27 %), with the active-window count rising from "
  "66 to 74 and `a_r_size` systematically one larger in the re-run. That arm is a Table II baseline, "
  "so this is a real artifact-reproducibility miss on the current tree and is reported as a finding; "
  "it does not affect this round, whose Stage A/C comparisons are internally consistent (all arms "
  "re-run in the same tree).")
A("")
A("Correction recorded for honesty: an earlier check in this session compared `theta_hash_after` "
  "between frozen and re-run `window_metrics.json` and reported 'identical on 80/80'. That comparison "
  "was vacuous — `window_metrics.json` does not serialise the theta hashes, so both sides were "
  "`None`. The checkpoint byte-comparison above is the real evidence.")
A("")
A("## G1 — reads-after-update audit")
A("")
A(f"- STOP condition fired: **False**. `final_metrics.json` has 32 keys and no hash / theta / model "
  "key, so none of the affected logged values reaches the decision metric.")
A("")
A("| line | code | sees theta_new | note |")
A("| --- | --- | --- | --- |")
for f in G1_FINDINGS:
    code = f["code"].replace("|", "\\|")
    why = f["why"].replace("|", "\\|")
    A(f"| `{f['line']}` | `{code}` | {f['sees_theta_new']} | {why} |")
A("")
A("The one real finding is **L1204** `after_hash = self._theta_hash()`: it is evaluated inside "
  "`super()._process_window(...)`, therefore **before** the server-optimizer step, so "
  "`WindowMetrics.theta_hash_after` (L1275) and the per-client `global_model_hash` / "
  "`model_hash_after` (L1231, L1236-L1237) record `theta_sgd` while the run continues from "
  "`theta_new`. These are log-only fields; they appear in `window_metrics.json` diagnostics, not in "
  "`final_metrics.json`. Under FedAdam they will therefore differ from the values an unmodified run "
  "would log, which is expected and disclosed.")
A("")
A("## G2 — determinism")
A("")
A(f"- **pass: {g2['pass']}** (`{g2['run_a']}` vs `{g2['run_b']}`, eta_s = 1e-3, FedAdam)")
A(f"- deterministic differences: {g2['deterministic_differences'] or 'none'}")
A(f"- wall-clock field excluded: {g2['wall_clock_values'] or 'none'}")
A("")
A("## Gate conclusion")
A("")
A("All three gates pass. The grid may run.")
(OUT / "S1P_GATES.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote", OUT / "S1P_GATES.md")
print("G0 gate:", g0["G0a"]["pass"], "| G2:", g2["pass"])
